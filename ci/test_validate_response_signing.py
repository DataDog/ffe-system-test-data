"""Regression checks for unambiguous response-signing fixture inputs."""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_response_signing", ROOT / "ci/validate-response-signing.py"
)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ResponseSigningValidationTest(unittest.TestCase):
    def test_adversarial_corpus_including_duplicate_http_headers_is_valid(self):
        with contextlib.redirect_stdout(io.StringIO()):
            validator.validate(ROOT)

    def test_duplicate_object_keys_are_rejected_in_every_input(self):
        mutations = [
            ("schemas/response-signing-v1.schema.json", '"title":', '"title": "ambiguous", "title":'),
            (
                "response-signing/v1/manifest.json",
                '"schema_version": 1',
                '"schema_version": 0, "schema_version": 1',
            ),
            (
                "response-signing/v1/corpus.json",
                '"expected_accept": true',
                '"expected_accept": false, "expected_accept": true',
            ),
            (
                "response-signing/v1/nested-der.json",
                '"expected_accept": true',
                '"expected_accept": false, "expected_accept": true',
            ),
            (
                "response-signing/v1/isolated-certificate-rules.json",
                '"expected_accept": true',
                '"expected_accept": false, "expected_accept": true',
            ),
            (
                "response-signing/v1/corpus.json",
                '"expected_accept": true',
                '"expected_accept": false, "expected\\u005faccept": true',
            ),
        ]
        for name in ("subject-der.json", "near-expiry.json", "extension-profile.json"):
            mutations.append((f"response-signing/v1/{name}", '"expected_accept": true',
                              '"expected_accept": false, "expected_accept": true'))
        for relative, old, new in mutations:
            with self.subTest(document=relative, replacement=new), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in ("schemas", "response-signing"):
                    shutil.copytree(ROOT / name, root / name)
                path = root / relative
                raw = path.read_text()
                self.assertIn(old, raw)
                path.write_text(raw.replace(old, new, 1))
                if path.parent.name == "v1" and path.name != "manifest.json":
                    # Keep integrity checks valid so rejection must come from JSON parsing.
                    manifest_path = root / "response-signing/v1/manifest.json"
                    manifest = json.loads(manifest_path.read_text())
                    manifest["files"][path.name]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                    manifest_path.write_text(json.dumps(manifest))
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaisesRegex(ValueError, "duplicate object key"):
                        validator.validate(root)


if __name__ == "__main__":
    unittest.main()

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import precomputed_obfuscation as obfuscation


class ObfuscatedCompanionsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.cases = self.root / "cases"
        self.source = self.cases / "evaluator" / "case.json"
        self.source.parent.mkdir(parents=True)
        self.fixture = {
            "name": "case", "description": "A normal case",
            "response": {"data": {"attributes": {"flags": {"flag": {"variationValue": 7}}}}},
            "evaluations": [{"flag": "flag", "expectedResult": {"value": 7}}],
            "expectations": {"exposures": [{"_count": 1, "flag": {"key": "flag"}}]},
        }
        self.source.write_text(json.dumps(self.fixture))
        self.exceptions = self.root / "exceptions.json"
        self.exceptions.write_text("{}")

    def sync(self, check=True):
        return obfuscation.synchronize(self.cases, self.exceptions, check)

    def test_number_tokens_survive_generation_without_rounding(self):
        for token in ['5.0', '-0', '-0.0', '1e+02', '1.20000000000000001',
                      '1.00000000000000001', '4503599627370497.5', '9007199254740993.5']:
            with self.subTest(token=token):
                raw = json.dumps(self.fixture).replace('"variationValue": 7', '"variationValue": ' + token)
                self.source.write_text(raw)
                self.sync(False)
                generated = next((self.cases / 'obfuscation').rglob('*.json')).read_text()
                self.assertIn('"variationValue": ' + token + '\n', generated)
                self.assertEqual([], self.sync())

    def test_missing_companion_fails_cli(self):
        result = subprocess.run([sys.executable, str(Path(obfuscation.__file__)), "--check",
                                 "--cases", str(self.cases), "--exceptions", str(self.exceptions)],
                                capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn("Missing obfuscated companion", result.stderr)

    def test_new_nested_source_is_discovered(self):
        self.sync(False)
        new = self.source.parent / "nested" / "new.json"
        new.parent.mkdir()
        new.write_text(json.dumps({**self.fixture, "name": "new"}))
        self.assertIn("Missing obfuscated companion: evaluator/nested/obfuscation-new.json", self.sync())
        self.sync(False)
        self.assertEqual([], self.sync())

    def test_changed_source_or_generated_expectations_fail(self):
        self.sync(False)
        self.fixture["evaluations"][0]["expectedResult"]["value"] = 9
        self.source.write_text(json.dumps(self.fixture))
        self.assertTrue(self.sync())
        self.sync(False)
        target = next((self.cases / "obfuscation").rglob("*.json"))
        target.write_text(target.read_text().replace('"value": 9', '"value": 8'))
        self.assertTrue(self.sync())

    def test_orphan_is_reported_and_removed(self):
        self.sync(False)
        new = self.source.with_name("other.json")
        new.write_text(json.dumps({**self.fixture, "name": "other"}))
        self.sync(False)
        new.unlink()
        self.assertTrue(any("Orphaned" in error for error in self.sync()))
        self.sync(False)
        self.assertEqual([], self.sync())

    def test_only_wire_keys_and_encoding_metadata_change(self):
        source = copy.deepcopy(self.fixture)
        source["_include"] = [{"platform": "ios"}, {"platform": "unity"}]
        source["evaluations"][0]["_skip"] = [{"platform": "ios"}]
        result = obfuscation.companion(source)
        self.assertEqual(["ios"], [p["platform"] for p in result["_include"]])
        self.assertEqual(source["evaluations"], result["evaluations"])
        self.assertEqual(source["expectations"], result["expectations"])
        self.assertIn("flag", source["response"]["data"]["attributes"]["flags"])

    def test_skip_filter_is_preserved_by_intersection(self):
        self.fixture["_skip"] = [{"platform": "android"}]
        result = obfuscation.companion(self.fixture)
        self.assertEqual(["ios", "flutter"], [p["platform"] for p in result["_include"]])
        self.assertNotIn("_skip", result)

    def test_web_only_fixture_gets_obfuscated_companion(self):
        self.fixture["_include"] = [{"platform": "web"}]
        result = obfuscation.companion(self.fixture)
        self.assertEqual(["web"], [p["platform"] for p in result["_include"]])

    def test_response_internal_dependency_keys_are_encoded(self):
        assignment = self.fixture["response"]["data"]["attributes"]["flags"]["flag"]
        assignment["dependencyEvaluations"] = [
            {"flagKey": "parent", "isPresentInAssignment": True},
            {"flagKey": "missing", "reason": "ERROR", "errorCode": "FLAG_NOT_FOUND"},
        ]
        self.fixture["expectations"] = {
            "exposures": [{"_count": 1, "flag": {"key": "parent"}}],
            "evaluationEvents": [{"_count": 1, "flag": {"key": "missing"}}],
        }

        result = obfuscation.companion(self.fixture)
        encoded_assignment = result["response"]["data"]["attributes"]["flags"][
            obfuscation.encode_key("flag")
        ]

        self.assertEqual(
            [obfuscation.encode_key("parent"), obfuscation.encode_key("missing")],
            [entry["flagKey"] for entry in encoded_assignment["dependencyEvaluations"]],
        )
        self.assertEqual("parent", assignment["dependencyEvaluations"][0]["flagKey"])
        self.assertEqual(
            obfuscation.encode_key("parent"),
            result["expectations"]["exposures"][0]["flag"]["key"],
        )
        self.assertEqual(
            obfuscation.encode_key("missing"),
            result["expectations"]["evaluationEvents"][0]["flag"]["key"],
        )

    def test_root_and_dependency_identity_ambiguity_is_rejected(self):
        assignment = self.fixture["response"]["data"]["attributes"]["flags"]["flag"]
        assignment["dependencyEvaluations"] = [{"flagKey": "flag", "isPresentInAssignment": True}]
        with self.assertRaises(ValueError):
            obfuscation.companion(self.fixture)

    def test_error_map_and_its_dependency_keys_are_encoded(self):
        attributes = self.fixture["response"]["data"]["attributes"]
        attributes["flagEvaluationErrors"] = {
            "failed": {
                "reason": "ERROR",
                "errorCode": "FLAG_NOT_FOUND",
                "dependencyEvaluations": [
                    {"flagKey": "missing", "reason": "ERROR", "errorCode": "FLAG_NOT_FOUND"}
                ],
            }
        }

        result = obfuscation.companion(self.fixture)
        errors = result["response"]["data"]["attributes"]["flagEvaluationErrors"]
        encoded_error = errors[obfuscation.encode_key("failed")]
        self.assertEqual(
            obfuscation.encode_key("missing"),
            encoded_error["dependencyEvaluations"][0]["flagKey"],
        )

    def test_exception_requires_existing_source_and_reason(self):
        for entries in [{"evaluator/case.json": ""}, {"deleted.json": "Not applicable"}]:
            self.exceptions.write_text(json.dumps(entries))
            with self.assertRaises(ValueError):
                self.sync()
        self.exceptions.write_text(json.dumps({"evaluator/case.json": "Wire-envelope rejection only"}))
        self.assertEqual([], self.sync())

    def test_untransformable_source_requires_explicit_exception(self):
        self.fixture["response"]["data"]["attributes"]["flags"] = None
        self.source.write_text(json.dumps(self.fixture))
        with self.assertRaises(ValueError):
            self.sync()

    def test_known_digest_vectors_are_independent_of_generation(self):
        vectors = {
            "flag": "9817872c144b018abd77e3915bd77e2c27f4f534dccff8ffaca27361e3a5e1ee",
            "Flag": "adca75d2141c51b0c0f084c1058edfb8e6e763f91aaf54ca06326d9847bd9586",
            " flag ": "b1a5f851cc82a3fdf03a461d72a2241584dcf455df1d384e02a937901b3bc80b",
            "caf\u00e9": "3bfa8c3c17c1b61035b98ecf14007cdf5cba5ce61a48e8cfb65f8106541892d3",
            "cafe\u0301": "1e8b7ec5e8028a1ec96b38dd37f6ccea041c0a90358904af40ac5810c23c8765",
            "\U0001f6b2/\u65d7": "94b611e0d3b26b52f6ad66013d1c72f8a92ea109390049759e75d3c8d3aa4dab",
            "a\0b": "bac134d201be5e7f28fc7019248f0809c2a013b137e866446ee71add2bc344c7",
            "": "072d985b427f536ad0a11b2d4c5e0f7e6f0ff6d23e779e082f75599ce3fe3eba",
        }
        for key, expected in vectors.items():
            self.assertEqual(expected, obfuscation.encode_key(key))


if __name__ == "__main__":
    unittest.main()

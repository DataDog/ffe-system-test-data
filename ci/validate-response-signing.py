#!/usr/bin/env python3
"""Validate the shape and pinned bytes of the response-signing conformance data."""

import base64
import hashlib
import json
from pathlib import Path

import jsonschema


def validate(root):
    directory = root / "response-signing/v3"
    schema = json.loads((root / "schemas/response-signing-v3.schema.json").read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    manifest = json.loads((directory / "manifest.json").read_text())
    assert manifest["schema_version"] == 1
    assert set(manifest["files"]) == {"corpus.json", "nested-der.json"}
    for name, expected in manifest["files"].items():
        raw = (directory / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"], name
        corpus = json.loads(raw)
        jsonschema.validate(corpus, schema)
        cases = corpus["cases"]
        ids = [case["id"] for case in cases]
        assert len(ids) == len(set(ids)), f"{name}: duplicate case id"
        assert len(cases) == expected["response_cases"], name
        assert sum(case["expected_accept"] for case in cases) == expected["accepted"], name
        for case in cases:
            for message in (case["request"], case["response"]):
                base64.b64decode(message["body_base64"], validate=True)
            if case["expected_accept"]:
                assert case["rejection_reason"] is None, case["id"]
                assert case["transcript_base64"], case["id"]
            if case.get("transcript_base64") is not None:
                base64.b64decode(case["transcript_base64"], validate=True)
        signing_cases = corpus.get("signing_cases", [])
        assert len(signing_cases) == expected["signing_cases"], name
        signing_ids = [case["id"] for case in signing_cases]
        assert len(signing_ids) == len(set(signing_ids)), name
        for case in signing_cases:
            assert case["case_id"] in ids, case["id"]
        print(f"{name}: {len(cases)} response cases, {len(signing_cases)} signer cases validated")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[1])

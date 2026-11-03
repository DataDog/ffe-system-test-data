#!/usr/bin/env python3
"""Validate the shape and pinned bytes of the response-signing conformance data."""

import base64
import hashlib
import json
from pathlib import Path

import jsonschema


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate object key {key!r}")
        result[key] = value
    return result


def validate(root):
    directory = root / "response-signing/v1"
    schema = json.loads(
        (root / "schemas/response-signing-v1.schema.json").read_text(),
        object_pairs_hook=reject_duplicate_keys,
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    manifest = json.loads(
        (directory / "manifest.json").read_text(), object_pairs_hook=reject_duplicate_keys
    )
    assert manifest["schema_version"] == 1
    assert set(manifest["files"]) == {"corpus.json", "nested-der.json", "isolated-certificate-rules.json"}
    for name, expected in manifest["files"].items():
        raw = (directory / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"], name
        corpus = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
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
                for message in (case["request"], case["response"]):
                    assert [v for k, v in message["headers"] if k.lower() ==
                            "x-datadog-feature-flags-signature-version"] == ["1"], case["id"]
                assert base64.b64decode(case["transcript_base64"], validate=True).startswith(
                    b"datadog.feature-flags.precomputed-assignments.v1\0"
                ), case["id"]
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

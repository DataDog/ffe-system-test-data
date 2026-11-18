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


DOMAIN = b"datadog.feature-flags.precomputed-assignments.v1\0"
MAX_INTERMEDIATES = 3


def header(message, name):
    return [v for k, v in message["headers"] if k.lower() == "x-datadog-feature-flags-" + name]


def check_credential(credential, case_id):
    assert credential["version"] == 1, case_id
    intermediates = credential["intermediates_der_base64"]
    assert 1 <= len(intermediates) <= MAX_INTERMEDIATES, case_id
    for value in [credential["certificate_der_base64"], credential["private_key_pkcs8_der_base64"], *intermediates]:
        base64.b64decode(value, validate=True)


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
    assert set(manifest["files"]) == {
        "corpus.json", "nested-der.json", "isolated-certificate-rules.json",
        "subject-der.json", "near-expiry.json", "extension-profile.json",
    }
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
        base64.b64decode(corpus["anchor_der_base64"], validate=True)
        for case in cases:
            for message in (case["request"], case["response"]):
                base64.b64decode(message["body_base64"], validate=True)
            if "anchor_der_base64" in case:
                base64.b64decode(case["anchor_der_base64"], validate=True)
            if case["expected_accept"]:
                assert case["rejection_reason"] is None, case["id"]
                assert case["transcript_base64"], case["id"]
                for message in (case["request"], case["response"]):
                    assert header(message, "signature-version") == ["1"], case["id"]
                # The chain header replaces the removed single-intermediate header.
                assert header(case["response"], "signing-intermediate") == [], case["id"]
                chain = header(case["response"], "signing-chain")
                assert len(chain) == 1 and 1 <= len(chain[0].split(",")) <= MAX_INTERMEDIATES, case["id"]
                for entry in chain[0].split(","):
                    base64.b64decode(entry, validate=True)
                transcript = base64.b64decode(case["transcript_base64"], validate=True)
                assert transcript.startswith(DOMAIN), case["id"]
                # Tail: u8 intermediate count, then one SHA-256 digest per intermediate.
                count = len(chain[0].split(","))
                assert transcript[-32 * count - 1] == count, case["id"]
                if "credential" in case:
                    check_credential(case["credential"], case["id"])
            else:
                assert case["rejection_reason"], case["id"]
            if case.get("transcript_base64") is not None:
                base64.b64decode(case["transcript_base64"], validate=True)
        signing_cases = corpus.get("signing_cases", [])
        assert len(signing_cases) == expected["signing_cases"], name
        signing_ids = [case["id"] for case in signing_cases]
        assert len(signing_ids) == len(set(signing_ids)), name
        for case in signing_cases:
            assert case["case_id"] in ids, case["id"]
            if "intermediate_der_base64" in case["credential"]:
                # The removed credential field must never sign.
                assert case["expected_signing"] is False, case["id"]
            elif case["expected_signing"]:
                check_credential(case["credential"], case["id"])
        print(f"{name}: {len(cases)} response cases, {len(signing_cases)} signer cases validated")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[1])

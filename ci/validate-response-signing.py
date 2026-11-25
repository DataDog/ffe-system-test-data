#!/usr/bin/env python3
"""Validate the shape and pinned bytes of the response-signing conformance data."""

import base64
import binascii
import gzip
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
MAX_LISTED_NAMES = 32
MAX_NAME_BYTES = 64


def header(message, name):
    return [v for k, v in message["headers"] if k.lower() == "x-datadog-feature-flags-" + name]


def plain_header(message, name):
    return [v for k, v in message["headers"] if k.lower() == name]


def check_name_list(value, case_id):
    """An accepted list: lowercase, sorted, unique names joined by "," with no spaces."""
    names = value.split(",")
    assert 1 <= len(names) <= MAX_LISTED_NAMES, case_id
    assert all(name and name == name.lower() and " " not in name and len(name.encode()) <= MAX_NAME_BYTES
               for name in names), case_id
    assert names == sorted(set(names)), case_id
    return names


def name_values(names, message):
    """u8(count), then lp(name) || u8(presence) || lp(value) for each name."""
    output = bytes([len(names)])
    for name in names:
        found = plain_header(message, name)
        value = found[0].encode() if found else b""
        output += len(name).to_bytes(4, "big") + name.encode() + bytes([1 if found else 0])
        output += len(value).to_bytes(4, "big") + value
    return output


def check_wire_body(response, case_id):
    """Compressed transport bytes must decode to the signed application bytes."""
    if "wire_body_base64" not in response:
        return
    encodings = [v for k, v in response["headers"] if k.lower() == "content-encoding"]
    assert encodings == ["gzip"], case_id
    try:
        wire = base64.b64decode(response["wire_body_base64"], validate=True)
    except binascii.Error:
        raise AssertionError(case_id)
    assert gzip.decompress(wire) == base64.b64decode(response["body_base64"], validate=True), case_id


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
            check_wire_body(case["response"], case["id"])
            if "anchor_der_base64" in case:
                base64.b64decode(case["anchor_der_base64"], validate=True)
            if case["expected_accept"]:
                assert case["rejection_reason"] is None and "sdk_reason" not in case, case["id"]
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
                request_list = header(case["request"], "signed-headers")
                assert len(request_list) == 1, case["id"]
                request_names = check_name_list(request_list[0], case["id"])
                assert {"content-type", "x-dd-feature-flags-capabilities"} <= set(request_names), case["id"]
                assert name_values(request_names, case["request"]) in transcript, case["id"]
                response_list = header(case["response"], "signed-response-headers")
                assert len(response_list) == 1, case["id"]
                response_names = check_name_list(response_list[0], case["id"])
                assert "content-type" in response_names, case["id"]
                verified = case["verified_response_headers"]
                assert list(verified) == response_names, case["id"]
                for listed in response_names:
                    assert verified[listed] == (plain_header(case["response"], listed) or [None])[0], case["id"]
                # Tail: u8 intermediate count, one SHA-256 digest per intermediate,
                # then the signed response list.
                entries = chain[0].split(",")
                tail = bytes([len(entries)]) + b"".join(
                    hashlib.sha256(base64.b64decode(entry)).digest() for entry in entries)
                assert transcript.endswith(tail + name_values(response_names, case["response"])), case["id"]
                if "credential" in case:
                    check_credential(case["credential"], case["id"])
            else:
                assert case["rejection_reason"] and case.get("sdk_reason"), case["id"]
                assert "verified_response_headers" not in case, case["id"]
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


def validate_chain(root):
    directory = root / "response-signing/chain"
    manifest = json.loads(
        (directory / "manifest.json").read_text(), object_pairs_hook=reject_duplicate_keys
    )
    assert manifest["schema_version"] == 1
    on_disk = {p.name for p in directory.iterdir()} - {"manifest.json", "README.md"}
    assert set(manifest["files"]) == on_disk, sorted(on_disk ^ set(manifest["files"]))
    for name, expected in manifest["files"].items():
        raw = (directory / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"], name
        if name.endswith(".json"):
            check_credential(json.loads(raw, object_pairs_hook=reject_duplicate_keys), name)
        elif name.endswith(".pem"):
            lines = raw.decode().strip().splitlines()
            assert lines[0] == "-----BEGIN CERTIFICATE-----" and lines[-1] == "-----END CERTIFICATE-----", name
            base64.b64decode("".join(lines[1:-1]), validate=True)
        for key in ("anchor", "credential"):
            if key in expected:
                assert expected[key] in manifest["files"], (name, expected[key])
    print(f"chain: {len(manifest['files'])} files validated")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[1])
    validate_chain(Path(__file__).resolve().parents[1])

#!/usr/bin/env python3
"""Check every response-signing v1 expectation with an independent verifier.

This script does not import the fixture generator or any SDK, signer or edge code.
It has its own strict DER reader, certificate profile, chain rules, time rules and
transcript builder. The OpenSSL command line tool verifies each ECDSA signature
and derives public keys from private keys.

For each response case it asserts `expected_accept` and the `rejection_reason`
code, and compares the transcript of accepted cases. For each signer case it
asserts `expected_signing`.
"""
import base64
import calendar
import datetime
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "response-signing/v1"
PROOF = "x-datadog-feature-flags-"
DOMAIN = b"datadog.feature-flags.precomputed-assignments.v1\0"
OTHER_DOMAINS = [b"datadog.feature-flags.precomputed-assignments.v2\0",
                 b"datadog.feature-flags.precomputed-assignments.v3\0"]
FFE_EKU = "1.3.6.1.4.1.99999.1.1"  # Placeholder OID; Datadog assigns the real one.
ANY_EKU = "2.5.29.37.0"
MAX_CERTIFICATE = 4096
MAX_BASE64 = 4 * -(-MAX_CERTIFICATE // 3)
MAX_SAFE_INTEGER = 2 ** 53 - 1
FORBIDDEN_EXTENSIONS = {"2.5.29.30", "2.5.29.33", "2.5.29.36", "2.5.29.54"}
KNOWN_EXTENSIONS = {"2.5.29.19", "2.5.29.15", "2.5.29.37", "2.5.29.14", "2.5.29.35"}
SEMANTIC_HEADERS = ["content-type", "dd-application-id", "x-rkyv", "x-use-cache",
                    "x-dd-feature-flags-capabilities"]


class Reject(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def require(condition, reason):
    if not condition:
        raise Reject(reason)


# ---------------------------------------------------------------- strict DER

class Node:
    def __init__(self, tag, content, items):
        self.tag, self.content, self.items = tag, content, items


def der(data, reason="certificate-encoding"):
    """Parse one complete strict-DER value. Raise Reject(reason) on any BER form."""
    budget = [512]

    def read(offset, limit, depth):
        require(depth <= 24 and budget[0] > 0 and offset + 2 <= limit, reason)
        budget[0] -= 1
        tag = data[offset]
        require(tag & 0x1F != 0x1F, reason)
        length = data[offset + 1]
        cursor = offset + 2
        if length & 0x80:
            count = length & 0x7F
            require(1 <= count <= 3 and cursor + count <= limit and data[cursor] != 0, reason)
            length = int.from_bytes(data[cursor:cursor + count], "big")
            cursor += count
            require(length >= 128, reason)
        end = cursor + length
        require(end <= limit, reason)
        content = data[cursor:end]
        if tag & 0x20:
            require(tag & 0xC0 or tag in (0x30, 0x31), reason)
            items, position, previous = [], cursor, None
            while position < end:
                child, following = read(position, end, depth + 1)
                raw = data[position:following]
                if tag == 0x31:
                    require(previous is None or previous <= raw, reason)
                    previous = raw
                items.append(child)
                position = following
            return Node(tag, content, items), end
        if tag == 0x01:
            require(content in (b"\x00", b"\xff"), reason)
        elif tag == 0x02:
            require(content and not (len(content) > 1 and (
                (content[0] == 0 and content[1] < 0x80) or (content[0] == 0xFF and content[1] >= 0x80))), reason)
        elif tag == 0x03:
            require(content and content[0] <= 7 and (len(content) > 1 or content[0] == 0), reason)
            require(content[-1] & ((1 << content[0]) - 1) == 0, reason)
        elif tag == 0x05:
            require(not content, reason)
        elif tag == 0x06:
            require(content and content[-1] < 0x80, reason)
            require(all(byte != 0x80 or (i and content[i - 1] >= 0x80) for i, byte in enumerate(content)), reason)
        elif tag in (0x17, 0x18):
            decode_time(tag, content, reason)
        return Node(tag, content, None), end

    require(isinstance(data, bytes) and data, reason)
    node, end = read(0, len(data), 0)
    require(end == len(data), reason)
    return node


def decode_time(tag, content, reason):
    text = content.decode("ascii", "replace")
    width = 2 if tag == 0x17 else 4
    require(re.fullmatch(r"[0-9]{%d}Z" % (width + 10), text), reason)
    year = int(text[:width])
    if width == 2:
        year += 1900 if year >= 50 else 2000
    fields = [int(text[width + i:width + i + 2]) for i in range(0, 10, 2)]
    try:
        moment = datetime.datetime(year, *fields, tzinfo=datetime.timezone.utc)
    except ValueError:
        raise Reject(reason)
    return calendar.timegm(moment.utctimetuple())


def oid_text(content):
    values, current = [], 0
    for byte in content:
        current = (current << 7) | (byte & 0x7F)
        if not byte & 0x80:
            values.append(current)
            current = 0
    first = min(values[0] // 40, 2)
    return ".".join(str(v) for v in [first, values[0] - 40 * first] + values[1:])


def encoded(node):
    """Re-encode a parsed node; strict DER makes this the original bytes."""
    content = node.content
    size = len(content)
    length = bytes([size]) if size < 128 else bytes([0x80 | ((size.bit_length() + 7) // 8)]) + \
        size.to_bytes((size.bit_length() + 7) // 8, "big")
    return bytes([node.tag]) + length + content


# ---------------------------------------------------------------- certificates

P256_SPKI_ALGORITHM = bytes.fromhex("301306072a8648ce3d020106082a8648ce3d030107")
ECDSA_SHA256 = bytes.fromhex("300a06082a8648ce3d040302")


def parse_certificate(data):
    require(0 < len(data) <= MAX_CERTIFICATE, "certificate-size")
    root = der(data)
    bad = "certificate-encoding"
    require(root.tag == 0x30 and len(root.items) == 3, bad)
    tbs, algorithm, signature = root.items
    require(tbs.tag == 0x30 and len(tbs.items) == 8, bad)
    version, serial, inner_algorithm, issuer, validity, subject, spki, extensions = tbs.items
    require(encoded(version) == b"\xa0\x03\x02\x01\x02" and serial.tag == 0x02, bad)
    require(encoded(algorithm) == ECDSA_SHA256 and encoded(inner_algorithm) == ECDSA_SHA256, bad)
    require(signature.tag == 0x03 and signature.content[:1] == b"\x00", bad)
    for name in (issuer, subject):
        require(name.tag == 0x30, bad)
        for rdn in name.items:
            require(rdn.tag == 0x31 and rdn.items, bad)
            for attribute in rdn.items:
                require(attribute.tag == 0x30 and len(attribute.items) == 2 and attribute.items[0].tag == 0x06, bad)
    require(validity.tag == 0x30 and len(validity.items) == 2, bad)
    times = [decode_time(item.tag, item.content, bad) for item in validity.items
             if item.tag in (0x17, 0x18)]
    require(len(times) == 2 and times[0] < times[1] <= MAX_SAFE_INTEGER, bad)
    require(spki.tag == 0x30 and len(spki.items) == 2 and encoded(spki.items[0]) == P256_SPKI_ALGORITHM, bad)
    point = spki.items[1].content
    require(spki.items[1].tag == 0x03 and len(point) == 66 and point[:2] == b"\x00\x04", bad)
    require(extensions.tag == 0xA3 and len(extensions.items) == 1 and extensions.items[0].tag == 0x30, bad)
    parsed = []
    for item in extensions.items[0].items:
        require(item.tag == 0x30 and len(item.items) in (2, 3) and item.items[0].tag == 0x06, bad)
        critical = False
        if len(item.items) == 3:
            require(item.items[1].tag == 0x01 and item.items[1].content == b"\xff", bad)
            critical = True
        require(item.items[-1].tag == 0x04, bad)
        parsed.append((oid_text(item.items[0].content), critical, item.items[-1].content))
    return {"der": data, "tbs": encoded(tbs), "signature": signature.content[1:],
            "issuer": encoded(issuer), "subject": encoded(subject), "spki": encoded(spki),
            "not_before": times[0], "not_after": times[1], "extensions": parsed}


def check_profile(certificate, role, index=0, count=0):
    """role is 'leaf', 'intermediate' (index 0 issued the leaf) or 'anchor' (above `count` intermediates)."""
    values = {}
    for identifier, critical, value in certificate["extensions"]:
        require(identifier not in values, "certificate-encoding")
        der(value)
        require(identifier not in FORBIDDEN_EXTENSIONS, "unsupported-constraint")
        require(identifier in KNOWN_EXTENSIONS or not critical, "critical-extension")
        values[identifier] = (critical, value)
    if "2.5.29.14" in values:
        node = der(values["2.5.29.14"][1])
        require(node.tag == 0x04 and node.content, "key-identifier")
        certificate["ski"] = node.content
    if "2.5.29.35" in values:
        node = der(values["2.5.29.35"][1])
        require(node.tag == 0x30 and len(node.items) == 1 and node.items[0].tag == 0x80
                and node.items[0].content, "key-identifier")
        certificate["aki"] = node.items[0].content
    purposes = None
    if "2.5.29.37" in values:
        node = der(values["2.5.29.37"][1])
        role_reason = {"leaf": "leaf-eku", "intermediate": "intermediate-eku", "anchor": "root-eku"}[role]
        require(node.tag == 0x30 and node.items and all(item.tag == 0x06 for item in node.items), role_reason)
        purposes = {oid_text(item.content) for item in node.items}

    def basic(reason):
        critical, value = values.get("2.5.29.19", (False, None))
        require(value is not None, reason)
        node = der(value)
        require(node.tag == 0x30 and len(node.items) <= 2, reason)
        items = list(node.items)
        ca = False
        if items and items[0].tag == 0x01:
            require(items[0].content == b"\xff", reason)  # DER omits the default FALSE.
            ca = True
            items.pop(0)
        path_length = None
        if items:
            require(len(items) == 1 and items[0].tag == 0x02 and items[0].content[0] < 0x80, reason)
            path_length = int.from_bytes(items[0].content, "big")
        return critical, ca, path_length

    if role == "leaf":
        critical, ca, path_length = basic("leaf-basic-constraints")
        require(critical and not ca and path_length is None, "leaf-basic-constraints")
        require(values.get("2.5.29.15") == (True, b"\x03\x02\x07\x80"), "leaf-key-usage")
        require(purposes is not None and FFE_EKU in purposes and ANY_EKU not in purposes, "leaf-eku")
    elif role == "intermediate":
        critical, ca, path_length = basic("intermediate-basic-constraints")
        require(critical and ca, "intermediate-basic-constraints")
        require(path_length is not None and path_length >= index, "intermediate-path-length")
        require(values.get("2.5.29.15") == (True, b"\x03\x02\x01\x06"), "intermediate-key-usage")
        require(purposes is None or FFE_EKU in purposes or ANY_EKU in purposes, "intermediate-eku")
    else:
        if "2.5.29.19" in values:
            _, _, path_length = basic("root-path-length")
            require(path_length is None or path_length >= count, "root-path-length")
        require(purposes is None or FFE_EKU in purposes or ANY_EKU in purposes, "root-eku")


# ---------------------------------------------------------------- signatures

_CACHE = {}


def openssl(*arguments, data=None):
    return subprocess.run(["openssl", *arguments], input=data, capture_output=True)


def ecdsa_der(signature):
    node = der(signature, "signature-encoding")
    require(node.tag == 0x30 and len(node.items) == 2, "signature-encoding")
    for item in node.items:
        require(item.tag == 0x02 and item.content[0] < 0x80 and len(item.content) <= 33
                and any(item.content), "signature-encoding")


def verify_signature(spki, message, signature):
    key = hashlib.sha256(spki + b"|" + signature + b"|" + message).digest()
    if key not in _CACHE:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "key.der").write_bytes(spki)
            (folder / "signature.der").write_bytes(signature)
            (folder / "message").write_bytes(message)
            result = openssl("dgst", "-sha256", "-verify", str(folder / "key.der"), "-keyform", "DER",
                             "-signature", str(folder / "signature.der"), str(folder / "message"))
            _CACHE[key] = result.returncode == 0
    return _CACHE[key]


def public_from_private(pkcs8):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "key.der"
        path.write_bytes(pkcs8)
        result = openssl("pkey", "-inform", "DER", "-in", str(path), "-pubout", "-outform", "DER")
    require(result.returncode == 0, "credential")
    return result.stdout


# ---------------------------------------------------------------- chain

def canonical_base64(value, reason, size_reason="certificate-size"):
    require(isinstance(value, str) and value, reason)
    require(len(value) <= MAX_BASE64, size_reason)
    require(re.fullmatch(r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?", value), reason)
    raw = base64.b64decode(value)
    require(base64.b64encode(raw).decode() == value, reason)
    require(len(raw) <= MAX_CERTIFICATE, size_reason)
    return raw


def validate_chain(anchor_der, intermediate_ders, leaf_der, now, issued_at, expires_at):
    count = len(intermediate_ders)
    leaf = parse_certificate(leaf_der)
    intermediates = [parse_certificate(item) for item in intermediate_ders]
    anchor = parse_certificate(anchor_der)
    check_profile(leaf, "leaf")
    for index, item in enumerate(intermediates):
        check_profile(item, "intermediate", index)
    check_profile(anchor, "anchor", count=count)
    path = [leaf] + intermediates + [anchor]
    for position in range(len(path) - 1):
        child, parent = path[position], path[position + 1]
        link = "chain-root" if parent is anchor else "chain-link"
        require(verify_signature(parent["spki"], child["tbs"], child["signature"]), link)
        require(child["issuer"] == parent["subject"], "chain-name" if parent is not anchor else link)
        require(not (child.get("aki") and parent.get("ski")) or child["aki"] == parent["ski"], "key-identifier")
        require(parent["not_before"] <= child["not_before"] and child["not_after"] <= parent["not_after"],
                "validity-containment")
    for item in path:
        require(item["not_before"] <= now < item["not_after"], "certificate-time")
        require(item["not_before"] <= issued_at and expires_at <= item["not_after"], "certificate-time")
    return leaf


# ---------------------------------------------------------------- transcript

def values(headers, name):
    return [value for key, value in headers if key.lower() == name]


def lp(data):
    return struct.pack(">I", len(data)) + data


def binding(request, domain):
    url = urlsplit(request["url"])
    host = url.hostname.lower()
    authority = "[" + host + "]" if ":" in host else host
    if url.port is not None and url.port != {"https": 443, "http": 80}[url.scheme]:
        authority = f"{authority}:{url.port}"
    headers = request["headers"]
    parts = [domain, lp(request["method"].encode()), lp(url.scheme.encode()), lp(authority.encode()),
             lp(url.path.encode()), lp((("?" + url.query) if url.query else "").encode()),
             lp(bytes.fromhex(values(headers, PROOF + "request-nonce")[0])),
             hashlib.sha256(base64.b64decode(request["body_base64"])).digest(),
             hashlib.sha256(values(headers, "dd-client-token")[0].encode()).digest()]
    for name in SEMANTIC_HEADERS:
        found = values(headers, name)
        parts.append(b"\x01" + lp(found[0].encode()) if found else b"\x00")
    found = values(headers, "authorization")
    parts.append(b"\x01" + hashlib.sha256(found[0].encode()).digest() if found else b"\x00")
    return b"".join(parts)


def response_tail(body, issued_at, expires_at, leaf, intermediates, legacy=False):
    tail = struct.pack(">H", 200) + struct.pack(">Q", issued_at) + struct.pack(">Q", expires_at)
    tail += struct.pack(">Q", len(body)) + hashlib.sha256(body).digest() + hashlib.sha256(leaf).digest()
    if legacy:
        return tail + hashlib.sha256(intermediates[0]).digest()
    return tail + bytes([len(intermediates)]) + b"".join(hashlib.sha256(item).digest() for item in intermediates)


# ---------------------------------------------------------------- verifier

def check_request(request):
    url = urlsplit(request["url"])
    headers = request["headers"]
    require(request["method"] == "POST" and url.scheme == "https" and url.hostname, "request")
    require(url.username is None and url.password is None and not url.fragment, "request")
    require(values(headers, PROOF + "signature-version") == ["1"], "request")
    nonce = values(headers, PROOF + "request-nonce")
    require(len(nonce) == 1 and re.fullmatch(r"[0-9a-f]{32}", nonce[0]), "request")
    token = values(headers, "dd-client-token")
    require(len(token) == 1 and "," not in token[0], "request")
    for name in SEMANTIC_HEADERS + ["authorization"]:
        require(len(values(headers, name)) <= 1, "duplicate-semantic-header")
    capabilities = [item.strip() for item in (values(headers, "x-dd-feature-flags-capabilities") or [""])[0].split(",")]
    require("response-signing-v1" in capabilities, "request")


def verify(case, anchor_der):
    request, response, now = case["request"], case["response"], case["now"]
    check_request(request)
    require(response["status"] == 200, "response-status")
    proof = {}
    for name in ["signature-version", "signing-certificate", "signing-chain", "certificate-id",
                 "issued-at", "expires-at", "signature"]:
        found = values(response["headers"], PROOF + name)
        require(found, "missing-proof")
        require(len(found) == 1, "duplicate-proof")
        require(name == "signing-chain" or "," not in found[0], "combined-proof")
        proof[name] = found[0]
    require(proof["signature-version"] == "1", "protocol-version")
    leaf_der = canonical_base64(proof["signing-certificate"], "certificate-encoding")
    entries = proof["signing-chain"].split(",")
    require(1 <= len(entries) <= 3, "chain-count")
    chain = [canonical_base64(entry, "chain-encoding") for entry in entries]
    require(proof["certificate-id"] == hashlib.sha256(leaf_der).hexdigest(), "certificate-id")
    times = []
    for name in ["issued-at", "expires-at"]:
        require(re.fullmatch(r"0|[1-9][0-9]{0,15}", proof[name]), "canonical-time")
        times.append(int(proof[name]))
        require(times[-1] <= MAX_SAFE_INTEGER, "canonical-time")
    issued_at, expires_at = times
    require(issued_at <= now + 30 and now < expires_at and issued_at < expires_at
            and expires_at - issued_at <= 300, "response-time")
    leaf = validate_chain(anchor_der, chain, leaf_der, now, issued_at, expires_at)
    signature = canonical_base64(proof["signature"], "signature-encoding", "signature-encoding")
    require(len(signature) <= 72, "signature-encoding")
    ecdsa_der(signature)
    body = base64.b64decode(response["body_base64"])
    tail = response_tail(body, issued_at, expires_at, leaf_der, chain)
    message = binding(request, DOMAIN) + tail
    if verify_signature(leaf["spki"], message, signature):
        return message
    # Diagnose the rejection; any path below still rejects.
    for domain in OTHER_DOMAINS:
        require(not verify_signature(leaf["spki"], binding(request, domain) + tail, signature), "transcript-domain")
    if len(chain) == 1:
        legacy = binding(request, DOMAIN) + response_tail(body, issued_at, expires_at, leaf_der, chain, True)
        require(not verify_signature(leaf["spki"], legacy, signature), "transcript-tail")
    raise Reject("transcript-signature")


def can_sign(credential, case, anchor_der):
    """A signer accepts the credential only if it could emit a valid proof at `now`."""
    try:
        require(set(credential) == {"version", "generation", "private_key_pkcs8_der_base64",
                                    "certificate_der_base64", "intermediates_der_base64"}, "credential")
        require(credential["version"] == 1, "credential")
        require(isinstance(credential["generation"], str) and 0 < len(credential["generation"]) <= 128,
                "credential")
        chain = credential["intermediates_der_base64"]
        require(isinstance(chain, list) and 1 <= len(chain) <= 3, "credential")
        intermediates = [canonical_base64(item, "credential") for item in chain]
        leaf_der = canonical_base64(credential["certificate_der_base64"], "credential")
        key = base64.b64decode(credential["private_key_pkcs8_der_base64"], validate=True)
        now = case["now"]
        leaf = parse_certificate(leaf_der)
        expires_at = min(now + 300, leaf["not_after"])
        require(now < expires_at, "certificate-time")
        leaf = validate_chain(anchor_der, intermediates, leaf_der, now, now, expires_at)
        require(public_from_private(key) == leaf["spki"], "key-mismatch")
        return True
    except Reject:
        return False


def main():
    failures, response_count, signing_count = [], 0, 0
    for path in sorted(DIRECTORY.glob("*.json")):
        if path.name == "manifest.json":
            continue
        corpus = json.loads(path.read_bytes())
        by_id = {}
        for case in corpus["cases"]:
            anchor = base64.b64decode(case.get("anchor_der_base64", corpus["anchor_der_base64"]))
            by_id[case["id"]] = (case, anchor)
            try:
                message, reason = verify(case, anchor), None
            except Reject as rejection:
                message, reason = None, rejection.reason
            response_count += 1
            label = f"{path.name}:{case['id']}"
            if (message is not None) != case["expected_accept"]:
                failures.append(f"{label}: expected accept={case['expected_accept']}, got reason {reason}")
            elif message is not None and base64.b64decode(case["transcript_base64"]) != message:
                failures.append(f"{label}: transcript differs")
            elif message is None and reason != case["rejection_reason"]:
                failures.append(f"{label}: expected reason {case['rejection_reason']}, got {reason}")
            if case["expected_accept"] and "credential" in case:
                signing_count += 1
                if not can_sign(case["credential"], case, anchor):
                    failures.append(f"{label}: embedded credential cannot sign")
        for signing in corpus.get("signing_cases", []):
            case, anchor = by_id[signing["case_id"]]
            signing_count += 1
            if can_sign(signing["credential"], case, anchor) != signing["expected_signing"]:
                failures.append(f"{path.name}:{signing['id']}: expected signing={signing['expected_signing']}")
    for failure in failures:
        print("FAIL", failure)
    print(f"independent verifier: {response_count} response cases and {signing_count} signer checks, "
          f"{len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

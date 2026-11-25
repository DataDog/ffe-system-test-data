#!/usr/bin/env python3
"""Generate every response-signing v1 fixture file from fixed synthetic inputs.

This is the only way to regenerate response-signing/v1/*.json. It uses only the
Python standard library, so the output bytes do not depend on a crypto package
version. Keys come from fixed labels, and ECDSA uses RFC 6979 deterministic
nonces with low-S normalization, so a rerun writes identical bytes.

The generator never imports or calls a signer or verifier under test. Each
expected result is set here from the protocol rules. Run
ci/verify-response-signing-vectors.py to check every expectation with a
separate verifier.

Usage:
  python3 response-signing/generate-v1.py          # write the files
  python3 response-signing/generate-v1.py --check  # fail if a file differs
"""
import argparse
import base64
import calendar
import copy
import hashlib
import hmac
import json
from pathlib import Path
import struct
from urllib.parse import urlsplit

DIRECTORY = Path(__file__).resolve().parent / "v1"
PREFIX = "x-datadog-feature-flags-"
DOMAIN = b"datadog.feature-flags.precomputed-assignments.v1\0"
PROTOTYPE_CHAIN_DOMAIN = b"datadog.feature-flags.precomputed-assignments.v2\0"
DRAFT_V3_DOMAIN = b"datadog.feature-flags.precomputed-assignments.v3\0"
# PLACEHOLDER: 1.3.6.1.4.1.99999 is not a Datadog-owned arc. Datadog must
# assign the production FFE assignment-signing EKU OID before release. Change it
# here only, then regenerate every fixture file.
FFE_EKU = "1.3.6.1.4.1.99999.1.1"
OTHER_PRODUCT_EKU = "1.3.6.1.4.1.99999.1.2"
ANY_EKU = "2.5.29.37.0"
CODE_SIGNING_EKU = "1.3.6.1.5.5.7.3.3"
# The request and response headers that carry the signed header name lists.
SIGNED_HEADERS = PREFIX + "signed-headers"
SIGNED_RESPONSE_HEADERS = PREFIX + "signed-response-headers"
# Request headers of the edge `bound` class. Each one must be in the signed
# request list when it is present. A list can also name other headers.
BOUND_REQUEST_HEADERS = ["content-type", "dd-application-id", "x-dd-feature-flags-capabilities", "x-rkyv"]
# The synthetic SDK also lists the staging header x-use-cache when it sets it.
# A listed staging header is bound like any listed name. An unlisted one is not.
SDK_LISTED_HEADERS = BOUND_REQUEST_HEADERS + ["x-use-cache"]
DEFAULT_RESPONSE_LIST = "content-type,dd-flag-selection-ignored"
MAX_LISTED_NAMES = 32
MAX_NAME_LENGTH = 64

# ---------------------------------------------------------------------------
# P-256 ECDSA (FIPS 186-4) with RFC 6979 nonces.

CURVE_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
CURVE_A = CURVE_P - 3
CURVE_B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
CURVE_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
GENERATOR = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
             0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def point_add(left, right):
    if left is None:
        return right
    if right is None:
        return left
    if left[0] == right[0] and (left[1] + right[1]) % CURVE_P == 0:
        return None
    if left == right:
        slope = (3 * left[0] * left[0] + CURVE_A) * pow(2 * left[1], -1, CURVE_P)
    else:
        slope = (right[1] - left[1]) * pow(right[0] - left[0], -1, CURVE_P)
    x = (slope * slope - left[0] - right[0]) % CURVE_P
    return x, (slope * (left[0] - x) - left[1]) % CURVE_P


def point_multiply(scalar, point):
    result = None
    while scalar:
        if scalar & 1:
            result = point_add(result, point)
        point = point_add(point, point)
        scalar >>= 1
    return result


def rfc6979_nonce(secret, digest_bytes):
    key_bytes = secret.to_bytes(32, "big")
    message = (int.from_bytes(digest_bytes, "big") % CURVE_N).to_bytes(32, "big")
    v, k = b"\x01" * 32, b"\x00" * 32
    k = hmac.new(k, v + b"\x00" + key_bytes + message, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v + b"\x01" + key_bytes + message, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    while True:
        v = hmac.new(k, v, hashlib.sha256).digest()
        candidate = int.from_bytes(v, "big")
        if 1 <= candidate < CURVE_N:
            return candidate
        k = hmac.new(k, v + b"\x00", hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()


def ecdsa_sign(secret, message, high_s=False):
    digest_bytes = hashlib.sha256(message).digest()
    e = int.from_bytes(digest_bytes, "big")
    nonce = rfc6979_nonce(secret, digest_bytes)
    r = point_multiply(nonce, GENERATOR)[0] % CURVE_N
    s = pow(nonce, -1, CURVE_N) * (e + r * secret) % CURVE_N
    assert r and s
    if s > CURVE_N // 2:
        s = CURVE_N - s
    if high_s:
        # The same signature with s replaced by n - s. ECDSA accepts both forms,
        # and the edge signer emits the high-S form about half of the time.
        s = CURVE_N - s
    return sequence(integer(r), integer(s))


def ecdsa_verify(public, message, signature):
    """Self-check only: the separate CI verifier uses OpenSSL instead."""
    fields = children(signature)
    r, s = (int.from_bytes(value[2:], "big") for value in fields)
    point = (int.from_bytes(public[1:33], "big"), int.from_bytes(public[33:], "big"))
    e = int.from_bytes(hashlib.sha256(message).digest(), "big")
    w = pow(s, -1, CURVE_N)
    total = point_add(point_multiply(e * w % CURVE_N, GENERATOR), point_multiply(r * w % CURVE_N, point))
    return total is not None and total[0] % CURVE_N == r


class Key:
    """Synthetic P-256 key derived from a fixed public label."""

    def __init__(self, label):
        seed = hashlib.sha256(b"ffe response-signing v1 synthetic key/" + label.encode()).digest()
        self.secret = int.from_bytes(seed, "big") % (CURVE_N - 1) + 1
        x, y = point_multiply(self.secret, GENERATOR)
        self.public = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
        self.identifier = hashlib.sha1(self.public).digest()

    def sign(self, message, high_s=False):
        return ecdsa_sign(self.secret, message, high_s)

    def pkcs8(self):
        ec_private_key = sequence(integer(1), octet(self.secret.to_bytes(32, "big")),
                                  tlv(0xA1, bitstring(self.public)))
        return sequence(integer(0), sequence(oid("1.2.840.10045.2.1"), oid("1.2.840.10045.3.1.7")),
                        octet(ec_private_key))


# ---------------------------------------------------------------------------
# DER encoding.

def tlv(tag, content):
    size = len(content)
    if size < 128:
        length = bytes([size])
    else:
        raw = size.to_bytes((size.bit_length() + 7) // 8, "big")
        length = bytes([0x80 | len(raw)]) + raw
    return bytes([tag]) + length + content


def sequence(*items):
    return tlv(0x30, b"".join(items))


def integer(value):
    assert value >= 0
    raw = value.to_bytes(value.bit_length() // 8 + 1, "big")
    return tlv(0x02, raw)


def oid(dotted):
    parts = [int(part) for part in dotted.split(".")]
    body = bytearray([40 * parts[0] + parts[1]])
    for part in parts[2:]:
        chunk = [part & 0x7F]
        part >>= 7
        while part:
            chunk.append(0x80 | (part & 0x7F))
            part >>= 7
        body.extend(reversed(chunk))
    return tlv(0x06, bytes(body))


def octet(value):
    return tlv(0x04, value)


def bitstring(value):
    return tlv(0x03, b"\x00" + value)


def utf8_name(common_name):
    return sequence(tlv(0x31, sequence(oid("2.5.4.3"), tlv(0x0C, common_name.encode()))))


def der_time(text):
    seconds = timestamp(text)
    year = int(text[:4])
    compact = text.replace("-", "").replace(":", "").replace("T", "")
    if 1950 <= year < 2050:
        return tlv(0x17, (compact[2:] + "Z").encode()), seconds
    return tlv(0x18, (compact + "Z").encode()), seconds


def timestamp(text):
    return calendar.timegm((int(text[:4]), int(text[5:7]), int(text[8:10]),
                            int(text[11:13]), int(text[14:16]), int(text[17:19])))


def children(data):
    """Split one DER value into its raw child values (for generated input only)."""
    def bounds(offset):
        length = data[offset + 1]
        start = offset + 2
        if length & 0x80:
            count = length & 0x7F
            length = int.from_bytes(data[start:start + count], "big")
            start += count
        return start, start + length
    start, end = bounds(0)
    result = []
    while start < end:
        _, next_offset = bounds(start)
        result.append(data[start:next_offset])
        start = next_offset
    return result


# ---------------------------------------------------------------------------
# Certificates.

ALGORITHM = sequence(oid("1.2.840.10045.4.3.2"))
BASIC_CONSTRAINTS = oid("2.5.29.19")
KEY_USAGE = oid("2.5.29.15")
EXTENDED_KEY_USAGE = oid("2.5.29.37")
SUBJECT_KEY_ID = oid("2.5.29.14")
AUTHORITY_KEY_ID = oid("2.5.29.35")
LEAF_KEY_USAGE = b"\x03\x02\x07\x80"  # digitalSignature
CA_KEY_USAGE = b"\x03\x02\x01\x06"  # keyCertSign and cRLSign


def extension(identifier, value, critical=False):
    return sequence(identifier, b"\x01\x01\xff" if critical else b"", octet(value))


def ca_basic_constraints(path_length=None):
    return sequence(b"\x01\x01\xff", b"" if path_length is None else integer(path_length))


def eku_value(purposes):
    return sequence(*[oid(purpose) for purpose in purposes])


class Node:
    """One certificate with its subject key and encoded subject name."""

    def __init__(self, key, name, der, not_before, not_after):
        self.key, self.name, self.der = key, name, der
        self.not_before, self.not_after = not_before, not_after


def issue(label, subject_key, subject_name, issuer_key, issuer_name, not_before, not_after, extensions):
    serial_seed = bytearray(hashlib.sha256(b"serial/" + label.encode()).digest()[:16])
    serial_seed[0] = 0x40 | (serial_seed[0] & 0x3F)
    start, start_seconds = der_time(not_before)
    end, end_seconds = der_time(not_after)
    spki = sequence(sequence(oid("1.2.840.10045.2.1"), oid("1.2.840.10045.3.1.7")),
                    bitstring(subject_key.public))
    tbs = sequence(tlv(0xA0, integer(2)), integer(int.from_bytes(serial_seed, "big")), ALGORITHM,
                   issuer_name, sequence(start, end), subject_name, spki,
                   tlv(0xA3, sequence(*extensions)))
    der = sequence(tbs, ALGORITHM, bitstring(issuer_key.sign(tbs)))
    return Node(subject_key, subject_name, der, start_seconds, end_seconds)


def make_root(label, common_name, key=None, path_length=None, purposes=None,
              not_before="2026-09-11T00:00:00", not_after="2036-09-08T03:18:08"):
    key = key or Key(label)
    name = utf8_name(common_name)
    extensions = [extension(BASIC_CONSTRAINTS, ca_basic_constraints(path_length), True),
                  extension(KEY_USAGE, CA_KEY_USAGE, True),
                  extension(SUBJECT_KEY_ID, octet(key.identifier)),
                  extension(AUTHORITY_KEY_ID, sequence(tlv(0x80, key.identifier)))]
    if purposes is not None:
        extensions.append(extension(EXTENDED_KEY_USAGE, eku_value(purposes)))
    return issue(label, key, name, key, name, not_before, not_after, extensions)


def make_ca(label, common_name, parent, not_before, not_after, path_length=0, purposes=None,
            key=None, basic=None, usage=CA_KEY_USAGE, extra=()):
    key = key or Key(label)
    basic = ca_basic_constraints(path_length) if basic is None else basic
    extensions = [extension(BASIC_CONSTRAINTS, basic, True), extension(KEY_USAGE, usage, True),
                  extension(SUBJECT_KEY_ID, octet(key.identifier)),
                  extension(AUTHORITY_KEY_ID, sequence(tlv(0x80, parent.key.identifier)))]
    if purposes is not None:
        extensions.append(extension(EXTENDED_KEY_USAGE, eku_value(purposes)))
    extensions.extend(extra)
    return issue(label, key, utf8_name(common_name), parent.key, parent.name, not_before, not_after, extensions)


def make_leaf(label, parent, not_before="2026-10-27T00:00:00", not_after="2026-10-30T00:00:00",
              purposes=(FFE_EKU,), key=None, basic=b"\x30\x00", usage=LEAF_KEY_USAGE,
              authority=None, issuer_name=None, extra=(), common_name="Synthetic Assignment Leaf"):
    key = key or Key(label)
    authority = parent.key.identifier if authority is None else authority
    extensions = [extension(BASIC_CONSTRAINTS, basic, True), extension(KEY_USAGE, usage, True),
                  extension(SUBJECT_KEY_ID, octet(key.identifier)),
                  extension(AUTHORITY_KEY_ID, sequence(tlv(0x80, authority)))]
    if purposes is not None:
        extensions.append(extension(EXTENDED_KEY_USAGE, eku_value(purposes)))
    extensions.extend(extra)
    return issue(label, key, utf8_name(common_name), parent.key, issuer_name or parent.name,
                 not_before, not_after, extensions)


# ---------------------------------------------------------------------------
# Wire format and transcript.

def encode(value):
    return base64.b64encode(value).decode("ascii")


def digest(value):
    return hashlib.sha256(value).digest()


def length_prefixed(value):
    return struct.pack(">I", len(value)) + value


def header_values(headers, name):
    return [value for key, value in headers if key.lower() == name]


def listed_names(headers, list_header):
    """The names in one signed list header, as sent. Empty when the header is absent."""
    values = header_values(headers, list_header)
    return values[0].split(",") if values else []


def name_values(names, headers):
    """u8(count), then lp(name) || u8(presence) || lp(value) for each listed name."""
    output = bytes([len(names)])
    for name in names:
        values = header_values(headers, name)
        output += length_prefixed(name.encode())
        # An absent header binds presence 0 and an empty value.
        output += b"\x01" + length_prefixed(values[0].encode()) if values else b"\x00" + length_prefixed(b"")
    return output


def request_prefix(request, domain=DOMAIN, layout="lists"):
    """Bytes before the response fields: the v1 request binding.

    `layout="fixed"` writes the previous v1 layout: five fixed header slots and
    no name list. Only the `previous-v1-header-layout` rejection uses it.
    """
    url = urlsplit(request["url"])
    headers = request["headers"]
    host = url.hostname
    authority = f"[{host}]" if ":" in host else host
    if url.port is not None and url.port != {"https": 443, "http": 80}[url.scheme]:
        authority += f":{url.port}"
    nonce = bytes.fromhex(header_values(headers, PREFIX + "request-nonce")[0])
    body = base64.b64decode(request["body_base64"])
    output = domain
    for value in [request["method"], url.scheme, authority, url.path,
                  # A URL that ends in "?" keeps the "?", the same as the edge.
                  f"?{url.query}" if "?" in request["url"] else ""]:
        output += length_prefixed(value.encode())
    output += length_prefixed(nonce) + digest(body)
    output += digest(header_values(headers, "dd-client-token")[0].encode())
    if layout == "fixed":
        for name in ["content-type", "dd-application-id", "x-rkyv", "x-use-cache",
                     "x-dd-feature-flags-capabilities"]:
            values = header_values(headers, name)
            output += b"\x00" if not values else b"\x01" + length_prefixed(values[0].encode())
    else:
        output += name_values(listed_names(headers, SIGNED_HEADERS), headers)
    values = header_values(headers, "authorization")
    output += b"\x00" if not values else b"\x01" + digest(values[0].encode())
    return output


def transcript(request, response_headers, body, issued_at, expires_at, leaf, intermediates, domain=DOMAIN,
               legacy_tail=False, layout="lists"):
    output = request_prefix(request, domain, layout)
    output += struct.pack(">HQQQ", 200, issued_at, expires_at, len(body)) + digest(body) + digest(leaf)
    if legacy_tail:
        # The removed single-intermediate tail: one digest and no count byte.
        assert len(intermediates) == 1
        return output + digest(intermediates[0])
    output += bytes([len(intermediates)])
    for intermediate in intermediates:
        output += digest(intermediate)
    if layout == "fixed":
        return output
    return output + name_values(listed_names(response_headers, SIGNED_RESPONSE_HEADERS), response_headers)


REQUEST_BODY = b'{"subject":{"id":"synthetic-user","country":"US"},"dd_env":"production"}'
# A request with a flag selection in data.attributes.flag_selection, as the
# SDKs send it. The response list must then name dd-flag-selection-ignored.
SELECTION_REQUEST_BODY = (b'{"data":{"type":"precompute-assignments-request","attributes":{'
                          b'"subject":{"id":"synthetic-user","country":"US"},"dd_env":"production",'
                          b'"flag_selection":{"tags":["team:payments"],"key_patterns":null}}}}')
# A top-level flag_selection is not a selection. The edge reads only
# data.attributes.flag_selection.
TOP_LEVEL_SELECTION_REQUEST_BODY = (b'{"subject":{"id":"synthetic-user","country":"US"},"dd_env":"production",'
                                    b'"flag_selection":{"tags":["team:payments"],"key_patterns":null}}')
RESPONSE_BODY = (b'{"flags":{"critical-demo":{"variation":"off","value":false}},'
                 b'"rulesRevision":"synthetic-r1","label":"caf\xc3\xa9"}')
# Fixed gzip bytes of RESPONSE_BODY; zlib output can differ between builds.
GZIP_RESPONSE_BODY = ("H4sIAAAAAAACAyXMwQnDMAxG4V3+c3Lo1WN0A9WVEoFqg+UYgvFAnaOLxSXXj8frEKPNETpi0aqRbH3zJ/+hUVGqmhMC"
                      "sgiWKXYwgpA5j7GgHMb+5KZ+V36muvO8rOUxc6MX2+RI8vtiXPbTAXRsAAAA")
BASE_URL = "https://flags.example.test:443/precompute/assignments?dd_env=production&marker=a%2Fb"
NOW = timestamp("2026-10-27T01:00:00")


def nonce_for(case_id):
    return hashlib.sha256(b"nonce/" + case_id.encode()).hexdigest()[:32]


def default_list(headers):
    """The signed request list that the synthetic SDK sends for these headers."""
    return ",".join(sorted({key.lower() for key, _ in headers if key.lower() in SDK_LISTED_HEADERS}))


DEFAULT_HEADERS = [["content-type", "application/json"], ["dd-client-token", "synthetic-client-token"],
                   ["dd-application-id", "synthetic-app"], ["x-use-cache", "true"],
                   ["x-dd-feature-flags-capabilities", "response-signing-v1"],
                   [PREFIX + "signature-version", "1"]]


def make_request(case_id, url=BASE_URL, headers=None, body=REQUEST_BODY, signed_headers=None):
    headers = copy.deepcopy(DEFAULT_HEADERS if headers is None else headers)
    signed_headers = default_list(headers) if signed_headers is None else signed_headers
    headers = headers + [[SIGNED_HEADERS, signed_headers], [PREFIX + "request-nonce", nonce_for(case_id)]]
    return {"url": url, "method": "POST", "headers": headers, "body_base64": encode(body)}


def credential(generation, leaf, intermediates, key=None):
    return {"version": 1, "generation": generation,
            "private_key_pkcs8_der_base64": encode((key or leaf.key).pkcs8()),
            "certificate_der_base64": encode(leaf.der),
            "intermediates_der_base64": [encode(node.der) for node in intermediates]}


def signed_case(case_id, leaf, intermediates, accept, reason, now=NOW, issued_at=None, expires_at=None,
                request=None, anchor=None, domain=DOMAIN, legacy_tail=False, signed_intermediates=None,
                leaf_der=None, include_credential=None, include_transcript=False, wire=False,
                high_s=False, response_list=DEFAULT_RESPONSE_LIST, response_extra=(), layout="lists"):
    """Build one response signed by `leaf.key` over the chain transcript.

    `response_extra` adds response headers before signing. `response_list` is the
    signed response list value, or None to omit the list header.
    """
    request = request or make_request(case_id)
    issued_at = now if issued_at is None else issued_at
    expires_at = min(issued_at + 300, leaf.not_after) if expires_at is None else expires_at
    leaf_der = leaf.der if leaf_der is None else leaf_der
    chain = [node.der for node in intermediates]
    signed_chain = chain if signed_intermediates is None else [node.der for node in signed_intermediates]
    body = RESPONSE_BODY
    headers = [["content-type", "application/json"], ["cache-control", "no-store, no-transform"],
               *[list(pair) for pair in response_extra],
               [PREFIX + "signature-version", "1"],
               [PREFIX + "signing-certificate", encode(leaf_der)],
               [PREFIX + "signing-chain", ",".join(encode(der) for der in chain)],
               [PREFIX + "certificate-id", digest(leaf_der).hex()],
               [PREFIX + "issued-at", str(issued_at)], [PREFIX + "expires-at", str(expires_at)]]
    if response_list is not None:
        headers.append([SIGNED_RESPONSE_HEADERS, response_list])
    signed = transcript(request, headers, body, issued_at, expires_at, leaf_der, signed_chain, domain,
                        legacy_tail, layout)
    signature = leaf.key.sign(signed, high_s)
    assert ecdsa_verify(leaf.key.public, signed, signature)
    headers.append([PREFIX + "signature", encode(signature)])
    response = {"status": 200, "headers": headers, "body_base64": encode(body)}
    if wire:
        response["headers"].append(["content-encoding", "gzip"])
        response["wire_body_base64"] = GZIP_RESPONSE_BODY
    case = {"id": case_id, "request": request, "response": response, "now": now,
            "expected_accept": accept, "rejection_reason": reason,
            "transcript_base64": encode(signed) if accept or include_transcript else None}
    if accept:
        # The values that verification returns. An SDK acts on these, not on a second read.
        case["verified_response_headers"] = {
            name: (header_values(headers, name) or [None])[0] for name in listed_names(headers, SIGNED_RESPONSE_HEADERS)}
    if anchor is not None:
        case["anchor_der_base64"] = encode(anchor.der)
    if include_credential if include_credential is not None else accept:
        case["credential"] = credential(case_id, leaf, intermediates)
    return case


def set_header(case, name, value):
    headers = case["response"]["headers"]
    index = [key for key, _ in headers].index(PREFIX + name)
    headers[index][1] = value


def remove_header(case, name):
    case["response"]["headers"] = [pair for pair in case["response"]["headers"] if pair[0] != PREFIX + name]


def mutated(base, case_id, reason, transform):
    """Copy a signed accepted case, then change bytes after signing."""
    case = copy.deepcopy(base)
    case.update(id=case_id, expected_accept=False, rejection_reason=reason, transcript_base64=None)
    case.pop("credential", None)
    case.pop("verified_response_headers", None)
    transform(case)
    return case


def signing_case(case_id, response_case, cred, expected):
    return {"id": case_id, "case_id": response_case, "credential": cred, "expected_signing": expected}


# The shared SDK reason code for each rule code. These are the browser verifier's
# codes, chosen as the one reference for every SDK. Each rejected case records
# its code as `sdk_reason`. A wrong header text encoding is a proof problem, so
# `certificate-encoding` from a malformed base64 header maps to `invalid-proof`.
SDK_REASONS = {
    "canonical-time": "invalid-proof", "certificate-encoding": "invalid-certificate",
    "certificate-id": "invalid-proof", "certificate-size": "invalid-proof",
    "certificate-time": "expired-proof", "chain-count": "invalid-proof", "chain-encoding": "invalid-proof",
    "chain-link": "invalid-certificate", "chain-name": "invalid-certificate",
    "chain-root": "invalid-certificate", "combined-proof": "invalid-proof",
    "critical-extension": "invalid-certificate", "duplicate-proof": "invalid-proof",
    "duplicate-semantic-header": "unsupported-request",
    "intermediate-basic-constraints": "invalid-certificate", "intermediate-eku": "invalid-certificate",
    "intermediate-key-usage": "invalid-certificate", "intermediate-path-length": "invalid-certificate",
    "key-identifier": "invalid-certificate", "leaf-basic-constraints": "invalid-certificate",
    "leaf-eku": "invalid-certificate", "leaf-key-usage": "invalid-certificate", "missing-proof": "missing-proof",
    "protocol-version": "invalid-proof", "response-status": "invalid-proof", "response-time": "expired-proof",
    "root-eku": "invalid-certificate", "root-path-length": "invalid-certificate",
    "signature-encoding": "invalid-proof", "transcript-domain": "invalid-signature",
    "transcript-signature": "invalid-signature", "transcript-tail": "invalid-signature",
    "unsupported-constraint": "invalid-certificate", "validity-containment": "invalid-certificate",
    "leaf-lifetime": "invalid-certificate",
    # The SDK checks its own request before it sends it.
    "signed-headers-missing": "unsupported-request", "signed-headers-syntax": "unsupported-request",
    "signed-headers-limit": "unsupported-request", "signed-headers-duplicate": "unsupported-request",
    "signed-headers-order": "unsupported-request", "signed-headers-forbidden": "unsupported-request",
    "signed-headers-required": "unsupported-request", "signed-header-absent": "unsupported-request",
    "unlisted-bound-header": "unsupported-request", "combined-semantic-header": "unsupported-request",
    # The signed response list is part of the proof.
    "response-headers-syntax": "invalid-proof", "response-headers-limit": "invalid-proof",
    "response-headers-duplicate": "invalid-proof", "response-headers-order": "invalid-proof",
    "response-headers-forbidden": "invalid-proof", "response-headers-required": "invalid-proof",
    "duplicate-response-header": "invalid-proof", "transcript-layout": "invalid-signature",
}
SDK_REASON_OVERRIDES = {"malformed-certificate-base64": "invalid-proof"}


def with_sdk_reasons(files):
    """Insert `sdk_reason` after `rejection_reason` in every rejected case."""
    for corpus_value in files.values():
        for index, case in enumerate(corpus_value["cases"]):
            if case["expected_accept"]:
                continue
            reason = SDK_REASON_OVERRIDES.get(case["id"], SDK_REASONS[case["rejection_reason"]])
            ordered = {}
            for key, value in case.items():
                ordered[key] = value
                if key == "rejection_reason":
                    ordered["sdk_reason"] = reason
            corpus_value["cases"][index] = ordered


# ---------------------------------------------------------------------------
# The PKI used by corpus.json.

ROOT_NAME = "SYNTHETIC RESPONSE SIGNING V1 TEST ROOT - NOT FOR PRODUCTION"
ROOT = make_root("root", ROOT_NAME)
INTERMEDIATE = make_ca("intermediate-2026", "Synthetic Intermediate 2026", ROOT,
                       "2026-10-01T00:00:00", "2027-10-01T00:00:00", path_length=0)
LEAF = make_leaf("leaf-2026", INTERMEDIATE)
# Two-intermediate hierarchy: root -> upper intermediate -> lower intermediate -> leaf.
UPPER = make_ca("upper-2026", "Synthetic Upper Intermediate 2026", ROOT,
             "2026-09-15T00:00:00", "2028-09-15T00:00:00", path_length=1)
LOWER = make_ca("lower-2026", "Synthetic Lower Intermediate 2026", UPPER,
                "2026-10-01T00:00:00", "2027-04-01T00:00:00", path_length=0)
LOWER_LEAF = make_leaf("leaf-lower-2026", LOWER)


def corpus():
    cases, signing = [], []
    add = cases.append

    # Accepted controls.
    base = signed_case("valid-current", LEAF, [INTERMEDIATE], True, None)
    add(base)
    rotated = make_leaf("leaf-2026-rotated", INTERMEDIATE, "2026-10-28T00:00:00", "2026-10-31T00:00:00")
    add(signed_case("valid-rotated-leaf", rotated, [INTERMEDIATE], True, None,
                    now=timestamp("2026-10-28T01:00:00")))
    later = make_ca("intermediate-2032", "Synthetic Intermediate 2032", ROOT,
                    "2032-08-01T00:00:00", "2033-08-01T00:00:00", path_length=0)
    later_leaf = make_leaf("leaf-2032", later, "2032-10-27T00:00:00", "2032-10-30T00:00:00")
    add(signed_case("valid-2032-rotated-intermediate-no-history", later_leaf, [later], True, None,
                    now=timestamp("2032-10-27T01:00:00")))
    headers = [["content-type", "application/json"], ["x-use-cache", "true"],
               ["x-dd-feature-flags-capabilities", "response-signing-v1"], [PREFIX + "signature-version", "1"],
               ["dd-client-token", "synthetic-overridden-token"],
               ["authorization", "Bearer synthetic-opaque-value"], ["dd-application-id", ""]]
    request = make_request("valid-effective-token-and-authorization", headers=headers)
    authorized = signed_case("valid-effective-token-and-authorization", LEAF, [INTERMEDIATE], True, None,
                             request=request)
    add(authorized)
    add(signed_case("valid-gzip-application-bytes", LEAF, [INTERMEDIATE], True, None, wire=True))
    headers = [["content-type", "application/json"], ["dd-client-token", "synthetic-client-token"],
               ["x-dd-feature-flags-capabilities", "response-signing-v1"], [PREFIX + "signature-version", "1"]]
    request = make_request("valid-ipv6-and-absent-optional-headers",
                           url="https://[2001:db8::1]:8443/precompute/assignments", headers=headers)
    add(signed_case("valid-ipv6-and-absent-optional-headers", LEAF, [INTERMEDIATE], True, None, request=request))
    two = signed_case("valid-two-intermediates", LOWER_LEAF, [LOWER, UPPER], True, None)
    add(two)
    lower_b = make_ca("lower-2026-b", "Synthetic Lower Intermediate 2026 B", UPPER,
                      "2026-10-20T00:00:00", "2027-04-20T00:00:00", path_length=0)
    lower_b_leaf = make_leaf("leaf-lower-2026-b", lower_b, "2026-10-28T00:00:00", "2026-10-31T00:00:00")
    add(signed_case("valid-rotated-lower-intermediate-no-history", lower_b_leaf, [lower_b, UPPER], True, None,
                    now=timestamp("2026-10-28T01:00:00")))
    top = make_ca("three-top", "Synthetic Three Level Top", ROOT,
                  "2026-09-15T00:00:00", "2028-09-15T00:00:00", path_length=2)
    middle = make_ca("three-middle", "Synthetic Three Level Middle", top,
                     "2026-09-20T00:00:00", "2028-03-20T00:00:00", path_length=1)
    lower = make_ca("three-lower", "Synthetic Three Level Lower", middle,
                    "2026-10-01T00:00:00", "2027-04-01T00:00:00", path_length=0)
    three_leaf = make_leaf("leaf-three", lower)
    three = signed_case("valid-three-intermediates", three_leaf, [lower, middle, top], True, None)
    add(three)
    leaf = make_leaf("valid-leaf-eku-ffe-and-other-oids", INTERMEDIATE,
                     purposes=(CODE_SIGNING_EKU, FFE_EKU, OTHER_PRODUCT_EKU))
    add(signed_case("valid-leaf-eku-ffe-and-other-oids", leaf, [INTERMEDIATE], True, None))
    for case_id, purposes in [("valid-intermediate-eku-ffe", (FFE_EKU,)),
                              ("valid-intermediate-eku-any", (ANY_EKU,))]:
        parent = make_ca(case_id, case_id, ROOT, "2026-10-01T00:00:00", "2027-10-01T00:00:00",
                         purposes=purposes)
        add(signed_case(case_id, make_leaf(case_id + "-leaf", parent), [parent], True, None))
    parent = make_ca("intermediate-pathlen-one", "intermediate-pathlen-one", ROOT,
                     "2026-10-01T00:00:00", "2027-10-01T00:00:00", path_length=1)
    add(signed_case("intermediate-pathlen-one", make_leaf("intermediate-pathlen-one-leaf", parent),
                    [parent], True, None))
    root_variants = {
        "valid-root-pathlen-equals-chain-length": make_root("root-pathlen-2", ROOT_NAME, ROOT.key, path_length=2),
        "valid-root-eku-ffe": make_root("root-eku-ffe", ROOT_NAME, ROOT.key, purposes=(FFE_EKU,)),
        "valid-root-eku-any": make_root("root-eku-any", ROOT_NAME, ROOT.key, purposes=(ANY_EKU,)),
    }
    for case_id, anchor in root_variants.items():
        add(signed_case(case_id, LOWER_LEAF, [LOWER, UPPER], True, None, anchor=anchor,
                        request=make_request(case_id)))
    # The same lower key and name, issued directly by the root, is a second valid path.
    lower_direct = make_ca("lower-2026-direct", "Synthetic Lower Intermediate 2026", ROOT,
                           "2026-10-01T00:00:00", "2027-04-01T00:00:00", key=LOWER.key)
    add(signed_case("valid-cross-issued-lower-intermediate", LOWER_LEAF, [lower_direct], True, None))

    # Chain-of-trust and certificate-profile rejections.
    rogue_root = make_root("rogue-root", "Synthetic Unrelated Root")
    rogue = make_ca("rogue-intermediate", "Synthetic Wrong Intermediate", rogue_root,
                    "2026-10-01T00:00:00", "2027-10-01T00:00:00")
    add(signed_case("unrelated-root", make_leaf("rogue-leaf", rogue), [rogue], False, "chain-root"))
    add(signed_case("direct-leaf-under-root", make_leaf("direct-leaf", ROOT), [INTERMEDIATE], False, "chain-link"))
    add(signed_case("expired-leaf", make_leaf("expired-leaf", INTERMEDIATE, "2026-10-24T01:00:00",
                                              "2026-10-27T00:59:59"),
                    [INTERMEDIATE], False, "certificate-time", expires_at=NOW + 300))
    add(signed_case("future-leaf", make_leaf("future-leaf", INTERMEDIATE, "2026-10-27T01:00:01",
                                             "2026-10-30T01:00:00"),
                    [INTERMEDIATE], False, "certificate-time"))
    variants = [
        ("leaf-ca-true", dict(basic=ca_basic_constraints(0), usage=CA_KEY_USAGE), "leaf-basic-constraints"),
        ("leaf-wrong-key-usage", dict(usage=b"\x03\x02\x05\xa0"), "leaf-key-usage"),
        ("leaf-wrong-eku", dict(purposes=(CODE_SIGNING_EKU,)), "leaf-eku"),
        ("leaf-eku-other-product-only", dict(purposes=(OTHER_PRODUCT_EKU,)), "leaf-eku"),
        ("leaf-eku-any-extended-key-usage", dict(purposes=(FFE_EKU, ANY_EKU)), "leaf-eku"),
        ("leaf-eku-missing", dict(purposes=None), "leaf-eku"),
        ("leaf-unknown-critical-extension",
         dict(extra=[extension(oid("1.2.3.4.5.6.7"), b"\x05\x00", True)]), "critical-extension"),
        ("leaf-issuer-name-mismatch", dict(issuer_name=utf8_name("Different Issuer Name")), "chain-name"),
        ("leaf-aki-mismatch", dict(authority=b"\x42" * 20), "key-identifier"),
        ("leaf-outlives-intermediate", dict(not_after="2027-10-01T00:00:01"), "validity-containment"),
        ("leaf-unsupported-name-constraints",
         dict(extra=[extension(oid("2.5.29.30"), bytes.fromhex("3015a0133011820f726573747269637465642e74657374"),
                               True)]), "unsupported-constraint"),
    ]
    leaves = {}
    for case_id, options, reason in variants:
        leaves[case_id] = make_leaf(case_id, INTERMEDIATE, **options)
        add(signed_case(case_id, leaves[case_id], [INTERMEDIATE], False, reason))
    # F16: the leaf spans at most 432300 seconds (120 hours and 5 minutes).
    add(signed_case("valid-leaf-lifetime-at-limit",
                    make_leaf("valid-leaf-lifetime-at-limit", INTERMEDIATE, not_after="2026-11-01T00:05:00"),
                    [INTERMEDIATE], True, None))
    add(signed_case("leaf-lifetime-over-limit",
                    make_leaf("leaf-lifetime-over-limit", INTERMEDIATE, not_after="2026-11-01T00:05:01"),
                    [INTERMEDIATE], False, "leaf-lifetime"))
    for case_id, options, reason in [
        ("intermediate-ca-false", dict(basic=b"\x30\x00"), "intermediate-basic-constraints"),
        ("intermediate-pathlen-absent", dict(path_length=None), "intermediate-path-length"),
        ("intermediate-ku-missing-crl-sign", dict(usage=b"\x03\x02\x02\x04"), "intermediate-key-usage"),
        ("intermediate-wrong-eku", dict(purposes=(CODE_SIGNING_EKU,)), "intermediate-eku"),
    ]:
        parent = make_ca(case_id, case_id, ROOT, "2026-10-01T00:00:00", "2027-10-01T00:00:00", **options)
        add(signed_case(case_id, make_leaf(case_id + "-leaf", parent), [parent], False, reason))
    short_upper = make_ca("upper-pathlen-zero", "Synthetic Upper Intermediate 2026", ROOT,
                       "2026-09-15T00:00:00", "2028-09-15T00:00:00", path_length=0, key=UPPER.key)
    add(signed_case("intermediate-pathlen-too-small-at-index-1", LOWER_LEAF, [LOWER, short_upper], False,
                    "intermediate-path-length"))
    for case_id, anchor, chain, reason in [
        ("root-pathlen-below-chain-length", make_root("root-pathlen-1", ROOT_NAME, ROOT.key, path_length=1),
         [LOWER, UPPER], "root-path-length"),
        ("root-pathlen-zero", make_root("root-pathlen-0", ROOT_NAME, ROOT.key, path_length=0), [INTERMEDIATE],
         "root-path-length"),
        ("root-eku-codesigning", make_root("root-eku-codesigning", ROOT_NAME, ROOT.key,
                                           purposes=(CODE_SIGNING_EKU,)), [LOWER, UPPER], "root-eku"),
    ]:
        leaf = LOWER_LEAF if len(chain) == 2 else LEAF
        add(signed_case(case_id, leaf, chain, False, reason, anchor=anchor))
    add(signed_case("missing-middle-intermediate", LOWER_LEAF, [LOWER], False, "chain-root"))
    # Both path lengths allow either position, so only the order is wrong.
    upper = make_ca("reversed-upper", "Synthetic Reversed Upper", ROOT,
                    "2026-09-15T00:00:00", "2028-09-15T00:00:00", path_length=1)
    lower_one = make_ca("reversed-lower", "Synthetic Reversed Lower", upper,
                        "2026-10-01T00:00:00", "2027-04-01T00:00:00", path_length=1)
    add(signed_case("reversed-chain-order", make_leaf("reversed-leaf", lower_one), [upper, lower_one], False,
                    "chain-link"))
    q1 = make_ca("four-1", "Synthetic Four Level 1", ROOT, "2026-09-15T00:00:00", "2028-09-15T00:00:00",
                 path_length=3)
    q2 = make_ca("four-2", "Synthetic Four Level 2", q1, "2026-09-16T00:00:00", "2028-09-14T00:00:00",
                 path_length=2)
    q3 = make_ca("four-3", "Synthetic Four Level 3", q2, "2026-09-17T00:00:00", "2028-09-13T00:00:00",
                 path_length=1)
    q4 = make_ca("four-4", "Synthetic Four Level 4", q3, "2026-10-01T00:00:00", "2027-04-01T00:00:00")
    four_leaf = make_leaf("leaf-four", q4)
    add(signed_case("four-intermediates", four_leaf, [q4, q3, q2, q1], False, "chain-count"))
    lower_b64, upper_b64 = encode(LOWER.der), encode(UPPER.der)
    for case_id, value in [("chain-empty-entry", f"{lower_b64},,{upper_b64}"),
                           ("chain-trailing-comma", f"{lower_b64},{upper_b64},"),
                           ("chain-space-after-comma", f"{lower_b64}, {upper_b64}"),
                           ("chain-entry-not-base64", f"{lower_b64},not@base64")]:
        case = signed_case(case_id, LOWER_LEAF, [LOWER, UPPER], False, "chain-encoding")
        set_header(case, "signing-chain", value)
        add(case)
    padding = extension(oid("1.2.3.4"), octet(b"\x00" * 3800))
    big = make_ca("chain-entry-oversized", "chain-entry-oversized", ROOT,
                  "2026-10-01T00:00:00", "2027-10-01T00:00:00", extra=[padding])
    assert len(big.der) > 4096
    add(signed_case("chain-entry-oversized", make_leaf("chain-entry-oversized-leaf", big), [big], False,
                    "certificate-size"))
    case = signed_case("legacy-intermediate-header-only", LEAF, [INTERMEDIATE], False, "missing-proof")
    headers = case["response"]["headers"]
    headers[[key for key, _ in headers].index(PREFIX + "signing-chain")][0] = PREFIX + "signing-intermediate"
    add(case)
    case = signed_case("duplicate-chain-header", LOWER_LEAF, [LOWER, UPPER], False, "duplicate-proof")
    case["response"]["headers"].append([PREFIX + "signing-chain", f"{lower_b64},{upper_b64}"])
    add(case)
    add(signed_case("chain-differs-from-signed-chain", LOWER_LEAF, [lower_direct], False, "transcript-signature",
                    signed_intermediates=[LOWER, UPPER]))
    add(signed_case("legacy-v1-transcript-tail", LEAF, [INTERMEDIATE], False, "transcript-tail",
                    legacy_tail=True))
    add(mutated(base, "missing-intermediate", "missing-proof", lambda c: remove_header(c, "signing-chain")))

    # Request and response binding rejections.
    def change_body(c):
        c["response"]["body_base64"] = encode(RESPONSE_BODY + b" ")
    add(mutated(base, "changed-response-bytes", "transcript-signature", change_body))

    def change_request_body(c):
        c["request"]["body_base64"] = encode(REQUEST_BODY + b" ")
    add(mutated(base, "changed-request-body", "transcript-signature", change_request_body))

    def request_header(name, value):
        def transform(c):
            headers = c["request"]["headers"]
            headers[[key for key, _ in headers].index(name)][1] = value
        return transform
    add(mutated(base, "changed-nonce", "transcript-signature",
                request_header(PREFIX + "request-nonce", "0" * 32)))
    add(mutated(base, "changed-effective-token", "transcript-signature",
                request_header("dd-client-token", "different-token")))

    def url(value):
        def transform(c):
            c["request"]["url"] = value
        return transform
    add(mutated(base, "changed-query-order", "transcript-signature",
                url("https://flags.example.test:443/precompute/assignments?marker=a%2Fb&dd_env=production")))
    add(mutated(base, "changed-authority", "transcript-signature",
                url("https://other.example.test:443/precompute/assignments?dd_env=production&marker=a%2Fb")))
    add(mutated(base, "changed-semantic-header", "transcript-signature", request_header("x-use-cache", "false")))

    def status(c):
        c["response"]["status"] = 201
    add(mutated(base, "changed-http-status", "response-status", status))
    add(signed_case("future-issued-at", LEAF, [INTERMEDIATE], False, "response-time", issued_at=NOW + 31))
    add(signed_case("expired-response", LEAF, [INTERMEDIATE], False, "response-time", issued_at=NOW - 300))
    add(signed_case("excess-response-lifetime", LEAF, [INTERMEDIATE], False, "response-time",
                    expires_at=NOW + 301))
    add(mutated(base, "noncanonical-issued-at", "canonical-time",
                lambda c: set_header(c, "issued-at", "0" + str(NOW))))
    add(mutated(base, "duplicate-proof-header", "duplicate-proof",
                lambda c: c["response"]["headers"].append([PREFIX + "signature-version", "1"])))

    def combined(c):
        remove_header(c, "signature-version")
        c["response"]["headers"].append([PREFIX + "signature-version", "1, 1"])
    add(mutated(base, "comma-combined-proof-header", "combined-proof", combined))
    add(mutated(base, "oversized-certificate", "certificate-size",
                lambda c: set_header(c, "signing-certificate", encode(b"\x00" * 4097))))
    add(mutated(base, "malformed-certificate-base64", "certificate-encoding",
                lambda c: set_header(c, "signing-certificate", "not@base64")))
    signature = base64.b64decode(dict(base["response"]["headers"])[PREFIX + "signature"])
    add(mutated(base, "signature-trailing-der", "signature-encoding",
                lambda c: set_header(c, "signature", encode(signature + b"\x00"))))
    add(signed_case("certificate-trailing-der", LEAF, [INTERMEDIATE], False, "certificate-encoding",
                    leaf_der=LEAF.der + b"\x00", include_transcript=True))
    r, s = (int.from_bytes(value[2:], "big") for value in children(signature))
    add(mutated(base, "cryptographic-signature-tampering", "transcript-signature",
                lambda c: set_header(c, "signature", encode(sequence(integer(r), integer(s + 1))))))
    add(mutated(base, "duplicate-request-semantic-header", "duplicate-semantic-header",
                lambda c: c["request"]["headers"].append(["x-use-cache", "true"])))
    for version in ["2", "3"]:
        add(mutated(base, f"unsupported-prototype-version-{version}", "protocol-version",
                    lambda c, v=version: set_header(c, "signature-version", v)))
    add(signed_case("draft-v3-domain", LEAF, [INTERMEDIATE], False, "transcript-domain", domain=DRAFT_V3_DOMAIN))
    add(signed_case("chain-v2-prototype-domain", LEAF, [INTERMEDIATE], False, "transcript-domain",
                    domain=PROTOTYPE_CHAIN_DOMAIN))

    # Signer cases: each signs the referenced case's request and body at its `now`.
    good = credential("valid-current", LEAF, [INTERMEDIATE])
    signing += [
        signing_case("signer-valid-key-pair", "valid-current", good, True),
        signing_case("signer-private-key-mismatch", "valid-current",
                     credential("valid-current", LEAF, [INTERMEDIATE], key=rotated.key), False),
        signing_case("signer-two-intermediates", "valid-two-intermediates",
                     credential("two", LOWER_LEAF, [LOWER, UPPER]), True),
        signing_case("signer-three-intermediates", "valid-three-intermediates",
                     credential("three", three_leaf, [lower, middle, top]), True),
        signing_case("signer-root-eku-ffe", "valid-root-eku-ffe",
                     credential("root-eku-ffe", LOWER_LEAF, [LOWER, UPPER]), True),
        signing_case("signer-legacy-intermediate-field", "valid-current",
                     {key: value for key, value in good.items() if key != "intermediates_der_base64"}
                     | {"intermediate_der_base64": encode(INTERMEDIATE.der)}, False),
        signing_case("signer-empty-intermediates", "valid-current",
                     credential("empty", LEAF, []), False),
        signing_case("signer-four-intermediates", "four-intermediates",
                     credential("four", four_leaf, [q4, q3, q2, q1]), False),
        signing_case("signer-reversed-chain", "valid-two-intermediates",
                     credential("reversed", LOWER_LEAF, [UPPER, LOWER]), False),
        signing_case("signer-missing-middle-intermediate", "valid-two-intermediates",
                     credential("missing-middle", LOWER_LEAF, [LOWER]), False),
        signing_case("signer-leaf-without-ffe-eku", "valid-current",
                     credential("codesigning", leaves["leaf-wrong-eku"], [INTERMEDIATE]), False),
        signing_case("signer-root-pathlen-below-chain-length", "root-pathlen-below-chain-length",
                     credential("root-pathlen-one", LOWER_LEAF, [LOWER, UPPER]), False),
    ]

    # Wire encodings that every verifier must accept.
    add(signed_case("valid-empty-query", LEAF, [INTERMEDIATE], True, None,
                    request=make_request("valid-empty-query",
                                         "https://flags.example.test:443/precompute/assignments?")))
    high_s = signed_case("valid-high-s-signature", LEAF, [INTERMEDIATE], True, None, high_s=True)
    r, s_value = (int.from_bytes(value[2:], "big") for value in
                  children(base64.b64decode(header_values(high_s["response"]["headers"], PREFIX + "signature")[0])))
    assert s_value > CURVE_N // 2
    add(high_s)

    # Time-rule boundaries. A verifier allows `issued_at` up to 30 seconds after
    # `now`, and accepts a proof until `expires_at`.
    add(signed_case("valid-issued-at-30-seconds-ahead", LEAF, [INTERMEDIATE], True, None, issued_at=NOW + 30))
    add(signed_case("valid-issued-at-1-second-ahead", LEAF, [INTERMEDIATE], True, None, issued_at=NOW + 1))
    add(signed_case("valid-proof-aged-299-seconds", LEAF, [INTERMEDIATE], True, None, issued_at=NOW - 299))
    add(signed_case("issued-at-equals-expires-at", LEAF, [INTERMEDIATE], False, "response-time",
                    issued_at=NOW + 1, expires_at=NOW + 1))
    late = make_leaf("leaf-not-before-after-issued-at", INTERMEDIATE, "2026-10-27T00:59:30", "2026-10-30T00:00:00")
    add(signed_case("leaf-not-before-after-issued-at", late, [INTERMEDIATE], False, "certificate-time",
                    issued_at=NOW - 60))
    early = make_leaf("leaf-starts-before-intermediate", INTERMEDIATE, "2026-09-30T00:00:00", "2026-10-30T00:00:00")
    add(signed_case("leaf-starts-before-intermediate", early, [INTERMEDIATE], False, "validity-containment"))

    # The certificate id is the lowercase hex SHA-256 of the leaf DER.
    add(mutated(base, "certificate-id-mismatch", "certificate-id",
                lambda c: set_header(c, "certificate-id", digest(rotated.der).hex())))
    add(mutated(base, "certificate-id-uppercase", "certificate-id",
                lambda c: set_header(c, "certificate-id", digest(LEAF.der).hex().upper())))

    # One bound request field changes after signing.
    add(mutated(base, "changed-request-path", "transcript-signature",
                url("https://flags.example.test:443/precompute/other?dd_env=production&marker=a%2Fb")))
    add(mutated(base, "changed-content-type", "transcript-signature",
                request_header("content-type", "application/json; charset=utf-8")))
    add(mutated(base, "changed-application-id", "transcript-signature",
                request_header("dd-application-id", "synthetic-other-app")))
    # An added bound header that the list does not name. The SDK rejects its own request.
    add(mutated(base, "added-x-rkyv", "unlisted-bound-header",
                lambda c: c["request"]["headers"].append(["x-rkyv", "true"])))
    rkyv = make_request("valid-x-rkyv-present", headers=DEFAULT_HEADERS + [["x-rkyv", "true"]])
    rkyv_case = signed_case("valid-x-rkyv-present", LEAF, [INTERMEDIATE], True, None, request=rkyv)
    add(rkyv_case)
    add(mutated(rkyv_case, "changed-x-rkyv", "transcript-signature", request_header("x-rkyv", "false")))
    add(mutated(base, "changed-capabilities", "transcript-signature",
                request_header("x-dd-feature-flags-capabilities", "response-signing-v1,synthetic-capability")))
    add(mutated(authorized, "changed-authorization", "transcript-signature",
                request_header("authorization", "Bearer synthetic-other-value")))

    # Header names are case-insensitive. The signature binds header values only.
    mixed = signed_case("valid-mixed-case-header-names", LEAF, [INTERMEDIATE], True, None)
    for message in (mixed["request"], mixed["response"]):
        message["headers"] = [["-".join(part[:1].upper() + part[1:] for part in name.split("-")), value]
                              for name, value in message["headers"]]
    add(mixed)
    signed_header_lists(cases, signing, base, request_header)
    return {"schema_version": 1, "synthetic": True, "anchor_der_base64": encode(ROOT.der),
            "cases": cases, "signing_cases": signing}



def set_request_list(value):
    def transform(c):
        headers = c["request"]["headers"]
        headers[[key for key, _ in headers].index(SIGNED_HEADERS)][1] = value
    return transform


def remove_request_header(name):
    def transform(c):
        c["request"]["headers"] = [pair for pair in c["request"]["headers"] if pair[0].lower() != name]
    return transform


def set_response_header(name, value):
    """Change, add (when absent) or remove (value None) one response header after signing."""
    def transform(c):
        headers = c["response"]["headers"]
        names = [key.lower() for key, _ in headers]
        if value is None:
            c["response"]["headers"] = [pair for pair in headers if pair[0].lower() != name]
        elif name in names:
            headers[names.index(name)][1] = value
        else:
            headers.insert(2, [name, value])
    return transform


def synthetic_names(count, long_name=None):
    """`count` synthetic header names. One of them is `long_name` when it is given."""
    names = [f"x-synthetic-{index:02d}" for index in range(count)]
    if long_name is not None:
        names[-1] = long_name
    return names


def signed_header_lists(cases, signing, base, request_header):
    """Vectors for the signed request and response header name lists."""
    add = cases.append

    # Accepted request lists.
    future = make_request("valid-listed-unknown-request-header",
                          headers=DEFAULT_HEADERS + [["x-synthetic-future", "synthetic-value"]],
                          signed_headers=",".join(sorted(default_list(DEFAULT_HEADERS).split(",") + ["x-synthetic-future"])))
    add(signed_case("valid-listed-unknown-request-header", LEAF, [INTERMEDIATE], True, None, request=future))
    # Gate, telemetry and tracing headers are not bound, so they stay out of the list.
    unlisted = make_request("valid-unlisted-gate-and-telemetry-headers", headers=DEFAULT_HEADERS + [
        ["dd-assignment-token", "synthetic-assignment-token"], ["dd-service", "synthetic-service"],
        ["traceparent", "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"]])
    add(signed_case("valid-unlisted-gate-and-telemetry-headers", LEAF, [INTERMEDIATE], True, None,
                    request=unlisted))
    # x-use-cache is a staging header, so it can stay out of the list.
    staging = make_request("valid-unlisted-staging-header",
                           signed_headers="content-type,dd-application-id,x-dd-feature-flags-capabilities")
    assert header_values(staging["headers"], "x-use-cache") == ["true"]
    add(signed_case("valid-unlisted-staging-header", LEAF, [INTERMEDIATE], True, None, request=staging))
    # 32 names, and one name of 64 bytes. Each listed header is present.
    long_name = "x-synthetic-" + "n" * (MAX_NAME_LENGTH - len("x-synthetic-"))
    extra = synthetic_names(MAX_LISTED_NAMES - 4, long_name)
    limits = make_request("valid-signed-headers-at-limits",
                          headers=DEFAULT_HEADERS + [[name, "synthetic-value"] for name in extra],
                          signed_headers=",".join(sorted(default_list(DEFAULT_HEADERS).split(",") + extra)))
    assert len(listed_names(limits["headers"], SIGNED_HEADERS)) == MAX_LISTED_NAMES
    add(signed_case("valid-signed-headers-at-limits", LEAF, [INTERMEDIATE], True, None, request=limits))

    # Rejected request lists. The SDK checks its own request and does not send it.
    default = default_list(DEFAULT_HEADERS)
    add(mutated(base, "signed-headers-missing", "signed-headers-missing", remove_request_header(SIGNED_HEADERS)))
    add(mutated(base, "duplicate-signed-headers-header", "duplicate-semantic-header",
                lambda c: c["request"]["headers"].insert(0, [SIGNED_HEADERS, default])))

    def without_content_type(c):
        remove_request_header("content-type")(c)
        set_request_list("dd-application-id,x-dd-feature-flags-capabilities,x-use-cache")(c)
    add(mutated(base, "signed-headers-required-content-type", "signed-headers-required", without_content_type))
    add(mutated(base, "signed-headers-required-capabilities", "signed-headers-required",
                set_request_list("content-type,dd-application-id,x-use-cache")))
    for case_id, value, reason in [
        ("signed-headers-unsorted", "dd-application-id,content-type,x-dd-feature-flags-capabilities,x-use-cache",
         "signed-headers-order"),
        ("signed-headers-duplicate-name",
         "content-type,content-type,dd-application-id,x-dd-feature-flags-capabilities,x-use-cache",
         "signed-headers-duplicate"),
        ("signed-headers-uppercase", "Content-Type,dd-application-id,x-dd-feature-flags-capabilities,x-use-cache",
         "signed-headers-syntax"),
        ("signed-headers-space-after-comma",
         "content-type, dd-application-id,x-dd-feature-flags-capabilities,x-use-cache", "signed-headers-syntax"),
        ("signed-headers-empty-entry",
         "content-type,,dd-application-id,x-dd-feature-flags-capabilities,x-use-cache", "signed-headers-syntax"),
        ("signed-headers-trailing-comma", default + ",", "signed-headers-syntax"),
        ("signed-headers-lists-client-token",
         "content-type,dd-application-id,dd-client-token,x-dd-feature-flags-capabilities,x-use-cache",
         "signed-headers-forbidden"),
        ("signed-headers-lists-proof-header", ",".join(sorted(default.split(",") + [PREFIX + "request-nonce"])),
         "signed-headers-forbidden"),
    ]:
        add(mutated(base, case_id, reason, set_request_list(value)))
    too_many = synthetic_names(MAX_LISTED_NAMES - 3)
    many = make_request("signed-headers-too-many-names",
                        headers=DEFAULT_HEADERS + [[name, "synthetic-value"] for name in too_many],
                        signed_headers=",".join(sorted(default.split(",") + too_many)))
    assert len(listed_names(many["headers"], SIGNED_HEADERS)) == MAX_LISTED_NAMES + 1
    add(signed_case("signed-headers-too-many-names", LEAF, [INTERMEDIATE], False, "signed-headers-limit",
                    request=many))
    too_long = long_name + "n"
    wide = make_request("signed-headers-name-too-long",
                        headers=DEFAULT_HEADERS + [[too_long, "synthetic-value"]],
                        signed_headers=",".join(sorted(default.split(",") + [too_long])))
    add(signed_case("signed-headers-name-too-long", LEAF, [INTERMEDIATE], False, "signed-headers-limit",
                    request=wide))
    # The list names x-rkyv, but the request has no x-rkyv. The SDK lists only the
    # headers that it set. The transcript is the one that the edge signs: it
    # writes presence 0 for a listed header that it did not receive.
    absent = make_request("signed-header-absent", signed_headers=",".join(sorted(default.split(",") + ["x-rkyv"])))
    add(signed_case("signed-header-absent", LEAF, [INTERMEDIATE], False, "signed-header-absent", request=absent,
                    include_transcript=True))
    add(mutated(base, "unlisted-bound-header", "unlisted-bound-header",
                set_request_list("content-type,x-dd-feature-flags-capabilities,x-use-cache")))
    add(mutated(base, "comma-in-single-value-header", "combined-semantic-header",
                request_header("content-type", "application/json,text/plain")))
    # A proxy removed a listed header. The edge signed presence 0, and the SDK
    # binds the value that it sent.
    edge_view = make_request("listed-request-header-removed-in-transit",
                             signed_headers=",".join(sorted(default.split(",") + ["x-rkyv"])))
    removed = signed_case("listed-request-header-removed-in-transit", LEAF, [INTERMEDIATE], False,
                          "transcript-signature", request=edge_view)
    removed["request"]["headers"].insert(-2, ["x-rkyv", "true"])
    add(removed)

    # Accepted response lists.
    selection = make_request("valid-flag-selection-ignored-present", body=SELECTION_REQUEST_BODY)
    present = signed_case("valid-flag-selection-ignored-present", LEAF, [INTERMEDIATE], True, None,
                          request=selection, response_extra=[["dd-flag-selection-ignored", "invalid_tag"]])
    add(present)
    absent_ignored = signed_case("valid-flag-selection-ignored-absent", LEAF, [INTERMEDIATE], True, None,
                                 request=make_request("valid-flag-selection-ignored-absent",
                                                      body=SELECTION_REQUEST_BODY))
    add(absent_ignored)
    add(signed_case("valid-response-list-content-type-only", LEAF, [INTERMEDIATE], True, None,
                    response_list="content-type"))
    add(signed_case("valid-top-level-flag-selection-not-selection", LEAF, [INTERMEDIATE], True, None,
                    request=make_request("valid-top-level-flag-selection-not-selection",
                                         body=TOP_LEVEL_SELECTION_REQUEST_BODY),
                    response_list="content-type"))
    # The raw header is present but not listed. Verification does not return it.
    add(signed_case("valid-unlisted-response-header-not-verified", LEAF, [INTERMEDIATE], True, None,
                    response_list="content-type", response_extra=[["dd-flag-selection-ignored", "invalid_tag"]]))
    add(signed_case("valid-response-list-extra-names", LEAF, [INTERMEDIATE], True, None,
                    response_list="cache-control,content-type,dd-flag-selection-ignored,x-synthetic-absent"))

    # Rejected response lists.
    add(mutated(base, "signed-response-headers-missing", "missing-proof",
                set_response_header(SIGNED_RESPONSE_HEADERS, None)))
    add(mutated(base, "duplicate-signed-response-headers", "duplicate-proof",
                lambda c: c["response"]["headers"].append([SIGNED_RESPONSE_HEADERS, DEFAULT_RESPONSE_LIST])))
    for case_id, value, reason, request in [
        ("response-headers-required-content-type", "dd-flag-selection-ignored", "response-headers-required", None),
        ("selection-ignored-not-listed", "content-type", "response-headers-required",
         make_request("selection-ignored-not-listed", body=SELECTION_REQUEST_BODY)),
        ("response-headers-unsorted", "dd-flag-selection-ignored,content-type", "response-headers-order", None),
        ("response-headers-duplicate-name", "content-type,content-type,dd-flag-selection-ignored",
         "response-headers-duplicate", None),
        ("response-headers-uppercase", "Content-Type,dd-flag-selection-ignored", "response-headers-syntax", None),
        ("response-headers-empty-entry", "content-type,,dd-flag-selection-ignored", "response-headers-syntax",
         None),
        ("response-headers-space-after-comma", "content-type, dd-flag-selection-ignored",
         "response-headers-syntax", None),
        ("response-headers-lists-proof-header", DEFAULT_RESPONSE_LIST + "," + PREFIX + "signature",
         "response-headers-forbidden", None),
        ("response-headers-too-many-names",
         ",".join(sorted(DEFAULT_RESPONSE_LIST.split(",") + synthetic_names(MAX_LISTED_NAMES - 1))),
         "response-headers-limit", None),
        ("response-headers-name-too-long", DEFAULT_RESPONSE_LIST + "," + too_long, "response-headers-limit", None),
    ]:
        # Each proof is signed over its own list, so only the list rule fails.
        add(signed_case(case_id, LEAF, [INTERMEDIATE], False, reason, response_list=value, request=request))
    add(mutated(base, "duplicate-listed-response-header", "duplicate-response-header",
                lambda c: c["response"]["headers"].append(["content-type", "application/json"])))
    add(mutated(base, "changed-listed-content-type", "transcript-signature",
                set_response_header("content-type", "text/plain")))
    add(mutated(absent_ignored, "added-flag-selection-ignored", "transcript-signature",
                set_response_header("dd-flag-selection-ignored", "invalid_tag")))
    add(mutated(present, "removed-flag-selection-ignored", "transcript-signature",
                set_response_header("dd-flag-selection-ignored", None)))
    add(mutated(present, "changed-flag-selection-ignored", "transcript-signature",
                set_response_header("dd-flag-selection-ignored", "too_many_values")))
    # A proof over the previous v1 layout: five fixed request slots and no lists.
    add(signed_case("previous-v1-header-layout", LEAF, [INTERMEDIATE], False, "transcript-layout",
                    layout="fixed"))

    # The edge signs the listed response values, and it does not sign a request
    # that has an unlisted bound header or a malformed list. A listed header that
    # is absent is signed with presence 0.
    good = credential("valid-current", LEAF, [INTERMEDIATE])
    signing += [
        signing_case("signer-flag-selection-ignored", "valid-flag-selection-ignored-present", good, True),
        signing_case("signer-listed-header-absent", "signed-header-absent", good, True),
        signing_case("signer-unlisted-bound-header", "unlisted-bound-header", good, False),
        signing_case("signer-signed-headers-unsorted", "signed-headers-unsorted", good, False),
    ]



# ---------------------------------------------------------------------------
# Supplements.

SUPPLEMENT_NOW = timestamp("2026-10-30T04:00:00")


def small_root(prefix, name):
    """A root without key identifiers or path length, for the isolated supplements."""
    key = Key(prefix + "-root")
    subject = utf8_name(name)
    return issue(prefix + "-root", key, subject, key, subject, "2026-10-27T04:00:00", "2027-10-30T04:00:00",
                 [extension(BASIC_CONSTRAINTS, ca_basic_constraints(), True),
                  extension(KEY_USAGE, CA_KEY_USAGE, True)])


def small_ca(label, root, name, basic=None):
    basic = ca_basic_constraints(0) if basic is None else basic
    return issue(label, Key(label), utf8_name(name), root.key, root.name,
                 "2026-10-28T04:00:00", "2026-11-29T04:00:00",
                 [extension(BASIC_CONSTRAINTS, basic, True), extension(KEY_USAGE, CA_KEY_USAGE, True)])


def small_leaf(label, key, parent, name, basic=b"\x30\x00", extra=()):
    return issue(label, key, utf8_name(name), parent.key, parent.name,
                 "2026-10-29T04:00:00", "2026-11-01T04:00:00",
                 [extension(BASIC_CONSTRAINTS, basic, True), extension(KEY_USAGE, LEAF_KEY_USAGE, True),
                  extension(EXTENDED_KEY_USAGE, eku_value([FFE_EKU]))] + list(extra))


def isolated_rules():
    root = small_root("isolated", "SYNTHETIC ISOLATED ROOT")
    intermediate = small_ca("isolated-intermediate", root, "SYNTHETIC ISOLATED INTERMEDIATE")
    # Omitting the default false CA flag keeps CA key usage and path length zero.
    no_ca_flag = small_ca("isolated-intermediate-ca-false", root, "SYNTHETIC ISOLATED INTERMEDIATE",
                          basic=b"\x30\x03\x02\x01\x00")
    key = Key("isolated-leaf")
    name = "SYNTHETIC ISOLATED LEAF"
    # A noncritical DER OCTET STRING extension pads the leaf past 4096 bytes.
    padding = extension(oid("1.2.3.4"), octet(b"\x00" * 3840))
    cases, signing = [], []
    for case_id, leaf, parent, reason in [
        ("isolated-valid", small_leaf("isolated-valid", key, intermediate, name), intermediate, None),
        ("isolated-oversized-certificate",
         small_leaf("isolated-oversized-certificate", key, intermediate, name, extra=[padding]),
         intermediate, "certificate-size"),
        # Leaf key usage stays; only the CA flag changes.
        ("isolated-leaf-ca-true",
         small_leaf("isolated-leaf-ca-true", key, intermediate, name, basic=b"\x30\x03\x01\x01\xff"),
         intermediate, "leaf-basic-constraints"),
        ("isolated-intermediate-ca-false", small_leaf("isolated-intermediate-ca-false", key, no_ca_flag, name),
         no_ca_flag, "intermediate-basic-constraints"),
    ]:
        case = signed_case(case_id, leaf, [parent], reason is None, reason, now=SUPPLEMENT_NOW,
                           include_credential=True, include_transcript=True)
        cases.append(case)
        # Each isolated certificate rule also applies to signing.
        signing.append(signing_case(case_id, case_id, case["credential"], reason is None))
    assert len(base64.b64decode(cases[1]["credential"]["certificate_der_base64"])) > 4096
    return {"schema_version": 1, "synthetic": True, "anchor_der_base64": encode(root.der),
            "cases": cases, "signing_cases": signing}


def nested_der():
    root = small_root("nested-der", "SYNTHETIC NESTED DER ROOT")
    intermediate = small_ca("nested-der-intermediate", root, "SYNTHETIC NESTED DER INTERMEDIATE")
    key = Key("nested-der-leaf")
    cases, signing = [], []
    for case_id, value, accept in [("valid-nested-integer", b"\x30\x03\x02\x01\x01", True),
                                   ("nonminimal-nested-integer", b"\x30\x04\x02\x02\x00\x01", False)]:
        leaf = small_leaf(case_id, key, intermediate, "SYNTHETIC NESTED DER LEAF",
                          extra=[extension(oid("1.2.3.4"), value)])
        case = signed_case(case_id, leaf, [intermediate], accept, None if accept else "certificate-encoding",
                           now=SUPPLEMENT_NOW, include_credential=True, include_transcript=True)
        cases.append(case)
        signing.append(signing_case(case_id, case_id, case["credential"], accept))
    return {"schema_version": 1, "synthetic": True, "anchor_der_base64": encode(root.der),
            "cases": cases, "signing_cases": signing}


def shared_key_chain():
    """Root and intermediate reissued with the public corpus leaf key."""
    key = LEAF.key
    root = make_root("root", ROOT_NAME, key=key)
    intermediate = make_ca("intermediate-2026", "Synthetic Intermediate 2026", root,
                           "2026-10-01T00:00:00", "2027-10-01T00:00:00", path_length=0, key=key)
    return root, intermediate


def subject_der():
    root, intermediate = shared_key_chain()
    cases, signing = [], []
    for case_id, value, accept in [("canonical-subject-integer", b"\x01", True),
                                   ("nonminimal-subject-integer", b"\x00\x01", False)]:
        # Unknown attribute OID 1.2.3.4 with an ASN.1 ANY INTEGER value.
        name = sequence(tlv(0x31, sequence(oid("1.2.3.4"), tlv(0x02, value))))
        extensions = [extension(BASIC_CONSTRAINTS, b"\x30\x00", True), extension(KEY_USAGE, LEAF_KEY_USAGE, True),
                      extension(SUBJECT_KEY_ID, octet(LEAF.key.identifier)),
                      extension(AUTHORITY_KEY_ID, sequence(tlv(0x80, intermediate.key.identifier))),
                      extension(EXTENDED_KEY_USAGE, eku_value([FFE_EKU]))]
        leaf = issue("leaf-2026", LEAF.key, name, intermediate.key, intermediate.name,
                     "2026-10-27T00:00:00", "2026-10-30T00:00:00", extensions)
        case = signed_case(case_id, leaf, [intermediate], accept, None if accept else "certificate-encoding",
                           include_credential=False)
        cases.append(case)
        signing.append(signing_case(case_id, case_id, credential("valid-current", leaf, [intermediate]), accept))
    return {"schema_version": 1, "synthetic": True, "anchor_der_base64": encode(root.der),
            "cases": cases, "signing_cases": signing}


def extension_profile():
    root, intermediate = shared_key_chain()
    cases, signing = [], []
    ski = extension(SUBJECT_KEY_ID, octet(LEAF.key.identifier))
    aki = extension(AUTHORITY_KEY_ID, sequence(tlv(0x80, intermediate.key.identifier)))
    for case_id, ski_value, aki_value, extra, accept in [
        ("extension-profile-valid", ski, aki, [], True),
        ("noncritical-policy-mappings", ski, aki,
         [extension(oid("2.5.29.33"), bytes.fromhex("300c300a06032a030406032a0305"))], False),
        ("empty-authority-key-identifier", ski, extension(AUTHORITY_KEY_ID, b"\x30\x00"), [], False),
        ("empty-authority-key-value", ski, extension(AUTHORITY_KEY_ID, b"\x30\x02\x80\x00"), [], False),
        ("empty-subject-key-identifier", extension(SUBJECT_KEY_ID, b"\x04\x00"), aki, [], False),
        ("absent-optional-key-identifiers", None, None, [], True),
    ]:
        extensions = [extension(BASIC_CONSTRAINTS, b"\x30\x00", True), extension(KEY_USAGE, LEAF_KEY_USAGE, True)]
        extensions += [value for value in (ski_value, aki_value) if value is not None]
        extensions += [extension(EXTENDED_KEY_USAGE, eku_value([FFE_EKU]))] + extra
        leaf = issue("leaf-2026", LEAF.key, LEAF.name, intermediate.key, intermediate.name,
                     "2026-10-27T00:00:00", "2026-10-30T00:00:00", extensions)
        reason = None if accept else ("unsupported-constraint" if extra else "key-identifier")
        case = signed_case(case_id, leaf, [intermediate], accept, reason, include_credential=False)
        cases.append(case)
        signing.append(signing_case(case_id, case_id, credential("valid-current", leaf, [intermediate]), accept))
    return {"schema_version": 1, "synthetic": True, "anchor_der_base64": encode(root.der),
            "cases": cases, "signing_cases": signing}


def near_expiry():
    end = LEAF.not_after
    cases, signing = [], []
    for remaining in [301, 300, 299, 1]:
        case_id = f"leaf-expires-in-{remaining}-seconds"
        cases.append(signed_case(case_id, LEAF, [INTERMEDIATE], True, None, now=end - remaining,
                                 include_credential=False))
    cases.append(signed_case("proof-outlives-leaf-by-one-second", LEAF, [INTERMEDIATE], False,
                             "certificate-time", now=end - 299, expires_at=end + 1))
    cases.append(signed_case("at-leaf-and-proof-expiry", LEAF, [INTERMEDIATE], False, "response-time",
                             now=end, issued_at=end - 1, expires_at=end))
    good = credential("valid-current", LEAF, [INTERMEDIATE])
    for case in cases:
        # A valid credential still signs before leaf expiry; the signer clips the proof lifetime.
        signing.append(signing_case(case["id"], case["id"], good, case["now"] < end))
    return {"schema_version": 1, "synthetic": True, "anchor_der_base64": encode(ROOT.der),
            "cases": cases, "signing_cases": signing}


def self_check(files):
    """Every certificate link carries a valid signature from its named issuer key."""
    for name, corpus_value in files.items():
        for case in corpus_value["cases"]:
            assert case["id"] and isinstance(case["expected_accept"], bool), name
            if case["expected_accept"]:
                assert case["rejection_reason"] is None and case["transcript_base64"], case["id"]
                headers = case["response"]["headers"]
                signature = base64.b64decode(header_values(headers, PREFIX + "signature")[0])
                leaf = base64.b64decode(header_values(headers, PREFIX + "signing-certificate")[0])
                spki = children(children(leaf)[0])[6]
                public = children(spki)[1][3:]
                assert ecdsa_verify(public, base64.b64decode(case["transcript_base64"]), signature), case["id"]
            else:
                assert case["rejection_reason"], case["id"]


def generate():
    files = {
        "corpus.json": corpus(),
        "isolated-certificate-rules.json": isolated_rules(),
        "nested-der.json": nested_der(),
        "subject-der.json": subject_der(),
        "near-expiry.json": near_expiry(),
        "extension-profile.json": extension_profile(),
    }
    with_sdk_reasons(files)
    self_check(files)
    rendered = {name: (json.dumps(value, indent=2) + "\n").encode() for name, value in files.items()}
    manifest = {"schema_version": 1, "generator": "response-signing/generate-v1.py", "files": {}}
    for name, raw in rendered.items():
        value = files[name]
        manifest["files"][name] = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "response_cases": len(value["cases"]),
            "accepted": sum(case["expected_accept"] for case in value["cases"]),
            "signing_cases": len(value.get("signing_cases", [])),
        }
    rendered["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    return rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if a committed file differs from the output")
    args = parser.parse_args()
    differences = []
    for name, raw in generate().items():
        path = DIRECTORY / name
        if args.check:
            if not path.exists() or path.read_bytes() != raw:
                differences.append(name)
        else:
            path.write_bytes(raw)
        print(f"{name}: {'checked' if args.check else 'written'} ({len(raw)} bytes)")
    if differences:
        raise SystemExit("regeneration differs: " + ", ".join(differences))


if __name__ == "__main__":
    main()

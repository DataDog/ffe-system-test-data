# Response signing conformance fixtures

These fixtures define shared inputs and expected results for the v1 assignment
response signer and client verifiers. Consumers pin an exact repository revision
and run their native implementation against these bytes. The files are test data.
Clients do not fetch them when they evaluate flags or verify a response.

## Suites

| File | Coverage | Consumers |
| --- | --- | --- |
| `v1/corpus.json` | 144 response cases: 35 accepted and 109 rejected. 16 signer cases. Includes `valid-empty-query`, `valid-high-s-signature`, the time-rule boundaries, `valid-mixed-case-header-names` and the signed header list cases. | Verifiers consume `cases`. Signers also consume `signing_cases`. |
| `v1/isolated-certificate-rules.json` | An accepted control, and isolated certificate-size, leaf-CA and intermediate-CA rejections. 4 signer cases. | Signers and verifiers |
| `v1/subject-der.json` | Canonical and nonminimal INTEGER encodings in the leaf subject, with valid signatures | Signers and verifiers |
| `v1/extension-profile.json` | Accepted controls, and isolated policy-mapping and empty key-identifier rejections | Signers and verifiers |
| `v1/near-expiry.json` | Four valid near-expiry proofs, a proof that outlives its leaf, and an exact-expiry rejection | Signers and verifiers |
| `v1/nested-der.json` | Canonical and noncanonical nested INTEGER encodings in a certificate extension | Signers and verifiers |
| `chain/` | Static test-CA credentials and roots for chain building, root rotation, leaf and root EKU, and root path length. Also the real us1.staging DC intermediate. See `chain/README.md`. | Verifiers |

## Protocol version 1 with a certificate chain

Version 1 is the first public response-signing protocol. No public client
verified the earlier single-intermediate form of v1, so v1 changed in place to
carry a certificate chain. These names do not change:

| Name | Value |
| --- | --- |
| Signature version header value (request and response) | `1` |
| Transcript domain | `datadog.feature-flags.precomputed-assignments.v1\0` |
| Capability header value | `response-signing-v1` |
| Credential JSON `version` | `1` |

The chain contract has these rules:

- The response header `x-datadog-feature-flags-signing-chain` holds 1 to 3
  intermediate certificates. Each entry is standard base64 DER of at most 4096
  bytes. A `,` without spaces separates the entries. Index 0 issued the leaf.
  Index `i + 1` issued index `i`. The pinned root issued the last entry.
- The header `x-datadog-feature-flags-signing-intermediate` is removed. A
  response that has only this header has no chain, and a verifier rejects it.
- The transcript ends with
  `SHA256(leaf) || u8(n) || SHA256(int[0]) || ... || SHA256(int[n-1])`. See
  [Transcript bytes](#transcript-bytes) for the complete layout.
- The leaf extended key usage (EKU) must contain the FFE assignment-signing EKU.
  It must not contain anyExtendedKeyUsage (`2.5.29.37.0`). Other OIDs are allowed.
- Intermediate `i` must have a critical basicConstraints with cA TRUE and a
  pathLenConstraint of at least `i`. Its EKU is absent, or it contains the FFE EKU
  or anyExtendedKeyUsage.
- If the pinned root has an EKU, the EKU must contain the FFE EKU or
  anyExtendedKeyUsage. If the root has a pathLenConstraint, it must be at least `n`.
- The credential field `intermediates_der_base64` is an array of 1 to 3 strings.
  Index 0 issued the leaf. A credential with the removed `intermediate_der_base64`
  field fails to parse, and the signer does not sign.

The FFE EKU in these fixtures is the placeholder `1.3.6.1.4.1.99999.1.1`.
This arc does not belong to Datadog. Datadog must assign the production OID
before release. Then change `FFE_EKU` in `generate-v1.py` and
`ci/verify-response-signing-vectors.py`, and regenerate all fixtures.

v1 changed in place a second time to bind signed lists of request and response
header names. See [Signed header lists](#signed-header-lists). Only staging used
the earlier form, and no public client verified it. The proof
`previous-v1-header-layout` uses the earlier form, and a verifier rejects it.

The corpus keeps rejection cases for the prototype version headers `2` and `3`.
It also rejects proofs signed with the abandoned draft-v3 domain and the chain
prototype v2 domain. The [single-intermediate v1 fixtures](https://github.com/DataDog/ffe-system-test-data/tree/efa1612b3a7a2217078b268af499e0dd4e8ab727/response-signing/v1)
remain available in history. Earlier validation receipts do not validate these bytes.

## Transcript bytes

The signature covers these bytes, in this order. `lp(x)` is `u32be(len(x)) || x`.
All integers are big-endian. Header names match case-insensitively. The two
signed lists bind the listed names and their values. `list(names)` is:

```text
u8(count) || for each name, in list order: lp(name) || u8(presence) || lp(value)
```

`presence` is `1` when the header is present, and `value` is its value. When the
header is absent, `presence` is `0` and `value` is empty, so the entry is
`lp(name) || u8(0) || lp("")`.

| Field | Bytes |
| --- | --- |
| Domain | `datadog.feature-flags.precomputed-assignments.v1\0` |
| Method | `lp(method)`, for example `lp("POST")` |
| Scheme | `lp("https")` |
| Authority | `lp(host)`. The host is lowercase. An IPv6 host is in brackets. A port is present only when it is not the scheme default. |
| Path | `lp(path)` with the request escaping unchanged |
| Query | `lp("?" + query)` when the URL contains `?`, also for an empty query. Otherwise `lp("")`. |
| Nonce | `lp(nonce)`, the 16 bytes that `x-datadog-feature-flags-request-nonce` encodes as 32 lowercase hex digits |
| Request body | `SHA256(request body)` |
| Client token | `SHA256(dd-client-token value)` |
| Signed request headers | `list(names)` for the names in `x-datadog-feature-flags-signed-headers` |
| `authorization` | `u8(0)` when absent, or `u8(1) || SHA256(value)` |
| Status | `u16(200)` |
| Times | `u64(issued_at) || u64(expires_at)` |
| Response body | `u64(len(body)) || SHA256(body)`, over the application bytes after content decoding |
| Leaf | `SHA256(leaf DER)` |
| Chain | `u8(n) || SHA256(int[0]) || ... || SHA256(int[n-1])` |
| Signed response headers | `list(names)` for the names in `x-datadog-feature-flags-signed-response-headers` |

These fixtures do not contain the draft revocation floor tail. That draft is on
hold, and its code does not change. While an SDK keeps the draft tail, the tail
stays the last field, after the signed response headers.

## Signed header lists

Each signed list is one header value: lowercase names, sorted in ascending byte
order, unique, and joined by `,` with no spaces. A name is an HTTP token of
lowercase characters. A list has 1 to 32 names. Each name has at most 64 bytes.
An empty entry, a space, an uppercase name, an unsorted list or a duplicate name
is malformed.

### Request list

The request header `x-datadog-feature-flags-signed-headers` names the request
headers that the SDK bound. The verifier of these fixtures applies these rules
to the request that the SDK sends:

- The list header is present on exactly one line.
- The list names `content-type` and `x-dd-feature-flags-capabilities`.
- The list does not name `dd-client-token`, `authorization` or a
  `x-datadog-feature-flags-` header. The token and `authorization` keep their
  hashed slots.
- Each listed header and each bound header has at most one line.
- A bound header that is present is in the list. The bound headers are
  `content-type`, `dd-application-id`, `x-dd-feature-flags-capabilities` and
  `x-rkyv`. These are the headers of the edge `bound` class.
- `x-use-cache` is a staging header, not a bound header. When the SDK lists it,
  the transcript binds it like any listed name. When it is not listed, it is not
  signed (`valid-unlisted-staging-header`).
- Each listed header is present. The SDK lists only the headers that it set.
- Only the `x-dd-feature-flags-capabilities` value can contain a comma.
- The list can name other headers. The transcript binds them with no format change.
- Headers that are not listed and not bound are not signed, for example
  `dd-assignment-token`, `dd-service` and `traceparent`.

The edge writes the values that it received. When a listed header did not arrive,
the edge signs presence `0`, and the SDK verification fails. The edge does not
sign a request that has an unlisted bound header or a malformed list.

### Response list

The response header `x-datadog-feature-flags-signed-response-headers` is a proof
header. It is required, and it has exactly one line. It names the response
headers that the edge bound. A verifier applies these rules:

- The list names `content-type`.
- When the request has a flag selection, the list names
  `dd-flag-selection-ignored`. Presence `0` is valid. A request has a flag
  selection when its JSON:API body has a `data.attributes.flag_selection`
  object that is not null. A top-level `flag_selection` and the URL query are
  not a selection.
- The edge names `dd-flag-selection-ignored` in every signed response list.
- The list does not name one of the 8 proof headers.
- Each listed header has at most one line. A listed header can be absent.

An SDK acts on a listed response header only after verification passes. It uses
the verified value. Each accepted case gives these values in
`verified_response_headers`, with `null` for an absent header. A response header
that is not listed is not verified, also when it is present
(`valid-unlisted-response-header-not-verified`).

### Rule codes

| `rejection_reason` | `sdk_reason` | Rule |
| --- | --- | --- |
| `signed-headers-missing` | `unsupported-request` | The request list header is absent. |
| `signed-headers-syntax` | `unsupported-request` | The request list has an empty entry, a space or a character that is not a lowercase token character. |
| `signed-headers-limit` | `unsupported-request` | More than 32 names, or a name longer than 64 bytes. |
| `signed-headers-duplicate` | `unsupported-request` | A name occurs twice. |
| `signed-headers-order` | `unsupported-request` | The names are not sorted. |
| `signed-headers-forbidden` | `unsupported-request` | The list names a credential or a proof header. |
| `signed-headers-required` | `unsupported-request` | `content-type` or `x-dd-feature-flags-capabilities` is not listed. |
| `signed-header-absent` | `unsupported-request` | A listed header is absent from the request. |
| `unlisted-bound-header` | `unsupported-request` | A bound header is present and not listed. |
| `combined-semantic-header` | `unsupported-request` | A listed value other than the capabilities contains a comma. |
| `duplicate-semantic-header` | `unsupported-request` | A listed or bound header, or the list header, has more than one line. |
| `response-headers-syntax`, `-limit`, `-duplicate`, `-order` | `invalid-proof` | The response list is malformed. The rules are the same as for the request list. |
| `response-headers-forbidden` | `invalid-proof` | The response list names a proof header. |
| `response-headers-required` | `invalid-proof` | A required response name is not listed. |
| `duplicate-response-header` | `invalid-proof` | A listed response header has more than one line. |
| `transcript-layout` | `invalid-signature` | The proof signs the earlier v1 layout with fixed header slots. |

An absent response list is `missing-proof`, and a second list line is
`duplicate-proof`. A listed header that changes after signing is
`transcript-signature`.

## Time rules

`issued-at` and `expires-at` are decimal Unix seconds: `0`, or digits without a
leading zero, at most `2^53 - 1`. A verifier accepts a proof at time `now` only
when all of these are true:

- `issued_at <= now + 30`. This allows a device clock that is up to 30 seconds slow.
- `now < expires_at`.
- `issued_at < expires_at`.
- `expires_at - issued_at <= 300`.
- For the leaf, each intermediate and the pinned root:
  `not_before <= now < not_after`, `not_before <= issued_at` and
  `expires_at <= not_after`.
- For the leaf: `not_after - not_before <= 432300` (120 hours and 5 minutes,
  rule F16). A longer leaf has `rejection_reason` `leaf-lifetime` and
  `sdk_reason` `invalid-certificate`. `valid-leaf-lifetime-at-limit` spans
  exactly 432300 seconds. `leaf-lifetime-over-limit` spans 432301 seconds.

There is no other limit on the age of a proof. A proof issued 299 seconds before
`now` is valid until `expires_at`. These cases test the boundaries:
`valid-issued-at-30-seconds-ahead`, `valid-issued-at-1-second-ahead`,
`future-issued-at` (31 seconds ahead), `valid-proof-aged-299-seconds`,
`issued-at-equals-expires-at` and `leaf-not-before-after-issued-at`.

## Running a consumer

1. Decode `body_base64` into exact bytes. Keep header order, duplicates and URL
   escaping, because several rejection cases use these differences.
   `response.body_base64` contains application bytes after HTTP content decoding.
   When `wire_body_base64` is present, transport tests serve those compressed
   bytes with the supplied encoding headers. Direct verifier tests use `body_base64`.
2. Use the file's `anchor_der_base64` as the only trusted root. When a case has its
   own `anchor_der_base64`, use that root for that case instead. The root-profile
   cases use this override. Use `now` as Unix epoch seconds, and convert it to the
   native clock unit if necessary. Use this fixed time after the synthetic
   certificates expire too.
3. Verify each request/response pair and assert `expected_accept`. For accepted
   cases, also compare the constructed transcript with `transcript_base64`.
   `rejection_reason` is a code for the violated rule. It is not a required native
   error string. Each rejected case also has `sdk_reason`: the reason code that
   every SDK reports for that case. Assert it in each SDK. The codes come from the
   browser verifier, which is the reference for all SDKs. `missing-proof` means
   that one or more proof headers are absent, including the chain header and the
   signed response list. For accepted cases, also compare the verified response
   values with `verified_response_headers`. A rejected case that has
   `transcript_base64` gives the bytes that the signer signs for that case.
4. Signers also load each `signing_cases` credential and the referenced response
   case. They sign that case's request, body and listed response headers at its
   `now`, with its trust anchor, and assert `expected_signing`. Clients do not run these cases, because
   they do not hold signing keys.

Each response carries its leaf and its chain. Verification fetches no certificate.
These fixtures cover buffered response proofs. They do not cover a signed NDJSON
protocol.

Native adapters, secret-store access, fail-open serving behavior and
implementation-specific diagnostics belong in consumer repositories. Keep these
fixtures independent of those adapters. Never derive expected results from the
implementation that you test.

## Corpus cases

Accepted cases:

- One intermediate (`valid-current`), a rotated leaf, a rotated intermediate in
  2032, an effective token with authorization, gzip transport bytes, and IPv6 with
  absent optional headers.
- `issued_at` 30 seconds and 1 second after `now`, and a proof issued 299
  seconds before `now`.
- Request and response header names in mixed case
  (`valid-mixed-case-header-names`), and a request with `x-rkyv`
  (`valid-x-rkyv-present`).
- Two intermediates (root, upper intermediate with pathLen 1, lower intermediate with
  pathLen 0, leaf) and three intermediates.
- A rotated lower intermediate under the same upper intermediate, with no earlier history.
- A leaf EKU with the FFE EKU and other OIDs. An intermediate EKU with the FFE EKU,
  or with anyExtendedKeyUsage. An intermediate pathLen of 1 at index 0
  (`intermediate-pathlen-one`).
- A root without pathLen (the default anchor), a root pathLen equal to the chain
  length, and a root EKU with the FFE EKU or with anyExtendedKeyUsage.
- The same lower intermediate key issued directly by the root
  (`valid-cross-issued-lower-intermediate`).

Rejected chain cases:

- Leaf EKU: codeSigning only (`leaf-wrong-eku`), another product OID only,
  FFE EKU with anyExtendedKeyUsage, and no EKU.
- Intermediate EKU without the FFE EKU or anyExtendedKeyUsage, pathLen absent,
  pathLen 0 at index 1, root pathLen below the chain length, root pathLen 0, and a
  root EKU of codeSigning only.
- Missing middle intermediate, reversed chain order, four intermediates, an empty
  entry, a trailing comma, a space after a comma, a non-base64 entry, and an entry
  over 4096 bytes.
- Only the removed `...-signing-intermediate` header, no chain header
  (`missing-intermediate`), and a duplicated chain header.
- `chain-differs-from-signed-chain`: the proof was signed for one valid chain, and
  the response carries a different valid chain. The transcript binds the chain.
- `legacy-v1-transcript-tail`: the proof was signed with the removed tail.

Rejected binding and time cases:

- One changed request field after signing: the path, `content-type`,
  `dd-application-id`, a changed `x-rkyv`, the capabilities value (it still
  contains `response-signing-v1`) and `authorization`. An added `x-rkyv` that is
  not listed is `unlisted-bound-header`.
- A `certificate-id` for a different leaf, and an uppercase `certificate-id`.
- `issued_at` equal to `expires_at`, a leaf whose `not_before` is after
  `issued_at`, and a leaf that starts before its intermediate.

Signed request list cases:

- Accepted: an unknown listed header (`valid-listed-unknown-request-header`),
  unlisted gate and telemetry headers, an unlisted `x-use-cache`, and 32 names
  with one name of 64 bytes (`valid-signed-headers-at-limits`).
- Rejected: no list, two list lines, `content-type` or the capabilities not
  listed, unsorted, a duplicate name, uppercase, a space after a comma, an empty
  entry, a trailing comma, a listed `dd-client-token`, a listed proof header,
  33 names, a name of 65 bytes, a listed header that is absent
  (`signed-header-absent`), an unlisted bound header, and a comma in
  `content-type`.
- `listed-request-header-removed-in-transit`: the edge did not receive a listed
  header and signed presence `0`. The SDK binds the value that it sent.

Signed response list cases:

- Accepted: `dd-flag-selection-ignored` present and absent for a request with a
  selection, a list with only `content-type`, a list with only `content-type`
  for a body with a top-level `flag_selection`, an unlisted response header,
  and extra listed names with one absent name.
- Rejected: no list, two list lines, `content-type` not listed,
  `dd-flag-selection-ignored` not listed for a selection, unsorted, a duplicate
  name, uppercase, an empty entry, a space after a comma, a listed proof header,
  33 names, a name of 65 bytes, and two `content-type` lines.
- A listed header that changes after signing: `content-type`, and
  `dd-flag-selection-ignored` added, removed or changed.
- `previous-v1-header-layout`: the proof signs the earlier v1 layout.

The other rejections cover unrelated roots, the leaf profile, expiry, changed
request or response bytes, malformed proof headers, signature tampering,
prototype versions and earlier domains. Each rejection changes one rule. The
certificate and proof signatures stay valid unless the case tests a signature.

Signer cases sign one, two and three intermediates, a root with an FFE EKU, a
listed `dd-flag-selection-ignored`, and a listed request header that is absent.
Signing must fail for a mismatched private key, the legacy credential field, an
empty chain, four intermediates, a reversed chain, a missing middle intermediate,
a leaf without the FFE EKU, a root pathLen below the chain length, an unlisted
bound header and an unsorted request list.

## Synthetic credentials

All certificates, identities, tokens and private keys in this suite are synthetic
test material. Each key comes from a fixed public label in the generator. The
included private keys are public, so that signer implementations can be tested.
`subject-der.json` and `extension-profile.json` reuse the corpus leaf key for the
root and the intermediate. These keys and certificates must never be trusted or
provisioned outside tests. This suite contains no production or staging
credentials and no customer responses.

## Boundary supplements

`isolated-certificate-rules.json` keeps valid certificate and response
signatures in each case. A noncritical DER OCTET STRING extension pads the
oversized leaf. The leaf-CA case keeps the leaf KeyUsage and has no path length.
The intermediate-CA case keeps the CA KeyUsage and path length zero, and omits the
CA flag. Each rejection changes only the named rule.

`subject-der.json` holds two correctly signed chains. The leaf subject contains an
attribute with OID `1.2.3.4` and INTEGER value 1. The canonical encoding is
`02 01 01`. A verifier must reject `02 02 00 01`, because the leading zero is not
necessary. A typed parser can keep this opaque attribute when it decodes and
encodes again, so equal re-encoded bytes alone are not sufficient. The root and
intermediate in this file and in `extension-profile.json` keep the corpus names,
serial numbers and key identifiers, but use the leaf key. Use each file's anchor
only for that file. Never put supplement anchors together in one trust store.

`extension-profile.json` requires rejection of policy mappings, also when they are
noncritical. When SKI or AKI is present, its identifier must not be empty. SKI and
AKI can be absent. Every rejection keeps valid certificate and proof signatures.

`nested-der.json` puts a canonical and a nonminimal INTEGER inside a noncritical
extension value. A verifier must reject the nonminimal encoding.

`near-expiry.json` uses the corpus chain. It accepts proofs when the leaf has 301,
300, 299 or 1 second left. Each accepted proof expires at
`min(issued_at + 300, leaf.not_after)`. One rejected proof extends one second past
the leaf, and is in the 300-second proof lifetime. Another rejected proof is
verified exactly when both the leaf and the proof expire.

For signer cases, assert `expected_signing` separately from `expected_accept`. A
verifier must reject the proof that outlives the leaf, but its valid credential
can still sign a new, clipped proof. For each successful signing, verify the new
proof and assert `now < expires_at <= min(now + 300, leaf.not_after)`. Do not
require the signer to choose the longest lifetime or to reproduce the fixture
signature bytes. At exact leaf expiry, signing must fail.

## Wire encodings that every verifier must accept

- **Empty query.** A request URL that ends in `?` with no query, such as
  `https://h/p?`, binds the query field as `?`. It does not bind an empty value.
  The edge, iOS and Android already do this. `valid-empty-query` tests it.
- **High-S ECDSA signature.** A verifier must accept a P-256 signature whose `s`
  is greater than `n / 2`. The edge signer emits this form about half of the
  time. `valid-high-s-signature` tests it. All other fixture signatures are
  low-S.

## Counts

`ci/validate-response-signing.py` prints the counts for each file.
`ci/verify-response-signing-vectors.py` prints the totals for all six v1 files:
164 response cases and 73 signer checks. A signer check is a signer case, or a
check that the credential of an accepted case can sign a new proof. It also
prints the 14 `chain/` cases.

| Scope | Response cases | Signer |
| --- | --- | --- |
| `v1/corpus.json` | 144 | 16 signer cases |
| All six v1 files | 164 | 73 signer checks |

## Validation and regeneration

`response-signing/generate-v1.py` is the only way to regenerate these files. It
writes all six fixture files and `v1/manifest.json`. It uses only the Python
standard library. It uses fixed key labels and RFC 6979 deterministic ECDSA, so
each run writes the same bytes. The generator does not import or call an SDK,
edge or signer implementation. It sets each expectation from the protocol rules.

```sh
python3 response-signing/generate-v1.py
python3 response-signing/generate-v1.py --check
python3 ci/verify-response-signing-vectors.py
python3 -m pip install jsonschema==4.25.1
python3 ci/validate-response-signing.py
python3 -m unittest discover -s ci -p 'test_validate_response_signing.py'
```

`ci/verify-response-signing-vectors.py` is a separate verifier. It does not import
the generator. It has its own strict DER parser, certificate profile, chain rules,
time rules and transcript builder. It uses the `openssl` command to verify each
ECDSA signature. For each response case, it checks `expected_accept`, the
`rejection_reason` code, and the transcript and `verified_response_headers` of
accepted cases. It also checks the signer transcript of a rejected case that
has one. For each signer
case, it checks `expected_signing`. It also runs each `chain/` expectation at the
`now` in `chain/manifest.json`, and checks the rule code of each rejection.

`ci/validate-response-signing.py` checks the schema, the exact file hashes, case
identities, references and counts. It checks that each rejected case has an
`sdk_reason`, and that each `wire_body_base64` decodes to the signed body. For
accepted cases, it checks the syntax of both signed lists, and that the
transcript contains the list bytes. It allows malformed proof and certificate
fields, because negative cases use them. Structural validation does not prove
cryptographic correctness. Run native signer and verifier tests when you change
this contract.

CI checks exact regeneration, the independent verifier and manifest integrity.
Review expectation changes together with the fixtures. Do not reformat signed
body bytes or normalize headers when you import fixtures. Follow the repository's
[consumer pinning rules](../CONTRIBUTING.md#updating-downstream-repositories).
Merge fixture updates before you change downstream pins or snapshots.

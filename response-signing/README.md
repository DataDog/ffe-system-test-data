# Response signing conformance fixtures

These fixtures define shared inputs and expected results for the v3 assignment
response signer and client verifiers. Consumers pin an exact repository revision
and run their native implementation against these bytes. The files are test data;
clients do not fetch them when evaluating flags or verifying a response.

## Suites

| File | Coverage | Consumers |
| --- | --- | --- |
| `v3/corpus.json` | 43 response cases: 6 accepted and 37 rejected; 2 private-key matching cases | Verifiers consume `cases`; signers also consume `signing_cases` |
| `v3/nested-der.json` | Canonical and noncanonical nested INTEGER encodings in certificate extensions | Signers and verifiers |

The core corpus is extracted without byte changes from the [browser verifier
fixtures](https://github.com/DataDog/openfeature-js-client/blob/b2211ccacd48008f455be30608132f61d693dd23/packages/browser/test/transport/responseSigning/corpus.json).
The nested-DER supplement preserves the independently constructed certificate
regression inputs and their expected results. `v3/manifest.json` records hashes
and applicability counts; extracting these fixtures does not change the protocol
or any expected acceptance result. The existing `profile_sha256` identifier is
retained as provenance for the original corpus.

## Running a consumer

1. Decode `body_base64` into exact bytes. Preserve header order, duplicates and
   URL escaping: several rejection cases exercise those distinctions.
2. Supply the fixture's `anchor_der_base64` as the local trust anchor and `now`
   as the clock. Use this fixed time even after the synthetic certificates expire.
3. Verify each request/response pair and assert `expected_accept`. For accepted
   cases, compare the constructed transcript with `transcript_base64` as well.
   `rejection_reason` describes the violated rule; it is not a required native
   exception string.
4. Signers additionally load each `signing_cases` credential and its referenced
   response case, then assert `expected_signing`. Clients exclude these cases
   because they do not hold signing keys. The nested-DER supplement's credentials
   let signers exercise the same accepted/rejected certificate boundary.

The positive cases include leaf rotation and a later intermediate under the same
root, without requiring the client to have seen earlier certificates. Negative
cases cover unrelated roots, invalid chain profiles, expiry, changed request or
response bytes, malformed proof headers and signature tampering. Each response
carries its leaf and intermediate; verification requires no certificate fetch.
These fixtures cover buffered response proofs, not a signed NDJSON protocol.

Native adapters, secret-store access assertions, fail-open serving behavior and
implementation-specific diagnostics belong in consumer repositories. Keep these
fixtures independent of those adapters; never derive expected results from the
implementation being tested.

## Synthetic credentials

All certificates, identities, tokens and private keys in this suite are synthetic
test material. The included leaf private keys are intentionally public so signer
implementations can be tested. They must never be trusted or provisioned outside
tests. There are no production or staging credentials or customer responses here.

## Validation and updates

Run `python3 ci/validate-response-signing.py` with `jsonschema` installed. It checks
the schema, exact fixture hashes, case identities, references and applicability
counts. It deliberately allows malformed proof/certificate fields used by
negative cases. Structural validation does not prove cryptographic correctness;
run native signer and verifier tests when changing this contract.

Review expectation changes together with the fixtures and update the manifest
deliberately. Do not reformat signed body bytes, regenerate keys, or normalize
headers during import. Follow the repository's [consumer pinning
rules](../CONTRIBUTING.md#updating-downstream-repositories).

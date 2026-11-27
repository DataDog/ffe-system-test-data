# BITS-02: generated rules-resource provenance audit

Snapshot: 27 November 2026, public corpus main
`fe24ed2c4872bf109b0c71ffb2229152d76b8963`.
Assignment: [CONTROL-047 BITS-02](https://github.com/DataDog/ffe-system-test-data/blob/b953a282d1466e37ac5deaeea69ec8c09829aedf/flex-fit-control/assignments/BITS-02-RULES-CORPUS-AUDIT.md);
[CONTROL-048 WS-12 boundaries](https://github.com/DataDog/ffe-system-test-data/blob/7d05096af15176b08441a82fe9a0f40b83055c6e/flex-fit-control/assignments/WS-12-SHARED-RULES-RESOURCES.md) also read.

Main contains **one current, integrity-verified rules resource**, with raw protobuf
and the exact serialized SDK initialization string. Its 68 source flags become
50 encoded flags; 18 omissions affect 20 core cases. Five optional suites have no
catalogued binary/wire resource. Main's artifacts were refreshed by merged #76;
open #86 changes the source without refreshing its artifacts. This audit changes
documentation only. FIT serving/loading implementation belongs to WS-12; no FIT
execution, generation, fixture edits, activation, PRs or tickets were performed.

## Authoritative files and encodings

[catalog.json](../../rules-resources/catalog.json) schema version 1 selects
`canonical-evaluator` from [ufc-config.json](../../ufc-config.json).
The accepted set is [generated/manifest.json](../../rules-resources/generated/manifest.json)
and the two files under `rules-resources/generated/canonical-evaluator/`.

| File | Bytes | SHA-256 at the audited base |
| --- | ---: | --- |
| `rules-resources/catalog.json` | 102 | `a49daf231a12027298b0b4426d3eb8e7b09b3420d6cfe7b580519cd8c5c1f58e` |
| `ufc-config.json` | 166409 | `e7b29c91472d9b9064ee01f08b50acd5e81f55b1465d5ffc622f7d8a60e18d66` |
| `rules-resources/generated/manifest.json` | 3895 | `a8ba090f74b385c062ae9e77211abc4ea85966176caa792d835343ba353a73ff` |
| `canonical-evaluator/ufc.pb` | 20436 | `8d01db1863661d0086f7139461d7110715e5e979af23e445f6b557d07094a0d6` |
| `canonical-evaluator/configuration-wire.json` | 27285 | `e9f3dd55172d2c39dd2ca5e583caf1ed8f071d9769f845673d1f077628a62465` |

Artifact paths in the last two rows are relative to `rules-resources/generated/`.
`ufc.pb` is uncompressed protobuf bytes. `configuration-wire.json` is UTF-8 JSON
object text with `version: 1` and `rules.response` containing base64 protobuf.
It is the **serialized ConfigurationWire itself**, without a second JSON-string
wrapper; this file has no trailing newline. Forward its exact text to the SDK's
supported parser/initialization API. Do not JSON-load/dump it into a replacement,
base64-wrap the complete file, or reconstruct wire in an IPC server. Inspecting
its structure here did not replace or rewrite the artifact.

In this snapshot the decoded `rules.response` bytes equal `ufc.pb`, including
SHA-256. That equality is an observation, not a general producer requirement:
[packageWire](../../tools/ufc/generate.mjs) permits the public serializer to
canonicalize protobuf map order while checking semantic payload equality and
stable wire serialization. Verify both committed artifact hashes independently.
No compressed, obfuscated, precomputed-only or hybrid rules-resource variant is
catalogued. Original UFC JSON is authored source; local filtered JSON is a
diagnostic, not a substitute initialization artifact.

## Producer and provenance boundaries

[generate.mjs](../../tools/ufc/generate.mjs) passes each complete, unchanged
catalogued UFC to a separately supplied production Go converter CLI. It checks
the supplied executable against `--converter-sha256`, checks its declared source
inventory against [converter-lock.json](../../tools/ufc/converter-lock.json), then
uses public `configurationFromRulesBinary`, `configurationToString` and
`configurationFromString` APIs from **@datadog/flagging-core 3.0.1**. This producer
pin is separate from a downstream SDK/provider pin. No new Python serializer is
needed. The converter does not infer split reasons; authored reasons and
deliberately malformed inputs remain significant.

The opaque converter-source inventory/content identity is
`1407f5429e6f10d883011cc5a208749ee1061ebfc8d07374e983cef0eb7fa725`.
It is not the executable digest. The public repository does not contain an
immutable converter distribution, its private source inventory or a reproducible
build attestation. Exact converter regeneration was **not run** in this audit.
The maintainer must supply the matching CLI, expected executable digest, source
and inventory to reproduce generation; private source identifiers need not be
published to do so.

The manifest binds catalogue bytes, source UFC, converter source identity,
`generate.mjs`, `converter-lock.json`, package manifests/lock and both artifacts.
These relationships were checked against actual bytes and decoded flag keys.
The generator SHA-256 is
`7e6d634547ead40137226b026d74a003f3b5320bf995006d6e16b9dc7c47e4c8`;
its npm lock SHA-256 is
`503a5cbe78ac55bbfe96aa544d57696885175248d105ab6f47f01598961b618c`.
Evaluation cases, schemas, documentation, tests, `parity.mjs` and local diagnostics
are outside that committed artifact-input hash set. Case-only changes therefore
need an exact paired corpus revision even when artifact integrity still passes.

`ufc.generated.json`, `report.json` and `parity.json` are gitignored local
diagnostics, absent from this clean source checkout. Generation reports every
omission with a reason and checks retained JSON against the original except for
reported omissions. Public main preserves the omission keys, but not those
per-flag converter error reasons. Do not infer representability or an SDK defect
from a missing flag alone. Existing fixture CI does not run these rules-artifact
integrity/regeneration checks; see [tool README](../../tools/ufc/README.md).

## Case pairing, omissions and diagnostic limits

The resource corresponds by convention to root `evaluation-cases/*.json`:
**398 cases in 50 files**. Four cases target deliberately absent keys and remain
in diagnostics; they are not conversion omissions. The catalogue has only
`id`/`source`, with no case-directory or case-digest field. The current parity
tool hard-codes root `evaluation-cases/` for every resource. Adding an optional
UFC to the catalogue alone would not establish its adjacent case pairing.

For an independently reproducible case snapshot, the audit computed
`edca1ad3c52db2c35c9ca5ddd055201f9bc7b39be5ccf5629e5e91293d2bc659`:
SHA-256 of UTF-8 `JSON.stringify` of a path-to-file-SHA256 object, inserting all
50 `evaluation-cases/*.json` paths in lexicographic order. This is an audit
fingerprint, not an additional canonical manifest field.

| Suite | Source flags | Cases / files | Committed catalogued protobuf/wire pair |
| --- | ---: | ---: | --- |
| root/core | 68 | 398 / 50 | One pair; 50 encoded flags |
| `dependent-flags` | 21 | 16 / 1 | None |
| `flag-selection` | 6 | 62 / 11 | None; selection also needs its declared server contract |
| `regex` | 41 | 69 / 4 | None |
| `scale` | 10030 | 109 / 14 | None |
| `scale-json` | 10 | 13 / 3 | None |

These total 667 cases / 83 files across six suites. Optional suites remain
explicitly selected; their source/cases are not covered by the canonical binary.
Respect authored applicability and capability variants before resource setup;
the diagnostic parity tool itself does not perform platform applicability or
capability-variant execution.

The manifest's 18 conversion omissions account for 20 root cases:

| Omitted source flag | Core cases |
| --- | ---: |
| `disabled_flag` | 3 |
| `invalid-gt-condition-flag` | 1 |
| `invalid-is-null-condition-flag` | 1 |
| `invalid-one-of-condition-flag` | 1 |
| `malformed-allocations-flag` | 1 |
| `operator-grease-flag` | 1 |
| `semver-invalid-comparand-consecutive-dots-test` | 1 |
| `semver-invalid-comparand-dot-suffix-test` | 1 |
| `semver-invalid-comparand-leading-zero-test` | 1 |
| `semver-invalid-comparand-non-string-test` | 1 |
| `semver-invalid-comparand-syntax-test` | 1 |
| `semver-invalid-comparand-vprefix-test` | 1 |
| `semver-version-parts-five-part-comparand-test` | 1 |
| `semver-version-parts-four-part-comparand-test` | 1 |
| `semver-version-parts-one-part-comparand-test` | 1 |
| `semver-version-parts-two-part-comparand-test` | 1 |
| `split-features-first-valid-key` | 1 |
| `variant-type-mismatch-flag` | 1 |

This is conversion coverage accounting, not an SDK exclusion policy. Keep the
authored negative inputs and expectations. No incorrect canonical definition was
established by this audit; converter reasons and consumer-specific evidence are
needed to distinguish invalid authoring, unrepresentable inputs and SDK defects.

Running the existing pinned diagnostic in memory exercised 378 cases, omitted
the 20 above, and reproduced six missing-PARSE_ERROR discrepancies in binary and
wire. Original/filtered JSON had no reported mismatch on these exercised fields.
Every row below expects caller default, reason ERROR and PARSE_ERROR; encoded
results lack the error code:

| Root case ID, zero-based | Binary/wire reason | Changed value, where observed |
| --- | --- | --- |
| `test-case-invalid-shard-bounds-isolation.json#0` | DEFAULT | No value mismatch |
| `test-case-invalid-shard-bounds-isolation.json#1` | DEFAULT | No value mismatch |
| `test-case-missing-split-shards-isolation.json#0` | UNKNOWN | default → trap |
| `test-case-null-shard-range-isolation.json#0` | STATIC | default → catch-all |
| `test-case-semver-invalid-comparand-waterfall.json#0` | STATIC | unknown → fallback |
| `test-case-semver-validation-flag.json#17` | DEFAULT | No value mismatch |

This reproduces #76's remaining malformed-input category, not platform FIT
conformance or a new per-SDK bug classification. No ticket reference is invented.
Parity compares only supplied value/reason/errorCode/serialId/doLog fields under
a fixed 2026-01-01 clock; it does not compare split features or telemetry. It also
reports ten JavaScript unsafe-number warnings, so diagnostic agreement cannot
prove exact large-integer preservation. Mismatches remain diagnostic and never
select generated flags or authorize expectation rewrites.

## Relevant published work

The provider inventory returned 86 PRs (58 merged, 15 open, 13 closed), below the
200-record request limit. All 15 open PR file lists were read with pagination;
relevant descriptions and source heads were inspected. CI claims in descriptions
remain author-reported unless reproduced below.

| PR / observed state and head | Effect on this audit |
| --- | --- |
| [#47](https://github.com/DataDog/ffe-system-test-data/pull/47), merged, `31717112c606a52e99c92f289b0aa06779d46afe` | Introduced catalogue, producer, raw protobuf/wire, opaque provenance and diagnostic-only parity. Historical counts in its description predate current main. |
| [#76](https://github.com/DataDog/ffe-system-test-data/pull/76), merged, `e43bc29f38104a5a6b8bed6770aef4b1b8a4150c` | Explicit reason annotations and refreshed canonical artifacts. Main passes current integrity; earlier stale-main reports are superseded. |
| [#77](https://github.com/DataDog/ffe-system-test-data/pull/77), merged, `1c5337a448f9ab65cdaaf904b55e7b40e892aca5` | Root JSON-number precision case is now in the refreshed source/payload; JS diagnostic limitations still apply. |
| [#53](https://github.com/DataDog/ffe-system-test-data/pull/53), [#54](https://github.com/DataDog/ffe-system-test-data/pull/54), [#56](https://github.com/DataDog/ffe-system-test-data/pull/56), [#75](https://github.com/DataDog/ffe-system-test-data/pull/75), merged | Metadata/features, suite/applicability and explicit missing-key error contracts. Features/capabilities need real consumers; case edits are outside artifact hashing. |
| [#78](https://github.com/DataDog/ffe-system-test-data/pull/78), merged, `52205a7155f9c28c5bdd29b5897478e789035bfd` | Added scale/scale-json/regex suites; no corresponding catalogue entries. |
| [#86](https://github.com/DataDog/ffe-system-test-data/pull/86), open, `67873b470ce5cec9e2e1a45650dcc2fff12e9ac1` | Four root flags / 12 cases; no regenerated artifacts. Its own UFC SHA is `ac82b833a99749cea36fbd1ebd7e03c556af440c0de91bbaca999205faef7bfc`, but its manifest still names `e7b29c…`. Regenerate before binary/wire uptake. Its separately noted missing-targeting-key contract question remains unresolved by this audit. |
| [#51](https://github.com/DataDog/ffe-system-test-data/pull/51), open, `52bb99716928350948d35032769c3521d85a08ec`; [#41](https://github.com/DataDog/ffe-system-test-data/pull/41), open, `3ae4334e35d75c73a889f18b8e00c004e50776c0`; [#28](https://github.com/DataDog/ffe-system-test-data/pull/28), open, `150015bab3875d334be27c07bd095433ed74187e` | Root doLog, absent/empty identity and shard-bound contracts. These older heads contain no rules-resource manifest. Reconcile with current main, preserve deliberate negatives, and regenerate if their source changes are adopted. |
| [#79](https://github.com/DataDog/ffe-system-test-data/pull/79), still open, `1cc95396c400228fe5347c5c83e207a2bf1ffc63` | #78 explicitly supersedes it; current main already has the 69-case regex suite. Do not count it as a second missing implementation. |
| [#81](https://github.com/DataDog/ffe-system-test-data/pull/81), open, `6f6c97a54a659e43d3d5ed3a001fada1a3696e9a` | Adds opt-in hostile-values UFC/cases; no canonical catalogue entry or protobuf/wire pair. |
| [#48](https://github.com/DataDog/ffe-system-test-data/pull/48), draft/open, `5e2430d9ad36644e2cecb6a32ddb8d05d7c98ac6` | Separate opt-out contract package: seven declared compiler JSON/protobuf pairs and 30 paired cases. All seven pair digests and three provenance/observation/vector digests match its own manifest. No ConfigurationWire files or canonical catalogue integration. Producer execution against nonpublic source was not reproduced. Hand-authored contract examples remain distinct from declared compiler outputs. |

The other open PRs affect precomputed data, signing or CI rather than these rules
resource/case paths. PR #48's package is a draft capability contract, not an
alternative canonical resource or proof of an implemented evaluator. Public PR
status alone does not authorize adopting its contract or changing source pins.

## Follow-through and verification

1. Keep the current canonical pair and source/case commit together. Before #86
   uptake, obtain the existing converter and regenerate/check its paired output;
   do not hand-edit artifacts or resurrect a stale pre-#76 manifest.
2. Obtain the existing converter omission report before assigning reasons to the
   18 omitted flags. Preserve the six encoded negative-case discrepancies as
   unresolved representation/consumer diagnostics pending owning-layer proof.
3. For optional-suite binary support, establish explicit source-to-case pairing
   and applicable producer support. The catalogue currently supplies neither
   those resources nor per-resource case metadata. No later-mode activation is
   implied. Coordinate any shared loader request with WS-12 instead of duplicating
   internal code.
4. A public converter distribution/build recipe and a CI artifact-integrity gate
   remain reproducibility/maintenance gaps. They are follow-up proposals, not
   implementations or newly filed tickets.

Executed, with Node 24.13.0 and locked serializer 3.0.1:

```sh
npm ci --prefix tools/ufc --ignore-scripts --no-audit --no-fund
node tools/ufc/validate-rules-resources.mjs
node --test --test-isolation=none --test-reporter=tap tools/ufc/rules-resources.test.mjs
python tools/ufc/validate-rules-schema.py
python -B ci/validate-fixtures.py
```

Results: integrity passes with one resource / 378 diagnostic cases; all nine
explicit Node subtests pass; catalogue schema passes; six authored suites / 667
cases / 83 files validate. Python commands used an activated existing virtual
environment. Read-only digest, decoded-inventory and diagnostic probes produced
only temporary audit output. No source/artifact replacement was generated.

For a maintainer with the separately supplied matching converter, the existing
producer commands are below; these were **not executed**:

```sh
npm --prefix tools/ufc run generate -- --converter CONVERTER_PATH --converter-sha256 EXECUTABLE_SHA256 --converter-source SOURCE_ROOT --converter-source-files LOCAL_INVENTORY
npm --prefix tools/ufc run check -- --converter CONVERTER_PATH --converter-sha256 EXECUTABLE_SHA256 --converter-source SOURCE_ROOT --converter-source-files LOCAL_INVENTORY
```

Generation success establishes serialization/integrity, not FIT execution,
offline initialization, network behaviour, SDK conformance or platform-mode
acceptance. That execution remains with coordinator/local agents under the
existing sequencing and ownership gates.

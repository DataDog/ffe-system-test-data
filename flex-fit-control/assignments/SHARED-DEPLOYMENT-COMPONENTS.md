# Shared FLEX/FIT components by deployment mode

CONTROL-025. This is the infrastructure dependency row of goal.md, separate from platform implementation rows. It records requirements and inspected evidence; it does not dispatch later-mode work or claim full implementation. Platform rows still need an existing core IPC server and accepted online-precomputed cell before their other modes begin.

All four columns require the shared typed feature-flag IPC contract, platform transport/readiness, corpus checkout and applicability selection, unchanged canonical assertions, configuration/context provenance, exposure/evaluation intake observation, and deliberate CI activation. SDK capability gaps and per-layer exclusions must remain visible. Exposure/evaluation/RUM controls, direct/OpenFeature access and deployment mode are separate dimensions.

## Online precomputed

- Mock FlagServer serving authored precomputed JSON without losing raw response bytes, including encoded keys and malformed-response cases; correct SDK endpoint aliases.
- Shared fixture loader/runner, faithful typed details and context assertions, fresh configuration receipt, strict genuine invalid-response classification and bounded no-emission assertions.
- Bounded batching/intake polling and platform address/transport readiness; preserve simulator/emulator/physical-device differences.
- Corpus-aware CI checkout/selection and inherited marker handling.

Status: existing main has precomputed JSON serving; WS-03 extends the native server/harness/rejection path locally, with prior independent foundation review. Web rejection integration and platform-specific repair/coverage remain open. WS-01 CI/marker foundations are locally reviewed; full publication/runtime gates remain. See [WS-01](WS-01.md), [WS-03](WS-03.md), [review queue](../REVIEWS.md), and goal.md ACT-01/02/04–06. Shared CI repairs [FIT244](https://github.com/DataDog/rum-sdk-integration-test-framework/pull/244) are separate from flags conformance.

## Offline precomputed

- Corpus-to-portable-precomputed configuration loader using the SDK's actual supported configuration format and producer contract.
- Offline IPC initialisation, context replacement/reinitialisation and typed/emission assertions, with explicit denial/observation proving no configuration fetch.
- Full applicable corpus selection beyond a few portable examples; persistent-cache/restoration coverage requires a restore-aware consumer rather than assuming portable load proves restoration.
- Platform app/package resources and shared CI/corpus activation.

Status: portable/targeted work exists in draft/conflicting [FIT235](https://github.com/DataDog/rum-sdk-integration-test-framework/pull/235), stacked with tracking [FIT231](https://github.com/DataDog/rum-sdk-integration-test-framework/pull/231). It does not establish a complete shared all-platform/full-corpus path. Reconcile existing work before implementation. Restore-related fixture work [data85](https://github.com/DataDog/ffe-system-test-data/pull/85) needs an actual consumer. See goal.md ACT-07/08/11. Later-mode execution remains gated per platform.

## Online rules

- FlagServer binary rules endpoint with the SDK-required response headers/contract, serving corpus-generated UFC protobuf bytes; do not substitute precomputed JSON.
- Generated UFC/resource catalogue loader tying paired evaluation cases to ufc.pb and manifest/source/converter provenance.
- Online rules IPC/provider initialisation, actual configuration fetch/context/refetch and typed/intake assertions, plus platform/CI activation.

Status: inspected FIT main e07ae57ef3108b18b10d2f67690bc36caf8303af serves precomputed JSON and has no binary rules endpoint. Existing branches/PRs must be reconciled before adding one. Corpus production-converter tooling and generated protobuf/wire resources already exist; do not rebuild a parallel producer. Proposed UFC changes such as [data86](https://github.com/DataDog/ffe-system-test-data/pull/86) need regenerated resources and paired FIT uptake. See [reference and generator provenance](../REFERENCE.md#sequencing-clarification--november-27-control-004), goal.md ACT-09/10 and each platform's online-rules ticket. Endpoint integration and cross-platform activation remain unverified; no later-mode assignment.

## Offline rules

- Corpus-generated portable configuration-wire.json and paired rules cases/resource manifest, derived from the authoritative UFC producer.
- Offline configuration injection and rules IPC initialisation/context/reinitialisation using the real evaluator, with explicit network denial and typed/error/metadata/intake assertions.
- Full applicable corpus/platform loading, converter-omission accounting and CI activation; persistent restoration remains a separate tested capability.

Status: merged Browser [FIT221](https://github.com/DataDog/rum-sdk-integration-test-framework/pull/221) supplies limited offline lifecycle and rules-loader infrastructure. The full rules corpus remains intentionally skipped and Browser-specific paths do not establish native support. Extend/reuse these components when the corresponding online-precomputed row is accepted. See goal.md ACT-09/10/11 and each platform's offline-rules ticket. Do not treat manual lifecycle evidence as a required CI conformance gate or a full-corpus pass.

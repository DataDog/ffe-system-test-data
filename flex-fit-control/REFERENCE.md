# Reference and contract baseline

Snapshot: November 27, 2026. Refresh mutable heads before implementation; these are reference revisions, not permission to overwrite WIP.

## Repositories and baseline

- FIT: https://github.com/DataDog/rum-sdk-integration-test-framework ; inspected main e07ae57ef3108b18b10d2f67690bc36caf8303af.
- Corpus: https://github.com/DataDog/ffe-system-test-data ; inspected main fe24ed2c4872bf109b0c71ffb2229152d76b8963.
- FIT IPC contract: https://github.com/DataDog/rum-sdk-integration-test-framework/blob/e07ae57ef3108b18b10d2f67690bc36caf8303af/proto/feature_flags.proto
- Web executor: apps/web/src/ipc_executor.ts; shared runner: scenarios/feature_flags/harness.py; scenario collection: scenarios/test_feature_flags.py.
- Corpus source: precomputed-assignments/cases; schema: schemas/precomputed-assignment.schema.json; rules: ufc-config.json, evaluation-cases, evaluation-suites and generated rules-resources with manifest provenance.

## IPC at the inspected FIT main

FeatureFlagService has eight RPCs: InitProvider, SetEvaluationContext, FlushEmissions, EvaluateBoolean, EvaluateString, EvaluateInteger, EvaluateFloat, EvaluateObject. Older tickets mentioning nine operations need reconciliation with actual source.

EvaluationContext has optional targeting_key at field 1 and arbitrary protobuf Value attributes at field 2. Preserve absent versus blank keys and recursive values. InitProviderRequest fields: flagging_proxy_url=1; context=2; optional evaluation_flush_interval_ms=3; optional and_wait=4; optional configuration_wire=6. Field 5 is allocated to the deployment-access contract. Do not reuse existing field numbers to introduce modes. Reconcile #138/#136/#230 and #231/#235 schema/generated-code overlaps before integrating.

Typed responses carry value, optional variant/reason/error_code and flag_metadata. Preserve genuine result metadata and error classification. FlushEmissions is best effort; poll actual intake within bounded observation windows rather than assuming return means delivery. Await readiness when requested, and distinguish invalid configuration from network/transport failure.

## Matrix axes

Platforms: Browser, Android, iOS, React Native, Flutter, Kotlin Multiplatform, MAUI, Electron; Unity is Not planned. Cells: online precomputed, offline precomputed, online rules, offline rules. OpenFeature/direct access, exposure tracking, evaluation-event tracking, RUM enrichment and cache/restoration are additional dimensions. Cross-platform wrappers need distinct Android/iOS receipts where applicable.

## Activation pitfalls found in the audit

- Main precomputed collection enables Web only. New platform code alone does not widen inclusion.
- Main rules loader accepts server SDK identifiers and Web, not native FIT identifiers. Add applicable identifiers and loader wiring with native rules delivery.
- Main full offline-rules corpus has a global skip and placeholder parameters; lifecycle proof is distinct. Diagnose SDK/contract failures and record exclusions under Instructions.md before broader activation.
- Collection/lazy parametrisation use own_markers, missing inherited module/class inclusion/exclusion. Ensure tests really collect for the intended platform.
- Corpus-only gitlink changes select Web/fixture-validation rules, not native runtime jobs. Native job setup must initialise the corpus and run the intended host suite. The bot pin-update path deliberately avoids platform jobs; a green rollup can have no runtime evidence.
- Three Web numeric-decimal fixtures still reference FFLSDK-292 although the ticket is Done. Verify the actual SDK pin before re-enabling.
- Shared main runner initialises once; context-change/refetch, request-body observation, ETag/304 sequences and persistent restoration need real consuming paths. clear_requests already exists.
- Main lacks structured expectedResponseError handling. Historical local native foundations contain a candidate; reconcile it rather than duplicating architecture.
- Plain/obfuscated dependent fixtures are Web-only on corpus main; corpus #88 adds Android. Positive obfuscation is intentionally excluded for RN/Unity; their unsupported-consumer expectations need coordinated change when support arrives. Unity SDK support is FFLSDK-263.
- Numeric precision includes reflect genuine platform API limits. Do not widen Int64 fixtures indiscriminately.
- Proposed UFC changes need regenerated resources/manifest and FIT pin uptake. Current inspected main source hash matches its manifest. Opt-in suites do not activate automatically.

Top-level eligible cases among 65: Web 20, Android 60, iOS 62, RN 35, Flutter 62, KMP/MAUI/Electron 18 each, Unity 38. These are static eligibility counts, not execution/pass counts; nested filters and FIT skips further reduce coverage.

## Existing work to preserve

FIT Android #136/#240 overlap; #241 is incremental on #136 and #139 preserves direct access. RN #230 is stacked on older #138; preserve Sameeran's work when reconciling with newer local candidates. #231 adds independent Web tracking; #235 targeted portable/offline scenarios; #234 dependent flags. #244 repairs shared KMP build/diagnostics, not flags conformance. See goal.md for links and audit-time state.

Corpus #88 Android dependent activation; #84 preview-pin fidelity; #85 restoredReason/signed-zero/Unicode; #81 hostile values; #86 reasons with generated-resource follow-up; #79 opt-in regex. #48 opt-out, #87 signing and #13 producer cases need explicit consumers/scope. #23 is evidence-only and #12 legacy.

The coordinator retains a November 17 package of shared native foundations, Android/iOS/RN/Flutter/Unity FIT candidates and SDK/provider companions. It contains overlapping shared/activation changes and historical runtime receipts. These are not all published or current. Request a portable handoff through REQUESTS.md before depending on inaccessible local material. Do not report those historical checks as fresh execution.

Keep authored reasons/source shapes intact and report disagreements. Investigated SDK gaps may be excluded as explicitly authorised; exclusions are not evidence of SDK correctness. Preserve source-to-artifact provenance and list conversion omissions.

## Existing local WIP inventory

Read [WIP-INVENTORY.md](WIP-INVENTORY.md) before implementing or replacing native/shared code. It distinguishes dirty candidates, unpushed commits, already published work and historical/deleted temporary checkouts. Request portable diffs through REQUESTS.md when local evidence is inaccessible.

## Sequencing clarification — November 27, CONTROL-004

An existing core FIT IPC server gates row eligibility; no server means the whole row is deferred. Verify source and startup/transport wiring before assigning. Unity is Not planned and has no verification/implementation assignment. Complete and independently accept online precomputed before parallelising the remaining three modes within an eligible row.

At the inspected FIT origin/main, src/rum_sdk_test/flagging/server.py exposes POST /flag-config returning precomputed JSON and OPTIONS; it does not implement a binary rules endpoint. Reconcile WIP/PR extensions before adding one. This is a source inspection, not runtime proof or a complete audit of every branch.

Corpus tools/ufc/README.md documents generation through the production Go converter and pinned flagging-core serializer. rules-resources/catalog.json currently names canonical-evaluator from ufc-config.json. The generated resource contains ufc.pb and configuration-wire.json with manifest provenance. The latter contains the portable wire string without extra JSON quoting. Use these generated resources and their paired cases; inspect open and merged corpus changes for additional UFCs/encodings. Do not assume every opt-in suite is already represented in the catalogue or that conversion includes every source flag.


## All-mode init reconciliation — CONTROL-031

See [INIT-CONTRACT-AUDIT.md](INIT-CONTRACT-AUDIT.md). URL versus wire cannot select all four modes. Explicit mode/source/evaluator validation and coordinated generated-client/server migration are proposed, not implemented. Existing rules artifact production is JavaScript-backed; Python verifies/loads/forwards it. No new Python SDK serializer or generic RPC rewrite is assigned.

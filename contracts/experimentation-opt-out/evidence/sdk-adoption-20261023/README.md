# SDK adoption and native evidence

The [source refresh](../../sdk-refresh.md) precedes each target's independent implementation pass.
Each owner recorded that pass before reading review comments. The original decisions and their authority remain unchanged.
This directory adds implementation evidence and review replies to the draft central proposal.

| Target | Implementation | Native evidence |
| --- | --- | --- |
| [iOS #3338](https://github.com/DataDog/dd-sdk-ios/pull/3338) | [386f8c5](https://github.com/DataDog/dd-sdk-ios/commit/386f8c5d59af9c9ffb9cf7dee6aa2e90c95a5c0f) | [237 Flags tests, 13 selected integration tests, and 187 source-adapter cases](ios/final-validation.json) |
| [Android #4024](https://github.com/DataDog/dd-sdk-android/pull/4024) | [6e5fe6c](https://github.com/DataDog/dd-sdk-android/commit/6e5fe6cf6266a5d965a44a7f1958f1bfe1fcf735) | [1792 native executions, 187 profile cases, and three emulator tests](android/exact-6e5fe6c-receipt.json) |
| [Java #12950](https://github.com/DataDog/dd-trace-java/pull/12950) | [578ffa77](https://github.com/DataDog/dd-trace-java/commit/578ffa77cbc52e6d5d8950657a05863a449f59ab), test-only follow-up to a4d3dfb | [2454 native tests, 90 policy and 36 operation cases per provider, and 5 runtime tests per provider](java/README.md) |

The [browser reference replay](browser-reference/browser-receipt.json) matches all 313 semantic cases at its merged PR head.
Its pending-assignment adapter injects a core result. It does not establish browser lifecycle or transport correctness.
Go source was rescanned at its merged head. Earlier Go native receipts retain their original source revisions.

The selected profiles remain pinned to central commit `0520866bedb8c059df9c493cfe27ad294390c603` and manifest `078465ba0a37f193e65c3641197ac859c375c9d114d0d131ccc330d0c28dfa31`.
This evidence addition does not change the model, selected case IDs, or semantic decision revisions.
See [linked validation history](../../decision-history.md#historical-linked-checks) for exact sources, failures, controls, and limits.

Native evidence establishes different boundaries:

- iOS uses a dedicated simulator, scripted assignment HTTP, and local event intake. Source-adapter and mutation receipts retain their original execution revisions.
- Android uses a real SDK core and local HTTP intake on an API 36 arm64 emulator. Callback saturation and worker lifetime require native checks.
- Java binds the installed providers and agent to the signed source. Legacy uses Remote Configuration; standalone uses its supported public HTTP source and TLS intake.
- The stock Java test agent lacks the evaluation-event route. A saved local adapter adds capture through the existing handler.
- Standalone Java Remote Configuration fails because the inherited baseline lacks a compatible bridge. The [failed receipt and source boundary](java/runtime/standalone-rc-boundary/) remain recorded.

Java's [omitted/null doLog disposition](java/local-d010-scope.json) is local compatibility under unchanged D010.
It does not create a shared missing-field default. Browser/mobile, Go, and Java retain their scoped timestamp grammars.
D017 Java call observations establish skipped helper calls, not a speedup.
The [Java smoke follow-up](java/smoke-followup/README.md) preserves the hosted failure and fixes its test expectations.
A→B→A produces three exposures. Full frozen-source suites pass 373 tests each on JDK 11 and 25.
The exact signed follow-up passes four smoke tests. Production and earlier runtime receipts remain unchanged.
All five formerly failed hosted smoke jobs pass. The [Payara dependency retry](java/payara-ci-retry-result.json) passes after an initial Maven HTTP 429 failure. Its dependent checks remain separate.

The [iOS hosted matrix](ios/HOSTED-FLAGS-386f8c5.md) records all 19 added tests passing on five platforms. It preserves TIA skips and removed test names.
Android [startup recovery](android/review6-runtime/exact-6e5fe6c-receipt.json) uses the real main looper and background workers with injected failures.
The Android Foundation documentation gate remains unavailable because this host lacks FactoryKit.
Its [traceback](android/review6-foundation-worktree.txt) retains the original bytes; an [export path map](android/export-path-map.json) corrects its source filename suffix.

Review backlinks are recorded for [iOS](ios/published-replies.json), [Android](android/published-replies.json), and [Java](java/published-replies.json).
All 39 SDK review threads have verified replies. Thirty-six are resolved; three retain explicit delivery or grammar dispositions.
The [rollout state](rollout-state.json) records current heads, CI snapshots and remaining gates. Thread resolution does not establish correctness.
The [older Java Boolean prototype](java-obsolete-pr-closure.json) was closed as superseded. One active implementation PR remains per language.

[Backend dependencies](backend-dependencies-final.json), Swift provider #44, hosted checks, and human approvals remain separate gates.
No SDK was merged, released, or deployed. The central proposal remains draft.

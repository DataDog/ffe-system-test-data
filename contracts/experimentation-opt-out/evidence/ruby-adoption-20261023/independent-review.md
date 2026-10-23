# Ruby experimentation opt-out independent review

Status: source and final runtime evidence review pass at signed Ruby `6c4e268d18e68523f0e5e6546a86d6754c350e3a`. No source finding remains open. Final acceptance binds native `ead1d3db2aa16e494f23e47b946ff12a7a1be53a` and harness `d4c4308b3600a48885564f687c37800b4eeb5c19`. Earlier pending statements below describe historical review stages.

The reviewer read production code before PR feedback. The reviewer changed no SDK source, expectations, or dependency files.

## Reviewed identity

- Initial immediate head: `ae37a103c4cc4524bd48a62723b261d63d7b8e31`.
- Future stack head: `08d63752f28308279b8c1410879d81f195c437b3`.
- Combined master-merged head: `3c59360edd1bc14f9cd3c4aefe9dae1e0013c8fb`, with the candidate changes identified below.
- Central contract: `98f1f5a4aab6e92fa0b74787cee94e36cc7c8e80`.
- Required libdatadog implementation: `ead1d3db2aa16e494f23e47b946ff12a7a1be53a`.
- Instructions read: root AGENTS.md, scoped OpenFeature AGENTS.md, LibdatadogDevelopment.md, lean-sdk-implement, and rollout coordination.

## Findings and disposition

| Finding | Counterexample and consequence | Contract classification | Candidate disposition |
| --- | --- | --- | --- |
| Invalid native string bytes could become absence | A present cutoff containing byte FF passes the original Ruby string/NUL guard. Native UTF-8 conversion drops the attribute. Enabled modes can then evaluate experiments normally. UTF-16LE instead raises Encoding::CompatibilityError during the original include? check. | D002 implementation boundary. No semantic revision. | NativeEvaluator validates a duplicate forced to UTF-8. It rejects invalid bytes and embedded NUL without changing the source string. Public-provider tests cover binary FF, invalid UTF-8, and UTF-16LE in all modes. |
| Embedded NUL attribute names could alias the reserved property | A key named dd_experimentation_opt_out_at followed by NUL and suffix is absent under exact Ruby lookup. C string conversion previously changed it into the reserved key. | D002 exact-property preservation. No semantic revision. | C conversion skips names containing NUL before extracting targeting_key or creating native attributes. A public-provider regression exercises the alias. |
| Activation expectations used the superseded scope | The existing core test and documentation required PARSE_ERROR for malformed activation in disabled and immediate modes. The pinned native implementation only requires activation validity for future mode with a valid cutoff. | Existing D004 revision 2 adoption. No semantic revision. | The test now checks the mode-specific result, variant, and logging eligibility. Documentation states the correct scope and includes unreachable allocations. |

The reviewer rejected an ASCII-only validation alternative. Chrono accepts internal Unicode whitespace between some timestamp components. The final byte-validation helper preserves that native grammar. Surrounding whitespace remains subject to the native D005 restriction. No browser parser or mobile acknowledgement rule was imported.

## Production path and configuration

Provider construction resolves an explicit mode before configured/environment defaults. Nil defers to configuration. Construction stores the resolved mode. Explicit disabled overrides an invalid environment value.

The extconf checks link actual native functions. Conditional C definitions expose only supported Ruby methods. Disabled needs neither added method. Immediate requires the legacy options method. Future requires the enum method. Capability tests distinguish unavailable, legacy-only, and complete support.

Evaluation follows Provider -> EvaluationEngine -> NativeEvaluator -> C extension -> the native rules evaluator. The Ruby guard runs before lossy native attribute conversion. The engine snapshots its evaluator. NoopEvaluator retains readiness behavior before configuration arrives.

Native assignment results control exposure eligibility. The separate telemetry option wraps telemetry hooks and controls span enrichment. The policy change does not reuse that option. Source inspection alone does not prove telemetry intake.

D015 remains Go-scoped. Ruby does not use the Go NoopProvider construction factory. This review does not request a constructor-order change based on that theorem.

## Adapter review

The copied fixture contains all 90 policy rows. The reviewer compared parsed rows with the pinned central corpus and found exact equality.

- Source corpus SHA256: `c4a1b9c9eed7197b8d66c1d3e46fcaaa4ec70143a2583b31baa04086c8f652dd`.
- Copied policy SHA256: `0d396beb2b627606f795386340d5e9d7443a40c51e84200b60527938969f7175`.
- Grid: three modes, three attribute states, five activation states, and two valid doLog values.

The adapter constructs real configuration and calls NativeEvaluator without a native mock. Before/equal/after values differ by one nanosecond. Invalid attributes use a Boolean. Invalid activation uses an invalid string. Missing activation omits the property.

Expected error and exclusion come from the fixture. Assertions check default or selected value, variant, allocation key, error code, and log eligibility. An ordinary fallback makes exclusion observable. No current SDK output supplies expected results.

The 90 rows do not cover every integration obligation. They omit missing-flag precedence, unreachable allocations, targeting rules, no-fallback results, malformed doLog compatibility, telemetry delivery, lifecycle, and complete timestamp grammar. Existing native tests and focused wrapper tests must cover applicable obligations. No broader coverage claim follows from this profile.

The 21 new public-provider string-boundary examples call the real native evaluator. Their exposure reporter is a mock. They prove provider return behavior when executed, not exposure HTTP delivery. The initial NUL-key example used a valid value. The final example uses an invalid value. This distinguishes absence from aliasing in both enabled modes.

## Executed checks and remaining evidence

The reviewer ran only source inspection, fixture equality/hash checks, and small Ruby string expressions. The string probe confirmed that ASCII-8BIT byte FF passes the original guard. It also confirmed that UTF-16LE raises at the original include? call. The reviewer did not run the native suite or public-provider tests.

Before qualification, verify all 90 adapter cases execute without skips. Bind the loaded native library to the required dependency SHA. Run the repository test tasks and applicable RBS/style checks. Preserve unsupported-library capability results separately from supported-library native results.

Useful defect controls are removal of the Ruby byte guard, removal of the C name guard, and restoration of unconditional malformed-activation failure. The relevant tests must fail with the control and pass after restoration. Do not alter fixture expectations.

The final exact-head review must inspect the signed candidate and receipts. A passing Ruby wrapper run does not prove package release, hosted CI, backend deployment, or HTTP telemetry delivery.

## Feedback classification after own-pass freeze

The coordinator reports no inline human threads or new Codex findings in either draft PR. PR 6521 has an older no-findings Codex review at ae37a103 and a request for immediate-mode native validation. PR 6542 has bot coverage feedback only. This is coordinator-supplied feedback classification, not an independent live GitHub read or approval.

The three own-pass findings reuse D002 and D004 revision 2. They do not change the Lean policy or its expected outputs.

## Initial candidate source binding

These hashes bind the reviewed working files. They do not identify a signed final commit.

| Repository-relative path | SHA256 |
| --- | --- |
| `ext/libdatadog_api/feature_flags.c` | `d61a6c59bff631ae29177a4b98fa4c5a15a682980e1dfae1e8e9414fcb703b1b` |
| `lib/datadog/open_feature/native_evaluator.rb` | `d006548da1f2cd59c127186c41712c017423d02dbf8d241f7131289c494582a8` |
| `sig/datadog/open_feature/native_evaluator.rbs` | `2e36c771eecb7bd0feebd9c09385a39b5bb1b140046d3b434b454689c97d1bae` |
| `spec/datadog/open_feature/native_evaluator_spec.rb` | `41694ea53c898c2cad2916738e8dcf7d65cf7b64acb74d600cca1d831ddede4a` |
| `spec/datadog/open_feature/provider_spec.rb` | `6488acf3c2c24c53b3300952f8917a6c3e44849fa954a7b02c8a19892d7f2fcc` |
| `spec/datadog/core/feature_flags_spec.rb` | `b6bd92fd8127060940f2cfcc5d3ffe7331b4051ac07ea0d47322ea683b6a65fd` |
| `docs/GettingStarted.md` | `711ea0be9a0b350c37f9b7dcf3380240b9836af46435c5c90417c2965baa6b89` |
| `spec/datadog/open_feature/fixtures/experimentation-opt-out-policy.jsonl` | `0d396beb2b627606f795386340d5e9d7443a40c51e84200b60527938969f7175` |


## Signed-source review

The reviewer independently verified both signatures with the task's allowed-signers file and `/usr/bin/ssh-keygen`. Both worktrees were clean.

- Ruby: `ce7658cbeace9cc60c4f22729d923badabcd4aef`.
- Harness: `d4c4308b3600a48885564f687c37800b4eeb5c19`.
- Verified signer: `leo.romanovsky@datadoghq.com`.
- Verified key fingerprint: `SHA256:OARkNwfvap+5aDU6m+alCIv0E+miVmtHAsf665i8dv0`.

The final semantic changes match the reviewed candidate. Formatting changes do not alter the tested input states. The RBS signatures include the native methods and validation helper. No additional correctness finding was identified.

### Defect controls and candidate evidence

The reviewer inspected the control script, restoration receipt, and assertion failures. Removing the Ruby byte guard causes six failures in 21 public-provider examples. Invalid byte strings return the experiment. UTF-16LE returns GENERAL instead of INVALID_CONTEXT.

Removing the C attribute-name guard causes two failures in 21 examples. The invalid NUL-suffixed property returns the default in immediate and future modes. Both require normal experiment evaluation because the exact reserved property is absent. These are expected behavioral failures, not build failures. The script restores both source files in its finally block.

The saved candidate native retry log reports 1043 latest-dependency examples and 1039 minimum-dependency examples. Both runs report zero failures and no pending/skipped examples. The focused core log reports 44 examples and zero failures. The final scoped style log reports 12 files and no offenses. The full Steep log reports no type errors.

These are candidate-run observations. The reviewer does not relabel them as completed exact-commit reruns. Earlier missing-GMP, RuboCop, and missing-Vale failures remain historical diagnostics. The empty Vale exact-head log alone does not establish its process exit status.

### Details controller and immutable expectations

The harness controller now calls the SDK's fetch_*_details methods. It serializes the actual value, reason, error code, variant, and flag metadata. Allocation identity comes from the provider's `__dd_allocation_key` metadata. It does not reconstruct decisions from expected fixtures or configuration.

The controller retains one evaluation per targeting key and returns the last details with the evaluation count. The existing rescue response lacks required error and metadata fields. The contract assertions therefore reject such a response rather than count it as conformance.

The fixture, generator, and assertion helper have no diff from harness `a45f53c4aef20eb130116556598e593785657159`. The reviewer checked these pins:

| Frozen artifact | Count | SHA256 |
| --- | --- | --- |
| SOURCE.json | one manifest | `0407fb0330aefbeb086f16784aba0e5629f9e0241e80cd1416308146cbc9679d` |
| runtime-cases.json | 252 materializations covering 90 policy rows | `c47cf29d64d176b418c916229208875b904cb871ed43a78c57a3838987911226` |
| lookup-cases.json | 9 lookup cases | `2538e44437c075adba6a58b354a307d6d67901f1b653daeaf3898fe5d5104961` |

The loader checks the manifest hash, every referenced file hash, unique case counts, and policy coverage. Details assertions require three actual responses per case. Delivery assertions compare exact exposure identities and hashed evaluation subjects/counts. Expected values remain independent of Ruby output.

The Ruby controller change does not itself prove any HTTP run. Runtime qualification still needs the exact loaded SDK and native library, nonskip counts, captured responses, and actual exposure/evaluation requests. Remote Ruby 3.1/4.0 and HTTP intake were not complete at this review.

### Signed-source hashes

| Repository-relative path | SHA256 |
| --- | --- |
| `ruby/ext/libdatadog_api/feature_flags.c` | `d61a6c59bff631ae29177a4b98fa4c5a15a682980e1dfae1e8e9414fcb703b1b` |
| `ruby/lib/datadog/open_feature/native_evaluator.rb` | `d006548da1f2cd59c127186c41712c017423d02dbf8d241f7131289c494582a8` |
| `ruby/sig/datadog/open_feature/native_evaluator.rbs` | `2e36c771eecb7bd0feebd9c09385a39b5bb1b140046d3b434b454689c97d1bae` |
| `ruby/sig/datadog/core/feature_flags.rbs` | `263be969a7c52def5e5fc742ee3df8b47a229e19dc9dccf51882089e7a3a393f` |
| `ruby/spec/datadog/open_feature/native_evaluator_spec.rb` | `d7b19c6f8827c1e7413feed5a70a0fdbee41cc2105c8cc73c92b7a8898fcece5` |
| `ruby/spec/datadog/open_feature/provider_spec.rb` | `3b5e1ceb70401cd57290eff856e441fb464716bc733d6795b6024431c9fd5459` |
| `ruby/spec/datadog/core/feature_flags_spec.rb` | `1a61a946b6d2b46f59c073e6a79cb0f5806a4ae98975af1f40e68927f24b28d5` |
| `ruby/docs/GettingStarted.md` | `711ea0be9a0b350c37f9b7dcf3380240b9836af46435c5c90417c2965baa6b89` |
| `ruby/docs/LibdatadogDevelopment.md` | `7f342b21b031ebdcc6768b93640b4d9a3d3398a4941e4ec5dc61db77c171813d` |
| `ruby/spec/datadog/open_feature/fixtures/experimentation-opt-out-policy.jsonl` | `0d396beb2b627606f795386340d5e9d7443a40c51e84200b60527938969f7175` |
| `system-tests/utils/build/docker/ruby/rails72/app/controllers/open_feature_controller.rb` | `c3be144260841e9f1b4bc774d3b9ccd30404deefb0fbf2f290a4542db0960a95` |


## Local exact-head receipt review

The reviewer checked `exact-head-commands.json` after the rerun completed. Both commands bind Ruby `ce7658cbeace9cc60c4f22729d923badabcd4aef` and report clean source before and after execution. Current source remains clean at that SHA.

| Local execution | Result | Verified log SHA256 |
| --- | --- | --- |
| Ruby 3.4.7, OpenFeature latest and minimum dependency tasks | 1043 + 1039 examples, zero failures, zero pending/skipped | `106f3e570c15c98a66eec9fbd767696a194ba455aa53cc20457d4b762a6b4c50` |
| Focused native core task | 44 examples, zero failures, zero pending/skipped | `27a2bd7159e4a5b82471778a54a6aeaa76420d4e3192ac8c4850969b1d6c664f` |

The native task uses the full OpenFeature spec pattern. It includes the 90-case adapter and public-provider boundary cases. The reviewer verified both saved log hashes against the receipt.

A separate loaded-image probe uses the same Ruby bundle environment after testing. It identifies the extension and loaded libdatadog dylib through dyld. The reviewer verified the probe and linkage receipt hashes. The loaded dylib hash is `7a09b43e8d1693ae22ae65fa1afebfec08407901c4ca53e2091aafc4acb79818`, which matches the recorded ead1d3d artifact. The extension hash is `db4d205d15e5f3014d2163cd74be1c64a366e63574222e76481d30a7db1c8c39`.

The earlier sandbox failure is preserved in `native-exact-head-sandbox-failure.log`. Its hash matches the historical receipt. The reviewer notified the coordinator that the old receipt still referenced the later successful log filename.

The runtime controller probe reports 10 successful checks using real OpenFeature 0.5.1 on Ruby 4.0.1. It uses a deterministic test provider and a controller shell. It verifies actual details serialization for all five value types, errors, metadata, and two subjects. It does not load the Datadog evaluator or perform HTTP intake.

The reviewer also inspected the planned runtime overlay scripts. They isolate task container/network names and loopback ports. The Ruby overlay selects Ruby 4.0 and the native vendor directory. Neither script changes expectations, assertions, SDK source, or the details controller. Applied overlay hashes and running-container identity still require final receipt review.


## Remote native matrix and compatibility review

The reviewer verified saved log hashes and exact counts for Linux/x86_64. Both receipts bind signed Ruby `ce7658cbeace9cc60c4f22729d923badabcd4aef`. Both sources remained clean.

| Runtime | Latest and minimum OpenFeature dependency tasks | Log SHA256 |
| --- | --- | --- |
| Ruby 3.1.7 | 1039 + 1039 examples, zero failures, zero pending/skipped | `06b31823f6dbfb009fbf672c416e81e67098beed898ed4e3fc520e6e6bdd5845` |
| Ruby 4.0.1 | 1043 + 1039 examples, zero failures, zero pending/skipped | `75e0e262b0bf26964bfca141ea078e81f252c49fe8383bae05a7f2f58121d370` |

Separate process-map probes load each compiled extension after the matrix run. Both map the native library hash `d57541423e435cbb6c76b35954e16cd738525a667b031fad7ad69dd098cb4921`. This matches the artifact manifest from the clean ead1d3d build. All seven recorded Ruby source hashes match the signed Ruby commit. The probes do not record OpenFeature version because those separate probes did not load that gem; task logs identify the matrix dependency runs.

The native build preserves default features and adds the two Ruby-required features. The matrix runs do not prove HTTP behavior.

The first HTTP app attempt failed during Rails boot, before tests. The runtime owner reports a net-imap 0.5.9 incompatibility with Ruby 4.0 Ractor.make_shareable. The failed attempt and lockfile remain preserved remotely. The reviewer has not yet inspected that exported failure capture.

The revised task overlay pins net-imap 0.6.2. It keeps the SDK, controller, corpus, and assertions unchanged. The reviewer verified all seven overlay base hashes against signed harness d4c4308. Five paths isolate names and ports. Two paths select Ruby 4.0, the native vendor directory, and the net-imap compatibility pin.

This is an explicit runtime dependency exception. Final HTTP acceptance requires the applied overlay hashes, final dependency lockfile, complete captures, and running-container identity. The reviewer requested a lockfile comparison to detect unrelated dependency updates. No HTTP acceptance claim is made yet.


## Test-order correction and historical HTTP replay

Ruby `6c4e268d18e68523f0e5e6546a86d6754c350e3a` changes only provider_spec.rb. The reviewer verified its signature and clean source. The capability check now runs inside the provider let. It executes before an outer hook can construct an enabled provider against an unsupported native library. Assertions, production paths, and corpus remain unchanged. No source finding is open.

The ce7658 HTTP export remains historical. The reviewer verified all 33 compact-export file hashes and all per-mode raw capture manifests. JUnit records seven tests per mode, with zero failures, errors, or skips.

The reviewer independently replayed saved policy, recovery, and lookup observations against the unchanged harness assertions and pinned expectations. Each mode includes 504 policy responses, 24 recovery responses, and 12 lookup responses. All exact details, exposure multisets, and hashed evaluation identity/count assertions pass.

| Historical ce7658 mode | All captured HTTP responses | All exposure events | All captured evaluation count | Replayed Lean-group exposures | Replayed Lean-group evaluation count |
| --- | --- | --- | --- | --- | --- |
| disabled | 1197, all HTTP 200 | 305 | 939 | 92 | 288 |
| immediate | 1197, all HTTP 200 | 94 | 939 | 26 | 288 |
| future | 1197, all HTTP 200 | 171 | 939 | 32 | 288 |

The all-capture counts above come from saved responses and intake events. They are not inferred from test code. The separate replay covers the three Lean-derived test methods. JUnit records the other four native integration methods as passed.

The HTTP app used Ruby 4.0.1 and OpenFeature 0.6.5. This differs from the earlier OpenFeature 0.5.1 controller-only probe. The exported initial failure record identifies zero executed tests and the net-imap 0.5.9 Ractor.make_shareable boot stack. The final lockfile hash matches its build receipt. The lock diff changes only net-imap to 0.6.2 and adds the explicit constraint.

These observations do not qualify the later test-only commit as an exact-head run. Final acceptance will bind the new native matrix, rebuilt app, and all three HTTP modes to 6c4e268.


## Final-head local rerun and recorder review

The reviewer verified the completed local rerun at 6c4e268. Saved log hashes match exact-head-commands.json. OpenFeature reports 1043 + 1039 examples with zero failures. The core task reports 44 examples with zero failures. No pending or skipped examples appear. The fresh loaded-native-final-head.json probe retains the same reviewed extension and native library hashes.

The central recorder was reviewed before execution. Its current design appends validation and adoption evidence without changing semantic decision fields, Lean definitions, or expected outputs. The reviewer requested exact Ruby/native/harness identity guards and approved-file hash checks. Historical CI failure and released-native compatibility rows require their own exact source and result counts. A pending RSpec example counts toward total examples and must not be reported as passed.

Final remote native and HTTP reruns remain pending. runtime-review.json will be written only after final exported observations and identity pass independent review.


## Final exact-head runtime evidence review

The final source and evidence review passes. The reviewer verified all 34 compact export hashes and all raw capture manifests. The final record is `runtime-review.json`. It approves 30 bounded files by exact hash, including runtime-summary.json. Bulk logs, raw HTTP headers, environment files, and the capture archive remain local. The reviewed export contains synthetic observations. No secrets or private URLs were found.

Both native matrix receipts bind signed Ruby `6c4e268d18e68523f0e5e6546a86d6754c350e3a` and native `ead1d3db2aa16e494f23e47b946ff12a7a1be53a`. The reviewer checked exact log hashes and counts. Ruby 3.1.7 reports 1039 + 1039 examples. Ruby 4.0.1 reports 1043 + 1039 examples. Both report zero failures and zero pending examples. Separate post-test process-map probes identify the reviewed native library and each compiled extension. Their seven Ruby source hashes match the signed commit.

All three HTTP modes bind harness `d4c4308b3600a48885564f687c37800b4eeb5c19`. Each running app has the final image and reviewed native library. Its installed Ruby source hashes match the signed commit. Unlike the matrix probes, these process-map receipts identify the running HTTP app.

| Final mode | Captured responses | Exposure events | Evaluation count | JUnit |
| --- | --- | --- | --- | --- |
| disabled | 1197, all HTTP 200 | 305 | 939 | 7 passed; zero failures, errors, skips |
| immediate | 1197, all HTTP 200 | 94 | 939 | 7 passed; zero failures, errors, skips |
| future | 1197, all HTTP 200 | 171 | 939 | 7 passed; zero failures, errors, skips |

These counts come from saved responses and captured wire events. The reviewer matched compact intake rows to raw Agent captures. Total observations are 3591 responses, 570 exposures, and 2817 evaluations. JUnit records 21 passed tests with no failures, errors, or skips.

The independent saved-capture replay covers policy, context recovery, and lookup precedence in each mode. It checks generated expectations, exact details, exposure multisets, and hashed requested-subject evaluation counts. Each mode passes 504 policy responses, 24 recovery responses, and 12 lookup responses. Each mode records 288 evaluations for these methods. Exposure counts are 92, 26, and 32. The other four integration methods have saved passing JUnit results and captured observations; their assertions were not independently reconstructed.

The HTTP run uses Linux/x86_64, Ruby 4.0.1, and OpenFeature 0.6.5. It uses the reviewed namespace, port, Ruby engine, native vendor, and net-imap 0.6.2 overlays. The dependency lock changes only net-imap and its explicit constraint. No SDK source, controller, expected output, or test assertion changed. The initial ce7658 net-imap 0.5.9 boot failure remains historical and records zero executed tests.

The current recorder has exact Ruby/native/harness guards and approved-file hash checks. It creates parent directories before copying nested evidence. It appends validation and adoption evidence without changing semantic decisions or Lean expectations. No recorder blocker remains for these approved files.

The released-native compatibility result is separate. Each minimum/latest appraisal reports 77 passed and 21 pending examples, with zero failures. Combined counts are 154 passed, 42 pending, and 196 total. These checks validate capability guards against released libdatadog 46.0.0.1.1. They do not prove opt-out behavior on that released library. The historical CI failures remain recorded.

Acceptance applies only to this source and recorded evidence. It does not approve merge, release, deployment, or fleet adoption. Local Remote Config and Agent captures do not prove production backend behavior. Other HTTP Ruby runtimes, full parser parity, concurrency properties, and D017 timing remain outside this result.

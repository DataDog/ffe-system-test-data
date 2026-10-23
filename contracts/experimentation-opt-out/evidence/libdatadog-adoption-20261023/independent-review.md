# Independent libdatadog review

No open source correctness finding remains at `ead1d3db2aa16e494f23e47b946ff12a7a1be53a`. The checkout is clean. The surrounding-whitespace rule is a narrow libdatadog adoption of D005. It does not adopt the complete browser parser.

This review was read-only. I reviewed production paths, tests, the C adapter, and recorded observations. I changed no SDK source and ran no native build or test process.

## Baselines

- Original PR head: `3eb48e6999b3792267b5179c9e1f4132298b958d`.
- Main merge: `6b5bc0b7cf2f9abdc64b12177fb059feeb3b187d`.
- Merged main parent: `9c3464f5d688c4963d10ec67eae2e9be7733b6c2`.
- Central contract: `f8a4176cd8360b12b56a8b6ec6ef215e2cc21077`.
- Canonical fixture submodule: `0781ce2c55f9da7f9290035c768bbc46570556c0`.

I read repository `AGENTS.md`, the applicable decisions and proofs, and `lean-sdk-rollout/references/coordination.md`.

## Production reachability and correctness

| Requirement | Source assessment |
| --- | --- |
| D002 and D016 | `eval_flag_with_options` resolves policy before flag lookup. Disabled mode ignores malformed input. Enabled malformed input returns `InvalidContext`. It does not mutate context. |
| D003 | Preparation retains parsed, missing, and failed activation states. Compilation records flag-wide invalidity once. Evaluations reuse compiled timestamps and validity. |
| D004 r2 | `Flag::eval` consumes invalid activation only for effective future policy. This happens before allocation traversal. Unreachable and ordinary allocations cannot hide malformed activation. Valid neighboring flags remain independent. |
| D011 | Exclusion uses `do_log` and `activation >= cutoff`. Missing activation is conservative. Eligible allocations continue through existing time, targeting, split, and assignment logic. |
| D017 | `find_allocation` skips `excludes` entirely when policy is inactive. The test counter sits inside this production boundary. It is not inferred from test inputs. |
| D005 subset | Cutoff and activation share `OptOutTimestamp`. It rejects surrounding whitespace, then uses Chrono. Existing `startAt` and `endAt` parsing is unchanged. |
| C API | Default, legacy Boolean, and enum entrypoints reach the Rust evaluator. Default calls select disabled behavior. Handle ownership is unchanged. |
| Panic result | The local helper catches unwinds and returns an owned `General` error with a fixed message. Its regression inspects and frees that result. Alternative crate macros are private. |

The explicit `TryParse` match corrects the initial inference error in the wrapper conversion. The parser test name now states its whitespace exception.

## Corpus and test assessment

All 90 policy rows exactly match the pinned central corpus bytes. Their IDs are unique. They cover the complete three-mode, three-attribute, five-activation, two-logging-state product. Expected answers are unchanged.

The adapter uses the production evaluator. It checks allocation, variation, value, serial ID, and `do_log`. Independent examples cover malformed activation after a match, behind a rule, outside a time window, and on an ordinary allocation. They preserve start/end validation and distinguish missing/null activation from malformed activation.

The older missing-flag unit test covers only future mode without a targeting key. The new whitespace regression covers both enabled modes with a valid subject. It also checks disabled behavior, activation error scope, and a valid neighbor. All nine D016 lookup cases appear in the C adapter with valid subjects.

The C adapter contains 243 policy materializations and nine lookup cases. It makes 504 calls through enum, legacy, and default entrypoints. It checks values, errors, reasons, allocation/variation identities, metadata, and exposure eligibility. Nine null/array/object attribute shapes are explicitly excluded because the C attribute type cannot represent them. All 90 abstract policy rows remain exercised.

The C inputs match fixture manifest `0407fb0330aefbeb086f16784aba0e5629f9e0241e80cd1416308146cbc9679d`. I checked the generator and the saved C observations. No expectation was replaced with SDK output.

## Historical failure and correction

The first C run recorded 250 passed and two failed cases. Immediate and future accepted surrounding whitespace in the cutoff. The shared extension cases required `INVALID_CONTEXT`.

The original review scope retained native Chrono grammar. The coordinator then explicitly selected only D005's surrounding-whitespace rule for libdatadog. The shared wrapper and focused tests implement that choice. Record this narrow adoption separately from fleet approval or complete browser-grammar parity.

The original failed observations remain unchanged. The latest saved C observations contain the same 252 IDs, all passing, across 504 calls. The latest native log reports 108 tests passed and zero skipped. These are reviewed owner-run records, not an independent rerun. The coordinator owns final artifact and tested-commit bindings.

Two negative-control logs also fail as intended. Restoring the original production policy fails the 90-case adapter. Removing the inactive guard fails the production exclusion-counter test. The controls do not establish complete mutation coverage.

## Limits

- Lean does not prove native refinement, C ABI behavior, or panic containment.
- D017 checks logical skipped work. No wall-clock performance or regression-free timing claim is established.
- Panic containment requires an unwind-capable build. Returned error text is redacted. The test does not prove panic-hook output is redacted.
- C results prove assignment output and exposure eligibility. They do not prove telemetry transport, wrapper lifecycle, deployment, or downstream adoption.
- Other Chrono syntax and existing malformed `doLog` behavior remain scoped differences. Mobile acknowledgement rules do not apply.
- This review makes no hosted CI, merge approval, release, or production-readiness claim.

## Reviewed file hashes

| File | SHA-256 |
| --- | --- |
| `libdd-ffe/src/rules_based/eval/eval_assignment.rs` | `f1135369ee455399ab811202d516b106f613ed2beab180f99c189836623140ee` |
| `libdd-ffe/src/rules_based/timestamp.rs` | `7c1665f72723050db6819be068ef7f0e872b6392ca8c8f9a36889932b74b0ab7` |
| `libdd-ffe/src/rules_based/ufc/models.rs` | `0384b9964972a10f73b7c03e6c079c84e091e4ad70ae6f43228ba7cc46598719` |
| `libdd-ffe/src/rules_based/ufc/compiled_flag_config.rs` | `46d0da6dda9f6bdbe37443855845b2df0824930ff1a494f0fb5f0653815b33c9` |
| `libdd-ffe-ffi/src/assignment.rs` | `50316fbdfcd982691d166ef4f96fb5a3ec3d668c18bde0410a03f523f48b4458` |
| `libdd-ffe/README.md` | `f593fbb0531d1314fc97f681cc9d28846d28b980ca8967ae08414d04d733f694` |
| `libdd-ffe-test-suite/tests/experimentation_opt_out.rs` | `9ed2ee2744d7f149d844486b8f1f685a0f5a20a0d5b1123de35fde8c75838f76` |
| `libdd-ffe-test-suite/tests/data/experimentation-opt-out-policy.jsonl` | `0d396beb2b627606f795386340d5e9d7443a40c51e84200b60527938969f7175` |
| `libdd-ffe-test-suite/tests/data/README.md` | `49c1c9a4a07b2ca84baa432669d2e47723d6c770080d93783c19960951b18a26` |
| `libdd-ffe-test-suite/tests/canonical_fixtures.rs` | `819c02b91b1f8e9879e61ec79c5ef7d2bee92c49d3eac29ee2f4054b09f09949` |
| `examples/ffi/ffe.c` | `8510adcee34f444e2321e270b8163b860abaf5562010b39bc1375cb269ee68f1` |

Recorded at 2026-10-23T12:55:20.772562+00:00.

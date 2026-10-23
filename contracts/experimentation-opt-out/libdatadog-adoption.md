# libdatadog opt-out adoption

[PR #2698](https://github.com/DataDog/libdatadog/pull/2698) implements the recorded rules at
[ead1d3db](https://github.com/DataDog/libdatadog/commit/ead1d3db2aa16e494f23e47b946ff12a7a1be53a).

| Decision | Implementation scope |
| --- | --- |
| D002, D016 | Disabled ignores cutoff. Malformed enabled input fails before flag lookup. |
| D003, D004 r2 | Activation is prepared once. Invalid activation fails only effective future mode, including unreachable allocations. |
| D005 r2 | Cutoff and activation reject surrounding whitespace. Other syntax retains Chrono behavior; startAt/endAt are unchanged. |
| D011 | Immediate excludes now. Future retains strictly older activation. Ordinary allocation order and exposure eligibility remain intact. |
| D017 r2 | Inactive policy skips the real exclusion helper. Native counts do not establish a speedup. |

The [profile](evidence/libdatadog-adoption-20261023/profile.json) includes all 90 policy cases from the unchanged Lean corpus.
The [adoption record](evidence/libdatadog-adoption-20261023/local-adoption.json) preserves parser and malformed-doLog scope.
No English decision revision, Lean statement, or expected case result changed.

| Evidence | Result |
| --- | --- |
| [Native receipt](evidence/libdatadog-adoption-20261023/native-receipt.json) | 108 tests pass; 363 baseline, 28 immediate, 44 future canonical evaluations pass. |
| [C observations](evidence/libdatadog-adoption-20261023/c-observations-exact-head.jsonl) | 252 cases pass across 504 calls through enum, legacy boolean, and default entry points. |
| [C applicability](evidence/libdatadog-adoption-20261023/c_contract.json) | Nine null/array/object attribute cases cannot be represented by the C attribute enum. |
| [Original D004 control](evidence/libdatadog-adoption-20261023/baseline-counterexample.log) | Original code fails the unchanged policy case. |
| [Inactive-call control](evidence/libdatadog-adoption-20261023/inactive-negative-control.log) | Restoring unconditional exclusion calls fails the native counter assertion. |
| [Original whitespace counterexample](evidence/libdatadog-adoption-20261023/c-summary-candidate.log) | Candidate passed 250 cases and failed 2; the final parser corrects both failures. |
| [Independent review](evidence/libdatadog-adoption-20261023/independent-review.md) | No open source correctness finding at the implementation commit. |

The [feedback ledger](evidence/libdatadog-adoption-20261023/feedback-ledger.json) records one target-specific panic-helper comment.
The [verified reply](evidence/libdatadog-adoption-20261023/published-reply.json) explains why other crate-private macros do not apply and records the native regression.
The thread is resolved. It adds no shared semantic rule. The prior Codex review covered an older commit and reported no observations.

The C run uses the [system-tests corpus](https://github.com/DataDog/system-tests/tree/a45f53c4aef20eb130116556598e593785657159/tests/ffe/fixtures/experimentation-opt-out-lean).
It checks returned values, errors, reasons, variants, allocation metadata, and exposure eligibility.
It does not establish event delivery, downstream Ruby/PHP/Python behavior, or deployed backend support.
The central proposal remains draft. No merge, release, deployment, or fleet approval is recorded.

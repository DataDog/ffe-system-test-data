# Ruby opt-out adoption

[Ruby PR #6521](https://github.com/DataDog/dd-trace-rb/pull/6521) contains all three modes at `6c4e268d18e68523f0e5e6546a86d6754c350e3a`.
The temporary native dependency is [libdatadog #2698](https://github.com/DataDog/libdatadog/pull/2698) at `ead1d3db2aa16e494f23e47b946ff12a7a1be53a`.
Replace the native override with a released dependency before merging Ruby.

| Decision | Ruby behavior |
| --- | --- |
| D002 | Disabled ignores the cutoff. Enabled modes reject invalid bytes before native conversion. Attribute names containing NUL cannot alias the reserved key. |
| D004 r2 | Malformed activation fails effective future mode for the whole flag, including unreachable allocations. |
| D005 r2 | Native surrounding-whitespace rejection applies. Other Chrono syntax remains unchanged, including accepted internal Unicode whitespace. |
| D010 | The policy profile uses explicit boolean doLog. Omitted-field compatibility remains native-scoped. |
| D011 | Immediate excludes experiments now. Future preserves strictly older activation. Ordinary allocation order continues. |
| D009 | Evaluation telemetry suppression remains independent from experiment exclusion and exposure eligibility. |
| D016 | A ready evaluator rejects malformed enabled input before flag lookup. |

The [profile](evidence/ruby-adoption-20261023/profile.json) preserves all 90 policy cases.
The [adoption record](evidence/ruby-adoption-20261023/local-adoption.json) preserves parser and dependency limits.
No English decision revision, Lean definition, or expected result changed.

| Evidence | Result |
| --- | --- |
| [Native receipt](evidence/ruby-adoption-20261023/native-receipt.json) | Ruby 3.4.7: 1043 + 1039 OpenFeature examples and 44 C-binding examples pass. Ruby 3.1.7: 1039 + 1039 pass. Ruby 4.0.1: 1043 + 1039 pass. |
| [Encoding control](evidence/ruby-adoption-20261023/invalid-encoding-negative-control.log) | Original guard causes 6 failures among 21 examples. |
| [NUL-name control](evidence/ruby-adoption-20261023/nul-attribute-alias-negative-control.log) | Original C conversion causes 2 failures among 21 examples. |
| [Runtime review](evidence/ruby-adoption-20261023/runtime-review.json) | Public resolution details and event delivery checked against the frozen shared corpus. Exact counts and limits are recorded. |
| [Independent review](evidence/ruby-adoption-20261023/independent-review.md) | No open correctness finding at the signed Ruby and harness commits. |

The runtime harness is `DataDog/system-tests@d4c4308b3600a48885564f687c37800b4eeb5c19`.
The [feedback ledger](evidence/ruby-adoption-20261023/feedback-ledger.json) records the native-validation request and older no-findings Codex review.
The two Ruby drafts are consolidated into #6521. No merge to master, package release, deployment, or human approval is recorded.

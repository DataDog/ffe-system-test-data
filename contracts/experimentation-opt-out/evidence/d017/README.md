# D017: Go guard and native evidence

Implemented in [627db08](https://github.com/DataDog/dd-trace-go/commit/627db08193d8019d33282024d8340327997205ec), following
[Aaron's call-site request](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4342540461). The [decision](../../decision-history.md#d017)
and [English contract](../../inactive-path.md) define the scope. Other SDK owners
must assess applicability before adopting this proposed operational profile.

| Evidence | Result | Limit |
| --- | --- | --- |
| [Lean model](model-validation.json) | 46 audited theorems, 313 semantic cases, 36 trace cases | Abstract model; no native timing proof |
| [Native observation](go/operational-receipt.json) | 36/36 pass | Forced traversal through the real provider and evaluator |
| [Baseline negative control](go/operational-receipt.json) | 15 expected failures; values unchanged | Restores the pre-guard evaluator, retaining the same adapter |
| [Package and race](go/native-validation.json) | 278 top-level tests / 1,631 passing test entries each | Local Go 1.26.0, linux/amd64 |
| [Independent review](independent-review.json) | No remaining blockers | Benchmark shutdown issue fixed before measurement |
| [CI registration](native-receipt.json) | Both helper and whole-evaluation benchmarks registered; ciselect passes | New benchmarks need a baseline before CI can compare them |

## Native observations and reproduction

The [adapter](go/conformance_test.go.txt) calls production `BooleanEvaluation`.
A [source overlay](go/run_conformance.py) observes actual helper entry and actual
allocation-loop/evaluateAllocation entry. It does not calculate a call count
from the requested mode. Empty splits force all supplied allocations to be
visited, matching the model's deliberately bounded input domain. `doLog` and
equal activation/cutoff encode the requested helper results. Wider selection,
event, lifecycle and malformed-activation behavior remains native test coverage.

```sh
python3 evidence/d017/go/run_conformance.py /path/to/dd-trace-go \
  corpus/inactive-path.jsonl /tmp/d017-native-results
```

Run this from the contract directory, with the Go checkout at the linked
implementation and the pinned baseline available locally. It rejects a changed
corpus and checks the exact discovery and expected pass/fail counts. It writes
only its output directory. The observer uses serial test state; run only its
named conformance test, and never benchmark an instrumented binary.

[Candidate assembly](go/candidate-evaluateFlag.asm) from the uninstrumented binary
shows the zero-mode branch jumping over `excludes`; the
[baseline assembly](go/baseline-evaluateFlag.asm) calls it unconditionally. This is
compiler evidence for this binary, separate from the abstract proof and timing.
Trailing whitespace in the saved assembly output is normalized.

## Local timing

[Raw measurements and receipt](go/benchmarks.json) record 10 alternating AB/BA
rounds, CPU affinity, Go 1.26.0/linux/amd64, 150 ms per benchmark and 34 complete
evaluation cases. The candidate and baseline use identical benchmark sources;
only the production guard differs. Binary hashes and build commands are in the
[native receipt](go/native-validation.json). The comparator is the previous
child [c5fec6a](https://github.com/DataDog/dd-trace-go/commit/c5fec6a009ffa29bf53f5377a21856c7c4aa5f56),
not the parent PR baseline.

Inactive-profile median changes range from -1.61% to +1.38%; active/retained
profiles range from -0.30% to +2.99%; the ten existing benchmarks range from
-0.33% to +2.57%. Allocation counts are unchanged. These are
mixed exploratory measurements on a shared host, without a hypothesis test or
approved percentage threshold. They do not establish a performance improvement
or close the six earlier parent-relative CI regressions. The production call
skip is established by the native observation and compiled branch; timing must
be assessed separately, including the new CI run.

The `.txt.gz` files preserve all raw timing outputs; package/race logs are also
compressed. Their uncompressed hashes remain in the receipts. The final console
summary of the timing runner had a display-only Python error after all 20
commands and receipt writing completed; its expression is fixed in the saved
runner. Every benchmark command exited zero and all 34 cases have 10 samples
per side. No staging, production, fleet approval or new system-test claim is made.

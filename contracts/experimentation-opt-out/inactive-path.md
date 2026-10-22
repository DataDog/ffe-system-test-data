# D017 r2: inactive opt-out skips allocation-exclusion work

Leo accepted the [call-site guard request](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4342540461)
in the review chat. Acceptance is scoped to Go; this document is the proposed
contract for other rules-based SDKs. The current public decision-setting reply
still describes the earlier partial fix; r2 has not been posted there yet.

## English rule and scope

After existing provider, context and flag checks, an inactive effective opt-out
policy must skip the allocation-exclusion operation. Disabled mode and an absent
subject cutoff are inactive. Enabled mode with an invalid cutoff remains
`INVALID_CONTEXT`; it must not become an ordinary evaluation. Active modes keep
their existing allocation decisions, including D004's malformed-activation rule.

The change must preserve values, errors, allocation order and applicable events.
It permits policy resolution and a cheap guard. It does not prohibit allocation
metadata reads needed for ordinary targeting or telemetry, or activation parsing
when configuration arrives. Go implements the rule by short-circuiting before
`excludes`; another SDK may use an equivalent branch, dispatch or specialization.

## Executable operational contract

[InactivePath.lean](lean/InactivePath.lean) models two explicit operations:
`skip` and `check`. An interpreter records the exclusion results and increments a
counter only when a `check` is executed. Both the guarded and unconditional
programs run through that same interpreter. The resulting theorems establish:

- The guard preserves exclusion decisions for any list of already visited allocations.
- An inactive policy executes zero exclusion checks for any list length.
- An active policy executes one check for each visited allocation.
- Invalid enabled context stays an error and does not enter allocation traversal.
- The old unconditional shape can return identical results while executing extra checks.

The model receives the helper's result for each visited allocation. It does not
model targeting, short-circuit traversal, the helper's full semantics, or every
SDK observable. The existing semantic corpus and native regression tests cover
those boundaries. Operation counts are logical events, not CPU instructions,
allocations, nanoseconds or a compiler guarantee.

[InactiveOracle.lean](lean/InactiveOracle.lean) runs this same definition as a
JSON-lines oracle. [The 36 trace cases](corpus/inactive-path.jsonl) are separate
from the unchanged 313 semantic cases and are pinned as `inactive-path-v1` in the
manifest. For example:

```json
{"args":{"mode":"disabled","attribute":"valid","checkResults":[true,false,true]},"expected":{"error":"NONE","excluded":[false,false,false],"exclusionChecks":0}}
```

This example's value-only expectation also accepts the old implementation. The
additional `exclusionChecks` observation distinguishes it. Expectations were
specified independently and compared with the executable Lean definition; no
SDK output supplies the expected result.

[Local validation](evidence/d017/model-validation.json) records 46 audited
theorems, 313 semantic cases and 36 trace cases passing. The
[negative control](evidence/d017/negative-control.json) restores unconditional
calls and is rejected by the zero-check proofs. These results establish the model
and oracle. The [Go implementation and native evidence](evidence/d017/README.md)
now establish the skipped call at the production boundary and compiled branch;
local timing results are mixed and carry no regression-free claim.

## Native fan-out obligations

Send each implementation owner the decision revision, independently pinned
manifest/profile, semantic cases, trace cases and its target source SHA. The
adapter must exercise the production path and observe the actual exclusion
boundary; it must not fabricate a zero count from the input mode or reimplement
the guard. A test-only hook or instrumented source overlay can expose the event.
Where instrumentation cannot preserve the relevant compiler behavior, return
that gap with compiler/assembly evidence for review rather than claiming a pass.

Use an uninstrumented binary for performance measurement. Pin the compiler,
architecture, baseline and candidate commits. Measure complete evaluations for
disabled mode, each enabled mode without a cutoff, and active opt-out. Include
allocation/context-size variation and the repository's performance CI entrypoints.
Record observed differences and uncertainty separately from the CI gate status;
no universal percentage threshold has been approved.

The [current Go benchmark report](https://github.com/DataDog/dd-trace-go/pull/5700#issuecomment-6319082919)
at [c5fec6a](https://github.com/DataDog/dd-trace-go/commit/c5fec6a009ffa29bf53f5377a21856c7c4aa5f56)
reported six regressions despite a passing performance gate. Preserve that
pre-fix evidence; it is not a measurement of the accepted guard.

Fan out to owners of shared evaluators first. A wrapper or a precomputed-only
client can report that the allocation-loop profile is not applicable, with the
owning dependency identified. Keep that status distinct from passing native
conformance. Return counterexamples centrally; the coordinator reconciles the
rule, increments its revision when necessary, and starts the next round.

Lean is already a runnable programming-language oracle as well as a proof
language; a second canonical implementation is unnecessary for this prototype.
A Go/TypeScript oracle could expose the same result-and-trace protocol, but would
need conformance checks against the selected canonical model. See Lean's
[evaluation documentation](https://docs.lean-lang.org/functional_programming_in_lean/Getting-to-Know-Lean/Evaluating-Expressions/)
and [proof-kernel description](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/).

# Edge review decisions

This update extends the [central draft proposal](https://github.com/DataDog/ffe-system-test-data/pull/55)
for [dd-source #140422](https://github.com/ddoghq/dd-source/pull/140422), reviewed at
[7a1f3c5263](https://github.com/ddoghq/dd-source/commit/7a1f3c52639d6bdd74dd4609fba716c50127e2e2). Leo selected the behavior in the
[current local decision record](evidence/edge-review-20261022/local-decisions.json).
The implementation is published at [939db39e16](https://github.com/ddoghq/dd-source/commit/939db39e166fdd40cf7744399477bfe9053964b0);
[publication evidence](evidence/edge-review-20261022/native-publication.json) binds it
to the tested patch. The [formatted replies](evidence/edge-review-20261022/formatted-replies.json)
were read back with their rendered sections verified, and retain the decision URLs below.
The [original reply readback](evidence/edge-review-20261022/published-replies.json) remains as history.
This presentation update changes no decision, source code, proof or native test expectation.
This is not fleet approval or merge/deployment evidence.

## D019: invalid regex rejects its flag

[Author decision](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4354082717).

Retain the modern rules-based SDK contract represented by the canonical fixture:
an invalid regex produces a flag-local `PARSE_ERROR`, while valid sibling flags
remain usable. Precompute omits the invalid flag. Do not fall through from the
invalid regex to a later allocation. This applies even with opt-out disabled.

The [review evidence](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4343814088)
reports this flag-isolation behavior in the tracer SDKs and identifies differences
in parsing grammar and validation timing. Accepting flag-local failure does not
claim all engines accept the same regex syntax. Save-time validation, an audit of
existing production patterns, and grammar convergence remain separate operational
work. The decision is deliberately not represented as a new Lean theorem.

## D020: tolerate unsupported request options

[Author decision](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4354083691).

At the edge request boundary, unknown names are ignored; null options, a null or
unknown named mode, and a null legacy boolean mean no option. Known options remain
active when mixed with unknown ones. In particular, legacy `true` still requests
immediate exclusion when the named mode is null or unknown.

Wrong value types, duplicate options, conflicting recognized enabled modes, and
invalid timestamps for recognized enabled modes still fail before origin access.
Ordinary requests return ordinary assignments and no opt-out acknowledgement.
Clients requesting an enabled policy must continue checking its acknowledgement;
server tolerance does not make an unsupported policy take effect.

This is an HTTP compatibility rule, not a change to provider constructor or
environment-variable mode validation. The [review request](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4343814538)
provides the distinguishing examples. Native tests cover the real request path;
this rule is not yet modeled in Lean.

## Reaffirmed decisions

- [D018](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4354082423): evaluators use `doLog`; the compiler must mark randomized allocations.
  No new wire bit or evaluator-local split analysis is introduced. Existing
  `doLog=false` fixture inputs test consumer behavior, not producer correctness.
- [D008](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4354083320): immediate keeps its legacy boolean acknowledgement. Future mode returns
  the named mode and UTC cutoff. Fraction formatting may change to 0, 3, 6, or 9
  digits; clients compare instants at nanosecond precision. Literal tests cover
  JSON/archive and buffered/streaming responses without reusing the serializer
  under test to compute expected values.
- [D011](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4354083029): a future cutoff retains allocations activated strictly before that
  supplied instant, including an activation after the request time.
- [D012](https://github.com/ddoghq/dd-source/pull/140422#discussion_r4354084692): this edge PR can remain standalone. Compiler classification and fallback
  retention plus stored-UFC rebuilds are prerequisites for enabling opt-out.
  Activation coverage/backfill is an additional future-mode prerequisite. An old
  UFC can have a pruned fallback or a randomized `doLog=false` allocation; neither
  is corrected just by deploying an evaluator. Omitted/disabled requests do not
  activate exclusion. Checked-in deployment schedules do not establish current
  deployed state or authorize merging.

## Validation and propagation

The native fixture pin is merged #52 at
[0781ce2c55](https://github.com/DataDog/ffe-system-test-data/commit/0781ce2c55f9da7f9290035c768bbc46570556c0): 363 baseline rows, 28 immediate rows,
and 44 future-mode rows. Go now checks specified `serialId` and `doLog` metadata,
including serial ID zero versus explicit null/omission. Baseline and capability
results share the metadata assertions.

The linked [validation history](decision-history.md) retains exact source and
patch hashes, native results, negative controls, and limits. New D019/D020 rules
have native evidence only; the existing Lean model/corpus and earlier receipts
are unchanged. [Propagation](propagation.json) assigns edge, producer, and client
obligations separately. Shared approval remains pending. The [feedback ledger](evidence/edge-review-20261022/feedback-ledger.json)
separates implemented fixes, accepted semantics and remaining follow-ups.

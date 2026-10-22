# Backend opt-out review: compiler-owned randomization

Work starts with [dd-source #139368](https://github.com/ddoghq/dd-source/pull/139368)
at [3e99ba2a](https://github.com/ddoghq/dd-source/commit/3e99ba2aee24479054e1018c7ac80bd06adb7478).
The implementation is published at [d0a2de5b58](https://github.com/ddoghq/dd-source/commit/d0a2de5b58dba158941d2c2f81016276a45ea2c1).
The shared contract remains a [draft proposal](https://github.com/DataDog/ffe-system-test-data/pull/55);
merge approval, deployment, and configuration rebuilds remain separate.

## D018: randomization is represented by doLog

Leo [reaffirmed the decision in the review thread](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4353896956): allocations that randomize must be excluded, and
`doLog` is the evaluator-facing signal that the backend must populate correctly.
The earlier “Keep” selection was withdrawn before implementation. The exact
statement and correction are retained in [local-decision.json](evidence/backend-review-20261022/local-decision.json).
The [posted reply readback](evidence/backend-review-20261022/published-replies.json)
now supplies the public decision-setting source. The earlier local setting is
retained in provenance; historical test receipts retain their original pins.

| Allocation | Producer output | Immediate mode with valid cutoff |
| --- | --- | --- |
| Completed standard experiment, still 50/50 | `doLog=true` | Skip |
| Ordinary percentage split | `doLog=true` | Skip |
| Single variant with partial percentage enrollment | `doLog=true` | Skip |
| Deterministic completed winner | `doLog=false` | Eligible |
| Active experiment, canary, bandit, generated holdout | Preserve existing exposure requirement | Skip when `doLog=true` |

This deliberately enables exposure events for ordinary randomized allocations.
It does not introduce a separate wire marker or evaluator-local inference.
Future-only mode retains its existing strictly-before cutoff rule. Newly logging
allocations without activation metadata are conservatively excluded in that mode;
activation coverage remains a producer rollout obligation. Aaron's separate
proposal to omit holdout activation in #139381 is not decided here.

The native classifier compares ordered first-match outcomes across the existing
shard partition dimensions. Both changing variation and changing between match
and fallthrough count as randomization. Rules and time windows do not themselves
make an allocation random. Empty ranges, contradictory shard intersections,
shadowed variants, and multiple same-variant splits covering all buckets do not
create false randomization.

[BackendReview.lean](lean/BackendReview.lean) models the composition
`compiledDoLog = existingExposure OR randomized` and the existing evaluator
policy. Its theorems do **not** prove that the native partition classifier is
correct. Native compiler tests and independent raw-bucket enumeration cover that
boundary. The original oracle inputs with explicit `doLog=false` remain valid as
consumer tests; they are not examples of correctly compiled randomized allocations.

## Feedback disposition for the bottom PR

| Feedback | Disposition and scope |
| --- | --- |
| [P1: completed allocation still randomizes](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4343813763) | Intent accepted by Leo; implement producer classification through existing `doLog`, preserving active-experiment and holdout exposure requirements. |
| [P2: synthetic holdout runner](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4343814230) | Accept either logging value for a concluded ordinary winner, retain correct-winner checks, and continue requiring logging for active ordinary experiments. |
| [P3: array binding](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4343814608) | Use `id = ANY(?::uuid[])` and `pq.Array` in the organization-scoped snapshot query. |

See the [machine-readable ledger](evidence/backend-review-20261022/feedback-ledger.json),
[full four-PR review snapshot](evidence/backend-review-20261022/stack-snapshot.json),
and [source pins](evidence/backend-review-20261022/source-pins.json).
All three fixes have [published replies](evidence/backend-review-20261022/review-replies.md).
Threads remain open for reviewer confirmation; publication does not imply approval.

## Propagation and release obligations

The exact parent of #139379 is #139368's inspected head. Carry the winner fix into
that child before validating retained fallbacks. The activation and edge PRs are
independent branches with deployment dependencies, not one linear Git stack.
The pre-publication snapshot had three unresolved threads and REVIEW_REQUIRED.
Both implementation PR commits are now GitHub-verified/valid. Fresh CI and review
state remain separate from the local native validation.

Deploy the compiler changes and rebuild stored UFCs before enabling opt-out in
consumers. A previously published randomized allocation with `doLog=false` remains
misclassified until its configuration is regenerated. Preserve the remaining
activation, fallback, validator, and edge rollout gates from D012.

## Local validation

- Compiler suite: 817 tests passed; repository/database suite: 269 passed.
- Holdout runner and primary-analysis suites: 255 passed.
- Classifier compared with independent raw-bucket enumeration for 500 generated cases.
- Restoring the old `doLog` output fails three new scenarios: concluded 50/50,
  ordinary 50/50, and partial enrollment. The final patch was restored and both
  repository suites rerun without cached test results.
- Lean: 53 theorem axiom audits, 313 existing semantic oracle cases, and 36 existing
  operational oracle cases passed. Seven new theorems cover D018 composition;
  native classification is outside the proof.

[Native receipt and patch hashes](evidence/backend-review-20261022/native-validation.json)
and [model receipt](evidence/backend-review-20261022/model-validation.json) retain
scope limits. Initial build attempts could not fetch a private dependency over
SSH; a temporary HTTPS credential configuration resolved this. The first
negative-control attempt stopped at unused-code lint, so only the later control
that reached assertions counts as behavioral evidence.

The [pre-publication remote snapshot](evidence/backend-review-20261022/final-review-snapshot.json)
is retained as historical review evidence. The [publication receipt](evidence/backend-review-20261022/native-publication.json)
binds the signed implementation to the exact tested patch. The broader stack remains
pending; these records do not claim its other feedback is addressed.

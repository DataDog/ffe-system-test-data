# Published review replies

Posted with authorization and read back from GitHub, then refreshed after main integration. Original readbacks remain in published-replies.json. Threads remain open for reviewer confirmation.

## P1: [Reply](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4353896956)

Fixed in [d0a2de5b58](https://github.com/ddoghq/dd-source/commit/d0a2de5b58dba158941d2c2f81016276a45ea2c1). The policy is to exclude allocations that randomize; the backend must represent that through the existing `doLog` field. The compiler now sets `doLog=true` when shard selection changes the variation or match/fallthrough outcome, covering completed 50/50 experiments, ordinary percentage splits, and partial enrollment. Deterministic completed winners remain `false`; existing active-experiment, canary, bandit, and holdout logging requirements are preserved. This deliberately enables exposure logging for ordinary randomized allocations. The evaluator predicate and future-mode cutoff rule stay unchanged.

Recorded as [D018](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/backend-feedback.md#d018-randomization-is-represented-by-dolog) in [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55), published at [656696f84f](https://github.com/DataDog/ffe-system-test-data/commit/656696f84fb83fea87798a0d4151af0f7e2fc16d), with this [decision thread](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4343813763) and the earlier withdrawn selection retained in provenance.

[Native evidence](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/evidence/backend-review-20261022/native-validation.json): 817 compiler tests and 269 database repository tests pass, including 500 independent raw-bucket enumeration cases. Restoring the old `doLog` output fails the three added scenarios above; restoring the fix passes both suites uncached. [Lean evidence](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/evidence/backend-review-20261022/model-validation.json): seven new composition theorems, 53 total audited; 313 existing semantic cases and 36 operational cases pass. The Lean abstraction does not prove the native classifier; the native tests cover that boundary.

Deployment still requires the fallback-preserving child and regenerated UFCs. Newly logging allocations without activation metadata retain the existing conservative future-mode exclusion; activation coverage remains a separate rollout obligation.

Post-merge validation at [0ae33d8f11](https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b): 918 compiler tests, 283 database repository tests, and 275 runner/primary-analysis tests pass. Both repository helpers are preserved from their respective parents. Main added a bucketing golden snapshot: its seven randomized `doLog` expectations were updated, with every assignment field unchanged. The earlier negative-control and Lean receipts retain their original source pins; D018 is unchanged.

## P2: [Reply](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4353897263)

Fixed in [d0a2de5b58](https://github.com/ddoghq/dd-source/commit/d0a2de5b58dba158941d2c2f81016276a45ea2c1). The holdout runner now accepts either `doLog` value for a concluded ordinary winner, still checks the selected winner, and continues requiring logging for active ordinary experiments. Regression cases cover both logging values and reject the wrong winner.

The holdout-runner and primary-analysis suites pass all 255 tests. [Native receipt](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/evidence/backend-review-20261022/native-validation.json), retained in [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55) alongside the [D018](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/backend-feedback.md#d018-randomization-is-represented-by-dolog) producer contract. This is local runner validation; it does not claim a deployed lifecycle run.

After integrating main in [0ae33d8f11](https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b), the expanded runner/primary-analysis suites pass all 275 tests. The concluded-winner and active-experiment logging checks remain intact.

## P3: [Reply](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4353897591)

Fixed in [d0a2de5b58](https://github.com/ddoghq/dd-source/commit/d0a2de5b58dba158941d2c2f81016276a45ea2c1): the organization-scoped bulk snapshot query uses `id = ANY(?::uuid[])` with `pq.Array(experimentIDs)`, matching the existing holdout-query pattern.

All 269 database repository tests pass with the change. [Native receipt](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/evidence/backend-review-20261022/native-validation.json) is published in [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55); this query-binding fix is native evidence, outside the Lean model proof.

After integrating main in [0ae33d8f11](https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b), all 283 database repository tests pass. The rollout-state loader and main's bandit-ordering helper are both preserved.

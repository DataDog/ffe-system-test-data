# Published review replies

Posted with authorization and read back from GitHub. P1 now follows the user-selected Go decision-reply format; prior readbacks remain in published-replies.json and main-merge-replies.json. The formatting update changes no decision or test evidence. Threads remain open for reviewer confirmation.

## P1: [Reply](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4353896956)

🤖 **Comment from Codex working with Leo:**

**Decision [D018, revision 1](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/decision-history.md#d018): the backend must represent randomization through the existing `doLog` field.**

Thanks, Aaron — agreed that a completed experiment can still randomize. We’re keeping allocations that randomize subject to opt-out, including ordinary percentage splits and partial enrollment. The backend owns that classification; evaluators retain the existing `doLog` predicate and future-mode cutoff rule. This records Leo’s clarification in [this decision thread](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4343813763); the earlier withdrawn selection remains in [provenance](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/evidence/backend-review-20261022/local-decision.json).

**Implemented in [d0a2de5b58](https://github.com/ddoghq/dd-source/commit/d0a2de5b58dba158941d2c2f81016276a45ea2c1); validated after merging main at [0ae33d8f11](https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b).** The compiler sets `doLog=true` when shard selection changes the variation or match/fallthrough outcome. Deterministic completed winners remain `false`, while existing active-experiment, canary, bandit, and holdout logging requirements are preserved.

**Shared proofs:** [draft FFE test-data PR #55](https://github.com/DataDog/ffe-system-test-data/pull/55) contains the [D018 decision](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/decision-history.md#d018), its Lean proofs, and the linked validation history.

<details>
<summary><b>Behavior</b> — the distinction we are preserving</summary>

| Allocation | Compiler output | Immediate mode with a valid subject cutoff |
| --- | --- | --- |
| Completed experiment still splitting 50/50 | `doLog=true` | Skip the allocation. |
| Ordinary percentage split | `doLog=true` | Skip the allocation. |
| Single variant with partial percentage enrollment | `doLog=true` | Skip the allocation. |
| Deterministic completed ordinary winner | `doLog=false` | Remains eligible for delivery. |
| Existing active-experiment, canary, bandit, or generated-holdout logging | Preserve the existing logging requirement. | Skip when `doLog=true`. |

This deliberately enables exposure logging for ordinary randomized allocations. Targeting rules and time windows do not themselves make an allocation random; changing between match and fallthrough does. First-match order, unreachable variants, empty ranges, and same-variant coverage are handled by the native classifier.

Future mode keeps its strictly-before cutoff rule: earlier activation remains eligible, while unknown activation is conservatively excluded. Deployment still requires the fallback-preserving child, regenerated UFCs, and activation coverage for newly logging allocations.

</details>

<details>
<summary><b>Native validation</b> — local checks at <a href="https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b">0ae33d8f11</a></summary>

- **918 compiler tests, 283 database repository tests, and 275 runner/primary-analysis tests pass.** The [merged-source receipt](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/evidence/backend-review-20261022/main-merge-native-validation.json) records the commands, source hashes, and exact execution scope. The repository run preceded only the compiler-test snapshot/comment correction; its library source was unchanged.
- The classifier matches **500 independent raw-bucket enumeration cases**, alongside targeted cases for partial enrollment, first-match ordering, unreachable variants, and same-variant coverage.
- Before main integration, restoring the old `doLog` output failed the completed 50/50, ordinary 50/50, and partial-enrollment regressions. The [negative-control receipt](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/evidence/backend-review-20261022/native-validation.json) retains its original source and patch pins; restoring the fix passed both Go suites uncached.
- Main introduced a golden snapshot with seven old `doLog=false` expectations. That initial failure is preserved in [V052](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/decision-history.md#v052). Updating only those seven logging bits leaves **every assignment field unchanged**; the subsequent compiler run passes, recorded in [V053](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/decision-history.md#v053).

These are local native checks. The model proof does not establish correctness of the Go partition classifier. Child-stack integration, CI, and deployed behavior remain separate evidence.

</details>

<details>
<summary><b>Sneak preview</b> — turning review decisions into reusable, checked contracts</summary>

The shared decisions and proofs are published in **[draft FFE test-data PR #55](https://github.com/DataDog/ffe-system-test-data/pull/55)** at [99854cf878](https://github.com/DataDog/ffe-system-test-data/commit/99854cf87802e03d2cc2c5ed324dfabcaafc5f34):

1. **[A versioned English decision — D018, revision 1](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/decision-history.md#d018)**, linked to where it was set.
2. **[An executable Lean model and checked proofs](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/lean/BackendReview.lean#L6-L41)** of the producer/evaluator composition.
3. **[The existing semantic corpus](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/corpus/browser-proposal.jsonl)** and **[operational corpus](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/corpus/inactive-path.jsonl)**, preserving the broader opt-out contract. These are not new D018 producer-classification cases; the classifier has separate native enumeration and regression tests.
4. **[A linked history of evidence](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/decision-history.md#historical-linked-checks)**, preserving passing and failing checks separately from the decision’s authority.

For example, [this theorem](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/lean/BackendReview.lean#L26-L28) is checked in the published model:

```lean
theorem immediate_excludes_randomized_allocations (existingExposure : Bool) :
    (compiledPolicy .immediate .valid .missing existingExposure true).exclude = true := by
  cases existingExposure <;> rfl
```

In plain English: within this model, an allocation classified as randomized is excluded in immediate mode with a valid subject cutoff, even without an existing exposure-logging requirement. The modeled compiler combines the two requirements as `existingExposure || randomized`; it does not infer randomization from native shard data.

The [model validation](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/evidence/backend-review-20261022/model-validation.json) passes **53 theorem audits**, including seven new D018 theorems, plus **313 existing semantic cases and 36 operational cases**. A separate theorem distinguishes the old non-logging split from the corrected producer contract.

The useful result is a reviewable rule with a source-pinned evidence trail. The Lean proof establishes properties of the model; the [native receipt](https://github.com/DataDog/ffe-system-test-data/blob/99854cf87802e03d2cc2c5ed324dfabcaafc5f34/contracts/experimentation-opt-out/evidence/backend-review-20261022/main-merge-native-validation.json) establishes the bounded compiler checks above. The central PR remains a draft, and fleet adoption remains a separate decision.

</details>


## P2: [Reply](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4353897263)

Fixed in [d0a2de5b58](https://github.com/ddoghq/dd-source/commit/d0a2de5b58dba158941d2c2f81016276a45ea2c1). The holdout runner now accepts either `doLog` value for a concluded ordinary winner, still checks the selected winner, and continues requiring logging for active ordinary experiments. Regression cases cover both logging values and reject the wrong winner.

The holdout-runner and primary-analysis suites pass all 255 tests. [Native receipt](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/evidence/backend-review-20261022/native-validation.json), retained in [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55) alongside the [D018](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/backend-feedback.md#d018-randomization-is-represented-by-dolog) producer contract. This is local runner validation; it does not claim a deployed lifecycle run.

After integrating main in [0ae33d8f11](https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b), the expanded runner/primary-analysis suites pass all 275 tests. The concluded-winner and active-experiment logging checks remain intact.

## P3: [Reply](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4353897591)

Fixed in [d0a2de5b58](https://github.com/ddoghq/dd-source/commit/d0a2de5b58dba158941d2c2f81016276a45ea2c1): the organization-scoped bulk snapshot query uses `id = ANY(?::uuid[])` with `pq.Array(experimentIDs)`, matching the existing holdout-query pattern.

All 269 database repository tests pass with the change. [Native receipt](https://github.com/DataDog/ffe-system-test-data/blob/656696f84fb83fea87798a0d4151af0f7e2fc16d/contracts/experimentation-opt-out/evidence/backend-review-20261022/native-validation.json) is published in [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55); this query-binding fix is native evidence, outside the Lean model proof.

After integrating main in [0ae33d8f11](https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b), all 283 database repository tests pass. The rollout-state loader and main's bandit-ordering helper are both preserved.

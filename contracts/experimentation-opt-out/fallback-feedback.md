# Fallback review: authored SemVer delivery

The native feedback fix for [dd-source #139379](https://github.com/ddoghq/dd-source/pull/139379)
is published in [50775244](https://github.com/ddoghq/dd-source/commit/50775244ad95c65017b7890a81fde9806e330b80), integrating the winner-classification parent
[0ae33d8f](https://github.com/ddoghq/dd-source/commit/0ae33d8f112685502bb8f16d8c96efbecb70219b)
without rewriting history. The [publication receipt](evidence/fallback-review-20261022/publication.json)
binds the tested files to that revision and records valid GitHub signatures for
both PR commits. Shared contract approval and rollout remain separate.

## D021: authored SemVer controls compatibility delivery

[Aaron's policy clarification](https://github.com/ddoghq/dd-source/pull/139379#discussion_r4343813531)
explicitly supersedes the bot's proposed preservation of older-SDK assignments.
The compiler already records SemVer targeting before optimization. Compatibility
filtering must consult that information even when an earlier deterministic
full-population allocation makes the SemVer rule unreachable. An override
replaces the authored waterfall and preserves its existing exception.

| Input | Capable payload, rollout enabled | Compatibility payload |
| --- | --- | --- |
| Ordinary full-population allocation, then SemVer | Include; SemVer rule pruned | Omit flag |
| Completed deterministic winner, then SemVer | Include; SemVer rule pruned | Omit flag |
| Active experiment, then SemVer | Include; fallback retained | Omit flag |
| Override with authored SemVer | Include override | Include override |
| No authored SemVer | Include | Include |

With the server SemVer rollout disabled, non-overridden authored SemVer flags
are omitted by the compiler. Filtering still scans remaining rules for decoded
configurations, which have no private build metadata. No wire field or tracer
version threshold changes. Unrelated flags remain available.

This is a reviewer-requested compiler/delivery policy implemented and published under
Leo's feedback and push requests. It is not a new fleet-approved SDK contract.
The exact authority, superseded alternative and scope are in
[decisions.json](decisions.json) and the [linked history](decision-history.md#d021).
D018's producer-owned randomization classification remains unchanged.

## Checked model and native boundary

[SemverDelivery.lean](lean/SemverDelivery.lean) states the delivery rule and six
theorems. For example:

```lean
theorem authored_semver_is_not_compatible (rollout : Bool) :
    compatibilityContains true false rollout = false := by
  cases rollout <;> rfl
```

For a flag with authored SemVer and no override, the abstract compatibility
payload omits the flag regardless of the rollout switch. The bounded
[24-case corpus](corpus/semver-delivery.json) covers three first allocations,
authored SemVer presence, override presence, and rollout on/off. Native tests
consume the same bytes through `BuildFlagsConfiguration` and `FilterSemverFlags`,
then check JSON/protobuf membership, source non-mutation, unrelated flags,
surviving conditions and eligible-subject assignments.

The model does not prove native optimization, full tracer routing, malformed
configuration handling, or deployment. Existing native tests separately cover
all SemVer operators, decoded-rule scanning, nil flags and map independence.
The local manifest pin establishes consistency; it is not independent fleet
acceptance. No existing oracle expectations were changed.

## Feedback and evidence

The [full stack snapshot](evidence/fallback-review-20261022/stack-snapshot.json),
[source pins](evidence/fallback-review-20261022/source-pins.json), and
[feedback ledger](evidence/fallback-review-20261022/feedback-ledger.json)
retain the original bot suggestion, Aaron's reversal, and the P3 stale-comment
request. The stale reference now names `eliminateDeadBranches`.

The [native receipt](evidence/fallback-review-20261022/native-validation.json)
records 947 compiler, 108 Remote Config and 85 cache-worker passing test entries.
The [before-fix control](evidence/fallback-review-20261022/native-negative-control.json)
fails exactly the ordinary and completed-winner pruning cases (plus the aggregate
parent test). The initial full compiler run also found three inherited test
expectations that discarded fallbacks. Their corrections retain all previous
bandit policy checks and existing allocation data; the
[golden diff](evidence/fallback-review-20261022/golden-diff.json) adds only two
ordinary default allocations. An intermediate test assertion failed to compile
because it used the internal field name on the JSON type; it was corrected and
the final full compiler suite passed.

The [model receipt](evidence/fallback-review-20261022/model-validation.json)
records 59 audited theorems, all 24 SemVer cases, 313 existing semantic cases,
36 operational cases and a separate 12-test verifier-control run. Native tests
use the exact same SemVer corpus bytes as the central model. These are local
results bound to the published native revision; they do not establish CI or deployment success.

Review replies remain unposted drafts. The original PR's approval and green
checks apply to its old head; fresh CI and reviewer acceptance remain separate
from the local validation and verified publication.
The parent's [new rollout-control concern](https://github.com/ddoghq/dd-source/pull/139368#discussion_r4354101407)
remains open and does not supersede D018's accepted randomization rule.

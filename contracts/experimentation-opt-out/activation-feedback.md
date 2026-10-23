# Activation feedback: preserve the RFC's customer choice

This proposal reconciles [dd-source #139381](https://github.com/ddoghq/dd-source/pull/139381)
with the governing RFC. The original review head was
[0e38ea7ac4](https://github.com/ddoghq/dd-source/commit/0e38ea7ac4c7a568fda98e3cf90cca900032fdc9).
The sync fix and latest-main integration were validated at
[4e7164752a](https://github.com/ddoghq/dd-source/commit/4e7164752a0c66f6b501fc6fcc1fd6a9182bd3a2).
D011/D012 retain their evaluator decision revisions; this does not grant fleet approval.
Public evidence contains decision, proof and native-result summaries. Full internal
source snapshots and raw logs remain private.

## Governing RFC decision

The [RFC](https://docs.google.com/document/d/153tRlj46l-XfBGCA2X_NvxW4vwYObaH8zm2moP_AqMk/edit)
explicitly distinguishes immediate withdrawal from future-only exclusion:

| Generated holdout | Immediate mode | Future-only mode |
| --- | --- | --- |
| Run activated before the subject cutoff | Skip; no holdout exposure | Continue normal evaluation and exposures for returned assignments |
| Run activated at or after the cutoff | Skip | Skip |
| Unknown activation | Skip | Skip conservatively |

The RFC's “Opt-out after enrollment without new telemetry” example names an
existing holdout activated before the cutoff. Its implementation table requires
generated holdout allocations to carry the holdout run's activation time.
Leo's [October 19 comment](https://docs.google.com/document/d/153tRlj46l-XfBGCA2X_NvxW4vwYObaH8zm2moP_AqMk/edit?disco=AAACJEiBKfM)
records the revised customer choice after Eric's feedback. The earlier October 16
reply describing immediate withdrawal is retained in the
[RFC provenance summary](evidence/activation-review-20261022/rfc-snapshot.json).
It must not erase the later mode distinction.

[Aaron's request to remove holdout activation](https://github.com/ddoghq/dd-source/pull/139381#discussion_r4343815683)
would change future-only mode: a previously eligible older holdout would become
unknown and therefore excluded. His example of an older holdout covering a newer
experiment is a real consequence of the chosen run-level continuity policy.
Future-only mode does not promise immediate withdrawal from all experimentation
or require prior enrollment. We retain the RFC rule and prepare a reply explaining
that tradeoff. The proposed alternate policy remains recorded as a conflict,
not silently accepted or treated as a defect in the existing cutoff comparator.

## Allocation-sync first activation

[The sync-start finding](https://github.com/ddoghq/dd-source/pull/139381#discussion_r4343813972)
fits the existing RFC: a newly started published standard experiment needs its
first activation recorded in the same transaction as the schedule start.
Both creation/replacement and update of an exposure schedule must use that rule.
An existing timestamp survives subsequent starts. Replication retains the sender's
state, drafts do not activate, ordinary rollouts keep their existing behavior,
and edits to already-running legacy schedules must not invent historical activation.

[ActivationReview.lean](lean/ActivationReview.lean) models the first-write and
guard rules and composes unchanged D011 policy with holdout metadata. Its
`dropping_holdout_activation_changes_future_policy` theorem preserves the
minimal counterexample to the proposed holdout change. The separate
`activation-producer-v1` oracle has 144 abstract sync cases and 12 holdout cases.
These are model checks. Database transactions, classification of real allocations,
UTC serialization, and the producer's derivation of holdout activation require
native evidence; this oracle is not a native refinement proof.

## Review and rollout boundaries

The [native receipt](evidence/activation-review-20261022/native-validation.json)
records five passing suites: service, experiment lifecycle, UFC compiler,
cross-DC and allocation HTTP. All 26 new sync regression leaf cases pass.
Service and lifecycle required longer limits after the retained default-limit
timeouts. The original-source negative control fails for both update and
replacement first starts; its 16 preservation/control cases pass. The exact
local patch, source hashes and all failed attempts are retained in the
[evidence bundle](evidence/activation-review-20261022/README.md).

The [complete feedback ledger](evidence/activation-review-20261022/feedback-ledger.json)
includes resolved and unresolved conversations, earlier fixes, and deployment
conditions. The old validator PR is merged and the current activation PR targets
main; its original stack description is historical. Migration and validator
deployment remain independent obligations. Reported migration log lines and
first-seen validator versions do not prove every target has the required schema
and validator, including staging and government sites.

The central contract remains a draft proposal. Local native results, CI,
human approval, deployment, and future-only SDK enablement are separate gates.

The [main-merge receipt](evidence/activation-review-20261022/main-merge-native-validation.json)
records seven passing native suites at the merged revision, including 26 sync
regression leaf cases. The merged shared model checks 71 theorems and 529 cases;
14 verifier controls pass. Model, native and deployment claims remain separate.

Published replies: [sync activation fix](https://github.com/ddoghq/dd-source/pull/139381#discussion_r4354604887) and
[RFC-backed holdout decision](https://github.com/ddoghq/dd-source/pull/139381#discussion_r4354605103).
The [publication receipt](evidence/activation-review-20261022/publication.json)
records verified source/proof revisions and readback.

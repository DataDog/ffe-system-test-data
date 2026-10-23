# Historical local reply drafts

These preserve the initial draft before authorized publication. Posted replies and
verified commit links are recorded separately after readback.

## Sync start: discussion_r4343813972

🤖 **Comment from Codex working with Leo:**

The allocation-sync start path needs the same first-activation guarantee as the
lifecycle and generic start paths. **Fixed locally against
[0e38ea7ac4](https://github.com/ddoghq/dd-source/commit/0e38ea7ac4c7a568fda98e3cf90cca900032fdc9).**
Both schedule save branches now record activation within the caller's transaction
and return the timestamp they wrote. The conditional update preserves an earlier
activation. Replication uses the sender's value; drafts, ordinary rollouts,
unstarted schedules and already-running legacy allocations do not acquire an
invented timestamp.

The baseline regression fails for both update and replacement starts while its
16 preservation/control cases pass. The final matrix extends coverage to creating
a schedule with no predecessor, with rollback checks for all three save paths.
All 26 new cases pass. Five native suites pass: service 1,110, lifecycle 176,
compiler 842, cross-DC 58 and allocation HTTP 192 JUnit cases, including parent
cases. Service and lifecycle needed longer limits after the retained timeout run.
Exact patch pins and results are in the [native receipt](native-validation.json).
These are local tests; deployment prerequisites remain separate.

## Holdout activation: discussion_r4343815683

🤖 **Comment from Codex working with Leo:**

**Decision [D011, revision 1](https://github.com/DataDog/ffe-system-test-data/blob/7853a11426a50691e748e64907e93d4682d91215/contracts/experimentation-opt-out/decision-history.md#d011): future-only mode retains pre-cutoff holdout runs.**

The [RFC](https://docs.google.com/document/d/153tRlj46l-XfBGCA2X_NvxW4vwYObaH8zm2moP_AqMk/edit)
explicitly covers an existing holdout activated before the cutoff: immediate mode
skips it, while future-only mode continues its evaluation and normal exposures.
Its implementation table says generated allocations carry the holdout run's
activation time. Leo's [October 19 reply to Eric](https://docs.google.com/document/d/153tRlj46l-XfBGCA2X_NvxW4vwYObaH8zm2moP_AqMk/edit?disco=AAACJEiBKfM)
records the customer choice between immediate withdrawal and future-only
exclusion, superseding the earlier immediate-withdrawal-only discussion.

Your older-holdout/newer-covered-experiment example is a consequence of this
run-level continuity choice. Dropping activation would change that choice by
treating every holdout as unknown. We should keep the RFC behavior unless we
explicitly revise the product decision.

**Implementation retained at
[0e38ea7ac4](https://github.com/ddoghq/dd-source/commit/0e38ea7ac4c7a568fda98e3cf90cca900032fdc9).**
Generated holdouts keep `doLog=true` and their stable run activation; shipping a
covered winner does not reset that clock.

**Shared proofs:** [draft FFE test-data PR #55](https://github.com/DataDog/ffe-system-test-data/pull/55)
contains the existing [D011 decision](https://github.com/DataDog/ffe-system-test-data/blob/7853a11426a50691e748e64907e93d4682d91215/contracts/experimentation-opt-out/decision-history.md#d011).
The new activation-specific proof and RFC evidence are local additions awaiting
authorized publication; they are not yet part of that published revision.

<details>
<summary><b>Behavior</b> — preserve the customer's selected mode</summary>

| Holdout run | Immediate | Future-only |
| --- | --- | --- |
| Before the cutoff | Skip | Evaluate normally; returned assignments retain exposures |
| At/after the cutoff | Skip | Skip |
| Unknown activation | Skip | Skip |

Future-only mode compares run activation, not an individual subject's first
enrollment. It does not promise immediate withdrawal from every experimentation
activity. Skipped allocations emit no exposure; no withdrawal telemetry or
automatic analysis correction is introduced.

</details>

<details>
<summary><b>Native validation</b> — local compiler and database evidence</summary>

The compiler tests retain the assertions that generated holdouts carry activation
and that winner selection preserves the holdout clock. The shared service change
is tested separately through database transactions, with regression coverage
from the existing HTTP and cross-DC suites. This does not add a new HTTP
reproduction of the exact sync-start request. The [native receipt](native-validation.json)
lists the five passing suites and source hashes.
This branch does not contain the future-mode evaluator implementation, so these
checks are not a combined producer/evaluator or deployed end-to-end test.

</details>

<details>
<summary><b>Sneak preview</b> — a checked counterexample to dropping metadata</summary>

The local [activation model](../../lean/ActivationReview.lean) contains this
checked theorem:

```lean
theorem dropping_holdout_activation_changes_future_policy :
    holdoutPolicy .future .valid .before ≠ holdoutPolicy .future .valid .missing := by decide
```

For a valid opted-out subject in future-only mode, keeping a before-cutoff holdout
timestamp and removing it produce different policy results. The model retains
the RFC-selected result. It does not prove native compiler or evaluator code.

The local proposal checks 65 theorems, 313 existing semantic cases, 36 operational
cases and 156 activation-producer cases. The latter comprise 144 abstract sync
states and 12 holdout mode/boundary cases. Native database and compiler evidence
remains separate, and the central contract remains a draft.

</details>

# Published activation review replies

[Published reply](https://github.com/ddoghq/dd-source/pull/139381#discussion_r4354604887)

🤖 **Comment from Codex working with Leo:**

**Fixed in [3c0214a3b5](https://github.com/ddoghq/dd-source/commit/3c0214a3b5497b70673e774f07aad9d52f582676); merged with main and validated at [4e7164752a](https://github.com/ddoghq/dd-source/commit/4e7164752a0c66f6b501fc6fcc1fd6a9182bd3a2).** Both schedule-save branches now record the first activation in the caller's transaction and return the timestamp they wrote. The conditional write preserves an existing activation; replication, drafts, ordinary rollouts, unstarted schedules and already-running legacy allocations do not acquire an invented timestamp.

The original-source regression fails for the update and replacement first-start cases while 16 controls pass. All **26** final creation/update/replacement cases pass, including rollback on each path. Seven local suites pass after the merge: service, lifecycle, compiler, repository, model, allocation HTTP and cross-DC. The new regression drives the database service directly; the existing HTTP suites provide surrounding coverage. [Pinned native results](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/evidence/activation-review-20261022/main-merge-native-validation.json).

**Shared proofs:** [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55), [D011](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/decision-history.md#d011), and the [activation model](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/lean/ActivationReview.lean) preserve the first-write and guard obligations. Model proofs, native tests, CI and deployment remain separate; migration and validator rollout prerequisites are still open.


[Published reply](https://github.com/ddoghq/dd-source/pull/139381#discussion_r4354605103)

🤖 **Comment from Codex working with Leo:**

**Decision [D011, revision 1](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/decision-history.md#d011): future-only mode retains holdout runs activated before the cutoff.**

Your older-holdout/newer-covered-experiment example is a consequence of the run-level continuity policy. The [RFC](https://docs.google.com/document/d/153tRlj46l-XfBGCA2X_NvxW4vwYObaH8zm2moP_AqMk/edit) explicitly retains pre-cutoff holdouts in future-only mode and requires generated allocations to carry the holdout run's activation. Leo's [October 19 clarification](https://docs.google.com/document/d/153tRlj46l-XfBGCA2X_NvxW4vwYObaH8zm2moP_AqMk/edit?disco=AAACJEiBKfM) records the customer choice between immediate withdrawal and future-only exclusion. Dropping activation would change that decision by treating every holdout as unknown.

**Implementation retained and validated at [4e7164752a](https://github.com/ddoghq/dd-source/commit/4e7164752a0c66f6b501fc6fcc1fd6a9182bd3a2).** Holdouts keep `doLog=true` and their stable run activation; shipping a covered winner does not reset the clock.

**Shared proofs:** [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55) and the [published D011 decision](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/decision-history.md#d011).

<details>
<summary><b>Behavior</b> — preserve the selected opt-out mode</summary>

| Holdout run activation | Immediate | Future-only |
| --- | --- | --- |
| Before cutoff | Skip | Evaluate normally; returned assignments retain exposures |
| At or after cutoff | Skip | Skip |
| Unknown | Skip | Skip conservatively |

Future-only mode compares run activation, not a subject's prior enrollment. It does not promise immediate withdrawal from every experimentation activity. Skipped allocations emit no exposure; no withdrawal telemetry or automatic analysis correction is introduced.

</details>

<details>
<summary><b>Native validation</b> — local checks at <a href="https://github.com/ddoghq/dd-source/commit/4e7164752a0c66f6b501fc6fcc1fd6a9182bd3a2">4e7164752a</a></summary>

Seven suites pass: service 1,146; lifecycle 176; compiler 896; repository 282; model 297; allocation HTTP 193; cross-DC 58 JUnit cases, including parent cases. The compiler retains assertions for holdout activation, unknown creation, artifact propagation and winner selection preserving the clock. All 26 new sync regression leaf cases pass. [Exact source and results](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/evidence/activation-review-20261022/main-merge-native-validation.json); [retained history](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/decision-history.md#historical-linked-checks) includes the original regression failures and earlier timeouts.

These are local checks. They do not establish a combined producer/future evaluator or deployed end-to-end result. CI, migration deployment and validator rollout remain separate.

</details>

<details>
<summary><b>Sneak preview</b> — reusable checked contract and counterexample</summary>

The [English decision](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/activation-feedback.md), [Lean model](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/lean/ActivationReview.lean), [156-case activation corpus](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/corpus/activation-producer.jsonl) and [linked validation history](https://github.com/DataDog/ffe-system-test-data/blob/188da74973dda1afe1e3ca17aac2654ad4fa016e/contracts/experimentation-opt-out/decision-history.md#historical-linked-checks) retain this distinction. The checked model contains:

```lean
theorem dropping_holdout_activation_changes_future_policy :
    holdoutPolicy .future .valid .before ≠ holdoutPolicy .future .valid .missing := by decide
```

Keeping an older holdout timestamp and removing it produce different results for a valid future-only opt-out. The model preserves the RFC-selected result; it does not prove native compiler/evaluator code.

The activation addition contributes 12 theorems and 156 model cases. The merged draft checks 71 theorems and 529 cases across semantic, operational, activation and SemVer profiles, plus 14 verifier controls. Public evidence contains summaries and source hashes; full internal snapshots and raw logs remain private. This central draft does not confer fleet approval.

</details>

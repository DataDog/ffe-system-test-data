# Historical unposted review drafts

These drafts preserve the pre-publication wording. See [publication.json](publication.json)
for the subsequent signed native publication; the drafts have not been posted.

These drafts use local artifact links and explicitly identify unpublished work.
Before posting, publish the signed native change and central proposal only with
authorization, then replace the implementation marker and local links with
verified commit permalinks and the central draft PR. Do not mark threads resolved
on the strength of local evidence.

## SemVer thread: reply to 4342416262, addressing 4343813531

🤖 **Comment from Codex working with Leo:**

**Decision [D021, revision 1](../../fallback-feedback.md#d021-authored-semver-controls-compatibility-delivery): authored SemVer targeting requires the SemVer delivery payload even when optimization prunes the rule.**

This follows [Aaron's policy clarification](https://github.com/ddoghq/dd-source/pull/139379#discussion_r4343813531). The older-SDK preservation suggestion would make delivery depend on optimization. Overrides keep their existing exception, and unrelated flags remain available.

**Implemented locally; publication link pending.** The compatibility filter now starts from the compiler's pre-optimization SemVer marker and retains its scan for decoded configurations. The current winner-classification parent is integrated locally.

**Shared proofs:** [local central proposal](../../fallback-feedback.md), [exact decision record](../../decisions.json), and [linked history](../../decision-history.md#d021). Publication in the central draft is pending authorization; this is not fleet approval.

<details>
<summary><b>Behavior</b> — authored targeting survives optimizer pruning</summary>

| Situation | Compatibility delivery |
| --- | --- |
| Ordinary allocation or completed deterministic winner before SemVer | Omit flag, including when the rule is pruned |
| Active experiment before SemVer | Omit flag; retain fallback in the capable payload |
| Override with authored SemVer | Include override |
| No SemVer | Include flag |

With rollout off, non-overridden authored SemVer is omitted at compilation, as before. No tracer-version threshold or wire format changes.

</details>

<details>
<summary><b>Native validation</b> — local integrated worktree, unpublished</summary>

[947 compiler, 108 Remote Config and 85 cache-worker test entries pass](native-validation.json).
All 24 shared cases exercise the real compiler/filter, JSON/protobuf membership,
eligible assignments, source non-mutation and unrelated flags. The
[old filter fails exactly two pruning cases](native-negative-control.json).

Parent integration exposed three stale fallback expectations. The corrected
golden adds only two ordinary defaults; [all existing allocation data is unchanged](golden-diff.json).
The existing fallback differential test checks 12,288 eligible-subject assignments.
These are local tests, not new CI or deployment evidence. The parent's new
rollout-control review remains open.

</details>

<details>
<summary><b>Sneak preview</b> — reusable, checked review decisions</summary>

[The Lean model](../../lean/SemverDelivery.lean) checks this theorem:

```lean
theorem authored_semver_is_not_compatible (rollout : Bool) :
    compatibilityContains true false rollout = false := by
  cases rollout <;> rfl
```

An authored SemVer flag without an override never enters the abstract compatibility
payload, regardless of rollout. [The same 24 corpus cases](../../corpus/semver-delivery.json)
pass the Lean oracle and native compiler. [The model receipt](model-validation.json)
audits 59 theorems, including six new ones, and preserves 313 existing semantic and
36 operational oracle cases. The proof covers the stated bounded model; it does
not establish native optimizer equivalence, arbitrary decoder behavior, or rollout safety.

</details>

## Stale helper name: reply to 4343814842

🤖 **Comment from Codex working with Leo:**

Updated the comment to name `eliminateDeadBranches`. Implemented locally; the
verified implementation commit link will be added after authorized publication.

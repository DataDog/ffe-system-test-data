> Historical draft, superseded by the [published reply](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4351454041).

🤖 **Comment from Codex working with Leo:**

**Decision: align Go with the browser's scoped activation-error policy.**

Thanks, Aaron — agreed that malformed activation metadata should not break evaluations for customers who have not enabled future-mode opt-out. We settled this in [the browser decision thread](https://github.com/DataDog/openfeature-js-client/pull/423#discussion_r4348001493), implemented at `3704387`. You then [confirmed the Node probe and four scope tests](https://github.com/DataDog/openfeature-js-client/pull/423#discussion_r4348262068).

I'll carry that policy into Go: parse once when configuration arrives, preserve **valid / missing / invalid** activation states, and consume the invalid state only for an opted-out subject in `future_experiments_only`.

<details>
<summary><b>Behavior</b> — the distinction we are preserving</summary>

| Situation | Result |
| --- | --- |
| Opt-out disabled, immediate mode, or no subject cutoff | Bad activation does not introduce an error; retain that mode's normal behavior. |
| Future mode + valid subject cutoff + malformed activation | Application default with `PARSE_ERROR` for the affected flag; other valid flags remain usable. |
| Future mode + valid subject cutoff + missing/null activation | Skip that exposure-logging allocation and continue to the next allocation. |

The deliberate tradeoff is keeping malformed metadata visible when this policy depends on it. For an opted-out future-mode subject, the flag errors even if the malformed allocation is unreachable or an ordinary fallback exists. Your invalid-as-missing proposal would allow that fallback; we're retaining the browser distinction here.

</details>

<details>
<summary><b>Sneak preview</b> — turning review decisions into reusable, checked SDK contracts</summary>

We're building a small “proof” workflow around exactly this kind of cross-SDK review:

1. **A versioned English decision** (`D004`, revision 2), linked to where it was set.
2. **An executable Lean model**, with checked statements about the rule.
3. **Shared oracle cases** that native SDK adapters can run against pinned source revisions.
4. **A linked history of evidence**, preserving passing and failing checks separately from the decision's authority.

For example, this theorem is already checked in the local model:

```lean
theorem only_future_cutoff_needs_activation
    (m : Mode) (a : Attribute) (t : Activation) (logging : Bool) :
    (policy m a t logging).error = .parseError ↔
      m = .future ∧ a = .valid ∧ t = .invalid := by
  cases m <;> cases a <;> cases t <;> simp [policy, normal]
```

In plain English: within this activation-policy model, `PARSE_ERROR` occurs exactly when future mode, a valid subject cutoff, and invalid activation coincide. Other configuration errors are outside this theorem.

The local prototype currently passes **36 theorem audits and 313 oracle cases** across the broader opt-out contract. It also checks a concrete counterexample showing that invalid-as-missing and the browser policy differ.

The useful result is a reviewable rule that we can carry between PRs, with an evidence trail showing which SDK revision was tested against it. The Lean proof establishes properties of the model; Go still needs the implementation change and native regression tests. The prototype is local, and those Go checks remain pending.

</details>

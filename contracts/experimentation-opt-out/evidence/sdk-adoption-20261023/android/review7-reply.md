🤖 **Comment from Codex working with Leo:**

**Decision [D008, revision 2](https://github.com/DataDog/ffe-system-test-data/blob/dbe8b6668ad18294a9228b01d2acfb4a6da810bf/contracts/experimentation-opt-out/decision-history.md#d008): preserve the reference implementation's effective-policy acknowledgement checks.**

This identifies an extension boundary. The [merged browser helper](https://github.com/DataDog/openfeature-js-client/blob/38d611cf4c73b9687b97f7da0f8224d2fefab966/packages/core/src/evaluation/experimentation-opt-out.ts#L96) and [current iOS helper](https://github.com/DataDog/dd-sdk-ios/blob/386f8c5d59af9c9ffb9cf7dee6aa2e90c95a5c0f/DatadogFlags/Sources/Models/FlagsEvaluationContext.swift#L94) use the same check. With no effective policy, they reject the legacy `true` acknowledgement and the two known filtered modes. Unknown mode strings alone are accepted.

**Implemented in [6e5fe6c](https://github.com/DataDog/dd-sdk-android/commit/6e5fe6cf6266a5d965a44a7f1958f1bfe1fcf735).** I am retaining that behavior and declining an Android-only change. The stricter rule is recorded as a separate cross-SDK proposal. No current-server counterexample was supplied. D008 records a source-observed baseline and a provenance gap; it does not claim public agreement on every unknown wire value. D020 concerns edge requests and does not establish this response policy.

**Shared proofs:** [central draft #55](https://github.com/DataDog/ffe-system-test-data/pull/55), [D008 and its source limits](https://github.com/DataDog/ffe-system-test-data/blob/dbe8b6668ad18294a9228b01d2acfb4a6da810bf/contracts/experimentation-opt-out/decision-history.md#d008).

<details>
<summary><b>Behavior</b> — current source behavior</summary>

| Effective policy and response | Result |
| --- | --- |
| No policy; legacy `true` | Reject |
| No policy; known `immediate` or `future_experiments_only` mode | Reject |
| No policy; unknown mode string and missing/false legacy value | Accept |
| Immediate or future policy; unknown mode string | Reject |

The last two rows are source observations. A future wire policy must define whether an unknown value indicates filtering. Changing that rule requires coordinated consumer expectations.

</details>

<details>
<summary><b>Native validation</b> — source inspection at <a href="https://github.com/DataDog/dd-sdk-android/commit/6e5fe6cf6266a5d965a44a7f1958f1bfe1fcf735">6e5fe6c</a></summary>

The independent inspection confirms Android/browser/iOS agreement for this branch. No code or corpus changes were made for this comment.

The existing 1,792 Android test executions and 187 selected profile cases pass. The profile contains 135 acknowledgement rows using only missing, immediate, and future modes. Those results do not validate unknown modes. No new runtime probe was executed for this proposal.

</details>

<details>
<summary><b>Sneak preview</b> — the proof boundary is explicit</summary>

The [checked proof](https://github.com/DataDog/ffe-system-test-data/blob/dbe8b6668ad18294a9228b01d2acfb4a6da810bf/contracts/experimentation-opt-out/lean/Proofs.lean#L91) states:

```lean
theorem no_policy_rejects_filtered_mode (ack : AckBoolean) (mode : AckMode)
    (cutoff : AckCutoff) (filtered : mode ≠ .missing) :
    acknowledges .none ack mode cutoff = false := by
  cases ack <;> cases mode
  all_goals first | exact (filtered rfl).elim | rfl
```

[The model's `AckMode`](https://github.com/DataDog/ffe-system-test-data/blob/dbe8b6668ad18294a9228b01d2acfb4a6da810bf/contracts/experimentation-opt-out/lean/Contract.lean#L149) contains only missing, immediate, and future. The theorem proves rejection of the two modeled filtered modes. It does not prove safety or acceptance of unknown strings. The draft retains this limit alongside [native evidence](https://github.com/DataDog/ffe-system-test-data/blob/dbe8b6668ad18294a9228b01d2acfb4a6da810bf/contracts/experimentation-opt-out/evidence/sdk-adoption-20261023/README.md).

</details>

# Unknown response-mode review assessment

Review root: 4355919118. This assessment is read-only.

Recommendation: preserve the user's merged-browser baseline. Treat rejection of every unknown response mode as a separate cross-SDK compatibility proposal.

Android, iOS, and the pinned merged-browser implementation use the same ordinary-response rule. They reject legacy boolean true and the two known filtered modes. An unknown mode with no true legacy acknowledgement is accepted. When an enabled effective policy applies, all three reject an unknown mode.

The review's scenario is possible only if a server returns assignments filtered under an unrecognized mode without the recognized filtering acknowledgement. No observed current-server response or counterexample to the supported wire contract was supplied. The scenario is therefore a proposed future or malformed-server response policy, not an Android-only mismatch.

D008 r2 states rejection of explicitly filtered responses. Its imported baseline identifies the known markers above. Its complete rule has no identified public decision-setting comment. The edge reaffirmation preserves supported immediate and future acknowledgement shapes. It does not decide unknown response values.

D020 governs edge request compatibility. It does not authorize or forbid accepting unknown response modes. The current mobile profile has 135 acknowledgement rows, with mode missing, immediate, or future only. Unknown values are outside that model and test domain.

The iOS implementation is in DatadogFlags/Sources/Models/FlagsEvaluationContext.swift, accepts(_:for:). It matches Android and browser. Its FlagAssignmentsFetcherTests.testOptedOutRequestRequiresBooleanAcknowledgement tests known markers and malformed mode together with legacy true. It does not select an unknown-mode-only rule.

The Android PrecomputeMapperOptOutTest covers ordinary acceptance and recognized-filter rejection in all configured modes. Browser experimentation-opt-out.spec.ts checks both known filtered modes and missing or malformed boolean acknowledgements for an effective immediate policy. Go evaluates allocations locally and has no corresponding precompute-response acknowledgement boundary.

If the proposal is adopted, select the complete response-value policy centrally first. Include unknown strings, empty strings, null, wrong types, and explicitly disabled. Then update the profile and all three consumers together. Do not infer a new rule from the existing finite Lean domain or claim D020 already selected it.

No production code, test corpus, central decision, or review thread was changed. No new tests were run for this source assessment. Exact commits, paths, hashes, and the minimal source trace are recorded in review7-semantic-assessment.json.

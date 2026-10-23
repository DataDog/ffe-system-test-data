---
name: lean-sdk-implement
description: Implement or adapt a reviewed, pinned Lean contract in one existing SDK repository, producing a native validated diff and evidence bundle while preserving SDK-specific integration behavior.
---

# Implement a Lean contract in one SDK

Before applying review-driven semantics, read the exact central decision revision prepared with `lean-sdk-decisions`. Use `lean-sdk-feedback` to distinguish author decisions from reviewer proposals and to check which parent fixes the current stack actually contains. A contradictory or superseded decision goes back to the contract owner; it is not an implementation exception.

Accept a task bundle with repository, immutable base SHA, owned files/modules, contract files and SHA256, corpus plus SHA256, explicit reviewed applicability profile ID and independently pinned profile-manifest SHA256, requirement decisions, dependencies, requested behavior, and publication scope. Inspect the bundle and native repository instructions before editing. Missing semantic decisions require clarification; continue unaffected work. A user request for a diff authorizes local implementation, not a push.

Verify the contract, corpus and profile-manifest hashes against the coordinator's reviewed bundle. Reject missing/unknown profiles and unreviewed exclusions; never infer an acceptance profile from the SDK's current behavior. Record any approved input restriction and expected included/excluded counts. Read the actual production entrypoint and existing tests. Implement the requested semantic delta inside that path; do not ship a standalone demo kernel or modify a generated/vendored copy whose owning dependency must change first. If production state cannot be represented by the supplied model, return a contract-gap trace before changing semantics. Do not erase identity, cache lifetime, eligibility, failure or platform behavior merely to fit a smaller oracle.

Work in an isolated clean worktree based on the pinned base. For dd-source, a dedicated sibling worktree is mandatory. Preserve unrelated local changes. You own only the assigned files/modules, are not alone in the workspace, and must accommodate others' edits. If the base moves, retain the original evidence, integrate the new base without rewriting published history, and rerun affected checks.

Implement the smallest native change and a thin conformance adapter that invokes actual production code. Adapt input/output representation only; do not reproduce the algorithm, suppress valid failing scenarios, or generate expected values from the SDK. Use the pinned Lean-derived expectations. Keep native concurrency, lifecycle, transport and serialization tests where they establish behavior beyond the model.

Run the repository-supported focused tests and adapter corpus. Verify that the native runner actually discovers and executes the adapter by name, and check expected trace/event counts; exit zero with zero matching tests is not success. A new test module can fall outside an old name filter. Classify infrastructure/precondition failures separately. Return a minimized counterexample for semantic disagreement. Independent review must inspect the diff and protecting evidence before publication; the implementation agent cannot weaken its acceptance contract to obtain a pass.

Write an evidence bundle using [evidence-bundle.md](references/evidence-bundle.md): exact diff, native commands/results, hashes, remaining limits, and a draft PR title/body. No commit, push, GitHub comment or PR creation unless authorized in the current task. When publication is authorized, use the rollout coordinator's publication rules and the current repository/workspace policies. Never interpret this skill as permission to publish.

---
name: lean-sdk-decisions
description: Persist and revise shared English and Lean SDK decisions from review feedback, with explicit authority, scope, counterexamples and pinned downstream obligations.
---

# Maintain the central SDK decision contract

Use after `lean-sdk-feedback` has collected complete discussion and source evidence, or when a user explicitly resolves a contract choice. Keep workflow instructions in skills and product policy in the designated versioned contract repository. For FFE, use `DataDog/ffe-system-test-data`; inspect live instructions and the existing decision layout before writing. Create an isolated local proposal branch when requested, preserving other worktrees. Branch creation does not authorize a push.

Reuse stable decision IDs and preserve earlier revisions. Record the English rule, authority/evidence URLs, scope, accepted/proposed/conflict status, affected implementation owners, model/corpus mapping, native obligations and supersession history. A source-verified SDK outcome establishes that SDK's behavior; it does not approve fleet policy. Do not import a retrospective POC baseline as accepted main. Explicit prior user decisions remain authoritative within their scope; a new reviewer preference alone does not supersede them.

For conflicting behavior, retain a minimal distinguishing input and each alternative's outcome. Separate malformed from absent, disabled provider from disabled opt-out, configured mode from effective policy, and parsing/preparation from evaluation-time error policy. Ask for a semantic choice only when necessary for dependent implementation; continue recording evidence, independent checks and non-conflicting work.

Ground the model in production before fan-out. Connect each rule to executable Lean definitions or explicitly mark it not modeled. Inspect statements and axioms, run an oracle and independent counterexamples, then compare actual native paths. Never call a proof of the model a proof of the SDK or treat finite corpus agreement as whole-program equivalence. Keep native lifecycle, nil handling, logging, concurrency, transport and performance evidence outside unsupported proof claims.

Freeze the exact English decisions, model, toolchain, corpus file inventory/IDs/counts and applicability profile with hashes. Bind target receipts to source SHA, adapter/patch hash and decision revision. An independently held manifest hash is required for trusted acceptance; hashes stored beside mutable inputs only establish consistency. A semantic revision invalidates earlier receipts for affected decisions. Implementers report contradictions centrally and cannot change their own acceptance baseline.

Produce a propagation plan by implementation owner and dependency, not one task per language label. Revalidate shared core before wrappers. Unknown, unapproved or conflicting decisions must not enter an accepted fleet bundle. Distinguish local proposal validation, central approval, native conformance, PR review, merge, release and deployed behavior. Reuse `lean-sdk-implement` and `lean-sdk-rollout` only for the corresponding authorized scope.

For an example, inspect `contracts/experimentation-opt-out/` on the FFE data proposal branch: browser D004 conflicts with both current Go and a proposed invalid-as-missing patch; D006 supersedes the earlier strict casing rule only in its recorded browser scope. Preserve that distinction when adapting another PR.

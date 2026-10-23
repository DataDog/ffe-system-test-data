---
name: lean-sdk-rollout
description: Coordinate parallel SDK agents from a reviewed Lean contract through native diffs, authorized signed draft PRs, and tracked merge and downstream adoption evidence across dependent repositories.
---

# Coordinate a Lean to SDK rollout

For review-driven changes, begin with `lean-sdk-feedback` and persist the reconciliation through `lean-sdk-decisions`. Reuse accepted decisions within their recorded scope. Keep unresolved semantic conflicts out of fleet acceptance bundles, and invalidate affected evidence when the contract revision changes.

First determine whether the user requests planning, local diffs, publication, or tracking an already authorized rollout. Do not infer push authority from a request to design the workflow or develop this skill. Existing task authorization persists; do not ask again when the exact action is already authorized.

Read the repository ownership/dependency map and reviewed contract bundle. Audit an unvalidated model against production with lean-sdk-audit before using it as acceptance authority. Freeze the English decisions, Lean statements/definitions, theorem audit, corpus/profile and hashes. Agents may propose contract changes, but implementation agents cannot edit their own acceptance baseline. Read [coordination.md](references/coordination.md) before dispatch.

Delegate independent implementation owners in bounded waves using lean-sdk-implement. Supply each worker an exact base SHA, contract/corpus hashes, owned paths, native commands and evidence output path. Tell every worker it is not alone and must preserve others' changes. Sequence shared libraries before package publication, vendoring and wrapper adoption; do not create two agents editing one shared core because two language labels reference it.

Track per target: contract-compatible, diff-prepared, native-validated, independently-reviewed, draft-published, CI-passed, human-approved, merged, released and downstream-adopted. Verify each transition from evidence. Missing toolchains, identity, approvals or backend observations remain distinct blockers. Keep meaningful independent work moving.

Before an authorized publication, apply [publication.md](references/publication.md) and the live workspace/repository rules. Produce the concrete diff and draft body first. Never amend commits, never create unsigned fallbacks, never silently force-push, and never mark drafts ready. Attach each created or worked-on PR to the current task using the app artifact tool when available.

Report diff/test status separately from PR review/approval and mergeability. "Landed" requires the observed merged commit plus any requested release/downstream adoption, not an agent's success message. The user's draft-only rule leaves the ready/merge transition to the authorized human workflow; do not claim fully autonomous landing.

---
name: lean-sdk-audit
description: Compare a pinned Lean behavioral contract with real SDK implementations and existing tests, quantify additional defect detection and duplicated semantic tests, and identify contract omissions before a cross-SDK rollout.
---

# Audit a Lean contract against SDKs

When the input includes PR feedback, use `lean-sdk-feedback` to reconstruct the complete discussion and current source state. Consult `lean-sdk-decisions` before treating an SDK-local outcome as a fleet contract; preserve reversals, native obligations, and unresolved policy alternatives.

Resolve the requested behavior and actual production implementation graph before comparing code. Language count is not implementation count: wrappers, vendored packages, FFI and mobile bridges may share one core. Keep source/contract disagreement open until the governing requirement is established; never treat the model as automatically correct.

Read each repository's AGENTS.md and testing guide. Pin live base/head SHAs and record dirty paths without changing them. Read production callers, not only a similarly named cache class. Map model inputs and outputs to actual SDK state, including optional identity fields, missing versus empty values, eligibility, cache lifetime, concurrency, queues and delivery failure. Record any excluded domain explicitly. Do not replace production behavior with a toy reimplementation in an adapter.

For independent repository groups, delegate one evidence pass per implementation owner. Give reviewers the pinned contract, SHAs, source scope and questions, without your expected findings. Each reviewer owns its report and isolated probe directory; no production edits are authorized by an audit. Consolidate dependent wrappers with their owning core and still inspect wrapper-specific state and lifecycle.

Use [coverage-measurement.md](references/coverage-measurement.md) for the behavior matrix, paired experiments and consolidation accounting. Prefer exact native tests. An unchanged source extraction can support a bounded algorithm result if its bytes/hash and excluded dependencies are recorded; it cannot establish full SDK integration.

Deliver per target: actual owner/path/SHA, equivalence domain, a distinguishing trace for each supported discrepancy, source versus executed evidence, native test coverage, must-keep platform checks, and a proposed adapter. Missing evidence stays unknown. Label a discovered mismatch as a model omission, intentional policy difference, product defect, or unresolved contract conflict. Do not fix it by silently weakening the model or filtering failing cases.

Quantify code-coverage percentages only with real instrumentation on the same scope and revision. Generated trace counts measure exercised inputs. Proof counts measure proved claims. Neither is a percentage of SDK correctness.

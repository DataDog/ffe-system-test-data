# Instructions

Revision: CONTROL-008, November 27, 2026. Issuer: coordinator, following Tyler's direct instructions.

## Current assignments — implementation resumed

Tyler resumed the matrix goal and explicitly requested workspace chats in the x-platform testing project. CONTROL-002 supersedes CONTROL-001's setup-only pause for the assignment below. Other rows are not implicitly assigned.

- **WS-01 — workspace activation foundations:** the newly created workspace chat owns the bounded assignment in [assignments/WS-01.md](assignments/WS-01.md). First verify workspace execution and Control Branch/repository access, then implement shared CI activation and inherited platform-marker fixes within that scope.
- **BITS-01 — Browser online precomputed:** BitsCode owns the bounded assignment in [assignments/BITS-01.md](assignments/BITS-01.md). Verify FIT source access first; do not duplicate WS-01 or broaden into later modes.
- **WS-02 — Android online precomputed:** a dedicated x-platform testing workspace chat owns [assignments/WS-02.md](assignments/WS-02.md). Reconcile existing stacks and native Android prerequisites; no other row may modify that shared SDK prerequisite without coordination.
- **WS-03 — shared native online-precomputed foundation:** coordinator-local implementation agent owns [assignments/WS-03.md](assignments/WS-03.md), excluding WS-01 CI/markers/conftest ownership.
- **WS-04 — iOS online precomputed:** coordinator-local implementation agent owns [assignments/WS-04.md](assignments/WS-04.md) and the shared native iOS prerequisite lane used by RN.
- **WS-05 — Browser execution:** coordinator-local execution agent owns [assignments/WS-05.md](assignments/WS-05.md); executes BITS-01 candidates and returns exact-head receipts.
- **Coordinator:** verify WS-01 started in the requested remote project, independently validate its deliverable and maintain documents. Coordinate the active lanes below and independently review handed-off heads.

No activation PRs or Control Branch PR. Implementors may push activation branches only after appropriate local checks pass with declared, investigated exclusions. The goal is active; SDK conformance is tracked separately.

## Platform eligibility and delivery order — CONTROL-004

Tyler requires an existing core RUM FIT IPC server before a platform row enters implementation. Verify the server, app startup/registration and harness transport against actual source, including relevant WIP; distinguish the core IPC server from FeatureFlagService. If no core IPC server exists, mark the entire platform row deferred. Do not expand this matrix assignment into building a new core IPC server. Unknown eligibility remains unverified and is not permission to dispatch a row. Unity is specifically unverified; an unpublished feature-flag candidate alone does not establish eligibility.

For every eligible row, complete online precomputed first, with applicable fixture activation, local runtime evidence, documented SDK gaps/exclusions and independent coordinator local Crucible acceptance. Only after that cell is accepted may offline precomputed, online rules and offline rules proceed in parallel. This sequence applies even where a later mode could technically be implemented independently. Shared mode infrastructure may be investigated and prepared in parallel without activating later cells prematurely. Retain one integration owner per platform row and bounded ownership of shared files.

Before implementing a deployment-mode path, inventory existing FIT infrastructure and open/merged changes. In particular, inspect FlagServer for actual rules payload delivery rather than assuming the endpoint exists. Rules-based protobuf and portable wire payloads must come from the corpus generation/catalogue tooling and the selected corpus revision, including applicable existing PRs. Do not invent a second converter, hand-edit generated payloads or treat generation success as SDK conformance. Record source/artifact provenance, conversion omissions and the corresponding evaluation cases. Online rules additionally requires the appropriate HTTP endpoint/headers and actual SDK consumption; offline rules requires the corresponding local-loading path.

WS-01 ownership is unchanged. CONTROL-005 assigns BITS-01 and WS-02 below; other rows await explicit assignment. No activation PRs.

## BitsCode execution boundary — CONTROL-007

Tyler confirmed BitsCode cannot run the FIT suite. BitsCode owns preparation, code/fixture changes and diagnosis from returned evidence, but delegates all FIT suite execution to coordinator-assigned local or workspace agents. Do not request more browser downloads/network permissions or attempt an execution workaround in BitsCode. Provide exact candidate patches/heads, FIT/corpus/SDK/provider revisions, commands, case selections, expected observations and setup requirements. WS-05 initially owns Browser FIT execution. Coordinator serialises shared runtime/toolchain use and returns failures for iteration. Static/schema/format checks in accessible repositories remain in BitsCode's scope where supported. A delegated run is attributed to the executor and tied to exact source identity; BitsCode must not claim it ran the suite itself. No activation push or ready acceptance before applicable delegated checks/publication gates pass.

## Matrix freshness — CONTROL-008

Tyler requires the matrix view in goal.md to be updated with every material implementation, assignment, blocker, test, publication or review update. Update the affected cells in the same control publication as detailed workstream/assignment changes, preserving ticket/PR links. Show owner, current stage and decisive evidence/blocker; distinguish implementor reports from independent verification. Reflect row-wide deferrals in every cell. Routine unchanged monitoring does not create a new matrix state.

## Authority and communication

Tyler's direct instructions take precedence. This document carries current assignments; goal.md carries scope/status; REFERENCE.md carries contracts and baseline sources; WORKSTREAM.md records ownership, results and defects; REQUESTS.md carries changes needed in inaccessible repos. Older PR descriptions and Slack messages are historical context and do not override newer instructions.

The coordinator commits and pushes new instructions before notifying @Datadog in the channel. On each notification, fetch the Control Branch and read the new revision before acting. Report progress, blockers, branch links and results in the channel. Read specifications here rather than relying on Slack paraphrases. Never publish secrets, tokens, raw private logs or customer data into control documents.

## Implementation workflow

1. Claim only the assigned platform/cell/sub-feature; record owner, base revisions, dependencies and overlap before editing. Preserve colleagues' commits and dirty work. Reconcile existing implementations/PRs before creating a competing implementation.
2. Edit the imported ffe-system-test-data corpus directly during testing and development to activate the cases applicable to the cell. Track corpus changes separately from the enclosing FIT gitlink; do not discard edits with a submodule refresh. Follow fixture-, evaluation- and matcher-level filters, not only top-level includes. Edit plain authored fixtures directly; regenerate obfuscated companions with the repository tooling rather than hand-editing generated files. Run the documented schema and companion checks when fixture data changes.
3. Implement the FIT server/adapter/component and test activation together where practical. Respect existing field numbers, generated bindings, native host differences and actual SDK capabilities.
4. Run every applicable case. Investigate every failure: harness/adapter, fixture, SDK defect, unsupported SDK capability, environment/toolchain, transport, timeout or contract ambiguity. Fix owned harness/activation defects; report dependencies instead of treating environment failures as SDK exclusions.
5. For an SDK defect/gap, first record expected/actual behaviour, minimal reproducer, revisions, platform/host/mode/API, affected fixtures and evidence in WORKSTREAM.md. Later ticket filing is separate. Canonical expected results remain intact; do not change them to match a defective SDK.
6. After diagnosis is recorded, apply the narrowest supported skip/xfail: per case/platform in corpus where appropriate, or per feature/platform in FIT. Explain the gap and link its workstream ID/ticket. Use xfail only where supported; do not invent unsupported fixture schema. Scope exclusions tightly and record re-enable conditions. Preserve unexpected-pass visibility where supported.
7. Verify local checks pass with all exclusions declared. Include selected/excluded/executed/passed/failed/xfail counts, platform and host, test command, exact FIT/corpus/SDK revisions, and requests/evaluations/telemetry relevant to the feature. Green schema checks or no-op jobs do not establish runtime coverage. Missing native execution is a blocker to report, not a passing cell.
8. Then push an activation branch in each repository that changed. Record both remote refs/revisions, dependencies and results. Do not open activation PRs yet. The coordinator will consolidate whole platform rows where possible before later PR creation is authorised. Do not merge or rewrite another owner's branch.

SDKs do not need to pass all corpus fixtures to finish an implementation cell. Use explicit states: implemented; validated locally with recorded exclusions; activation branch pushed; blocked; consolidated; merged. SDK conformance remains a separate ledger. The coordinator independently validates implementation and exclusion rationale before accepting a cell.

## Repository access gaps

Use REQUESTS.md for a repository you cannot access. Record target repository/base revision, requested file paths and exact patch or actionable implementation changes, acceptance checks and blocking cells. Commit/push the request on the Control Branch if permitted, then link it in Slack. If control writes are unavailable, report that limitation and send the request to the coordinator for committed publication. Never claim an inaccessible target was changed or verified.

## Branch discipline

Control Branch: documentation/coordination only; never open a PR. Keep implementation and fixture activation off this branch. Follow repository instructions and signing requirements. Commit only owned files. Coordinate Control Branch updates by fetching/rebasing or serialising pushes; never force-push over another contributor. Prefer platform-specific workstream/request files if simultaneous updates would collide; keep the indexes updated.

## Local Crucible review gate

Tyler requires local Crucible reviews on branches reported as **ready**. Treat ready as an implementor handoff, not coordinator acceptance. The coordinator queues and reviews the exact published branch head against its declared actual base, including paired FIT/corpus activation revisions and recorded exclusions. No PR is required to conduct this local branch review, and the no-activation-PR policy remains in force.

A ready handoff must identify repository, branch URL, exact base/head, matching corpus/FIT dependencies, local test evidence, diagnosed SDK gaps and exact exclusions. Use [REVIEWS.md](REVIEWS.md) to track pending/in-progress/changes-required/accepted reviews. Run local Crucible independently of implementation; record completed specialist/peer coverage, verification and any unavailable checks. Do not claim a complete council or native runtime pass when evidence is partial.

Iterate on reproduced P0/P1 findings and re-review the changed head until none remain in implementation, harness, activation or exclusion handling. Diagnosed SDK defects may retain the authorised narrow exclusions; review their evidence, scope and re-enable conditions instead of requiring every SDK fixture to pass. Keep unverified access/runtime checks explicit. Every material head/dependency change invalidates affected review evidence and requires a refreshed review. Do not post GitHub review comments, apply labels, approve PRs or open PRs as a side effect of these local branch reviews.

## Delivery gates

Preserve manual-only lifecycle checks outside required CI unless a later instruction changes that policy. Full corpus execution may progress with investigated and recorded exclusions under the policy above. Keep approval, CI, technical mergeability, actual runtime proof and SDK conformance separate. Do not automatically open tickets, request reviews, change PR readiness or create PRs without the applicable assignment/authorisation.

Use Canadian English in prose. Preserve identifiers and quoted source spellings.

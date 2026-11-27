# Instructions

Revision: CONTROL-001, November 27, 2026. Issuer: coordinator, following Tyler's direct instructions.

## Current assignment: establish control only

BitsCode: read README.md, goal.md, this document, REFERENCE.md, WORKSTREAM.md and REQUESTS.md from the named remote Control Branch. Acknowledge CONTROL-001 in the designated Slack channel and report whether you can read the branch and push a documentation update. Report the exact fetched revision. Do not begin matrix implementation, create activation branches or open PRs during this setup assignment. Wait for a committed assignment and its Slack notification.

## Authority and communication

Tyler's direct instructions take precedence. This document carries current assignments; goal.md carries scope/status; REFERENCE.md carries contracts and baseline sources; WORKSTREAM.md records ownership, results and defects; REQUESTS.md carries changes needed in inaccessible repos. Older PR descriptions and Slack messages are historical context and do not override newer instructions.

The coordinator commits and pushes new instructions before notifying @Datadog in the channel. On each notification, fetch the Control Branch and read the new revision before acting. Report progress, blockers, branch links and results in the channel. Read specifications here rather than relying on Slack paraphrases. Never publish secrets, tokens, raw private logs or customer data into control documents.

## Implementation workflow for future assignments

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

## Delivery gates

Preserve manual-only lifecycle checks outside required CI unless a later instruction changes that policy. Full corpus execution may progress with investigated and recorded exclusions under the policy above. Keep approval, CI, technical mergeability, actual runtime proof and SDK conformance separate. Do not automatically open tickets, request reviews, change PR readiness or create PRs without the applicable assignment/authorisation.

Use Canadian English in prose. Preserve identifiers and quoted source spellings.

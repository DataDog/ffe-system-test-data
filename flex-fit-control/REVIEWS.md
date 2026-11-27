# Local Crucible review queue

Policy revision CONTROL-003, November 27, 2026. Coordinator owns review acceptance. Each branch reported ready receives a local Crucible review; implementor readiness alone is not acceptance. No activation PRs.

| Assignment / branch | Reported ready | Exact base/head and paired dependencies | Review state | Evidence / next action |
| --- | --- | --- | --- | --- |
| WS-01 shared activation foundations | No; implementation in progress | Not handed off yet | Awaiting ready branch | Workspace confirmed CONTROL-002 read and fetched current FIT/Android stack heads; queue review when the implementor supplies a ready branch and verification receipt. |

For each ready handoff record repository/remote branch, actual base/head and merge base, FIT/corpus/SDK revisions, ownership, local check commands/counts, exclusions with workstream gap IDs, specialist/peer coverage, numbered findings with evidence, fixes and verification, remaining P0/P1 count and coordinator disposition. Keep evidence tied to exact revisions. If a dependency or branch head changes, refresh affected checks/review.

Review states: awaiting ready branch; queued; in progress; changes required; accepted with stated coverage/limitations; blocked. Acceptance requires no remaining P0/P1 implementation/activation/exclusion defects. SDK gaps may be narrowly excluded only after investigation and recording, per Instructions.md. An environment blocker or partial review remains visible and must not be presented as a clean runtime result.

This queue starts empty of ready branches under current assignments; historical open PRs and candidate receipts in goal.md are not automatically ready handoffs. Local branch reviews make no GitHub review/label/readiness mutations and do not authorise PR creation.

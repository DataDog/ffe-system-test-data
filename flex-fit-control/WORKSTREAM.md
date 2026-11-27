# Workstream, implementation receipts and SDK gaps

Updated November 27, 2026. Implementation resumed under CONTROL-002; workspace chat execution/access is the first verification gate. The November 27 inventory in goal.md is the baseline; its historical checks are not new validation.

## Ownership and assignments

| Work | Owner | State | Next action |
| --- | --- | --- | --- |
| Control setup and matrix coordination | Codex coordinator | Initial control files pushed; signed commit verified | CONTROL-001 acknowledgement requested; implementation remains unassigned |
| BitsCode | No implementation assignment yet | CONTROL-001 acknowledged at c481ab2; all six reads succeeded | Read CONTROL-002; avoid overlapping WS-01 |
| WS-01 shared activation foundations | Dedicated x-platform testing workspace chat | Chat created and execution verified on ffe-xplatform; implementing; Control Branch read confirmed | Implement ACT-01/02, report local checks and ready branch for local Crucible review |
| Platform rows | Await coordinator assignment | Preserve existing WIP and owners | Reconcile dependencies before fanout |

## Control publication receipt

The coordinator pushed the six initial documents on typo/flex-fit-control and verified the signed commit and matching remote revision. Local Markdown links resolve and no machine-local paths were published. Documentation only; fixture content and implementation code are unchanged. No PR was opened.

BitsCode notification and acknowledgement request: https://dd.slack.com/archives/C0CKGQ8T483/p1795797929001209 . BitsCode subsequently acknowledged all six Control Branch reads at c481ab2. Actual bot push remains untested. Current instructions are CONTROL-002; the earlier setup-only pause is superseded for the named assignment.

## WS-01 workspace launch receipt

Chat: FLEX workspace activation foundations; thread ID 01a21df1-4c96-7152-b4f1-2a5be423c216; host workspace-ffe-xplatform; project x-platform testing. Initial commands returned hostname ffe-xplatform and resolved workspace /home/bits/go/src/github.com/DataDog. This verifies remote chat creation and command execution. The repository-collection root is not a Git checkout; the coordinator directed the implementor to scope commands to the FIT and fixture repositories.

Assignment: [WS-01](assignments/WS-01.md), CONTROL-002. Latest workspace progress confirms CONTROL-002 is readable and current FIT main plus Android #136/#241 heads were fetched. The agent is implementing shared fixes while preserving that stack. Earlier waiting-on-approval status has cleared. No ready branch or completed validation is reported. CONTROL-003 adds mandatory local Crucible review at the ready handoff; see REVIEWS.md.

## Review policy update — CONTROL-003

Tyler requires local Crucible reviews on branches reported ready. Coordinator reviews exact heads and paired dependencies, validates exclusions and iterates on P0/P1 findings before acceptance. [Review queue](REVIEWS.md) established; no current assignment has reported a ready branch. No activation PRs or external review publication.

## Existing chat and WIP preservation scan

[WIP-INVENTORY.md](WIP-INVENTORY.md) records four other FLEX-related chats and current local evidence. The 13 native FIT/SDK/provider candidates still have uncommitted overlays; one additional shared IPC commit is unpushed. Flutter launcher, RN iOS registration, MAUI lint, portable filtering and checkout-helper candidates also survive. Some old copies overlap merged/published work; the old pin refresh is already pushed. No candidate in this inventory is implicitly ready or accepted. Reconcile this work before new implementations; local-only origins on three SDK candidates require care before publication.

## Recording implementation progress

For each cell record: stable ID, platform/native host, delivery/evaluation mode, API/sub-features, owner, linked tickets/PRs, real base/FIT/corpus/SDK revisions, branch links, changes, executed checks/counts, exclusions, remaining blockers and independent coordinator validation. Distinguish active coverage from SDK conformance. Add timestamps and links to durable evidence. No activation PRs yet.

## SDK gap ledger

No new SDK defects are claimed by this initial control setup. Existing known-ticket dependencies include FFLSDK-292 numeric behaviour/pin verification, FFLSDK-263 Unity obfuscation, FFLSDK-271 extended SemVer and FFLSDK-290/291 reason contracts. These references require reproduction against the chosen SDK before new exclusions or closure claims. Check goal.md for prior investigation context.

For every newly diagnosed gap add:

- ID (GAP-platform-number), owner, observed date and any existing ticket.
- Platform/host/mode/API, exact SDK and FIT/corpus revisions.
- Fixture paths/case IDs and minimal reproduction/command.
- Expected and actual behaviour, evidence and root-cause classification.
- Coverage/impact, proposed remedy or follow-up question; ticket filing pending if no ticket exists.
- Exclusion layer, exact scope/reason and linked commit; record after diagnosis and before relying on a green run.
- Re-enable conditions, removal owner and verification receipt; track unexpected passes where supported.

Do not put raw credentials, customer data or private logs in this repository. Summarise evidence and use appropriate access-controlled references.

## Delivery sequencing update — CONTROL-004

Tyler clarified row eligibility and order: existing core IPC server, then completed/independently accepted online precomputed, then parallel remaining modes. Rows lacking a core server are deferred; unverified rows cannot yet be dispatched. Unity core-server eligibility is unverified. Inventory existing shared FIT mode infrastructure and corpus-generated protobuf/wire artifacts before introducing new infrastructure. Source inspection confirms the inspected main FlagServer has precomputed JSON serving but no binary rules endpoint; corpus generation tooling and canonical protobuf/wire resources already exist. No new platform assignment or runtime acceptance is claimed by this update. WS-01 remains the only assigned implementation workstream.

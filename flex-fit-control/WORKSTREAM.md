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

## Execution launch — CONTROL-005

Tyler authorised execution under the revised sequence. BITS-01 is assigned Browser online precomputed, conditional on actual FIT access. WS-02 is assigned Android online precomputed in a dedicated workspace chat, including ownership of the shared native Android prerequisite lane. All other platform implementation rows await explicit assignment. Preliminary core-IPC source audit finds eight existing platform transports; Unity lacks an established mainline core and its candidate remains unvalidated, so its entire row is deferred pending confirmed eligibility evidence. Full source receipts are being assembled.

WS-01 reports signed local head 47f8760c5c7ca870a13029bb711cd74d3a506bae based on e07ae57ef3108b18b10d2f67690bc36caf8303af, 912 unit passes, 49 focused checks, Python lint/type checks and no new exclusions. These are implementor-reported. Publication is blocked by repository-wide lint/tooling requirements and sandbox limits; Dynamic Build authentication/native runtime remain unverified. Portable patch/report requested for independent local review. No acceptance or remote activation branch is claimed.

## Active execution — CONTROL-006

- BITS-01 dispatched in Slack: https://dd.slack.com/archives/C0CKGQ8T483/p1795801633460089 . Browser online precomputed; actual FIT access acknowledgement pending.
- WS-02 workspace chat created: FLEX Android online precomputed, ID 01a21e1e-6622-7d42-877a-d0fd475f729d, x-platform testing. Execution receipt pending.
- WS-03 coordinator-local shared_native_foundation agent is reconciling minimum shared online-precomputed foundations; existing main already has configuration_wire/metadata and fixture_json fidelity, so avoid duplicate schema/helpers.
- WS-04 coordinator-local ios_online_precomputed agent is recovering app/service/tests and comparing SDK/provider companions. Xcode exists; disk is limited, so reuse assets. Exact shared dependency remains pending.
- [IPC-ELIGIBILITY.md](IPC-ELIGIBILITY.md) records eight source-eligible rows and Unity deferred. RN/Flutter/KMP/MAUI/Electron are not yet separately assigned implementation lanes; they await bounded shared-interface/ownership handoffs. No later-mode work dispatched.

## Delegated BitsCode runtime — CONTROL-007

Tyler confirmed BitsCode cannot run FIT; all its FIT execution now belongs to local/workspace executors. WS-05 local Browser execution assigned; BitsCode remains code/activation owner and supplies exact test requests/patches. BitsCode verified FIT read and reported WRITE permission, actual push untested. It identified separate RUM SDK and npm flagging-provider pins. Its Chromium download request was denied; do not retry that runtime setup in BitsCode. No Browser runtime pass is claimed. Coordinator independently reproduced WS-01 focused49pass and both failing mutation controls; full review/council/unit run remains in progress.

## Matrix freshness — CONTROL-008

goal.md now reflects every active lane and the whole deferred Unity row. Each subsequent material update must refresh affected matrix cells in the same publication. WS-05 browser_execution local agent launched; BitsCode remains implementation owner. WS-01 local Crucible has independently reproduced49focused passes plus killed inherited-filter and corpus-route mutants; council/full-suite work continues. WS-03 broader failures were reported as missing Chromium; bounded local runtime preparation underway, with no SDK exclusions or acceptance claimed. WS-04 helper15passes remains separate from pending simulator proof.

## Current execution and source handoffs — CONTROL-009

WS-04 reports simulator app compilation and15helper passes using unchanged pinned iOS SDK/provider; real IPC/intake is pending, with absent-key SDK capability gap to record separately. WS-03 reports899initial unit passes plus all57environment-blocked cases passing after Chromium setup, separate runs against the same signed head; full lint/tool gaps and independent review remain. WS-05 local Browser build is ready with flag provider2.4.0 and65cases collected; actual baseline is starting. FIT source handoffs require access-controlled transfer; the app patch has been withdrawn from current public evidence. The public Android SDK candidate remains available. No native cell acceptance or activation push is claimed.

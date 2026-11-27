# Workstream, implementation receipts and SDK gaps

Updated November 27, 2026. Implementation resumed under CONTROL-002; workspace chat execution/access is the first verification gate. The November 27 inventory in goal.md is the baseline; its historical checks are not new validation.

## Ownership and assignments

| Work | Owner | State | Next action |
| --- | --- | --- | --- |
| Control and matrix coordination | Codex coordinator | CONTROL-010 current; matrix refreshed with each material publication | Independently validate exact candidates and maintain evidence/gap ledger |
| BITS-01 Browser implementation | BitsCode | FIT preparation and diagnosis; runtime delegated | Supply candidates and consume WS-05 evidence; no FIT runs in BitsCode |
| WS-01 shared activation foundations | x-platform testing workspace chat | Local candidate; independent specialist review found no actionable defect; coordinator environment reruns pending | Finish independent verification and required publication gates |
| WS-02 Android online precomputed | Dedicated x-platform testing workspace chat | Shared private handoff delivered; integration/compilation underway | Actual native runtime proof; shared Android SDK lane ownership retained |
| WS-03 shared native foundation and simulator topology | Coordinator-local agent | Local signed candidates; focused checks pass, topology full suite pending | Independent review and source-based iOS execution |
| WS-04 iOS online precomputed | Coordinator-local agent | Simulator built on unchanged pins; full source-based FIT run underway | Diagnose every failure and record gaps before exclusions |
| WS-05 Browser FIT execution | Coordinator-local agent | Baseline underway; numeric diagnostic queued | Return actual runtime/configuration/intake evidence to BitsCode |
| WS-06 KMP/MAUI/Electron prerequisites | Existing WS-01 workspace chat | Read-only audit complete | Preserve source evidence; integration prerequisites recorded |
| WS-07 Electron online precomputed | Existing WS-01 workspace chat | Implementation assigned under CONTROL-011 | Separate candidate, renderer IPC/configuration/intake and delegated runtime proof |
| Other platform rows | Queued; Unity deferred | Preserve existing WIP and shared lane ownership | Online-precomputed acceptance before later modes |

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

## Runtime transport and queued-row audit — CONTROL-010

Browser WS-05 baseline is executing with 65 discovered / 17 applicable / 48 skipped; completed result pending. iOS reached InitProvider; independent plain HTTP reproduction isolates advertised-LAN self-connect failure, while one actual simulator loopback diagnostic passes typed evaluation/intake. WS-03 owns a separate source-level topology candidate; no SDK exclusion or accepted runtime result follows from the diagnostic. Android received its private shared diff and is integrating/compiling. WS-06 read-only KMP/MAUI/Electron capability audit is assigned to the existing WS-01 workspace chat. WS-01 independent council/verifier is complete with no actionable defect; full coordinator unit run still underway. Matrix refreshed in this publication.


## Latest execution handoff and matrix refresh — November 27, 2026

WS-03 reports a separate simulator-only topology candidate, 14 focused passes, and full unit execution in progress. Its required lint run still fails at the existing MAUI checkout and missing Flutter tooling stages. WS-04 integrated this candidate and is running the full selected corpus using actual source address selection, without the diagnostic plugin. No cell is accepted and no activation branch has been pushed.

The coordinator's WS-01 full unit run completed with 882 passes and 30 browser-runtime failures before Chromium setup. The exact 30 failed tests are being rerun after runtime preparation; these are separate executions, not a single clean full-suite result.

BitsCode supplied [BITS-01-EXEC-001](https://dd.slack.com/archives/C0CKGQ8T483/p1795803243456209). WS-05 keeps its existing baseline running, then diagnoses the three numeric quarantines with a temporary local probe. This is neither permanent exclusion removal nor readiness. Actual FIT source remains in the access-controlled handoff. goal.md is refreshed in the same publication.

### GAP-ios-001 — OpenFeature error codes omitted

Owner: WS-04; observed November 27, 2026. iOS simulator, online precomputed, OpenFeature API. Native SDK 44a1d94727b0f6ec2382c0d65d0662a1c66cae03; provider 075e5f85e6d25cc07ca22ad536ba6a36adbd6d49; OpenFeature Swift 0.3.1; corpus fe24ed2c4872bf109b0c71ffb2229152d76b8963. These are the unchanged SDK/provider pins used by the candidate.

Diagnostic real-RPC/configuration/intake executions found two failures: defaults-and-emission-gates expects TYPE_MISMATCH for flutter.fixture.string; empty-flags-response expects FLAG_NOT_FOUND for fixture.bool.missing. Actual errorCode is absent in both results. Implementor source inspection attributes this to provider conversions omitting the native error code. The diagnostic transport override was required for those runs; confirmation in the current source-based full run is pending. This is separate from the host LAN transport failure and absent-key SDK capability investigation.

Evidence: WS-04 coordinator-local probe-reports contains the two case AI reports. Full private paths and logs remain access-controlled. No new ticket or exclusion has been created. Preserve authored expectations. Before using an exclusion, confirm affected cases/access paths in the source-based run and record its exact scope, removal owner and re-enable check. Re-enable condition: corresponding typed provider evaluations return the expected OpenFeature error code and both cases pass with configuration/intake evidence.


## Review evidence, prerequisite audit and next assignment — CONTROL-011

WS-01 independent local Crucible completed with no actionable finding: five native specialists, native coverage fallback and targeted verifier. External peer was unavailable. Coordinator reproduced 49 focused passes and two failing mutation controls. Full unit run had 882 passes and 30 missing-browser-runtime failures; all 30 passed in the environment rerun against the same candidate. These separate runs cover all 912 cases; no single uninterrupted green full run is claimed. Full lint and authenticated Dynamic Build/native evidence remain delivery limitations.

WS-03 simulator child reports 960 unit passes, 14 focused passes and clean signed handoff; independent Crucible started against the combined base-to-child delta. WS-04 confirms real-source simulator cases pass without diagnostic overrides; full corpus outcome remains pending.

WS-02 integrated the private shared dependency and reports 69 focused plus 135 broader checks. Kotlin compilation exposed the missing established deployment-access selector; a disposable probe with the published selector compiled and passed ktlint. Coordinator approved bounded schema/generated-artifact reconciliation with defaults and field allocations preserved. No Android runtime executed; workspace has no device/emulator. Coordinator-local Android runtime handoff is next.

WS-06 source audit completed: Electron can reuse its renderer flagging transport; KMP requires native integration and aligned iOS provider dependencies; MAUI requires flag bindings/wrappers and resolved package-identity evidence. Those are integration prerequisites, not fixture conformance failures and not reasons to defer rows that already have core IPC. Source inspection is not runtime proof. WS-07 Electron implementation is assigned to the existing workspace chat, preserving WS-01. Matrix and review queue refreshed in this publication.

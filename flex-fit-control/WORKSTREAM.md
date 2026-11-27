# Workstream, implementation receipts and SDK gaps

Updated November 27, 2026. Implementation resumed under CONTROL-002; workspace chat execution/access is the first verification gate. The November 27 inventory in goal.md is the baseline; its historical checks are not new validation.

## Ownership and assignments

| Work | Owner | State | Next action |
| --- | --- | --- | --- |
| Control and matrix coordination | Codex coordinator | CONTROL-032 current; matrix refreshed with each material publication | Independently validate exact candidates and maintain evidence/gap ledger |
| BITS-01 Browser implementation | BitsCode | FIT preparation and diagnosis; runtime delegated | Supply candidates and consume WS-05 evidence; no FIT runs in BitsCode |
| WS-01 shared activation foundations | x-platform testing workspace chat | Local candidate; independent specialist review found no actionable defect; coordinator environment reruns pending | Finish independent verification and required publication gates |
| WS-02 Android online precomputed | Dedicated x-platform testing workspace chat | Shared private handoff delivered; integration/compilation underway | Actual native runtime proof; shared Android SDK lane ownership retained |
| WS-03 shared native foundation and simulator topology | Coordinator-local agent | Local signed candidates; focused checks pass, topology full suite pending | Independent review and source-based iOS execution |
| WS-04 iOS online precomputed | Coordinator-local agent | Simulator built on unchanged pins; full source-based FIT run underway | Diagnose every failure and record gaps before exclusions |
| WS-05 Browser FIT execution | Coordinator-local agent | Baseline underway; numeric diagnostic queued | Return actual runtime/configuration/intake evidence to BitsCode |
| WS-06 KMP/MAUI/Electron prerequisites | Existing WS-01 workspace chat | Read-only audit complete | Preserve source evidence; integration prerequisites recorded |
| WS-07 Electron online precomputed | Existing WS-01 workspace chat | Implementation assigned under CONTROL-011 | Separate candidate, renderer IPC/configuration/intake and delegated runtime proof |
| WS-09 Electron FIT execution | Coordinator-local executor | Assigned under CONTROL-016 | Exact private candidate build and actual runtime receipts |
| WS-08 Flutter online precomputed | Coordinator-local agent | Implementation assigned under CONTROL-013 | Reconcile WIP and verify both native hosts |
| Other platform rows | Queued; Unity Not planned | Preserve existing WIP and shared lane ownership | Online-precomputed acceptance before later modes |

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


## Completed Browser baseline and shared review controls — CONTROL-012

WS-05 completed the unchanged Browser baseline: exit 0, 17 passed / 48 skipped, 65 selected and 53 deselected, 1209.64 seconds. The 48 skips comprise 45 corpus platform filters and three pre-existing numeric quarantines. It immediately read and preserved all 62 generated AI reports; the three compatibility skips occur before report generation. This baseline does not activate excluded coverage or establish full Browser conformance. BITS-01-EXEC-001 three-case numeric diagnostic is now running with unchanged expectations/pins.

WS-03 independent local council has five completed native specialist jobs, native coverage fallback and a targeted verifier, all retaining no actionable defect. External peer unavailable. Coordinator reproduced 83 focused passes and three isolated positive controls: marker bypass, fresh-receipt bypass and Android loopback each caused test failures; source restored and mutation tree clean. Full coordinator unit suite remains live; no final pass count claimed yet. Platform malformed-response classification and intake remain platform gates.

WS-04 source-based full corpus run has passed real positive cases and exposed further numeric/obfuscation failures; complete AI-report diagnosis is pending. Bounded iOS-only compatibility policy/test ownership is granted under Instructions.md. No new SDK exclusion has yet been authored or approved as a diagnosis. Respect corpus generated-content rules and record gaps/removal conditions before exclusions. Matrix and review evidence updated in this publication.


## Flutter implementation launch — CONTROL-013

WS-08 coordinator-local Flutter online-precomputed assignment is published. It reconciles preserved app/SDK/launcher candidates and actual APIs, preserving shared Android/iOS ownership and unrelated WIP. Both native hosts need separate actual verification. Flutter tooling is absent; preparation is bounded by existing assets, actual project constraints and disk budget. No implementation result, conformance outcome or ready branch is claimed. goal.md updated in the same publication.


## Shared candidate verification and Browser numeric diagnosis — CONTROL-014

Coordinator independently completed all 960 framework unit tests on exact WS-03 child 286af174684cca80eeec627b3c530a2b4a6d010f in 258.71 seconds, plus 83 focused checks and three restored/killed mutation controls. The six independent review lenses and targeted verifier retain no actionable defect. Full platform lint/tooling and native platform conformance remain separate gates; no activation push or acceptance claimed.

### GAP-browser-001 — existing FFLSDK-292 numeric quarantine reproduced

Owner: BITS-01, local execution WS-05; observed November 27, 2026. Existing ticket [FFLSDK-292](https://linear.app/datadoghq/issue/FFLSDK-292). Exact FIT e07ae57ef3108b18b10d2f67690bc36caf8303af, corpus a4966e2ee78f15b0b36f204417ceac9895079262, loaded local RUM bundle built from Browser b3bd0bc59b35467f84f4f8203c9ac1a1f418a992; provider 2.4.0/core 3.6.0; Chromium 153.0.8010.12. Runtime RUM version reports dev; original source/build provenance is retained in private evidence.

Numeric-decimal-float, numeric-decimal-integer and numeric-decimal-number: exactly three cases executed, all failed, no skips/xfails. Each fails at inexact-whole-double: actual 9007199254740992 with TARGETING_MATCH, variant present and no error; expected default -99.5 with ERROR/TYPE_MISMATCH and absent variant. Fifteen of 21 applicable evaluations were attempted: 12 matched, three failed, six remained unexecuted after assertions. Each case fetched configuration once with HTTP 200; executor recorded five exposures and five evaluation events per case plus separate RUM events. Private AI/JUnit, per-evaluation and traffic receipts were preserved and immediately read. An earlier overbroad selection attempt was interrupted/preserved; these counts are the final exact-node run.

The temporary numeric probe was restored and the executor tree is clean. Keep the existing three Web quarantines; no permanent policy or canonical expectation change. Re-enable when the same three authored cases pass typed value/reason/error/variant and emission assertions on the intended runtime. Browser's remaining 45 top-level corpus exclusions are being audited for stale filters versus unsupported wire/features before cell acceptance.

## Electron local handoff — CONTROL-014

WS-07 reports signed local candidate 4191626a9894199b0768311fb991b912a4fc2ba1 stacked on WS-01 47f8760c5c7ca870a13029bb711cd74d3a506bae. It adds Electron scenario/corpus CI integration; 914 unit passes, 45 focused checks and static 18 applicable / 47 excluded of 65. All three numeric cases remain selected; no exclusions added and zero Electron runtime cases executed. The source audit identified a shared zero-quiet-period observation gap for Electron renderer flush. Bounded repair and regression ownership granted; updated private handoff/macOS runtime needed. This is a harness prerequisite, not an SDK defect. Matrix refreshed with all outcomes.


## Browser excluded coverage and Flutter dependency proposal — CONTROL-015

WS-05's source audit of 45 excluded Browser corpus cases found material stale filtering: provider 2.4.0 uses core 3.6.0 with the corpus's obfuscation encoding support. Grouping: two native exact-integer exclusions, one unsupported-consumer case where Browser is capable, 17 encoded positive/hash/salt activation candidates, six mixed numeric-boundary cases with nested Web-applicable evaluations, three encoded decimal numeric-gap candidates, and 16 malformed-encoding whole-response rejection cases. These are source classifications, not newly executed passes or failures. BITS-01 is assigned corpus activation preparation starting with the 17 cases and bounded Web error-contract coordination; WS-05 remains executor. The shared WS-03 rejection implementation exists locally for native transports and must be integrated rather than duplicated; Web transport support remains incomplete. The original 17-case baseline is insufficient for whole-cell acceptance while eligible coverage is still excluded.

WS-05 also confirmed all-types traffic: one HTTP200 configuration request, five evaluations, five exposures and five evaluation events. Full private evidence remains access-controlled.

WS-08 reports the pinned Flutter package lacks the recovered OpenFeature API; a clean newer pure-Dart flag package may be separable from the current native RUM/plugin pin. Coordinator granted bounded Flutter scenario/init/flush hunks and requires real package-resolution/compatibility evidence before adopting that proposal. Optional historical conformance overlays remain separate. No Flutter runtime result or pin-change acceptance is claimed. Matrix updated alongside these instructions.


## Local runtime expansion and toolchain preparation — CONTROL-016

WS-09 local Electron executor is assigned; WS-07 remains code owner. Coordinator imported and checksum-verified the private initial signed bundle, preserving the exact WS-01 prerequisite. The authorised observation-fix child is pending. No Electron runtime proof yet; actual loaded identities and separate renderer/main traffic must be verified.

WS-08 prepared Flutter3.44.0/Dart3.12.0 from its verified official release tag, satisfying the existing Dart constraint without a constraint bump. The executable absence is resolved; this does not establish dependency resolution, full lint or Flutter native runtime success. Coordinator is materialising exact pinned MAUI/Flutter SDK checkouts in the shared review tree to investigate remaining lint gates. Disk remains bounded; no broad cleanup or source changes claimed. Matrix reflects both updates.


## Latest local execution state — CONTROL-016 awaiting signing recovery

Remote remains CONTROL-015 because the configured 1Password SSH signing agent refused local and workspace signed commits. Same-identity retry failed; no bypass or unsigned commit/push. Latest matrix/instructions remain staged locally, and runtime work continues under existing authorisation. Tyler has been asked to unlock/approve the configured agent.

WS-09 verified the exact unsigned Electron observation-fix overlay tree and is building actual runtime assets; no Electron execution result yet. WS-08 resolved the clean separate Dart flag package against unchanged RUM/plugin, reports 19 Dart tests/analyzer, 13 launcher tests and Android APK build success. Runtime awaits dynamic forwarding; task-owned emulator only. Bounded explicit Flutter topology and dynamic-owned-port forwarding ownership granted; no native proof yet.

WS-04 full real-source iOS baseline: 10 passed, 52 failed, three existing platform skips from 65, 1256.70 seconds. Every failing AI report was read. Proposed diagnosis groups are three provider error-code cases, five native numeric conversion cases, four native whole-response numeric parsing cases and 40 applicable encoded fixtures. No exclusions authored. Coordinator inspected exact unmodified provider typed conversions and SDK strict numeric casts/dictionary decoding; a separate direct native public-API control is pending to strengthen attribution. Detailed gap scope and re-enable criteria below precede any reliance on exclusions.

### GAP-ios-001 — source-based confirmation and expanded scope

Same pinned SDK/provider/corpus as earlier entry. Source-based baseline confirms defaults-and-emission-gates, empty-flags-response and type-mismatch-all-types fail because expected error codes are absent. All five provider typed conversions omit the native error; coordinator inspected exact source. Removal owner WS-04; restore all three cases when public provider typed value/reason/error/variant and emission assertions pass. No expectation edits or exclusions yet.

### GAP-ios-002 — strict numeric conversion

Owner/removal owner WS-04. Same SDK44a1d947/provider075e5f85/corpusfe24ed2 and FIT a1fb408f250b20eaa46f9cd7994849c3e77bfcd3. Source-based baseline fails numeric-boundaries-float, numeric-boundaries-integer, numeric-boundaries-number, numeric-float and numeric-number. Valid exact cross-numeric requests return defaults, for example -2147483648 becomes -99 or -99.5. Coordinator inspected SDK numeric variants using strict type casts and public provider delegation. Direct native public-API control is pending; do not attribute an adapter defect to this gap. Re-enable these cases after valid widening/integral conversions and authored reason/error/emission assertions pass. No exclusion yet.

### GAP-ios-003 — whole-response numeric parsing

Owner/removal owner WS-04; same exact inputs above. Numeric-decimal-float, numeric-decimal-integer, numeric-decimal-number and numeric-integer fail InitProvider with the explicit SDK-invalid-response classification for valid authored JSON numeric edge cases. Expected behaviour preserves healthy assignments and per-flag numeric failures. Coordinator inspected the SDK whole-dictionary throwing decoder and strict numeric decoding; keep transport/IPC errors distinct. Re-enable when all four authored cases complete with their exact numeric/negative-result and intake assertions. No exclusion yet.

### GAP-ios-004 — encoded assignments and rejection feature

Owner/removal owner WS-04; same exact inputs above. All 40 applicable encoded fixtures fail: positive encoded assignments return defaults and the 16 malformed-descriptor cases are accepted instead of explicit INVALID_RESPONSE rejection. Two other encoded cases already exclude iOS. Pinned SDK lacks the corresponding encoding/descriptor path in the inspected implementation; generated numeric/error cases also intersect the other gaps. Proposed scope is an iOS-only encoded-feature compatibility exclusion, preserving generated canonical fixtures. Re-enable after key encoding/rotation and descriptor-rejection matrix pass, then evaluate remaining numeric/provider gaps individually. No exclusion authored yet; exact failure inventory/private reports retained by WS-04.


## Latest runtime receipts and Android ready handoff — local CONTROL-016

WS-09 actual Electron smoke passed on exact unsigned observation-fix tree e08134afdee24a807a03956b0ea61b6e55f90417: one case in45.33seconds, immediate AI-report read, one HTTP200 configuration POST with authored context, five typed results and five exposure/five evaluation events. Separate main-bridged RUM recorded six resource/six view events. Loaded Electron45.3.2/Chromium156.0.8078.100; renderer version dev tied to verified Browser b3bd0bc build. Three exact numeric cases now running; no exclusions or acceptance.

WS-02 reports signed local f00e34003d4f35026653c16a945389aa24dd5844 ready for emulator execution. Established selector and Android flush-order integration complete; 960 FIT unit tests, three JVM selector cases, Kotlin compile/ktlint, Python/type checks and Web types pass reported. Corpus #88 head26f75b6; Python/Web/Android generated bindings included, Swift/Dart regeneration needs local coordination. 130 cases collect across direct/OpenFeature; zero device executions. Private exact bundle requested; independent local Crucible queued. No push or acceptance.

Coordinator Flutter lint stage now passes after exact SDK materialisation/toolchain preparation:32 files formatted with no changes and analyzer zero issues. Its normal pub-get step changed the old lock resolution, including plugin3.4.0 to actual pinned-source3.6.0; coordinator inspected/restored only that generated lock change to keep reviewed source exact. This is not a claim of an unchanged-lock full lint pass. MAUI full native build/lint remains unproven; disk now approximately13GiB, so large builds/downloads are paused pending bounded owned-artifact budgeting. No broad cache cleanup.


## iOS exclusion preparation authorised — local CONTROL-016

Coordinator read the exact independent native-control source/log. Same-type native getters returned float0 and integer5; cross-numeric getters returned defaults with native typeMismatch before any IPC mapping. Two HTTP200 receipts were recorded. This macOS diagnostic is not an officially supported platform conformance run and its overall exit1 came from a separate incorrect raw-provider reason assertion; do not call the whole diagnostic passing. Combined with the actual iOS simulator failures and inspected SDK casts, this supports GAP-ios-002 attribution. No further unsupported initialisation retries are required.

WS-04 may now prepare exclusions for the recorded12 authored plain cases (GAP-ios-001/002/003) in the imported corpus and the40 applicable encoded cases through iOS-only feature compatibility (GAP-ios-004), respecting generator rules and canonical expectations. Preserve already-excluded cases/reasons, use canonical gap IDs and stated removal conditions, then rerun the whole65-case selection with actual configuration/evaluation/intake evidence. Anticipated10passed/55skipped is only a prediction until executed; report actual counts and remaining coverage. No activation push or cell acceptance before independent review and publication gates. Matrix reflects preparation, not a green result.


### GAP-electron-001 — renderer numeric gap reproduced

Owner/removal owner WS-07; executor WS-09. Existing related ticket FFLSDK-292. Exact parent4191626a9894199b0768311fb991b912a4fc2ba1 plus unsigned observation treee08134afdee24a807a03956b0ea61b6e55f90417; same corpus/Browser/provider/core pins as the execution brief. Actual Electron45.3.2/Chromium156.0.8078.100. All three exact numeric-decimal cases failed in34.62seconds with no skips, reproducing inexact-whole-double actual9007199254740992/TARGETING_MATCH/variant present/noerror versus default-99.5/ERROR/TYPE_MISMATCH/no variant. Fifteen of21 applicable evaluations attempted:12matched/3failed, six not reached. Each configuration request returnedHTTP200. These failures occur before flush/poll: call-end zero emission counts provide no absence or emission-conformance proof. All AI reports read immediately. No exclusion authored. Re-enable after all three exact value/reason/error/variant and bounded emission assertions pass. Current18 applicable authored nodes are now running as an unexcluded inventory; static65discovered/47excluded is separate from actual runtime selection. The two dependent fixtures' Web-only includes look stale for the same renderer and remain unverified activation work.

## Latest private execution progress — local CONTROL-016

WS-04 prepared the recorded authored-case filters and iOS encoded-feature compatibility after diagnosis, respecting include-versus-skip schema rules; generator companions regenerated and all65schema checks pass reported, four compatibility checks pass. Its complete actual-source rerun is starting; no green result claimed. Three additional no-init/no-IPC SDK model controls pass reported, supplementing the earlier limited direct control.

WS-08 reports94 focused topology/forwarding checks and Android build pass. Initial smoke was blocked before launch by mobilecli missing from PATH; it reused WS-04's existing1.0.24 installation and the smoke retry is live. This is an environment recovery, not an SDK failure. Dynamic forwarding avoids wrong-app connections. No new download and no native pass yet. Root matrix refreshed; remote publication still awaits the configured signing agent.


## Unity Not planned and signed publication recovery — CONTROL-017

Tyler explicitly changed the entire Unity row to **Not planned**. All four matrix cells, current instructions/reference/eligibility disposition and ACT-13 now agree. Earlier deferred/unverified Unity entries are historical and superseded. Preserve candidate inventory; no Unity eligibility, core IPC, implementation or delivery-ticket work is assigned. The other eight delivery rows retain their gates.

Following Tyler's requested retry, signed CONTROL-016 publication succeeded at 1383fff31f7e4bd9f8f722396dfd2d385255be87; signature verified good and remote head matched. This update preserves signed publication and the configured identity.


## Emulator transport diagnosis and current execution — CONTROL-018

WS-08's genuine Flutter Android app installed and reached its own InitProvider over the allocated gRPC forward. Provider initialisation then failed with no configuration HTTP receipts; no typed/intake pass claimed. On the task AVD, the same temporary mock POST via advertised LAN returned no HTTP bytes, while the documented emulator host alias returned HTTP200 and a receipt. This is a transport/infrastructure gap, not an SDK exclusion. Coordinator approved explicit declared emulator host access with physical-device/default preservation; actual SDK smoke must verify it. Task AVD/owned forwards were released after diagnosis. All runtime retries and AI reports are retained privately.

Current SDK identities, canonical fixtures and Unity Not planned disposition are unchanged. Android private bundle reassembled and checksums verified for local review; no device runtime yet. Electron real smoke passes and its18-case current-applicability inventory continues, separate from47 static exclusions. Matrix cells refreshed and shortened to show current state without contradictory historical zero-runtime summaries.


## Runtime receipts and signed handoff — CONTROL-019

WS-04 actual-source full selection completed: 10 passed / 55 scoped skips / 0 failures from 65 cases in491.57seconds. Final37 call-phase AI reports were read;28 setup skips retain JUnit reasons. Runtime manifest records31 typed RPCs,10 configurationHTTP200 receipts,27 exposures and30 evaluation records representing31 evaluations. The12 authored-case and encoded-feature exclusions follow the previously documented SDK gaps; no new canonical expectation changes. Candidate remains for independent local Crucible review and aggregate lint gates, not accepted. Signing is recovered; owner is retrying configured signed local commits.

WS-08 declared Android Emulator host routing now passes genuine SDK smoke: configurationHTTP200 receipt1, all five typed value/detail assertions, five exposures and five evaluations with canonical matching. Native RUM remains disabled without environment credentials; the pure-Dart flags SDK/public OpenFeature path was exercised. Bounded diagnostics and passive synthetic-context receipt are continuing before task AVD release. Exact pinned Browser source was reused without download/build; the previously environment-blocked document audit passes separately. Full fixture acceptance is outstanding.

WS-07 signed quiet-period child8598538616ec739ecc928cd2c421eea69bbee24a was imported privately and its good signature verified. Parent4191626a9894199b0768311fb991b912a4fc2ba1; treee08134afdee24a807a03956b0ea61b6e55f90417 is identical to WS-09's live runtime overlay, so metadata reconciliation does not require repeating unchanged runtime. Bundle SHA-256 ee7c4597c007d7e6ee6134465e7d52d9979a1fab8cc6406bebf944fc375b2ddc. Current18-node inventory remains live; independent review is queued.

BITS-01-EXEC-002 arrived in Slack thread1795804743.272149 with archive fileF0CND2UFUQ0. The existing connector reports attachment metadata without download content; numbered text transport requested before local verification/execution. Bot reports65valid fixtures, synchronized generator companions and41tooling tests; these remain implementor reports until coordinator reproduction. The17-case /87-evaluation activation preserves canonical payloads, nested filters, existing numeric quarantines and other platforms. No runtime result claimed. Unity remains Not planned across all four cells.


## Electron baseline and RN workspace handoff — CONTROL-020

WS-09 completed all18 currently applicable Electron nodes in707.30seconds:15passed/3known numeric failures/0skips or xfails. All18 final AI reports read. Of90 applicable evaluations,84attempted:81matched/3failed/6not reached after failed assertions. All18configurationPOSTs returnedHTTP200; actual intake54exposures/68evaluation events. Forty-seven top-level filtered cases were not selected, with21nested evaluation and21nested event-matcher exclusions separately inventoried. No additional failure or new exclusion. Signed child metadata reconciled to identical tested tree and checkout clean. Whole-cell acceptance still requires applicable stale-filter activation/rejection work and independent review.

Existing workspace chat is assigned WS-10 React Native online precomputed, beginning with exact current PR230/older stack and dirty WIP reconciliation before bounded implementation. Android/iOS native SDK and shared schema owners retain their lanes. Local Android correctness council has started; affected harness tests are running independently. No activation PRs or later-mode assignments.


## Signed iOS review and Flutter diagnosed gaps — CONTROL-021

Coordinator verified good signatures on FIT4bc3a62838895147466fb72d75e7e1683927aa2a and corpus261df0f204655f05b3ea680485d53e4509c901cf. Both clean and exact dependency recorded; FIT treefb7efad3afb35e9c34605b5a9f74a2c36844a505, corpus tree67d05e9dd69122cb5ed7b82bbbd2a54c43deea9c. Independent correctness review started. The remaining mandatory aggregate lint limitations include MAUI full SDK build and Flutter wrapper PATH/tool configuration; they do not imply signing remains blocked. No activation push.

Flutter passive receipt independently captured actual datadog_flags1.2.0 request with canonical targeting_key precomputed-user, attributes plan=pro/platform=flutter, configurationHTTP200 and5exposures/5evaluations. Five unique fixtures now executed:2passed(all-types and encoded all-types)/3failed; repeated context smoke is a sixth run, not a sixth unique case. Diagnostic failures after successful configuration: unknown variation expectedPARSE_ERROR butFLAG_NOT_FOUND; dependent error expectedGENERAL butFLAG_NOT_FOUND; inexact whole numeric value expectedTYPE_MISMATCH but accepted. Clean SDK source71ad97b687f164cde9f43de5d6b42f48b791b9fd confirms failed/error-only entries dropped by assignment decoder and float conversion without an exactness gate. Dependency graph emission and failing-case emission remain unproven because failure precedes flush. Private SDK-GAPS.md contains exact source/AI receipts. No exclusions yet. Full64-applicable Android inventory assigned with task AVD ownership; Flutter iOS not executed. Final73topology/forward/harness checks pass reported, scopedPyright0.


## Android P1 and Browser delegated execution — CONTROL-022

Independent Android correctness specialist identifies oneP1: genuine SDK malformed-configuration rejection is propagated generically and never produces the strict invalid-response marker required by the shared harness. Native error remains reachable even when OpenFeature wraps its initialisation exception. The pinned SDK distinguishes parsing and network failures internally without a stable public parse-specific code; bounded classification or an upstream typed API is necessary. Repair assigned to WS-02 with genuine positive and negative regression controls. Root independently ran73affected harness/server/HTTPunit tests successfully in122.31seconds; specialist44rejection tests also pass, but synthetic marker tests do not prove Android translation. No device runtime or clean council claimed.

Separate Android metadata limitation: public OpenFeature Kotlin0.6.2 exposes scalar typed getters without public key enumeration. Arbitrary native scalar metadata cannot be generically enumerated through that API; track capability explicitly without reflection or extra evaluations.

BITS-01 archive reconstructed from15numbered Slack chunks; each chunk checksum,28511-byte archive SHA-256 b4e547fc6649e98072f8e479ec9eb7507afddf7d318b9b6ca1c67704f080a4c1, ZIP integrity and exact corpus patch SHA-256 00d91c75efac3a4f5a4cfc2f95fcc081663f472822760bd29687aa9484719d04 verified by coordinator. Local WS-05 executor assigned semantic/static verification, exact17nodes then full65function; no runtime result yet.

Flutter full Android corpus run is live with exact retained handle and owned AVD. Full framework unit run reported996pass/1missing-Browser-source failure; exact pinned Browser source was subsequently reused and that audit independently passed1/1. These are separate executions. Flutter lint reported41Dartfiles/analyzer clean. Host free space12.132GiB is close to12GiBfloor; no concurrent large builds/downloads. Only measured owned reproducible intermediates may be reclaimed after preserving APK/evidence.


## Independent checks and resource recovery — CONTROL-023

WS-05 independently reproduced32-file patch semantics: all65 non-root-applicability JSON field spans byte-identical, other eight platforms unchanged, Web applicability20to37. All65schemas valid, generator synchronization and41tooling tests pass. Exactly17nodes collected; focused Browser run is live with passive context/config/intake receipts and unchanged sourcebundle/lock. No download/build/SDKchange. Full65run remains subsequent work; no focused pass claim yet.

WS-04 independent correctness reviewer returns no actionable finding after service/lifecycle/context/details/native-error mapping and exact paired exclusion review. Independently confirms all24changed corpus JSON files preserve every non-root-applicability field,5compatibility tests pass. This is one lens, not full Crucible acceptance. Performance reviewer started; other lenses/coverage/verifier pending.

Disk fell below12GiBfloor while corpus runners were live. Coordinator reclaimed only task-owned unused Electron41.1.0 SDK development runtime and completed iOS compiler intermediates/index; tested Electron45runtime, iOS built app/Products, all source and evidence preserved. Measured13.386GiB free after recovery. Flutter retained the identical live runner without pause/restart; no process timing intervention. No concurrent large builds/downloads.


## Review findings, private RN reconciliation and run recovery — CONTROL-024

Android signed repair acbeb6b2de9f9b6ddee1653697ac4768ce7c2f48, childf00e34003d4f35026653c16a945389aa24dd5844, treeb429406124efa20732510b635018d9a21959a78b, handed off privately. Owner reports compile/ktlint/14JVM/73Python passes; actual published parser exercised with modelled callback/readiness controls. Thirty-two device rejection nodes collected but none executed. Independent signature/import/delta review pending; no P1 closure yet.

Independent iOS QA/SRE lenses returned no actionable finding; source rejection fidelity is distinct from absent negative-case device runtime. Senior lens and coordinator source inspection identify P1 composed MAUI/iOS startup regression: IosDriver now gates launch on gRPC even when MauiDriver uses it for HTTP/JSON. Bounded transport-aware repair assigned. Two performance P2 candidates remain under adjudication, not automatic acceptance blockers or instructions to add arbitrary limits.

RN preserved tracked FIT/SDK diffs were captured without modifying original staged work and transferred privately over configured workspace SSH; remote gzip hashes matched. Exact bases e613bea09f5b53e4a72c8ea435e137e25ee69bf4 and1ebc9bcbb06626985481baa0311c7a9c022d8a94 recorded in private manifest. SDK/native endpoint prerequisites still under reconciliation. Both local GitHub API and connected read returned404 for historical FIT PR230 conversation; no clean review-coverage claim or identity workaround. Current public RN1507 metadata refreshed and supplied to owner.

Flutter child handoff runner/emulator disappeared: both session handles unavailable, authoritative process inventory showed neither runner nor emulator, no exit/JUnit survived and log ended midcase. Cause unproven; suspected child-turn process lifetime. Preserved interrupted-full-01 with4passes/2failures, not full coverage. Root verified no devices, booted solely task AVD and launched distinct guarded full-02-root-owned run with retained session23520/emulator88841. Never restarted a process observed live. Separate run identity/logs/receipts/EXIT_CODE and final AI/JUnit are required; partials cannot be summed as a complete run. Disk recovered above13GiB; no new build/download. Browser exact17-node run continues separately with fresh receipts.


## Shared components matrix row — CONTROL-025

Per Tyler, inserted Shared FLEX/FIT components immediately above Browser. Each deployment-mode column now calls out required server/loader/IPC/scenario/intake/CI components, current implementation limits and a linked component brief. Online-precomputed foundations are local/integrating; offline-precomputed portable/full-corpus work incomplete; online-rules binary endpoint absent on inspected main while corpus protobuf production already exists; offline-rules Browser lifecycle/loader exists with full-corpus/native activation incomplete. No new later-mode work or acceptance inferred; Unity remains Not planned.


## Repair verification and first encoded Browser results — CONTROL-026

Coordinator imported Android child acbeb6b2de9f9b6ddee1653697ac4768ce7c2f48 after verifying raw bundle SHA-256 ae7a2102232978c01ab76ee7209baacc946fffbe5e779ed0d5777d1d189cdd16, bundle prerequisites, good configured signature and exact treeb429406124efa20732510b635018d9a21959a78b. Isolated review tree moved cleanly to child. Independent correctness delta confirms bounded repair/no remaining actionable delta finding; source review does not prove device/gRPC integration. Fresh native evidence/identity required, cancellation/timeouts/network/HTTP remain unclassified and pinned compatibility-shim documentation is accurate. Full Android council/runtime remain pending.

iOS owner reproduced MAUI/iOS transport regression before change and reports31focused checks passing after transport-aware readiness repair, including real HTTP404 listener and nativegRPC probes. Mandatory lint caught new-test style/type issues being corrected. Unrelated RN lockfile modified only by lint preparation is being preserved diagnostically and restored before signed child. No native build/device actions. Delta review and full council/verifier remain pending.

BITS-01-EXEC-002 focused17case Browser run completed675.46seconds:15passed/2failed/0skipped. Both fixed digest/salt vectors fail at eighth evaluation with an empty flag key: expected canonical value-7/TARGETING_MATCH/variant/noerror, observed fallback/ERROR/GENERAL/no variant. Owning layer remains under diagnosis; no SDK gap exclusion or canonical change inferred yet. All17fresh AI reports read and preserved. Full65same-candidate run remains required; positive earlier cases prove encoded coverage directly.

RN owner verified both private WIP patches and reports9mocked bridge tests passing. Coordinator chooses matching public RN1507 source0e2f26fb60361f3394062302dbab37b1e406d1a1 for actual smoke/full inventory with its published native dependencies, excluding separate1567hook changes. SDK context/error capability gaps require diagnosis/recording rather than blocking the run or importing optional overlays. No Android/iOS platform owner pins changed.


## Browser owning-layer diagnosis and signed iOS repair — CONTROL-027

Browser executor independently confirmed the two fixed-vector failures originate in Playwright request serialization: default-valued non-optional flag_key omitted, so JS forwards undefined. Public core3.6 controls distinguish explicit empty string(value-7/TARGETING_MATCH/variant) from undefined(TypeError). These are FIT integration failures, not SDK exclusions. Focused17run attempted85of87evaluations:83matched/2failed/2not reached;17configurationHTTP200,68exposures/84evaluation events observed at call end. Failed cases stop before flush, so no absence/conformance inference. All17contexts independently match authored target/attributes; extra provider targetingKey attribute recorded separately. WS-11 shared repair assigned; full65unchanged run live.

iOS signed repair215fb35b2b3283ec39fb5d39c3bcd1e32b638865, directparent4bc3a62838895147466fb72d75e7e1683927aa2a, tree4d92a1657b31e464edaaf2410bbfed8d6a3d4660 independently signature-verified. Sevenfiles bounded readiness/MAUI transport/docs/test change; source tree clean. Original independent senior reviewer confirms P1 remedied with no actionable delta finding; its own tests6passed/4socket-bind sandbox-blocked. Root complete framework unit run on exact child now live with host permissions, no native builds/device use. All five specialist lenses and native coverage fallback completed; final stateful verifier remains. Two performance P2 observations still require coordinator adjudication.

Root-owned Flutter full-02 remains live at the original guarded identity; partial receipts are not a complete result. No cell acceptance or activation push.


## Raw protobuf transport requirement and review receipts — CONTROL-028

Tyler rejected the proto-JSON control-RPC design and explicitly requires raw protobuf bytes. Existing Browser transport converts control messages to plain objects and directly dispatches without generated receiving-side decode; this is distinct from SDK configuration payloads. WS-11 signed serializer-only candidate d56d3659e29cf2ad7b9480f880e4ef3ff16dbef6 remains preserved but is superseded, not integrated. Owner reports110neighbouring tests and strict Python lint passing; coordinator independently reproduced19focused passes. Correctness/performance/QA/SRE source lenses found no actionable defect in that narrower patch, which does not satisfy the newly explicit binary requirement. Isolated replacement must encode/decode requests and responses with generated protobuf codecs and cover Browser, Electron and Flutter Web. No fixture exclusion or SDK workaround. Live WS-05 baseline remains unchanged.

iOS coordinator exact-child framework suite973passed in279.58seconds. All five native lenses, native coverage fallback and stateful verifier complete with no remainingP0/P1. Synchronous flush actor blocking remains a source-confirmedP2 without an observed hang; client registry retention is bounded operationally by fresh process per corpus case, not an OOM finding. External RPC cancellation remains unverified. Coordinator exact-child full65simulator corpus started and is live; no final corpus result yet. Aggregate lint gaps remain.

RN workspace reports65canonical cases collected,35applicable including17response-rejection cases; actual Android build remains live, no native execution claim. Flutter root-owned full02 remains live. Android independent performance source review raisesP2 repeat-initialization lifecycle allocation; adjudication/device evidence pending, no automatic SDK lifecycle workaround. Disk growth traced to per-case Flutter proxy-port dart-defines producing distinct retained compiler snapshots; only task-owned completed/reproducible artefacts reclaimed, source/apps/evidence preserved.


## Transport clarification hold — CONTROL-029

Tyler asked to hold while discussing serialized ConfigurationWire for offline rules initialization. Coordinator clarified SDK configuration payload and outer control RPC are distinct layers; serialized configuration remains unchanged inside the request. Binary replacement has not been dispatched or integrated. Both proposed transport remedies remain on hold; WS-05 confirmed it will finish the existing unchanged baseline only. Other platform reviews and existing iOS/Flutter executions continue.


## ConfigurationWire ownership clarified — CONTROL-030

Tyler confirmed offline init input is a serialized ConfigurationWire and requires that exact payload to cross FLEX/FIT RPC. Production belongs exclusively in the corpus generator or test runner, never an IPC server. Coordinator withdraws CONTROL-028's broader generic binary-RPC rewrite interpretation and separates this producer/payload contract from WS-11's online-precomputed default-value defect. Shared components row/brief now state ownership and exact producer-to-SDK equality proof. No later-mode work dispatched.

Coordinator independently reproduced all110WS-11 neighbouring tests in152.91seconds; original narrower candidate retained for complete review rather than architecture rewrite. iOS exact-child simulator run completed10passed/55skipped/0fail in498.37seconds, exit0; fresh AI/traffic/corpus exclusion audit assigned independently. No row acceptance or activation push.


## All-mode init audit — CONTROL-031

Tyler requested all-WIP verification and a non-ambiguous final init shape. Two independent source audits plus coordinator refreshed30open FIT PR heads and privately read current RN workspace staged tree4ad01494f28936830d1a876271515a6eb16b6c8c. Existing schema lacks a four-mode discriminator;235 hybrid acceptance cannot prove the requested pure evaluator. Explicit mode/source validation draft prepared for review, no implementation/live changes. Existing serialized rules artifact confirmed; new Python serializer investigation stopped. Matrix shared row/reference refreshed.


## CONTROL-032 — terminal Flutter evidence and Browser repair integration

Flutter Android full02:24passed/40failed/1skipped in2317.41seconds. Independent audit read all65fresh reports and confirmed64configuration POSTs/HTTP200 with matching contexts. Six SDK gap groups own the40failures; see [FLUTTER-GAPS.md](FLUTTER-GAPS.md). Failed-case zero intake counts precede flush and prove no emission absence. Android-only exclusions are preparation, not acceptance; Flutter iOS remains untested.

Browser unchanged full run is incomplete: its process handle is missing, authoritative process inspection found no runner, no terminal JUnit exists. Keep its partial evidence separate. The independently reviewed WS-11 default-preservation repair is integrated locally for the two previously failing vectors; runtime is live using unchanged assets/corpus. Coordinator19focused/110neighbouring passes and five specialists/coverage fallback/stateful verifier found no actionable defect. Full repaired corpus and aggregate lint remain pending.

RN workspace produced an ARM64 compile-only APK and private source handoff; reported10bridge/54Python checks do not establish runtime conformance. iOS fresh exact-child receipts independently establish10passes/55scopedskips,10matching configuration requests/HTTP200,31typed evaluations represented by30evaluation records,27exposures and no observed diagnostics;973unit passes are separate. No activation branch accepted or PR opened.

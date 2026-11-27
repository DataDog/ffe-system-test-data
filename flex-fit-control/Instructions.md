# Instructions

Revision: CONTROL-022, November 27, 2026. Issuer: coordinator, following Tyler's direct instructions.

## Current assignments — implementation resumed

Tyler resumed the matrix goal and explicitly requested workspace chats in the x-platform testing project. CONTROL-002 supersedes CONTROL-001's setup-only pause for the assignment below. Other rows are not implicitly assigned.

- **WS-01 — workspace activation foundations:** the newly created workspace chat owns the bounded assignment in [assignments/WS-01.md](assignments/WS-01.md). First verify workspace execution and Control Branch/repository access, then implement shared CI activation and inherited platform-marker fixes within that scope.
- **BITS-01 — Browser online precomputed:** BitsCode owns the bounded assignment in [assignments/BITS-01.md](assignments/BITS-01.md). Verify FIT source access first; do not duplicate WS-01 or broaden into later modes.
- **WS-02 — Android online precomputed:** a dedicated x-platform testing workspace chat owns [assignments/WS-02.md](assignments/WS-02.md). Reconcile existing stacks and native Android prerequisites; no other row may modify that shared SDK prerequisite without coordination.
- **WS-03 — shared native online-precomputed foundation:** coordinator-local implementation agent owns [assignments/WS-03.md](assignments/WS-03.md), excluding WS-01 CI/markers/conftest ownership.
- **WS-04 — iOS online precomputed:** coordinator-local implementation agent owns [assignments/WS-04.md](assignments/WS-04.md) and the shared native iOS prerequisite lane used by RN.
- **WS-05 — Browser execution:** coordinator-local execution agent owns [assignments/WS-05.md](assignments/WS-05.md); executes BITS-01 candidates and returns exact-head receipts.
- **WS-06 — remaining-row capability audit:** WS-01 workspace chat additionally performs the read-only assignment in [assignments/WS-06.md](assignments/WS-06.md); no new implementation ownership is implied.
- **Coordinator:** verify WS-01 started in the requested remote project, independently validate its deliverable and maintain documents. Coordinate the active lanes below and independently review handed-off heads.

No activation PRs or Control Branch PR. Implementors may push activation branches only after appropriate local checks pass with declared, investigated exclusions. The goal is active; SDK conformance is tracked separately.

## Platform eligibility and delivery order — CONTROL-004

Tyler requires an existing core RUM FIT IPC server before a platform row enters implementation. Verify the server, app startup/registration and harness transport against actual source, including relevant WIP; distinguish the core IPC server from FeatureFlagService. If no core IPC server exists, mark the entire platform row deferred. Do not expand this matrix assignment into building a new core IPC server. Unknown eligibility remains unverified and is not permission to dispatch a row. Unity is **Not planned**, per Tyler’s latest direction; do not dispatch Unity eligibility work, a new core IPC server, implementation or delivery-ticket creation. Preserve historical WIP as inventory.

For every eligible row, complete online precomputed first, with applicable fixture activation, local runtime evidence, documented SDK gaps/exclusions and independent coordinator local Crucible acceptance. Only after that cell is accepted may offline precomputed, online rules and offline rules proceed in parallel. This sequence applies even where a later mode could technically be implemented independently. Shared mode infrastructure may be investigated and prepared in parallel without activating later cells prematurely. Retain one integration owner per platform row and bounded ownership of shared files.

Before implementing a deployment-mode path, inventory existing FIT infrastructure and open/merged changes. In particular, inspect FlagServer for actual rules payload delivery rather than assuming the endpoint exists. Rules-based protobuf and portable wire payloads must come from the corpus generation/catalogue tooling and the selected corpus revision, including applicable existing PRs. Do not invent a second converter, hand-edit generated payloads or treat generation success as SDK conformance. Record source/artifact provenance, conversion omissions and the corresponding evaluation cases. Online rules additionally requires the appropriate HTTP endpoint/headers and actual SDK consumption; offline rules requires the corresponding local-loading path.

WS-01 ownership is unchanged. CONTROL-005 assigns BITS-01 and WS-02 below; other rows await explicit assignment. No activation PRs.

## BitsCode execution boundary — CONTROL-007

Tyler confirmed BitsCode cannot run the FIT suite. BitsCode owns preparation, code/fixture changes and diagnosis from returned evidence, but delegates all FIT suite execution to coordinator-assigned local or workspace agents. Do not request more browser downloads/network permissions or attempt an execution workaround in BitsCode. Provide exact candidate patches/heads, FIT/corpus/SDK/provider revisions, commands, case selections, expected observations and setup requirements. WS-05 initially owns Browser FIT execution. Coordinator serialises shared runtime/toolchain use and returns failures for iteration. Static/schema/format checks in accessible repositories remain in BitsCode's scope where supported. A delegated run is attributed to the executor and tied to exact source identity; BitsCode must not claim it ran the suite itself. No activation push or ready acceptance before applicable delegated checks/publication gates pass.

## Matrix freshness — CONTROL-008

Tyler requires the matrix view in goal.md to be updated with every material implementation, assignment, blocker, test, publication or review update. Update the affected cells in the same control publication as detailed workstream/assignment changes, preserving ticket/PR links. Show owner, current stage and decisive evidence/blocker; distinguish implementor reports from independent verification. Reflect row-wide deferrals in every cell. Routine unchanged monitoring does not create a new matrix state.

## Source handoff visibility — CONTROL-009

Verify the visibility of every source repository before placing patches or source excerpts in this public Control Branch. A public SDK does not establish visibility of FIT or other repositories. Keep internal-source payloads in access-controlled coordinator/implementor handoffs; public control documents may record safe status and bounded requests without embedding internal code. Never use a public evidence path as a workaround for an access or transfer restriction. Recheck all payloads and linked sources before publication.

## Simulator transport investigation — CONTROL-010

The iOS runner reached actual IPC, but this host's advertised LAN self-connect path failed before HTTP request parsing. An independent standard-library server reproduced the same failure; loopback worked. Treat this as a topology/environment investigation, not an SDK defect or a reason to weaken expectations. WS-03 owns a separate bounded topology-based address-selection candidate, preserving its signed original head and Android/physical-device LAN routing. The existing iOS driver is simulator-only; verify actual source selection and real RPC/configuration/intake after integration. Plugin-based diagnostic runs remain separate evidence. No network-probing fallback or global mobile-loopback replacement.

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


## Next bounded integrations — CONTROL-011

WS-02 may integrate the existing published deployment-access selector into its combined candidate: preserve the existing field allocation, default OpenFeature behaviour and direct-access selection; keep configuration-wire field 6 and metadata fidelity. Own this bounded shared schema/generated-artifact lane until handoff; coordinate iOS consumers and regenerate through repository tooling. Unknown selector values must reject. This authorises reconciliation of the established contract, not later deployment-mode implementation. Investigate Android flush ordering and supply an access-controlled portable candidate for coordinator-local Android runtime execution.

WS-06 prerequisite audit is complete as a source audit. Assign WS-07 Electron online-precomputed implementation to the same workspace chat; see [assignments/WS-07.md](assignments/WS-07.md). Preserve WS-01. KMP and MAUI remain queued with their distinct native integration prerequisites; their existing core IPC keeps those rows eligible. BitsCode remains Browser implementation owner; WS-05 remains its local runtime executor. No activation PRs.


## Bounded iOS gap handling — CONTROL-012

WS-04 may own iOS-only compatibility policy and its focused regression coverage in the shared compatibility module/tests. Preserve Browser/Electron owners' policies and all other platform behaviour. Complete source-based diagnosis and record exact gaps, scope and removal conditions in WORKSTREAM.md before relying on exclusions. Generated corpus content must be regenerated through its authorised generator, never manually edited; where a generated feature family is affected, use the appropriate narrow iOS consumer-layer policy. Applicable authored plain-case filters may be edited directly in the imported corpus, following its instructions. Do not classify an adapter, IPC, transport or harness defect as an SDK conformance exclusion. All canonical expected values remain intact.


## Flutter row launch — CONTROL-013

WS-08 coordinator-local Flutter online-precomputed implementation is assigned under [assignments/WS-08.md](assignments/WS-08.md). Reconcile preserved Flutter app/SDK/launcher candidates and reuse shared native foundations. Native Android/iOS SDK lanes remain WS-02/WS-04; request prerequisite changes through those owners. Both native Flutter hosts require separate verification. No later modes or activation PRs.


## Electron emission observation — CONTROL-014

WS-07 may own the bounded shared harness condition and focused regressions that give Electron the existing Web renderer emission quiet period. It uses the same asynchronous renderer flush. Preserve native driver behaviour and the shared rejection path, and prove delayed unexpected emissions fail using a positive control. This is an integration/harness prerequisite, never an SDK exclusion. Return an updated exact private candidate for macOS execution and independent review.


## Browser exclusion audit follow-through — CONTROL-015

WS-05 found that the current Browser flagging core supports the corpus's obfuscation encoding, so blanket Browser exclusion is not justified by lack of obfuscation. BITS-01 must reconcile the 45 excluded corpus cases, starting with the 17 source-eligible encoded positive/hash/salt cases. Prepare applicable corpus activation through its authorised generation path and provide a safe exact fixture patch/test request for delegated execution. Source eligibility is not a pass. Preserve justified exact-integer/unsupported-consumer filters, retain the reproduced numeric quarantines, and diagnose mixed numeric boundaries with narrow applicability rather than hiding their valid evaluations.

Sixteen malformed-encoding rejection cases require actual Web init-error classification and runner integration. The shared WS-03 candidate now handles explicit complete-response rejection for gRPC/HTTP but is not yet integrated into the Web execution tree; do not duplicate that shared work or claim Web error transport is already supported. BITS-01 owns a bounded Web adapter contract proposal; coordinator owns shared runner coordination. Only positively identified malformed configuration may emit the agreed rejection marker; ordinary transport/readiness failures remain failures. Request required source changes through the access-controlled handoff. BitsCode continues to delegate all FIT runs.

## Flutter integration hunk ownership — CONTROL-015

WS-08 may own Flutter-only scenario inclusion and conftest provider-init/flush/readiness hunks, preserving WS-01 marker/CI, iOS, Android and other owners' behaviour. Its proposed separate clean Dart flag-package pin is provisional: prove actual dependency resolution and compatibility with the existing RUM/plugin pin before adopting it. Use genuine batching and bounded intake where no public flush API exists; no fake acknowledgement. Native SDK prerequisite ownership remains unchanged.


## Electron delegated local execution — CONTROL-016

WS-09 coordinator-local Electron executor is assigned [assignments/WS-09.md](assignments/WS-09.md). WS-07 remains implementation owner. Prepare the exact private candidate and actual macOS runtime, then smoke/decimal/full applicable execution after the authorised observation fix is integrated. Existing WS-05 Browser evidence is retained; future Browser requests remain delegated. No activation PRs.


## Local execution coordination — CONTROL-016

WS-08 owns two bounded prerequisites in its candidate: explicit Flutter native-host topology through a public driver property and shared address-selector factory, and Android host-port allocation via adb's dynamic port forwarding. Keep Android device IPC port unchanged, connect to the exact returned host port and remove only the owned forward. No global wrapper loopback, private-field inspection, host-port guessing or remove-all cleanup. Root coordinates shared harness/conftest construction-site hunks and retains other owners' changes. These changes need focused regression controls and actual Flutter runtime identity checks.

Configured SSH signing-agent failures delayed this revision. Preserve signed-commit requirements and verify the signed remote head before claiming publication. Runtime work and exact private patch testing may proceed during a signing interruption; no unsigned commits/pushes or ready-publication claims.


## Unity disposition — CONTROL-017

Tyler directs that the entire Unity row is **Not planned**. This supersedes earlier deferred/unverified Unity wording. All four deployment-mode cells reflect Not planned. Unity is outside current execution scope; preserve historical candidates without assigning new work or creating delivery tracking. Other rows retain their existing eligibility and online-precomputed-first gates.


## Explicit Android Emulator host access — CONTROL-018

WS-08 may extend its public driver/addressing topology support with an explicit emulator host-loopback alias. Android Emulator provides 10.0.2.2 for this purpose; the task AVD returned HTTP200 through it while advertised LAN returned no HTTP bytes/receipt. Treat this as infrastructure routing, not an SDK conformance gap. Use a declared emulator strategy property, preserve URL scheme/port/path/query, and preserve physical-device LAN and iOS/Web/Electron loopback defaults. No runtime probing/fallback or global Android/wrapper remap. Validate conflicting/invalid topology inputs and cover configuration plus intake URLs. Native Android adoption remains a separate WS-02 coordination hunk; other wrappers remain unchanged until explicitly integrated.

Use the official networking contract: https://developer.android.com/studio/run/emulator-networking-address . Real app configuration/evaluation/intake must pass on the source implementation before acceptance. Diagnostic shell HTTP success alone is insufficient. Unity remains Not planned.


## Delegated Browser handoff transport — CONTROL-019

BITS-01-EXEC-002 is received as a Slack attachment, but the coordinator connector exposes its file ID without downloadable content. BitsCode: return the existing archive as numbered base64 text chunks in the original Slack handoff thread (1795804743.272149), with the archive SHA-256, byte count and total chunk count. This is transport of the prepared source-free/public-corpus handoff, not new implementation or permission to push. Preserve the exact fixture patch SHA-256 00d91c75efac3a4f5a4cfc2f95fcc081663f472822760bd29687aa9484719d04. Do not include internal FIT source. Coordinator verifies archive and patch hashes before applying in the isolated WS-05 corpus and delegating the 17 exact nodes followed by the full function. No activation PRs or early activation push. Existing Web rejection integration remains separately pending.


## React Native workspace lane — CONTROL-020

Assign WS-10 React Native online precomputed to the existing workspace activation-foundations chat now that WS-07 handed off its signed candidate. Follow assignments/WS-10-react-native-online-precomputed.md. Begin with current PR230/WIP reconciliation, preserving Sameeran's work, then implement within the bounded RN ownership. Native SDK/shared schema owner coordination is required before overlapping changes. This assignment does not open later modes or change BitsCode's Browser lane.


## Flutter complete Android inventory and iOS review — CONTROL-021

WS-08 may re-reserve its task AVD for the complete64-applicable Android corpus sweep using the verified APK and source topology, retaining exact handles and ownership. WS-02 has not reserved the device. Preserve APK/hash/evidence before measured cleanup of solely task-owned reproducible intermediates; maintain12GiB free-space floor. No broad SDK exclusion without case diagnosis. Flutter iOS runtime remains a separate pending obligation. WS-04 signed paired candidate is now in coordinator independent local Crucible; signing is recovered and aggregate lint gates remain distinct.


## Android rejection integration repair — CONTROL-022

WS-02 owns repair of the local Crucible P1: genuine Android SDK whole-response parsing rejection currently never reaches the shared strict invalid-response marker. Translate only positively identified native parse rejection during awaited initialisation/readiness. Preserve network/HTTP errors, timeout, cancellation and freshHTTP200/no-emission harness guards. The pinned SDK exposes the native error publicly but no stable public parse-specific code; document any narrowly pinned compatibility classification rather than claiming a public typed error API. Do not classify all provider errors as rejection or exclude the cases as unsupported SDK behaviour. Add direct/OpenFeature malformed-response positive tests and network/timeout/cancellation negative controls, then return signed private child and exact evidence for independent re-review. No SDK conformance overlay, activation push or PR.

Also document OpenFeature Kotlin0.6.2 metadata enumeration limitation separately: typed public getters cannot enumerate arbitrary keys. Avoid reflection, fixture-derived reconstruction or duplicate evaluation that changes telemetry. Required preservation beyond the public API remains an explicit capability gap until a proper public API is available. Coordinate shared schema generators with native owners.

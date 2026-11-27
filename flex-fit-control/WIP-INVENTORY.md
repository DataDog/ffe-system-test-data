# FLEX chat and unpublished-WIP scan

Scanned November 27, 2026. This is an inventory and preservation report, not implementation validation or a ready handoff.

## Other FLEX chats

| Chat | What the chat reported | What is verified now | Disposition |
| --- | --- | --- | --- |
| FLEX | Local MAUI cleanup, Android diagnostic handoffs and older pin/CI work; most recent coding summary November 23 | MAUI lint candidate still has an uncommitted edit; older fixture-pin branch is actually pushed now; separate Flutter/RN candidates remain dirty | Reuse current candidates and avoid repeating historical pin/CI work. |
| android2 | September 28 parser fix for omitted extraLogging, three files, 487 SDK tests and targeted device checks; explicitly uncommitted/unpublished | Named temporary parser/FIT worktrees are absent. Portable brief survives; newer Android prerequisite snapshots also contain parser work, but equivalence was not established here | Recovery/reconciliation item, not a currently existing parser branch or fresh pass. |
| dd-sdk-android http | Android #3926 merged; later user-requested cleanup turn failed | Original temporary cleartext checkout is absent; the chat reports the PR merged September 29 | Historical delivered work; no active HTTP implementation WIP established by that chat. Do not infer cleanup succeeded. |
| Plan rules-based UFC fixtures | Research/planning only, with saved compatibility/resource plan | The plan file exists and is untracked in dd-source | Preserve the planning artifact; do not count it as converter implementation or publish it wholesale into the public control repository. |

The recent-chat tool showed only FLEX and this coordinator in the project; the older local chat catalogue recovered the three additional related chats above. All four were read through the app, with older substantive messages checked where recent turns were guidance refreshes/monitoring. Local catalogue project IDs differ from app IDs; older-chat association is corroborated by catalogue names, common FLEX working directory and conversation subject. This is not a claim that every inaccessible/remote/archived chat was enumerated.

## Preserved native delivery package — verified uncommitted

All 13 physical candidates listed below still exist with local changes. Six are FIT/shared candidates and seven are SDK/provider prerequisites; the Android/RN Android work and shared copies overlap, so these are not 13 independent required PRs. Their corresponding named implementation branches are absent from the live GitHub branch lists (Flutter's SDK copy is detached). Existing public PRs such as #136/#230 do not contain these dirty overlays merely because their base history is published.

| Candidate | Worktree name | Local branch | Changed status entries |
| --- | --- | --- | --- |
| fit-shared | native-ipc-shared | typo/fit-ipc-shared | 20 |
| fit-android | native-ipc-android | typo/fit-ipc-android | 21 |
| fit-ios | native-ipc-ios | typo/fit-ipc-ios | 33 |
| fit-react-native | native-ipc-react-native | typo/fit-ipc-react-native | 36 |
| fit-flutter | native-ipc-flutter | typo/fit-ipc-flutter | 33 |
| fit-unity | native-ipc-unity | typo/fit-ipc-unity | 53 |
| sdk-android | native-ipc-android-316-sdk | typo/fit-ipc-android-316 | 37 |
| sdk-ios | native-ipc-ios-322-sdk | typo/ios-native322-ipc-prerequisites | 19 |
| sdk-ios-provider | native-ipc-ios-provider | typo/fit-ipc-provider-errors | 6 |
| sdk-react-native | native-ipc-react-native-sdk | typo/rn-fit-ipc-prerequisites | 25 |
| sdk-rn-android | native-ipc-rn-android-sdk | typo/rn-native-android-context | 19 |
| sdk-flutter | dd-sdk-flutter | detached HEAD | 17 |
| sdk-unity | unity-provider-ipc | typo/unity-provider-ipc | 19 |

Counts are Git status entries, including generated files/gitlinks, not unique logical changes. No source or fixture tests were rerun. Historical November 17 validation does not establish compatibility with current main.

The shared candidate additionally has commit ea6b6dc21bd572a1c0f5180357525dfc42548ad9, “test: support native precomputed configuration endpoints”, absent from all refreshed FIT remote refs. Its 20 dirty entries are additional uncommitted work. Native SDK candidates for Android, RN's Android prerequisite and iOS have local-filesystem origin URLs; a push to their current origin would not publish to GitHub. Reconcile authentic upstream routing before eventual authorised publication.

## Additional shared/platform WIP

| Worktree | Verified local state | Handling |
| --- | --- | --- |
| rum-241-flutter-ci-candidate | Four entries: launcher failure/readiness handling, retry tests, new failure tests and Flutter docs | Preserve and reconcile before a new Flutter driver repair. No complete native pass inferred. |
| rum-241-native-ci-candidate | Two modified files: RN iOS project registration (+9 lines) and docs (+7) | Preserve generated Swift service-registration integration; separate from shared KMP repair. |
| ci235-platform-filter-20261120 | Portable configuration module filtering/doc edits plus a new focused filtering regression | Overlaps WS-01 inherited-marker work and browser #235; reconcile before duplicating. |
| ci230-lint-auth-20261120 | Three modified submodule checkout/update helper scripts | Existing candidate relevant to checkout/auth routing; no permission to change identities or bypass authentication. |
| ci241-maui-20261123 | Modified lint/maui.sh | Local lint-only cleanup, not a compiled MAUI flags result. |
| ci-native-builds-20261120 | KMP diagnostic driver and test edits | Older overlap with already pushed #244; not automatically a new deliverable. |
| rules-fixtures | Sixteen status entries: old fixture/converter/resource experiment | Historical prototype overlapping later published rules resources; inspect deltas before salvage. |
| ci76-fixture-refresh-20261120 | Historical staged corpus refresh with three unresolved generated-resource conflicts | Conflict/reconciliation copy, not a ready activation branch. Do not cherry-pick or overwrite current corpus blindly. |
| web-offline-rules | Seventeen entries of old Web offline/proto/loader work | Historical precursor to merged #221; useful evidence, not a new missing feature by itself. |
| pr138 | Uncommitted proto/feature_flags.proto edit | Reconcile with the current shared IPC schema and RN stack before reuse. |
| flex-corpus-reasons-pin / web-offline-pr | Dirty corpus gitlinks; former also has dependency-directory artifacts | Separate actual pin change from generated/dependency artifacts. |

The FIT primary checkout also has a changed browser SDK gitlink and untracked configuration/planning/test artifacts. Other SDK worktrees contain unrelated Mobile SDKs/readiness/review work: they were observed by repository-level status enumeration but are not attributed to FLEX deliverables by this report. Raw inventory remains coordinator-local.

## Already published and historical distinctions

The clean codex/fit-fixture-refresh-20261120 branch exists remotely at its local head 7360506efa0d7995aea304e4fdad025b744596c4. Do not continue describing it as unpushed. Local branch-name absence alone does not prove unique commits are unpublished: older branch commits can be merged or reachable through other branches. Only the shared ea6b6dc commit above is called unpushed after refreshed-reference comparison. Deleted temporary worktrees are not recoverable dirty backups merely because an old chat links them.

## Next handling

1. Reconcile WS-01 with portable-test filtering and checkout-helper candidates; preserve its ownership and use exact portable change requests when remote workers cannot read local worktrees.
2. Reuse the native package rather than reimplementing each adapter. Snapshot/compare dirty SDK/provider overlays before moving them; no cleanup or reset is authorised by this scan.
3. Recover the parser investigation from its brief and compare with current Android SDK/prerequisite code before deciding whether any implementation remains missing.
4. Give each salvageable candidate an owner and current base/dependency/test receipt. A candidate becomes ready only when explicitly handed off with verified checks/exclusions; then conduct the mandatory local Crucible review under CONTROL-003.

No activation branches, implementation commits, PRs, tickets, cleanup or source edits were made by this scan. Only coordination documentation is published separately. Git remote metadata was refreshed to check publication; dirty work was preserved. Workspace WS-01 remains an independent active implementation; it was not audited as completed WIP here.

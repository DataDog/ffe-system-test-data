# FLEX-FIT Control Branch

Repository: **DataDog/ffe-system-test-data**. Branch: **typo/flex-fit-control**. Folder: **flex-fit-control/**. Updated November 27, 2026.

This branch is the team's authoritative coordination home for the FLEX platform × deployment-mode matrix. FLEX means FLagging EXpectations within RUM Framework Integration Testing. **Do not open a PR for this branch. Do not put implementation or fixture activation changes on it.**

## Read in this order

1. [Instructions.md](Instructions.md) — current assignments, authority, activation/exclusion workflow and communications. Current revision: CONTROL-001; setup/acknowledgement only.
2. [goal.md](goal.md) — full matrix, existing tickets/PRs and activation audit. November 27 status snapshot; refresh mutable state before implementation.
3. [REFERENCE.md](REFERENCE.md) — source contract, baseline revisions and known integration pitfalls.
4. [WORKSTREAM.md](WORKSTREAM.md) — ownership, implementation receipts and SDK defect/exclusion ledger.
5. [REQUESTS.md](REQUESTS.md) — requested diffs/implementation changes for repositories a contributor cannot access.

## Location and communication

- Branch: https://github.com/DataDog/ffe-system-test-data/tree/typo/flex-fit-control/flex-fit-control
- Team channel: https://dd.enterprise.slack.com/archives/C0CKGQ8T483
- Mention @Datadog when notifying BitsCode. Commit and push instruction changes first, then send their links and instruction revision in Slack. BitsCode reads specifications from this branch and posts progress in the channel.

## Access decision

BitsCode verified read access to this repository on November 27: main HEAD fe24ed2c4872bf109b0c71ffb2229152d76b8963 and an actual read of top-level README.md. It separately reported GitHub MAINTAIN and read_only=false on its managed attachment. Its actual push ability has not yet been exercised. The coordinator has independently verified push permission; this branch's publication establishes the coordinator's write path. FIT fallback is unnecessary unless BitsCode later reports a concrete limitation.

Access probe and response: https://dd.slack.com/archives/C0CKGQ8T483/p1795797629289759 and https://dd.slack.com/archives/C0CKGQ8T483/p1795797775823789 .

## Current user decisions

Activate the imported corpus directly during development. Investigate and record every SDK defect/gap before appropriately scoped skips or xfails. SDKs do not have to pass every fixture. Once locally green with declared exclusions, implementors may push activation branches. **No activation PRs yet**; consolidate platform rows later where practical. Existing PRs/WIP stay intact until their assigned owner reconciles them. Current setup does not dispatch implementation.

Keep this branch current as goals, instructions, references and results change. Fetch/rebase or serialise documentation writes and never force-push over another contributor. The coordinator independently validates implementation and exclusion rationale.

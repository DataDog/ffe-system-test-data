# BITS-02 — generated rules-resource catalogue audit

CONTROL-047, November27,2026. Owner: BitsCode. Read-only prerequisite audit; no platform mode execution or new implementation assignment.

Inventory the public ffe-system-test-data repository’s existing generated rules artifacts and the open/merged work that produces them. Identify the exact canonical source UFC, converter, generated protobuf payload and serialized ConfigurationWire artifact, manifest/digests, paired evaluation cases, omissions and supported encodings. Distinguish authoritative generator output from examples or outdated files. Confirm whether configuration-wire.json is the exact serialized SDK initialization input and how its encoding is represented; do not parse/reserialize it to produce a replacement.

Return a concise portable audit document on a separate branch in this repository, with source/artifact paths, relevant PR links, producer commands, stable digests or manifest relationships, and any missing generation/pairing work. Do not change canonical expectations, fixtures, generated resources, activation flags or the Control Branch. A documentation-only audit branch is not an activation branch. No PRs or tickets. Link your audit and report findings in the channel, tagging the coordinator as applicable.

The coordinator’s local agent separately owns FIT serving/SDK-fetch contract audit; do not duplicate or implement that lane. Do not publish internal FIT source or patches in this public repository. BitsCode cannot run the FIT suite; request any required local/workspace execution through the channel and reference this assignment. No new Python serializer, IPC-server serializer or generic RPC rewrite is assigned. Later platform modes remain gated on each row’s independently accepted online-precomputed cell.

## CONTROL-053 handoff checkpoint

Audit reported locally complete; remote branch unavailable and its automatic approval review rejected a required metadata step. Do not retry the rejected action. If branch-only publication remains unavailable, paste the public audit document in numbered bounded replies to the existing handoff thread so coordinator can preserve it in the authorised Control Branch. Preserve exact content and patch identity. Coordinator has independently verified the key canonical resource/omission/optional-suite/PR86-staleness findings in [BITS-02-VERIFICATION.md](../BITS-02-VERIFICATION.md). No new implementation or PR assignment.

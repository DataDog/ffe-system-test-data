# Workstream, implementation receipts and SDK gaps

Updated November 27, 2026. Initial control setup only. No implementor has been dispatched by CONTROL-001. The November 27 inventory in goal.md is the baseline; its historical checks are not new validation.

## Ownership and assignments

| Work | Owner | State | Next action |
| --- | --- | --- | --- |
| Control setup and matrix coordination | Codex coordinator | Initial control files pushed; signed commit verified | CONTROL-001 acknowledgement requested; implementation remains unassigned |
| BitsCode | Unassigned implementation scope | Main-repo read verified; control acknowledgement pending | Read CONTROL-001 and report fetched revision/access |
| Platform rows | Await coordinator assignment | Preserve existing WIP and owners | Reconcile dependencies before fanout |

## Control publication receipt

The coordinator pushed the six initial documents on typo/flex-fit-control and verified the signed commit and matching remote revision. Local Markdown links resolve and no machine-local paths were published. Documentation only; fixture content and implementation code are unchanged. No PR was opened.

BitsCode notification and acknowledgement request: https://dd.slack.com/archives/C0CKGQ8T483/p1795797929001209 . Instructions remain CONTROL-001 (setup only). BitsCode's main-repository read is verified; its actual Control Branch read/push path awaits acknowledgement.

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

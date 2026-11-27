# BITS-01 — Browser online precomputed

Owner: BitsCode in the designated Slack channel. Revision CONTROL-005, November 27, 2026. Tyler explicitly authorised goal execution. Read Instructions.md, REFERENCE.md, goal.md and WIP-INVENTORY.md before acting.

## Scope and ownership

Complete the Browser online-precomputed cell first. Existing core browser IPC executor and Playwright harness establish source eligibility; fresh runtime execution remains required. Own browser-specific feature-flag adapter/scenarios, applicable corpus activation and focused checks for this cell. You are not alone: preserve existing work and do not edit WS-01-owned CI selection/checkout or marker implementation. Shared runner/proto changes need a bounded request to the coordinator before editing so native owners do not collide. Do not implement offline or rules modes yet.

First verify actual access to DataDog/rum-sdk-integration-test-framework and the Control Branch with the configured identity. If FIT is inaccessible, record an exact request through REQUESTS.md or a BITS-01-specific request document on this branch and report the blocker in Slack. Do not implement a replacement harness in the corpus repo. Actual push permission remains unproven until used; no credential workarounds.

Reconcile existing main and PRs #231/#234/#235, fixture pin work and applicable SDK capabilities rather than duplicating their changes. Preserve independent exposure/evaluation/RUM controls. Verify whether the selected Browser SDK contains the FFLSDK-292 numeric fix, reproduce the three existing numeric quarantines and remove only obsolete skips after passing execution. Inspect all applicable online-precomputed core/dependent/plain/obfuscated/rejection cases and nested filters; do not infer completeness from top-level eligibility. Identify missing capabilities/consumer paths explicitly.

## Verification and delivery

Edit the imported corpus directly during development where activation is needed. Run selected cases through the real browser IPC/provider/FlagServer/intake path; record selected, excluded, executed, passed, failed and xfail counts and exact FIT/corpus/SDK revisions. Investigate every failure. Record SDK defects in a portable workstream before narrow supported exclusions, retaining canonical expectations and re-enable conditions. Environment failures are blockers, not SDK xfails. Follow repository instructions and signing/publication gates. Once locally green with declared exclusions, push activation branches for changed repos, no PRs. Hand off exact bases/heads/dependencies and commands/evidence for independent coordinator local Crucible review. Online-precomputed acceptance precedes later-mode assignments.

Use BITS-01-specific evidence/request files on the Control Branch to avoid central-document write races. Fetch/reconcile before pushing; never force-push. Report progress and blockers in Slack, tagging Datadog where appropriate; the Control Branch is the specification source. No PRs, tickets, external reviews or CI triggers as side effects.

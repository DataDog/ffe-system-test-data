# Java implementation report

The signed SDK commit is `a4d3dfb21cec0658417d4f3842dc8c8465a27371`.
The parent signed the ordinary merge with master `3718fdc518506e5700df8b7d448639971cd3470c`.
No source changes remain in this agent's local worktree.

- Both production parsers retain an invalid activation marker. They parse activation once during configuration ingestion.
- Both evaluators check all allocations before selection. Malformed activation returns `PARSE_ERROR` only for future mode with a valid cutoff.
- Both evaluator loops skip the exclusion helper when the cutoff is absent. This covers disabled mode and an absent attribute.
- Both helpers classify only `Boolean.TRUE` as randomization. Omitted and null `doLog` retain Java ordinary-allocation compatibility.
- Legacy bootstrap constructors remain compatible. Capability checks protect new field access when an older agent supplies the bootstrap class.
- Both README files describe future-only malformed-activation errors.
- Canonical fixture tests now run 28 immediate and 44 future cases at fixture commit `8c4d2410aa643aa6b97c8547ae5fe358c46b7f6f`.
- Legacy canonical tests now use the production parser. Their removed parser copy rejected a valid split.features fixture.

The central model remains unchanged at `0520866bedb8c059df9c493cfe27ad294390c603`.
Each native adapter executes all 90 Java policy cases. Each external operation probe executes all 36 call-count cases.
The policy adapter verifies the corpus hash, profile hash, case count, unique IDs, and exact selected ID set.

Exact-commit native checks passed: standalone 1251, legacy API 838, parser library 365. There were no failures or skips.
Scoped formatting checks and agent/provider artifact builds passed. Both operational replays passed all 36 cases.

Negative controls detected each regression in both implementations:

| Mutation | Failed tests per implementation |
| --- | ---: |
| Apply malformed-activation error in every mode | 13 |
| Restore `Boolean.FALSE.equals(doLog)` | 2 |
| Remove the inactive call-site guard | 15 |

All mutations were restored. Full suites passed after restoration. A later exact-commit run also passed.

Java retains its existing timestamp grammar. This work does not adopt browser grammar differences.
D015 remains scoped: Java provider disablement keeps its existing initialization exception lifecycle.
D010 remains unchanged. Omitted/null compatibility is a Java-local `no_shared_impact` review disposition.

Runtime validation uses an isolated system-tests checkout at `abe62eb21f53adba0d8ac038fe0539f8f05fb124` plus saved harness changes.
Both production paths passed five runtime tests. Each run evaluated all 90 policy cases through OpenFeature.
Legacy uses Remote Configuration. Standalone uses its public HTTP configuration source with a JSON:API envelope.
Both runs observed one exposure after three retained-experiment evaluations. Enabled evaluation telemetry reported three retained evaluations and one control.
Suppressed evaluation telemetry reported only the control evaluation. Exposure delivery remained unchanged.
The receipts bind the signed source, provider artifacts, embedded provider, installed agent, capture images, and adapter hashes.

The stock test agent lacks the flagevaluation route. The local capture image adds that route through its existing request capture handler.
Standalone uses a local TLS intake with a test certificate. This checks public HTTP delivery without production credentials.
The signed standalone baseline has no compatible Remote Configuration bridge. Its RC run returned `PROVIDER_NOT_READY`.
This inherited capability boundary does not change the opt-out implementation. Runtime validation uses its supported agentless path.
Earlier failed harness attempts remain in the evidence. No SDK source change was needed for the final runtime passes.

Java timestamp grammar and provider disablement lifecycle remain scoped differences. No new fleet grammar decision was made.
No staging, production, hosted CI, publication, or merge-readiness claim is made by this report.

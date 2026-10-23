# Java SDK adoption evidence

The tested SDK commit is `DataDog/dd-trace-java@a4d3dfb21cec0658417d4f3842dc8c8465a27371`.
The central contract pin is `0520866bedb8c059df9c493cfe27ad294390c603`.
The source comparison verified 12,309 Git blobs. No tracked source differences remained during final validation.
The implementation preserves Java timestamp grammar and the existing disabled-provider lifecycle.

## Results

| Check | Result |
| --- | --- |
| Standalone native module | 1,251 passed; 0 failed; 0 skipped |
| Legacy API native module | 838 passed; 0 failed; 0 skipped |
| Parser library native module | 365 passed; 0 failed; 0 skipped |
| Pinned policy profile | All 90 cases passed in each native implementation |
| Operational profile | All 36 cases passed in each implementation |
| Legacy runtime through Remote Configuration | 5 passed; 0 failed; 0 skipped; all 90 policy cases exercised |
| Standalone runtime through HTTP configuration and TLS intake | 5 passed; 0 failed; 0 skipped; all 90 policy cases exercised |

The native module totals include the 90 policy cases per implementation. They exclude the separate operational probes.
Each runtime includes omitted/null `doLog` checks and flag-wide malformed-activation checks.
For each implementation, three retained-experiment evaluations produced one exposure.
Enabled telemetry reported three retained evaluations and one ordinary control evaluation.
Suppressed telemetry reported only the control evaluation. Exposure delivery remained unchanged.
These assertions cover delivered intake payloads and exposure deduplication.

## Evidence boundaries

`final-native/receipt.json` reports module counts. Native JUnit files retain policy and operational receipts.
`case-observations.json` lists the native case IDs that passed.
`operation-observations.json` records actual helper-call counts, helper results, and post-policy allocation eligibility.
The probe observes `isAllocationActive` entry after the opt-out gate. All probe allocations have empty splits and no active-window restriction.
This lets the probe observe every retained allocation without selecting a value early.
All 36 observed results match the pinned operational corpus in each implementation.
The probe measures native control flow. It makes no timing or benchmark claim.

`runtime/summary.json` reports the runtime outcomes. Each runtime receipt binds the SDK, harness, adapter, images, and artifact hashes.
The runner extracts the embedded provider and installed agent from the actual client image. Their hashes match the signed-source artifacts.
The runtime harness base is `DataDog/system-tests@abe62eb21f53adba0d8ac038fe0539f8f05fb124`.
The harness has isolated, uncommitted test changes. Both final runs use the same adapter hash.
The Java application runs on JDK 21 in Linux amd64 containers.

The stock test agent lacks `/evp_proxy/v2/api/v2/flagevaluation` capture.
The test-only image adds this route to its existing event capture handler.
Standalone HTTP uses a local JSON:API endpoint and a local TLS intake with a test certificate.
No production credentials or production endpoints were used.
These tests prove SDK delivery to local intake fixtures. They do not prove backend schema acceptance, staging, or production operation.

The standalone baseline has no compatible Remote Configuration bridge.
Its `AgentBridges.detect()` returns `NONE`, and the signed agent has no bridge instrumentation for this API.
Its RC attempt returned `PROVIDER_NOT_READY`. The final standalone run uses its supported agentless path.
`runtime/standalone-rc-boundary/` retains the exact invocation, failed receipt, JUnit output, and unchanged baseline source evidence.
Earlier failed harness attempts are recorded in `runtime/earlier-attempts.json`.
No SDK source change was required for the runtime setup corrections.

## Review disposition

The independent audit was frozen before reading the review snapshot.
The sole comment is `4342792807`, thread `PRRT_kwDOBVFpxM6u-76S`.
The accepted fix uses `!Boolean.TRUE.equals(allocation.doLog)` in both helpers.
Omitted/null compatibility is Java-local `no_shared_impact`.
D010 remains unchanged. Its formal domain uses valid booleans and does not define malformed-field defaults.
The parent owns the full Lean-style reply and publication.

Negative controls reverted D004 scoping, the `doLog` predicate, and the D017 call-site guard.
They failed 13, 2, and 15 tests per implementation, respectively.
`negative-controls.json` binds the unchanged production-file hashes.
`negative-control-adapters/` preserves the original operation probe used for the mutation checks.
The final operation probe adds observations of helper results and post-policy allocation eligibility.
All mutations were restored before the final clean-source validation.

## Reproduction

Use an isolated checkout at the exact SDK commit and canonical fixture pin `8c4d2410aa643aa6b97c8547ae5fe358c46b7f6f`.
Use the repository wrapper and configured toolchains. Limit Gradle to two workers.
The remote environment needed the public Maven mirror option shown below.

```sh
./gradlew :dd-openfeature:test :products:feature-flagging:feature-flagging-api:test :products:feature-flagging:feature-flagging-lib:test --max-workers=2 -PmavenRepositoryProxy=https://maven-central.storage-download.googleapis.com/maven2
```

Update the workspace paths in `adapters/operations.init.gradle` before replaying the external operation probes.
The operational corpus and both probe sources are included.
The signed repository contains the native policy tests and pinned resource files.

For runtime reproduction, use an isolated system-tests checkout at the recorded harness SHA.
Apply the appropriate runtime harness patch. Copy the final Python adapter and pinned policy cases into the harness.
The patches reference the separately included Maven settings file and a test TLS truststore.
Build the test-agent overlay from `runtime/adapters/capture-agent.Dockerfile`.
Generate a local test certificate and truststore for the standalone fixture.
Use certificate names `event-platform-intake.java-optout-gw0.test`, `event-platform-intake.java-optout-gw1.test`, and `event-platform-intake.java-optout-master.test`.
The public certificate used here is included. The private test key and binary truststore remain in the isolated evidence workspace.
Build the standalone fixture from `runtime/adapters/standalone-backend.Dockerfile`.
Update workspace paths in `runtime/adapters/run_runtime.py`, then execute both variants.
The runner binds copied jars and client image contents to the receipts.

Build artifacts and full logs remain outside this export. `logs-retained-manifest.json` records their log hashes and location.
No SDK branch push, PR comment, or PR state change was performed by this sub-agent.

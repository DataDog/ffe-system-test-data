# KMP and MAUI online-precomputed prerequisites

CONTROL-035, November27. Source-backed prerequisite brief, not an implementation dispatch. Existing core IPC is eligible on both native hosts for each row; neither row is deferred under the missing-core policy. SDK feature support, FIT integration and runtime conformance remain separate.

## KMP

FIT pins published common SDK1.6.0, Android native3.9.0 and iOS3.12.0. Fresh upstream developc5608b842e1135c928280cc5eb3a20a25a6d8b2d complete recursive tree1060entries is not truncated and has no flagging/OpenFeature module/API. Current upstream native dependencies3.16.0/3.21.0 do not themselves expose a common KMP flag API. [Verified upstream source](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/tree/c5608b842e1135c928280cc5eb3a20a25a6d8b2d).

A real common flags wrapper/provider is prerequisite to KMP SDK conformance. Then add the common app adapter and native IPC registration/generated bindings, align native dependencies with WS-02/WS-04 and avoid duplicate iOS core linkage across package managers. Reusing direct native services may produce separately labelled native-host evidence, but cannot close the KMP SDK API slice. Existing delivery tracking: FFLSDK-143.

## MAUI

Pinned clean SDKa44ba752694d09c29d1d542d26b392833f03a1a9 has no flagging wrapper/native binding dependencies. FIT declares Datadog.Maui0.1.0 while pinned SDK builds0.2.0; restored application identity is unverified. Pinned native versions are Android3.14.0/iOS3.17.0.

Prerequisite ownership must cover native Android/iOS flagging wrappers/bindings and a unified .NET flags API, including five typed results/details, actual reason/error/variant/metadata, context/readiness, custom configuration/intake endpoints and repeatable non-destructive emission draining. Then add FeatureFlagService messages/dispatch to existing HTTP IPC and reconcile exact resolved package/native identities. Existing generic Android flush shuts down SDK executors and must not be reused within a continuing flag lifecycle. Existing tracking: FFLSDK-147.

## Verification and boundaries

Implementations must invoke the framework SDK's real flags API rather than manufacture evaluator behaviour or label direct native calls as framework conformance. Activate imported corpus during development, start with all-types smoke, then full online-precomputed inventory separately on Android/iOS. Capture exact loaded source/package identities, configuration POST/context, typed details, exposures/evaluations and investigated host-scoped exclusions. Independent Crucible review remains required. No runtime proof currently exists for either row; no later modes are assigned.

Native Android can build in the workspace; iOS requires macOS/Xcode and package-manager alignment. MAUI additionally needs .NET10 MAUI workloads and matching Xcode. Budget disk before native builds. PR244 remains separate KMP compatibility infrastructure. No new tickets/PRs or SDK prerequisite implementation are opened by this brief. Internal source traces remain coordinator-private.

## CONTROL-057 concrete SDK design follow-through

[BITS-03](BITS-03-FRAMEWORK-FLAGS-PREREQUISITES.md) is assigned read-only file-level API/bridge/test implementation briefings for both prerequisites. Coordinator refreshed current KMP develop c5608b842e1135c928280cc5eb3a20a25a6d8b2d and MAUI develop 817c77cace2c8d85a798da9f06628268f4b1db21, full non-truncated trees and open PR lists; no open flagging prerequisite was identified. Full API/interop inspection remains part of BITS-03. Tickets FFLSDK-143/147 and parent109 were read; no ticket mutation or SDK implementation is assigned. Preserve older pinned identities above as inventory.

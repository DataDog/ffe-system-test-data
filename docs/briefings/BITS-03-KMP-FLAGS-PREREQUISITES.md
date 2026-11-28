# BITS-03 — KMP flags SDK prerequisite briefing

27 November 2026. Read-only proposal under
[CONTROL-057 assignment](https://github.com/DataDog/ffe-system-test-data/blob/ae2b5ac9f98068abb2a508c9e63e0fc61e863510/flex-fit-control/assignments/BITS-03-FRAMEWORK-FLAGS-PREREQUISITES.md)
, with CONTROL-058 steering read. No SDK/FIT changes, builds, dependency changes, devices, PRs, tickets or
publication were performed. Role names below describe prospective ownership, not dispatched work. Existing
core IPC is eligible; this SDK prerequisite is separate from it.

## Source identity and existing work

Read access succeeded through attached public checkouts. KMP `develop` is
**c5608b842e1135c928280cc5eb3a20a25a6d8b2d**. Its build version is `1.10.0-dev`; the version constructor in
`ProjectConfig.kt`, rather than a restored FIT package, establishes this source identity.
[Native catalogue](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/blob/c5608b842e1135c928280cc5eb3a20a25a6d8b2d/gradle/libs.versions.toml)
pins Android **3.16.0** and iOS **3.21.0**, Kotlin 2.2.21, JDK 21 and AGP 9.2.1. Android min/compile SDK are
23/36; Apple minimum is 15. These native versions contain flags modules, but adding them does not establish a
working common API or binary compatibility.

Exact inspected native tags resolve to Android `dad2312223110e2e7ed84cf46cefe3a45bc759c6` and iOS
`36ca2cfdf8e02a2753fd66f6dbdd2a065a84e412`. Current native develop snapshots were also checked: Android
`4831b6cd2c5c612841ddd3013c95ba2597dd68ec`, iOS `bae6efb89717e7e30eb143fc84963d5cee0e4f2f`. Those are
informational, not selected upgrades. Newer Android source still has string-only attributes and no Long
resolver, although numeric conversion/error behavior has evolved. Do not project newer behavior onto pinned
artifacts.

The coordinator's older FIT inventory is KMP 1.6.0 / Android 3.9.0 / iOS 3.12.0. It is not the source audited
here; no dependency restore or loaded-binary identity was measured.
[Prior inventory](https://github.com/DataDog/ffe-system-test-data/blob/ae2b5ac9f98068abb2a508c9e63e0fc61e863510/flex-fit-control/assignments/KMP-MAUI-PREREQUISITES.md).

Inspection covered registered modules, common and platform declarations, all checked-in API surfaces, native
aliases, and bridge/build infrastructure. `settings.gradle.kts` registers core, Logs, RUM, Session Replay,
WebView and integrations; no Flags module/provider is registered. Existing
`RumMonitor.addFeatureFlagEvaluation(s)` annotates a view with an already supplied value. It does not fetch
assignments, resolve values, report evaluation details, or supply a flags provider. See
[common RUM surface](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/blob/c5608b842e1135c928280cc5eb3a20a25a6d8b2d/features/rum/api/commonMain/apiSurface).

Provider inventory returned 347 PRs with a 500-record limit; all titles/branches/states were inspected. The
only open PRs are [#364](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/pull/364), Ktor tracing
default, and [#51](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/pull/51), credentials. Both
complete file lists were read; neither supplies this prerequisite. Merged
[#359](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/pull/359) updated native pins and explicitly
made no KMP public API change. Merged [#337](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/pull/337)
supplies the existing SPM build pipeline. No implemented KMP flags facade/OpenFeature provider was found. This
is not an audit of every historical PR discussion or unpublished branch.

## Guidance and decisions before implementation

Read the full
[AGENTS.md](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/blob/c5608b842e1135c928280cc5eb3a20a25a6d8b2d/AGENTS.md)
and
[CONTRIBUTING.md](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/blob/c5608b842e1135c928280cc5eb3a20a25a6d8b2d/CONTRIBUTING.md)
, plus the linked `sdk-tests`, `sdk-feature-knowledge` /KMP reference, `sdk-native-update`, and validation
guidance in `sdk-pr-prepare`. Only their investigation/design guidance was used; no preparation workflow was
executed. Important requirements are common/native semantic parity, no native types in common public
signatures, internal implementation types, no new SDK threads/scopes, additive ABI-conscious changes,
generated API/metadata review, and real native delegation tests.

The KMP guidance requires maintaining-team discussion, project-member approval and signed commits for future
contributions; it does not state the native iOS RFC rule as a KMP-wide approval gate. If the chosen solution
changes upstream iOS API, that repository's
[AGENTS.md](https://github.com/DataDog/dd-sdk-ios/blob/bae6efb89717e7e30eb143fc84963d5cee0e4f2f/AGENTS.md)
explicitly says: **“Do NOT introduce new public API without RFC review.”** Its
[development guidance](https://github.com/DataDog/dd-sdk-ios/blob/bae6efb89717e7e30eb143fc84963d5cee0e4f2f/docs/DEVELOPMENT.md)
also requires internal RFC approval/cross-platform alignment for relevant initialization, configuration and
data-collection changes. This briefing seeks no execution approval; owners must resolve the public shape and
bridge ownership before implementation.

## Actual native contracts and fidelity blockers

| Concern | Android 3.16.0 | iOS 3.21.0 | Consequence |
| --- | --- | --- | --- |
| Construction | `Flags.enable(config)`, `FlagsClient.Builder(name).build()` | `Flags.enable(with:)`, `FlagsClient.create(...)` | Use the existing framework-initialized core once; never initialize a second native core. |
| Context | `EvaluationContext(String, Map<String,String>)` | `FlagsEvaluationContext(String, [String:AnyValue])` | Typed Android attributes and absent versus empty subject are unresolved native-contract limitations. Never stringify/drop values or substitute identity. |
| Ready/update | callback success/failure plus observable NotReady/Ready/Reconciling/Stale/Error | completion `Result<Void,FlagsError>` plus state observable | HTTP200 or a first-flags callback alone is not readiness. Preserve stale/error and late completion semantics. |
| Typed details | generic `resolve(key, default)` yields value, variant, reason, errorCode/message, metadata | five `get*Details` conveniences yield value, variant, nullable reason, error and allocationKey | One details call per evaluation; calling value and details separately duplicates tracking. |
| Integer | Int32; converter has Int and Double branches, no Long branch | Swift Int, 64-bit on the supported arm64 targets | Full signed-int64 portable reads need native Android work first. Do not narrow a default or route integers through Double. |
| Object | JSONObject / recursive Map overload | AnyValue dictionary/array/scalars/null | Common object getter should require an object root and preserve nested numeric/boolean/null kinds. |
| Error/detail limits | four error codes at this tag; metadata is filtered native primitive data plus allocationKey | three evaluation errors; no generic metadata/serialId field | Preserve actual null reasons and unavailable fields. Missing PARSE_ERROR/GENERAL or metadata remains a gap, not a manufactured result. |

Evidence:
[Android public API](https://github.com/DataDog/dd-sdk-android/blob/dad2312223110e2e7ed84cf46cefe3a45bc759c6/features/dd-sdk-android-flags/api/apiSurface),
[context](https://github.com/DataDog/dd-sdk-android/blob/dad2312223110e2e7ed84cf46cefe3a45bc759c6/features/dd-sdk-android-flags/src/main/kotlin/com/datadog/android/flags/model/EvaluationContext.kt),
[converter](https://github.com/DataDog/dd-sdk-android/blob/dad2312223110e2e7ed84cf46cefe3a45bc759c6/features/dd-sdk-android-flags/src/main/kotlin/com/datadog/android/flags/internal/FlagValueConverter.kt);
[Swift client](https://github.com/DataDog/dd-sdk-ios/blob/36ca2cfdf8e02a2753fd66f6dbdd2a065a84e412/DatadogFlags/Sources/Client/FlagsClientProtocol.swift),
[details/errors](https://github.com/DataDog/dd-sdk-ios/blob/36ca2cfdf8e02a2753fd66f6dbdd2a065a84e412/DatadogFlags/Sources/Models/FlagDetails.swift),
[AnyValue](https://github.com/DataDog/dd-sdk-ios/blob/36ca2cfdf8e02a2753fd66f6dbdd2a065a84e412/DatadogFlags/Sources/Models/AnyValue.swift).

These pins contain the needed native modules; they are source-visible starting points, not proven
binary/corpus-compatible choices. A complete int64/typed-context contract cannot be delivered by a thin
wrapper over them. Owner choices: obtain native support first, or explicitly approve a smaller
Int32/string-attribute API and retain the unrepresentable FIT slices as uncovered. The latter must not be
presented as full portable support. Unknown/future native outcomes must retain an unsupported/raw category and
fail relevant verification, never become success. Android native defects should be one shared dependency
proposal coordinated with other consumers, not independently reimplemented in each framework.

Swift context completion distinguishes invalidResponse from networkError and initializationTimedOut; a response
rejection classification must preserve those boundaries. Android exposes a Throwable callback and a public
FlagsInitializationTimeoutException; a stable public invalid-response classifier was not established at these
pins. Carry an unclassified native failure honestly until the native owner supplies a bounded contract. Do not
classify by arbitrary exception text, assume every initialization failure rejected malformed data, or add a
reflection-based dependency on native implementation classes.

## Proposed framework API and Apple bridge

Proposed names, not existing exports or an approved mode contract:

```kotlin
// Desired full-fidelity shape; Long/typed-context support is gated above.
Flags.enable(configuration: FlagsConfiguration)
FlagsClient.create(name: String): FlagsClient
client.setEvaluationContext(context: FlagsContext, completion: FlagsContextCompletion)
client.state: FlagsStateObservable
client.getBooleanDetails(key: String, defaultValue: Boolean): FlagDetails<Boolean>
client.getStringDetails(key: String, defaultValue: String): FlagDetails<String>
client.getIntegerDetails(key: String, defaultValue: Long): FlagDetails<Long>
client.getDoubleDetails(key: String, defaultValue: Double): FlagDetails<Double>
client.getObjectDetails(key: String, defaultValue: FlagObject): FlagDetails<FlagObject>
```

Configuration needs configuration/exposure/evaluation endpoint URLs, trackExposures/trackEvaluations, native
initialization timeout and evaluation aggregation interval, with explicit units. Separate product
configuration from test-only queue barriers. `FlagsContext` must keep dedicated subject and attributes
distinct; use a typed JSON value model rather than unconstrained Any/string conversion. A nullable subject is
a desired portable input, not supported by the pinned native constructor: absent/null must be rejected as an
unsupported context before mutation/fetch until native semantics exist. Empty string must remain an actual
empty string. An attribute literally named targetingKey must not be promoted to the subject. Validate the
entire update before changing active native state.

`FlagDetails<T>` should be a constructor-controlled regular class with value, nullable reason/variant,
structured evaluation error and read-only metadata. Preserve Android native metadata and Swift allocationKey;
do not infer other metadata from fixtures or use snapshots as a substitute for evaluation. Native fallback
values/defaults and native telemetry must stay consistent. Float getters use Double, retain
finite/zero/non-finite default semantics where supported, and do not repair native rounding after evaluation.
Such postprocessing can disagree with telemetry already emitted by the native call.

Apple is a concrete build blocker:
[the pinned Objective-C surface](https://github.com/DataDog/dd-sdk-ios/blob/36ca2cfdf8e02a2753fd66f6dbdd2a065a84e412/api-surface-objc)
has an empty DatadogFlags section. Its Swift structs/enums/generic protocol are not Objective-C exports. KMP's
[generated cinterop definitions](https://github.com/DataDog/dd-sdk-kotlin-multiplatform/blob/c5608b842e1135c928280cc5eb3a20a25a6d8b2d/tools/build-plugins/src/main/kotlin/com/datadog/build/plugin/iosnative/tasks/GenerateDatadogCInteropDefsTask.kt)
use `language = Objective-C`.
[Kotlin's official interop documentation](https://kotlinlang.org/docs/native-objc-interop.html) confirms pure
Swift modules are not imported by this path. Merely registering `DatadogFlags` cannot expose FlagsClient.

Recommended review candidate: a **KMP-owned Swift bridge**, shipped as part of the SDK, with proposed
`features/flags/native/Package.swift` and `Sources/DatadogKMPFlagsBridge/FlagsBridge.swift`. It imports
DatadogFlags, delegates to the same core, and exposes NSObject client/result wrappers, five concrete typed
methods, explicit ObjC selectors and completion/listener protocols. Use Int64/Double primitives, tagged
JSON/Foundation values with explicit NSNumber Boolean/integer discrimination, and bounded structured errors.
Swift generics, Result and associated-value enums must stay inside Swift. A bridge used only by the FIT app
would not establish a shipped KMP feature.

The existing synthetic SPM target is C-only and references remote SDK products. Extend that build pipeline
deliberately to build the owned Swift bridge and generated public header; it does not already support this
local Swift target. The alternative is an upstream DatadogFlags ObjC facade, requiring native RFC/release/pin
work. Choose one owner/path, not both. Ensure a single resolved dd-sdk-ios package/core across the bridge, KMP
and final app; compare symbols and runtime initialization, not just dependency declarations.

No common Datadog OpenFeature provider exists. The Android native `flags-openfeature` provider is Android
implementation work, not an Apple-capable common provider. A future framework provider is separate work after
the genuine SDK facade; this brief does not use it to claim success.

## Dependency-ordered implementation and test split

1. **API/native owners:** settle integer width, context capabilities, result/error fidelity, bridge ownership
   and lifecycle. For full fidelity, Android prospective native sites are FlagsClient,
   model/EvaluationContext, internal/FlagValueConverter, request models/serialization, telemetry context
   schemas and their tests. A constructor-only Map type change is insufficient. Preserve binary compatibility
   through additive APIs. No native implementation is dispatched here.
2. **KMP API owner:** new `features/flags/build.gradle.kts`;
   `src/commonMain/kotlin/com/datadog/kmp/flags/{Flags,FlagsClient,FlagDetails,FlagsContext,FlagValue,FlagsStateObservable}.kt`
; `configuration/FlagsConfiguration.kt`; internal PlatformFlagsClient/configuration builders. Follow Logs'
   builder and internal PlatformLogger pattern, not a new evaluator. Common tests cover validation, immutable
   models with behavior and lifecycle mapping.
3. **Android actual owner:** `src/androidMain/.../Flags.kt`, internal AndroidFlagsClient/configuration/result
   mappers; one native generic details call per typed getter, callback/listener cancellation and same-core
   ownership. Add native Flags alias at the existing Android version in `gradle/libs.versions.toml`. Add
   narrowly owned cleartext test configuration if needed: current core native-builder mapping is in
   `core/src/androidMain/.../Datadog.kt`; common configuration exposes no allow-cleartext switch. An
   application network-security file alone may not enable native SDK HTTP.
4. **Apple bridge/actual owner:** owned Swift files above,
   `src/appleMain/.../internal/{AppleFlagsClient,NativeFlagsClientProxy,FlagValueMapping}.kt`, and Apple
   configuration actuals. Register cinterop for the bridge; link DatadogFlags/Core/Internal dependencies as
   required by actual symbols. Extend
   `tools/build-plugins/.../iosnative/{DatadogSpmBuildPlugin,DatadogFrameworksPlugin}.kt` and
   synthetic-package/build tasks only to the selected bridge design. Unit-test package generation,
   framework/header discovery and target filtering. Use existing DDRumMonitorProxy testing pattern for ObjC
   classes.
5. **Build/publication owner:** register the module in `settings.gradle.kts`, root `publishableProjects`,
   `.gitlab-ci.yml` release/test jobs and documentation. Add module API surfaces, Android/Apple compiler
   metadata and Android dependency inventory using existing tasks. `sample/shared/build.gradle.kts` must
   depend on/export the new SDK API when validating Swift consumption. Align both sample Xcode exactVersion
   references if the native pin changes. Do not hand-edit NATIVE_SDK_VERSIONS.md or generated models. Decide
   tvOS support explicitly rather than exposing a no-op common implementation.
6. **SDK verification owner:** new common/Android-host/Apple mapper, client, callback/state and configuration
   tests at the mirrored source paths. Android uses JUnit5/Mockito/Elmyr/AssertJ; common/Apple use
   kotlin.test/Mokkery and an internal native proxy. Test malformed/unknown errors, before-ready reads, empty
   flags/keys/defaults, Int32/Int64 boundaries and 2^53 precision, fractional/overflow/inexact values, nested
   objects/null, context collisions/unsupported inputs without fetch, completion races/timeouts, stale
   updates, listener cancellation and repeated calls after drain. Verify real tracking delegation exactly
   once. Prove meaningful controls fail when mapping/delegation is broken. Mock tests alone do not prove
   telemetry or linking.

Future commands, **none run here**, after the module and required native APIs exist:

```sh
./gradlew :features:flags:testAndroidHostTest
./gradlew :features:flags:ktlintCheck :features:flags:detekt
./gradlew :sample:androidApp:assembleDebug
./gradlew :features:flags:generateApiSurface :features:flags:generateCompilerMetadata :features:flags:listTransitiveDependencies
./gradlew checkGeneratedFiles
# macOS with matched Xcode/Kotlin toolchain and iOS SDK (3.19+ needs Xcode 26):
./gradlew :buildDatadogFrameworks
./gradlew :features:flags:iosSimulatorArm64Test
./gradlew :sample:shared:compileKotlinIosSimulatorArm64
```

API/metadata tasks modify tracked generated files and checks compare against HEAD; future owners must
inspect/commit intended outputs in their authorized workflow. Add tvOS compile/tests only if selected. Linux
can test common/Android mapping, JVM behavior and build-plugin output; it cannot establish Apple
cinterop/header/link/Swift consumer/runtime proof. Android device proof requires an owned device and the exact
framework artifact, not just host tests. Sample APK launch may use `adb -s DEVICE_SERIAL install -r APK_PATH`
and `adb -s DEVICE_SERIAL shell am start -n APP_COMPONENT` after verifying the actual output/component; do not
guess an application ID or use another lane's device. No such command was run.

## Telemetry, safe observation, and later FIT integration

Actual path: context update → native precomputed POST → native repository/state → one native typed-details
call → native exposure dedup/doLog path and native evaluation aggregation → native storage/upload → dedicated
configured intakes. Android exposes `useCustomFlagEndpoint`, `useCustomExposureEndpoint`,
`useCustomEvaluationEndpoint`, `evaluationFlushInterval` (milliseconds, clamped 1–60s). Swift equivalents are
customFlags/Exposure/EvaluationEndpoint and evaluationFlushInterval (seconds). Respect consent and native
source/version metadata; RUM view annotation alone is not an exposure/evaluation receipt.

For repeated cases, never call stopInstance, clearAllData or flushAndShutdownExecutors as an intermediate
flush. First use native aggregation interval plus frequent upload settings and bounded collector waits,
preserving the SDK and observing a complete post-evaluation quiet interval. This is observation, not a
deterministic queue-empty guarantee. Native Android `EvaluationEventsProcessor.flush()` and Swift
`EvaluationAggregator.sendEvaluations()` are internal; no shipped common barrier exposes them. Strong
deterministic draining needs a separately reviewed **verification-only** asynchronous barrier that drains
aggregation, waits for event-write completion, then storage/upload completion without shutting down executors.
Prospective native sites are those classes plus SDK-core queue hooks; wrappers alone cannot truthfully promise
this at the inspected pins. Swift core SPI flush is non-destructive but does not itself establish that the
private flags aggregation has been emitted. Keep blocking work off the UI/main thread. Prove drain → another
context update/read/upload works; deadline/network errors must remain failures. Native named-client
retention/cache/dedup means unique unbounded client names are not a reset strategy; repeated-process isolation
is a fallback until reset/isolation behavior is proven.

After the SDK exists and is approved, coordinator-owned FIT integration should consume the **common facade**
through the existing eligible IPC. Privately reconcile generated service registrations and app dependency
pins; no internal FIT source is included here. Online-precomputed first: all-types smoke on Android/iOS, then
the entire imported applicable corpus unchanged. Capture exact framework/native source and loaded artifacts,
configuration POST body/context/HTTP status, one typed RPC result/details per evaluation and real intake
events/counts. Distinguish bridge/API gaps, native SDK gaps and harness failures. Do not count arbitrary
transport/timeouts as malformed-response rejection or create blanket skips. Require independent local Crucible
review and aggregate/publication gates before cell acceptance. No later mode or init-schema migration is
assigned. Existing tracking is FFLSDK-143 under FFLSDK-109; no new ticket is proposed or filed by this
briefing.

Validation of this briefing: read-only source/API/pin and provider-PR inspections only. No compilation,
dependency resolution, generated header/binary inspection, SDK unit/runtime tests, FIT execution or empirical
native compatibility result is claimed.

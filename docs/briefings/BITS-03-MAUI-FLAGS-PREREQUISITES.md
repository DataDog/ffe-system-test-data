# BITS-03 — MAUI flags SDK prerequisite briefing

27 November 2026. Read-only proposal under
[CONTROL-057 assignment](https://github.com/DataDog/ffe-system-test-data/blob/ae2b5ac9f98068abb2a508c9e63e0fc61e863510/flex-fit-control/assignments/BITS-03-FRAMEWORK-FLAGS-PREREQUISITES.md)
, with CONTROL-058 steering read. No SDK/FIT implementation, builds, devices, dependency changes, tickets,
PRs, commits or publication were performed. Prospective ownership below is a plan, not a dispatch. Existing
MAUI core IPC is eligible; native bindings and a real framework flags API remain separate prerequisites.

## Source/package identity and existing work

Read access succeeded to public `DataDog/dd-sdk-maui`, `develop`
**817c77cace2c8d85a798da9f06628268f4b1db21**.
[versions.properties](https://github.com/DataDog/dd-sdk-maui/blob/817c77cace2c8d85a798da9f06628268f4b1db21/versions.properties)
and the actual projects declare SDK **1.0.1**, Android native **3.15.0**, iOS native **3.19.0**. Android
wrapper Gradle dependencies and all native binding versions align with that inventory. The iOS wrapper
Package.swift pins exactly 3.19.0. These tags resolve to Android `83deee17bb68d64a61dd12d626ef112b028f41e0`
and iOS `61348d738e15d8418226e923e9db3bd6a97d1e00`.

[Datadog.Maui.csproj](https://github.com/DataDog/dd-sdk-maui/blob/817c77cace2c8d85a798da9f06628268f4b1db21/bindings/Datadog.Maui/Datadog.Maui.csproj)
publishes `Datadog.Maui` and targets net9.0-ios/android and net10.0-ios/android, with minimum iOS15 /
Android23.
[global.json](https://github.com/DataDog/dd-sdk-maui/blob/817c77cace2c8d85a798da9f06628268f4b1db21/global.json)
selects .NET10.0.100 with latestFeature roll-forward. The same SDK builds the net9 targets; do not assume a
.NET9-only toolchain is sufficient.

The coordinator's earlier FIT inventory is a different source, `a44ba752694d09c29d1d542d26b392833f03a1a9`,
building 0.2.0 while the app declares 0.1.0, with native Android3.14.0/iOS3.17.0. No restored package identity
was verified here. Updating a source checkout alone cannot settle this: a future integration receipt must
record selected NuGet source/version/hash, project.assets.json and actual assembly/native versions.
[Prior public inventory](https://github.com/DataDog/ffe-system-test-data/blob/ae2b5ac9f98068abb2a508c9e63e0fc61e863510/flex-fit-control/assignments/KMP-MAUI-PREREQUISITES.md).

Inspection covered C# public declarations, all binding csproj/ApiDefinition registrations, Android wrapper
Gradle dependencies/exports and Swift wrapper package/source. The framework exposes core, logs, RUM, tracing,
Session Replay and related helpers; neither flags construction/evaluation nor a framework OpenFeature
provider/binding dependency was found. RUM APIs and incidental fields named flags are not a flags client. iOS
Package.swift includes six other native products but no DatadogFlags; the Android wrapper and C# binding
projects likewise omit flags.

Provider inventory returned 100 PRs under a 200-record limit. All titles/branches/states were inspected; the
sole open PR [#106](https://github.com/DataDog/dd-sdk-maui/pull/106) concerns mapping-build IDs, and its
complete file list contains no flags feature. Relevant merged work:
[#88](https://github.com/DataDog/dd-sdk-maui/pull/88) sets current native pins,
[#104](https://github.com/DataDog/dd-sdk-maui/pull/104) releases1.0.1,
[#44](https://github.com/DataDog/dd-sdk-maui/pull/44) provides the Session Replay vertical-slice pattern, and
[#46](https://github.com/DataDog/dd-sdk-maui/pull/46) adds the existing Flush command. No delivered flags
prerequisite was found in current source/open files. Historical titles were screened; every historical
discussion/unpublished branch was not audited.

## Guidance and design decisions

Read full
[AGENTS.md](https://github.com/DataDog/dd-sdk-maui/blob/817c77cace2c8d85a798da9f06628268f4b1db21/AGENTS.md)
and
[CONTRIBUTING.md](https://github.com/DataDog/dd-sdk-maui/blob/817c77cace2c8d85a798da9f06628268f4b1db21/CONTRIBUTING.md)
, applicable SPEC architecture/bridge/testing/version sections, actual build/check scripts, test project
registrations and CI. No project SKILL.md was found. Existing examples contain stale filenames/counts; actual
csproj/source/scripts establish current exports and commands. In particular, CONTRIBUTING describes swift
test, while check.sh correctly uses an iOS-simulator xcodebuild test because the full wrapper imports
UIKit-dependent RUM.

Existing guidance requires Objective-C-compatible NSObject exports with matching C# selectors, JVM-compatible
methods, one place for each dependency, cross-platform parity, three-layer tests and example proof. It
contains no explicit MAUI RFC gate. New product names/contracts still need maintainer agreement; this
read-only assignment authorizes none. If the solution instead changes upstream iOS public API, its
[AGENTS.md](https://github.com/DataDog/dd-sdk-ios/blob/bae6efb89717e7e30eb143fc84963d5cee0e4f2f/AGENTS.md)
says **“Do NOT introduce new public API without RFC review.”** Its
[development guidance](https://github.com/DataDog/dd-sdk-ios/blob/bae6efb89717e7e30eb143fc84963d5cee0e4f2f/docs/DEVELOPMENT.md)
also requires RFC approval and cross-platform alignment for relevant lifecycle/configuration/data-collection
changes. A MAUI-owned Swift wrapper over existing Swift APIs does not establish that an upstream API change is
necessary.

## Native APIs that can actually be wrapped

| Concern | Android3.15.0 | iOS3.19.0 | Framework requirement |
| --- | --- | --- | --- |
| Construct | Flags.enable; FlagsClient.Builder(name).build | Flags.enable(with:); FlagsClient.create(name:in:) | Reuse the core initialized by DdSdk, not a new native core. |
| Context | required String subject, Map<String,String> attributes | required String subject, [String:AnyValue] | Preserve identity separately from attributes; unsupported typed/absent inputs require an explicit capability decision. |
| Readiness | callback and state/listeners | completion Result<Void,FlagsError> and observable state | A successful HTTP response alone cannot mark the client ready; handle stale/error and late callbacks. |
| Five details types | generic resolve: Boolean/String/Int/Double/JSONObject or Map | five getBoolean/String/Integer/Double/ObjectDetails methods | Exactly one native evaluation per requested evaluation, with native error/reason/variant preserved. |
| Integer/object | Int32; map/JSONObject recursive object | Swift Int64 on supported arm64; AnyValue | Desired C# long cannot be narrowed. Nested numeric/null/array fidelity must survive every bridge. |
| Details/error | native ResolutionDetails includes errorCode/message and primitive metadata; four error codes | FlagDetails has nullable reason/variant, allocationKey and only providerNotReady/flagNotFound/typeMismatch errors | Missing native error categories/metadata remain gaps. Do not manufacture ERROR, PARSE_ERROR, GENERAL or serialId. |

Evidence:
[Android surface](https://github.com/DataDog/dd-sdk-android/blob/83deee17bb68d64a61dd12d626ef112b028f41e0/features/dd-sdk-android-flags/api/apiSurface),
[context](https://github.com/DataDog/dd-sdk-android/blob/83deee17bb68d64a61dd12d626ef112b028f41e0/features/dd-sdk-android-flags/src/main/kotlin/com/datadog/android/flags/model/EvaluationContext.kt),
[converter](https://github.com/DataDog/dd-sdk-android/blob/83deee17bb68d64a61dd12d626ef112b028f41e0/features/dd-sdk-android-flags/src/main/kotlin/com/datadog/android/flags/internal/FlagValueConverter.kt);
[Swift client](https://github.com/DataDog/dd-sdk-ios/blob/61348d738e15d8418226e923e9db3bd6a97d1e00/DatadogFlags/Sources/Client/FlagsClientProtocol.swift),
[details](https://github.com/DataDog/dd-sdk-ios/blob/61348d738e15d8418226e923e9db3bd6a97d1e00/DatadogFlags/Sources/Models/FlagDetails.swift),
[context](https://github.com/DataDog/dd-sdk-ios/blob/61348d738e15d8418226e923e9db3bd6a97d1e00/DatadogFlags/Sources/Models/FlagsEvaluationContext.swift).

Both native pins contain Flags; neither is currently included in MAUI. They are source-visible starting
points, not proven binary/corpus-compatible artifacts. Current native develop snapshots were checked
separately (Android4831b6cd2c5c612841ddd3013c95ba2597dd68ec; iOSbae6efb89717e7e30eb143fc84963d5cee0e4f2f).
Newer Android still lacks Long reads/typed attributes; newer native error/numeric changes must not be
attributed to these pins.

Full signed64/typed-context support needs a coordinated Android native prerequisite first. Prospective sites
are FlagsClient, EvaluationContext, FlagValueConverter, request and telemetry context serialization/models and
tests. A type alias or wrapper conversion is insufficient. Alternatively, owners could explicitly approve a
narrower Int32/string-context product API, with uncovered FIT slices; that is a scope decision, not
conformance. Do not parse raw assignment snapshots into a C# evaluator to fill the gap.

Swift context completion distinguishes invalidResponse from networkError and initializationTimedOut; a response
rejection classification must preserve those boundaries. Android exposes a Throwable callback and a public
FlagsInitializationTimeoutException; a stable public invalid-response classifier was not established at these
pins. Carry an unclassified native failure honestly until the native owner supplies a bounded contract. Do not
classify by arbitrary exception text, assume every initialization failure rejected malformed data, or add a
reflection-based dependency on native implementation classes.

## Proposed product API and native exports

Names below are proposals, not existing calls or a mode-contract migration:

```csharp
DdFlags.Enable(FlagsConfiguration configuration);
DdFlagsClient client = DdFlags.CreateClient(string name);
Task<FlagsContextUpdate> client.SetEvaluationContextAsync(FlagsContext context);
FlagDetails<bool> client.GetBooleanDetails(string key, bool defaultValue);
FlagDetails<string> client.GetStringDetails(string key, string defaultValue);
FlagDetails<long> client.GetIntegerDetails(string key, long defaultValue);
FlagDetails<double> client.GetDoubleDetails(string key, double defaultValue);
FlagDetails<FlagObject> client.GetObjectDetails(string key, FlagObject defaultValue);
// State subscription returns a disposable listener registration.
```

Long/typed-context signatures state desired full fidelity; their Android implementation is blocked as
described above. Do not label the sketch immediately implementable. Configuration needs native
flags/exposure/evaluation endpoint URLs, tracking switches, aggregation interval and initialization timeout
with explicit units. Keep test-only queue barriers outside the customer facade. FlagsContext must retain
subject presence separately from the typed attribute map, including an attribute literally called
targetingKey. Validate before changing the current client or initiating a request. At these pins, a
null/absent dedicated subject has no native representation: report an unsupported input before side effects,
rather than replacing it with empty string. Preserve actual empty strings.

FlagDetails should retain actual native nullable reason/variant, structured native evaluation errors and
read-only metadata; map Swift allocationKey and Android native metadata only. Distinguish initialization
failures from evaluation errors. Preserve caller defaults exactly, including false, zero, empty string/object
and special Double defaults where supported. Do not reinterpret successful rounded native values into
corrected results after tracking already happened. Unknown native errors/states are explicit
unsupported/native outcomes, never success. Avoid recording raw customer-bearing native messages in telemetry.

Use a closed, tagged JSON value representation for FlagObject/context/metadata. Existing
[DdSdk conversion helpers](https://github.com/DataDog/dd-sdk-maui/blob/817c77cace2c8d85a798da9f06628268f4b1db21/bindings/Datadog.Maui/DdSdk.cs)
are not a sufficient flags codec: ToJavaObject falls back to string for null/unrecognized objects; ToNSObject
also stringifies unknown types. A flags-specific mapper must preserve recursive null, Boolean versus NSNumber,
signed integers, Double, strings, object/array distinctions and reject unsupported CLR types. Do not silently
serialize them with ToString. If using JsonElement at an internal boundary, retain number kind and clone data
before its JsonDocument is disposed; do not treat undefined as null. Ordinary JSON cannot carry non-finite
numbers, so special floating defaults need a typed bridge, not a JSON round trip.

**Swift wrapper:** add DatadogFlags to the existing Package.swift target, then proposed
`Sources/DatadogWrapper/DdFlags.swift`, typed client/result NSObject wrappers, and
`Protocols/FlagsModuleProtocol.swift` / FlagsClientProtocol adapter for injection. Swift can call the native
generic protocol directly inside this wrapper. Its outer surface must use explicit @objc selectors and
Objective-C-compatible typed values/callbacks. Keep Swift Result, associated-value enums, generic
FlagDetails<T> and AnyValue inside Swift. Use a bounded error object/domain/code, not an NSError description
classifier. Bind five concrete result classes or concrete typed getters with a shared metadata envelope; never
erase Int64/Double into strings.

**C# iOS binding:** proposed `bindings/Datadog.iOS.Binding/ApiDefinition.Flags.cs`, explicitly included
through ObjcBindingApiDefinition in its csproj; update StructsAndEnums.cs only for chosen native bridge enums.
Export attributes must match the generated Swift header exactly, including colon count, nullability and
callback signatures. Native DatadogFlags itself has an empty
[ObjC surface](https://github.com/DataDog/dd-sdk-ios/blob/61348d738e15d8418226e923e9db3bd6a97d1e00/api-surface-objc)
; C# cannot bind its Swift generic interface simply by naming it in ApiDefinition. Existing Session Replay
wrapper/binding is the nearest complete registration pattern.

**Kotlin wrapper:** proposed
`native-wrappers/android/datadogwrapper/src/main/kotlin/com/datadog/wrapper/{DdFlags,DdFlagsClient,DdFlagDetails,DdFlagsCallback}.kt`
. Expose Java-compatible concrete classes and listener interfaces; static factories use @JvmStatic. Keep
Kotlin Result/suspend/sealed native states/generic resolve details inside Kotlin and return typed export
models. Names on the JNI surface are proposals pending generated binding inspection. Use one real native
generic resolve call per getter, then project its result without a second read or fabricated tracking.

**Android dependency/binding ownership:** add `implementation("com.datadoghq:dd-sdk-android-flags:3.15.0")` at
the selected aligned version in wrapper Gradle. The smallest proposed packaging path adds a matching
`AndroidMavenLibrary` with `Bind="false"` to the existing
`bindings/Datadog.Android.Binding/Datadog.Android.Binding.csproj`: wrapper exports contain only wrapper
types, so native flags need runtime packaging, not a second customer-facing C# native API. Preserve its
Core/Internal dependency graph through existing feature packages; do not package the Flags AAR in another
project too. Extend ProGuard extraction/consumer rules, artifact verification and version-alignment checks to
cover this AAR. Audit POM dependencies explicitly: AndroidMavenLibrary does not recursively add dependency
artifacts, especially with existing VerifyDependencies=false settings. Reuse Core/Internal/Gson/OkHttp/Kotlin
packages; do not bundle duplicate native cores or Maven copies of libraries already supplied by NuGet. See
[Microsoft's dependency rules](https://learn.microsoft.com/en-us/dotnet/android/binding-libs/advanced-concepts/android-maven-library).

The existing wrapper binding removes com.datadog.android.* nodes. Therefore no proposed exported wrapper
signature may mention a native Flags type. Inspect generated api.xml to prove that before choosing Bind=false.
If owners instead require directly bound native classes, that would require an explicit Datadog.Android.Flags
feature-binding package and revised dependency ownership; it is a larger alternative, not an extra package to
create by default. A packaged native AAR without wrapper/facade exports is not framework flags support.

The proposed unified C# facade is
`bindings/Datadog.Maui/{DdFlags,DdFlagsClient,FlagDetails,FlagsContext,FlagsState}.cs` plus
configuration/value mappers, following DdRum/SessionReplay's internal test bridge pattern. Keep platform
branching inside this layer, not consumer or FIT application code. No framework OpenFeature
provider/dependency exists; introducing one would be separate SDK work after this facade, not an assumed
success path.

## Implementation order and test receipts

1. **API/native owners:** settle width/context/error limits, same-core ownership, immutable JSON
   representation and listener/lifecycle contract. Coordinate any Android native enhancement once with KMP and
   other consumers. Confirm whether the bounded API is an SDK client API or a future separately shipped
   OpenFeature provider. No mode enum/schema is changed here.
2. **Native wrapper owners:** implement enable/create/update/readiness and five typed details against exact
   aligned native modules, with injection protocols and tests. Add the Swift wrapper product dependency and
   Android Flags runtime AAR. Handle before-init/duplicate-name/failed-context/late-callback cases using
   actual native behavior. Native clients are retained by name; endlessly generating client IDs is not a
   release/reset lifecycle.
3. **Bindings/package owner:** generate/check ObjC header and JNI API, add the C# iOS ApiDefinition and
   existing Android binding runtime dependency, integrate build order and ProGuard packaging, then verify
   package graph and one core on each host. The minimal runtime-only Android path keeps the existing project
   graph; if the larger feature-binding alternative is selected, include that new project in
   solution/release/version-management and CI enumerations. Reconcile source/package/assembly/native identity,
   including the old FIT mismatch, before runtime claims.
4. **C# facade owner:** add product models/converters, client handle and disposal of subscriptions,
   asynchronous context completion and internal `IFlagsBridge` test seam. Native client disposal is not
   established by the pinned registry; subscription disposal must not imply native-client destruction. Do not
   reuse broad exception handling/default substitutions to hide unsupported input or failures. SDK-layer
   invalid-input rejection must preserve current provider state and perform no fetch/tracking.
5. **SDK test owner:** add xUnit `DdFlagsConfigurationTests`, `DdFlagsClientTests`, `FlagsValueMappingTests`
   and NativeFlagsBridge fake; explicitly link new source files in
   `tests/Datadog.Maui.Tests/Datadog.Maui.Tests.csproj`. Its plain net9/net10 source-linked tests do not
   compile the ANDROID/IOS branches. Add Android wrapper JUnit/MockK tests under the mirrored src/test path;
   Swift XCTest/client-protocol tests under DatadogWrapperTests. Include real cross-boundary result tests in a
   consuming MAUI app to cover the platform code that mocks cannot exercise.

Tests must verify all arguments and all details fields, exactly one native evaluation/tracking path per
getter, unsupported/unknown native failures, readiness/stale/error, duplicate/empty names/keys, context update
races and invalid-input atomicity. Cover caller defaults, Int32/Int64 extremes and 2^53 boundaries,
fractional/overflow/inexact conversion, negative zero and non-finite Double defaults, recursive
objects/arrays/null and Boolean NSNumber discrimination. Separate expected native gaps from bridge errors; no
canonical expectation edits. Use actual native tracking delegation controls, then intake evidence; C# fake
counters alone are not event proof. After drain, update context/evaluate again and prove the SDK remains
usable.

Future commands, **not executed**:

```sh
./check.sh --maui
./check.sh --maui --net9
./check.sh --android
(cd native-wrappers/android && ./gradlew :datadogwrapper:assembleRelease)
dotnet format example.slnx --verify-no-changes
# After exact native/binding dependencies have been built and packed:
dotnet build bindings/Datadog.Android.Binding -c Release -f net10.0-android
dotnet build bindings/Datadog.Maui -c Release -f net10.0-android
dotnet build example/example.csproj -f net10.0-android
# macOS/Xcode, matching .NET iOS/MAUI workloads:
(cd native-wrappers/ios && ./build.sh)
./check.sh --ios
dotnet build bindings/Datadog.iOS.Binding -c Release -f net10.0-ios
dotnet build example/example.csproj -f net10.0-ios
./verify-artifacts.sh --nuget
# Runtime jobs only in an owned isolated environment, with script cleanup approved:
(cd example && ./build.sh --android --run)
# macOS, owned simulator:
(cd example && ./build.sh --ios --run)
```

Repeat native bindings/consumer compile for supported net9 TFMs; use the exact existing .gitlab-ci matrix and
any deliberately selected new-project registrations. API/ABI proof includes generated ObjC
selectors/nullability/callbacks, generated Android api.xml/C# signatures, reference assembly/public .NET API
comparison and compile-consumer checks for both TFMs. No dedicated managed API-compatibility baseline task was
established in this audit; agree and record that release check rather than inventing a passing gate. Inspect
linker output/XCFramework and release DEX/NuGet contents to prove types and native code survive trimming/R8.
Host unit tests cannot establish that.

Linux can check pure C# source-linked tests, Android wrapper/JNI binding builds and Android runtime only with
the required .NET/Android workloads and an owned emulator. It cannot build/verify iOS wrappers or iOS MAUI
artifacts. iOS native3.19+ needs Xcode26; exact .NET Apple workload/Xcode/Kotlin-independent tool
compatibility must be checked before provisioning. Contributor prose saying Xcode15+ is insufficient for the
actual pin. Root `build.sh` also builds iOS, so Linux cannot use it as an aggregate proof. The root and
example scripts delete global Datadog NuGet caches; future execution must use a separately approved isolated
environment/cache, not a shared active workspace. No cleanup was run here. The example's Android --run command
does not select a device; coordinator must arrange an owned single-device environment or add reviewed targeted
launch handling before device execution, not reuse live RN resources.

## Telemetry, safe draining and later FIT work

Enable on the same DdSdk core, then native context update performs the real precomputed POST; native
typed-details evaluation records native exposures (doLog/dedup) and aggregated evaluations, then native
storage/upload reaches dedicated intakes. Bind Android custom flag/exposure/evaluation endpoints and Swift
customFlags/Exposure/EvaluationEndpoint separately, with trackExposures/trackEvaluations and interval
controls. Milliseconds on Android versus seconds in Swift require explicit conversion. Core batch/upload
settings and consent remain genuine SDK configuration. Local HTTP also needs owned network-security/ATS
permissions; Android already supports `_dd.needsClearTextHttp` through AdditionalConfiguration. Preserve
source=maui and the resolved SDK version from DdSdk's existing additional-configuration path.

**DdSdk.Flush is not a reusable drain.** Its
[public remarks and native implementation](https://github.com/DataDog/dd-sdk-maui/blob/817c77cace2c8d85a798da9f06628268f4b1db21/bindings/Datadog.Maui/DdSdk.cs)
explicitly shut down Android executors. Never call it between continuing evaluations/context changes. Swift
Datadog.flush is non-destructive core SPI, but a core-only flush does not prove private flags aggregation was
emitted first.

Safe initial repeated-case observation: configure the native evaluation aggregation interval and
frequent/small uploads, use bounded asynchronous collector waits plus a full post-evaluation quiet interval,
and fail on missing/extra receipts. This preserves the client, but is not a deterministic queue-empty
guarantee. Stronger FIT-only verification requires a reviewed asynchronous barrier in the SDK/native layer:
drain Android EvaluationEventsProcessor / Swift EvaluationAggregator, await real write completion, then core
storage/upload completion, leaving timers/executors/providers operational. Those flag aggregation methods are
internal; no such framework barrier exists at these pins. It is a separately owned prerequisite, not
permission to call private methods via reflection, synthesize events, clear dedup, or reuse stop/shutdown.
Keep it distinct from product APIs, off the UI thread, with a timeout and a second-evaluation regression.
Native cache/dedup isolation between authored cases must be proven; a fresh owned process per case can isolate
state while same-client repeated evaluations test dedup. Do not claim reusable reset from unique retained
clients.

Only after a real framework API is available should the coordinator privately extend existing eligible MAUI
IPC dispatch to call this facade and generated service bindings. No internal FIT paths/source are copied here.
Start online-precomputed all-types smoke on Android and iOS, then full unchanged imported corpus; no later
deployment mode or init contract is assigned. Record exact NuGet/native/assembly/APK/app identities,
configuration HTTP/context, typed actual details and real intake receipts. Preserve authored
defaults/expectations, investigate native and host-specific gaps narrowly, and fail transport/lifecycle errors
instead of treating them as response rejection. Require independent local Crucible review, aggregate checks
and separate publication gates. Existing tracking is FFLSDK-147 under FFLSDK-109; no ticket/status changes
were made.

Validation: source/API/dependency/export declarations and provider metadata were inspected read-only. No
restore, build, generated-header/assembly/AAR inspection, unit/native/FIT execution or demonstrated binary
compatibility is claimed.

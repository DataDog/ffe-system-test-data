# Java independent pass before PR reviews

Frozen source: `DataDog/dd-trace-java@660b5b96114cc29f2edc8c806b9a621621ba552e` (PR #12950).
Central decisions inspected: `DataDog/ffe-system-test-data@d23d0f51a1b96c2e9a98f29a984325e58e6f41ca`, `activation-and-semver-feedback-v10`.
No Java PR review comments were read. No production files were changed. The Java worktree remained clean.

## Implementation owners

1. Standalone `dd-openfeature`: `Provider` -> `DDEvaluator` -> `internal.evaluation.FlagEvaluator`; production Jackson UFC parser and immutable allocation objects.
2. Legacy `products/feature-flagging`: API `Provider` -> API `DDEvaluator`; agent library Moshi UFC parser; bootstrap allocation objects. The provider can use older agent classes, so new field reads need capability guards.

Both owners evaluate rules locally. Browser request acknowledgement, per-context assignment transport, and pending refresh D001/D008/D014 do not directly apply. Both snapshot configuration once per evaluation. No new cache or telemetry mutation was found in this diff.

## Findings

### J1 — D004 activation errors have the wrong scope (implementation delta required)

Both production parsers reject the complete flag when any allocation has malformed non-null `randomizationActivatedAt`. Both evaluators then return `PARSE_ERROR` in every mode, including disabled and absent cutoff. This also rejects a malformed allocation after an already matching ordinary allocation. D004 requires prepared valid/missing/invalid state, followed by flag-level `PARSE_ERROR` only for future mode with a valid subject cutoff.

Source: standalone `UniversalFlagConfigParser.java:249-258`; legacy `UniversalFlagConfigParser.java:634-645`; both `RandomizationActivationTest` classes explicitly assert current parse-time removal. Both READMEs explicitly promise all-mode failure and need the same correction.

Executed distinguishing trace: unchanged standalone production parser with an ordinary first allocation and an unreachable malformed second allocation removes the target for string `bad`, boolean, number, array and object activation. A neighboring valid flag survives. Null and valid activation retain the target. See `parser-probe.log` and `parser-probe-manifest.json`. This is an unchanged source extraction compiled with Java 21 `--release 11`, cached Jackson 2.15.3, SLF4J 2.0.7, and JSR305 3.0.2. It proves the parser result only, not Gradle integration or the legacy parser runtime.

Minimal change: represent invalid activation separately from missing/null, parse once, and preserve the flag. With future mode plus non-null cutoff, inspect every prepared allocation before allocation selection. If any activation is invalid, return the existing per-flag PARSE_ERROR response. Disabled, immediate, and absent-cutoff paths retain normal allocation selection. Preserve other parsing failures and Java timestamp grammar. Add backward-compatible constructor overloads and guard new legacy bootstrap field access against old agents.

### J2 — D017 inactive operation is still called (implementation delta required)

Standalone `FlagEvaluator.java:159-161` and legacy `DDEvaluator.java:329-331` call `ExperimentationOptOut.excludes` for each visited allocation even when the cutoff is null. The helper returns immediately, but the recorded D017 boundary is the operation call itself. Add `experimentationCutoff != null &&` at both production call sites. Existing `missingAttributePreservesParticipation` tests call the helper directly; they do not observe whether production skips it. Keep the helper null guard for defensive callers.

Use a native instrumented operation boundary and a negative control that restores the unconditional call. Keep whole-evaluation JMH measurements separate from logical call counts. The standalone benchmark already covers disabled, immediate, future, and opted-out/absent inputs, but no registration for this benchmark was found under `.gitlab` or `.github`. No legacy opt-out benchmark was found. Do not claim a runtime speedup from the source guard.

### J3 — D015 provider disablement requires a Java-specific decision (preserve lifecycle)

Standalone `Provider.java:85` resolves the mode before `FeatureFlagsRuntime.create` checks `settings.configurationSource()`. An invalid configured mode therefore throws during construction even with `DD_FEATURE_FLAGS_ENABLED=false`, an unsupported source, or the legacy disablement toggle. Existing Java disablement throws `Feature Flags is disabled` during initialization; it does not construct a Go-style NoopProvider. Legacy construction also resolves mode before agent activation. Record this mapping and preserve the Java lifecycle unless a separate scoped decision authorizes a change. The central adoption instruction from the coordinator explicitly preserves it.

### J4 — Java parser differs from browser/Go (intentional scoped difference; do not change)

Both cutoff methods use `DateTimeFormatter.ISO_OFFSET_DATE_TIME`, matching Java allocation timestamps. Native parser checks accept lowercase t/z, missing seconds, offset seconds, expanded years, and UTC normalization outside years 0000–9999. They reject more than nine fractional digits and offsets beyond 18 hours. See `parser-probe.log`. Browser D005–D007 acceptance cannot silently replace the Java profile. Existing timestamp tests mostly compare the implementation against the same formatter, so they do not independently define grammar.

### J5 — legacy canonical fixture tests bypass the production parser (coverage gap)

Standalone `CanonicalFixtureTest` uses the production parser. Legacy `DDEvaluatorTest:1144` uses its own Moshi CONFIG_ADAPTER and custom Instant/flag/SemVer adapters. A future D004 fix to the production legacy parser can therefore diverge from this fixture path without being tested together. Add the thin policy adapter at a boundary that invokes the real legacy parser and the actual legacy evaluator. The library module can add test-only access to the API module without a production dependency, or a native smoke test can exercise both built modules.

Both owners assert exact current capability counts: 26 immediate and 42 future cases at fixture commit `b28876200152f00c7d5eb04616f721afa5955c1d`. Inventory is in `fixture-inventory.json`. The submodule is uninitialized in the audit worktree. These cases do not cover the new D004 tri-state cross-product; they must coexist with the 90-case Lean policy adapter. Do not change the expected counts to conceal missing cases.

### J6 — telemetry evidence needs future-retention coverage (coverage gap)

Both telemetry suites cover the four combinations of immediate exclusion and evaluation telemetry suppression. They assert ordinary fallback, no exposure for excluded experiments, independent evaluation telemetry, and customer hook continuity. No future-mode or activation-specific scenarios were found in either telemetry suite. Retain a native integration case for a retained older experiment: exposure remains eligible, evaluation telemetry follows only its own control, and cache dedup remains intact. Add excluded future and equality cases if they establish a distinct metadata/cache path.

## Native adapter proposal

Consume the coordinator's pinned 90-case Java policy profile and expected outputs. For each case, construct UFC wire JSON with an experimental allocation, ordinary fallback and valid neighbor. Use the production parser and evaluator for the target owner. Map mode, absent/valid/malformed subject, activation missing/invalid/before/equal/after, and doLog; compare value, error, allocation identity and neighbor isolation. Expected results must come from the pinned corpus. Assert all 90 IDs execute, with no runtime applicability inference. Add a dedicated unreachable-invalid trace because first-match behavior otherwise hides incomplete validation.

Keep parser grammar, no-agent/older-agent linkage, provider initialization, configuration replacement, exposure delivery/dedup, independent telemetry and concurrency outside the bounded policy claim. Native lifecycle checks remain required.

## Focused validation commands after implementation

Use the repository JDK/toolchain configuration. A local Java 21 exists at `/Applications/Android Studio.app/Contents/jbr/Contents/Home`; `/usr/libexec/java_home` does not discover it. Standard commands:

```sh
./gradlew :dd-openfeature:test --tests '*ExperimentationOptOut*' --tests '*RandomizationActivationTest' --tests '*CanonicalFixtureTest' --tests '*EvaluationTelemetryOptOutTest' --tests '*ProviderTest'
./gradlew :products:feature-flagging:feature-flagging-api:test --tests '*ExperimentationOptOut*' --tests '*DDEvaluatorTest' --tests '*EvaluationTelemetryOptOutTest' --tests '*ExposureHookWithoutAgentTest'
./gradlew :products:feature-flagging:feature-flagging-lib:test --tests '*RandomizationActivationTest' --tests '*UniversalFlagConfigParser*' --tests '*ExperimentationOptOut*'
./gradlew :dd-openfeature:test :products:feature-flagging:feature-flagging-api:test :products:feature-flagging:feature-flagging-lib:test
```

Run the actual new adapter by name and record nonzero test counts. Initialize only the canonical fixture submodule at its pinned SHA. Preserve Java 11 compatibility and add the repository-required formatting checks after edits. System-tests with the built standalone provider, standalone agentless mode, and legacy provider/agent remain beyond-unit evidence. They have not been run by this audit.

## Base merge risk

Inspected cached `origin/master@3718fdc518506e5700df8b7d448639971cd3470c`. Merge base is `fe25fd4f49376c1dd9c44f6872ca49434f9a4ae0`; branch divergence is 10 branch commits and 8 base commits. The read-only three-way merge showed no conflict markers. No incoming changes were found under dd-openfeature or products/feature-flagging. `metadata/supported-configurations.json` changes on both sides merge in separate sections. Base has CI/build/documentation and unrelated instrumentation changes. A current remote refresh and full revalidation are still required before publication; this audit did not fetch or merge.

## Evidence limits

The own-pass report is source-backed plus a standalone native parser probe. No full native Gradle suite, live CI, runtime intake, legacy parser execution, mutation experiment, or performance comparison was run in this audit. No review comments were consumed. No claims about full SDK equivalence or deployment readiness are made.

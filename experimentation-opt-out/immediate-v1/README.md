# Immediate experimentation opt-out

This suite covers the timestamp-based MVP in [dd-trace-go#5666](https://github.com/DataDog/dd-trace-go/pull/5666).
It contains 41 scenarios and 57 evaluations. SDKs must opt into this suite explicitly.
The existing `evaluation-cases/` format and cases remain unchanged.

## Contract

- The provider mode is `DISABLED` by default. It ignores `dd_experimentation_opt_out_at` in that mode.
- In `IMMEDIATE` mode, a valid RFC3339 timestamp string excludes the subject on every evaluation.
- Fractional seconds and timezone offsets are supported. The timestamp records a preference; it does not schedule exclusion.
- An absent attribute permits experimentation. A present invalid value returns the caller default with `ERROR` / `INVALID_CONTEXT`.
- Exclusion skips allocations with `doLog=true`, including the existing default when `doLog` is absent. The check precedes targeting and sharding.
- Evaluation continues through ordinary allocations in order. Their targeting rules still apply. If none match, return the caller default.
- Eligible subjects retain their existing buckets. Excluded subjects are not reassigned into the experiment's control arm.
- Exclusion emits no exposure, withdrawal event, or synthetic variant. Evaluation telemetry remains a separate control.

This suite records the MVP's `doLog` classifier, not a general experiment lifecycle definition.
A holdout or winner that retains `doLog=true` is excluded. The SDK cannot restore a fallback removed by a compiler.
Future-experiments-only behavior, activation timestamps, compiler changes, and precompute protocol changes are outside this suite.

## Run a scenario

1. Create a fresh provider and empty telemetry caches for each scenario in `cases.json`.
2. Map `providerOptions.experimentationOptOutMode` to the SDK enum. An absent mode means the default.
3. Enable evaluation event collection. Honor the optional `enableEvaluationTelemetryOptOutParameter` independently.
4. Load the adjacent `ufc-config.json` through the normal configuration decoder.
5. Run `evaluations` in order on that provider. Replace the per-evaluation context; do not merge attributes from an earlier step.
6. Use the typed getter named by `variationType`. Assert `result.value`, `result.reason`, and optional `result.errorCode`.
7. Assert `result.allocationKey` through the SDK's result metadata. Null means no allocation was selected.
8. Flush telemetry after each evaluation. Assert cumulative `exposureCount` and `evaluationCount` for the scenario.

`evaluationCount` sums logical evaluations, not HTTP requests or aggregated event objects.
`exposureCount` includes deduplication. Do not reset caches between evaluations in one scenario.
For every emitted exposure, check the subject, flag, allocation, and variant against the selected result and UFC.
The suite does not prescribe SDK-specific metadata field names or a synthetic variant for defaults.

The fixtures use standard UFC types: `BOOLEAN`, `STRING`, `INTEGER`, `NUMERIC`, and `JSON`.
All values are small enough for consistent JSON number handling across languages.
The split uses MD5 of `opt-out-<targetingKey>`, the first four bytes as an unsigned big-endian integer, modulo 10,000.
`subject-0` maps to shard 1,814 (control). `subject-2` maps to shard 6,957 (treatment).
These anchors verify unchanged buckets, not exact population counts in a finite sample.

## Coverage

| Cases | Purpose |
| --- | --- |
| Default, disabled, missing, legacy boolean | Require explicit activation and the current timestamp attribute |
| Valid and invalid timestamps | Accept supported timestamps; reject malformed context without an exposure |
| Five value types, ordinary-first, targeted fallback, no fallback | Preserve ordinary delivery and caller defaults |
| Ordinary percentage rollouts | Preserve non-experiment sharding for opted-out subjects |
| Missing `doLog`, holdout, logged winner, disabled flag | Record the classifier's current behavior and limits |
| Control/treatment baselines and withdrawal/re-entry | Preserve eligible buckets, exposure deduplication, and per-evaluation changes |
| Initially excluded and independent subjects | Do not record false participation or leak state between subjects |
| Telemetry-only and both controls | Keep evaluation telemetry independent from experimentation and exposures |

Run static checks with `python3 ci/validate-immediate-opt-out.py`.
Static validation checks fixture shape and references. An SDK runner must verify evaluation and emission behavior.

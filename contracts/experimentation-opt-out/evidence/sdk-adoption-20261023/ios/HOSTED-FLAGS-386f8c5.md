# Hosted Flags execution at 386f8c5

Repository: DataDog/dd-sdk-ios  
Commit: `386f8c5d59af9c9ffb9cf7dee6aa2e90c95a5c0f`  
Read time: 2026-10-23T03:36:24Z  
Source: Datadog CI Visibility, pipeline [146948453](https://gitlab.ddbuild.io/DataDog/dd-sdk-ios/-/pipelines/146948453).

All 19 tests added against develop passed on all five Apple platforms. There were 95 final outcomes for these tests.

| Platform | Passed unique tests | Skipped by TIA | Failed | Passing attempts |
| --- | ---: | ---: | ---: | ---: |
| [iOS](https://gitlab.ddbuild.io/DataDog/dd-sdk-ios/-/jobs/2168876892) | 188 | 49 | 0 | 188 |
| [tvOS](https://gitlab.ddbuild.io/DataDog/dd-sdk-ios/-/jobs/2168876893) | 188 | 49 | 0 | 251 |
| [watchOS](https://gitlab.ddbuild.io/DataDog/dd-sdk-ios/-/jobs/2168876894) | 188 | 49 | 0 | 188 |
| [visionOS](https://gitlab.ddbuild.io/DataDog/dd-sdk-ios/-/jobs/2168876895) | 181 | 56 | 0 | 181 |
| [macOS](https://gitlab.ddbuild.io/DataDog/dd-sdk-ios/-/jobs/2168876896) | 188 | 49 | 0 | 251 |

Each platform has 237 unique final test outcomes. TIA means Test Impact Analysis. Every skip has `test.skipped_by_itr=true`. macOS and tvOS each have 63 additional passing attempts for early flake detection. They are excluded from unique test counts. The separate failed-attempt query returned no events.

## Original review names

Three names from [review thread 4343863269](https://github.com/DataDog/dd-sdk-ios/pull/3338#discussion_r4343863269) passed on all five platforms:

- `testExperimentationOptOutUsesEvaluationOptions`
- `testOptedOutRequestRequiresBooleanAcknowledgement`
- `testFutureOptOutRequiresTypedModeAndExactCutoffAcknowledgement`

These two names are absent at this commit:

- `testObsoleteRequestCannotPublishStateOrNotify`
- `testContextChangeInCompletionDoesNotEmitOldReadyNotification`

The develop merge replaced their internal state-manager API. The three current deferred/reentrant state-manager tests were skipped by TIA on every platform. Their names and source links are in the JSON matrix.

Current repository coverage passed on all five platforms:

- [Delayed success publication](https://github.com/DataDog/dd-sdk-ios/blob/386f8c5d59af9c9ffb9cf7dee6aa2e90c95a5c0f/DatadogFlags/Tests/Client/FlagsRepositoryTests.swift#L2523) pauses inside the first request's completion. A newer context or reset changes the state. Resuming the first completion cannot publish its obsolete ready notification.
- [Both response orders](https://github.com/DataDog/dd-sdk-ios/blob/386f8c5d59af9c9ffb9cf7dee6aa2e90c95a5c0f/DatadogFlags/Tests/Client/FlagsRepositoryTests.swift#L2676) retain the newer flags and complete each request once.
- [Superseded success during reconciliation](https://github.com/DataDog/dd-sdk-ios/blob/386f8c5d59af9c9ffb9cf7dee6aa2e90c95a5c0f/DatadogFlags/Tests/Client/FlagsRepositoryTests.swift#L2781) cannot end the latest reconciliation or restore old assignments.
- [Initialization completion ordering](https://github.com/DataDog/dd-sdk-ios/blob/386f8c5d59af9c9ffb9cf7dee6aa2e90c95a5c0f/DatadogFlags/Tests/Client/FlagsRepositoryTests.swift#L1965) delivers completion before ready listeners.

This supports stale state and notification isolation. It does not prove identical semantics for the removed internal predicate/before-notify hook. Current develop deliberately completes superseded requests once.

## Evidence boundary

The final-event query returned complete pages for all five platforms. Each page has 237 unique tests, the expected commit, test-level events, and no continuation cursor. The compact JSON includes all 19 added names, the five original review names, related current tests, source links, query metadata, and job URLs.

Direct execution of the skipped state-manager tests remains a hosted coverage gap. These runs do not prove backend deployment or Swift provider release readiness. No CI rerun, source edit, or GitHub write was performed.

The feature usage document already waits for successful `setEvaluationContext` completion. The PR body should use the same pattern before evaluating a flag.

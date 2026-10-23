# Review 4355693358: concurrent named-client mode warning

The former second registry lookup returned an existing client without checking its experimentation mode. Two concurrent calls could therefore bypass the existing warning policy.

The fix performs one atomic lookup or creation. A newly created client returns immediately. An existing client goes through the warning policy after the registry lock is released.

The winning client and its experimentation mode stay unchanged. In graceful configurations, the losing caller receives the existing warning. In strict-debug configurations, the existing exception policy now applies consistently.

The latch-controlled regression checks both enabled modes against a disabled winner. It checks winner identity and that registry reads complete while warning delivery is blocked. The warning-disabled negative control fails both cases.

The regression does not deterministically reproduce the former between-lock scheduling window. Source inspection establishes that path. The negative control establishes sensitivity to the required warning.

Candidate validation passed 663 Flags tests per variant, with no failures, errors, or skips. Detekt and ktlint passed with CI warnings treated as errors.

Only FlagsFeature registration flow and its regression test changed. Existing cda7955 runtime and profile receipts remain evidence for that commit. This change does not alter policy, callback dispatch, assignments, cache, telemetry, or HTTP behavior. A further device run is not required for this scope.

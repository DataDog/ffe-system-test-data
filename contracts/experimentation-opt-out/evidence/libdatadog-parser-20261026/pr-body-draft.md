# What does this PR do?

Adds `Disabled`, `Immediate`, and `FutureExperimentsOnly` evaluation modes using `dd_experimentation_opt_out_at`. SDK wrappers resolve provider configuration; the evaluator reads no process settings.

- Immediate mode skips exposure-logging allocations before targeting and randomization.
- Future mode retains activation strictly before the cutoff. Equal, later, missing, or null activation excludes the allocation.
- Invalid activation returns per-flag `PARSE_ERROR` only for future mode with a valid cutoff, including unreachable allocations.
- Cutoff and activation share the documented ASCII timestamp grammar: valid Gregorian fields, lowercase t/z, nanosecond truncation, and normalized UTC years 0000–9999. Whitespace, named zones, compact offsets and leap seconds are rejected; allocation schedules retain their existing parser.
- Ordinary allocations and retained exposure eligibility remain intact. Existing C entry points retain their default and boolean-mode behavior.

# Motivation

Customers need to exclude subjects from experimentation immediately or from experiments activated at or after their opt-out time.

# Additional Notes

The parser refinement follows the [review feedback](https://github.com/DataDog/libdatadog/pull/2698#discussion_r4380967749) and the scoped D005/D006/D007 contract. The cross-SDK lowercase disagreement remains separately tracked.

# How to test the change?

Native tests cover all 90 shared policy cases, malformed input, unreachable allocations, valid neighboring flags, timestamp boundaries, inactive exclusion calls, and panic containment. Shared fixtures use the merged #52 commit.

| Tested commit | Validation | Result | Evidence |
| --- | --- | --- | --- |
| `DataDog/libdatadog@ead1d3db2aa16e494f23e47b946ff12a7a1be53a` | Packaged C integration: mode/cutoff/error boundaries, allocation metadata, exposure eligibility, and legacy APIs; macOS/arm64 | 252 cases and 504 calls passed; 1 FFE example passed. 9 null/array/object attribute cases cannot be represented by the C API. | [Native receipt](https://github.com/DataDog/ffe-system-test-data/blob/98f1f5a4aab6e92fa0b74787cee94e36cc7c8e80/contracts/experimentation-opt-out/evidence/libdatadog-adoption-20261023/native-receipt.json) |

Downstream SDK runtime and telemetry delivery were not tested. [Shared decisions and scoped adoption](https://github.com/DataDog/ffe-system-test-data/blob/98f1f5a4aab6e92fa0b74787cee94e36cc7c8e80/contracts/experimentation-opt-out/libdatadog-adoption.md).

Local parser follow-up (uncommitted and unpublished): all 50 timestamp cases pass through both production paths across 464 evaluations, including all seven reviewer examples. The new adapter fails against the prior parser. All 110 native tests pass, including the unchanged 90 policy cases and FFI tests; check, formatting, Clippy, docs and shared-model verification pass. The C integration receipt above remains historical evidence for its stated commit, not this follow-up patch.

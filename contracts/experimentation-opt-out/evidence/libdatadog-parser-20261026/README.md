# libdatadog #2698 parser fix

Status: locally validated, uncommitted and unpublished. The baseline PR commit is not the fixed implementation. Apply `libdatadog.patch` to the pinned base in `summary.json` to reproduce it.

The shared D005 r2 / D006 r2 / D007 r1 grammar now governs subject cutoffs and JSON activation. Exact ASCII fields and Gregorian dates are required; lowercase t/z and truncation beyond nanoseconds are retained. Written and normalized UTC years stay within 0000–9999. Allocation schedules and D004 malformed-versus-missing policy are unchanged.

The original 313 corpus rows and all Lean source files are unchanged. Seven exact reviewer examples extend the corpus to 320 rows. All 50 timestamp rows run through both production paths, at equality and representable adjacent nanoseconds for valid timestamps, for 464 evaluator calls. The existing 90 policy cases remain unchanged.

The new adapter fails against the original parser (`baseline.log`) and passes with the patch (`timestamp.log`). All 110 native tests pass with no skips (`native-host.log`); the first run's sandbox socket-binding failures remain in `native.log`. Check, formatting, Clippy, documentation tests, and 14 verifier tests pass. Lean 4.19.0 audits all 71 theorems and replays 320 semantic, 36 operational, 156 activation, and 24 SemVer cases. These are distinct model and native observations.

`profile.json` freezes applicability without exclusions. `summary.json` records the base, patch, source hashes, toolchains, and validation limits. `feedback.json` records local user authority and the missing public setting. The model execution used its recorded manifest; subsequent changes add evidence/history only. The final manifest integrity check verifies the complete resulting bundle.

No commit, push, GitHub reply, thread resolution, release, downstream adoption, or fleet approval is claimed for this fix.

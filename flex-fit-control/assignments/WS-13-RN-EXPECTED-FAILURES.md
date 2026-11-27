# WS-13 — precise RN SDK expected failures

CONTROL-049. Local RN test-policy owner. Existing service, SDK, fixture expectations and other platform behaviour remain unchanged. No activation PRs or publication before applicable checks pass.

The coordinator completed the unchanged canonical RN Android selection:35failed/30skipped,35fresh configurationHTTP200 responses with exact fixture contexts,65fresh reports. Seventeen ordinary nonempty cases fail native parsing,17response-rejection cases fail with the same unclassified native error, and the empty-response case returns three correct typed defaults but no evaluation records. No new exclusions were present. These are the three gaps in RN-GAPS.md; downstream assertions behind the parsing failure remain unverified.

Implement host-aware, exact-path expected-failure policy for only these investigated Android cases. Preserve actual case execution. Prefer strict expected failures restricted to a dedicated known-gap exception: throw that exception only after the exact recorded SDK failure fingerprint and fresh successful configuration receipt are established. Unexpected IPC/network/readiness errors, different SDK errors, assertion failures and unexpected emissions must remain failures. If an SDK upgrade makes the canonical case pass, strict XPASS must require removal/reassessment of the policy. Do not add wholesale skips or broaden SDK error classification in the IPC service.

For the empty-response tracking gap, execute and validate all typed reads and the normal flush/observation first. Recognise only the recorded missing-evaluation signature with no unexpected exposures/evaluations and a fresh configuration receipt; do not catch arbitrary assertion failures. Keep other emission assertions intact. Expected failures do not prove assertions that are unreachable behind the recorded defect.

Do not apply Android parsing/classification policy to iOS, other platforms, future case IDs, similarly named files outside the imported corpus or uninvestigated generated counterparts. No iOS runtime result is available. Defaults-and-emission-gates may reveal the separate tracking gap after parsing is repaired; do not hide that future distinct failure behind the current parsing policy.

Own a small test-policy helper, the common runner/scenario integration and focused policy tests only. Preserve existing staged RN topology/app work and the independently reviewed selected-device repair. Avoid circular imports. Test exact host/path scope, wrong error/status, stale/missing/non200 receipts, unexpected emissions, unexpected transport failures and strict XPASS behaviour; preserve Web numeric exclusions. Then independent local Crucible and canonical rerun. Record scope and evidence; do not claim SDK conformance from an all-xfailed selection. The known positive diagnostic control is separate from canonical conformance.

## CONTROL-050 review checkpoint

Initial implementation is local. Coordinator focused policy/rejection tests:135passed; implementor policy/rejection/compatibility selection:138passed. Independent correctness review found a P2 asynchronous receipt-inventory defect. Re-read the complete fresh receipt inventory immediately before each known-gap exception, after flush/observation; delayed extra HTTP200 or non200 receipts must remain ordinary failures. Correction and red/fix regression controls assigned. Final review and canonical device rerun remain pending. Aggregate lint/publication are not complete.

## CONTROL-051 final policy review

The asynchronous receipt boundary correction is independently verified. Coordinator final tests142passed; four delayed200/403 receipt controls fail under restored weak guards. Five native lenses, native Coverage fallback and final stateful verifier report no remaining P0/P1/P2. Exact-path host/error policy is frozen during a new canonical Android runtime run. No terminal rerun result yet. Full aggregate lint and publication remain outstanding; expected failures remain SDK gaps, not conformance.

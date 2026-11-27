# Local Crucible review queue

Policy revision CONTROL-003, November 27, 2026. Coordinator owns review acceptance. Each branch reported ready receives a local Crucible review; implementor readiness alone is not acceptance. No activation PRs.

| Assignment / branch | Reported ready | Exact base/head and paired dependencies | Review state | Evidence / next action |
| --- | --- | --- | --- | --- |
| WS-01 shared activation foundations | Local implementation handed off; publication blocked | FIT base e07ae57ef3108b18b10d2f67690bc36caf8303af; head 47f8760c5c7ca870a13029bb711cd74d3a506bae; corpus a4966e2, Browser b3bd0bc | Independent local review complete: no actionable finding; delivery not accepted | Five native specialists, native coverage fallback and targeted verifier; external peer unavailable. Coordinator 49 focused passes, two killed mutants; full run 882 passed / 30 missing-runtime failures, followed by all 30 passing after Chromium setup. Separate executions. Full lint, Dynamic Build/native runtime proof remain. |
| WS-03 native foundations and simulator topology | Local candidates handed off; publication blocked | FIT base e07ae57ef3108b18b10d2f67690bc36caf8303af; foundation e5bf01e01bcaa581d39b67587e35f8e25c9a195a; child head 286af174684cca80eeec627b3c530a2b4a6d010f | Five specialists, native coverage fallback and targeted verifier retain no actionable finding; independent unit execution complete; publication blocked; not accepted | Coordinator reproduced 83 focused passes and three killed mutants (marker, fresh receipt, Android loopback). Coordinator independently ran all 960 unit tests successfully in 258.71 seconds. Native rejection/inventory and full lint gaps remain; external peer unavailable. |
| WS-02 Android online precomputed | Signed local candidate ready for emulator handoff | FIT base e07ae57ef3108b18b10d2f67690bc36caf8303af; head f00e34003d4f35026653c16a945389aa24dd5844; tree fcd8512161c033967743782de0bf2bea02969a5c; WS-03 e5bf01e; corpus 26f75b6 | Queued independent local Crucible and runtime; private bundle imported and signature/tree verified | Implementor reports 960 unit passes, three JVM selector tests, compile/ktlint and regenerated Python/Web/Android bindings; Swift/Dart generators unavailable there. 130 cases collected, none executed on device. Full lint/runtime remain. |

For each ready handoff record repository/remote branch, actual base/head and merge base, FIT/corpus/SDK revisions, ownership, local check commands/counts, exclusions with workstream gap IDs, specialist/peer coverage, numbered findings with evidence, fixes and verification, remaining P0/P1 count and coordinator disposition. Keep evidence tied to exact revisions. If a dependency or branch head changes, refresh affected checks/review.

Review states: awaiting ready branch; queued; in progress; changes required; accepted with stated coverage/limitations; blocked. Acceptance requires no remaining P0/P1 implementation/activation/exclusion defects. SDK gaps may be narrowly excluded only after investigation and recording, per Instructions.md. An environment blocker or partial review remains visible and must not be presented as a clean runtime result.

Review entries above concern handed-off local candidates; historical open PRs and candidate receipts in goal.md are not automatically ready handoffs. Local branch reviews make no GitHub review/label/readiness mutations and do not authorise PR creation.


CONTROL-019 queue additions: WS-04 full actual-source candidate now reports10pass/55scopedskip/0fail, exact signed paired handoff pending; independent local council required. WS-07 signed child8598538616ec739ecc928cd2c421eea69bbee24a (parent4191626a9894199b0768311fb991b912a4fc2ba1, treee08134afdee24a807a03956b0ea61b6e55f90417) verified and queued after live WS-09 inventory. WS-08 real SDK smoke passes but is not a ready/full-row handoff. No review acceptance is inferred from runtime counts.


CONTROL-021: coordinator independently verified signed/clean paired iOS FIT4bc3a62838895147466fb72d75e7e1683927aa2a (basee07ae57) and corpus261df0f204655f05b3ea680485d53e4509c901cf (basefe24ed2). Local correctness specialist started, other lenses/verifier pending. Android correctness specialist is also live; no verdict yet. No clean council or acceptance inferred.


CONTROL-022 Android correctness result: oneP1 pending repair, noP0 found in this lens. Android InitProvider lacks strict malformed-response translation; exact pinned SDK public error state retained, no public parse-specific code. Owner must add bounded mapping and positive/negative controls, followed by independent re-review. Root73affected tests pass; they do not prove device mapping. Other specialist lenses/coverage/verifier remain incomplete. Metadata enumeration is a separate SDK/API capability gap.


CONTROL-023 iOS correctness lens: NONE,5independent compatibility passes and all24changed corpus files verified non-filter-equivalent. Performance lens live; other council jobs/coverage/verifier incomplete. Root independently verified signed heads as recorded above. No platform accepted.


CONTROL-024 iOS council partial: correctness/QA/SRE NONE; senior P1 confirmed by coordinator source trace through MauiDriver -> IosDriver -> unconditionalgrpc readiness. Owner repair assigned; P1 remains open until tested/re-reviewed. Performance twoP2 observations retained in private candidate ledger for adjudication. Other required coverage/verifier work pending. Android repair handed off, independent delta verification pending. No full clean council or cell acceptance claimed.


CONTROL-026 Android P1 source delta confirmed fixed at signedacbeb6b2de9f9b6ddee1653697ac4768ce7c2f48 by original independent correctness reviewer; actual device/gRPC control still open and full council incomplete. iOS readiness repair reports31focused positives/negative controls; signed child/delta verification pending. Two performance P2 observations remain under adjudication.


CONTROL-027: iOS signed child215fb35b2b3283ec39fb5d39c3bcd1e32b638865 signature verified; original senior reviewer confirms P1 fixed/no remaining actionable delta. Correctness, QA, SRE, senior and native coverage lenses complete; external launcher absent, native fallback disclosed. Performance P2 actor-blockingflush/client-retention candidates remain in private ledger. Root full-unit exact child run live; final targeted stateful verifier pending. WS-11 transport branch will require its own independent local review and runtime controls once ready.


CONTROL-028: iOS exact-child coordinator full unit suite973pass; all five native lenses/native coverage fallback/stateful verifier complete without remainingP0/P1. P2 synchronous actor-blocking flush retained; no untested remedy applied. External RPC cancellation unverified. Exact-child full simulator corpus live; lint/publication gates open. WS-11 serializer-only review superseded by Tyler's explicit binary control-RPC requirement; preserve existing candidate/evidence, independently review replacement rather than accepting narrower repair. Android performanceP2 repeated feature enablement candidate pending coordinator adjudication; remaining council/runtime gates open.


CONTROL-032 WS-11: exact basee07ae57ef3108b18b10d2f67690bc36caf8303af, reviewed headd56d3659e29cf2ad7b9480f880e4ef3ff16dbef6. Five native specialist lenses plus native coverage fallback and stateful verifier found no actionable defect; external peer unavailable. Coordinator19focused/110neighbouring tests passed. Default scalars now cross the existing JSON boundary while optional/message presence and response/error paths remain intact. Browser validation integration87442cf; two real failed-baseline vectors running, full repaired corpus/aggregate lint pending. This review does not establish all-mode initialization or cell acceptance.


CONTROL-033 Android stateful verifier completed on clean repaired headacbeb6b2de9f9b6ddee1653697ac4768ce7c2f48. Exact released SDK objectdad2312223110e2e7ed84cf46cefe3a45bc759c6 confirms fresh malformed-response classification and cancellation identity. No remainingP0/P1 found across council/coverage/verifier. ConfirmedP2 repeated-init registration/worker retention within one process; current driver clears app data and launches fresh per case with one init, so no cross-case carryover demonstrated. Device RPC/HTTP/intake proof still absent; no acceptance.


CONTROL-037 RN exact signed local importb31433e3d7bf2121cb74bead81a68d85d5ecfa9b/basef00e34003d4f35026653c16a945389aa24dd5844/tree4ad01494f28936830d1a876271515a6eb16b6c8c: five native specialist jobs completed, plus native coverage fallback/targeted verifier (external launcher absent). Empty-key/default request defect repaired in private candidate tree4c379e205e0c5d69260453bd60b083a2d4caf66c; root16tests pass and6baseline failures verified separately. Follow-up non-finite float response encoding and repeat-init retained client/worker lifecycle remainP2; response repair assigned. Actual native SDK/runtime, resolved iOS build and full corpus evidence pending; no acceptance.

# Independent Android callback remediation review

Result: no remaining actionable defect found in the scoped candidate.

The candidate contains seven changed files on `f15ab92ed86724dfedac559c45f7a4355f53b594`.
All seven reviewed hashes match the frozen implementation manifest.
Manifest SHA-256: `7aad3b748c80f352533090b1b28e43080e14103a305b6c19e353ce11b5936b73`.

Final signed commit: `cda7955b6361876526fa2035db23dbf88a9e74e1`.
All seven committed file hashes match the reviewed candidate. Exact-head tests and runtime checks are running separately.

The reviewer read AGENTS.md, CONTRIBUTING.md, docs/README.md, sdk-review, and sdk-tests.
The existing branch does not match the prescribed ticket branch pattern. The assigned review proceeded without branch changes.
The review covered the candidate diff, repository snapshot implementation, executor factory, backpressure queue, effect delivery, and feature stop.

## Findings and decisions

| Scope | Evidence and conclusion |
| --- | --- |
| Invalid-context cleanup | DatadogFlagsClient.kt:134–135 reads getAssignmentsSnapshot under telemetryLock. DefaultFlagsRepository reads its AtomicReference without a persistence wait. This addresses 4355492717. |
| Executor lifetime | FlagsClient.kt creates a dispatcher per client. Each drain creates a fresh core worker and calls shutdown after submission. The dispatcher retains no idle worker. This addresses 4355492722. |
| Backpressure | EvaluationCallbackDispatcher.kt:23–38 stores callbacks in its own queue and submits one task per fresh worker. Core's IGNORE_NEWEST cannot discard a burst of callback tasks because that burst never enters the core queue. This addresses 4355492726 for normal dispatch. |
| Serial and reentrant drain | Enqueue and the empty-queue/draining reset use the same lock. A concurrent callback either joins the existing drain or starts a new drain after the prior queue becomes empty. User code executes outside the lock. Reentrant callbacks append in FIFO order. |
| Feature stop | Accepted callbacks remain in the dispatcher and finish on the already submitted drain. Worker shutdown does not discard its active task. The stop test confirms delivery after FlagsFeature.onStop clears registered clients. |
| Worker startup failure | An intermediate candidate left draining true after createWorker threw. This was reported and fixed. Rejection and SecurityException now reset scheduling and log the failure. Pending callbacks remain available to a later dispatch. |
| Safe-call order | ParsePosition now follows java.security and precedes java.util. The new ArrayDeque Runnable overload is beside the existing Function0 overload. This addresses 4355492733. |

## Executed evidence inspected

The implementation worker executed these checks. The independent reviewer read the XML files and final static-check log.

| Suite | Debug | Release | Failures / errors / skips |
| --- | ---: | ---: | --- |
| Native Flags | 661 | 661 | 0 / 0 / 0 |
| OpenFeature | 82 | 82 | 0 / 0 / 0 |
| Single-FIT Flags | 148 | 148 | 0 / 0 / 0 |
| Total | 891 | 891 | 0 / 0 / 0 |

New tests cover nonblocking cleanup, worker shutdown, callback retention, worker recreation, feature stop, FIFO reentry, callback exceptions, submission denial, and drain-exit races.
The race test uses latches and bounded waits. It verifies a maximum of one active callback and eventual worker termination.

The full test run first failed its separate Detekt task on an undeclared ArrayDeque overload.
The corrected static-check run passed. No behavioral source change followed the successful test executions.

The baseline emulator receipt at the published base records nine submitted callbacks, two delivered callbacks, seven dropped tasks, and one surviving callback worker.
The final candidate emulator run is deferred to the signed commit. This review does not claim that native result yet.

## Boundaries

- Worker startup denial or rejected submission has no automatic retry. Pending callbacks require a later dispatch.
- The pending queue is unbounded. A blocked customer callback delays later callbacks and retains their memory.
- Accepted callbacks drain after stop. Calls on a retained stopped client receive no additional lifecycle guarantee.
- Callback scheduling, queue progress, and worker shutdown are outside the Lean contract claims.
- The reviewer changed no production source, tests, Git state, CI state, or external review thread.
- The unrelated `.mcp.json merge refused / Repository not found` output was not produced by this reviewer.

Detailed hashes and inspected XML receipts are in `callback-review-candidate.json`.

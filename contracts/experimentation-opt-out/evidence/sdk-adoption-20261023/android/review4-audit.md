The four review findings are valid at `f15ab92ed86724dfedac559c45f7a4355f53b594`. The first implementation pass did not cover these paths. Earlier receipts remain unchanged.

1. Invalid-context telemetry cleanup called `getEvaluationContext()`. The real repository waits up to 100 ms for persistence there. The new regression detected that getter call. It did not measure a 100 ms stall. Cleanup now reads the nonblocking assignments snapshot under the shared policy lock.
2. The core factory created the callback executor but did not own its shutdown. The baseline emulator observed one callback thread alive after SDK stop and a bounded join. The new dispatcher shuts down each fresh worker in a finally block after submitting its drain.
3. With real core capacity one and IGNORE_NEWEST, the baseline delivered two of nine callbacks. The core reported seven dropped tasks. OpenFeature continuation suspension follows from its callback-based bridge; the baseline probe itself used native callbacks. The dispatcher now keeps pending completions in its own queue and submits one drain task to each fresh core worker.
4. ParsePosition was before java.lang in the safe-call list. It now follows java.lang/reflection and precedes java.util. The new Runnable queue overload is listed beside the existing Function0 overload.

The corrected baseline regression run failed all four focused probes for the expected reasons. The first test harness attempt omitted the mocked HTTP factory; that setup failure is retained separately. Candidate tests add serial order, callback reentry, drain-exit races, submission failure recovery, worker creation denial recovery, and accepted completion delivery after feature stop.

The dispatcher owns accepted completions until they drain. A worker receives shutdown immediately after submission. Shutdown permits its accepted drain task to finish. SDK stop does not interrupt a customer callback or wait for that callback. Calls on a retained client after SDK stop receive no new lifecycle guarantee.

The pending queue is unbounded. A blocked callback delays later serial callbacks and retains their memory. If worker creation is denied or submission is rejected, pending completions wait for the next dispatch. No automatic retry or caller-thread fallback is provided. Shutdown denial is logged. Normal Android execution has no SecurityManager; exception tests cover the defensive paths.

These are native scheduling and lifecycle properties. The Lean model does not prove Android I/O, executor ownership, scheduling, resource failures, or thread termination. The shared acceptance policy and pinned 187-case profile are unchanged.

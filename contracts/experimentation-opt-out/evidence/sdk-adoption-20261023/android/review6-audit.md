# Callback startup recovery and asynchronous example

Review roots: 4355800957 and 4355800964.

## Confirmed defects

A failed callback-worker creation or submission left accepted callbacks queued. Only a later external execute call retried delivery. A sole provider-initialization callback could therefore remain pending indefinitely.

The README resolved a flag immediately after an asynchronous context update. That code could read the application default before acknowledged assignments arrived.

## Implementation

Commit 6e5fe6cf6266a5d965a44a7f1958f1bfe1fcf735 retains one drain reservation after startup failure. It posts one worker-start retry to the application main looper after one second. Repeated startup failures schedule another delayed attempt. New completions join the same pending queue.

The retry runs worker-start code only. Customer callbacks remain on core-created background workers. Each created worker receives one drain task and is shut down in a finally block. The first worker error is logged once per drain. A rejected looper post receives a separate diagnostic.

The README resolves the flag in onSuccess. It shows an explicit failure callback and states that callbacks run in the background.

## Proof boundaries

Three sole-callback regressions cover creation denial, submission denial, and submission rejection. Reinstating the former failed-start implementation makes all three tests fail. Additional regressions cover repeated failures without log flooding, concurrent enqueue during retry scheduling, and rejected retry posting.

These are Kotlin JVM tests with injected workers and retry scheduling. They do not prove Android looper wiring or actual operating-system failure behavior. The separate emulator receipt records real main-looper scheduling and core-worker delivery with injected initial failures.

No Lean theorem proves callback retry, Android scheduling, or worker lifetime. Shared model and profile checks retain their own policy and response-validation scope.

## Remaining limits

Retries require the application main looper to process messages and the operating system eventually to permit a worker. Permanent thread denial cannot produce a background callback. Retry frequency is bounded at one attempt per second, and the pending queue remains intact.

If the looper rejects posting during process or looper shutdown, the dispatcher logs that boundary and retains pending work. It does not run customer callbacks on the caller, fetch thread, or looper. No delivery after process termination is promised.

A customer callback that blocks still retains an unbounded pending queue. Existing accepted callbacks survive SDK feature stop. This change adds no guarantee for new calls on a retained client after stop.

The documentation gate could not run because the provisioned Python environment lacks factorykit. This is a tool gap, not a passing documentation check. Source review confirms the asynchronous example now resolves after success.

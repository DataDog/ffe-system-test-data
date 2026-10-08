# Dependent flag fixture decisions

Status: provisional executable contract for the initial Node server SDK slice.

This corpus keeps every initial dependent-flag scenario in the existing
`ufc-config.json`. Existing consumers can therefore continue loading one UFC
document and every file in `evaluation-cases/`. Multiple UFC payload selection
is deferred until a case requires a different global evaluator configuration.

The shared document sets `evaluatorParams.maxDependencyDepth` to `2`. This
allows the same payload to prove successful evaluation at depths 0, 1, and 2,
and rejection of a third dependency edge.

## Decisions used by the fixtures

- The root flag is depth 0 and the configured maximum is inclusive.
- An omitted `flagEvaluation.property` means `variant_key`; the explicit form
  is also accepted.
- Dependent conditions exercise the four supported string operators:
  `ONE_OF`, `NOT_ONE_OF`, `MATCHES`, and `NOT_MATCHES`. Their value semantics
  remain the ordinary UFC operator semantics.
- Conditions are evaluated in declaration order and short-circuit. An
  unreached missing prerequisite is not an error.
- Completed prerequisite evaluations are memoized per root call. Repeated
  references produce one prerequisite exposure and one prerequisite evaluation
  event.
- A fatal graph-resolution failure aborts the entire root evaluation. The root
  returns the caller default with `reason: ERROR` and a normalized error code.
- Missing prerequisites propagate `FLAG_NOT_FOUND`. Cycle and maximum-depth
  failures currently normalize to `GENERAL` at the public SDK boundary.
- Exposure candidates are buffered until the graph succeeds. Fatal failure
  discards every root and prerequisite exposure candidate, including those
  produced by successful prerequisites reached before the failure.
- Evaluation telemetry is not transactional. Successfully completed nodes
  retain their evaluation events, and every affected ancestor (including the
  root) emits an error evaluation as the failure propagates. A missing key or
  rejected dependency edge has no delivered flag node, so these fixtures do
  not require a separate evaluation event for it.
- Successful trees emit ordinary exposure and evaluation events for reached,
  assigned prerequisites and for the root. Event ordering is not asserted
  because collection and transport may batch events.

## Deliberately deferred

- Different UFC payloads per evaluation case. The current single payload is
  sufficient for today's depth boundary and preserves every existing consumer.
- Timing constants. Cluster and SDK harnesses own bounded waiting and settling;
  environment-sensitive durations are not part of the semantic contract.
- Test-only traversal output. Memoization and short-circuiting are asserted
  through externally observable results and event counts instead.
- Dedicated public error codes for cycle or depth failures. The initial cases
  use OpenFeature `GENERAL`; a later cross-SDK decision may replace it.
- Conditions targeting `reason` or `error_code`. These are supported by the
  draft design but are intentionally kept out of today's minimum end-to-end
  slice until ordinary targetable errors are distinguished from fatal graph
  resolution failures in every evaluator.

## Downstream consumption

A consumer loads `ufc-config.json`, evaluates each case as before, and may read
the optional case-level `expectations` object. Each event matcher contains a
`flag` and optional `_count`. Evaluation-event matchers may additionally carry
an `errorCode`; `null` asserts a successful evaluation, while a non-null code
asserts the propagated error and that the event used the runtime default.
Matchers are unordered and exclusive. An empty exposure array plus
`noUnmatchedEvents: true` asserts atomic exposure rollback; evaluation-event
matchers remain populated for successful prior nodes and affected ancestors.

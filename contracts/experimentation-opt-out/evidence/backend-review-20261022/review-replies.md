# Draft review replies

These replies are local drafts. Publish the implementation and central decision
before replacing this header with verified commit and decision permalinks.
No comment or thread resolution has been posted.

## P1: compiler classification

The intended contract is to exclude randomizing allocations, with `doLog` carrying
that signal from the backend. The compiler now sets it when shard selection can
change the variation or match/fallthrough outcome, including concluded experiments
that still split and ordinary percentage rollouts. Deterministic completed winners
remain `doLog=false`; existing active-experiment and holdout logging stays intact.
This also enables exposures for ordinary randomized allocations. Evaluators retain
the existing `doLog` predicate and future-mode cutoff rule.

## P2: synthetic holdout runner

The runner accepts either logging value for a concluded ordinary winner, while
still checking its variant and requiring exposure logging for active experiments.
The holdout runner and primary-analysis suites pass all 255 tests.

## P3: query parameters

The organization-scoped snapshot query now binds the experiment IDs with
`id = ANY(?::uuid[])` and `pq.Array`, matching the existing holdout query pattern.

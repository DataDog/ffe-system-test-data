# SDK implementation refresh — 2026-10-22

Browser #423 and Go #5666 are merged. Their final reviewed heads are
[`38d611c`](https://github.com/DataDog/openfeature-js-client/commit/38d611cf4c73b9687b97f7da0f8224d2fefab966)
and [`54b5ad7`](https://github.com/DataDog/dd-trace-go/commit/54b5ad7fe9818966d32eeceabb6c048005f077f6).
The [live snapshot](evidence/sdk-refresh-20261022/live-pr-snapshot.json) records merge commits separately.
The [source rescan](evidence/sdk-refresh-20261022/source-review.json) binds inspected production files to those heads.

This refresh precedes the independent implementation reviews of iOS #3338,
Android #4024 and Java #12950. It preserves the existing decision wording,
original decision-setting threads, and historical results. The user's current
request authorizes applying these decisions within those PRs. This is not fleet approval.

## Decisions retained

| Rule | Decisions | Application |
| --- | --- | --- |
| Disabled ignores the attribute; absent differs from malformed | D002, D016 | All three targets; preserve native readiness checks. |
| Parse activation once; retain missing and invalid separately | D003, D004 | Both Java evaluators; mobile delegates allocation evaluation to edge. |
| Invalid activation fails only an effective future-mode evaluation | D004 | Java includes unreachable and ordinary allocations in flag-wide validity. |
| Effective policy controls request options and acknowledgement | D008, D014 | iOS and Android; never use configured mode alone. |
| Context and policy identify usable assignments | D001 | Mobile lifecycle, caches, and delayed responses need native checks. |
| Exclusion and evaluation telemetry are independent | D009 | Preserve subject identity, retained exposures, and telemetry opt-out. |
| Future means strictly earlier activation, not prior enrollment | D011 | Preserve ordinary order; equal, later and unknown activation exclude. |
| Inactive policy skips exclusion operations | D017 | Apply Go's operational rule to Java; validate real call sites separately from timing. |

## Differences that remain explicit

Go uses its existing RFC3339 parser. Browser accepts lowercase delimiters.
The source rescan does not choose a new fleet timestamp grammar. Mobile retains
the browser profile already implemented in its PRs. Java retains its existing
timestamp parser unless a separate, supported contract decision changes it.

D015 describes Go's NoopProvider construction. Java has a different disabled
provider lifecycle. An audit must map that lifecycle before transferring the rule.
The existing doLog defaults also differ on malformed input. This task does not
replace the separate required-boolean work with a new permissive default.

## Pinned work and evidence boundaries

The [adoption plan](evidence/sdk-refresh-20261022/adoption-plan.json) records one
target PR per SDK. The mobile profile includes all 187 parser/request/acknowledgement
cases. The Java profile includes all 90 abstract policy cases. The existing 36-case
D017 profile applies separately. These profiles do not replace platform tests.

Lean proves model properties. Source inspection establishes the inspected code
shape. Native adapters establish finite agreement. Native integration, hosted CI,
human review, release dependencies and deployed behavior remain separate evidence.

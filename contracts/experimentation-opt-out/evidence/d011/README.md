# D011: explain the actual opt-out time

[Go documentation](https://github.com/DataDog/dd-trace-go/pull/5700) at [535d4a3](https://github.com/DataDog/dd-trace-go/commit/535d4a35ef18e1c202b293b5ca55d79259f90492)
and the [shared fixture README](https://github.com/DataDog/ffe-system-test-data/pull/52) at [8aba254](https://github.com/DataDog/ffe-system-test-data/commit/8aba25473785f502de660618ca864fba2ed1e0cc) now say:

> Supply the time the subject opted out. A later cutoff keeps experiments activated
> before that later time eligible, including experiments started after the subject
> opted out. Targeting and schedules still apply.

This is a clarification of [D011 r1](../../decision-history.md#d011), reaffirmed in
[the Go reply](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4352957366) and previously set in
[the browser discussion](https://github.com/DataDog/openfeature-js-client/pull/423#discussion_r4344317522). It adds no new timestamp rejection
or evaluation behavior; broader SDK adoption retains its recorded scope.

[The existing fixture pair](fixture-pair.json) uses an experiment activated on
October 20. A cutoff of October 19 skips that allocation and selects the older
allocation (`1 / SPLIT`); October 21 retains it (`3 / TARGETING_MATCH`). Both
cases pass through the actual Go fixture runner. The complete flag and these two
cases are identical between Go's pinned fixtures and the shared fixture branch.
This verifies this pair; it does not mean Go consumed the entire newer fixture revision.

[The verification receipt](verification.json) records the exact two discovered
native leaf tests, their source pins and [raw log](native-pair.jsonl). The fixture
branch's validator passes 363 cases across 46 files. Independent review found no
issues in the wording or evidence mapping.

The existing [Lean boundary proofs](../../lean/Proofs.lean) cover strict-before
retention and equality exclusion in the abstract policy. Their [previous model
validation](../d017/publication-validation.json) remains historical evidence;
Lean source and corpus are unchanged and were not rerun for this wording change.
The fixture pair alone is not presented as proof against scheduling behavior,
and these proofs do not model enrollment or allocation schedules.

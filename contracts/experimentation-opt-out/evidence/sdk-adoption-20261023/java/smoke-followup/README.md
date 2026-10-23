# Java smoke-test remediation

The five failed hosted smoke jobs report the same exposure test. Each job retried it four times.
The failure is reproducible on signed commit `a4d3dfb21cec0658417d4f3842dc8c8465a27371`.
The test receives 232 exposures and expects 231.

The fixture update adds a return to an earlier assignment for `integer-flag` and subject `5`.
The sequence is `50/50 split / one`, `targeted allocation / three`, then `50/50 split / one`.
The production cache records the last assignment for each flag and subject.
It correctly emits all three transitions.
The smoke helper used a lifetime set and removed the third event from its expectation.

`diagnosis.json` records the exact extra event and confirms that no expected event is missing.
It also records source hashes for the original smoke test and three production cache files.
All four files match merged master `3718fdc518506e5700df8b7d448639971cd3470c`.
This diagnosis uses source comparison and native reproduction. It does not rely on the CI service's failure classification.

The correction changes one smoke-test file. It changes no production code or shared decision.
The helper now records the last assignment per flag and subject.
The intake assertion compares event counts for each flag, subject, allocation, variant, and serial ID.
A dedicated HTTP sequence evaluates standard twice, VIP twice, and standard twice.
The test requires exactly three exposures: standard, VIP, and standard.

The negative control restores lifetime deduplication in the test helper.
It must fail the new sequence because it expects only two exposures.
The source must be restored before final validation.

The earlier a4 runtime, policy, operation, and negative-control receipts remain unchanged.
The new native results apply to a4 plus the recorded test-only patch until the parent signs the correction.
Hosted CI results at a4 remain failed. A passing local reproduction does not change that status.

## Results

- Original signed a4 reproduction: 3 tests, 1 expected failure; 232 exposures versus 231 expected.
- Formatted candidate, JDK 11: 373 passed, 0 failed, 0 skipped; Spotless passed.
- Formatted candidate, JDK 25: 373 passed, 0 failed, 0 skipped; Spotless passed.
- Lifetime-set negative control: 3 tests, 1 expected failure; the regression expected three exposures and received two helper entries.
- Restored signed head `578ffa77cbc52e6d5d8950657a05863a449f59ab`, JDK 25: 4 passed, 0 failed, 0 skipped.
- The exact-head run covers RC advertisement, span enrichment, repeated/returning assignments, and the full fixture exposure intake.

The candidate runs used the exact file later committed in the signed follow-up.
The separate pre-format JDK 25 run passed 373 tests but failed formatting. It does not bind to the final file.
The compact XML omits process output. The baseline failure text is shortened.
`raw-artifacts.json` binds the complete preserved originals with SHA-256 hashes and remote paths.

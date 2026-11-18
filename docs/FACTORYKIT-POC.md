# FactoryKit POC findings

This branch applies [FactoryKit](https://github.com/ddoghq/factorykit) at
`f98a056` to this repository. The goal is to find how far FactoryKit goes for
the FFE shared contract and where it stops. This is a POC. It is not a proposal
to merge.

## What works

| Step | Result |
| --- | --- |
| Read-only onboarding scan | Runs. It reports no existing FactoryKit layers. |
| `setup inspect` and `setup prepare` | Run with `--host claude`. They report the missing Foundation entry. |
| `factoryspec validate` and `factoryspec bindings` | Pass after the fixes listed below. All three nudge and check bindings match. |
| Foundation report and gate | `allow`. The gate gives two advisories on a fixture change. |
| FFE contract nudge | A repository-owned nudge, [`ffe_contract_nudges.py`](../scripts/ffe_contract_nudges.py), fires when a contract path changes. It asks for a KB decision citation. |
| Verification plan | The path rule selects the `precomputed` procedure from the diff. A JSON judgment maps the criterion. |
| Verification run | It runs the same commands as CI through a `command-v1` adapter. |
| Knowledge index | It builds a local index of 229 files. Search for `holdout` and `exposure doLog` returns the relevant fixtures and README sections. |

The verifier found a real mistake in the first demo change. The change edited a
precomputed fixture without regenerating its obfuscated companion.
`precomputed_obfuscation.py --check` failed. After `--write`, the run passed.

## Where it breaks down

1. **Hidden schema dependencies.** Validation needs
   `verification-contract.schema.json`, and planning needs
   `verification-planner-result.schema.json`. Both must be tracked at fixed
   paths, but the Foundation starter does not include them. Each one failed
   with a "path is not tracked" error.
2. **Repository nudge module path.** A module name such as
   `ffe_contract_nudges` resolves to a file at the repository root. A module in
   `scripts/` needs the dotted name `scripts.ffe_contract_nudges`.
3. **Directory links are false positives.** The Foundation report marks links
   to directories, such as `evaluation-cases/`, as missing targets. The
   directories exist.
4. **Ambient interpreter.** `command-v1` runs `python3` from `PATH`. On a Mac
   with system Python 3.9, `jsonschema` is missing, and all checks fail. The
   run passed only with an interpreter that has `jsonschema`. A prerequisite or
   a pinned environment is necessary.
5. **Planner host.** `--planner` accepts only `codex`. It also needs a planner
   skill in the contract. This POC uses a hand-written JSON judgment instead.
6. **Large fixtures.** Knowledge `validate` fails on four scale-suite files
   larger than 512 KiB. Search still works on the other files.
7. **Single repository scope.** FactoryKit verifies a diff in this repository
   only. It cannot verify that an SDK PR, for example in `dd-sdk-android`,
   conforms to these fixtures. The cross-repo loop still needs
   `ci/run-downstream-conformance.sh` or a hub repository.
8. **No KB connection.** The nudge only reminds people about the FFE LEAN KB.
   FactoryKit cannot read decisions from Google Sheets. Its Knowledge layer
   indexes tracked Git files only.

## Files in this POC

- `factoryspec.yaml`, `factory/` descriptors, and schemas
- [`scripts/foundation_check.py`](../scripts/foundation_check.py): the Foundation entry
- [`scripts/factorykit_fixture_check.py`](../scripts/factorykit_fixture_check.py): CI validators as a `command-v1` check
- [`scripts/ffe_contract_nudges.py`](../scripts/ffe_contract_nudges.py): the contract decision nudge
- [`docs/README.md`](README.md) and [`docs/VERIFICATION.md`](VERIFICATION.md)

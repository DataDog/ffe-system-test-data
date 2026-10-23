# Native Go D004 receipt

Implementation: [c5fec6a009ff](https://github.com/DataDog/dd-trace-go/commit/c5fec6a009ffa29bf53f5377a21856c7c4aa5f56).
Decision and results: [Go review reply](https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4351454041).

`native-receipt.json` records exact commands, source/patch/adapter hashes, toolchain,
the pinned fixture submodule and test results. `independent-review.json` records
the reviewed file hashes and scope. `publication.json` verifies every PR commit.
The policy input is all 90 unchanged policy rows from the prior pinned contract;
`profile.json` explains why the 223 other-family rows do not apply to this change.
Neither those exclusions nor passing policy cases establish timestamp grammar parity.

To replay the adapter, check out the exact implementation SHA, initialize its
fixture submodule, and use Go 1.26.0. From that SDK checkout, set `D004_EVIDENCE`
to this directory and run:

```sh
python3 - <<'PY'
import hashlib, json, os, pathlib, subprocess, tempfile
evidence = pathlib.Path(os.environ['D004_EVIDENCE']).resolve()
sdk = pathlib.Path.cwd().resolve()
profile_pin = 'f3f4b3d5f0010d80b18491e29323f8e083bf666835399b7d722ef7e67d33f830'
assert hashlib.sha256((evidence / 'profile.json').read_bytes()).hexdigest() == profile_pin
profile = json.loads((evidence / 'profile.json').read_text())
receipt = json.loads((evidence / 'native-receipt.json').read_text())
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == receipt['source_sha']
for name, pin in json.loads((evidence / 'independent-review.json').read_text())['file_sha256'].items():
    assert hashlib.sha256((sdk / 'openfeature' / name).read_bytes()).hexdigest() == pin
assert hashlib.sha256((evidence / 'policy-cases.json').read_bytes()).hexdigest() == profile['policy_cases_sha256']
assert hashlib.sha256((evidence / 'conformance_test.go.txt').read_bytes()).hexdigest() == receipt['adapter_sha256']
with tempfile.TemporaryDirectory(prefix='go-d004-') as tmp:
    overlay = pathlib.Path(tmp) / 'overlay.json'
    overlay.write_text(json.dumps({'Replace': {
        str(sdk / 'openfeature/zz_lean_d004_conformance_test.go'): str(evidence / 'conformance_test.go.txt')
    }}))
    env = dict(os.environ, LEAN_D004_CASES=str(evidence / 'policy-cases.json'))
    subprocess.run(['go', 'test', '-overlay=' + str(overlay), './openfeature/',
                    '-run', '^TestLeanD004PolicyConformance$', '-count=1', '-v'], env=env, check=True)
PY
```

The runner asserts 90 discovered corpus rows. Variant checks distinguish ordinary
fallback delivery from simply returning the default. `negative-controls.json`
describes the two source overlays that the native regression tests rejected.
Full package and race results include 278 top-level tests each; 1,631 includes
their subtests and is not a count of independent scenarios. No CI, system-test
rerun at this SHA, performance or deployed-behavior claim is made.

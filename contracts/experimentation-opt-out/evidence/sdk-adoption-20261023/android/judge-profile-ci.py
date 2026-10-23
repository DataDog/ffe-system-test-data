#!/usr/bin/env python3
"""Compare emitted native observations with the independently pinned mobile profile."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CENTRAL = HERE.parents[1] / 'contract/contracts/experimentation-opt-out/evidence/sdk-refresh-20261022'
PINS = {
    'mobile-precompute-v1.json': 'e7dd38b344dfd74822d567828add9107ac642ce72df5341bef42fc0d3891dc5f',
    'mobile-precompute-v1-cases.json': '16ab568b1d642322fbe0a066219c5002684439eac4f8824464e7fbc7b14df528',
}
for name, wanted in PINS.items():
    assert hashlib.sha256((CENTRAL / name).read_bytes()).hexdigest() == wanted
cases = json.loads((CENTRAL / 'mobile-precompute-v1-cases.json').read_text())
observations = [json.loads(line) for line in (HERE / 'exact-f15ab92-profile-observations.jsonl').read_text().splitlines()]
expected = {row['id']: row['expected'] for row in cases}
assert len(observations) == len(expected) == 187
assert set(expected) == {row['id'] for row in observations}
mismatches = [
    {'id': row['id'], 'expected': expected[row['id']], 'observed': row['observed']}
    for row in observations if row['observed'] != expected[row['id']]
]
result = {
    'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'source_status': subprocess.check_output(['git', 'status', '--porcelain'], text=True),
    'profile_pins': PINS,
    'cases': 187,
    'passed': 187 - len(mismatches),
    'mismatches': mismatches,
    'observations_sha256': hashlib.sha256((HERE / 'exact-f15ab92-profile-observations.jsonl').read_bytes()).hexdigest(),
    'scope': 'Actual production parser, request factory and response mapper; source-linked composition, mocked logger/context; no live HTTP or lifecycle execution.',
}
(HERE / 'exact-f15ab92-profile187-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
sys.exit(bool(mismatches))

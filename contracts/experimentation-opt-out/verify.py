#!/usr/bin/env python3
"""Check a pinned decision proposal and replay its Lean oracle; no SDK/fleet claim."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
history_spec = importlib.util.spec_from_file_location('decision_history', ROOT / 'decision_history.py')
decision_history = importlib.util.module_from_spec(history_spec)
history_spec.loader.exec_module(decision_history)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semver_delivery_cases(root, manifest):
    profile = manifest['semver_delivery_profile']
    if profile['id'] != 'authored-semver-delivery-v1' or profile['decision_revisions'] != {'D021': 1}:
        raise ValueError('Unexpected SemVer delivery profile')
    if profile['corpus'] not in manifest['files']:
        raise ValueError('SemVer corpus is not frozen in the manifest')
    rows = json.loads((root / profile['corpus']).read_text())
    ids = [row['id'] for row in rows]
    if len(set(ids)) != len(ids) or ids != profile['case_ids'] or len(rows) != profile['case_count']:
        raise ValueError('SemVer corpus inventory differs from reviewed profile')
    expected_keys = {'primaryContains', 'compatibilityContains', 'semverRetained'}
    for row in rows:
        if row['decision_ids'] != ['D021'] or set(row['expected']) != expected_keys:
            raise ValueError('Unexpected SemVer decision or expected fields')
        if any(type(value) is not bool for value in row['expected'].values()):
            raise ValueError('SemVer outputs must be booleans')
    return rows


def inactive_path_cases(root, manifest):
    profile = manifest.get('operational_profile')
    if not profile or profile['id'] != 'inactive-path-v1':
        raise ValueError('Missing reviewed inactive-path operational profile')
    name = profile['corpus']
    if name not in manifest['files']:
        raise ValueError('Operational corpus is not frozen in the manifest')
    rows = [json.loads(line) for line in (root / name).read_text().splitlines()]
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)) or ids != profile['case_ids'] or len(rows) != profile['case_count']:
        raise ValueError('Operational corpus inventory differs from reviewed profile')
    for row in rows:
        if row['decision_ids'] != ['D017'] or row['kind'] != 'allocation-check-trace':
            raise ValueError('Unexpected operational decision or case kind')
        expected = row['expected']
        if set(expected) != {'error', 'excluded', 'exclusionChecks'} or type(expected['exclusionChecks']) is not int or expected['exclusionChecks'] < 0:
            raise ValueError('Operational oracle must include exclusion-check counts')
    return rows


def activation_cases(root, manifest):
    profile = manifest.get('activation_profile')
    if not profile or profile['id'] != 'activation-producer-v1':
        raise ValueError('Missing reviewed activation producer profile')
    name = profile['corpus']
    if name not in manifest['files']:
        raise ValueError('Activation producer corpus is not frozen')
    rows = [json.loads(line) for line in (root / name).read_text().splitlines()]
    ids = [r['id'] for r in rows]
    if len(set(ids)) != len(ids) or ids != profile['case_ids'] or len(rows) != profile['case_count']:
        raise ValueError('Activation producer corpus inventory differs')
    for row in rows:
        if row['kind'] not in {'sync-activation', 'holdout-policy'} or not set(row['decision_ids']) <= {'D011', 'D012'}:
            raise ValueError('Unknown activation producer case')
    by_id = {r['id']: r['expected'] for r in rows}
    controls = {'sync-028': 2, 'sync-024': None, 'sync-030': None, 'sync-029': None,
                'sync-012': None, 'sync-044': 10, 'holdout-future-before': False,
                'holdout-future-missing': True, 'holdout-immediate-before': True}
    if any(by_id.get(key) != expected for key, expected in controls.items()):
        raise ValueError('Independent activation producer expectation differs')
    return rows


def check_bundle(root, expected_manifest):
    manifest_path = root / 'manifest.json'
    if sha(manifest_path) != expected_manifest:
        raise ValueError('Manifest differs from independently supplied pin')
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest['files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Manifest path escapes bundle')
        if sha(root / name) != expected:
            raise ValueError(f'Changed or missing acceptance input: {name}')
    rows = [json.loads(line) for line in (root / 'corpus/browser-proposal.jsonl').read_text().splitlines()]
    ids = [row['id'] for row in rows]
    if len(set(ids)) != len(ids) or ids != manifest['case_ids']:
        raise ValueError('Corpus inventory differs from pinned IDs')
    if len(rows) != manifest['case_count'] or dict(Counter(r['kind'] for r in rows)) != manifest['counts_by_kind']:
        raise ValueError('Corpus counts differ')
    controls = json.loads((root / 'corpus/independent-controls.json').read_text())
    by_id = {row['id']: row for row in rows}
    for key, expected in controls.items():
        if by_id[key]['expected'] != expected:
            raise ValueError(f'Independent expectation disagrees: {key}')
    decisions = json.loads((root / 'decisions.json').read_text())
    decision_ids = [d['id'] for d in decisions['decisions']]
    inactive_path_cases(root, manifest)
    activation_cases(root, manifest)
    for key, revision in manifest['activation_profile']['decision_revisions'].items():
        if next((d['revision'] for d in decisions['decisions'] if d['id'] == key), None) != revision:
            raise ValueError('Activation profile refers to a different decision revision')
    semver_delivery_cases(root, manifest)
    if next((d['revision'] for d in decisions['decisions'] if d['id'] == 'D021'), None) != 1:
        raise ValueError('SemVer profile refers to a different decision revision')
    for key, revision in manifest['operational_profile']['decision_revisions'].items():
        if next((d['revision'] for d in decisions['decisions'] if d['id'] == key), None) != revision:
            raise ValueError('Operational profile refers to a different decision revision')
    if len(set(decision_ids)) != len(decision_ids):
        raise ValueError('Duplicate decision IDs')
    if decisions['status'] != 'proposal' or decisions['fleet_approved'] is not False:
        raise ValueError('This bundle has no authority to claim fleet approval')
    history = json.loads((root / decisions['validation_history_file']).read_text())
    decision_history.validate(root, decisions, history)
    if (root / 'decision-history.md').read_text() != decision_history.render(decisions, history):
        raise ValueError('Linked decision history is stale; regenerate it')
    for row in rows:
        if not set(row['decision_ids']) <= set(decision_ids):
            raise ValueError(f'Unknown decision in {row["id"]}')
    feedback = json.loads((root / 'feedback.json').read_text())
    snapshot = json.loads((root / 'evidence/go-review-snapshot.json').read_text())
    known = {c['id'] for pr in snapshot['pull_requests'] for kind in
             ('inline_comments', 'reviews', 'conversation_comments') for c in pr[kind]}
    mapped = set()
    for item in feedback['items']:
        if not set(item['sources']) <= known or not set(item['decision_ids']) <= set(decision_ids):
            raise ValueError(f'Unknown feedback reference: {item["id"]}')
        mapped.update(item['sources'])
    for pr in snapshot['pull_requests']:
        for thread in pr['threads']:
            if not set(thread['comment_ids']) <= mapped:
                raise ValueError(f'Unclassified review thread: {thread["id"]}')
    return manifest, rows


def replay(root, lean, rows):
    lean = str(Path(lean).resolve())
    version = subprocess.check_output([lean, '--version'], text=True).strip()
    if not re.search(r'\bversion 4\.19\.0\b', version):
        raise ValueError(f'Expected Lean 4.19.0, got {version}')
    with tempfile.TemporaryDirectory(prefix='ffe-lean-decisions-') as tmp:
        build = Path(tmp)
        env = dict(os.environ, LEAN_PATH=str(build))
        modules = ('Contract', 'Proofs', 'Oracle', 'Review', 'InactivePath', 'InactiveOracle', 'BackendReview', 'ActivationReview', 'ActivationOracle', 'SemverDelivery', 'SemverOracle')
        for name in modules:
            shutil.copyfile(root / f'lean/{name}.lean', build / f'{name}.lean')
        logs = []
        for name in modules:
            run = subprocess.run([lean, '-o', f'{name}.olean', f'{name}.lean'], cwd=build,
                                 env=env, text=True, capture_output=True)
            log = run.stdout + run.stderr
            if run.returncode:
                raise ValueError(f'{name}.lean compilation failed:\n{log}')
            if 'sorry' in log or 'warning:' in log:
                raise ValueError(f'Proof warning or hole: {log}')
            logs.append(log)
        # Inspect every theorem, rather than relying on a hand-maintained #print list.
        audits = ['import Proofs', 'import Review', 'import InactivePath', 'import BackendReview', 'import ActivationReview', 'import SemverDelivery']
        for file, namespace in [('Proofs', 'PR423'), ('Review', 'GoReview'), ('InactivePath', 'InactivePath'), ('BackendReview', 'BackendReview'), ('ActivationReview', 'ActivationReview'), ('SemverDelivery', 'SemverDelivery')]:
            for theorem in re.findall(r'^theorem\s+(\w+)', (build / f'{file}.lean').read_text(), re.M):
                audits.append(f'#print axioms {namespace}.{theorem}')
        (build / 'Audit.lean').write_text('\n'.join(audits) + '\n')
        audit = subprocess.check_output([lean, 'Audit.lean'], cwd=build, env=env, text=True)
        for axiom_set in re.findall(r'depends on axioms: \[([^]]*)\]', audit):
            if set(x.strip() for x in axiom_set.split(',') if x.strip()) - {'propext', 'Quot.sound'}:
                raise ValueError(f'Unexpected trusted axiom: {axiom_set}')
        requests = []
        for row in rows:
            request = {k: v for k, v in row.items() if k not in ('expected', 'decision_ids')}
            request['profile'] = 'proposal'
            requests.append(json.dumps(request))
        run = subprocess.run([lean, '--run', 'Oracle.lean'], input='\n'.join(requests)+'\n',
                             cwd=build, env=env, text=True, capture_output=True, check=True)
        actual_rows = [json.loads(line) for line in run.stdout.splitlines()]
        actual = {r['id']: r['observed'] for r in actual_rows}
        expected = {r['id']: r['expected'] for r in rows}
        if len(actual) != len(actual_rows) or actual != expected:
            raise ValueError('Oracle output missing, duplicated or different from frozen expectations')
        operational = inactive_path_cases(root, json.loads((root / 'manifest.json').read_text()))
        run = subprocess.run([lean, '--run', 'InactiveOracle.lean'],
                             input=''.join(json.dumps({k: v for k, v in row.items()
                                         if k not in ('expected', 'decision_ids')})+'\n' for row in operational),
                             cwd=build, env=env, text=True, capture_output=True, check=True)
        observed = [json.loads(line) for line in run.stdout.splitlines()]
        actual = {row['id']: row['observed'] for row in observed}
        if len(actual) != len(observed) or actual != {row['id']: row['expected'] for row in operational}:
            raise ValueError('Operational oracle results or exclusion-check counts differ')
        activation = activation_cases(root, json.loads((root / 'manifest.json').read_text()))
        run = subprocess.run([lean, '--run', 'ActivationOracle.lean'],
                             input=''.join(json.dumps({k: v for k, v in row.items()
                                         if k not in ('expected', 'decision_ids')})+'\n' for row in activation),
                             cwd=build, env=env, text=True, capture_output=True, check=True)
        observed = [json.loads(line) for line in run.stdout.splitlines()]
        actual = {row['id']: row['observed'] for row in observed}
        if len(actual) != len(observed) or actual != {row['id']: row['expected'] for row in activation}:
            raise ValueError('Activation producer oracle results differ')
        semver = semver_delivery_cases(root, json.loads((root / 'manifest.json').read_text()))
        run = subprocess.run([lean, '--run', 'SemverOracle.lean'],
                             input=''.join(json.dumps({'id': row['id'], 'args': row['args']})+'\n' for row in semver),
                             cwd=build, env=env, text=True, capture_output=True, check=True)
        observed = [json.loads(line) for line in run.stdout.splitlines()]
        actual = {row['id']: row['observed'] for row in observed}
        if len(actual) != len(observed) or actual != {row['id']: row['expected'] for row in semver}:
            raise ValueError('SemVer oracle results differ')
        return {'lean_version': version, 'theorems_audited': len(audits)-6,
                'activation_oracle_cases': len(activation), 'semver_oracle_cases': len(semver),
                'oracle_cases': len(rows), 'operational_oracle_cases': len(operational), 'axiom_audit': audit,
                'native_sdk_tests_run': False, 'fleet_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    manifest, rows = check_bundle(ROOT, args.manifest_sha256)
    print(json.dumps(replay(ROOT, args.lean, rows), indent=2))


if __name__ == '__main__':
    main()

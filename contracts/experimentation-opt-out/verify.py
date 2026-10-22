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
        for name in ('Contract', 'Proofs', 'Oracle', 'Review'):
            shutil.copyfile(root / f'lean/{name}.lean', build / f'{name}.lean')
        logs = []
        for name in ('Contract', 'Proofs', 'Oracle', 'Review'):
            run = subprocess.run([lean, '-o', f'{name}.olean', f'{name}.lean'], cwd=build,
                                 env=env, text=True, capture_output=True)
            log = run.stdout + run.stderr
            if run.returncode:
                raise ValueError(f'{name}.lean compilation failed:\n{log}')
            if 'sorry' in log or 'warning:' in log:
                raise ValueError(f'Proof warning or hole: {log}')
            logs.append(log)
        # Inspect every theorem, rather than relying on a hand-maintained #print list.
        audits = ['import Proofs', 'import Review']
        for file, namespace in [('Proofs', 'PR423'), ('Review', 'GoReview')]:
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
        return {'lean_version': version, 'theorems_audited': len(audits)-2,
                'oracle_cases': len(rows), 'axiom_audit': audit,
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

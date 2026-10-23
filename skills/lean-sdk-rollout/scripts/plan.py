#!/usr/bin/env python3
"""Validate ownership/pins and produce bounded dependency waves; never execute or publish."""
import argparse
import json
from pathlib import PurePosixPath
import re

def overlap(a, b):
    pa, pb = PurePosixPath(a), PurePosixPath(b)
    return pa == pb or pa in pb.parents or pb in pa.parents

def plan(bundle, slots=3):
    if not isinstance(slots, int) or slots < 1:
        raise ValueError('slots must be positive')
    tasks = bundle['implementations']
    if not tasks:
        raise ValueError('No implementation owners')
    profiles = bundle.get('reviewed_profiles', {})
    if not profiles or any(not re.fullmatch('[0-9a-f]{64}', digest) for digest in profiles.values()):
        raise ValueError('Reviewed profile manifest hashes are required')
    ids = [task['id'] for task in tasks]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate implementation owner; combine language labels in targets')
    for task in tasks:
        profile = task.get('profile')
        if profile not in profiles or task.get('profile_manifest_sha256') != profiles[profile]:
            raise ValueError('Unknown profile or unreviewed profile manifest hash')
        if not re.fullmatch('[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', task['repository']) or task['repository'].endswith('.git'):
            raise ValueError('Repository must be canonical owner/repo, without URL or .git')
        if not re.fullmatch('[0-9a-f]{40}', task['base_sha']):
            raise ValueError('Each base must be an immutable commit SHA')
        for key in ('contract_sha256', 'corpus_sha256'):
            if not re.fullmatch('[0-9a-f]{64}', task[key]):
                raise ValueError('Missing content pin: ' + key)
        if not task.get('targets') or not task.get('owned_paths'):
            raise ValueError('Targets and ownership are required')
        for path in task['owned_paths']:
            if not path or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts or any(c in path for c in '*?[]\\'):
                raise ValueError('Ownership requires literal relative paths inside the repository')
        if set(task.get('depends_on', [])) - set(ids):
            raise ValueError('Unknown dependency')
    for index, left in enumerate(tasks):
        for right in tasks[index + 1:]:
            if left['repository'].lower() == right['repository'].lower() and any(
                    overlap(a, b) for a in left['owned_paths'] for b in right['owned_paths']):
                raise ValueError('Overlapping ownership: ' + left['id'] + ' / ' + right['id'])
    done = set()
    waves = []
    while len(done) < len(tasks):
        ready = [task['id'] for task in tasks if task['id'] not in done
                 and set(task.get('depends_on', [])) <= done]
        if not ready:
            raise ValueError('Dependency cycle')
        wave = ready[:slots]
        waves.append(wave)
        done.update(wave)
    return {'mode': 'local-diff', 'waves': waves, 'implementation_count': len(tasks),
            'target_count': len({target for task in tasks for target in task['targets']}),
            'publication_authorized': False,
            'note': 'This plan grants no commit, push, PR, merge, release or external-write permission.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle')
    parser.add_argument('--slots', type=int, default=3)
    args = parser.parse_args()
    with open(args.bundle) as handle:
        print(json.dumps(plan(json.load(handle), args.slots), indent=2))

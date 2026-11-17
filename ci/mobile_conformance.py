#!/usr/bin/env python3
# Unless explicitly stated otherwise, all files in this repository are licensed under the
# Apache License Version 2.0. This product includes software developed at Datadog
# (https://www.datadoghq.com/). Copyright 2025-Present Datadog, Inc.
"""Preview base/head precomputed fixtures against one disposable native SDK checkout."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location(
    'snapshot_importer', Path(__file__).with_name('sync-precomputed-fixtures.py'))
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)

DESTINATIONS = {
    'ios': 'DatadogFlags/Tests/Fixtures/precomputed',
    'android': 'reliability/single-fit/flags/src/test/resources/precomputed',
}
ANDROID_MODULE = 'reliability/single-fit/flags'
ANDROID_TEST = 'com.datadog.android.flags.integration.CanonicalPrecomputedTest'


def install_snapshot(fixtures, sha, sdk, platform):
    # Reuse the byte-preserving importer, including for bases predating its CLI.
    # Never accept a configurable replacement destination in a downstream repo.
    content = importer.snapshot(fixtures, sha)
    destination = sdk / DESTINATIONS[platform]
    if destination.resolve() != destination or any(p.is_symlink() for p in destination.parents):
        raise ValueError('Snapshot destination must not contain symlinks')
    if destination.exists():
        if not (destination / 'SOURCE.json').is_file():
            raise ValueError('Refusing to replace a directory without snapshot provenance')
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for name, data in content.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return len(json.loads(content['index.json']))


def native_command(platform, output):
    if platform == 'android':
        return ['./gradlew', ':reliability:single-fit:flags:cleanTestDebugUnitTest',
                ':reliability:single-fit:flags:testDebugUnitTest', '--tests', ANDROID_TEST,
                '--no-daemon', '--no-build-cache', '--console=plain']
    return ['xcodebuild', '-workspace', 'Datadog.xcworkspace', '-scheme', 'DatadogFlags',
            '-destination', os.environ['IOS_DESTINATION'],
            '-only-testing:DatadogFlagsTests/CanonicalPrecomputedTests',
            '-resultBundlePath', str(output / 'tests.xcresult'),
            'CODE_SIGNING_ALLOWED=NO', 'test']


def android_results(directory):
    cases = []
    for file in directory.glob('TEST-*.xml'):
        cases.extend(ET.parse(file).getroot().iter('testcase'))
    # Require actual canonical cases, not an unrelated successful test report.
    cases = [c for c in cases if c.get('classname') == ANDROID_TEST]
    executed = [c for c in cases if c.find('skipped') is None]
    failures = [c for c in executed if c.find('failure') is not None or c.find('error') is not None]
    return {'executed': len(executed), 'failed': len(failures),
            'failures': [c.get('name') for c in failures]}


def ios_results(output):
    raw = subprocess.check_output(['xcrun', 'xcresulttool', 'get', 'test-results', 'summary',
                                   '--path', str(output / 'tests.xcresult')])
    (output / 'test-summary.json').write_bytes(raw)
    result = json.loads(raw)
    return {'executed': result['passedTests'] + result['failedTests'],
            'failed': result['failedTests'], 'failures': result.get('testFailures', [])}


def test_status(exit_code, report):
    if report['executed'] == 0:
        return 'no-tests' if exit_code == 0 else 'build-or-runner-failure'
    if report['failed']:
        return 'test-failure'
    return 'pass' if exit_code == 0 else 'build-or-runner-failure'


def compare(base, head):
    if base == head == 'pass':
        return 'compatible'
    if base == 'pass' and head == 'test-failure':
        return 'new-regression'
    if base == 'test-failure' and head == 'pass':
        return 'improvement'
    if base == head == 'test-failure':
        return 'inconclusive-both-fail'
    return 'inconclusive-setup-or-execution'


def run_revision(args, label, sha):
    output = args.output / label
    output.mkdir()  # Never reuse stale results from an earlier attempt.
    result = {'fixture_sha': sha, 'status': 'setup-failure'}
    try:
        result['fixture_count'] = install_snapshot(args.fixtures, sha, args.sdk, args.platform)
        command = native_command(args.platform, output)
        result['command'] = command
        if args.platform == 'android':
            # A compilation failure must not reuse the base run's JUnit report.
            reports = args.sdk / ANDROID_MODULE / 'build/test-results/testDebugUnitTest'
            if reports.exists():
                shutil.rmtree(reports)
        env = {**os.environ, 'SKIP_LINT': '1', 'USE_TEST_VISIBILITY': '0'}
        with (output / 'test.log').open('w') as log:
            result['exit_code'] = subprocess.run(command, cwd=args.sdk, env=env,
                                                  stdout=log, stderr=subprocess.STDOUT).returncode
        result['status'] = 'build-or-runner-failure'
        if args.platform == 'android':
            reports = args.sdk / ANDROID_MODULE / 'build/test-results/testDebugUnitTest'
            if reports.exists():
                shutil.copytree(reports, output / 'junit')
            report = android_results(output / 'junit')
        else:
            report = ios_results(output)
        result.update(report)
        result['status'] = test_status(result['exit_code'], report)
    except (OSError, ValueError, KeyError, ET.ParseError, subprocess.CalledProcessError) as error:
        result['error'] = str(error)
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'{label}: {result["status"]}', flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=DESTINATIONS, required=True)
    for name in ('fixtures', 'sdk', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--head', required=True)
    args = parser.parse_args()
    args.fixtures, args.sdk, args.output = (p.resolve() for p in (args.fixtures, args.sdk, args.output))
    args.output.mkdir(parents=True, exist_ok=True)
    sdk_sha = importer.git(args.sdk, 'rev-parse', 'HEAD').decode().strip()
    # Resolve immutable revisions up front. The SDK checkout never changes between runs.
    base_sha, head_sha = [importer.git(args.fixtures, 'rev-parse', '--verify', s + '^{commit}')
                          .decode().strip() for s in (args.base, args.head)]
    base = run_revision(args, 'base', base_sha)
    head = run_revision(args, 'head', head_sha)
    classification = compare(base['status'], head['status'])
    result = {'platform': args.platform, 'sdk_sha': sdk_sha,
              'classification': classification, 'base': base, 'head': head}
    (args.output / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    summary = (f'### {args.platform} unit compatibility: {classification}\n\n'
               f'SDK commit: `{sdk_sha}`\n\n'
               '| Fixtures | Revision | Result | Executed tests |\n'
               '| --- | --- | --- | ---: |\n'
               f'| Base | `{base_sha}` | {base["status"]} | {base.get("executed", "unknown")} |\n'
               f'| Proposed | `{head_sha}` | {head["status"]} | {head.get("executed", "unknown")} |\n\n'
               'Advisory unit-test evidence, not deployed-client validation. '
               'Both failing does not establish that the failures are identical. '
               'Inspect the per-revision native reports and logs.\n')
    for label, revision in [('Base', base), ('Proposed', head)]:
        if revision.get('failures'):
            # JSON escaping prevents test names from injecting Markdown/HTML.
            details = json.dumps(revision['failures'][:20], indent=2).replace('`', '\\u0060').replace('<', '\\u003c')
            summary += f'\n{label} failures (first 20):\n\n```json\n{details}\n```\n'
    print(summary)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as file:
            file.write(summary)
    if classification != 'compatible':
        print(f'::warning title=Mobile fixture preview::{args.platform}: {classification}; see artifacts.')
    # Completed comparisons are advisory. Setup/execution gaps must stay visibly failed.
    return 1 if classification == 'inconclusive-setup-or-execution' else 0


if __name__ == '__main__':
    raise SystemExit(main())

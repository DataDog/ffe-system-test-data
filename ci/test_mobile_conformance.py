# Unless explicitly stated otherwise, all files in this repository are licensed under the
# Apache License Version 2.0. This product includes software developed at Datadog
# (https://www.datadoghq.com/). Copyright 2025-Present Datadog, Inc.
"""Exercise comparison reporting and snapshot isolation without native toolchains."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import mobile_conformance as preview


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.sdk = self.root / 'sdk'
        self.sdk.mkdir()
        self.args = argparse.Namespace(platform='android', sdk=self.sdk, fixtures=self.root,
                                       output=self.root / 'output')
        self.args.output.mkdir()

    def test_comparison_classification(self):
        for base, head, expected in [
            ('pass', 'pass', 'compatible'),
            ('pass', 'test-failure', 'new-regression'),
            ('test-failure', 'pass', 'improvement'),
            ('test-failure', 'test-failure', 'inconclusive-both-fail'),
            ('pass', 'build-or-runner-failure', 'inconclusive-setup-or-execution'),
            ('setup-failure', 'pass', 'inconclusive-setup-or-execution'),
            ('pass', 'no-tests', 'inconclusive-setup-or-execution'),
        ]:
            with self.subTest(base=base, head=head):
                self.assertEqual(preview.compare(base, head), expected)

    def test_only_executed_canonical_tests_count(self):
        (self.root / 'TEST-example.xml').write_text(f'''<testsuite>
          <testcase classname="{preview.ANDROID_TEST}" name="passes"/>
          <testcase classname="{preview.ANDROID_TEST}" name="fails"><failure/></testcase>
          <testcase classname="{preview.ANDROID_TEST}" name="excluded"><skipped/></testcase>
          <testcase classname="OtherTest" name="unrelated"/>
        </testsuite>''')
        report = preview.android_results(self.root)
        self.assertEqual(report, {'executed': 2, 'failed': 1, 'failures': ['fails']})
        self.assertEqual(preview.test_status(1, report), 'test-failure')

    def test_success_exit_with_no_tests_is_not_compatible(self):
        self.assertEqual(preview.test_status(0, {'executed': 0, 'failed': 0}), 'no-tests')
        self.assertEqual(preview.test_status(1, {'executed': 1, 'failed': 0}), 'build-or-runner-failure')

    def test_swift_native_summary(self):
        summary = {'passedTests': 0, 'failedTests': 1, 'skippedTests': 2,
                   'testFailures': [{'message': 'fractional value accepted'}]}
        with patch.object(preview.subprocess, 'check_output', return_value=json.dumps(summary).encode()):
            self.assertEqual(preview.ios_results(self.root)['executed'], 1)
            self.assertEqual(json.loads((self.root / 'test-summary.json').read_text()), summary)

    def test_snapshot_copies_exact_bytes_and_removes_old_cases(self):
        # Use the actual committed fixture tree, without creating unsigned test commits.
        fixtures = Path(__file__).resolve().parent.parent
        destination = self.sdk / preview.DESTINATIONS['android']
        destination.mkdir(parents=True)
        (destination / 'SOURCE.json').write_text('{}')
        (destination / 'obsolete.json').write_text('{}')
        (self.sdk / 'keep.txt').write_text('unrelated SDK content')
        count = preview.install_snapshot(fixtures, 'HEAD', self.sdk, 'android')
        self.assertGreater(count, 0)
        self.assertFalse((destination / 'obsolete.json').exists())
        self.assertEqual((self.sdk / 'keep.txt').read_text(), 'unrelated SDK content')
        preview.importer.verify(destination)
        for name, value in preview.importer.snapshot(fixtures, 'HEAD').items():
            self.assertEqual((destination / name).read_bytes(), value)

    def test_refuses_unowned_or_symlink_destination(self):
        destination = self.sdk / preview.DESTINATIONS['android']
        destination.mkdir(parents=True)
        (destination / 'keep.txt').write_text('keep')
        with patch.object(preview.importer, 'snapshot', return_value={}):
            with self.assertRaises(ValueError):
                preview.install_snapshot(self.root, 'HEAD', self.sdk, 'android')
            destination.rename(destination.with_name('real'))
            destination.symlink_to(destination.with_name('real'), target_is_directory=True)
            with self.assertRaises(ValueError):
                preview.install_snapshot(self.root, 'HEAD', self.sdk, 'android')
        self.assertEqual((destination / 'keep.txt').read_text(), 'keep')

    def test_snapshot_installation_does_not_round_numbers(self):
        raw = b'{"value": 4503599627370497.5, "decimal": 1.20000000000000001}\n'
        content = {'index.json': b'["cases/numbers.json"]', 'cases/numbers.json': raw}
        with patch.object(preview.importer, 'snapshot', return_value=content):
            preview.install_snapshot(self.root, 'HEAD', self.sdk, 'ios')
        self.assertEqual((self.sdk / preview.DESTINATIONS['ios'] / 'cases/numbers.json').read_bytes(), raw)

    def test_build_failure_cannot_reuse_base_test_results(self):
        reports = self.sdk / preview.ANDROID_MODULE / 'build/test-results/testDebugUnitTest'
        reports.mkdir(parents=True)
        (reports / 'TEST-stale.xml').write_text(f'<testsuite><testcase classname="{preview.ANDROID_TEST}"/></testsuite>')
        with patch.object(preview, 'install_snapshot', return_value=57), \
             patch.object(preview.subprocess, 'run', return_value=argparse.Namespace(returncode=1)):
            result = preview.run_revision(self.args, 'head', 'a' * 40)
        self.assertNotEqual(result['status'], 'pass')
        self.assertEqual(result['executed'], 0)
        self.assertFalse(reports.exists())

    def test_setup_failure_is_recorded_without_starting_tests(self):
        with patch.object(preview, 'install_snapshot', side_effect=ValueError('missing corpus')), \
             patch.object(preview.subprocess, 'run') as run:
            result = preview.run_revision(self.args, 'base', 'b' * 40)
        run.assert_not_called()
        self.assertEqual(result['status'], 'setup-failure')
        self.assertEqual(json.loads((self.args.output / 'base/result.json').read_text()), result)

    def test_comparison_runs_head_after_base_failure_and_records_fixed_sdk(self):
        argv = ['preview', '--platform', 'android', '--fixtures', str(self.root),
                '--sdk', str(self.sdk), '--output', str(self.args.output),
                '--base', 'base', '--head', 'head']
        with patch('sys.argv', argv), \
             patch.object(preview.importer, 'git', side_effect=[b'a' * 40, b'b' * 40, b'c' * 40]), \
             patch.object(preview, 'run_revision', side_effect=[
                 {'status': 'test-failure'}, {'status': 'test-failure'}]) as run, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(preview.main(), 0)  # Completed mismatch remains advisory.
        self.assertEqual([call.args[1:] for call in run.call_args_list],
                         [('base', 'b' * 40), ('head', 'c' * 40)])
        result = json.loads((self.args.output / 'comparison.json').read_text())
        self.assertEqual(result['sdk_sha'], 'a' * 40)
        self.assertEqual(result['classification'], 'inconclusive-both-fail')


if __name__ == '__main__':
    unittest.main()

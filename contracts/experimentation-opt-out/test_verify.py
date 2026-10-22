"""Negative controls for acceptance evidence; no native SDK or network operations."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('verify', ROOT / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class AcceptanceControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'bundle'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.pin = verify.sha(self.root / 'manifest.json')

    def test_original_bundle_is_accepted(self):
        _, rows = verify.check_bundle(self.root, self.pin)
        self.assertEqual(len(rows), 313)

    def test_cross_repository_validation_links_the_tested_commit(self):
        decisions = json.loads((self.root / 'decisions.json').read_text())
        history = json.loads((self.root / 'validation-history.json').read_text())
        row = next(e for e in history['entries'] if e['id'] == 'V028')
        rendered = verify.decision_history.render(decisions, history)
        self.assertIn('https://github.com/DataDog/ffe-system-test-data/commit/' + row['source_sha'], rendered)
        self.assertNotIn('https://github.com/DataDog/dd-trace-go/commit/' + row['source_sha'], rendered)

    def test_value_only_operational_oracle_is_rejected(self):
        path = self.root / 'corpus/inactive-path.jsonl'
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        for row in rows:
            del row['expected']['exclusionChecks']
        path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        manifest_path = self.root / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['files']['corpus/inactive-path.jsonl'] = verify.sha(path)
        manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
        self.pin = verify.sha(manifest_path)
        with self.assertRaisesRegex(ValueError, 'must include exclusion-check counts'):
            verify.check_bundle(self.root, self.pin)

    def test_missing_operational_case_is_rejected_after_repin(self):
        path = self.root / 'corpus/inactive-path.jsonl'
        path.write_text('\n'.join(path.read_text().splitlines()[1:])+'\n')
        manifest_path = self.root / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['files']['corpus/inactive-path.jsonl'] = verify.sha(path)
        manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
        self.pin = verify.sha(manifest_path)
        with self.assertRaisesRegex(ValueError, 'Operational corpus inventory'):
            verify.check_bundle(self.root, self.pin)

    def test_missing_case_is_rejected(self):
        corpus = self.root / 'corpus/browser-proposal.jsonl'
        corpus.write_text('\n'.join(corpus.read_text().splitlines()[1:])+'\n')
        with self.assertRaisesRegex(ValueError, 'acceptance input'):
            verify.check_bundle(self.root, self.pin)

    def test_missing_semver_case_is_rejected_after_repin(self):
        corpus = self.root / 'corpus/semver-delivery.json'
        rows = json.loads(corpus.read_text())
        corpus.write_text(json.dumps(rows[1:])+'\n')
        path = self.root / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['files']['corpus/semver-delivery.json'] = verify.sha(corpus)
        path.write_text(json.dumps(manifest)+'\n')
        with self.assertRaisesRegex(ValueError, 'SemVer corpus inventory'):
            verify.check_bundle(self.root, verify.sha(path))

    def test_mutated_model_is_rejected(self):
        model = self.root / 'lean/Contract.lean'
        model.write_text(model.read_text().replace('seconds > 253402300799', 'seconds > 253402300798'))
        with self.assertRaisesRegex(ValueError, 'acceptance input'):
            verify.check_bundle(self.root, self.pin)

    def test_coherent_replacement_cannot_change_external_pin(self):
        corpus = self.root / 'corpus/browser-proposal.jsonl'
        rows = [json.loads(x) for x in corpus.read_text().splitlines()]
        rows[0]['expected'] = {'accepted': False}
        corpus.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        manifest = self.root / 'manifest.json'
        data = json.loads(manifest.read_text())
        data['files']['corpus/browser-proposal.jsonl'] = verify.sha(corpus)
        manifest.write_text(json.dumps(data, indent=2)+'\n')
        with self.assertRaisesRegex(ValueError, 'independently supplied pin'):
            verify.check_bundle(self.root, self.pin)

    def test_prior_revision_pin_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'independently supplied pin'):
            verify.check_bundle(self.root, '0' * 64)

    def edit_ledger_and_repin(self, mutate):
        path = self.root / 'decisions.json'
        ledger = json.loads(path.read_text())
        mutate(ledger)
        path.write_text(json.dumps(ledger, indent=2)+'\n')
        manifest_path = self.root / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['files']['decisions.json'] = verify.sha(path)
        manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
        self.pin = verify.sha(manifest_path)

    def test_setting_thread_from_another_pr_is_rejected(self):
        self.edit_ledger_and_repin(lambda ledger: ledger['decisions'][0]['latest_setting'].update(
            thread_url='https://github.com/DataDog/dd-trace-go/pull/5700#discussion_r4342540303'))
        with self.assertRaisesRegex(ValueError, 'thread must belong'):
            verify.check_bundle(self.root, self.pin)

    def test_unacknowledged_provenance_gap_is_rejected(self):
        self.edit_ledger_and_repin(lambda ledger: ledger['decisions'][0]['latest_setting'].update(
            thread_url=None, gap=None))
        with self.assertRaisesRegex(ValueError, 'explicit provenance gap'):
            verify.check_bundle(self.root, self.pin)

    def test_dropped_historical_check_is_rejected(self):
        self.edit_ledger_and_repin(lambda ledger: ledger['decisions'][0].update(validation_history_ids=[]))
        with self.assertRaisesRegex(ValueError, 'links are missing or inconsistent'):
            verify.check_bundle(self.root, self.pin)


if __name__ == '__main__':
    unittest.main()

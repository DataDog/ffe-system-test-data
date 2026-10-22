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

    def test_missing_case_is_rejected(self):
        corpus = self.root / 'corpus/browser-proposal.jsonl'
        corpus.write_text('\n'.join(corpus.read_text().splitlines()[1:])+'\n')
        with self.assertRaisesRegex(ValueError, 'acceptance input'):
            verify.check_bundle(self.root, self.pin)

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


if __name__ == '__main__':
    unittest.main()

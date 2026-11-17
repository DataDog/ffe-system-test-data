"""Regression tests for generated fixture snapshots and recursive discovery."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('sync', Path(__file__).with_name('sync-precomputed-fixtures.py'))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        subprocess.run(['git', 'init', '-q', self.source], check=True)
        for path in sync.FILES:
            target = self.source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('{}')
        case = self.source / 'precomputed-assignments/cases/new/nested/case.json'
        case.parent.mkdir(parents=True)
        case.write_text(json.dumps({'name': 'case', 'evaluations': [], 'response': {}}))
        subprocess.run(['git', '-C', self.source, 'add', '.'], check=True)
        # Test repository identity only; no task commits or hooks are changed.
        subprocess.run(['git', '-C', self.source, '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
                        '-c', 'user.name=Fixture test', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'fixture'], check=True)
        self.destination = self.root / 'snapshot'
        for path, value in sync.snapshot(self.source, 'HEAD').items():
            target = self.destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)

    def test_response_bytes_preserve_tokens_and_escaped_keys(self):
        raw = b'{"name":"x", "response": {"a\\\"b": [1.00000000000000001, 5.0, 1e-400]}, "evaluations": []}'
        self.assertEqual(b'{"a\\\"b": [1.00000000000000001, 5.0, 1e-400]}\n', sync.response_bytes(raw))

    def test_nested_discovery_and_verification(self):
        sync.verify(self.destination)
        self.assertEqual(json.loads((self.destination / 'index.json').read_text()), ['cases/new/nested/case.json'])

    def test_modified_json_fails(self):
        (self.destination / 'cases/new/nested/case.json').write_text('{}')
        with self.assertRaises(ValueError):
            sync.verify(self.destination)

    def test_missing_case_fails(self):
        (self.destination / 'cases/new/nested/case.json').unlink()
        with self.assertRaises(ValueError):
            sync.verify(self.destination)

    def test_unindexed_case_fails(self):
        (self.destination / 'cases/new.json').write_text('{}')
        with self.assertRaises(ValueError):
            sync.verify(self.destination)

    def test_symlink_rejected(self):
        (self.destination / 'link').symlink_to(self.source)
        with self.assertRaises(ValueError):
            sync.verify(self.destination)

    def test_invalid_revision_rejected(self):
        with self.assertRaises(ValueError):
            sync.snapshot(self.source, '--help')

    def test_unity_guids_are_stable(self):
        sync.unity_metadata(self.destination)
        meta = self.destination / 'cases/new/nested/case.json.meta'
        original = meta.read_text()
        sync.unity_metadata(self.destination)
        self.assertEqual(original, meta.read_text())
        sync.verify(self.destination)

    def test_cli_rejects_destructive_destinations_without_mutation(self):
        consumer = self.root / 'consumer'
        ci = consumer / 'ci'
        ci.mkdir(parents=True)
        importer = ci / 'sync-precomputed-fixtures.py'
        shutil.copyfile(sync.__file__, importer)
        (consumer / '.git').mkdir()
        (consumer / '.git/config').write_text('keep git data')
        (consumer / 'resources').mkdir()
        keep = consumer / 'resources/keep.txt'
        keep.write_text('keep unrelated data')
        (consumer / 'alias').symlink_to(consumer / 'resources', target_is_directory=True)
        for destination in ['', '.', '.git', '.git/fixtures', 'resources', 'alias/fixtures', '../outside']:
            with self.subTest(destination=destination):
                (ci / 'precomputed-fixtures.json').write_text(json.dumps({'destination': destination}))
                before = {p.relative_to(consumer): p.read_bytes() for p in consumer.rglob('*') if p.is_file()}
                result = subprocess.run([sys.executable, str(importer), '--source', str(self.source)],
                                        capture_output=True, text=True)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual(before, {p.relative_to(consumer): p.read_bytes()
                                         for p in consumer.rglob('*') if p.is_file()})

    def test_cli_refresh_preserves_guids_and_replaces_cases(self):
        consumer = self.root / 'consumer'
        ci = consumer / 'ci'
        ci.mkdir(parents=True)
        importer = ci / 'sync-precomputed-fixtures.py'
        shutil.copyfile(sync.__file__, importer)
        (ci / 'precomputed-fixtures.json').write_text(json.dumps({
            'destination': 'fixtures', 'unityMetadata': True,
        }))
        command = [sys.executable, str(importer), '--source', str(self.source), '--ref', 'HEAD']
        subprocess.run(command, check=True, capture_output=True)
        destination = consumer / 'fixtures'
        meta = destination / 'cases/new/nested/case.json.meta'
        custom_guid = '0123456789abcdef0123456789abcdef'
        meta.write_text(meta.read_text().replace(
            meta.read_text().split('guid: ')[1].splitlines()[0], custom_guid,
        ))
        removed = self.source / 'precomputed-assignments/cases/removed.json'
        removed.write_text(json.dumps({'name': 'removed', 'evaluations': [], 'response': {}}))
        subprocess.run(['git', '-C', self.source, 'add', '.'], check=True)
        commit = ['git', '-C', self.source, '-c', 'commit.gpgsign=false', '-c',
                  'core.hooksPath=/dev/null', '-c', 'user.name=Fixture test', '-c',
                  'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture update']
        subprocess.run(commit, check=True)
        subprocess.run(command, check=True, capture_output=True)
        self.assertTrue((destination / 'cases/removed.json.meta').exists())
        removed.unlink()
        changed = self.source / 'precomputed-assignments/cases/new/nested/case.json'
        changed.write_text(json.dumps({'name': 'case', 'evaluations': [], 'response': {}, 'description': 'Updated'}))
        added = changed.with_name('added.json')
        added.write_text(json.dumps({'name': 'added', 'evaluations': [], 'response': {}}))
        subprocess.run(['git', '-C', self.source, 'add', '.'], check=True)
        subprocess.run(commit, check=True)
        subprocess.run(command, check=True, capture_output=True)
        self.assertIn('guid: ' + custom_guid, meta.read_text())
        self.assertEqual(changed.read_bytes(), (destination / 'cases/new/nested/case.json').read_bytes())
        self.assertFalse((destination / 'cases/removed.json').exists())
        self.assertFalse((destination / 'cases/removed.json.meta').exists())
        self.assertTrue((destination / 'cases/new/nested/added.json.meta').exists())
        unrelated = destination / 'keep.txt'
        unrelated.write_text('not part of the snapshot')
        rejected = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn('outside the previous snapshot', rejected.stderr)
        self.assertEqual('not part of the snapshot', unrelated.read_text())
        unrelated.unlink()
        subprocess.run(command + ['--verify'], check=True, capture_output=True)
        subprocess.run(command + ['--check'], check=True, capture_output=True)


if __name__ == '__main__':
    unittest.main()

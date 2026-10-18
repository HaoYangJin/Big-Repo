import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from scripts import verify_plugin

ROOT = Path(__file__).parents[1]


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='plugin distribution ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo with spaces'
        self.root.mkdir()
        shutil.copytree(ROOT / 'plugins', self.root / 'plugins', ignore=shutil.ignore_patterns('__pycache__'))
        for directory in ('.agents', '.claude-plugin'):
            shutil.copytree(ROOT / directory, self.root / directory)
        for args in [('init', '-q'), ('add', '.'),
                     ('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                      'commit', '-qm', 'test: distribution fixture')]:
            subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)
        self.output = Path(self.temp.name) / 'output with spaces'

    def test_actual_distribution_and_checksum(self):
        report = verify_plugin.verify(self.root, self.output)
        self.assertEqual(report['status'], 'verified-distribution')
        self.assertEqual(len(report['skills']), 6)
        self.assertFalse(report['working_tree_dirty'])
        self.assertTrue(report['reproducible'])
        archive = self.output / 'build-one' / report['archive']
        self.assertTrue(archive.is_file())
        with self.assertRaises(ValueError):
            verify_plugin.inspect_archive(archive, '0' * 64)

    def test_marketplace_version_drift_blocks_distribution(self):
        file = self.root / '.claude-plugin/marketplace.json'
        data = json.loads(file.read_text(encoding='utf-8'))
        data['plugins'][0]['version'] = '99.0.0'
        file.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaises(ValueError):
            verify_plugin.verify(self.root, self.output)

    def test_missing_skill_reference_blocks_distribution(self):
        (self.root / 'plugins/repo-maintainer/skills/repo-intake/references/task-protocol.md').unlink()
        with self.assertRaises(ValueError):
            verify_plugin.verify(self.root, self.output)


if __name__ == '__main__':
    unittest.main()

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts/explore.py'
spec = importlib.util.spec_from_file_location('explore', SCRIPT)
explore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(explore)


class ExploreTests(unittest.TestCase):
    def test_real_snapshot_tracks_structure_without_file_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            def git(*args):
                return subprocess.run(['git', '-C', tmp, *args], check=True, capture_output=True)
            git('init', '-b', 'main')
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.invalid')
            (repo / 'README.md').write_text('private body must not be exported')
            (repo / 'tests').mkdir()
            (repo / 'tests/test_example.py').write_text('private code')
            git('add', '.')
            git('commit', '-m', 'test: initial')
            data = explore.collect(repo)
            self.assertEqual(data['files'], 2)
            self.assertEqual([s['present'] for s in data['signals']], [True, False, True, False])
            self.assertFalse(data['dirty'])
            (repo / 'untracked.txt').write_text('secret')
            self.assertTrue(explore.collect(repo)['dirty'])
            self.assertNotIn('private body', explore.render(data))
            with self.assertRaises(ValueError):
                explore.collect(repo / 'tests')

    def test_embedded_json_cannot_terminate_script(self):
        data = explore.demo()
        data['name'] = '</script><script>alert(1)</script>&'
        page = explore.render(data)
        embedded = page.split('<script id="repo-data" type="application/json">')[1].split('</script>')[0]
        self.assertEqual(json.loads(embedded), data)
        self.assertNotIn('<', embedded)
        self.assertNotIn('__REPO_DATA__', page)

    def test_payload_template_markers_remain_literal_data(self):
        data = explore.demo()
        data['name'] = '__CATALOG_DATA__'
        data['branch'] = '__REPO_DATA__'
        page = explore.render(data)
        embedded = page.split('<script id="repo-data" type="application/json">')[1].split('</script>')[0]
        self.assertEqual(json.loads(embedded), data)

    def test_demo_cli_is_offline_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'demo.html'
            command = [sys.executable, str(SCRIPT), '--demo', '--output', str(target)]
            result = subprocess.run(command, cwd=tmp, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            original = target.read_bytes()
            self.assertIn(b'connect-src \'none\'', original)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(target.read_bytes(), original)

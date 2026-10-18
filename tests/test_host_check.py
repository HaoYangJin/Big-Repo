from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

from scripts import check_host
from scripts.verify_plugin import SKILLS


class HostCheckTests(unittest.TestCase):
    def test_tool_cli_emits_utf8_under_legacy_stdio(self):
        with tempfile.TemporaryDirectory(prefix='legacy encoding ') as directory:
            fixture = Path(directory)
            (fixture / 'README.md').write_text('# 中文说明\n', encoding='utf-8')
            tool = Path(__file__).parents[1] / 'plugins/repo-maintainer/scripts/repo_tools.py'
            env = dict(os.environ, PYTHONIOENCODING='cp1252', PYTHONUTF8='0')
            result = subprocess.run([sys.executable, str(tool), 'preview', '--repo', str(fixture),
                                     '--repository', 'example/private'], env=env, capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('中文说明', result.stdout.decode('utf-8'))

    def test_codex_inventory_requires_enabled_installed_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = []
            for name in SKILLS:
                file = root / 'skills' / name / 'SKILL.md'
                file.parent.mkdir(parents=True)
                file.write_text('fixture')
                skills.append({'name': 'repo-maintainer:' + name, 'enabled': True,
                               'pluginId': 'repo-maintainer@repo-standards-ci', 'path': str(file)})
            self.assertEqual(check_host.inventory_from_codex(skills, root), SKILLS)
            skills[0]['enabled'] = False
            with self.assertRaises(ValueError):
                check_host.inventory_from_codex(skills, root)
            skills[0]['enabled'] = True
            skills[0]['path'] = str(root.parent / 'outside.md')
            with self.assertRaises(ValueError):
                check_host.inventory_from_codex(skills, root)

    def test_claude_inventory_requires_version_and_all_skills(self):
        text = 'repo-maintainer 1.1.0\n  Source: repo-maintainer@inline\n  Skills (6)  ' + ', '.join(SKILLS)
        self.assertEqual(check_host.inventory_from_claude(text, '1.1.0'), SKILLS)
        with self.assertRaises(ValueError):
            check_host.inventory_from_claude(text.replace('repo-audit, ', ''), '1.1.0')
        with self.assertRaises(ValueError):
            check_host.inventory_from_claude(text, '9.0.0')

    def test_actual_installed_tool_scenarios_without_cli_or_model(self):
        with tempfile.TemporaryDirectory(prefix='host tools ') as directory:
            plugin = Path(__file__).parents[1] / 'plugins/repo-maintainer'
            checks = check_host.exercise_tools(plugin, Path(directory) / 'fixture with spaces')
            self.assertIn('private-clickable-badge', checks)
            self.assertIn('preview-idempotent', checks)
            self.assertIn('public-star-history', checks)
            self.assertIn('workspace-preserved', checks)


if __name__ == '__main__':
    unittest.main()

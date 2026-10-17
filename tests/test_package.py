import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / 'plugins/repo-maintainer'


class PackageTests(unittest.TestCase):
    def test_manifests_and_marketplaces_resolve(self):
        codex = json.loads((PLUGIN / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        claude = json.loads((PLUGIN / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(codex['name'], claude['name'])
        self.assertEqual(codex['version'], claude['version'])
        self.assertTrue((PLUGIN / codex['skills']).is_dir())
        market = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        self.assertEqual((ROOT / market['plugins'][0]['source']['path']).resolve(), PLUGIN.resolve())
        market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
        self.assertEqual((ROOT / market['plugins'][0]['source']).resolve(), PLUGIN.resolve())

    def test_six_skills_and_self_contained_references(self):
        skills = list((PLUGIN / 'skills').glob('*/SKILL.md'))
        self.assertEqual(len(skills), 6)
        protocols = []
        for skill in skills:
            text = skill.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'))
            self.assertIn('name: ' + skill.parent.name + '\n', text)
            self.assertRegex(text, r'description: .+')
            self.assertNotIn('[TODO:', text)
            protocols.append((skill.parent / 'references/task-protocol.md').read_bytes())
        self.assertTrue(all(p == protocols[0] for p in protocols))

    def test_markdown_local_links(self):
        missing = []
        for file in ROOT.rglob('*.md'):
            if any(part in ('work', '.git', '.venv') for part in file.relative_to(ROOT).parts):
                continue
            text = re.sub(r'```[^\n]*\n.*?```', '', file.read_text(encoding='utf-8'), flags=re.S)
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                if urlparse(target).scheme or target.startswith('#'):
                    continue
                path = unquote(target.split('#')[0].strip('<>'))
                if not (file.parent / path).exists():
                    missing.append(str(file.relative_to(ROOT)) + ': ' + target)
        self.assertEqual(missing, [])


if __name__ == '__main__':
    unittest.main()

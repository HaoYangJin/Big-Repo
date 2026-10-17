import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).parents[1] / 'plugins/repo-maintainer/scripts/collect_research.py'


class ResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('collect_research', MODULE)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_signals_have_line_evidence(self):
        signals = self.module.inspect_text('README.md', '# Demo\n![CI](https://img.shields.io/test)\nhttps://star-history.com/x\n')
        self.assertEqual(signals['badges'], [2])
        self.assertEqual(signals['star_history'], [3])
        self.assertEqual(signals['release_automation'], [])

    def test_no_false_claim_of_absence(self):
        self.assertEqual(self.module.inspect_text('README.md', '# Demo')['star_history'], [])

    def test_repository_input_restricted(self):
        for value in ['../evil', 'a/b/c', 'https://github.com/a/b', 'a/b?x=1']:
            with self.assertRaises(ValueError):
                self.module.validate_repo(value)

    def test_sample_roster(self):
        import json
        roster = json.loads((MODULE.parents[3] / 'research/roster.json').read_text(encoding='utf-8'))
        self.assertEqual(len(roster), 60)
        self.assertEqual(len({x['repository'] for x in roster}), 60)


if __name__ == '__main__':
    unittest.main()

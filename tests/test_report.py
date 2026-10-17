import importlib.util
from pathlib import Path
import tempfile
import json
import unittest

FILE = Path(__file__).parents[1] / 'scripts/build_research.py'


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('report', FILE)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_observations_keep_provenance(self):
        data = {'documents': [{'status': 'inspected', 'path': 'README.md',
                               'url': 'https://github.com/a/b/blob/sha/README.md',
                               'signals': {'badges': [2]}}]}
        found = self.m.evidence(data, 'badges')
        self.assertEqual(found[0]['url'], 'https://github.com/a/b/blob/sha/README.md#L2')
        self.assertEqual(self.m.evidence(data, 'unknown'), [])

    def test_report_handles_missing_and_no_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            record = {'repository': 'a/b', 'requested_repository': 'a/b', 'category': 'sdk',
                      'status': 'collected', 'metadata': {}, 'documents': [], 'errors': [],
                      'commits': [], 'pull_requests': [], 'releases': [], 'workflow_paths': []}
            (root / 'data/a__b.json').write_text(json.dumps(record))
            self.m.build(root / 'data', root / 'out')
            text = (root / 'out/profiles/a__b.md').read_text(encoding='utf-8')
            self.assertIn('GitHub Release', text)
            self.assertIn('未知', text)
            self.assertIn('仓库展示与玩法', text)
            self.assertTrue((root / 'out/source-index.json').exists())


if __name__ == '__main__':
    unittest.main()

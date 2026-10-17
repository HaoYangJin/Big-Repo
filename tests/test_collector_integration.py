from test_research import MODULE
import base64
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.request import Request


class FakeAPI:
    def __init__(self, error=False):
        self.fetched_at = {}
        self.error = error

    def get(self, endpoint):
        self.fetched_at[endpoint] = '2026-10-18T00:00:00+00:00'
        sha = 'a' * 40
        if endpoint == '/repos/a/b':
            return {'full_name': 'a/b', 'private': False, 'default_branch': 'main',
                    'owner': {'login': 'a', 'type': 'Organization'}}
        if '/commits?sha=' in endpoint:
            return [{'sha': sha, 'html_url': 'https://github.com/a/b/commit/' + sha,
                     'commit': {'committer': {'date': '2026-10-18'}, 'message': 'docs: update\nbody'}}]
        if '/git/trees/' in endpoint:
            if endpoint.endswith(sha):
                return {'tree': [{'path': 'README.md', 'type': 'blob', 'sha': 'blob', 'size': 10},
                                 {'path': '.github', 'type': 'tree', 'sha': 'github'}]}
            if endpoint.endswith('github'):
                return {'tree': [{'path': 'workflows', 'type': 'tree', 'sha': 'wf'}]}
            return {'tree': [{'path': 'ci.yml', 'type': 'blob', 'sha': 'blob', 'size': 10}]}
        if '/git/blobs/' in endpoint:
            return {'content': base64.b64encode(b'# Demo\npytest\n').decode()}
        if '/pulls?' in endpoint:
            return [{'number': 1, 'title': 'docs: update', 'html_url': 'https://github.com/a/b/pull/1',
                     'merged_at': '2026-10-18', 'base': {'ref': 'main'}, 'head': {'sha': sha},
                     'merge_commit_sha': sha}]
        if endpoint.endswith('/reviews?per_page=100'):
            return [{'state': 'APPROVED'}]
        if '/files?' in endpoint:
            return [{'filename': 'README.md'}]
        if '/releases?' in endpoint:
            return [{'draft': False, 'prerelease': False, 'tag_name': 'v1',
                     'html_url': 'https://github.com/a/b/releases/tag/v1',
                     'published_at': '2026-10-18', 'target_commitish': 'main'}]
        if '/commits/v1' in endpoint:
            return {'sha': sha}
        if '/actions/runs?' in endpoint:
            if self.error:
                raise RuntimeError('GitHub HTTP 403')
            return {'workflow_runs': [{'id': 1, 'conclusion': 'success', 'head_sha': sha}]}
        if '/tags?' in endpoint:
            return [{'name': 'v1', 'commit': {'sha': sha}}]
        raise AssertionError(endpoint)


class CollectorIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('collector', MODULE)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_collect_evidence_and_times(self):
        data = self.m.collect(FakeAPI(), {'repository': 'a/b', 'category': 'sdk'})
        self.assertEqual(data['status'], 'collected')
        self.assertEqual(len(data['documents']), 2)
        self.assertEqual(data['documents'][0]['signals']['tests'], [2])
        self.assertEqual(data['pull_requests'][0]['review_states'], ['APPROVED'])
        self.assertEqual(data['releases'][0]['tag'], 'v1')
        self.assertEqual(data['collected_at'], '2026-10-18T00:00:00+00:00')
        self.assertIn('assembled_at', data)

    def test_permission_gap_is_preserved(self):
        data = self.m.collect(FakeAPI(error=True), {'repository': 'a/b', 'category': 'sdk'})
        self.assertEqual(data['status'], 'collected-with-gaps')
        self.assertTrue(data['errors'])

    def test_private_repository_stops_collection(self):
        api = FakeAPI()
        api.get = lambda endpoint: {'private': True}
        self.assertEqual(self.m.collect(api, {'repository': 'a/b', 'category': 'sdk'})['status'], 'private-skipped')

    def test_missing_repo_record(self):
        api = FakeAPI()
        def missing(endpoint):
            raise RuntimeError('GitHub HTTP 404')
        api.get = missing
        self.assertEqual(self.m.collect(api, {'repository': 'a/b', 'category': 'sdk'})['status'], 'inaccessible')

    def test_redirect_never_forwards_cross_origin_token(self):
        redirect = self.m.SafeRedirect()
        for url in ['http://api.github.com/a', 'https://evil.example/a', 'https://api.github.com:8443/a']:
            with self.assertRaises(ValueError):
                redirect.redirect_request(Request('https://api.github.com/a'), None, 302, 'Found', {}, url)

    def test_cached_token_not_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(self.m.subprocess, 'run', return_value=SimpleNamespace(stdout='SECRET\n')):
                api = self.m.GitHub(directory)
            endpoint = '/repos/a/b'
            import hashlib
            p = Path(directory) / (hashlib.sha256(endpoint.encode()).hexdigest() + '.json')
            p.write_text('{"ok": true}', encoding='utf-8')
            self.assertEqual(api.get(endpoint), {'ok': True})
            self.assertIn(endpoint, api.fetched_at)
            self.assertNotIn('SECRET', p.read_text())
            with self.assertRaises(ValueError):
                api.get('/user')

    def test_main_writes_atomic_record_and_resumes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            roster = base / 'roster.json'
            roster.write_text(json.dumps([{'repository': 'a/b', 'category': 'sdk'}]))
            argv = ['collect', '--roster', str(roster), '--output', str(base / 'data'), '--cache', str(base / 'cache')]
            with patch.object(self.m, 'GitHub', return_value=FakeAPI()), patch.object(self.m, '__name__', 'collect'), patch('sys.argv', argv):
                self.m.main()
                record = base / 'data/a__b.json'
                first = record.read_bytes()
                self.m.main()
                self.assertEqual(record.read_bytes(), first)


if __name__ == '__main__':
    unittest.main()

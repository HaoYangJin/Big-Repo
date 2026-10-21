import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


class PublishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = Path(__file__).parents[1] / 'scripts/publish_plugin.py'
        spec = importlib.util.spec_from_file_location('publish_plugin', script)
        cls.publisher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.publisher)

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.commit = 'a' * 40
        self.files = {}
        for name, content in [('Big-Repo-2.0.0.zip', b'validated zip'),
                              ('Big-Repo-2.0.0.zip.sha256', b'checksum'),
                              ('INSTALL-2.0.0.md', b'install')]:
            file = self.root / name
            file.write_bytes(content)
            self.files[name] = file
        self.manifest = self.root / 'manifest.json'
        self.data = {'repository': 'a/b', 'tag': 'v2.0.0', 'commit': self.commit,
                     'sha256': self.publisher.digest(self.files['Big-Repo-2.0.0.zip']),
                     'files': [{'path': name, 'sha256': self.publisher.digest(file)}
                               for name, file in self.files.items()]}
        self.save()
        self.remote = {}
        self.draft = True
        self.moves_tag = False
        self.writes = []
        self.releases = [{'id': 123, 'tag_name': 'v2.0.0'}]

    def save(self):
        self.manifest.write_text(json.dumps(self.data))

    def api(self, endpoint):
        if '/git/ref/' in endpoint:
            return {'object': {'type': 'tag', 'sha': 'b' * 40}}
        if '/git/tags/' in endpoint:
            return {'object': {'type': 'commit', 'sha': 'f' * 40 if self.moves_tag else self.commit}}
        if '/releases?' in endpoint:
            return self.releases
        self.assertEqual(endpoint, 'repos/a/b/releases/123')
        return {'id': 123, 'tag_name': 'v2.0.0', 'draft': self.draft,
                'html_url': 'https://github.com/a/b/releases/tag/v1.3.0',
                'assets': [{'name': name, 'state': 'uploaded'} for name in self.remote]}

    def command(self, args, cwd=None):
        operation = args[2]
        if operation == 'upload':
            file = Path(args[4])
            self.writes.append(('upload', file.name))
            self.remote[file.name] = file.read_bytes()
        elif operation == 'download':
            name = args[args.index('--pattern') + 1]
            destination = Path(args[args.index('--dir') + 1]) / name
            destination.write_bytes(self.remote[name])
        elif operation == 'edit':
            self.writes.append(('publish',))
            self.draft = False
        else:
            self.fail('Unexpected command')
        return '', ''

    def publish(self, runner=None):
        with patch.object(self.publisher, 'api', side_effect=self.api), patch.object(
                self.publisher, 'run', side_effect=runner or self.command):
            return self.publisher.publish(self.manifest)

    def test_complete_publication_and_already_published_rerun(self):
        self.assertEqual(self.publish()['status'], 'published')
        self.assertEqual(len(self.writes), 4)
        self.assertEqual(self.writes[-1], ('publish',))
        self.writes.clear()
        self.assertEqual(self.publish()['status'], 'published')
        self.assertEqual(self.writes, [])

    def test_partial_upload_resumes_only_matching_missing_assets(self):
        name = next(iter(self.files))
        self.remote[name] = self.files[name].read_bytes()
        self.publish()
        self.assertNotIn(('upload', name), self.writes)
        self.assertEqual(len(self.writes), 3)

    def test_missing_or_ambiguous_release_prevents_any_write(self):
        for releases in ([], self.releases * 2):
            self.releases = releases
            with self.assertRaises(ValueError):
                self.publish()
            self.assertEqual(self.writes, [])

    def test_release_lookup_paginates_before_selecting_stable_id(self):
        pages = [[{'id': i + 1, 'tag_name': 'v0.0.1'} for i in range(100)], self.releases]
        with patch.object(self.publisher, 'api', side_effect=pages) as request:
            self.assertEqual(self.publisher.release_id('a/b', 'v2.0.0'), 123)
        self.assertEqual(request.call_args_list[1].args[0], 'repos/a/b/releases?per_page=100&page=2')

    def test_existing_mismatch_and_extra_asset_prevent_any_write(self):
        for name in (next(iter(self.files)), 'unexpected.txt'):
            self.remote = {name: b'wrong bytes'}
            with self.assertRaises(ValueError):
                self.publish()
            self.assertEqual(self.writes, [])

    def test_changed_tag_prevents_upload(self):
        self.moves_tag = True
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.writes, [])

    def test_tag_moving_during_upload_prevents_publication(self):
        def runner(args, cwd=None):
            result = self.command(args, cwd)
            if args[2] == 'upload':
                self.moves_tag = True
            return result

        with self.assertRaises(ValueError):
            self.publish(runner)
        self.assertTrue(self.draft)
        self.assertNotIn(('publish',), self.writes)

    def test_failed_or_corrupted_upload_never_publishes(self):
        calls = []

        def failed(args, cwd=None):
            if args[2] == 'upload':
                calls.append(args)
                raise subprocess.TimeoutExpired('gh', 300)
            return self.command(args, cwd)

        with self.assertRaises(subprocess.TimeoutExpired):
            self.publish(failed)
        self.assertEqual(len(calls), 1)
        self.assertTrue(self.draft)

        def corrupt(args, cwd=None):
            result = self.command(args, cwd)
            if args[2] == 'upload':
                self.remote[Path(args[4]).name] = b'corrupt'
            return result

        with self.assertRaises(ValueError):
            self.publish(corrupt)
        self.assertTrue(self.draft)

    def test_tampered_or_escaping_local_asset_prevents_any_write(self):
        self.files['INSTALL-2.0.0.md'].write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.writes, [])
        self.data['files'][0]['path'] = '../outside'
        self.save()
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.writes, [])

    def test_invalid_inputs_fail_before_commands(self):
        for tag, commit, sha in [('v1.3.0;echo bad', self.commit, 'a' * 64),
                                 ('v2.0.0', 'main', 'a' * 64),
                                 ('v2.0.0', self.commit, 'bad')]:
            with patch.object(self.publisher, 'run') as command, self.assertRaises(ValueError):
                self.publisher.prepare(self.root, self.root.parent / 'out', 'a/b', tag, commit, sha)
            command.assert_not_called()

    def test_brand_names_preserve_historical_releases(self):
        self.assertEqual(self.publisher.package_name('1.2.0'), 'repo-maintainer')
        self.assertEqual(self.publisher.package_name('1.3.0'), 'Repo-Standards')

    def test_zero_test_run_cannot_prepare_publication(self):
        for platform in ('.codex-plugin', '.claude-plugin'):
            folder = self.root / 'source/.' / platform
            folder.mkdir(parents=True)
            (folder / 'plugin.json').write_text(json.dumps({'name': 'big-repo', 'version': '2.0.0'}))

        def command(args, cwd=None):
            if args[0] == 'git':
                return (self.commit + '\n' if args[1] == 'rev-parse' else ''), ''
            return '', 'Ran 0 tests in 0.001s\nOK\n'

        with patch.object(self.publisher, 'run', side_effect=command), self.assertRaises(ValueError):
            self.publisher.prepare(self.root / 'source', self.root / 'out', 'a/b',
                                   'v2.0.0', self.commit, 'a' * 64)
        self.assertFalse((self.root / 'out/manifest.json').exists())

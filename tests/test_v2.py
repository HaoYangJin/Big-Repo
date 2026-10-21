import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from contextlib import contextmanager

ROOT = Path(__file__).parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location('v2_' + name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = load('project_workflow')
        cls.tools = cls.workflow.TOOLS

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'project'
        self.repo.mkdir()
        self.repo = self.repo.resolve()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.repo / 'README.md').write_text('# Existing\nKeep my introduction.\n', encoding='utf-8')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True, capture_output=True).stdout

    def policy(self):
        return {'schema_version': 1, 'trigger': 'task-or-feedback', 'plugin_path': '.repo-maintainer/plugin',
                'repository': None, 'base_branch': 'main', 'delivery': 'commit', 'release': 'explicit-request',
                'clients': ['codex', 'claude'], 'validation': [{'id': 'check', 'argv': ['git', 'diff', '--check']}],
                'ci_policy': 'none', 'required_checks': []}

    def test_catalog_matches_actual_skills_and_templates(self):
        catalog = json.loads((ROOT / 'assets/catalog.json').read_text(encoding='utf-8'))
        for kind, expected in [('skill', 8), ('template', 6)]:
            entries = [i for i in catalog['items'] if i['kind'] == kind]
            self.assertEqual(len(entries), expected)
            self.assertEqual(len({i['id'] for i in entries}), expected)
            for item in entries:
                self.assertTrue((ROOT / item['path']).is_file())

    def test_showcase_is_idempotent_and_private_by_default(self):
        self.tools.sync_showcase(self.repo, 'example/project')
        text = (self.repo / 'README.md').read_text(encoding='utf-8')
        self.assertIn('Keep my introduction.', text)
        self.assertNotIn('api.star-history.com', text)
        self.assertEqual(self.tools.sync_showcase(self.repo, 'example/project')['changed'], [])
        self.tools.sync_showcase(self.repo, 'example/project', public=True)
        self.assertIn('api.star-history.com', (self.repo / 'README.md').read_text(encoding='utf-8'))
        self.assertIn('connect-src', (self.repo / 'docs/big-repo-explorer.html').read_text(encoding='utf-8'))

    def test_existing_unowned_explorer_is_preserved(self):
        (self.repo / 'docs').mkdir()
        target = self.repo / 'docs/big-repo-explorer.html'
        target.write_text('User content', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.tools.sync_showcase(self.repo)
        self.assertEqual(target.read_text(encoding='utf-8'), 'User content')
        self.assertNotIn('showcase:start', (self.repo / 'README.md').read_text(encoding='utf-8'))

    def test_create_local_prepares_before_first_commit_and_preserves_content(self):
        result = self.workflow.create(self.repo, delivery='commit')
        self.assertEqual(result['status'], 'needs-configuration')
        self.assertIsNone(result['config']['repository'])
        self.assertTrue((self.repo / '.big-repo/plugin/scripts/runtime_resources.py').exists())
        self.assertIn('Keep my introduction.', (self.repo / 'README.md').read_text(encoding='utf-8'))
        self.assertIn('尚无提交', load('explore').collect(self.repo)['head'])

    def test_migration_retains_active_identity_and_invalidates_old_evidence(self):
        policy = self.policy()
        legacy = self.repo / '.repo-maintainer'
        legacy.mkdir()
        self.workflow.write_json(legacy / 'config.json', policy)
        (self.repo / 'AGENTS.md').write_text('# User rules\nRetain this.\n', encoding='utf-8')
        state_root = self.repo / '.git/repo-maintainer'
        identifier = 'a' * 64
        task_path = state_root / 'tasks' / identifier
        self.workflow.write_json(state_root / 'active.json', {'id': identifier})
        state = {'id': identifier, 'objective': 'Keep task', 'status': 'reviewed', 'attempts': 2,
                 'config_digest': self.workflow.config_digest(policy), 'delivery': 'commit', 'pr_number': 42}
        self.workflow.write_json(task_path / 'state.json', state)
        self.workflow.write_json(task_path / 'task.json', {'allowed_paths': ['.repo-maintainer/**']})
        self.workflow.write_json(task_path / 'evidence.json', {'review': {'status': 'approved'}})
        self.workflow.migrate(self.repo)
        new_path = self.repo / '.git/big-repo/tasks' / identifier
        migrated = json.loads((new_path / 'state.json').read_text())
        self.assertEqual(migrated['id'], identifier)
        self.assertEqual(migrated['pr_number'], 42)
        self.assertEqual(migrated['status'], 'working')
        self.assertFalse((new_path / 'evidence.json').exists())
        self.assertTrue((new_path / 'migration-old-evidence.json').exists())
        self.assertTrue((self.repo / '.git/big-repo/legacy-project-backup/config.json').exists())
        self.assertIn('Retain this.', (self.repo / 'AGENTS.md').read_text(encoding='utf-8'))
        self.assertFalse(self.workflow.migrate(self.repo)['migrated'])

    def test_migration_conflict_refuses_to_overwrite(self):
        self.workflow.write_json(self.repo / '.repo-maintainer/config.json', self.policy())
        self.workflow.write_json(self.repo / '.big-repo/config.json', self.policy())
        with self.assertRaises(self.workflow.WorkflowError):
            self.workflow.migrate(self.repo)

    def test_init_and_create_require_explicit_legacy_migration(self):
        self.workflow.write_json(self.repo / '.repo-maintainer/config.json', self.policy())
        with self.assertRaises(self.workflow.WorkflowError):
            self.workflow.initialize(self.repo)
        with self.assertRaises(self.workflow.WorkflowError):
            self.workflow.create(self.repo)
        self.assertFalse((self.repo / '.big-repo').exists())

    def test_non_github_origin_is_rejected_before_remote_creation(self):
        self.git('remote', 'add', 'origin', 'https://gitlab.com/example/project.git')
        with patch.object(self.workflow, 'command', wraps=self.workflow.command) as calls:
            with self.assertRaises(self.workflow.WorkflowError):
                self.workflow.create(self.repo, 'example/project')
        self.assertFalse(any(call.args[0][0] == 'gh' for call in calls.call_args_list))

    def test_migration_config_and_instruction_failures_roll_back(self):
        for failure in ('config', 'instruction'):
            with self.subTest(failure=failure):
                self.workflow.write_json(self.repo / '.repo-maintainer/config.json', self.policy())
                agents = self.repo / 'AGENTS.md'
                agents.write_text('# Preserve user rules\n', encoding='utf-8')
                original_json = self.workflow.write_json
                original_atomic = self.workflow.atomic_text

                def write_json(path, data):
                    if failure == 'config' and path == self.repo / '.big-repo/config.json':
                        raise OSError('injected config write failure')
                    return original_json(path, data)

                def write_text(path, data):
                    if failure == 'instruction' and path == agents:
                        raise OSError('injected instruction write failure')
                    return original_atomic(path, data)

                with patch.object(self.workflow, 'write_json', side_effect=write_json), patch.object(self.workflow, 'atomic_text', side_effect=write_text):
                    with self.assertRaises(OSError):
                        self.workflow.migrate(self.repo)
                self.assertTrue((self.repo / '.repo-maintainer/config.json').exists())
                self.assertFalse((self.repo / '.big-repo/config.json').exists())
                self.assertFalse((self.repo / '.git/big-repo').exists())
                self.assertEqual(agents.read_text(encoding='utf-8'), '# Preserve user rules\n')

    def test_interrupted_migration_journal_recovers_on_retry(self):
        self.workflow.write_json(self.repo / '.repo-maintainer/config.json', self.policy())
        original = self.workflow.write_json
        def write(path, data):
            if path == self.repo / '.big-repo/config.json':
                raise OSError('simulated interruption')
            return original(path, data)
        with patch.object(self.workflow, 'write_json', side_effect=write), patch.object(self.workflow, '_rollback_migration', side_effect=OSError('process interrupted')):
            with self.assertRaises(OSError):
                self.workflow.migrate(self.repo)
        self.assertTrue((self.repo / '.git/big-repo/migration.json').exists())
        self.assertTrue(self.workflow.migrate(self.repo)['migrated'])

    def test_partial_instruction_temporary_write_preserves_user_rules(self):
        self.workflow.write_json(self.repo / '.repo-maintainer/config.json', self.policy())
        agents = self.repo / 'AGENTS.md'
        agents.write_text('# Original user rules\n', encoding='utf-8')
        original = self.workflow.tempfile.NamedTemporaryFile

        @contextmanager
        def partial_file(*args, **kwargs):
            with original(*args, **kwargs) as stream:
                if kwargs.get('prefix') == '.AGENTS.md.big-repo-':
                    class Partial:
                        name = stream.name
                        def write(self, data):
                            stream.write(data[:10])
                            raise OSError('partial temporary write')
                    yield Partial()
                else:
                    yield stream
        with patch.object(self.workflow.tempfile, 'NamedTemporaryFile', partial_file):
            with self.assertRaises(OSError):
                self.workflow.migrate(self.repo)
        self.assertEqual(agents.read_text(encoding='utf-8'), '# Original user rules\n')
        self.assertFalse(list(self.repo.glob('.AGENTS.md.big-repo-*')))
        self.assertTrue(self.workflow.migrate(self.repo)['migrated'])

    def test_create_remote_uncertain_outcome_is_queried_not_recreated(self):
        responses = [subprocess.CompletedProcess([], 1, '{"message":"Not Found"}', '')]
        remote = {'id': 1, 'full_name': 'example/project', 'private': True}
        original = self.workflow.command
        writes = []

        def command(argv, repo=None):
            if argv[:3] == ['gh', 'repo', 'create']:
                writes.append(argv)
                raise subprocess.TimeoutExpired(argv, 90)
            if argv[:2] == ['gh', 'api']:
                return json.dumps(remote)
            return original(argv, repo)

        original_run = subprocess.run
        def run(argv, **kwargs):
            if argv[:2] == ['gh', 'api']:
                return responses.pop(0)
            return original_run(argv, **kwargs)
        with patch.object(self.workflow, 'command', side_effect=command), patch.object(self.workflow.subprocess, 'run', side_effect=run):
            result = self.workflow.create(self.repo, 'example/project', delivery='commit')
        self.assertEqual(len(writes), 1)
        self.assertIn('--private', writes[0])
        self.assertTrue(result['created'])
        self.assertEqual(self.workflow.identity(self.repo), 'example/project')


if __name__ == '__main__':
    unittest.main()

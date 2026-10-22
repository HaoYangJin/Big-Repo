"""Safety defaults and explicit lifecycle operations against isolated repositories."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('policy_workflow', ROOT / 'scripts/project_workflow.py')
        cls.w = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.w)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name).resolve()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        # Keep Git housekeeping out of filesystem snapshots of this isolated repo.
        self.git('config', 'maintenance.auto', 'false')
        self.git('config', 'gc.auto', '0')
        (self.repo / 'README.md').write_text('# User project\nKeep it.\n', encoding='utf-8')
        self.git('add', 'README.md')
        self.git('commit', '-m', 'test: baseline')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def init(self, **kwargs):
        return self.w.initialize(self.repo, checks=['git diff --check'], **kwargs)

    def files(self):
        return {p.relative_to(self.repo).as_posix(): p.read_bytes()
                for p in self.repo.rglob('*') if p.is_file()}

    def test_default_init_is_local_without_persistent_instructions_or_showcase(self):
        readme = (self.repo / 'README.md').read_bytes()
        with patch.object(self.w.TOOLS, 'sync_showcase') as showcase:
            result = self.init()
        self.assertEqual(result['status'], 'configured')
        config = result['config']
        self.assertEqual(config['schema_version'], 2)
        self.assertEqual(config['delivery'], 'commit')
        self.assertEqual(config['clients'], [])
        self.assertEqual(config['profile'], 'core')
        self.assertTrue(config['policy_confirmed'])
        self.assertFalse((self.repo / 'AGENTS.md').exists())
        self.assertFalse((self.repo / 'CLAUDE.md').exists())
        self.assertEqual((self.repo / 'README.md').read_bytes(), readme)
        showcase.assert_not_called()

    def test_init_and_create_dry_run_have_no_filesystem_or_remote_writes(self):
        before = self.files()
        with patch.object(self.w.TOOLS, 'sync_showcase') as showcase:
            result = self.init(dry_run=True, client='both', delivery='merge')
        self.assertEqual(result['status'], 'preview')
        self.assertIn('AGENTS.md', result['changes'])
        self.assertEqual(self.files(), before)
        showcase.assert_not_called()
        target = self.repo / 'uncreated'
        with patch.object(self.w, 'command', side_effect=AssertionError('No remote or Git init')):
            result = self.w.create(target, 'example/project', dry_run=True)
        self.assertEqual(result['status'], 'preview')
        self.assertFalse(target.exists())

    def test_showcase_preflight_failure_leaves_initialization_untouched(self):
        readme = self.repo / 'README.md'
        readme.write_text(
            '# User project\n\n<!-- big-repo:showcase:start -->\n'
            '<!-- big-repo:showcase:start -->\n'
            '<!-- big-repo:showcase:end -->\n',
            encoding='utf-8',
        )
        before = self.files()
        with self.assertRaises(ValueError):
            self.init(profile='full', showcase='local')
        self.assertEqual(self.files(), before)

    def test_create_rejects_impossible_public_showcase_before_writes(self):
        target = self.repo / 'new-project'
        before = self.files()
        for repository, visibility in ((None, 'public'), ('example/project', 'private')):
            with self.subTest(repository=repository, visibility=visibility):
                with self.assertRaises(self.w.WorkflowError):
                    self.w.create(
                        target,
                        repository,
                        visibility,
                        profile='full',
                        showcase='public',
                        dry_run=True,
                    )
                self.assertFalse(target.exists())
                self.assertEqual(self.files(), before)

    def test_instructions_reflect_selected_policy_and_client(self):
        self.init(client='codex')
        text = (self.repo / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('仅本地提交', text)
        self.assertNotIn('无需再说', text)
        self.assertNotIn('自动合并', text)
        self.assertFalse((self.repo / 'CLAUDE.md').exists())
        self.assertIn('规划', text)

    def test_update_preserves_showcase_unless_explicitly_changed(self):
        self.init(profile='full', showcase='local')
        result = self.init(update=True, client='codex')
        self.assertEqual(result['config']['showcase'], 'local')
        result = self.init(update=True, showcase='none')
        self.assertEqual(result['config']['showcase'], 'none')

    def test_workflow_showcase_uses_runtime_version_in_generated_explorer(self):
        result = self.init(profile='full', showcase='local')
        text = (self.repo / 'docs/big-repo-explorer.html').read_text(encoding='utf-8')
        self.assertIn(f'<span class="tag">{result["config"]["runtime_version"]}</span>', text)
        self.assertNotIn('<span class="tag">2.0.0</span>', text)

    def test_update_preserves_policy_provenance_when_delivery_is_unchanged(self):
        self.init(delivery='merge', ci=['tests'])
        original = self.w.configuration(self.repo)['policy_record']
        result = self.init(update=True, client='codex')
        self.assertEqual(result['config']['delivery'], 'merge')
        self.assertEqual(result['config']['policy_record'], original)

    def test_status_without_task_is_read_only_and_shows_policy(self):
        self.init()
        before = self.files()
        result = self.w.status(self.repo)
        self.assertEqual(self.files(), before)
        self.assertEqual(result['policy']['delivery'], 'commit')
        self.assertEqual(result['policy']['clients'], [])
        self.assertFalse((self.repo / '.git/big-repo').exists())

    def test_legacy_policy_requires_confirmation_before_begin(self):
        self.init()
        config = self.w.configuration(self.repo)
        for key in ('policy_confirmed', 'enabled', 'profile', 'runtime_version', 'policy_record'):
            config.pop(key, None)
        config['schema_version'] = 1
        config['clients'] = ['codex']
        self.w.write_json(self.repo / self.w.CONFIG, config)
        result = self.w.begin(self.repo, 'Change', ['README.md'])
        self.assertEqual(result['status'], 'needs-policy-confirmation')
        self.assertFalse((self.repo / '.git/big-repo').exists())
        result = self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertTrue(result['config']['policy_confirmed'])

    def test_upgrade_and_disconnect_refuse_active_tasks_and_dry_runs_do_not_write(self):
        self.init(client='codex')
        self.w.begin(self.repo, 'Change', ['README.md'])
        before = self.files()
        for operation in (self.w.upgrade, self.w.disconnect):
            with self.assertRaisesRegex(self.w.WorkflowError, 'active-task'):
                if operation == self.w.upgrade:
                    operation(self.repo, delivery='commit', client='none', profile='core')
                else:
                    operation(self.repo)
        self.assertEqual(self.files(), before)
        self.w.cancel(self.repo, 'User cancels before upgrade')
        before = self.files()
        self.w.upgrade(self.repo, delivery='commit', client='none', profile='core', dry_run=True)
        self.w.disconnect(self.repo, dry_run=True)
        self.assertEqual(self.files(), before)

    def test_disconnect_only_removes_owned_instructions_and_disables_tasks(self):
        original = '# User rules\r\nRetain this.\r\n'
        agents = self.repo / 'AGENTS.md'
        agents.write_bytes(original.encode())
        self.init(client='both')
        with agents.open('ab') as stream:
            stream.write(b'\nUser tail.\n')
        readme = (self.repo / 'README.md').read_bytes()
        self.w.disconnect(self.repo)
        text = agents.read_bytes().decode()
        self.assertTrue(text.startswith(original))
        self.assertTrue(text.endswith('\nUser tail.\n'))
        self.assertNotIn(self.w.START, text)
        self.assertEqual((self.repo / 'README.md').read_bytes(), readme)
        self.assertFalse(self.w.configuration(self.repo)['enabled'])
        self.assertEqual(self.w.begin(self.repo, 'Change', ['README.md'])['status'], 'disconnected')

    def test_malformed_marker_and_unknown_runtime_file_refuse_lifecycle_writes(self):
        self.init(client='codex')
        agents = self.repo / 'AGENTS.md'
        original = agents.read_bytes()
        agents.write_text(self.w.START, encoding='utf-8')
        before = self.files()
        with self.assertRaises(self.w.WorkflowError):
            self.w.disconnect(self.repo)
        self.assertEqual(self.files(), before)
        agents.write_bytes(original)
        (self.repo / '.big-repo/plugin/user.txt').write_text('User resource')
        before = self.files()
        with self.assertRaisesRegex(self.w.WorkflowError, 'unowned-runtime'):
            self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertEqual(self.files(), before)

    def test_upgrade_rolls_back_on_partial_project_write(self):
        self.init(client='codex')
        config = (self.repo / self.w.CONFIG).read_bytes()
        agents = (self.repo / 'AGENTS.md').read_bytes()
        original = self.w.atomic_text

        def fail(path, text):
            if path.name == 'AGENTS.md':
                raise OSError('simulated interruption')
            return original(path, text)

        with patch.object(self.w, 'atomic_text', side_effect=fail):
            with self.assertRaises(OSError):
                self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertEqual((self.repo / self.w.CONFIG).read_bytes(), config)
        self.assertEqual((self.repo / 'AGENTS.md').read_bytes(), agents)

    def test_invalid_options_and_missing_showcase_resources_do_not_write(self):
        before = self.files()
        for options in ({'delivery': 'invalid'}, {'showcase': 'local'}, {'client': 'invalid'}):
            with self.subTest(options=options), self.assertRaises(self.w.WorkflowError):
                self.init(**options)
            self.assertEqual(self.files(), before)

    def test_core_runtime_has_no_research_images_or_explorer(self):
        self.init()
        runtime = self.repo / '.big-repo/plugin'
        self.assertFalse((runtime / 'assets').exists())
        self.assertFalse((runtime / 'research').exists())
        self.assertFalse((runtime / 'scripts/explore.py').exists())
        self.assertFalse((runtime / 'scripts/collect_research.py').exists())
        self.assertTrue((runtime / 'skills/repo-showcase/SKILL.md').exists())

    def test_core_source_cannot_claim_full_upgrade(self):
        self.init()
        script = self.repo / '.big-repo/plugin/scripts/project_workflow.py'
        spec = importlib.util.spec_from_file_location('core_workflow', script)
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        before = self.files()
        with self.assertRaisesRegex(core.WorkflowError, 'full-source'):
            core.upgrade(self.repo, delivery='commit', client='none', profile='full')
        self.assertEqual(before, self.files())
        result = self.w.upgrade(self.repo, delivery='commit', client='none', profile='full')
        self.assertEqual(result['config']['profile'], 'full')
        self.assertTrue((script.parents[1] / 'assets/explorer.html').exists())

    def test_interrupted_lifecycle_blocks_task_and_init_before_writes(self):
        self.init(client='codex')
        original = self.w.atomic_text

        def fail(path, text):
            if path.name == 'AGENTS.md':
                raise OSError('interrupted')
            return original(path, text)

        with patch.object(self.w, 'atomic_text', side_effect=fail), patch.object(
                self.w, 'rollback_lifecycle', side_effect=OSError('process stopped')):
            with self.assertRaises(OSError):
                self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        before = self.files()
        self.assertEqual(self.w.status(self.repo)['status'], 'recovery-required')
        self.assertEqual(before, self.files())
        for operation in (lambda: self.w.begin(self.repo, 'Change', ['README.md']),
                          lambda: self.w.deliver(self.repo),
                          lambda: self.init(update=True)):
            with self.assertRaisesRegex(self.w.WorkflowError, 'lifecycle-recovery-required'):
                operation()
            self.assertEqual(before, self.files())
        self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertEqual(self.w.begin(self.repo, 'Change', ['README.md'])['status'], 'working')

    def test_interrupted_upgrade_is_recovered_before_retry(self):
        self.init(client='codex')
        original = self.w.atomic_text

        def fail(path, text):
            if path.name == 'AGENTS.md':
                raise OSError('interrupted')
            return original(path, text)

        with patch.object(self.w, 'atomic_text', side_effect=fail), patch.object(self.w, 'rollback_lifecycle', side_effect=OSError('process stopped')):
            with self.assertRaises(OSError):
                self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        result = self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertEqual(result['status'], 'upgraded')
        self.assertFalse(self.w.configuration(self.repo)['clients'])

    def test_interrupted_upgrade_refuses_modified_runtime_or_user_rules(self):
        self.init(client='codex')
        original = self.w.atomic_text

        def fail(path, text):
            if path.name == 'AGENTS.md':
                raise OSError('interrupted')
            return original(path, text)

        with patch.object(self.w, 'atomic_text', side_effect=fail), patch.object(self.w, 'rollback_lifecycle', side_effect=OSError('process stopped')):
            with self.assertRaises(OSError):
                self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        file = self.repo / '.big-repo/plugin/user.txt'
        file.write_text('Concurrent user data')
        before = self.files()
        with self.assertRaisesRegex(self.w.WorkflowError, 'runtime-conflict'):
            self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertEqual(before, self.files())

    def test_stable_launcher_recovers_after_runtime_directory_is_absent(self):
        self.init(client='codex')
        plugin = self.repo / '.big-repo/plugin'
        launcher = self.repo / '.big-repo/workflow.py'
        self.assertTrue(launcher.is_file())
        original_replace = Path.replace

        def replace(path, target):
            if path.name == 'new-runtime' and Path(target) == plugin:
                raise OSError('process stopped during runtime swap')
            return original_replace(path, target)

        with patch.object(Path, 'replace', new=replace), patch.object(
                self.w, 'rollback_lifecycle', side_effect=OSError('process stopped')
        ):
            with self.assertRaises(OSError):
                self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertFalse(plugin.exists())
        old_script = next(
            (self.repo / '.git/big-repo').glob('backup-*/old-runtime/scripts/project_workflow.py')
        )
        old_script.write_text('raise SystemExit(99)\n', encoding='utf-8')

        status = subprocess.run(
            [sys.executable, str(launcher), 'status', '--repo', str(self.repo)],
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertEqual(json.loads(status.stdout)['status'], 'recovery-required')

        recovered = subprocess.run(
            [
                sys.executable,
                str(launcher),
                'upgrade',
                '--repo',
                str(self.repo),
                '--delivery',
                'commit',
                '--client',
                'none',
                '--profile',
                'core',
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)['status'], 'upgraded')
        self.assertTrue(plugin.is_dir())

    def test_stable_launcher_recovers_an_interrupted_runtime_creation(self):
        self.init(client='codex')
        plugin = self.repo / '.big-repo/plugin'
        launcher = self.repo / '.big-repo/workflow.py'
        removed = self.repo / 'removed-runtime'
        plugin.replace(removed)
        original_replace = Path.replace

        def replace(path, target):
            if path.name == 'new-runtime' and Path(target) == plugin:
                raise OSError('process stopped during runtime creation')
            return original_replace(path, target)

        with patch.object(Path, 'replace', new=replace), patch.object(
                self.w, 'rollback_lifecycle', side_effect=OSError('process stopped')
        ):
            with self.assertRaises(OSError):
                self.w.upgrade(self.repo, delivery='commit', client='none', profile='core')
        self.assertFalse(plugin.exists())

        recovered = subprocess.run(
            [
                sys.executable,
                str(launcher),
                'upgrade',
                '--repo',
                str(self.repo),
                '--delivery',
                'commit',
                '--client',
                'none',
                '--profile',
                'core',
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)['status'], 'upgraded')
        self.assertTrue((plugin / 'scripts/project_workflow.py').is_file())

    def test_legacy_deliver_does_not_query_or_write_remote(self):
        self.init()
        config = self.w.configuration(self.repo)
        config['schema_version'] = 1
        config['clients'] = ['codex']
        self.w.write_json(self.repo / self.w.CONFIG, config)
        with patch.object(self.w, 'observed_pr', side_effect=AssertionError('Unexpected remote query')):
            self.assertEqual(self.w.deliver(self.repo)['status'], 'needs-policy-confirmation')
        self.assertFalse((self.repo / '.git/big-repo').exists())


if __name__ == '__main__':
    unittest.main()

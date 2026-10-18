import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / 'plugins/repo-maintainer/scripts/project_workflow.py'


class ProjectWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('project_workflow', SCRIPT)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Workflow Test')
        self.git('config', 'user.email', 'workflow@example.invalid')
        self.git('remote', 'add', 'origin', 'https://github.com/example/project.git')
        (self.repo / '.gitignore').write_text('__pycache__/\n*.pyc\n')
        (self.repo / 'AGENTS.md').write_text('# Existing rules\nKeep my rules.\n')
        (self.repo / 'CLAUDE.md').write_text('# Existing Claude rules\n')
        (self.repo / 'feature.py').write_text('def value():\n    return 1\n')
        (self.repo / 'checks').mkdir()
        (self.repo / 'checks/test_feature.py').write_text(
            'import unittest\nfrom feature import value\n'
            'class FeatureTest(unittest.TestCase):\n'
            '    def test_positive_value(self):\n        self.assertGreater(value(), 0)\n')
        self.git('add', '.')
        self.git('commit', '-m', 'test: initial project')
        self.remote_head = None
        self.pr = None
        self.writes = []
        self.pending = False
        self.merge_timeout = False
        self.create_timeout = False

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def setup_project(self, delivery='merge', no_ci=False):
        result = self.m.initialize(self.repo, delivery=delivery, no_ci=no_ci,
                                  checks=[f'{self.quote_python()} -B -m unittest discover -s checks'],
                                  ci=None if no_ci else ['tests'], base='main')
        self.assertEqual(result['status'], 'configured')
        self.git('add', '.')
        self.git('commit', '-m', 'chore: enable project delivery')

    def quote_python(self):
        return self.m.shlex.quote(sys.executable)

    def start(self, event='feedback-1', delivery=None):
        return self.m.begin(self.repo, 'Update positive value', ['feature.py', 'checks/**'], event, delivery)

    def change(self, value=42):
        (self.repo / 'feature.py').write_text(f'def value():\n    return {value}\n')
        self.git('add', 'feature.py')
        self.git('commit', '-m', 'fix: update positive value')

    def validated_review(self):
        self.assertEqual(self.m.check(self.repo)['status'], 'validated')
        self.assertEqual(self.m.review(self.repo, self.git('rev-parse', 'HEAD'), ['independent-test-review'])['status'], 'reviewed')

    def pr_data(self):
        head = self.git('rev-parse', 'HEAD')
        return {'url': 'https://github.com/example/project/pull/1', 'number': 1,
                'state': 'OPEN', 'isDraft': False, 'headRefOid': head,
                'headRefName': self.git('branch', '--show-current'), 'baseRefName': 'main',
                'mergeable': 'MERGEABLE', 'mergeStateStatus': 'CLEAN', 'reviewDecision': '',
                'mergeCommit': None, 'statusCheckRollup': [{'name': 'tests', 'status': 'COMPLETED', 'conclusion': 'SUCCESS'}]}

    @contextmanager
    def github(self):
        original = subprocess.run

        def fake(argv, **kwargs):
            output = ''
            if argv[:2] == ['git', 'ls-remote']:
                output = '' if self.remote_head is None else self.remote_head + '\trefs/heads/task\n'
            elif argv[:2] == ['git', 'push']:
                self.writes.append('push')
                self.remote_head = self.git('rev-parse', 'HEAD')
            elif argv[:3] == ['gh', 'pr', 'list']:
                output = json.dumps([] if self.pr is None else [self.pr])
            elif argv[:3] == ['gh', 'pr', 'create']:
                self.writes.append('create-pr')
                self.pr = self.pr_data()
                if self.create_timeout:
                    raise subprocess.TimeoutExpired('gh', 90)
                output = self.pr['url']
            elif argv[:3] == ['gh', 'pr', 'view']:
                output = json.dumps(self.pr)
            elif argv[:2] == ['gh', 'api']:
                output = json.dumps({'full_name': 'example/project', 'permissions': {'push': True}, 'allow_squash_merge': True})
            elif argv[:3] == ['gh', 'pr', 'merge']:
                self.writes.append('merge')
                self.assertEqual(argv[-2:], ['--match-head-commit', self.git('rev-parse', 'HEAD')])
                self.pr.update(state='MERGED', mergeCommit={'oid': 'a' * 40})
                if self.merge_timeout:
                    raise subprocess.TimeoutExpired('gh', 60)
            else:
                return original(argv, **kwargs)
            if not kwargs.get('text'):
                output = output.encode()
            return subprocess.CompletedProcess(argv, 0, output, '' if kwargs.get('text') else b'')

        with patch.object(self.m.subprocess, 'run', side_effect=fake):
            yield

    def body(self):
        file = self.m.state_dir(self.repo) / 'pr-body.md'
        file.write_text('Fix positive value; project tests passed.')
        return file

    def test_onboarding_preserves_rules_and_vendors_portable_runtime(self):
        self.setup_project()
        for file, original in [('AGENTS.md', '# Existing rules\nKeep my rules.\n'), ('CLAUDE.md', '# Existing Claude rules\n')]:
            text = (self.repo / file).read_text()
            self.assertTrue(text.startswith(original))
            self.assertEqual(text.count(self.m.START), 1)
            self.assertIn('普通问答', text)
        config = self.m.configuration(self.repo)
        self.assertEqual(config['trigger'], 'task-or-feedback')
        self.assertNotIn(str(self.repo), json.dumps(config))
        copied = self.repo / config['plugin_path'] / 'scripts/project_workflow.py'
        self.assertTrue(copied.is_file())
        result = subprocess.run([sys.executable, str(copied), 'status', '--repo', str(self.repo)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['status'], 'configured')
        before = self.git('status', '--porcelain')
        self.m.initialize(self.repo)
        self.assertEqual(self.git('status', '--porcelain'), before)

    def test_missing_validation_and_ci_are_not_reported_ready(self):
        result = self.m.initialize(self.repo)
        self.assertEqual(result['status'], 'needs-configuration')
        self.assertIn('project-validation-commands', result['missing'])
        self.assertIn('actual-ci-check-names-or-confirmed-no-ci-policy', result['missing'])
        self.assertEqual(self.start()['status'], 'needs-configuration')
        self.assertEqual(self.m.initialize(self.repo)['status'], 'needs-configuration')
        self.assertEqual(self.m.status(self.repo)['status'], 'needs-configuration')

    def test_malformed_instruction_blocks_are_preserved(self):
        file = self.repo / 'AGENTS.md'
        text = file.read_text() + self.m.START
        file.write_text(text)
        with self.assertRaises(self.m.WorkflowError):
            self.m.initialize(self.repo)
        self.assertEqual(file.read_text(), text)
        self.assertFalse((self.repo / self.m.CONFIG).exists())

    def test_begin_deduplicates_event_and_blocks_parallel_objective(self):
        self.setup_project()
        first = self.start()
        self.assertTrue(self.git('branch', '--show-current').startswith('maintain/'))
        again = self.start()
        self.assertEqual(first['task_id'], again['task_id'])
        self.assertTrue(again['resumed'])
        with self.assertRaises(self.m.WorkflowError):
            self.m.begin(self.repo, 'Different feedback', ['feature.py'], 'feedback-2')
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_failed_checks_are_retained_and_recovered_on_fixed_candidate(self):
        self.setup_project(delivery='commit')
        self.start()
        self.change(-99)
        first = self.m.check(self.repo)
        self.assertEqual(first['status'], 'blocked')
        self.assertNotEqual(first['checks'][0]['exit_code'], 0)
        failure_log = Path(first['checks'][0]['result'])
        with self.assertRaises(self.m.WorkflowError):
            self.m.check(self.repo)
        self.change(42)
        second = self.m.check(self.repo)
        self.assertEqual(second['status'], 'validated')
        self.assertNotEqual(first['checks'][0]['result'], second['checks'][0]['result'])
        self.assertIn(b'FAIL', failure_log.read_bytes())
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_resume_cannot_ignore_narrower_delivery(self):
        self.setup_project()
        self.start()
        with self.assertRaisesRegex(self.m.WorkflowError, 'delivery-changed'):
            self.start(delivery='commit')
        with self.assertRaisesRegex(self.m.WorkflowError, 'delivery-changed'):
            self.start(event=None, delivery='commit')

    def test_remote_delivery_covers_existing_branch_commits(self):
        self.setup_project()
        baseline = self.git('rev-parse', 'HEAD')
        self.git('switch', '-c', 'user-work')
        (self.repo / 'unrelated.txt').write_text('prior work')
        self.git('add', '.')
        self.git('commit', '-m', 'feat: prior work')
        self.assertTrue(self.start()['initial_changes_require_reconciliation'])
        self.change()
        path, _, _, task = self.m.current_task(self.repo)
        self.assertEqual(task['base_sha'], baseline)
        self.assertEqual(self.m.check(self.repo)['status'], 'blocked')
        self.assertEqual(self.writes, [])

    def test_resume_requires_same_scope(self):
        self.setup_project()
        self.start()
        for event in ('feedback-1', None):
            with self.assertRaisesRegex(self.m.WorkflowError, 'scope-changed'):
                self.m.begin(self.repo, 'Update positive value', ['feature.py'], event)

    def test_remote_baseline_includes_local_main_ahead_of_origin(self):
        self.setup_project()
        baseline = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/main', baseline)
        (self.repo / 'unrelated.txt').write_text('prior local main work')
        self.git('add', '.')
        self.git('commit', '-m', 'feat: prior local main work')
        self.start()
        self.change()
        self.assertEqual(self.m.current_task(self.repo)[3]['base_sha'], baseline)
        self.assertEqual(self.m.check(self.repo)['status'], 'blocked')

    def test_block_cannot_reactivate_closed_task(self):
        self.setup_project(delivery='commit')
        self.start()
        self.m.cancel(self.repo, 'User cancelled')
        with self.assertRaisesRegex(self.m.WorkflowError, 'task-already-closed'):
            self.m.block(self.repo, 'retry')
        self.assertEqual(self.m.status(self.repo)['status'], 'cancelled')
        self.start(event='new-task')
        self.validated_review()
        self.m.deliver(self.repo)
        with self.assertRaisesRegex(self.m.WorkflowError, 'task-already-closed'):
            self.m.block(self.repo, 'retry')
        self.assertEqual(self.m.status(self.repo)['status'], 'completed')

    def test_final_commit_invalidation_and_scope_are_enforced(self):
        self.setup_project(delivery='commit')
        self.start()
        self.change()
        self.validated_review()
        self.change(999)
        with self.assertRaises(self.m.WorkflowError):
            self.m.deliver(self.repo)
        (self.repo / 'outside.txt').write_text('unrelated')
        self.assertEqual(self.m.check(self.repo)['status'], 'blocked')

    def test_local_delivery_and_completed_event_are_idempotent(self):
        self.setup_project(delivery='commit')
        first = self.start()
        self.change()
        self.validated_review()
        self.assertEqual(self.m.deliver(self.repo)['result']['status'], 'committed')
        self.assertEqual(self.m.deliver(self.repo)['status'], 'completed')
        self.assertEqual(self.start()['task_id'], first['task_id'])
        self.assertEqual(self.start()['status'], 'completed')

    def test_no_change_task_finishes_without_remote_writes(self):
        self.setup_project()
        self.start()
        self.validated_review()
        with self.github():
            result = self.m.deliver(self.repo)
        self.assertEqual(result['result']['status'], 'no-changes')
        self.assertEqual(self.writes, [])

    def test_policy_and_origin_changes_prevent_delivery(self):
        self.setup_project(delivery='pr')
        with self.assertRaises(self.m.WorkflowError):
            self.start(delivery='merge')
        self.start()
        self.change()
        self.validated_review()
        self.git('remote', 'set-url', 'origin', 'https://github.com/example/other.git')
        with self.assertRaises(self.m.WorkflowError):
            self.m.deliver(self.repo)
        config = self.m.configuration(self.repo)
        config['delivery'] = 'merge'
        self.m.write_json(self.repo / self.m.CONFIG, config)
        with self.assertRaises(self.m.WorkflowError):
            self.m.check(self.repo)

    def test_remote_delivery_waits_reuses_pr_and_merges_once(self):
        self.setup_project()
        self.start()
        self.change()
        self.validated_review()
        with self.github():
            self.pr = self.pr_data()
            self.pr['statusCheckRollup'][0].update(status='IN_PROGRESS', conclusion='')
            waiting = self.m.deliver(self.repo)
            self.assertEqual(waiting['status'], 'waiting')
            self.pr['statusCheckRollup'][0].update(status='COMPLETED', conclusion='SUCCESS')
            done = self.m.deliver(self.repo)
            self.assertEqual(done['result']['status'], 'merged')
            self.assertEqual(self.m.deliver(self.repo)['status'], 'completed')
        self.assertEqual(self.writes, ['push', 'merge'])

    def test_new_pr_is_created_and_merge_timeout_is_reconciled(self):
        self.setup_project()
        self.start()
        self.change()
        self.validated_review()
        self.merge_timeout = True
        with self.github():
            first = self.m.deliver(self.repo, 'fix: value', self.body())
            self.assertEqual(first['status'], 'blocked')
            second = self.m.deliver(self.repo)
            self.assertEqual(second['result']['status'], 'merged')
        self.assertEqual(self.writes, ['push', 'create-pr', 'merge'])

    def test_create_timeout_reconciles_existing_pr_without_duplicate(self):
        self.setup_project(delivery='pr')
        self.start()
        self.change()
        self.validated_review()
        self.create_timeout = True
        with self.github():
            with self.assertRaises(subprocess.TimeoutExpired):
                self.m.deliver(self.repo, 'fix: value', self.body())
            done = self.m.deliver(self.repo)
            self.assertEqual(done['result']['status'], 'pr-delivered')
        self.assertEqual(self.writes, ['push', 'create-pr'])

    def test_visible_failed_ci_blocks_even_for_confirmed_no_ci_policy(self):
        self.setup_project(no_ci=True)
        self.start()
        self.change()
        self.validated_review()
        with self.github():
            self.pr = self.pr_data()
            self.pr['statusCheckRollup'][0]['conclusion'] = 'FAILURE'
            self.assertEqual(self.m.deliver(self.repo)['status'], 'blocked')
        self.assertNotIn('merge', self.writes)

    def test_no_ci_policy_still_requires_review_then_can_merge(self):
        self.setup_project(no_ci=True)
        self.start()
        self.change()
        self.assertEqual(self.m.check(self.repo)['status'], 'validated')
        with self.assertRaises(self.m.WorkflowError):
            self.m.deliver(self.repo)
        self.m.review(self.repo, self.git('rev-parse', 'HEAD'), ['independent-test-review'])
        with self.github():
            self.pr = self.pr_data()
            self.pr['statusCheckRollup'] = []
            self.assertEqual(self.m.deliver(self.repo)['status'], 'completed')
        self.assertEqual(self.writes, ['push', 'merge'])

    def test_inference_uses_manifest_scripts_without_shell_execution(self):
        (self.repo / 'package.json').write_text(json.dumps({'packageManager': 'pnpm@10.0.0',
            'scripts': {'lint': 'lint-tool', 'test': 'test-tool'}}))
        checks = self.m.infer_checks(self.repo)
        self.assertEqual(checks, [{'id': 'lint', 'argv': ['pnpm', 'run', 'lint']},
                                  {'id': 'test', 'argv': ['pnpm', 'run', 'test']}])
        self.assertEqual(self.git('branch', '--show-current'), 'main')

    def test_user_cancellation_preserves_work_and_allows_replanning(self):
        self.setup_project()
        task = self.start()
        (self.repo / 'feature.py').write_text('def value():\n    return 88\n')
        config = self.m.configuration(self.repo)
        config['delivery'] = 'commit'
        self.m.write_json(self.repo / self.m.CONFIG, config)
        self.assertEqual(self.m.cancel(self.repo, 'User changed task scope')['status'], 'cancelled')
        self.assertIn('return 88', (self.repo / 'feature.py').read_text())
        self.assertTrue((Path(task['state_directory']) / 'state.json').exists())
        next_task = self.m.begin(self.repo, 'Replanned task', ['feature.py', '.repo-maintainer/**'], 'feedback-2')
        self.assertNotEqual(next_task['task_id'], task['task_id'])

    def test_nested_process_lock_prevents_concurrent_operation(self):
        directory = self.m.state_dir(self.repo)
        with self.m.locked(directory):
            with self.assertRaises(self.m.WorkflowError):
                with self.m.locked(directory):
                    self.fail('Concurrent lock should not be acquired')
        with self.m.locked(directory):
            pass

    def test_unicode_feedback_and_managed_update_preserve_existing_bytes(self):
        file = self.repo / 'AGENTS.md'
        original = '# 我的项目规则\r\n保留原有说明。\r\n'.encode('utf-8')
        file.write_bytes(original)
        self.setup_project(delivery='commit')
        self.assertTrue(file.read_bytes().startswith(original))
        with file.open('ab') as stream:
            stream.write('\r\n用户追加的尾部说明。\r\n'.encode('utf-8'))
        tail = '\r\n用户追加的尾部说明。\r\n'.encode('utf-8')
        self.m.initialize(self.repo, update=True)
        self.assertTrue(file.read_bytes().startswith(original))
        self.assertTrue(file.read_bytes().endswith(tail))
        result = self.m.begin(self.repo, '修复中文反馈中的输入问题', ['feature.py', 'AGENTS.md'], '反馈-42')
        self.assertEqual(result['status'], 'working')
        self.assertEqual(self.m.status(self.repo)['objective'], '修复中文反馈中的输入问题')

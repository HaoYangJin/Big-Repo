import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

MODULE = Path(__file__).parents[1] / 'scripts/repo_tools.py'


class ToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('repo_tools', MODULE)
        cls.tools = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.tools)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-b', 'main')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        (self.root / 'README.md').write_text('# Test\n', encoding='utf-8')
        self.git('add', 'README.md')
        self.git('commit', '-m', 'docs: init')
        self.base = self.git('rev-parse', 'HEAD').strip()
        self.task = {'objective': 'update docs', 'base_sha': self.base,
                     'allowed_paths': ['README.md', 'docs/**'],
                     'allowed_actions': ['commit', 'push', 'create-pr'],
                     'validation': [{'id': 'docs', 'command': 'manual: content and links'}],
                     'done_when': ['PR ready for review']}

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                              capture_output=True, text=True, encoding='utf-8').stdout

    def evidence(self, code=0):
        return {'fingerprint': self.tools.snapshot(self.root)['fingerprint'],
                'checks': [{'id': 'docs', 'exit_code': code,
                            'command': 'manual: content and links', 'result': 'checked'}]}

    def test_clean_snapshot_does_not_mutate(self):
        before = self.git('status', '--porcelain')
        data = self.tools.snapshot(self.root)
        self.assertEqual(data['head_sha'], self.base)
        self.assertEqual(before, self.git('status', '--porcelain'))

    def test_dirty_untracked_and_deleted_change_fingerprint(self):
        first = self.evidence()['fingerprint']
        (self.root / 'other.txt').write_text('one')
        second = self.evidence()['fingerprint']
        (self.root / 'README.md').unlink()
        self.assertNotEqual(first, second)
        self.assertNotEqual(second, self.evidence()['fingerprint'])

    def test_preflight_preserves_existing_changes(self):
        (self.root / 'README.md').write_text('# Edited\n')
        result = self.tools.preflight(self.root, self.task)
        self.assertEqual(result['status'], 'handoff')
        self.assertEqual((self.root / 'README.md').read_text(), '# Edited\n')

    def test_allowed_change_passes(self):
        (self.root / 'README.md').write_text('# Updated\n')
        result = self.tools.accept(self.root, self.task, self.evidence())
        self.assertEqual(result['status'], 'verified-local')

    def test_missing_and_stale_evidence(self):
        self.assertEqual(self.tools.accept(self.root, self.task, {})['status'], 'handoff')
        evidence = self.evidence()
        (self.root / 'README.md').write_text('# Changed\n')
        self.assertIn('stale-evidence', self.tools.accept(self.root, self.task, evidence)['issues'])

    def test_first_failure_even_with_later_success(self):
        evidence = self.evidence(1)
        evidence['checks'].append(dict(evidence['checks'][0], exit_code=0))
        self.assertIn('validation-failed', self.tools.accept(self.root, self.task, evidence)['issues'])

    def test_unknown_check_failure_also_stops(self):
        evidence = self.evidence()
        evidence['checks'].append({'id': 'unexpected', 'exit_code': 2})
        self.assertEqual(self.tools.accept(self.root, self.task, evidence)['status'], 'handoff')

    def test_out_of_scope_committed_change(self):
        (self.root / 'secret.txt').write_text('not in scope')
        self.git('add', 'secret.txt')
        self.git('commit', '-m', 'docs: unrelated')
        result = self.tools.accept(self.root, self.task, self.evidence())
        self.assertIn('out-of-scope:secret.txt', result['issues'])

    def test_rename_checks_deleted_source(self):
        self.git('mv', 'README.md', 'renamed.md')
        result = self.tools.accept(self.root, self.task, self.evidence())
        self.assertIn('out-of-scope:renamed.md', result['issues'])

    def test_task_validation_rejects_traversal_and_release(self):
        for key, value in [('allowed_paths', ['../*']), ('allowed_actions', ['release']),
                           ('base_sha', '--help'), ('validation', [])]:
            task = dict(self.task, **{key: value})
            with self.assertRaises(ValueError):
                self.tools.preflight(self.root, task)

    def test_nonancestor_base(self):
        self.git('checkout', '--orphan', 'other')
        self.git('commit', '-m', 'docs: unrelated root')
        self.assertIn('base-not-ancestor', self.tools.preflight(self.root, self.task)['issues'])

    def test_missing_readme_and_asset(self):
        (self.root / 'README.md').unlink()
        self.assertEqual(self.tools.audit_showcase(self.root)['status'], 'handoff')
        (self.root / 'README.md').write_text('![demo](missing.gif)')
        self.assertIn('missing-local:missing.gif', self.tools.audit_showcase(self.root)['issues'])

    def test_private_external_images_are_blocked(self):
        (self.root / 'README.md').write_text('![stars](https://api.star-history.com/svg?repos=private/name)')
        result = self.tools.audit_showcase(self.root, private=True)
        self.assertTrue(any(i.startswith('private-external-media:') for i in result['issues']))

    def test_dark_theme_html_is_inspected(self):
        (self.root / 'README.md').write_text('<picture><source media="(prefers-color-scheme: dark)" srcset="dark.svg"><img src="light.svg"></picture>')
        result = self.tools.audit_showcase(self.root)
        self.assertIn('missing-local:dark.svg', result['issues'])
        self.assertIn('missing-local:light.svg', result['issues'])

    def test_anchors_do_not_trigger_handoff(self):
        (self.root / 'README.md').write_text('[Usage](#usage)\n\n## Usage\n')
        self.assertEqual(self.tools.audit_showcase(self.root)['status'], 'checked-offline')

    def test_html_media_whitespace_and_unquoted_values(self):
        for html in ('<img src = "https://example.invalid/private.png">',
                     '<img src=https://example.invalid/private.png>',
                     '<video poster="https://example.invalid/private.png"></video>'):
            (self.root / 'README.md').write_text(html)
            self.assertEqual(self.tools.audit_showcase(self.root)['status'], 'handoff')

    def test_placeholder_detection(self):
        (self.root / 'README.md').write_text('![demo](https://example.com/OWNER/REPO.gif)')
        self.assertIn('placeholder', self.tools.audit_showcase(self.root)['issues'])

    def test_showcase_preview_is_idempotent_and_private_safe(self):
        first = self.tools.render_showcase('# Demo\n', 'a/b', private=True)
        second = self.tools.render_showcase(first, 'a/b', private=True)
        self.assertEqual(first, second)
        self.assertNotIn('star-history.com', first)
        self.assertNotIn('shields.io', first)

    def test_public_zero_stars_no_fake_trend(self):
        text = self.tools.render_showcase('# Demo', 'a/b', private=False)
        self.assertNotIn('star-history.com', text)
        self.assertNotIn('排名', text)

    def test_public_star_history_opt_in(self):
        text = self.tools.render_showcase('# Demo', 'a/b', private=False, star_history=True)
        self.assertIn('api.star-history.com', text)
        self.assertIn('文字入口', text)

    def test_private_history_and_bad_repo_rejected(self):
        with self.assertRaises(ValueError):
            self.tools.render_showcase('', 'a/b', private=True, star_history=True)
        with self.assertRaises(ValueError):
            self.tools.render_showcase('', 'a/b?token=x')

    def test_bad_marker_rejected(self):
        with self.assertRaises(ValueError):
            self.tools.render_showcase('<!-- big-repo:showcase:start -->', 'a/b')

    def test_network_checks_never_default(self):
        (self.root / 'README.md').write_text('[link](https://example.invalid/no-network)')
        result = self.tools.audit_showcase(self.root)
        self.assertEqual(result['external_links'][0]['status'], 'not-network-checked')

    def test_hidden_staged_change_is_not_accepted(self):
        (self.root / 'other.txt').write_text('baseline')
        self.git('add', 'other.txt')
        self.git('commit', '-m', 'docs: baseline')
        self.task['base_sha'] = self.git('rev-parse', 'HEAD').strip()
        (self.root / 'other.txt').write_text('staged one')
        self.git('add', 'other.txt')
        (self.root / 'other.txt').write_text('baseline')
        evidence = self.evidence()
        self.assertIn('out-of-scope:other.txt', self.tools.accept(self.root, self.task, evidence)['issues'])
        (self.root / 'other.txt').write_text('staged two')
        self.git('add', 'other.txt')
        (self.root / 'other.txt').write_text('baseline')
        self.assertNotEqual(evidence['fingerprint'], self.evidence()['fingerprint'])

    def test_url_secrets_never_returned(self):
        secret = 'VERY_PRIVATE_VALUE'
        (self.root / 'README.md').write_text(f'![x](https://user:{secret}@example.com/x?token={secret})')
        result = json.dumps(self.tools.audit_showcase(self.root))
        self.assertNotIn(secret, result)
        self.assertIn('credential-in-url', result)
        for target in ('missing.png?token=', '../missing?token='):
            (self.root / 'README.md').write_text(f'![x]({target}{secret})')
            result = json.dumps(self.tools.audit_showcase(self.root))
            self.assertNotIn(secret, result)
            self.assertIn('credential-in-url', result)

    def test_reference_images_are_inspected(self):
        (self.root / 'README.md').write_text('![stars][chart]\n\n[chart]: https://api.star-history.com/svg?repos=private/name\n')
        result = self.tools.audit_showcase(self.root)
        self.assertEqual(result['status'], 'handoff')
        self.assertEqual(len(result['external_links']), 1)

    def test_cli_operations_and_input_errors(self):
        task = self.root.parent / (self.root.name + '-task.json')
        evidence = self.root.parent / (self.root.name + '-evidence.json')
        self.addCleanup(lambda: task.unlink(missing_ok=True))
        self.addCleanup(lambda: evidence.unlink(missing_ok=True))
        task.write_text(json.dumps(self.task))
        evidence.write_text(json.dumps(self.evidence()))
        commands = [(['snapshot'], 0), (['showcase', '--format', 'markdown'], 0),
                    (['preflight', '--task', str(task)], 0),
                    (['accept', '--task', str(task), '--evidence', str(evidence)], 0),
                    (['preview', '--repository', 'a/b'], 0),
                    (['preflight'], 2), (['pr', '--pr', 'bad'], 2),
                    (['preview', '--readme', '../outside.md'], 2)]
        for options, expected in commands:
            with patch('sys.argv', ['tools', *options, '--repo', str(self.root)]), redirect_stdout(StringIO()):
                self.assertEqual(self.tools.main(), expected)

    def test_pr_status_success_and_permission_failure(self):
        with patch.object(self.tools.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=b'{"headRefOid":"abc"}')) as query:
            self.assertEqual(self.tools.pr_status('a/b#1')['status'], 'observed')
            # gh 2.46 supports these PR fields but rejects baseRefOid entirely.
            fields = query.call_args.args[0][-1].split(',')
            self.assertNotIn('baseRefOid', fields)
            self.assertTrue({'headRefOid', 'baseRefName', 'mergeCommit'} <= set(fields))
        with patch.object(self.tools.subprocess, 'run', return_value=SimpleNamespace(returncode=1)):
            self.assertEqual(self.tools.pr_status('a/b#1')['status'], 'handoff')

    def test_extra_validation_and_invalid_evidence(self):
        self.assertEqual(self.tools.accept(self.root, self.task, {'checks': 'not a list'})['status'], 'handoff')
        self.task['validation'].append(self.task['validation'][0])
        with self.assertRaises(ValueError):
            self.tools.preflight(self.root, self.task)

    def test_local_traversal_and_bad_schemes(self):
        (self.root / 'README.md').write_text('[bad](../outside.txt)\n[bad](javascript:evil)\n[mail](mailto:a@example.invalid)')
        issues = self.tools.audit_showcase(self.root)['issues']
        self.assertIn('outside-repository:../outside.txt', issues)
        self.assertIn('unsupported-link-scheme:javascript', issues)

    def test_detached_head_and_nonancestor_accept(self):
        self.git('checkout', '--detach')
        self.assertIn('detached-head', self.tools.preflight(self.root, self.task)['issues'])
        self.assertIn('detached-head', self.tools.accept(self.root, self.task, self.evidence())['issues'])
        self.task['base_sha'] = 'f' * 40
        self.assertIn('base-not-ancestor', self.tools.accept(self.root, self.task, self.evidence())['issues'])

    def test_invalid_marker_order_and_snapshot_subdirectory(self):
        with self.assertRaises(ValueError):
            self.tools.render_showcase('<!-- big-repo:showcase:end --><!-- big-repo:showcase:start -->', 'a/b')
        nested = self.root / 'nested'
        nested.mkdir()
        with self.assertRaises(ValueError):
            self.tools.snapshot(nested)


if __name__ == '__main__':
    unittest.main()

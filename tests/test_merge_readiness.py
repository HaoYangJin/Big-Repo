import unittest
import json
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
from types import SimpleNamespace

import test_repo_tools as fixtures


class MergeReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.ToolTests.setUpClass()
        cls.tools = fixtures.ToolTests.tools

    git = fixtures.ToolTests.git
    evidence = fixtures.ToolTests.evidence

    def setUp(self):
        fixtures.ToolTests.setUp(self)
        self.task['allowed_actions'].append('merge')
        self.task['merge'] = {'repository': 'a/b', 'base_branch': 'main', 'required_checks': ['ci']}
        self.pr = {'url': 'https://github.com/a/b/pull/1', 'state': 'OPEN', 'isDraft': False,
                   'headRefOid': self.base, 'headRefName': 'main', 'baseRefName': 'main',
                   'mergeable': 'MERGEABLE', 'mergeStateStatus': 'CLEAN', 'reviewDecision': '',
                   'statusCheckRollup': [{'name': 'ci', 'status': 'COMPLETED', 'conclusion': 'SUCCESS'}]}

    def merge_evidence(self):
        evidence = self.evidence()
        evidence['review'] = {'head_sha': self.base, 'status': 'approved',
                              'reviewers': ['independent-review'], 'blocking_findings': 0}
        return evidence

    def readiness(self, evidence=None, reference='a/b#1'):
        with patch.object(self.tools, 'repository_policy', return_value=self.permission()), patch.object(
                self.tools, 'pr_status', return_value={'status': 'observed', 'pr': self.pr}):
            return self.tools.merge_readiness(self.root, self.task, evidence or self.merge_evidence(), reference)

    def permission(self):
        return {'status': 'observed', 'repository': 'a/b', 'can_push': True, 'squash_allowed': True}

    def test_merge_ready_does_not_mutate_repository(self):
        before = self.git('status', '--porcelain')
        self.assertEqual(self.readiness()['status'], 'ready-to-merge')
        self.assertEqual(before, self.git('status', '--porcelain'))

    def test_head_mismatch_and_wrong_target_block(self):
        self.pr['headRefOid'] = 'f' * 40
        self.assertIn('pr-head-mismatch', self.readiness()['issues'])
        self.pr['headRefOid'] = self.base
        self.pr['baseRefName'] = 'other'
        self.assertIn('pr-base-mismatch', self.readiness()['issues'])
        self.assertIn('pr-repository-mismatch', self.readiness(reference='a/other#1')['issues'])

    def test_missing_ci_draft_conflict_and_failed_ci_block(self):
        self.pr['statusCheckRollup'] = []
        self.assertEqual(self.readiness()['status'], 'handoff')
        self.pr['statusCheckRollup'] = [{'name': 'ci', 'status': 'COMPLETED', 'conclusion': 'FAILURE'}]
        self.assertIn('ci-not-success:ci', self.readiness()['issues'])
        self.pr['isDraft'] = True
        self.pr['mergeable'] = 'CONFLICTING'
        result = self.readiness()
        self.assertIn('draft-pr', result['issues'])
        self.assertIn('pr-not-mergeable', result['issues'])

    def test_pending_ci_waits_without_approving(self):
        self.pr['statusCheckRollup'] = [{'name': 'ci', 'status': 'IN_PROGRESS', 'conclusion': ''}]
        self.pr['mergeStateStatus'] = 'UNSTABLE'
        self.assertEqual(self.readiness()['status'], 'waiting')

    def test_skipped_cancelled_and_extra_failure_block(self):
        for result in ['SKIPPED', 'CANCELLED', 'NEUTRAL', 'TIMED_OUT']:
            self.pr['statusCheckRollup'][0]['conclusion'] = result
            self.assertEqual(self.readiness()['status'], 'handoff')
        self.pr['statusCheckRollup'] = [{'name': 'ci', 'status': 'COMPLETED', 'conclusion': 'SUCCESS'},
                                      {'name': 'extra', 'status': 'COMPLETED', 'conclusion': 'FAILURE'}]
        self.assertEqual(self.readiness()['status'], 'handoff')

    def test_review_must_match_head_and_remote_policy(self):
        evidence = self.merge_evidence()
        evidence['review']['head_sha'] = 'f' * 40
        self.assertIn('review-missing-or-stale', self.readiness(evidence)['issues'])
        self.pr['reviewDecision'] = 'CHANGES_REQUESTED'
        self.assertIn('review-blocked', self.readiness()['issues'])

    def test_no_merge_authorization_and_no_permissions(self):
        self.task['allowed_actions'].remove('merge')
        self.assertIn('merge-not-authorized', self.readiness()['issues'])
        self.task['allowed_actions'].append('merge')
        with patch.object(self.tools, 'repository_policy', return_value=self.permission()), patch.object(
                self.tools, 'pr_status', return_value={'status': 'handoff', 'issues': ['github-pr-unavailable']}):
            self.assertEqual(self.tools.merge_readiness(self.root, self.task, self.merge_evidence(), 'a/b#1')['status'], 'handoff')

    def test_repository_permission_or_squash_required(self):
        for permission in [dict(self.permission(), can_push=False), dict(self.permission(), squash_allowed=False), {'status': 'handoff'}]:
            with patch.object(self.tools, 'repository_policy', return_value=permission):
                result = self.tools.merge_readiness(self.root, self.task, self.merge_evidence(), 'a/b#1')
                self.assertEqual(result['status'], 'handoff')

    def test_repository_policy_read_only_api(self):
        payload = b'{"full_name":"a/b","permissions":{"push":true},"allow_squash_merge":true}'
        with patch.object(self.tools.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=payload)):
            self.assertEqual(self.tools.repository_policy('a/b'), self.permission())
        with patch.object(self.tools.subprocess, 'run', return_value=SimpleNamespace(returncode=1)):
            self.assertEqual(self.tools.repository_policy('a/b')['status'], 'handoff')

    def test_local_validation_failure_cannot_merge(self):
        evidence = self.merge_evidence()
        evidence['checks'][0]['exit_code'] = 1
        self.assertIn('validation-failed', self.readiness(evidence)['issues'])

    def test_empty_or_malformed_merge_policy_rejected(self):
        for policy in [{}, {'repository': 'a/b', 'base_branch': 'main', 'required_checks': []},
                       {'repository': 'a/b?token=x', 'base_branch': 'main', 'required_checks': ['ci']}]:
            self.task['merge'] = policy
            with self.assertRaises(ValueError):
                self.tools.validate_task(self.task)


class AutomaticMergeTests(unittest.TestCase):
    setUpClass = classmethod(MergeReadinessTests.setUpClass.__func__)
    setUp = MergeReadinessTests.setUp
    git = fixtures.ToolTests.git
    evidence = fixtures.ToolTests.evidence
    merge_evidence = MergeReadinessTests.merge_evidence
    permission = MergeReadinessTests.permission

    def merged_pr(self):
        return dict(self.pr, state='MERGED', mergeCommit={'oid': 'a' * 40})

    def execute(self, post=None, evidence=None, code=0, error=None):
        original = self.tools.subprocess.run
        self.writes = []

        def run(command, **kwargs):
            if command[:3] == ['gh', 'pr', 'merge']:
                self.writes.append(command)
                if error:
                    raise error
                return SimpleNamespace(returncode=code)
            return original(command, **kwargs)

        observations = [{'status': 'observed', 'pr': dict(self.pr)},
                        post or {'status': 'observed', 'pr': self.merged_pr()}]
        with patch.object(self.tools, 'repository_policy', return_value=self.permission()), patch.object(
                self.tools, 'pr_status', side_effect=observations), patch.object(
                self.tools.subprocess, 'run', side_effect=run):
            return self.tools.merge_pr(self.root, self.task, evidence or self.merge_evidence(), 'a/b#1')

    def test_merge_locks_sha_and_confirms_remote_commit(self):
        before = self.git('status', '--porcelain')
        result = self.execute()
        self.assertEqual(result['status'], 'merged')
        self.assertEqual(result['merge_commit'], 'a' * 40)
        self.assertEqual(self.writes, [['gh', 'pr', 'merge', '1', '--repo', 'a/b',
                                       '--squash', '--match-head-commit', self.base]])
        self.assertEqual(before, self.git('status', '--porcelain'))

    def test_waiting_and_failed_checks_do_not_write(self):
        for status, conclusion, expected in [('IN_PROGRESS', '', 'waiting'),
                                              ('COMPLETED', 'FAILURE', 'handoff')]:
            self.pr['statusCheckRollup'][0].update(status=status, conclusion=conclusion)
            self.assertEqual(self.execute()['status'], expected)
            self.assertEqual(self.writes, [])

    def test_missing_authorization_stale_evidence_and_review_do_not_write(self):
        evidence = self.merge_evidence()
        evidence['review']['head_sha'] = 'f' * 40
        self.assertEqual(self.execute(evidence=evidence)['status'], 'handoff')
        self.assertEqual(self.writes, [])
        evidence = self.merge_evidence()
        evidence['fingerprint'] = 'stale'
        self.assertEqual(self.execute(evidence=evidence)['status'], 'handoff')
        self.assertEqual(self.writes, [])
        self.task['allowed_actions'].remove('merge')
        self.assertEqual(self.execute()['status'], 'handoff')
        self.assertEqual(self.writes, [])

    def test_changed_head_is_checked_again_before_write(self):
        self.pr['headRefOid'] = 'f' * 40
        self.assertIn('pr-head-mismatch', self.execute()['issues'])
        self.assertEqual(self.writes, [])

    def test_queued_merge_is_not_reported_as_merged(self):
        result = self.execute(post={'status': 'observed', 'pr': self.pr})
        self.assertEqual(result['issues'], ['merge-outcome-unconfirmed'])
        self.assertEqual(len(self.writes), 1)

    def test_post_merge_identity_and_commit_must_match(self):
        for changes in [{'headRefOid': 'f' * 40}, {'baseRefName': 'other'},
                        {'headRefName': 'other'}, {'url': 'https://github.com/a/b/pull/2'},
                        {'url': None}, {'mergeCommit': None}, {'mergeCommit': {'oid': 'invalid'}}]:
            post = dict(self.merged_pr(), **changes)
            self.assertEqual(self.execute(post={'status': 'observed', 'pr': post})['status'], 'handoff')
            self.assertEqual(len(self.writes), 1)

    def test_failed_command_reads_remote_without_retry(self):
        self.assertEqual(self.execute(code=1)['status'], 'merged')
        self.assertEqual(len(self.writes), 1)
        result = self.execute(code=1, post={'status': 'observed', 'pr': self.pr})
        self.assertEqual(result['issues'], ['merge-command-failed'])
        self.assertEqual(len(self.writes), 1)

    def test_timeout_and_unavailable_post_read_are_unconfirmed(self):
        for error in [subprocess.TimeoutExpired('gh', 60), OSError('PRIVATE')]:
            result = self.execute(error=error)
            self.assertEqual(result['issues'], ['merge-outcome-unconfirmed'])
            self.assertNotIn('PRIVATE', json.dumps(result))
            self.assertEqual(len(self.writes), 1)
        for post in [{'status': 'handoff', 'issues': ['github-pr-unavailable']},
                     {'status': 'observed', 'pr': None}, {'status': 'observed', 'pr': []}]:
            result = self.execute(post=post)
            self.assertEqual(result['issues'], ['merge-outcome-unconfirmed'])
            self.assertEqual(len(self.writes), 1)

    def test_cli_merge_dispatch_and_exit_status(self):
        task = self.root.parent / (self.root.name + '-task.json')
        evidence = self.root.parent / (self.root.name + '-evidence.json')
        self.addCleanup(lambda: task.unlink(missing_ok=True))
        self.addCleanup(lambda: evidence.unlink(missing_ok=True))
        task.write_text(json.dumps(self.task))
        evidence.write_text(json.dumps(self.merge_evidence()))
        options = ['tools', 'merge', '--repo', str(self.root), '--task', str(task),
                   '--evidence', str(evidence), '--pr', 'a/b#1']
        for status, expected in [('merged', 0), ('waiting', 3), ('handoff', 2)]:
            with patch('sys.argv', options), patch.object(self.tools, 'merge_pr', return_value={
                    'status': status}) as merge, redirect_stdout(StringIO()) as output:
                self.assertEqual(self.tools.main(), expected)
                self.assertEqual(json.loads(output.getvalue())['status'], status)
                self.assertEqual(merge.call_args.args[-1], 'a/b#1')
        with patch('sys.argv', ['tools', 'merge']), patch.object(self.tools, 'merge_pr') as merge, redirect_stdout(StringIO()):
            self.assertEqual(self.tools.main(), 2)
            merge.assert_not_called()

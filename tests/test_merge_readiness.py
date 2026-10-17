import unittest
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

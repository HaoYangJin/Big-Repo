"""Read-only repository checks and stdout-only showcase previews. Python 3.11+."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
from html.parser import HTMLParser
from html import unescape
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from urllib.parse import quote, unquote, urlparse, urlunparse


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                            check=True, timeout=60)
    return result.stdout


def paths(data):
    return [p.decode('utf-8', errors='surrogateescape') for p in data.split(b'\0') if p]


def snapshot(repo):
    repo = Path(repo).resolve()
    actual = Path(git(repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if repo != actual:
        raise ValueError('Pass the repository root, not a nested directory')
    head = git(repo, 'rev-parse', '--verify', 'HEAD').decode().strip()
    branch = git(repo, 'branch', '--show-current').decode().strip()
    status = git(repo, 'status', '--porcelain=v1', '-z', '--untracked-files=all')
    files = sorted(set(paths(git(repo, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'))))
    digest = hashlib.sha256()
    digest.update((head + '\0' + branch).encode())
    digest.update(status)
    digest.update(git(repo, 'ls-files', '--stage', '-z'))
    for name in files:
        file = repo / name
        if not file.parent.resolve().is_relative_to(repo):
            raise ValueError('Tracked path traverses a directory outside repository')
        digest.update(name.encode('utf-8', errors='surrogateescape') + b'\0')
        try:
            info = file.lstat()
            digest.update(str(stat.S_IMODE(info.st_mode)).encode())
            if file.is_symlink():
                digest.update(b'link:' + os.fsencode(os.readlink(file)))
            elif stat.S_ISREG(info.st_mode):
                with file.open('rb') as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(block)
            else:
                # Submodule directories are not recursively read.
                digest.update(b'non-regular')
        except FileNotFoundError:
            digest.update(b'deleted')
    rules = [p for p in files if Path(p).name in ('AGENTS.md', 'CLAUDE.md', 'CONTRIBUTING.md', 'CODEOWNERS')]
    return {'head_sha': head, 'branch': branch, 'dirty': bool(status),
            'fingerprint': digest.hexdigest(), 'rule_paths': rules,
            'fingerprint_scope': 'tracked and non-ignored untracked files; ignored files and submodule contents are excluded'}


def validate_task(task):
    required = ('objective', 'base_sha', 'allowed_paths', 'allowed_actions', 'validation', 'done_when')
    if not isinstance(task, dict) or any(not task.get(k) for k in required):
        raise ValueError('Task requires objective, base_sha, allowed_paths, allowed_actions, validation, done_when')
    if not isinstance(task['base_sha'], str) or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', task['base_sha']):
        raise ValueError('base_sha must be a full commit SHA')
    for key in ('allowed_paths', 'allowed_actions', 'validation', 'done_when'):
        if not isinstance(task[key], list):
            raise ValueError(key + ' must be an array')
    for pattern in task['allowed_paths']:
        if (not isinstance(pattern, str) or not pattern or pattern.startswith('/') or '\\' in pattern
                or ':' in pattern or '..' in PurePosixPath(pattern).parts):
            raise ValueError('allowed_paths must be repository-relative POSIX patterns')
    if not all(isinstance(a, str) and a in ('commit', 'push', 'create-pr', 'merge') for a in task['allowed_actions']):
        raise ValueError('Only commit, push, create-pr and merge actions are supported')
    if 'merge' in task['allowed_actions']:
        policy = task.get('merge')
        if (not isinstance(policy, dict)
                or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', str(policy.get('repository', '')))
                or not isinstance(policy.get('base_branch'), str) or not policy['base_branch'].strip()
                or not isinstance(policy.get('required_checks'), list) or not policy['required_checks']
                or any(not isinstance(c, str) or not c.strip() for c in policy['required_checks'])
                or len(set(policy['required_checks'])) != len(policy['required_checks'])):
            raise ValueError('Merge requires repository, base_branch and unique required_checks')
    checks = task['validation']
    if any(not isinstance(c, dict) or not isinstance(c.get('id'), str) or not c['id']
           or not isinstance(c.get('command'), str) or not c['command'] for c in checks):
        raise ValueError('Validation requires nonempty id and command strings')
    if len({c['id'] for c in checks}) != len(checks):
        raise ValueError('Validation ids must be unique')


def preflight(repo, task):
    validate_task(task)
    current = snapshot(repo)
    issues = []
    result = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', task['base_sha'], 'HEAD'],
                            capture_output=True, timeout=60)
    if result.returncode:
        issues.append('base-not-ancestor')
    if current['dirty']:
        issues.append('existing-changes-require-scope-reconciliation')
    if not current['branch']:
        issues.append('detached-head')
    return {'status': 'handoff' if issues else 'ready', 'issues': issues, 'snapshot': current,
            'note': 'Read-only preflight; validation commands have NOT been executed.'}


def accept(repo, task, evidence):
    validate_task(task)
    current = snapshot(repo)
    issues = []
    ancestor = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', task['base_sha'], 'HEAD'],
                             capture_output=True, timeout=60)
    if ancestor.returncode:
        return {'status': 'handoff', 'issues': ['base-not-ancestor'], 'snapshot': current}
    changed = set(paths(git(repo, 'diff', '--no-renames', '--name-only', '-z', task['base_sha'], 'HEAD')))
    changed.update(paths(git(repo, 'diff', '--cached', '--no-renames', '--name-only', '-z', 'HEAD')))
    changed.update(paths(git(repo, 'diff', '--no-renames', '--name-only', '-z')))
    changed.update(paths(git(repo, 'ls-files', '--others', '--exclude-standard', '-z')))
    for name in sorted(changed):
        if not any(fnmatch.fnmatchcase(name, pattern) for pattern in task['allowed_paths']):
            issues.append('out-of-scope:' + name)
    if not isinstance(evidence, dict) or evidence.get('fingerprint') != current['fingerprint']:
        issues.append('stale-evidence')
    checks = evidence.get('checks', []) if isinstance(evidence, dict) else []
    if not isinstance(checks, list):
        checks = []
        issues.append('invalid-evidence')
    for check in checks:
        if not isinstance(check, dict) or type(check.get('exit_code')) is not int or check['exit_code'] != 0:
            issues.append('validation-failed')
    for expected in task['validation']:
        matches = [c for c in checks if isinstance(c, dict) and c.get('id') == expected['id']]
        if len(matches) != 1 or matches[0].get('command') != expected['command'] or not matches[0].get('result'):
            issues.append('missing-or-ambiguous-check:' + expected['id'])
    if not current['branch']:
        issues.append('detached-head')
    return {'status': 'handoff' if issues else 'verified-local', 'issues': sorted(set(issues)),
            'changed_paths': sorted(changed), 'snapshot': current,
            'note': 'Evidence is caller-attested, not tamper-proof. No push/PR authorization is inferred.'}


class MediaParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.extend((value, False) for key, value in attrs if key == 'href' and value)
            return
        if tag not in ('img', 'source', 'video', 'audio', 'iframe', 'embed', 'image'):
            return
        for key, value in attrs:
            if value and key in ('src', 'poster', 'href', 'xlink:href'):
                self.links.append((value, True))
            elif value and key == 'srcset':
                self.links.extend((part.strip().split()[0], True) for part in value.split(',') if part.strip())


def visible_markdown(text):
    """Mask code/comments in context; this is a bounded Markdown scanner."""
    visible = list(text)
    def mask(begin, end):
        visible[begin:end] = ['\n' if char == '\n' else ' ' for char in text[begin:end]]
    index = 0
    while index < len(text):
        if text.startswith('<!--', index):
            end = text.find('-->', index + 4)
            end = len(text) if end == -1 else end + 3
            mask(index, end)
            index = end
            continue
        if index == 0 or text[index - 1] == '\n':
            opening = re.match(r' {0,3}(`{3,}|~{3,})([^\n]*)', text[index:])
            if opening and (opening[1][0] != '`' or '`' not in opening[2]):
                marker = re.escape(opening[1][0])
                closing = re.compile(r'^ {0,3}' + marker + '{' + str(len(opening[1]))
                                     + r',}[ \t]*\r?$', re.M).search(text, index + opening.end())
                end = len(text) if closing is None else closing.end()
                mask(index, end)
                index = end
                continue
        if text[index] == '\\':
            index += 2
            continue
        if text[index] == '<' and re.match(r'</?[A-Za-z][A-Za-z0-9-]*(?=[\s/>])', text[index:]):
            end, quote_char = index + 1, None
            while end < len(text):
                char = text[end]
                if quote_char:
                    if char == quote_char:
                        quote_char = None
                elif char in ('"', "'"):
                    quote_char = char
                elif char == '>':
                    break
                end += 1
            if end < len(text):
                index = end + 1
                continue
        if text[index] == '`':
            opening = re.match(r'`+', text[index:])[0]
            start = index + len(opening)
            # A blank line or fenced block ends the paragraph; inline spans cannot cross it.
            boundary = re.search(r'\n[ \t]*\n|\n {0,3}(?:`{3,}|~{3,})', text[start:])
            limit = len(text) if boundary is None else start + boundary.start()
            closing = re.compile(r'(?<!`)' + re.escape(opening) + r'(?!`)').search(text, start, limit)
            if closing:
                mask(index, closing.end())
                index = closing.end()
                continue
            index = start
            continue
        index += 1
    return ''.join(visible)


def markdown_references(text):
    """Read inline/reference links with nested image labels; not a full CommonMark parser."""
    def normalize_label(label):
        return re.sub(r'\s+', ' ', label).strip().casefold()

    definitions = {normalize_label(m[1]): m[2] for m in re.finditer(
        r'^\s{0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?', text, re.M)}
    links, stack, index = [], [], 0
    while index < len(text):
        char = text[index]
        if char == '\\':
            index += 2
            continue
        if char == '[':
            stack.append((index, index > 0 and text[index - 1] == '!'))
        elif char == ']' and stack:
            begin, media = stack.pop()
            label, after = text[begin + 1:index], index + 1
            if after < len(text) and text[after] == '(':
                depth, end = 1, after + 1
                while end < len(text) and depth:
                    if text[end] == '\\':
                        end += 2
                        continue
                    if text[end] == '(':
                        depth += 1
                    elif text[end] == ')':
                        depth -= 1
                    end += 1
                if depth == 0:
                    match = re.match(r'\s*(?:<([^>\n]+)>|([^\s]+))', text[after + 1:end - 1])
                    if match:
                        links.append((unescape(match[1] or match[2]), media))
                    index = end - 1
            elif after < len(text) and text[after] == '[':
                end = text.find(']', after + 1)
                if end != -1:
                    reference = normalize_label(text[after + 1:end] or label)
                    if reference in definitions:
                        links.append((unescape(definitions[reference]), media))
                    index = end
            elif (after == len(text) or text[after] != ':') and normalize_label(label) in definitions:
                links.append((unescape(definitions[normalize_label(label)]), media))
        index += 1
    return links


def audit_showcase(repo, readme='README.md', private=True):
    root = Path(repo).resolve()
    file = (root / readme).resolve()
    if not file.is_relative_to(root):
        raise ValueError('README must stay inside repository')
    if not file.is_file():
        return {'status': 'handoff', 'issues': ['missing-readme'], 'external_links': []}
    text = visible_markdown(file.read_text(encoding='utf-8'))
    issues = []
    if re.search(r'\bOWNER\b|\bREPO\b|\{\{[^}]+\}\}|\[TODO:', text):
        issues.append('placeholder')
    links = markdown_references(text)
    media_parser = MediaParser()
    media_parser.feed(text)
    links.extend(media_parser.links)
    external = []
    for target, media in dict.fromkeys(links):
        parsed = urlparse(target)
        safe_url = urlunparse(parsed._replace(netloc=parsed.netloc.rsplit('@', 1)[-1],
                                              query='[redacted]' if parsed.query else '',
                                              fragment='[redacted]' if parsed.fragment else ''))
        if parsed.username or parsed.password or re.search(r'[?&#](token|access_token|api_key|key|secret|password|auth|signature)=', unquote(target), re.I):
            issues.append('credential-in-url')
        if target.startswith('#'):
            continue
        if parsed.scheme in ('http', 'https') or target.startswith('//'):
            external.append({'url': safe_url, 'media': media, 'status': 'not-network-checked'})
            if private and media:
                issues.append('private-external-media:' + safe_url)
        elif not parsed.scheme and not target.startswith('#'):
            local = (file.parent / unquote(parsed.path)).resolve()
            if not local.is_relative_to(root):
                issues.append('outside-repository:' + safe_url)
            elif not local.exists():
                issues.append('missing-local:' + safe_url)
        elif parsed.scheme not in ('mailto',):
            issues.append('unsupported-link-scheme:' + parsed.scheme)
    return {'status': 'handoff' if issues else 'checked-offline', 'issues': sorted(set(issues)),
            'external_links': external, 'note': 'No network requests made; fragments and remote availability are not verified.'}


def render_showcase(text, repository, private=True, star_history=False):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', repository):
        raise ValueError('Expected owner/repository')
    if private and star_history:
        raise ValueError('Public Star History is disabled for private repositories')
    start, end = '<!-- repo-maintainer:showcase:start -->', '<!-- repo-maintainer:showcase:end -->'
    body = '\n'.join([start, '## 项目导航', '', '- [仓库说明](README.md)', '',
                       '版本、贡献与演示入口按仓库内现存资料配置；不以星标数代替质量评价。'])
    if star_history:
        encoded = quote(repository, safe='')
        body += ('\n\n### Star History\n\n'
                 f'![Star History](https://api.star-history.com/svg?repos={encoded}&type=Date)\n\n'
                 f'[文字入口：查看星标历史](https://www.star-history.com/#{repository}&Date)\n\n'
                 '图表来自第三方服务，反映其可用数据；不是下载量、质量或使用人数。')
    body += '\n' + end
    if text.count(start) != text.count(end) or text.count(start) > 1:
        raise ValueError('Unbalanced or duplicate showcase markers')
    if start in text:
        if text.index(start) > text.index(end):
            raise ValueError('Reversed showcase markers')
        begin, finish = text.index(start), text.index(end) + len(end)
        return text[:begin] + body + text[finish:]
    return text.rstrip() + '\n\n' + body + '\n'


def pr_status(reference):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*', reference):
        raise ValueError('PR must be owner/repository#number')
    repository, number = reference.split('#')
    response = subprocess.run(['gh', 'pr', 'view', number, '--repo', repository, '--json',
                               'url,state,isDraft,headRefOid,baseRefOid,headRefName,baseRefName,statusCheckRollup,mergeable,mergeStateStatus,reviewDecision'],
                              capture_output=True, timeout=60)
    if response.returncode:
        return {'status': 'handoff', 'issues': ['github-pr-unavailable'], 'note': 'No retry or remote mutation performed.'}
    return {'status': 'observed', 'pr': json.loads(response.stdout)}


def repository_policy(repository):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', repository):
        raise ValueError('Expected owner/repository')
    response = subprocess.run(['gh', 'api', '--hostname', 'github.com', 'repos/' + repository],
                              capture_output=True, timeout=60)
    if response.returncode:
        return {'status': 'handoff', 'issues': ['repository-policy-unavailable']}
    data = json.loads(response.stdout)
    return {'status': 'observed', 'repository': data.get('full_name'),
            'can_push': (data.get('permissions') or {}).get('push') is True,
            'squash_allowed': data.get('allow_squash_merge') is True}


def merge_readiness(repo, task, evidence, reference):
    """Observe readiness only. Caller must lock the returned SHA during actual merge."""
    local = accept(repo, task, evidence)
    if local['status'] != 'verified-local':
        return local
    issues, waiting = [], []
    if 'merge' not in task['allowed_actions']:
        return {'status': 'handoff', 'issues': ['merge-not-authorized']}
    policy = task['merge']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*', reference):
        raise ValueError('PR must be owner/repository#number')
    repository, number = reference.split('#')
    if repository.casefold() != policy['repository'].casefold():
        return {'status': 'handoff', 'issues': ['pr-repository-mismatch']}
    permissions = repository_policy(repository)
    if (permissions.get('status') != 'observed'
            or str(permissions.get('repository', '')).casefold() != repository.casefold()
            or not permissions.get('can_push') or not permissions.get('squash_allowed')):
        return {'status': 'handoff', 'issues': ['repository-permission-or-squash-unavailable']}
    observed = pr_status(reference)
    if observed.get('status') != 'observed':
        return {'status': 'handoff', 'issues': ['github-pr-unavailable']}
    pr = observed['pr']
    current = local['snapshot']
    if current['dirty']:
        issues.append('uncommitted-changes')
    if pr.get('headRefOid') != current['head_sha']:
        issues.append('pr-head-mismatch')
    if pr.get('headRefName') != current['branch']:
        issues.append('pr-branch-mismatch')
    if pr.get('baseRefName') != policy['base_branch']:
        issues.append('pr-base-mismatch')
    if pr.get('url', '').casefold() != f'https://github.com/{repository}/pull/{number}'.casefold():
        issues.append('pr-repository-mismatch')
    if pr.get('state') != 'OPEN':
        issues.append('pr-not-open')
    if pr.get('isDraft') is not False:
        issues.append('draft-pr')
    if pr.get('reviewDecision') in ('CHANGES_REQUESTED', 'REVIEW_REQUIRED'):
        issues.append('review-blocked')
    review = evidence.get('review', {})
    if (not isinstance(review, dict) or review.get('head_sha') != current['head_sha']
            or review.get('status') != 'approved' or type(review.get('blocking_findings')) is not int
            or review.get('blocking_findings') != 0 or not isinstance(review.get('reviewers'), list)
            or not review['reviewers'] or any(not isinstance(r, str) or not r.strip() for r in review['reviewers'])):
        issues.append('review-missing-or-stale')
    checks = pr.get('statusCheckRollup') or []
    names = {c.get('name', c.get('context', '')) for c in checks}
    for name in policy['required_checks']:
        if name not in names:
            issues.append('missing-ci:' + name)
    for check in checks:
        name = check.get('name', check.get('context', 'unknown'))
        state = check.get('state') if check.get('__typename') == 'StatusContext' else check.get('status')
        if state in ('PENDING', 'QUEUED', 'IN_PROGRESS', 'WAITING', 'REQUESTED', 'PENDING_APPROVAL'):
            waiting.append('ci-pending:' + name)
        elif (check.get('state') if check.get('__typename') == 'StatusContext' else check.get('conclusion')) != 'SUCCESS':
            issues.append('ci-not-success:' + name)
    if pr.get('mergeable') == 'UNKNOWN':
        waiting.append('mergeability-pending')
    elif pr.get('mergeable') != 'MERGEABLE':
        issues.append('pr-not-mergeable')
    if not waiting and pr.get('mergeStateStatus') != 'CLEAN':
        issues.append('merge-state-not-clean')
    return {'status': 'handoff' if issues else ('waiting' if waiting else 'ready-to-merge'),
            'issues': sorted(set(issues)), 'pending': sorted(set(waiting)),
            'head_sha': current['head_sha'], 'pr_url': pr.get('url'),
            'note': 'Read-only observation. Evidence is caller-attested. Merge separately with --match-head-commit; do not bypass platform rules.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['snapshot', 'preflight', 'accept', 'showcase', 'preview', 'pr', 'merge-readiness'])
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--task', type=Path)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--readme', default='README.md')
    parser.add_argument('--repository')
    parser.add_argument('--public', action='store_true', help='Explicitly declare repository public')
    parser.add_argument('--star-history', action='store_true')
    parser.add_argument('--pr')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    args = parser.parse_args()
    try:
        if args.operation == 'snapshot':
            result = snapshot(args.repo)
        elif args.operation in ('preflight', 'accept', 'merge-readiness'):
            if not args.task or (args.operation in ('accept', 'merge-readiness') and not args.evidence):
                raise ValueError('Task and, for accept, evidence file are required')
            task = json.loads(args.task.read_text(encoding='utf-8'))
            if args.operation == 'preflight':
                result = preflight(args.repo, task)
            else:
                evidence = json.loads(args.evidence.read_text(encoding='utf-8'))
                result = accept(args.repo, task, evidence) if args.operation == 'accept' else merge_readiness(
                    args.repo, task, evidence, args.pr or '')
        elif args.operation == 'showcase':
            result = audit_showcase(args.repo, args.readme, private=not args.public)
        elif args.operation == 'preview':
            readme = (args.repo / args.readme).resolve()
            if not readme.is_relative_to(args.repo.resolve()):
                raise ValueError('README must stay inside repository')
            print(render_showcase(readme.read_text(encoding='utf-8'), args.repository or '',
                                 private=not args.public, star_history=args.star_history))
            return 0
        else:
            result = pr_status(args.pr or '')
        if args.format == 'markdown':
            print('## repo-maintainer\n\n```json\n' + json.dumps(result, ensure_ascii=False, indent=2) + '\n```')
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get('status') == 'handoff' else (3 if result.get('status') == 'waiting' else 0)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        # Do not echo subprocess stdout/stderr, command arguments or file content.
        print(json.dumps({'status': 'handoff', 'issues': [type(error).__name__],
                          'note': 'Invalid input, repository state or unavailable dependency; inspect locally.'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

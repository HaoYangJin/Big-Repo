"""Project onboarding and task/feedback delivery. No scheduler or model credentials."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid
from urllib.parse import urlsplit

SPEC = importlib.util.spec_from_file_location('workflow_repo_tools', Path(__file__).with_name('repo_tools.py'))
TOOLS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOLS)
CONFIG = '.repo-maintainer/config.json'
START = '<!-- repo-maintainer:workflow:start -->'
END = '<!-- repo-maintainer:workflow:end -->'
LEVELS = {'commit': 0, 'pr': 1, 'merge': 2}
RUNTIME_ROOTS = {'.codex-plugin', '.claude-plugin', 'skills', 'scripts', 'references', 'templates', 'assets',
                 'README.md', 'CHANGELOG.md', 'LICENSE', 'NOTICE'}


class WorkflowError(ValueError):
    pass


def command(argv, repo=None):
    result = subprocess.run(argv, cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
    if result.returncode:
        raise WorkflowError('command-failed:' + Path(argv[0]).name)
    return result.stdout


def root(path):
    path = Path(path).resolve()
    actual = Path(command(['git', 'rev-parse', '--show-toplevel'], path).strip()).resolve()
    if actual != path:
        raise WorkflowError('pass-repository-root')
    return path


def safe_path(repo, relative):
    repo = Path(repo).resolve()
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise WorkflowError('expected-repository-relative-path')
    target = repo / path
    for part in (target, *target.parents):
        if part == repo:
            break
        if part.is_symlink() or not part.resolve().is_relative_to(repo):
            raise WorkflowError('linked-project-path')
    return target


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix='.workflow-', delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def identity(repo):
    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=repo,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if result.returncode:
        return None
    value = result.stdout.strip()
    if '://' in value:
        parsed = urlsplit(value)
        host, name = parsed.hostname, parsed.path.strip('/')
    else:
        match = re.fullmatch(r'(?:[^@/]+@)?([^:/]+):(.+)', value)
        if not match:
            return None
        host, name = match.groups()
    name = name.removesuffix('.git')
    if host != 'github.com' or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name):
        return None
    return name


def infer_checks(repo):
    package = repo / 'package.json'
    if package.is_file():
        data = json.loads(package.read_text(encoding='utf-8'))
        manager = str(data.get('packageManager', '')).split('@')[0]
        if manager not in ('npm', 'pnpm', 'yarn'):
            manager = 'pnpm' if (repo / 'pnpm-lock.yaml').exists() else ('yarn' if (repo / 'yarn.lock').exists() else 'npm')
        return [{'id': name, 'argv': [manager, 'run', name]} for name in ('lint', 'typecheck', 'test')
                if isinstance(data.get('scripts', {}).get(name), str)
                and 'no test specified' not in data['scripts'][name]]
    tests = repo / 'tests'
    # Infer unittest only with direct evidence; the agent supplies other runners.
    if tests.is_dir() and any('unittest.TestCase' in p.read_text(encoding='utf-8')
                              for p in tests.glob('test*.py') if p.is_file()):
        return [{'id': 'tests', 'argv': ['python', '-m', 'unittest', 'discover', '-s', 'tests']}]
    return []


def validate_config(data):
    if (data.get('schema_version') != 1 or data.get('trigger') != 'task-or-feedback'
            or data.get('delivery') not in LEVELS or data.get('ci_policy') not in ('required', 'none')
            or data.get('release') != 'explicit-request'):
        raise WorkflowError('invalid-project-policy')
    if not isinstance(data.get('base_branch'), str) or not data['base_branch'].strip():
        raise WorkflowError('missing-base-branch')
    if (not isinstance(data.get('plugin_path'), str) or not data['plugin_path']
            or not isinstance(data.get('clients'), list) or not data['clients']
            or any(c not in ('codex', 'claude') for c in data['clients'])
            or (data.get('repository') is not None and not re.fullmatch(
                r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', str(data['repository'])))):
        raise WorkflowError('invalid-project-identity-or-client')
    checks = data.get('validation')
    if not isinstance(checks, list):
        raise WorkflowError('invalid-validation-list')
    names = []
    for check in checks:
        if (not isinstance(check, dict) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', str(check.get('id', '')))
                or not isinstance(check.get('argv'), list) or not check['argv']
                or any(not isinstance(a, str) or not a or '\0' in a for a in check['argv'])):
            raise WorkflowError('invalid-validation-command')
        names.append(check['id'])
    ci = data.get('required_checks')
    if (len(names) != len(set(names)) or not isinstance(ci, list)
            or any(not isinstance(c, str) or not c.strip() for c in ci) or len(ci) != len(set(ci))
            or (data['ci_policy'] == 'none' and ci)):
        raise WorkflowError('invalid-check-policy')


def configuration(repo):
    data = json.loads(safe_path(repo, CONFIG).read_text(encoding='utf-8'))
    validate_config(data)
    return data


def config_digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def instruction_block(plugin):
    script = plugin + '/scripts/project_workflow.py'
    return f'''{START}
## 开发任务与反馈的自动交付

本项目已接入 repo-maintainer。收到开发需求、缺陷反馈或本轮测试/CI/审查反馈时，读取 `{CONFIG}` 和 `{plugin}/skills/maintenance-delivery/SKILL.md`，复用项目配置完成本轮维护和交付，用户无需再说“提交、上传、创建 PR”。普通问答、只读审查和用户明确的更窄限制按其原范围执行。

由当前 AI 客户端执行：理解任务及项目规则 → 运行 `python {script} begin --repo . --objective "实际需求" --allowed-path "实际改动范围"`（已有任务先 status）→ 开发并同步相关说明 → 按项目约定精确提交 → check → 独立 AI 审查并用 review 登记真实结论 → deliver。begin 会复用事件/任务记录，deliver 会核对远端状态，等待 CI 或处理失败后继续同一任务，不能把推送或创建 PR 当作已合并。

命令详情与故障恢复见 `{plugin}/references/project-workflow.md`。保留用户已有工作；任务/日志保存在 Git 元数据内，不提交、不伪造验证或独立审查。配置不取代用户授权、项目规则与客户端权限；不读取或保存凭据值，不设置定时任务。版本发布遵循 explicit-request 策略，只有用户明确指定版本才执行。
{END}
'''


def runtime_files(directory):
    files = {}
    for path in directory.rglob('*'):
        relative = path.relative_to(directory)
        if (relative.parts[0] not in RUNTIME_ROOTS
                or any(p in ('__pycache__', '.git', '.venv') for p in relative.parts)
                or path.name.startswith('.env') or path.suffix in ('.pyc', '.pem', '.key')):
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(directory):
            raise WorkflowError('linked-plugin-resource')
        if path.is_file():
            files[relative] = path
    return files


def initialize(repo, client=None, delivery=None, checks=None, ci=None, no_ci=False,
               base=None, plugin_path=None, update=False):
    repo = root(repo)
    config_file = safe_path(repo, CONFIG)
    previous = configuration(repo) if config_file.exists() else None
    if previous and not update:
        missing = readiness(previous)
        return {'status': 'needs-configuration' if missing else 'configured', 'missing': missing,
                'config': previous, 'note': 'Existing project settings preserved; use init --update for an intentional policy change.'}
    clients = (['codex', 'claude'] if client == 'both' else [client]) if client else (previous['clients'] if previous else ['codex', 'claude'])
    files = [safe_path(repo, 'AGENTS.md' if c == 'codex' else 'CLAUDE.md') for c in clients]
    texts = {}
    for file in files:
        text = file.read_bytes().decode('utf-8') if file.exists() else ''
        if text.count(START) != text.count(END) or text.count(START) > 1 or (START in text and text.index(END) < text.index(START)):
            raise WorkflowError('malformed-managed-instructions')
        texts[file] = text
    plugin = plugin_path or (previous['plugin_path'] if previous else '.repo-maintainer/plugin')
    target = safe_path(repo, plugin)
    source = Path(__file__).resolve().parents[1]
    if plugin_path and target.resolve() != source:
        raise WorkflowError('plugin-path-must-be-this-plugin-in-project')
    if not previous and not plugin_path and target.exists():
        # An interrupted copy may be reused only when it matches this runtime.
        existing = runtime_files(target)
        expected = runtime_files(source)
        if (set(existing) != set(expected)
                or any(existing[name].read_bytes() != file.read_bytes() for name, file in expected.items())):
            raise WorkflowError('existing-runtime-needs-reconciliation-not-overwrite')
    if not plugin_path and not target.exists():
        # Vendor the complete portable runtime; never copy caches, links or credentials.
        candidates = runtime_files(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
            staged = Path(temporary) / 'plugin'
            staged.mkdir()
            for relative, path in candidates.items():
                destination = staged / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
            staged.replace(target)
    if not (target / 'scripts/project_workflow.py').is_file():
        raise WorkflowError('project-runtime-missing')
    branch = command(['git', 'symbolic-ref', '--quiet', '--short', 'refs/remotes/origin/HEAD'], repo).strip() if subprocess.run(
        ['git', 'symbolic-ref', '--quiet', 'refs/remotes/origin/HEAD'], cwd=repo, capture_output=True).returncode == 0 else None
    current = command(['git', 'branch', '--show-current'], repo).strip()
    data = {'schema_version': 1, 'trigger': 'task-or-feedback', 'plugin_path': plugin,
            'repository': identity(repo), 'base_branch': base or (previous['base_branch'] if previous else (branch.removeprefix('origin/') if branch else current or 'main')),
            'delivery': delivery or (previous['delivery'] if previous else 'merge'),
            'release': 'explicit-request', 'clients': sorted(set(clients + (previous['clients'] if previous else []))),
            'validation': ([{'id': f'check-{i + 1}', 'argv': shlex.split(c)} for i, c in enumerate(checks)]
                           if checks is not None else (previous['validation'] if previous else infer_checks(repo))),
            'ci_policy': 'none' if no_ci else (previous['ci_policy'] if previous and ci is None else 'required'),
            'required_checks': [] if no_ci else (ci if ci is not None else (previous['required_checks'] if previous else []))}
    validate_config(data)
    block = instruction_block(plugin)
    for file, text in texts.items():
        result = (text[:text.index(START)] + block.rstrip('\n') + text[text.index(END) + len(END):]
                  if START in text else text + ('\n\n' if text and not text.endswith('\n\n') else '') + block)
        if result != text:
            file.write_bytes(result.encode('utf-8'))
    write_json(config_file, data)
    missing = readiness(data)
    return {'status': 'needs-configuration' if missing else 'configured', 'missing': missing, 'config': data}


def readiness(config):
    missing = []
    if not config['validation']:
        missing.append('project-validation-commands')
    if config['delivery'] != 'commit' and not config.get('repository'):
        missing.append('github-origin')
    if config['delivery'] == 'merge' and config['ci_policy'] == 'required' and not config['required_checks']:
        missing.append('actual-ci-check-names-or-confirmed-no-ci-policy')
    return missing


def state_dir(repo):
    directory = Path(command(['git', 'rev-parse', '--absolute-git-dir'], repo).strip()) / 'repo-maintainer'
    directory.mkdir(parents=True, exist_ok=True)
    return directory


@contextmanager
def locked(directory):
    # Kernel locks release on process exit, including crashes; no stale PID locks.
    with (directory / 'workflow.lock').open('a+b') as stream:
        # Windows byte locks also prohibit reads of an already locked byte.
        # Inspect metadata before acquiring the lock instead of reading it.
        if os.fstat(stream.fileno()).st_size == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise WorkflowError('another-task-operation-is-running') from error
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def active(directory):
    pointer = json.loads((directory / 'active.json').read_text(encoding="utf-8"))
    identifier = pointer.get('id', '')
    if not re.fullmatch(r'[0-9a-f]{64}', identifier):
        raise WorkflowError('invalid-task-state')
    path = directory / 'tasks' / identifier
    return path, json.loads((path / 'state.json').read_text(encoding="utf-8"))


def save(path, state, status, **details):
    if status != 'blocked':
        state.pop('reason', None)
    state.update(status=status, **details)
    state.setdefault('history', []).append({'status': status, **details})
    write_json(path / 'state.json', state)


def begin(repo, objective, allowed_paths, event=None, delivery=None):
    repo = root(repo)
    config = configuration(repo)
    if readiness(config):
        return {'status': 'needs-configuration', 'missing': readiness(config)}
    chosen = delivery or config['delivery']
    if LEVELS[chosen] > LEVELS[config['delivery']]:
        raise WorkflowError('task-cannot-expand-project-delivery-policy')
    if chosen != 'commit' and (identity(repo) or '').casefold() != config['repository'].casefold():
        raise WorkflowError('origin-repository-changed')
    directory = state_dir(repo)
    with locked(directory):
        identifier = hashlib.sha256((event or str(uuid.uuid4())).encode()).hexdigest()
        path = directory / 'tasks' / identifier
        if path.exists():
            state = json.loads((path / 'state.json').read_text(encoding="utf-8"))
            if state['objective'] != objective or state['config_digest'] != config_digest(config):
                raise WorkflowError('event-already-bound-to-different-task')
            if state['delivery'] != chosen:
                raise WorkflowError('delivery-changed-cancel-and-replan-task')
            if set(json.loads((path / 'task.json').read_text(encoding='utf-8'))['allowed_paths']) != set(allowed_paths):
                raise WorkflowError('scope-changed-cancel-and-replan-task')
            return {'status': state['status'], 'task_id': identifier, 'state_directory': str(path), 'resumed': True}
        if (directory / 'active.json').exists():
            previous_path, previous = active(directory)
            if previous['status'] not in ('completed', 'cancelled'):
                if previous['objective'] == objective and previous['config_digest'] == config_digest(config):
                    if previous['delivery'] != chosen:
                        raise WorkflowError('delivery-changed-cancel-and-replan-task')
                    if set(json.loads((previous_path / 'task.json').read_text(encoding='utf-8'))['allowed_paths']) != set(allowed_paths):
                        raise WorkflowError('scope-changed-cancel-and-replan-task')
                    return {'status': previous['status'], 'task_id': previous['id'], 'state_directory': str(previous_path), 'resumed': True}
                raise WorkflowError('unfinished-task-resume-before-starting-another')
        current = TOOLS.snapshot(repo)
        baseline = current['head_sha']
        if chosen != 'commit':
            baseline = None
            for ref in ('refs/remotes/origin/' + config['base_branch'], 'refs/heads/' + config['base_branch']):
                try:
                    baseline = command(['git', 'rev-parse', '--verify', ref + '^{commit}'], repo).strip()
                    break
                except WorkflowError:
                    continue
            if baseline is None:
                raise WorkflowError('base-branch-reference-unavailable-fetch-and-reconcile')
            command(['git', 'merge-base', '--is-ancestor', baseline, current['head_sha']], repo)
        task = {'objective': objective, 'base_sha': baseline, 'allowed_paths': allowed_paths,
                'allowed_actions': ['commit'] + (['push', 'create-pr'] if chosen != 'commit' else []) + (['merge'] if chosen == 'merge' else []),
                'validation': [{'id': c['id'], 'command': shlex.join(c['argv'])} for c in config['validation']],
                'done_when': ['Current task verified, independently reviewed and delivered using project policy']}
        if chosen == 'merge':
            task['merge'] = {'repository': config['repository'], 'base_branch': config['base_branch'],
                             'required_checks': config['required_checks'], 'ci_policy': config['ci_policy']}
        TOOLS.validate_task(task)
        if not current['branch']:
            raise WorkflowError('detached-head-needs-task-branch')
        if current['branch'] == config['base_branch'] and chosen != 'commit':
            command(['git', 'switch', '-c', 'maintain/' + identifier[:12]], repo)
        path.mkdir(parents=True)
        state = {'id': identifier, 'objective': objective, 'config_digest': config_digest(config),
                 'delivery': chosen, 'initial_snapshot': current, 'attempts': 0}
        write_json(path / 'task.json', task)
        save(path, state, 'working')
        write_json(directory / 'active.json', {'id': identifier})
        return {'status': 'working', 'task_id': identifier, 'state_directory': str(path),
                'initial_changes_require_reconciliation': current['dirty'] or baseline != current['head_sha']}


def current_task(repo):
    directory = state_dir(repo)
    path, state = active(directory)
    config = configuration(repo)
    if config_digest(config) != state['config_digest']:
        raise WorkflowError('project-policy-changed-reconcile-active-task')
    return path, state, config, json.loads((path / 'task.json').read_text(encoding="utf-8"))


def check(repo, retry_reason=None):
    repo = root(repo)
    with locked(state_dir(repo)):
        path, state, config, task = current_task(repo)
        if state['status'] in ('completed', 'cancelled'):
            return {'status': state['status'], 'note': 'Start a new task for new work.'}
        before = TOOLS.snapshot(repo)
        if state.get('failed_fingerprint') == before['fingerprint'] and not retry_reason:
            raise WorkflowError('unchanged-failed-candidate-needs-diagnosis-before-retry')
        attempt = state['attempts'] + 1
        logs = path / 'runs' / str(attempt)
        logs.mkdir(parents=True)
        checks = []
        for item, expected in zip(config['validation'], task['validation']):
            try:
                result = subprocess.run(item['argv'], cwd=repo, capture_output=True, timeout=300)
                code, output = result.returncode, result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                code, output = 124, b'Validation timed out; diagnose before retrying.\n'
            except OSError:
                code, output = 127, b'Validation executable unavailable.\n'
            log = logs / (item['id'] + '.log')
            log.write_bytes(output)
            checks.append({**expected, 'exit_code': code, 'result': str(log)})
        after = TOOLS.snapshot(repo)
        evidence = {'fingerprint': before['fingerprint'], 'checks': checks}
        write_json(logs / 'evidence.json', evidence)
        write_json(path / 'evidence.json', evidence)
        accepted = TOOLS.accept(repo, task, evidence)
        passed = accepted['status'] == 'verified-local' and before['fingerprint'] == after['fingerprint']
        save(path, state, 'validated' if passed else 'blocked', attempts=attempt,
             failed_fingerprint=None if passed else before['fingerprint'],
             head_sha=before['head_sha'], issues=accepted.get('issues', []), retry_reason=retry_reason)
        return {'status': state['status'], 'checks': checks, 'issues': state['issues'], 'state_directory': str(path)}


def review(repo, head, reviewers, blocking=0):
    repo = root(repo)
    with locked(state_dir(repo)):
        path, state, _, task = current_task(repo)
        if state['status'] in ('completed', 'cancelled'):
            raise WorkflowError('closed-task-does-not-accept-new-review')
        evidence = json.loads((path / 'evidence.json').read_text(encoding="utf-8"))
        current = TOOLS.snapshot(repo)
        if (head != current['head_sha'] or current['dirty'] or not reviewers
                or any(not r.strip() for r in reviewers) or blocking < 0
                or TOOLS.accept(repo, task, evidence)['status'] != 'verified-local'):
            raise WorkflowError('review-needs-clean-validated-final-head')
        evidence['review'] = {'head_sha': head, 'status': 'approved' if blocking == 0 else 'changes-requested',
                              'reviewers': reviewers, 'blocking_findings': blocking}
        write_json(path / 'evidence.json', evidence)
        save(path, state, 'reviewed' if blocking == 0 else 'blocked')
        return {'status': state['status'], 'review': evidence['review']}


def pr_list(config, branch):
    output = command(['gh', 'pr', 'list', '--repo', config['repository'], '--head', branch,
                      '--base', config['base_branch'], '--state', 'all', '--json', 'number,state,headRefOid'])
    return json.loads(output)


def observed_pr(config, number):
    reference = f'{config["repository"]}#{number}'
    observed = TOOLS.pr_status(reference)
    if observed.get('status') != 'observed':
        raise WorkflowError('github-pr-unavailable')
    return reference, observed['pr']


def deliver(repo, title=None, body_file=None, retry_reason=None):
    repo = root(repo)
    with locked(state_dir(repo)):
        path, state, config, task = current_task(repo)
        if state['status'] in ('completed', 'cancelled'):
            return {'status': state['status'], 'result': state.get('result'), 'note': 'Event is closed; no write performed.'}
        evidence = json.loads((path / 'evidence.json').read_text(encoding="utf-8"))
        if state.get('pr_number'):
            _, observed = observed_pr(config, state['pr_number'])
            if (observed.get('state') == 'MERGED' and observed.get('headRefOid') == state.get('delivery_head')
                    and evidence.get('review', {}).get('head_sha') == state.get('delivery_head')
                    and evidence.get('review', {}).get('status') == 'approved'
                    and observed.get('headRefName') == state.get('delivery_branch')
                    and observed.get('baseRefName') == config['base_branch']
                    and observed.get('url', '').casefold() == f'https://github.com/{config["repository"]}/pull/{state["pr_number"]}'.casefold()
                    and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', str((observed.get('mergeCommit') or {}).get('oid', '')))):
                result = {'status': 'merged', 'pr_url': observed['url'], 'merge_commit': observed['mergeCommit']['oid']}
                save(path, state, 'completed', result=result)
                return {'status': 'completed', 'result': result}
            if observed.get('state') == 'CLOSED':
                raise WorkflowError('pr-closed-reconcile-feedback-before-delivery')
            if ('merge-outcome-unconfirmed' in state.get('result', {}).get('issues', [])
                    or 'merge-command-failed' in state.get('result', {}).get('issues', [])) and not retry_reason:
                raise WorkflowError('query-merge-outcome-and-diagnose-before-retry')
        current = TOOLS.snapshot(repo)
        accepted = TOOLS.accept(repo, task, evidence)
        reviewed = evidence.get('review', {})
        if (accepted['status'] != 'verified-local' or current['dirty']
                or reviewed.get('head_sha') != current['head_sha'] or reviewed.get('status') != 'approved'
                or reviewed.get('blocking_findings') != 0 or not reviewed.get('reviewers')):
            raise WorkflowError('delivery-needs-current-validation-and-independent-review')
        if current['head_sha'] == task['base_sha']:
            result = {'status': 'no-changes', 'head_sha': current['head_sha']}
            save(path, state, 'completed', result=result)
            return {'status': 'completed', 'result': result}
        if state['delivery'] == 'commit':
            result = {'status': 'committed', 'head_sha': current['head_sha']}
            save(path, state, 'completed', result=result)
            return {'status': 'completed', 'result': result}
        if (identity(repo) or '').casefold() != config['repository'].casefold() or current['branch'] == config['base_branch']:
            raise WorkflowError('delivery-needs-task-branch-and-matching-origin')
        state['delivery_head'] = current['head_sha']
        state['delivery_branch'] = current['branch']
        remote = command(['git', 'ls-remote', 'origin', 'refs/heads/' + current['branch']], repo).split()
        if not remote or remote[0] != current['head_sha']:
            save(path, state, 'pushing')
            try:
                command(['git', 'push', 'origin', 'HEAD:refs/heads/' + current['branch']], repo)
            except WorkflowError:
                remote = command(['git', 'ls-remote', 'origin', 'refs/heads/' + current['branch']], repo).split()
                if not remote or remote[0] != current['head_sha']:
                    save(path, state, 'blocked', issues=['push-not-confirmed'])
                    return {'status': 'blocked', 'issues': state['issues']}
        prs = pr_list(config, current['branch'])
        opened = [p for p in prs if p['state'] == 'OPEN']
        merged = [p for p in prs if p['state'] == 'MERGED' and p['headRefOid'] == current['head_sha']]
        if len(opened) > 1:
            raise WorkflowError('ambiguous-open-pr')
        if not opened and merged:
            number = merged[0]['number']
        elif opened:
            number = opened[0]['number']
        else:
            if state.get('creation_unconfirmed') and not retry_reason:
                raise WorkflowError('query-pr-outcome-before-retrying-creation')
            if not title or not body_file:
                raise WorkflowError('new-pr-needs-agent-written-title-and-body-file')
            save(path, state, 'creating-pr', creation_unconfirmed=True)
            try:
                command(['gh', 'pr', 'create', '--repo', config['repository'], '--base', config['base_branch'],
                         '--head', current['branch'], '--title', title, '--body-file', str(Path(body_file).resolve())])
            except WorkflowError:
                pass
            opened = [p for p in pr_list(config, current['branch']) if p['state'] == 'OPEN']
            if len(opened) != 1:
                save(path, state, 'blocked', issues=['pr-creation-unconfirmed'])
                return {'status': 'blocked', 'issues': state['issues']}
            number = opened[0]['number']
        reference, pr = observed_pr(config, number)
        if (pr.get('headRefOid') != current['head_sha'] or pr.get('headRefName') != current['branch']
                or pr.get('baseRefName') != config['base_branch']
                or pr.get('url', '').casefold() != f'https://github.com/{config["repository"]}/pull/{number}'.casefold()):
            raise WorkflowError('pr-identity-or-head-mismatch')
        save(path, state, 'observed-pr', pr_number=number, creation_unconfirmed=False)
        if state['delivery'] == 'pr' and pr.get('state') == 'OPEN':
            result = {'status': 'pr-delivered', 'pr_url': pr['url'], 'head_sha': current['head_sha']}
            save(path, state, 'completed', result=result)
            return {'status': 'completed', 'result': result}
        if pr.get('state') == 'MERGED' and (pr.get('mergeCommit') or {}).get('oid'):
            result = {'status': 'merged', 'pr_url': pr['url'], 'merge_commit': pr['mergeCommit']['oid']}
        else:
            result = TOOLS.merge_pr(repo, task, evidence, reference)
        status = 'completed' if result['status'] == 'merged' else ('waiting' if result['status'] == 'waiting' else 'blocked')
        save(path, state, status, result=result)
        return {'status': status, 'result': result}


def status(repo):
    repo = root(repo)
    config = configuration(repo)
    directory = state_dir(repo)
    if not (directory / 'active.json').exists():
        missing = readiness(config)
        return {'status': 'needs-configuration' if missing else 'configured', 'missing': missing, 'policy': config}
    path, state = active(directory)
    return {'status': state['status'], 'task_id': state['id'], 'objective': state['objective'],
            'state_directory': str(path), 'attempts': state['attempts'], 'result': state.get('result'),
            'policy_changed': state['config_digest'] != config_digest(config)}


def cancel(repo, reason):
    repo = root(repo)
    with locked(state_dir(repo)):
        path, state = active(state_dir(repo))
        if state['status'] == 'completed':
            raise WorkflowError('completed-task-cannot-be-cancelled')
        save(path, state, 'cancelled', cancellation_reason=reason)
        return {'status': 'cancelled', 'state_directory': str(path),
                'note': 'Task records, user work, branches and existing PRs preserved.'}


def block(repo, reason):
    repo = root(repo)
    with locked(state_dir(repo)):
        path, state, _, _ = current_task(repo)
        if state['status'] in ('completed', 'cancelled'):
            raise WorkflowError('task-already-closed')
        save(path, state, 'blocked', reason=reason)
        return {'status': 'blocked', 'state_directory': str(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['init', 'begin', 'check', 'review', 'deliver', 'status', 'block', 'cancel'])
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--client', choices=['codex', 'claude', 'both'])
    parser.add_argument('--delivery', choices=list(LEVELS))
    parser.add_argument('--check', action='append')
    parser.add_argument('--ci-check', action='append')
    parser.add_argument('--no-ci', action='store_true')
    parser.add_argument('--base-branch')
    parser.add_argument('--plugin-path')
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--objective')
    parser.add_argument('--allowed-path', action='append')
    parser.add_argument('--event-id')
    parser.add_argument('--head')
    parser.add_argument('--reviewer', action='append')
    parser.add_argument('--blocking-findings', type=int, default=0)
    parser.add_argument('--title')
    parser.add_argument('--body-file', type=Path)
    parser.add_argument('--retry-reason')
    parser.add_argument('--reason')
    try:
        args = parser.parse_args()
        if args.operation == 'init':
            result = initialize(args.repo, args.client, args.delivery, args.check, args.ci_check,
                                args.no_ci, args.base_branch, args.plugin_path, args.update)
        elif args.operation == 'begin':
            if not args.objective or not args.allowed_path:
                raise WorkflowError('begin-needs-objective-and-actual-allowed-paths')
            result = begin(args.repo, args.objective, args.allowed_path, args.event_id, args.delivery)
        elif args.operation == 'check':
            result = check(args.repo, args.retry_reason)
        elif args.operation == 'review':
            if not args.head or not args.reviewer:
                raise WorkflowError('review-needs-final-head-and-real-reviewer')
            result = review(args.repo, args.head, args.reviewer, args.blocking_findings)
        elif args.operation == 'deliver':
            result = deliver(args.repo, args.title, args.body_file, args.retry_reason)
        elif args.operation == 'status':
            result = status(args.repo)
        elif args.operation == 'cancel':
            if not args.reason:
                raise WorkflowError('cancellation-needs-user-directed-reason')
            result = cancel(args.repo, args.reason)
        else:
            if not args.reason:
                raise WorkflowError('block-needs-concrete-reason')
            result = block(args.repo, args.reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 3 if result['status'] == 'waiting' else (2 if result['status'] in ('blocked', 'needs-configuration') else 0)
    except WorkflowError as error:
        print(json.dumps({'status': 'blocked', 'issues': [str(error)]}))
        return 2
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        print(json.dumps({'status': 'blocked', 'note': 'Read project policy and task state; reconcile the failed prerequisite before retrying. No credentials or raw CLI errors printed.'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

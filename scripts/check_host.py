"""Real CLI loading and installed-tool checks. Never invokes a model or requests credentials."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

try:
    from .verify_plugin import SKILLS, verify
except ImportError:
    from verify_plugin import SKILLS, verify

PLUGIN_ID = 'repo-maintainer@repo-standards-ci'
VERSIONS = {'codex': '0.163.0', 'claude-code': '2.1.302'}


def run(command, cwd, env=None, expected=0):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=60)
    if result.returncode != expected:
        raise RuntimeError('cli-command-exit-' + str(result.returncode))
    return result.stdout


def inventory_from_codex(skills, plugin_root):
    selected = [s for s in skills if s.get('pluginId') == PLUGIN_ID]
    names = sorted(s['name'] for s in selected)
    if names != ['repo-maintainer:' + name for name in SKILLS]:
        raise ValueError('Codex skill inventory mismatch')
    for skill in selected:
        file = Path(skill['path']).resolve()
        if not skill.get('enabled') or not file.is_file() or not file.is_relative_to(plugin_root.resolve()):
            raise ValueError('Codex skill not enabled or loaded outside installation')
    return SKILLS.copy()


def inventory_from_claude(text, version):
    match = re.search(r'^\s*Skills \((\d+)\)\s+(.+)$', text, re.M)
    if (not re.search(r'^repo-maintainer ' + re.escape(version) + r'\s*$', text, re.M)
            or 'Source: repo-maintainer@inline' not in text or not match
            or int(match[1]) != len(SKILLS) or sorted(s.strip() for s in match[2].split(',')) != SKILLS):
        raise ValueError('Claude skill inventory mismatch')
    return SKILLS.copy()


def codex_skills(cli, env, cwd, plugin_root):
    messages = queue.Queue()
    process = subprocess.Popen([cli, '--no-daemon', 'app-server', '--stdio'], cwd=cwd, env=env,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               text=True, encoding='utf-8')
    def read():
        try:
            for line in process.stdout:
                messages.put(json.loads(line))
        except (ValueError, OSError):
            messages.put({'error': 'invalid-server-stream'})
    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    def send(item):
        process.stdin.write(json.dumps(item) + '\n')
        process.stdin.flush()
    def response(identifier):
        deadline = time.monotonic() + 35
        while True:
            item = messages.get(timeout=max(0.1, deadline - time.monotonic()))
            if 'error' in item:
                raise RuntimeError('app-server-error')
            if item.get('id') == identifier:
                return item['result']
            if time.monotonic() >= deadline:
                raise RuntimeError('app-server-timeout')
    try:
        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'repo_maintainer_ci', 'version': '1.1.0'}}})
        response(1)
        send({'method': 'initialized', 'params': {}})
        send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(cwd)], 'forceReload': True}})
        result = response(2)['data']
        if len(result) != 1 or result[0]['errors']:
            raise ValueError('Codex skill load errors')
        return inventory_from_codex(result[0]['skills'], plugin_root)
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        reader.join(timeout=2)
        process.stdin.close()
        process.stdout.close()


def exercise_tools(plugin, fixture):
    fixture.mkdir(parents=True)
    (fixture / 'README.md').write_text('# Isolated fixture\n', encoding='utf-8')
    for name in ('light.svg', 'dark.svg'):
        (fixture / name).write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
    for args in (['init', '-q'], ['add', '.'], ['-c', 'user.name=Fixture', '-c',
                 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
                 '-c', 'core.hooksPath=' + str(fixture / 'no-hooks'), 'commit', '-qm', 'test: isolated fixture']):
        run(['git', '-C', str(fixture), *args], fixture)
    original = (fixture / 'README.md').read_bytes()
    def tool(options, expected=0):
        before = (fixture / 'README.md').read_bytes()
        status = run(['git', 'status', '--porcelain', '--untracked-files=all'], fixture)
        result = run([sys.executable, '-B', str(plugin / 'scripts/repo_tools.py'), *options,
                      '--repo', str(fixture)], fixture, expected=expected)
        if before != (fixture / 'README.md').read_bytes() or status != run(
                ['git', 'status', '--porcelain', '--untracked-files=all'], fixture):
            raise ValueError('Tool changed the fixture')
        return result
    checks = []
    try:
        if json.loads(tool(['snapshot']))['dirty']:
            raise ValueError('Fixture not clean')
        if json.loads(tool(['showcase']))['issues']:
            raise ValueError('Unexpected showcase finding')
        preview = tool(['preview', '--repository', 'example/private-fixture'])
        if 'star-history.com' in preview:
            raise ValueError('Private preview contains external statistics')
        (fixture / 'README.md').write_text(preview, encoding='utf-8')
        if tool(['preview', '--repository', 'example/private-fixture']).strip() != preview.strip():
            raise ValueError('Non-idempotent preview')
        checks.append('preview-idempotent')
        cases = [
            ('private-clickable-badge', '[![x](https://example.invalid/a.svg)](README.md)',
             'private-external-media:', 2),
            ('html-missing-link', '<a href="missing.md">Guide</a>', 'missing-local:', 2),
            ('code-examples', '```md\n![x](missing.png)\n```\n`<img src="missing.png">`', None, 0),
            ('dark-images', '<picture><source srcset="dark.svg"><img src="light.svg"></picture>', None, 0),
        ]
        for name, text, finding, expected in cases:
            (fixture / 'README.md').write_text(text, encoding='utf-8')
            result = json.loads(tool(['showcase'], expected))
            if finding and not any(i.startswith(finding) for i in result['issues']):
                raise ValueError('Missing expected guard')
            if not finding and result['issues']:
                raise ValueError('Unexpected showcase finding')
            checks.append(name)
        public = tool(['preview', '--repository', 'example/public-fixture', '--public', '--star-history'])
        if 'api.star-history.com' not in public or '文字入口' not in public:
            raise ValueError('Missing public preview or fallback')
        checks.append('public-star-history')
    finally:
        (fixture / 'README.md').write_bytes(original)
    if run(['git', 'status', '--porcelain'], fixture):
        raise ValueError('Fixture changed after checks')
    return checks + ['workspace-preserved']


def check(repo, output, host, cli):
    distribution = verify(repo, output / 'distribution')
    env = os.environ.copy()
    for key in ('GH_TOKEN', 'GITHUB_TOKEN', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'CLAUDE_CODE_OAUTH_TOKEN'):
        env.pop(key, None)
    env['NO_COLOR'] = '1'
    with tempfile.TemporaryDirectory(prefix='isolated host ', dir=output) as directory:
        work = Path(directory)
        market, cwd = work / 'market with spaces', work / 'session with spaces'
        market.mkdir()
        cwd.mkdir()
        with zipfile.ZipFile(output / 'distribution/build-one' / distribution['archive']) as bundle:
            bundle.extractall(market)  # Freshly built ZIP was path/symlink checked by verify().
        plugin = market / 'repo-maintainer'
        env['CODEX_HOME'] = str(work / 'codex-home')
        env['CLAUDE_CONFIG_DIR'] = str(work / 'claude-home')
        Path(env['CODEX_HOME']).mkdir()
        Path(env['CLAUDE_CONFIG_DIR']).mkdir()
        version = run([cli, '--version'], cwd, env).strip()
        expected = ('codex-cli ' if host == 'codex' else '') + VERSIONS[host]
        if not (version == expected or version.startswith(expected + ' ')):
            raise ValueError('Unexpected CLI version')
        if host == 'codex':
            catalog = market / '.agents/plugins/marketplace.json'
            catalog.parent.mkdir(parents=True)
            catalog.write_text(json.dumps({'name': 'repo-standards-ci', 'plugins': [{
                'name': 'repo-maintainer', 'source': {'source': 'local', 'path': './repo-maintainer'},
                'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                'category': 'Productivity'}]}), encoding='utf-8')
            run([cli, 'plugin', 'marketplace', 'add', str(market)], cwd, env)
            installed = json.loads(run([cli, 'plugin', 'add', PLUGIN_ID, '--json'], cwd, env))
            plugin = Path(installed['installedPath']).resolve()
            if not plugin.is_relative_to(Path(env['CODEX_HOME']).resolve()):
                raise ValueError('Installation outside isolated home')
            inventory = json.loads(run([cli, 'plugin', 'list', '--marketplace', 'repo-standards-ci', '--json'], cwd, env))
            selected = [p for p in inventory['installed'] if p['pluginId'] == PLUGIN_ID]
            if len(selected) != 1 or not selected[0]['enabled'] or selected[0]['version'] != distribution['version']:
                raise ValueError('Plugin not enabled at expected version')
            skills = codex_skills(cli, env, cwd, plugin)
        else:
            validation = json.loads(run([cli, 'plugin', 'validate', str(plugin), '--json'], cwd, env))
            if not validation['success'] or validation['manifest']['errors']:
                raise ValueError('Claude manifest validation failed')
            details = run([cli, '--plugin-dir', str(plugin), '--bare', 'plugin', 'details', 'repo-maintainer'], cwd, env)
            skills = inventory_from_claude(details, distribution['version'])
        checks = exercise_tools(plugin, work / 'fixture with spaces')
    return {'status': 'verified-host', 'host': host, 'cli_version': VERSIONS[host],
            'plugin_version': distribution['version'], 'source_sha': distribution['source_sha'],
            'archive_sha256': distribution['sha256'], 'skills': skills, 'checks': checks,
            'model_calls': False, 'global_config_changed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--host', choices=tuple(VERSIONS), required=True)
    parser.add_argument('--cli', required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        report = check(args.repo.resolve(), args.output.resolve(), args.host, str(Path(args.cli).resolve()))
        exit_code = 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError,
            queue.Empty, zipfile.BadZipFile) as error:
        report = {'status': 'handoff', 'host': args.host, 'issue_type': type(error).__name__, 'model_calls': False}
        exit_code = 2
    (args.output / 'host-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())

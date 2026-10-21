"""Generate an offline repository explorer and isolated delivery simulator."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import re


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, timeout=30).stdout


def collect(repo):
    repo = Path(repo).resolve()
    actual = Path(git(repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if actual != repo:
        raise ValueError('Pass the repository root')
    files = {p.decode('utf-8', errors='replace') for p in git(repo, 'ls-files', '-z').split(b'\0') if p}
    try:
        head = git(repo, 'rev-parse', '--verify', 'HEAD').decode().strip()
    except subprocess.CalledProcessError:
        head = '尚无提交 / unborn HEAD'
    return {
        'mode': 'local', 'name': repo.name,
        'head': head,
        'branch': git(repo, 'branch', '--show-current').decode().strip() or 'detached HEAD',
        'dirty': bool(git(repo, 'status', '--porcelain')),
        'captured': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'files': len(files),
        'signals': [
            {'label': '项目说明', 'present': any(Path(p).name.lower() == 'readme.md' for p in files)},
            {'label': '协作规则', 'present': bool(files & {'AGENTS.md', 'CLAUDE.md', 'CONTRIBUTING.md'})},
            {'label': '测试目录', 'present': any(p.startswith(('tests/', 'test/')) for p in files)},
            {'label': 'GitHub CI', 'present': any(p.startswith('.github/workflows/') and p.endswith(('.yml', '.yaml')) for p in files)},
        ],
    }


def demo():
    return {'mode': 'demo', 'name': '示例仓库', 'head': '演示数据，无真实提交',
            'branch': 'demo/first-task', 'dirty': False, 'captured': '固定演示数据', 'files': 24,
            'signals': [{'label': label, 'present': present} for label, present in
                        [('项目说明', True), ('协作规则', True), ('测试目录', True), ('GitHub CI', False)]]}


def render(data):
    root = Path(__file__).resolve().parents[1]
    template = (root / 'assets/explorer.html').read_text(encoding='utf-8')
    # JSON stays data even if a repository name contains HTML or a script terminator.
    payload = json.dumps(data, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    catalog = json.loads((root / 'assets/catalog.json').read_text(encoding='utf-8'))
    for item in catalog['items']:
        path = (root / item['path']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Invalid catalog resource')
        if item['kind'] == 'template':
            if path.parent != root / 'templates':
                raise ValueError('Template outside library')
            item['body'] = path.read_text(encoding='utf-8')
    changelog = (root / 'CHANGELOG.md').read_text(encoding='utf-8')
    released = {r['version']: r for r in catalog['releases']}
    catalog['timeline'] = []
    for match in re.finditer(r'^## (\d+\.\d+\.\d+)\s*\n(.*?)(?=^## |\Z)', changelog, re.M | re.S):
        version, body = match.groups()
        catalog['timeline'].append({'version': version, 'released': version in released,
            'date': released.get(version, {}).get('date'),
            'summary': '\n'.join(line.removeprefix('- ') for line in body.splitlines() if line.startswith('- '))[:650]})
    library = json.dumps(catalog, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return re.sub(r'__REPO_DATA__|__CATALOG_DATA__',
                  lambda match: payload if match[0] == '__REPO_DATA__' else library, template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--repo', type=Path)
    mode.add_argument('--demo', action='store_true')
    parser.add_argument('--output', type=Path, required=True, help='New HTML file; existing files are never overwritten')
    args = parser.parse_args()
    try:
        page = render(demo() if args.demo else collect(args.repo))
        with args.output.open('x', encoding='utf-8', newline='\n') as output:
            output.write(page)
        print(json.dumps({'status': 'created', 'output': str(args.output), 'mode': 'demo' if args.demo else 'local'}))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError):
        print('Cannot create explorer: use a Git root and a new writable output path.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

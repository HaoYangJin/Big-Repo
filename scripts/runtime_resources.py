"""One portable runtime inventory for onboarding and deterministic releases."""
from pathlib import Path
import re
from urllib.parse import urlparse, unquote

DIRECTORIES = {'skills', 'templates', 'references'}
SCRIPTS = {'project_workflow.py', 'repo_tools.py', 'explore.py', 'runtime_resources.py', 'collect_research.py'}
ASSETS = {'explorer.html', 'catalog.json', 'social-preview.png', 'explorer-demo.png'}
ROOT_FILES = {'README.md', 'README.en.md', 'CHANGELOG.md', 'LICENSE', 'NOTICE'}


def runtime_files(directory):
    directory = Path(directory).resolve()
    files = {}
    # Enumerate only runtime roots; do not walk Git history, task logs, research
    # snapshots or development output merely to discard them afterwards.
    candidates = []
    for name in sorted(DIRECTORIES):
        root = directory / name
        if root.exists():
            candidates.append(root)
            candidates.extend(root.rglob('*'))
    candidates.extend(directory / name for name in ROOT_FILES)
    candidates.extend(directory / 'scripts' / name for name in SCRIPTS)
    candidates.extend(directory / 'assets' / name for name in ASSETS)
    candidates.extend(directory / name / 'plugin.json' for name in ('.codex-plugin', '.claude-plugin'))
    candidates.extend(directory / 'research' / name for name in ('roster.json', 'source-index.json'))
    for path in candidates:
        relative = path.relative_to(directory)
        parts = relative.parts
        if any(p in {'.git', '.venv', '__pycache__', 'dist', 'work', 'tmp'} for p in parts):
            continue
        allowed = (parts[0] in DIRECTORIES or relative.as_posix() in ROOT_FILES
                   or (len(parts) == 2 and parts[0] in {'.codex-plugin', '.claude-plugin'} and parts[1] == 'plugin.json')
                   or (len(parts) == 2 and parts[0] == 'scripts' and parts[1] in SCRIPTS)
                   or (len(parts) == 2 and parts[0] == 'assets' and parts[1] in ASSETS)
                   or relative.as_posix() in {'research/roster.json', 'research/source-index.json'})
        if not allowed:
            continue
        if any(p.is_symlink() or not p.resolve().is_relative_to(directory)
               for p in (path, *path.parents) if p != directory and directory in p.parents):
            raise ValueError('Linked resources are not distributable')
        if path.is_file() and not path.name.startswith('.env') and path.suffix not in {'.pyc', '.pem', '.key'}:
            files[relative] = path
    return files


def resource_bytes(relative, path, files, version):
    data = path.read_bytes()
    if path.suffix == '.md':
        root = path
        for _ in relative.parts:
            root = root.parent
        root = root.resolve()
        def replace(match):
            target = match[2]
            if urlparse(target).scheme or target.startswith('#'):
                return match[0]
            local, _, fragment = target.partition('#')
            resolved = (path.parent / unquote(local)).resolve()
            try:
                resource = resolved.relative_to(root)
            except ValueError:
                raise ValueError('Markdown link leaves source root')
            if resource in files:
                return match[0]
            remote = resource.as_posix()
            url = f'https://github.com/HaoYangJin/Big-Repo/blob/v{version}/{remote}'
            if fragment:
                url += '#' + fragment
            return match[1] + url + match[3]
        data = re.sub(r'(\[[^\]]*\]\()([^\s)]+)(\))', replace, data.decode('utf-8')).encode('utf-8')
    if path.suffix in {'.md', '.py', '.json', '.html', '.txt', '.template', '.svg'}:
        data = data.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').encode('utf-8')
    return data

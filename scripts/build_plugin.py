"""Build a deterministic plugin ZIP and SHA-256 file. No install or publication."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile
import importlib.util
_spec = importlib.util.spec_from_file_location("runtime_resources", Path(__file__).with_name("runtime_resources.py"))
_resources = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_resources)

ALLOWED_DIRS = {'.codex-plugin', '.claude-plugin', 'skills', 'scripts', 'references', 'templates', 'assets'}
ALLOWED_ROOT = {'README.md', 'LICENSE', 'NOTICE', 'CHANGELOG.md', 'plugin.json', 'mcp.json'}
EXCLUDED = {'__pycache__', '.git', '.venv', '.pytest_cache', 'work', 'dist', 'tmp'}
TEXT_SUFFIXES = {'.md', '.py', '.json', '.yaml', '.yml', '.txt', '.template', '.svg', '.html', '.css', '.js'}


def portable_member(relative):
    name = relative.as_posix()
    reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{p}{i}' for p in ('COM', 'LPT') for i in range(1, 10)}
    if (not name or relative.is_absolute() or any(part in ('..', '.') for part in relative.parts)
            or any(ord(c) < 32 or c in '\\<>:"|?*' for c in name)
            or any(part.endswith(('.', ' ')) or part.split('.')[0].upper() in reserved for part in relative.parts)):
        raise ValueError('Non-portable archive member path')
    return name


def checked_path(file, plugin):
    relative = file.relative_to(plugin)
    portable_member(relative)
    if not file.resolve().is_relative_to(plugin):
        raise ValueError('Resource resolves outside plugin directory')
    for parent in (file, *file.parents):
        if parent == plugin:
            break
        linked = parent.is_symlink()
        if os.name == 'nt' and parent.exists():
            linked = linked or bool(getattr(parent.lstat(), 'st_file_attributes', 0) & 0x400)
        if linked:
            raise ValueError('Linked resources are not distributable')


def build(plugin, output):
    plugin, output = Path(plugin).resolve(), Path(output).resolve()
    if output.is_relative_to(plugin):
        raise ValueError('Output must be outside plugin directory')
    manifest_paths = [plugin / folder / 'plugin.json' for folder in ('.codex-plugin', '.claude-plugin')]
    for file in manifest_paths:
        checked_path(file, plugin)
    manifests = [json.loads(file.read_text(encoding='utf-8')) for file in manifest_paths]
    name, version = manifests[0]['name'], manifests[0]['version']
    if any(m.get('name') != name or m.get('version') != version for m in manifests):
        raise ValueError('Plugin manifests must agree on name and version')
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        raise ValueError('Invalid plugin name')
    if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', version):
        raise ValueError('Invalid plugin version')
    package_name = "Big-Repo" if name == "big-repo" else name
    members = []
    files = _resources.runtime_files(plugin)
    for relative, file in sorted(files.items(), key=lambda item: item[0].as_posix()):
        checked_path(file, plugin)
        members.append((portable_member(relative), _resources.resource_bytes(relative, file, files, version)))
    if not any(p.endswith('/SKILL.md') for p, _ in members):
        raise ValueError('Plugin must contain a skill')
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'{package_name}-{version}.zip'
    checksum = output / (archive.name + '.sha256')
    staged = []
    try:
        # Exclusive, unique files in the destination directory avoid collisions.
        with tempfile.NamedTemporaryFile(dir=output, prefix=f'.{name}-', suffix='.zip.tmp',
                                         mode='w+b', delete=False) as stream:
            temporary = Path(stream.name)
            staged.append(temporary)
            # Stored entries avoid compression-library variation across systems.
            with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as bundle:
                for path, data in members:
                    info = zipfile.ZipInfo(package_name + '/' + path, date_time=(1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    bundle.writestr(info, data)
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        with tempfile.NamedTemporaryFile(dir=output, prefix=f'.{name}-', suffix='.sha256.tmp',
                                         mode='w', encoding='utf-8', newline='\n', delete=False) as stream:
            checksum_temporary = Path(stream.name)
            staged.append(checksum_temporary)
            stream.write(digest + '  ' + archive.name + '\n')
        # Prepare both before publication. Each replacement is atomic, not a pair transaction.
        # Replacing a destination symlink replaces the link, without opening its target.
        temporary.replace(archive)
        checksum_temporary.replace(checksum)
    finally:
        for file in staged:
            file.unlink(missing_ok=True)
    return {'archive': str(archive), 'checksum': str(checksum), 'sha256': digest,
            'files': len(members), 'version': version}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin', type=Path, default=Path(__file__).resolve().parents[1] / '.')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[2] / 'Big-Repo-dist')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.plugin, args.output), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({'status': 'handoff', 'issues': ['invalid-package-input-or-output']}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

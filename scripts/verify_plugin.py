"""Verify the actual distributable, marketplace metadata and reproducibility. Python 3.11+."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
import subprocess
from urllib.parse import unquote, urlparse
import zipfile

try:
    from .build_plugin import build, portable_member
except ImportError:
    from build_plugin import build, portable_member

SKILLS = sorted(('repo-intake', 'maintenance-delivery', 'repo-audit',
                 'release-preparation', 'skill-maintenance', 'repo-showcase'))


def inspect_archive(archive, expected_digest):
    archive = Path(archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_digest:
        raise ValueError('Archive checksum mismatch')
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('Archive integrity failure')
        names = bundle.namelist()
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError('Duplicate or case-colliding resources')
        for info in bundle.infolist():
            portable_member(PurePosixPath(info.filename))
            if (not info.filename.startswith('repo-maintainer/')
                    or stat.S_ISLNK(info.external_attr >> 16)):
                raise ValueError('Unexpected archive member')
        manifests = [json.loads(bundle.read('repo-maintainer/' + path)) for path in (
            'plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json')]
        canonical = manifests[0]
        for field in ('name', 'version', 'description', 'author'):
            if not canonical.get(field) or any(m.get(field) != canonical[field] for m in manifests):
                raise ValueError('Manifest identity mismatch')
        skills = sorted(PurePosixPath(name).parent.name for name in names if name.endswith('/SKILL.md'))
        if skills != SKILLS:
            raise ValueError('Expected the six supported skills')
        for skill in skills:
            entry = f'repo-maintainer/skills/{skill}/SKILL.md'
            text = bundle.read(entry).decode('utf-8')
            if not text.startswith('---\n') or not re.search(r'^name: ' + re.escape(skill) + '$', text, re.M):
                raise ValueError('Invalid skill metadata')
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if urlparse(target).scheme or target.startswith('#'):
                    continue
                resource = posixpath.normpath(str(PurePosixPath(entry).parent / unquote(target.split('#')[0])))
                if not resource.startswith('repo-maintainer/') or resource not in names:
                    raise ValueError('Missing or escaping skill reference')
        return {'version': canonical['version'], 'files': len(names), 'skills': skills}


def verify(repo, output):
    repo, output = Path(repo).resolve(), Path(output).resolve()
    plugin = repo / 'plugins/repo-maintainer'
    canonical = json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))
    for folder, source_key in (('.agents/plugins', 'path'), ('.claude-plugin', None)):
        market = json.loads((repo / folder / 'marketplace.json').read_text(encoding='utf-8'))
        entries = [p for p in market['plugins'] if p['name'] == canonical['name']]
        if len(entries) != 1:
            raise ValueError('Marketplace plugin identity missing or duplicated')
        entry = entries[0]
        source = entry['source'][source_key] if source_key else entry['source']
        if (repo / source).resolve() != plugin or entry.get('version', canonical['version']) != canonical['version']:
            raise ValueError('Marketplace source or version mismatch')
    first, second = build(plugin, output / 'build-one'), build(plugin, output / 'build-two')
    if Path(first['archive']).read_bytes() != Path(second['archive']).read_bytes():
        raise ValueError('Non-reproducible distribution')
    checksum = Path(first['checksum']).read_text(encoding='utf-8').split()
    if checksum != [first['sha256'], Path(first['archive']).name]:
        raise ValueError('Invalid checksum file')
    inspected = inspect_archive(first['archive'], first['sha256'])
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], timeout=20, text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], timeout=20))
    report = {'status': 'verified-distribution', **inspected, 'source_sha': head,
              'working_tree_dirty': dirty, 'sha256': first['sha256'],
              'archive': Path(first['archive']).name, 'reproducible': True, 'model_calls': False}
    (output / 'distribution.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.repo, args.output), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile):
        print(json.dumps({'status': 'handoff', 'issues': ['distribution-verification-failed']}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

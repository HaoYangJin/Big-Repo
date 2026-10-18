"""Prepare a pinned plugin build, then verify and publish an existing release draft."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile


def run(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=300)
    if result.returncode:
        # CLI errors may contain signed URLs or authentication details.
        raise ValueError(f'{command[0]} exited with code {result.returncode}; no write retried')
    return result.stdout, result.stderr


def digest(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


def validate_target(repository, tag, commit, sha256):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid repository')
    if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', tag):
        raise ValueError('Expected a stable vMAJOR.MINOR.PATCH tag')
    if not re.fullmatch(r'[0-9a-f]{40}', commit) or not re.fullmatch(r'[0-9a-f]{64}', sha256):
        raise ValueError('Expected a full commit SHA and SHA-256')


def prepare(source, output, repository, tag, commit, sha256):
    validate_target(repository, tag, commit, sha256)
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.is_relative_to(source):
        raise ValueError('Output must be outside the source checkout')
    actual, _ = run(['git', 'rev-parse', 'HEAD'], cwd=source)
    status, _ = run(['git', 'status', '--porcelain'], cwd=source)
    if actual.strip() != commit or status.strip():
        raise ValueError('Source must be clean and match the pinned commit')
    version = tag[1:]
    for platform in ('.codex-plugin', '.claude-plugin'):
        manifest = json.loads((source / 'plugins/repo-maintainer' / platform / 'plugin.json').read_text())
        if manifest['name'] != 'repo-maintainer' or manifest['version'] != version:
            raise ValueError('Plugin version does not match release tag')
    output.mkdir(parents=True, exist_ok=True)
    stdout, stderr = run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'], cwd=source)
    (output / 'tests.log').write_text(stdout + stderr, encoding='utf-8')
    count = re.search(r'Ran ([0-9]+) tests?\b', stderr)
    if not count or int(count[1]) == 0:
        raise ValueError('No tests executed')
    builds = []
    for directory in ('first', 'second'):
        stdout, _ = run([sys.executable, str(source / 'scripts/build_plugin.py'),
                         '--output', str(output / directory)], cwd=source)
        builds.append(json.loads(stdout))
    archive = output / 'first' / f'repo-maintainer-{version}.zip'
    checksum = archive.with_suffix('.zip.sha256')
    if (digest(archive) != sha256 or digest(Path(builds[1]['archive'])) != sha256
            or checksum.read_text().strip() != f'{sha256}  {archive.name}'):
        raise ValueError('Build differs from the validated artifact or checksum')
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('Invalid ZIP')
    install = archive.parent / f'INSTALL-{version}.md'
    install.write_bytes((source / 'plugins/repo-maintainer/README.md').read_bytes())
    data = {'repository': repository, 'tag': tag, 'commit': commit, 'sha256': sha256,
            'tests_executed': int(count[1]), 'files': [
                {'path': str(file.relative_to(output)), 'sha256': digest(file)}
                for file in (archive, checksum, install)]}
    (output / 'manifest.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return data


def api(path):
    stdout, _ = run(['gh', 'api', path])
    return json.loads(stdout)


def remote_commit(repository, tag):
    obj = api(f'repos/{repository}/git/ref/tags/{tag}')['object']
    for _ in range(5):
        if obj['type'] == 'commit':
            return obj['sha']
        if obj['type'] != 'tag':
            break
        obj = api(f'repos/{repository}/git/tags/{obj["sha"]}')['object']
    raise ValueError('Cannot resolve tag to commit')


def release_id(repository, tag):
    # GitHub's get-by-tag endpoint only returns published releases, not drafts.
    matches = []
    for page in range(1, 101):
        releases = api(f'repos/{repository}/releases?per_page=100&page={page}')
        if not isinstance(releases, list):
            raise ValueError('Unexpected release list')
        matches.extend(r['id'] for r in releases if r.get('tag_name') == tag)
        if len(releases) < 100:
            break
    else:
        raise ValueError('Release list exceeds inspection limit')
    if len(matches) != 1 or type(matches[0]) is not int or matches[0] <= 0:
        raise ValueError('Expected exactly one existing release for the tag')
    return matches[0]


def verify_assets(repository, tag, release, expected, directory):
    assets = release.get('assets', [])
    if (len(assets) != len(expected) or {a['name'] for a in assets} != set(expected)
            or any(a.get('state') != 'uploaded' for a in assets)):
        raise ValueError('Release asset set is incomplete or unexpected')
    for name, file in expected.items():
        run(['gh', 'release', 'download', tag, '--repo', repository, '--pattern', name,
             '--dir', str(directory)])
        if digest(directory / name) != digest(file):
            raise ValueError('Downloaded asset differs from validated bytes')


def publish(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    data = json.loads(manifest_path.read_text())
    repository, tag = data['repository'], data['tag']
    validate_target(repository, tag, data['commit'], data['sha256'])
    version = tag[1:]
    names = {f'repo-maintainer-{version}.zip', f'repo-maintainer-{version}.zip.sha256',
             f'INSTALL-{version}.md'}
    expected = {}
    for item in data['files']:
        file = (manifest_path.parent / item['path']).resolve()
        if not file.is_relative_to(manifest_path.parent) or digest(file) != item['sha256']:
            raise ValueError('Local asset is outside output or has changed')
        if file.name in expected:
            raise ValueError('Duplicate local asset')
        expected[file.name] = file
    if set(expected) != names or digest(expected[f'repo-maintainer-{version}.zip']) != data['sha256']:
        raise ValueError('Unexpected local asset set or ZIP digest')
    if remote_commit(repository, tag) != data['commit']:
        raise ValueError('Remote tag no longer points to the validated commit')
    identity = release_id(repository, tag)

    def release_state():
        release = api(f'repos/{repository}/releases/{identity}')
        if (release.get('id') != identity or release.get('tag_name') != tag
                or type(release.get('draft')) is not bool):
            raise ValueError('Unexpected release identity or draft state')
        return release

    release = release_state()
    assets = release.get('assets', [])
    if (len({a['name'] for a in assets}) != len(assets)
            or any(a['name'] not in expected or a.get('state') != 'uploaded' for a in assets)):
        raise ValueError('Unexpected existing assets; refusing to overwrite')
    if release['draft']:
        # Existing bytes must match before resuming a partially completed upload.
        with tempfile.TemporaryDirectory() as tmp:
            for asset in assets:
                run(['gh', 'release', 'download', tag, '--repo', repository,
                     '--pattern', asset['name'], '--dir', tmp])
                if digest(Path(tmp) / asset['name']) != digest(expected[asset['name']]):
                    raise ValueError('Existing asset differs; refusing to overwrite')
        existing = {a['name'] for a in assets}
        for name, file in expected.items():
            if name not in existing:
                run(['gh', 'release', 'upload', tag, str(file), '--repo', repository])
        with tempfile.TemporaryDirectory() as tmp:
            verify_assets(repository, tag, release_state(), expected, Path(tmp))
        # Recheck the tag immediately before the public write.
        if remote_commit(repository, tag) != data['commit']:
            raise ValueError('Remote tag changed before publication')
        run(['gh', 'release', 'edit', tag, '--repo', repository, '--draft=false', '--latest'])
    release = release_state()
    if release['draft']:
        raise ValueError('Release is still a draft')
    with tempfile.TemporaryDirectory() as tmp:
        verify_assets(repository, tag, release, expected, Path(tmp))
    return {'status': 'published', 'tag': tag, 'commit': data['commit'],
            'url': release['html_url'], 'sha256': data['sha256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    build = sub.add_parser('prepare')
    for name in ('source', 'output', 'repository', 'tag', 'commit', 'sha256'):
        build.add_argument('--' + name, required=True)
    upload = sub.add_parser('publish')
    upload.add_argument('--manifest', required=True)
    args = parser.parse_args()
    try:
        if args.operation == 'prepare':
            result = prepare(args.source, args.output, args.repository, args.tag, args.commit, args.sha256)
        else:
            result = publish(args.manifest)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        print(json.dumps({'status': 'blocked', 'note': 'Inspect the current release and validation state before retrying; no write retried or asset overwritten.'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

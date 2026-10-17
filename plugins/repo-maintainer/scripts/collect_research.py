"""Bounded, resumable public GitHub research. Python 3.11+, standard library only."""
from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

PATTERNS = {
    'tests': r'pytest|unittest|\bvitest\b|\bjest\b|cargo test|go test|npm test|pnpm test|\bctest\b',
    'lint': r'\bruff\b|\beslint\b|\bclippy\b|pre-commit|\bblack\b|\bgofmt\b|\bprettier\b',
    'generated_code': r'generated (?:code|files?)|code.?gen|stainless|do not edit|auto.?generated',
    'release_automation': r'release-please|changesets|semantic-release|goreleaser|pypa/gh-action-pypi-publish|npm publish|gh release create|publish.*pypi',
    'permissions': r'^\s*permissions\s*:|id-token\s*:|contents\s*:\s*write',
    'pinned_actions': r'uses:\s*[^\s]+@[0-9a-f]{40}\b',
    'conventional_commits': r'conventional.?commits|commitlint|\bfeat\(|\bfix\(',
    'security': r'security policy|report.*vulnerabilit|security advisori|responsible disclosure|SECURITY\.md',
    'star_history': r'star-history|starhistory',
    'badges': r'shields\.io|badge\.fury\.io|badge\.svg|badgen\.net|img\.shields',
    'media': r'!\[[^\]]*\]\(|<img\b|<video\b|\.gif\b|asciinema|\.webm\b',
    'theme_images': r'prefers-color-scheme|gh-dark-mode-only|gh-light-mode-only|<picture\b',
    'playground': r'codesandbox|stackblitz|playground|gitpod|codespaces|colab\.research|huggingface\.co/spaces',
    'community': r'all-contributors|contributors?\.svg|good.first.issue|\broadmap\b|/discussions\b|\backnowledg',
    'story': r'\bmilestones?\b|release highlights|\btimeline\b|easter.egg|\bhistory\b',
}


def validate_repo(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', value):
        raise ValueError('Expected owner/repository without URL, query or traversal')
    return value


def inspect_text(path, text):
    return {key: [i for i, line in enumerate(text.splitlines(), 1)
                  if re.search(pattern, line, re.I)][:12] for key, pattern in PATTERNS.items()}


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != 'https' or parsed.hostname != 'api.github.com' or parsed.port not in (None, 443):
            raise ValueError('Refusing cross-origin API redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class GitHub:
    def __init__(self, cache, refresh=False):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.refresh = refresh
        self.fetched_at = {}
        # Never print/store the token or forward it to raw/CDN hosts.
        result = subprocess.run(['gh', 'auth', 'token', '--hostname', 'github.com'],
                                capture_output=True, text=True, check=True, timeout=30)
        self.token = result.stdout.strip()

    def get(self, endpoint):
        if not endpoint.startswith('/repos/') or '\n' in endpoint:
            raise ValueError('Only repository read endpoints are supported')
        cache = self.cache / (hashlib.sha256(endpoint.encode()).hexdigest() + '.json')
        if cache.exists() and not self.refresh:
            self.fetched_at[endpoint] = datetime.fromtimestamp(cache.stat().st_mtime, timezone.utc).isoformat()
            return json.loads(cache.read_text(encoding='utf-8'))
        req = Request('https://api.github.com' + endpoint, headers={
            'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'repo-maintainer-research/0.1'})
        for attempt in range(3):
            try:
                with build_opener(SafeRedirect).open(req, timeout=45) as response:
                    data = response.read(12_000_001)
                if len(data) > 12_000_000:
                    raise ValueError('API response exceeds 12 MB bound')
                result = json.loads(data)
                cache.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
                self.fetched_at[endpoint] = datetime.fromtimestamp(cache.stat().st_mtime, timezone.utc).isoformat()
                return result
            except HTTPError as error:
                if error.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f'GitHub HTTP {error.code}: {endpoint}') from None
            except (URLError, TimeoutError):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f'GitHub transport failure: {endpoint}') from None


def collect(api, item):
    requested = validate_repo(item['repository'])
    record = {'requested_repository': requested, 'category': item['category'],
              'collected_at': datetime.now(timezone.utc).isoformat(), 'errors': [],
              'method': 'bounded-public-source-inspection-v1'}

    def get(endpoint, fallback=None):
        try:
            return api.get(endpoint)
        except (RuntimeError, ValueError) as error:
            record['errors'].append(str(error))
            return fallback

    meta = get('/repos/' + requested)
    if not meta:
        record['status'] = 'inaccessible'
        return record
    if meta.get('private'):
        record['status'] = 'private-skipped'
        return record
    repo = validate_repo(meta['full_name'])
    prefix = '/repos/' + repo
    record['repository'] = repo
    record['metadata'] = {k: meta.get(k) for k in ('html_url', 'description', 'homepage', 'language',
        'stargazers_count', 'forks_count', 'open_issues_count', 'pushed_at', 'created_at', 'archived',
        'default_branch', 'license', 'topics', 'owner', 'has_discussions')}
    # Keep only public owner identity, not the redundant API profile payload.
    record['metadata']['owner'] = {k: meta['owner'].get(k) for k in ('login', 'type', 'html_url')}
    commits = get(prefix + '/commits?sha=' + quote(meta['default_branch'], safe='') + '&per_page=20', [])
    record['commits'] = [{'sha': c['sha'], 'url': c['html_url'],
                          'date': c['commit']['committer']['date'],
                          'subject': c['commit']['message'].splitlines()[0]} for c in commits]
    if not commits:
        record['status'] = 'no-default-commit'
        return record
    sha = commits[0]['sha']
    record['default_sha'] = sha
    root = get(prefix + '/git/trees/' + sha, {}).get('tree', [])
    entries = {e['path']: e for e in root}
    doc_re = re.compile(r'^(readme|contribut|security|agents|claude|owners|codeowners|maintain|governance|code.of.conduct|release|changelog|changes|support|package\.json|pyproject\.toml|cargo\.toml|go\.mod|makefile|\.changeset|\.release|release-please|\.all-contributors)', re.I)
    selected = {p: e for p, e in entries.items() if e['type'] == 'blob' and doc_re.search(p)}
    root_paths = list(entries)
    workflows = []
    for directory in ('.github', 'docs', 'doc', '.claude-plugin', '.codex-plugin'):
        entry = entries.get(directory)
        if not entry or entry['type'] != 'tree':
            continue
        children = get(prefix + '/git/trees/' + entry['sha'], {}).get('tree', [])
        for child in children:
            path = directory + '/' + child['path']
            root_paths.append(path)
            if child['type'] == 'blob' and (doc_re.search(child['path']) or child['path'].lower().endswith('template.md') or child['path'] in ('dependabot.yml', 'renovate.json', 'plugin.json')):
                selected[path] = child
            if directory == '.github' and child['type'] == 'tree' and child['path'] in ('workflows', 'ISSUE_TEMPLATE', 'PULL_REQUEST_TEMPLATE'):
                nested = get(prefix + '/git/trees/' + child['sha'], {}).get('tree', [])
                for n in nested:
                    np = path + '/' + n['path']
                    root_paths.append(np)
                    if n['type'] == 'blob':
                        if child['path'] == 'workflows':
                            workflows.append((np, n))
                        else:
                            selected[np] = n
    workflows.sort(key=lambda pair: (not bool(re.search('release|publish|test|ci|secur|depend', pair[0], re.I)), pair[0]))
    for path, entry in workflows[:12]:
        selected[path] = entry
    # Inspect representative skill/plugin entrypoints in content-focused repositories.
    for directory in ('skills', 'plugins'):
        entry = entries.get(directory)
        if not entry or entry['type'] != 'tree':
            continue
        children = get(prefix + '/git/trees/' + entry['sha'], {}).get('tree', [])
        for child in [c for c in children if c['type'] == 'tree'][:3]:
            nested = get(prefix + '/git/trees/' + child['sha'], {}).get('tree', [])
            for n in nested:
                if n['type'] == 'blob' and n['path'].lower() in ('skill.md', 'readme.md'):
                    selected[directory + '/' + child['path'] + '/' + n['path']] = n
    # Preserve bounded selection coverage rather than imply exhaustive code inspection.
    record['root_and_selected_directory_paths'] = sorted(root_paths)
    record['workflow_paths'] = [p for p, _ in workflows]
    record['documents'] = []
    for path, entry in selected.items():
        if entry.get('size', 0) > 400_000:
            record['documents'].append({'path': path, 'status': 'skipped-size', 'sha': entry['sha']})
            continue
        blob = get(prefix + '/git/blobs/' + entry['sha'])
        if not blob:
            continue
        content = base64.b64decode(blob['content']).decode('utf-8', errors='replace')
        record['documents'].append({'path': path, 'sha': entry['sha'], 'status': 'inspected',
            'url': f'https://github.com/{repo}/blob/{sha}/{quote(path, safe="/")}',
            'lines': len(content.splitlines()), 'signals': inspect_text(path, content)})
    prs = []
    for page in range(1, 6):
        closed = get(prefix + f'/pulls?state=closed&sort=updated&direction=desc&per_page=100&page={page}', [])
        prs += [p for p in closed if p.get('merged_at') and p.get('base', {}).get('ref') == meta['default_branch']]
        if len(prs) >= 3 or len(closed) < 100:
            break
    record['pull_requests'] = []

    def runs_for(commit):
        if not commit:
            return []
        data = get(prefix + '/actions/runs?head_sha=' + quote(commit, safe='') + '&per_page=10', {})
        return [{k: r.get(k) for k in ('id', 'name', 'path', 'event', 'status', 'conclusion', 'html_url', 'head_sha')}
                for r in data.get('workflow_runs', [])]

    for pr in prs[:3]:
        files = get(prefix + f'/pulls/{pr["number"]}/files?per_page=100', [])
        reviews = get(prefix + f'/pulls/{pr["number"]}/reviews?per_page=100', [])
        record['pull_requests'].append({'number': pr['number'], 'title': pr['title'],
            'url': pr['html_url'], 'merged_at': pr['merged_at'], 'merge_commit_sha': pr['merge_commit_sha'],
            'files': [f['filename'] for f in files], 'files_may_be_truncated': len(files) == 100,
            'file_changes': [{k: f.get(k) for k in ('filename', 'status', 'additions', 'deletions', 'blob_url')} for f in files],
            'review_states': [r['state'] for r in reviews], 'reviews_may_be_truncated': len(reviews) == 100,
            'merge_commit_workflow_runs': runs_for(pr['merge_commit_sha']),
            'head_commit_workflow_runs': runs_for(pr.get('head', {}).get('sha'))})
    record['pr_selection'] = 'latest-updated closed PRs merged into current default branch; up to 500 closed PRs scanned'
    # Releases endpoint is descending creation order; select non-draft, non-prerelease within 100.
    releases = []
    for page in range(1, 6):
        batch = get(prefix + f'/releases?per_page=20&page={page}', [])
        releases.extend(batch)
        if len([r for r in releases if not r['draft'] and not r['prerelease']]) >= 3 or len(batch) < 20:
            break
    record['releases'] = []
    for release in [r for r in releases if not r['draft'] and not r['prerelease']][:3]:
        commit = get(prefix + '/commits/' + quote(release['tag_name'], safe=''), {})
        record['releases'].append({'tag': release['tag_name'], 'url': release['html_url'],
            'published_at': release['published_at'], 'target_commitish': release['target_commitish'],
            'commit_sha': commit.get('sha'), 'assets': [a['name'] for a in release.get('assets', [])],
            'workflow_runs': runs_for(commit.get('sha'))})
    record['release_selection'] = 'first 3 stable published releases among latest 100 GitHub release records, API creation order'
    record['tags'] = [{'name': t['name'], 'sha': t['commit']['sha']}
                      for t in get(prefix + '/tags?per_page=3', [])]
    record['unknowns'] = ['effective branch protection', 'effective token permissions',
                          'external CI execution', 'private maintainer procedures',
                          'historical star counts unless independently collected']
    record['assembled_at'] = datetime.now(timezone.utc).isoformat()
    record['source_times'] = {key: value for key, value in api.fetched_at.copy().items()
                              if key.startswith(prefix + '/') or key in (prefix, '/repos/' + requested)}
    times = list(record['source_times'].values())
    record['collected_at'] = min(times) if times else None
    record['last_source_fetch_at'] = max(times) if times else None
    record['status'] = 'collected-with-gaps' if record['errors'] else 'collected'
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roster', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild records from cache without refreshing network responses')
    parser.add_argument('--workers', type=int, default=4, choices=range(1, 9))
    args = parser.parse_args()
    roster = json.loads(args.roster.read_text(encoding='utf-8'))
    for item in roster:
        validate_repo(item['repository'])
    args.output.mkdir(parents=True, exist_ok=True)
    api = GitHub(args.cache, args.refresh)
    pending = [i for i in roster if args.refresh or args.rebuild or not (args.output / (i['repository'].replace('/', '__') + '.json')).exists()]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        tasks = {executor.submit(collect, api, item): item for item in pending}
        for future in as_completed(tasks):
            item = tasks[future]
            data = future.result()
            output = args.output / (item['repository'].replace('/', '__') + '.json')
            temporary = output.with_suffix('.tmp')
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            temporary.replace(output)
            print(item['repository'], data['status'], 'documents=', len(data.get('documents', [])),
                  'PRs=', len(data.get('pull_requests', [])), 'releases=', len(data.get('releases', [])), flush=True)


if __name__ == '__main__':
    main()

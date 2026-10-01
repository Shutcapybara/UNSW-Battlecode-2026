"""Semi-regular repository hygiene, run on the Mac by the hub actuator (and on demand with `hubctl git sync`).

Policy (director decision D-007): commit only paths that match the include list, have been quiet for
`quiet_minutes`, and parse (Python) or carry `bot.toml` (bot directories); never stage the working tree wholesale;
never delete, rebase or force-push; merge `origin/<branch>` with an ordinary merge and stop on conflict; push only
when the merge is clean. Everything it does or skips is reported in `HUB/git/<epoch>.json` and in the review packet.
"""
import ast
import fnmatch
import json
import os
import subprocess
import time
from pathlib import Path

from . import db

DEFAULT_POLICY = dict(enabled=True, interval_seconds=10800, branch='main', push=True, quiet_minutes=60,
                      include=['bots/*', 'docs/*', 'game_stats/runs/*.parquet', 'game_stats/imports/*.json', 'tools/*', 'tests/*',
                               'maps/*.map', 'benchmark.toml', 'comparison.toml', 'README.md', '.gitignore'],
                      never=['.battlecode-api-key', 'experiment_data/*', 'build/*', 'public_replays/*', 'hub-state/*', '*.replay', '*.replay.gz',
                             'game_stats.parquet', 'game_stats/sources/*', '*.tgz', '*.zip', '*.lock', '.venv/*', 'unswbc/*', 'replays/*', '*.log'])
TRAILER = 'Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01NuyM2R5hEK6qXBdiZEEFub'
STALE_LOCK_SECONDS = 3600  # .git/index.lock older than this is removed before a pass (D-041 housekeeping)


def git(repo, *args, timeout=120, check=False):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(f'git {" ".join(args)} failed: {result.stderr.strip()[:400]}')
    return result


def matches(path, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern.rstrip('*') + '*') or path.startswith(pattern.rstrip('*')):
            return True
        if pattern.endswith('/*') and path.startswith(pattern[:-1]):
            return True
    return False


IGNORED_DIRS = {'__pycache__', '.unswbc-build', 'build', '.git', '.pytest_cache'}


def latest_mtime(path):
    """Newest mtime under `path`, ignoring caches and build output (a running campaign touches __pycache__)."""
    path = Path(path)
    if path.is_file():
        return path.stat().st_mtime
    latest = 0.0
    for f in path.rglob('*'):
        if any(part in IGNORED_DIRS for part in f.relative_to(path).parts) or f.suffix in ('.pyc', '.pyo'):
            continue
        if f.is_file():
            latest = max(latest, f.stat().st_mtime)
    return latest


def python_parses(path):
    path = Path(path)
    files = [path] if path.is_file() else [f for f in path.rglob('*.py')]
    for f in files:
        if f.suffix != '.py' or '__pycache__' in f.parts:
            continue
        try:
            ast.parse(f.read_text(errors='replace'), filename=str(f))
        except SyntaxError as exc:
            return False, f'{f.name}: {exc.msg} line {exc.lineno}'
    return True, ''


def classify(repo, policy, now=None):
    """Return dict(commit=[paths], skipped=[(path, reason)]) from `git status`."""
    now = now or time.time()
    status = git(repo, '--no-optional-locks', 'status', '--porcelain=v1', '--untracked-files=all', '-z', check=True).stdout
    entries = [e for e in status.split('\0') if e]
    commit, skipped = [], []
    quiet = policy['quiet_minutes'] * 60
    seen_dirs = set()
    i = 0
    while i < len(entries):
        entry = entries[i]
        code, path = entry[:2], entry[3:]
        if code[0] == 'R':  # renamed: the next entry is the old path
            i += 1
        i += 1
        if 'D' in code:
            skipped.append((path, 'deletion (never automated)'))
            continue
        if matches(path, policy['never']):
            skipped.append((path, 'never list'))
            continue
        if not matches(path, policy['include']):
            skipped.append((path, 'outside include list'))
            continue
        # Untracked files inside a new bot directory are committed as the whole directory once it is quiet.
        unit = path
        parts = path.split('/')
        if code == '??' and parts[0] == 'bots' and len(parts) > 2:
            unit = '/'.join(parts[:2])
            if unit in seen_dirs:
                continue
            seen_dirs.add(unit)
            if not (Path(repo) / unit / 'bot.toml').exists():
                skipped.append((unit, 'bot directory without bot.toml'))
                continue
        age = now - latest_mtime(Path(repo) / unit)
        if age < quiet:
            skipped.append((unit, f'settling ({int(age // 60)} min < {policy["quiet_minutes"]})'))
            continue
        ok, why = python_parses(Path(repo) / unit)
        if not ok:
            skipped.append((unit, f'python does not parse: {why}'))
            continue
        commit.append(unit)
    return dict(commit=sorted(set(commit)), skipped=skipped)


def summarize(paths):
    bots = [p for p in paths if p.startswith('bots/')]
    runs = [p for p in paths if p.startswith('game_stats/')]
    docs = [p for p in paths if p.startswith('docs/')]
    other = [p for p in paths if p not in bots + runs + docs]
    bits = []
    if bots:
        bits.append(f'{len(bots)} bot snapshot{"s" if len(bots) != 1 else ""}')
    if runs:
        bits.append(f'{len(runs)} game-stats contribution{"s" if len(runs) != 1 else ""}')
    if docs:
        bits.append(f'{len(docs)} doc file{"s" if len(docs) != 1 else ""}')
    if other:
        bits.append(f'{len(other)} other')
    return ', '.join(bits) or 'nothing'


def sync(repo, root, policy, actor='hub/gitkeeper', dry_run=False, now=None):
    repo = Path(repo)
    report = dict(at=db.now_iso(), repo=str(repo), dry_run=dry_run, committed=[], skipped=[], merged=None, pushed=None, errors=[], attention=[])
    try:
        branch = git(repo, '--no-optional-locks', 'rev-parse', '--abbrev-ref', 'HEAD', check=True).stdout.strip()
        report['branch'] = branch
        if branch != policy['branch']:
            report['attention'].append(f'checkout is on {branch}, not {policy["branch"]}; nothing done')
            return finish(root, report)
        lock = repo / '.git' / 'index.lock'
        if lock.exists() and (now or time.time()) - lock.stat().st_mtime > STALE_LOCK_SECONDS:
            # an index.lock no git process has touched for an hour is a crash leftover (1 Oct: three in four days,
            # each blocking every commit until a human removed it); git holds the lock only for the length of one command
            try:
                lock.unlink()
                report['attention'].append('stale .git/index.lock removed (older than %d min)' % (STALE_LOCK_SECONDS // 60))
            except OSError as exc:
                report['attention'].append(f'stale .git/index.lock could not be removed: {exc}')
        for marker in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'index.lock', 'rebase-merge', 'rebase-apply'):
            if (repo / '.git' / marker).exists():
                report['attention'].append(f'.git/{marker} present; a human must finish or clear it; nothing done')
                return finish(root, report)
        if (repo / '.git' / 'REBASE_HEAD').exists() and not any((repo / '.git' / d).exists() for d in ('rebase-merge', 'rebase-apply')):
            # a REBASE_HEAD without a rebase directory is a leftover of a finished/aborted rebase (27 Sep), not an operation in progress
            try:
                (repo / '.git' / 'REBASE_HEAD').unlink()
                report['attention'].append('stale .git/REBASE_HEAD removed (no rebase in progress)')
            except OSError as exc:
                report['attention'].append(f'stale .git/REBASE_HEAD could not be removed: {exc}')
        plan = classify(repo, policy, now=now)
        report['skipped'] = plan['skipped']
        if plan['commit'] and not dry_run:
            git(repo, 'add', '--', *plan['commit'], check=True)
            message = f"[hub-git] {summarize(plan['commit'])}\n\n" + '\n'.join(f'- {p}' for p in plan['commit']) + f'\n\nAutomated by tools/hub/gitkeeper.py (policy D-007).\n\n{TRAILER}\n'
            result = git(repo, 'commit', '-q', '-m', message)
            if result.returncode:
                report['errors'].append('commit: ' + result.stderr.strip()[:300])
            else:
                report['committed'] = plan['commit']
                report['commit'] = git(repo, 'rev-parse', '--short', 'HEAD').stdout.strip()
        elif plan['commit']:
            report['would_commit'] = plan['commit']
        fetch = git(repo, 'fetch', '--quiet', 'origin', policy['branch'], timeout=180)
        if fetch.returncode:
            report['errors'].append('fetch: ' + fetch.stderr.strip()[:300])
            return finish(root, report)
        behind = git(repo, 'rev-list', '--count', f'HEAD..origin/{policy["branch"]}').stdout.strip()
        ahead = git(repo, 'rev-list', '--count', f'origin/{policy["branch"]}..HEAD').stdout.strip()
        report['behind'], report['ahead'] = int(behind or 0), int(ahead or 0)
        if report['behind'] and not dry_run:
            dirty = [line[3:].strip() for line in git(repo, '--no-optional-locks', 'status', '--porcelain=v1', '--untracked-files=no').stdout.splitlines() if line.strip()]
            incoming = set(git(repo, '--no-optional-locks', 'diff', '--name-only', f'HEAD...origin/{policy["branch"]}').stdout.split())
            clash = sorted(set(dirty) & incoming)
            if clash:
                report['attention'].append(f'origin is ahead and touches locally modified files {clash[:5]}; merge deferred until they are quiet')
            else:
                if dirty:
                    report['attention'].append(f'merged with {len(dirty)} locally modified tracked file(s) untouched by origin (left as they are)')
                merge = git(repo, 'merge', '--no-edit', f'origin/{policy["branch"]}', timeout=300)
                if merge.returncode:
                    git(repo, 'merge', '--abort')
                    report['attention'].append('merge conflict with origin; aborted; a director must merge by hand')
                    report['merged'] = False
                    return finish(root, report)
                report['merged'] = True
                report['ahead'] = int(git(repo, 'rev-list', '--count', f'origin/{policy["branch"]}..HEAD').stdout.strip() or 0)
        if policy.get('push') and not dry_run and report['ahead'] and report.get('merged') is not False:
            push = git(repo, 'push', '--quiet', 'origin', policy['branch'], timeout=300)
            report['pushed'] = push.returncode == 0
            if push.returncode:
                report['errors'].append('push: ' + push.stderr.strip()[:300])
    except Exception as exc:
        report['errors'].append(repr(exc)[:300])
    return finish(root, report)


def finish(root, report):
    out = Path(root) / 'git'
    out.mkdir(parents=True, exist_ok=True)
    (out / f'{int(time.time())}.json').write_text(db.j(report))
    (out / 'latest.json').write_text(db.j(report))
    try:
        conn = db.connect(root)
        db.kv_set(conn, 'git_last_sync', report)
        db.event(conn, root, 'hub/gitkeeper', 'git_sync', dict(committed=len(report['committed']), skipped=len(report['skipped']), pushed=report.get('pushed'),
                                                              merged=report.get('merged'), errors=report['errors'], attention=report['attention']))
        conn.close()
    except Exception:
        pass
    return report

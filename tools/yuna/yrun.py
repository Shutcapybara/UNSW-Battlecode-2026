#!/usr/bin/env python3
"""Spike panel runner: resumable, sharded, deadline-bounded fixture execution.

plan.json  = {"fixtures": [{id, map, map_path, cand, cand_path, opp, opp_path, side}], ...}
results    = append-only JSONL, one row per completed/errored fixture id.

The candidate plays team A when side == "A" (`unswbc run map cand opp`), else team B.
Each worker keeps private copies of bot sources so concurrent builds never collide.
Replays are analysed with the repository's comparison_metrics.analyse and then deleted
unless --keep-replays is given. Errors are recorded as errors, never as outcomes.
"""
import argparse, json, os, re, shutil, subprocess, sys, time, hashlib, socket, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CHECKS = (20, 50, 100, 200, 300, 400, 500)
KEYS = ("units", "total", "longest", "pearls", "splits", "deaths", "enemy_kills",
        "killed_by_enemy", "team_kills", "self_collisions", "wall_deaths", "tle", "space_share")
ANSI = re.compile(r'\x1b\[[0-9;]*m')
OUTCOME = re.compile(r'^(?:team ([AB]) wins|draw) after (\d+) rounds\b(?: \(([^)]*)\))?', re.M)
FAULT = re.compile(r'^round \d+: bot \d+ \(team [AB]\) (?!died:).*(?:exited|timed out|ran out of time|timeout|broken pipe|failed).*$', re.M)
IGN = ('.git', '.unswbc-build', '__pycache__', 'build', '.DS_Store')


def tree_sha(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).rglob('*')):
        if p.is_file() and not any(x in IGN for x in p.relative_to(d).parts):
            h.update(str(p.relative_to(d)).encode()); h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def summarise(replay, repo):
    sys.path.insert(0, str(Path(repo) / 'tools'))
    from comparison_metrics import analyse
    s = analyse(str(replay))
    out = dict(reason=s['reason'], final=s['final'], checkpoints={})
    for t in 'AB':
        ser = s['series'][t]
        byr = {p['round']: p for p in ser}
        last = ser[-1]
        for c in CHECKS:
            p = byr.get(c)
            if p is None and c > last['round']:
                p = dict(last, alive_at_check=False) if last['units'] == 0 else None
                if p is not None:
                    p = {**p, 'ended_before': True}
            if p is not None:
                out['checkpoints'].setdefault(str(c), {})[t] = {k: p.get(k) for k in KEYS} | (
                    {'ended_before': True} if p.get('ended_before') else {})
        out.setdefault('totals', {})[t] = {k: last.get(k) for k in KEYS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan'); ap.add_argument('results')
    ap.add_argument('--repo', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--launch-deadline', type=float, default=1e9, help='seconds after start to stop launching')
    ap.add_argument('--kill-deadline', type=float, default=1e9)
    ap.add_argument('--timeout', type=float, default=600)
    ap.add_argument('--short-after', type=float, default=1e9, help='after this many seconds only launch small maps')
    ap.add_argument('--short-area', type=int, default=625)
    ap.add_argument('--min-area', type=int, default=0)
    ap.add_argument('--max-area', type=int, default=10**9)
    ap.add_argument('--retry-errors', action='store_true')
    ap.add_argument('--reverse', action='store_true')
    ap.add_argument('--keep-replays', default='')
    ap.add_argument('--host', default=socket.gethostname())
    ap.add_argument('--also-done', nargs='*', default=[], help='other hosts result files whose ids are skipped')
    a = ap.parse_args()
    t0 = time.monotonic()
    plan = json.load(open(a.plan))
    si, sn = map(int, a.shard.split('/'))
    done = set()
    for rf in [a.results] + a.also_done:
        if not os.path.exists(rf): continue
        for line in open(rf):
            try:
                row = json.loads(line)
                if a.retry_errors and row.get('outcome') == 'error': continue
                done.add(row['id'])
            except Exception: pass
    todo = [f for f in plan['fixtures'] if int(f['id'], 16) % sn == si and f['id'] not in done]
    if a.reverse: todo.reverse()
    print(f'{len(todo)} fixtures to run on shard {a.shard}', flush=True)
    work = Path(a.work); work.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    def area(mp):
        t = (Path(a.repo) / mp).read_bytes(); i = t.find(b'MAP ')
        p = t[i:i + 40].split(b'\n')[0].split(); return int(p[1]) * int(p[2])
    areas = {f['map_path']: 0 for f in todo}
    for mp in areas: areas[mp] = area(mp)
    def take():
        small_only = time.monotonic() - t0 > a.short_after
        for k, f in enumerate(todo):
            if not a.min_area <= areas[f['map_path']] <= a.max_area: continue
            if not small_only or areas[f['map_path']] <= a.short_area:
                return todo.pop(k)
        return None
    keep = Path(a.keep_replays) if a.keep_replays else None
    if keep: keep.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

    def copy_bot(wk, name, path):
        dst = work / f'wk{wk}' / name
        if not dst.exists():
            shutil.copytree(Path(a.repo) / path, dst, ignore=shutil.ignore_patterns(*IGN))
        return dst

    def worker(wk):
        n = 0
        while True:
            if time.monotonic() - t0 > a.launch_deadline: return n
            with lock:
                f = take()
            if f is None: return n
            A, B = ((f['cand'], f['cand_path']), (f['opp'], f['opp_path'])) if f['side'] == 'A' else \
                   ((f['opp'], f['opp_path']), (f['cand'], f['cand_path']))
            pa, pb = copy_bot(wk, *A), copy_bot(wk, *B)
            rp = work / f'wk{wk}' / f"{f['id']}.replay"
            cmd = ['unswbc', 'run', str(Path(a.repo) / f['map_path']), str(pa), str(pb), '-o', str(rp)]
            start = time.monotonic()
            remaining = min(a.timeout, a.kill_deadline - (start - t0))
            try:
                pr = subprocess.run(cmd, capture_output=True, text=True, timeout=max(1, remaining), env=env,
                                    cwd=work / f'wk{wk}')
                log, err = pr.stdout + pr.stderr, None
            except subprocess.TimeoutExpired as e:
                if a.kill_deadline - (start - t0) < a.timeout:
                    return n  # deadline abort: not a result, leave fixture for the next call
                log, err = str(e.stdout or ''), f'timed out after {a.timeout}s'
            row = dict(id=f['id'], cand=f['cand'], opp=f['opp'], map=f['map'], side=f['side'],
                       host=a.host, seconds=round(time.monotonic() - start, 2))
            ms = list(OUTCOME.finditer(ANSI.sub('', log or '')))
            if err is None and ms and pr.returncode == 0:
                m = ms[-1]
                win, rounds, how = m.group(1), int(m.group(2)), m.group(3)
                row.update(winner_team=win or 'draw', rounds=rounds, how=how,
                           outcome='D' if not win else 'W' if win == f['side'] else 'L')
            else:
                row.update(outcome='error', error=err or 'no result line', tail=(log or '')[-400:])
            row['faults'] = FAULT.findall(log or '')[:5]
            if row['outcome'] != 'error' and rp.exists():
                try: row['stats'] = summarise(rp, a.repo)
                except Exception as e: row['stats_error'] = repr(e)
            if rp.exists():
                if keep: shutil.move(str(rp), keep / rp.name)
                else: rp.unlink()
            with lock:
                with open(a.results, 'a') as fh: fh.write(json.dumps(row) + '\n')
            n += 1

    with ThreadPoolExecutor(a.jobs) as ex:
        counts = list(ex.map(worker, range(a.jobs)))
    print(f'ran {sum(counts)} in {time.monotonic()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()

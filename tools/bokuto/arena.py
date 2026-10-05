#!/usr/bin/env python3
"""bokuto arena: a resumable, time-budgeted game runner and scorecard.

    python3 arena.py run  --out RESULTS.jsonl --fixtures FIX.json [--jobs 4] [--budget 165] [--replays DIR]
    python3 arena.py h2h  --out RESULTS.jsonl --a BOT --b BOT [--maps live17] [--seeds 1 2 3] ...
    python3 arena.py pool --out RESULTS.jsonl --bot BOT [--seeds 1]
    python3 arena.py report RESULTS.jsonl [--bot BOT]

A fixture is (map, botA, botB, seed). Results are appended to a JSONL file; a fixture whose key is already
in the file is skipped, so a run can be resumed in slices (the Cowork VM kills every process when a shell
call ends, so --budget stops launching new games when the budget would be exceeded).
Paths: --root is the repo root (bots/, maps/); --unswbc is the engine executable.
"""
from __future__ import annotations

import argparse, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

RESULT = re.compile(r'team (A|B) wins after (\d+) rounds \(([^)]*)\)')
DRAW = re.compile(r'draw after (\d+) rounds', re.I)

LIVE17 = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma', 'autarky',
          'devil', 'trauma', 'australia', 'islands', 'unsw', 'maze', 'weakhold', 'stripes', 'tower_defense']
ZOO = ['fenrir-v18-arrival-ready-beds', 'yuna-v05-core', 'chaewon-y04-probe', 'sinbad-v07-divecap',
       'gavroche-v32-supported-divecap', 'ouroboros-m01-vibing-mimic', 'kazuha-s01-swarm-dissolve',
       'hunter-v20-portal-scouts']
HEAVY = ['schooltime', 'slithery_fight', 'portals', 'australia', 'unsw', 'islands']


def fkey(f):
    return f"{f['map']}|{f['a']}|{f['b']}|{f['seed']}"


def load_done(out: Path):
    done = {}
    if out.exists():
        for line in out.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get('reason') == 'ERROR' and r.get('rc') != 0 and 'Text file busy' in r.get('tail', ''):
                continue
            done[r['key']] = r
    return done


def map_path(root: Path, m: str) -> Path:
    p = root / 'maps' / (m if m.endswith('.map') else m + '.map')
    if not p.exists():
        p = root / 'maps' / 'live' / (m + '.map')
    return p


def run_game(root: Path, unswbc: str, f: dict, replay_dir: Path | None, nice: int, timeout: int):
    cmd = []
    if nice:
        cmd += ['nice', '-n', str(nice)]
    cmd += [unswbc, 'run', '--seed', str(f['seed']), '--no-debug']
    rp = None
    if replay_dir:
        replay_dir.mkdir(parents=True, exist_ok=True)
        rp = replay_dir / (fkey(f).replace('|', '__').replace('/', '+') + '.json')
        cmd += ['-o', str(rp)]
    else:
        cmd += ['--no-replay']
    cmd += [str(map_path(root, f['map'])), str(root / 'bots' / f['a']), str(root / 'bots' / f['b'])]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(root))
        text = p.stdout + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired as e:
        text = (e.stdout or '') + (e.stderr or '') if isinstance(e.stdout, str) else ''
        rc = -9
    dt = time.time() - t0
    rec = dict(key=fkey(f), **f, rc=rc, secs=round(dt, 1), winner=None, rounds=None, reason=None,
               replay=str(rp) if rp else None)
    m = RESULT.search(text)
    if m:
        rec['winner'] = m.group(1)
        rec['rounds'] = int(m.group(2))
        rec['reason'] = m.group(3)
    elif DRAW.search(text):
        rec['winner'] = 'D'
        rec['rounds'] = int(DRAW.search(text).group(1))
        rec['reason'] = 'draw'
    else:
        rec['reason'] = 'ERROR'
        rec['tail'] = text[-600:]
    # runtime faults: the engine prints "died: <reason>" lines; record faults by team
    faults = re.findall(r'bot (\d+) \(team (A|B)\) died: (.*)', text)
    bad = [t for (_id, t, why) in faults if any(k in why for k in ('no valid action', 'timed out', 'runtime', 'error', 'crash'))]
    rec['faults_A'] = bad.count('A')
    rec['faults_B'] = bad.count('B')
    return rec


def run_fixtures(args, fixtures):
    root = Path(args.root).resolve()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(out)
    todo = [f for f in fixtures if fkey(f) not in done]
    print(f'{len(fixtures)} fixtures, {len(done)} done, {len(todo)} to run', flush=True)
    if not todo:
        return
    replay_dir = Path(args.replays) if args.replays else None
    t_start = time.time()
    # warm-up: compile every bot once, serially (parallel first runs race on .unswbc-build/bot)
    warm = sorted({f['a'] for f in todo} | {f['b'] for f in todo})
    wmap = map_path(root, 'live/arena') if map_path(root, 'live/arena').exists() else map_path(root, todo[0]['map'])
    for b in warm:
        bd = root / 'bots' / b
        stamp = bd / '.unswbc-build' / '.bokuto-warm'
        src_mtime = max((p.stat().st_mtime for p in bd.iterdir() if p.is_file()), default=0)
        if stamp.exists() and stamp.stat().st_mtime >= src_mtime:
            continue
        print(f'warming {b}', flush=True)
        subprocess.run([args.unswbc, 'run', '--no-replay', '--seed', '1', str(wmap), str(bd), str(bd)],
                       capture_output=True, text=True, timeout=args.timeout, cwd=str(root))
        stamp.parent.mkdir(exist_ok=True)
        stamp.touch()
    launched = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as ex, out.open('a') as fh:
        futs = {}
        it = iter(todo)
        # keep the pool full while the budget allows a new game
        def can_launch():
            if args.budget <= 0:
                return True
            return time.time() - t_start < args.budget - args.game_secs
        for _ in range(args.jobs):
            if not can_launch():
                break
            f = next(it, None)
            if f is None:
                break
            futs[ex.submit(run_game, root, args.unswbc, f, replay_dir, args.nice, args.timeout)] = f
            launched += 1
        while futs:
            for fut in as_completed(list(futs)):
                f = futs.pop(fut)
                rec = fut.result()
                fh.write(json.dumps(rec) + '\n'); fh.flush()
                w = rec['winner']
                print(f"{rec['map']:>16} {rec['a'][:22]:>22} v {rec['b'][:22]:<22} s{rec['seed']} -> {w} r{rec['rounds']} {rec['reason']} ({rec['secs']}s)", flush=True)
                if can_launch():
                    nf = next(it, None)
                    if nf is not None:
                        futs[ex.submit(run_game, root, args.unswbc, nf, replay_dir, args.nice, args.timeout)] = nf
                        launched += 1
                break
    left = len(todo) - launched
    print(f'slice done: launched {launched}, remaining {left}, {time.time() - t_start:.0f}s', flush=True)


def h2h_fixtures(a, b, maps, seeds):
    fx = []
    for s in seeds:
        for m in maps:
            fx.append(dict(map=m, a=a, b=b, seed=s))
            fx.append(dict(map=m, a=b, b=a, seed=s))
    return fx


def pool_fixtures(bot, maps, seeds, zoo=ZOO):
    fx = []
    for s in seeds:
        for m in maps:
            for z in zoo:
                fx.append(dict(map=m, a=bot, b=z, seed=s))
                fx.append(dict(map=m, a=z, b=bot, seed=s))
    return fx


def parse_maps(spec):
    if spec == 'live17':
        return ['live/' + m for m in LIVE17]
    if spec == 'heavy':
        return ['live/' + m for m in HEAVY]
    return spec.split(',')


def report(path, bot=None, opp=None):
    recs = list(load_done(Path(path)).values())
    if not recs:
        print('no results'); return
    bots = sorted({r['a'] for r in recs} | {r['b'] for r in recs})
    if bot is None:
        # the bot appearing in every record
        cands = [x for x in bots if all(x in (r['a'], r['b']) for r in recs)]
        bot = cands[0] if cands else bots[0]
    rows = [r for r in recs if bot in (r['a'], r['b']) and (opp is None or opp in (r['a'], r['b']))]
    by_map = {}
    by_opp = {}
    tot = [0, 0, 0]
    err = 0
    faults = 0
    for r in rows:
        if r['winner'] is None:
            err += 1
            continue
        seat = 'A' if r['a'] == bot else 'B'
        o = r['b'] if seat == 'A' else r['a']
        faults += r.get('faults_A' if seat == 'A' else 'faults_B', 0)
        res = 2 if r['winner'] == 'D' else (0 if r['winner'] == seat else 1)
        tot[res] += 1
        by_map.setdefault(r['map'], [0, 0, 0])[res] += 1
        by_opp.setdefault(o, [0, 0, 0])[res] += 1
    print(f'{bot}: W-L-D {tot[0]}-{tot[1]}-{tot[2]}  ({tot[0] / max(1, sum(tot)):.3f})  errors {err}  own-faults {faults}  n={len(rows)}')
    print('by opponent:')
    for o, v in sorted(by_opp.items(), key=lambda kv: -kv[1][0] / max(1, sum(kv[1]))):
        print(f'  {o:<40} {v[0]:>3}-{v[1]:<3} {v[0] / max(1, sum(v)):.2f}')
    print('by map:')
    for m, v in sorted(by_map.items(), key=lambda kv: kv[1][0] / max(1, sum(kv[1]))):
        print(f'  {m:<24} {v[0]:>3}-{v[1]:<3} {v[0] / max(1, sum(v)):.2f}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument('--unswbc', default='unswbc')
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--budget', type=float, default=0, help='seconds; stop launching when a new game would not finish')
    ap.add_argument('--game-secs', type=float, default=45, help='expected game length for the budget check')
    ap.add_argument('--nice', type=int, default=15)
    ap.add_argument('--timeout', type=int, default=900)
    ap.add_argument('--replays', default=None)
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('--out', required=True); r.add_argument('--fixtures', required=True)
    h = sub.add_parser('h2h'); h.add_argument('--out', required=True); h.add_argument('--a', required=True); h.add_argument('--b', required=True)
    h.add_argument('--maps', default='live17'); h.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3])
    p = sub.add_parser('pool'); p.add_argument('--out', required=True); p.add_argument('--bot', required=True)
    p.add_argument('--maps', default='live17'); p.add_argument('--seeds', type=int, nargs='+', default=[1])
    rp = sub.add_parser('report'); rp.add_argument('path'); rp.add_argument('--bot'); rp.add_argument('--opp')
    args = ap.parse_args()
    if args.cmd == 'report':
        report(args.path, args.bot, args.opp); return
    if args.cmd == 'run':
        fixtures = json.loads(Path(args.fixtures).read_text())
    elif args.cmd == 'h2h':
        fixtures = h2h_fixtures(args.a, args.b, parse_maps(args.maps), args.seeds)
    else:
        fixtures = pool_fixtures(args.bot, parse_maps(args.maps), args.seeds)
    run_fixtures(args, fixtures)


if __name__ == '__main__':
    main()

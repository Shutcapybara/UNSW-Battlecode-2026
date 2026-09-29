#!/usr/bin/env python3
"""Alicia (RL-1) environment: the only way this lane plays games.

A fixture is (policy params, map, seat, seed, opponent). The candidate is always the tunable bot
(bots/alicia-02-tunable unless --bot); the policy is injected as ALICIA_PARAMS in the game's environment (native
bots inherit it; the sandbox passes no environment, so shipped defaults are the constants). Each game goes through
`unswbc run` (the lanes' code path), the replay is decoded in the worker by tools.analysis.features (the BENCHMARKS
extractor), a metric row is appended to a JSONL cache, and the replay is deleted unless --keep.

Resumable: a fixture already in the cache (same params hash, map, seat, seed, opponent, bot) is not replayed.

    python3 tools/alicia/env.py --params '{}' --maps trophy,devil --opps yuna-v05-core --seeds 1001 --cache C.jsonl
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
UNSWBC = os.environ.get('UNSWBC', str(Path(sys.executable).parent / 'unswbc'))
BOT = 'alicia-02-tunable'
RESULT = re.compile(r'team (A|B) wins after (\d+) rounds')
KEEP = ['pearls@25', 'pearls@50', 'pearls@100', 'pearls@150', 'pearls@250', 'pearls@400', 'units@100', 'total@100',
        'units@250', 'total@250', 'births@100', 'births', 'dragon_turns', 'top1_share@100', 'total_share@100',
        'total_share@250', 'pearls@150|rel', 'death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k',
        'death_h2h_ally_per1k', 'death_invalid_per1k', 'death_enemy_body_per1k', 'death_h2h_enemy_per1k',
        'newborn_deaths10_per100', 'deaths_per1k', 'won', 'rounds', 'reason']


def params_env(params: dict) -> str:
    return ';'.join(f'{k}={params[k]!r}' if isinstance(params[k], float) else f'{k}={params[k]}' for k in sorted(params))


def phash(params: dict) -> str:
    return hashlib.sha1(params_env(params).encode()).hexdigest()[:12]


def fkey(fx: dict) -> str:
    return f"{fx.get('bot', BOT)}|{phash(fx['params'])}|{fx['map']}|{fx['seat']}|{fx['seed']}|{fx['opp']}"


def prebuild(bot: str) -> None:
    from unswbc.project import Project
    Project.from_dir(str(ROOT / 'bots' / bot)).compile()


def play(fx: dict, keep_dir: str | None = None) -> dict:
    """one game -> metric row for the candidate's side (plus the opponent's key numbers)."""
    from tools.analysis.features.frame import load
    from tools.analysis.features.extract import extract
    bot = fx.get('bot', BOT)
    a, b = (bot, fx['opp']) if fx['seat'] == 'A' else (fx['opp'], bot)
    env = dict(os.environ)
    if fx['params']:
        env['ALICIA_PARAMS'] = params_env(fx['params'])
    else:
        env.pop('ALICIA_PARAMS', None)
    t0 = time.time()
    tmp = Path(keep_dir or tempfile.gettempdir()) / f"alicia-{os.getpid()}-{hashlib.sha1(fkey(fx).encode()).hexdigest()[:10]}.replay"
    row = {k: fx[k] for k in ('map', 'seat', 'seed', 'opp')}
    row.update(key=fkey(fx), phash=phash(fx['params']), bot=bot, tag=fx.get('tag'))
    try:
        p = subprocess.run([UNSWBC, 'run', '--seed', str(fx['seed']), '--no-logs', '--no-indicator', '--no-draw',
                            '-o', str(tmp), f"maps/{fx['map']}.map", f'bots/{a}', f'bots/{b}'],
                           capture_output=True, text=True, timeout=1800, cwd=ROOT, env=env)
        out = p.stdout + p.stderr
        row['rc'] = p.returncode
        if p.returncode != 0 or not tmp.exists():
            row['error'] = out.strip()[-300:]
            return row
        g = load(str(tmp))
        o = extract(g, {})
        me = next(r for r in o['side_rows'] if r['side'] == fx['seat'])
        them = next(r for r in o['side_rows'] if r['side'] != fx['seat'])
        row['field_map'] = g['map']
        for k in KEEP:
            v = me.get(k)
            row[k] = float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
        for k in ('pearls@100', 'pearls@250', 'units@100', 'total@100', 'total@250'):
            row['opp_' + k] = them.get(k)
    except subprocess.TimeoutExpired:
        row['rc'] = -9; row['error'] = 'timeout'
    except Exception as e:  # a decode failure is recorded, not fatal
        row['rc'] = -1; row['error'] = f'{type(e).__name__}: {e}'[:300]
    finally:
        row['secs'] = round(time.time() - t0, 1)
        if not keep_dir:
            tmp.unlink(missing_ok=True)
    return row


def load_cache(path) -> dict:
    out = {}
    if path and Path(path).exists():
        for line in open(path):
            if line.strip():
                r = json.loads(line)
                if r.get('rc') == 0:
                    out[r['key']] = r
    return out


def run(fixtures: list[dict], cache: str, jobs: int, keep_dir: str | None = None, log=print, retries: int = 1) -> list:
    """play every fixture not yet in the cache; return rows in fixture order (None for a failed fixture)."""
    Path(cache).parent.mkdir(parents=True, exist_ok=True)
    have = load_cache(cache)
    for attempt in range(retries + 1):
        todo = list({fkey(f): f for f in fixtures if fkey(f) not in have}.values())  # identical policies share a game
        if not todo:
            break
        # long maps first so the generation's tail is short
        todo.sort(key=lambda f: f['map'] not in ('schooltime', 'slithery_fight', 'portals', 'big_empty', 'Colosseum'))
        t0, done = time.time(), 0
        with open(cache, 'a') as fh, ProcessPoolExecutor(jobs) as ex:
            futs = [ex.submit(play, f, keep_dir) for f in todo]
            for fut in as_completed(futs):
                r = fut.result(); done += 1
                fh.write(json.dumps(r) + '\n'); fh.flush()
                if r.get('rc') == 0:
                    have[r['key']] = r
                elif log:
                    log(f"  game failed rc={r.get('rc')} {r['key']}: {r.get('error', '')[:160]}")
                if log and (done % 50 == 0 or done == len(todo)):
                    log(f'  {done}/{len(todo)} games, {time.time() - t0:.0f}s')
    return [have.get(fkey(f)) for f in fixtures]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--params', default='{}', help='JSON dict of Params overrides')
    ap.add_argument('--bot', default=BOT)
    ap.add_argument('--maps', required=True)
    ap.add_argument('--opps', required=True)
    ap.add_argument('--seeds', default='1001')
    ap.add_argument('--seats', default='AB')
    ap.add_argument('--cache', required=True)
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument('--keep', help='keep replays in this directory')
    a = ap.parse_args()
    params = json.loads(a.params)
    fx = [dict(params=params, bot=a.bot, map=m, seat=s, seed=int(sd), opp=o)
          for sd in a.seeds.split(',') for m in a.maps.split(',') for o in a.opps.split(',') for s in a.seats]
    prebuild(a.bot)
    for o in set(a.opps.split(',')):
        prebuild(o)
    rows = run(fx, a.cache, a.jobs, a.keep)
    ok = [r for r in rows if r]
    print(f'{len(ok)}/{len(rows)} fixtures have rows in {a.cache}')


if __name__ == '__main__':
    main()

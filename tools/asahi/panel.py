#!/usr/bin/env python3
"""Asahi (Phase 3 Evaluator) panels: run, extract, and record one arm on the standing configuration.

Standing configuration (Phase 3 Evaluator prompt; D-043):
  pool = run_panel.ZOO (8) x run_panel.LIVE_MAPS_M2 (17) x both seats  -> 272 fixtures per seed
  gen  = run_panel.ZOO (8) x GEN (29 maps) x both seats                 -> 464 fixtures per seed
         GEN = maps/new/*.map (20)
             + the maps/var/*_tr twins whose source map did not change in the 2 Oct swap
               (crossroads, devil, portals, queen_of_spades, trauma)
             + maps/m2tr/*_tr: the transposes of maps/live/{autarky,default,dilemma,trophy}, which replace the
               four stale var twins (tools/asahi/twins.py; the generator is tools/ouroboros/mapgen.py's T, which
               reproduces every existing var twin exactly from its pre-swap source).
  An arm is a bot directory (one switch per directory). Runs are keyed by the runtime-source fingerprint:
  build/asahi/runs/<bot>/<fp8>/<panel>/{replays/, index.jsonl, run.json, features/}. Resumable.

    python tools/asahi/panel.py run BOT --panel both --seeds 1 [--jobs 14] [--logs]
    python tools/asahi/panel.py extract BOT --panel both
    python tools/asahi/panel.py fixtures --panel both --seeds 1        # counts only
"""
from __future__ import annotations

import argparse, glob, hashlib, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
from tools.analysis.features import run_panel as R  # noqa: E402

RUNS = ROOT / 'build/asahi/runs'
STALE_VAR = {'autarky', 'default', 'dilemma', 'trophy'}
GEN_MAPS = sorted(
    [f'new/{p.stem}' for p in (ROOT / 'maps/new').glob('*.map')]
    + [f'var/{p.stem}' for p in (ROOT / 'maps/var').glob('*_tr.map') if p.stem[:-3] not in STALE_VAR]
    + [f'm2tr/{p.stem}' for p in (ROOT / 'maps/m2tr').glob('*_tr.map')])
POOL_MAPS = list(R.LIVE_MAPS_M2)
assert len(GEN_MAPS) == 29 and len(POOL_MAPS) == 17, f'panel composition changed: gen {len(GEN_MAPS)}, pool {len(POOL_MAPS)} (run tools/asahi/twins.py)'
HEAVY_MAPS = {'live/slithery_fight', 'live/schooltime', 'live/portals', 'live/australia', 'live/unsw', 'live/islands'}
# Chongqing C7-03 behavioural classes (post-m2 field). Gen maps are their own class.
CLASS = {**{m: 'A' for m in ['devil', 'trophy', 'stripes', 'tower_defense', 'queen_of_spades', 'default', 'autarky']},
         **{m: 'B' for m in ['australia', 'unsw', 'islands', 'maze', 'schooltime']},
         **{m: 'C' for m in ['trauma', 'weakhold', 'dilemma']}, 'slithery_fight': 'D', 'portals': 'E'}


# Queen-keeper panel (D-075 §E, Q-sugawara-01 §4.2): the pool's 17 maps against the two free-lane queen keepers only,
# 68 fixtures per seed. Opponents are untracked copies made by tools/asahi/copybot.py (fingerprints in .asahi-source.json).
QK_OPPS = ['bokuto-04-queen', 'kenma-03-pocket-queen']


def panel_maps(panel: str) -> list[str]:
    return POOL_MAPS if panel in ('pool', 'qk') else GEN_MAPS


def panel_opps(panel: str) -> list[str]:
    return QK_OPPS if panel == 'qk' else list(R.ZOO)


def map_class(mapkey: str) -> str:
    return CLASS.get(mapkey.split('/', 1)[1], '?') if mapkey.startswith('live/') else 'gen'


def fixtures(bot: str, panel: str, seeds: list[int]) -> list[dict]:
    maps = panel_maps(panel)
    out = []
    for seed in seeds:
        for m in maps:
            for opp in panel_opps(panel):
                for a, b, seat in ((bot, opp, 'A'), (opp, bot, 'B')):
                    out.append(dict(panel=panel, map=m, seed=seed, botA=a, botB=b, opp=opp, seat=seat,
                                    game=f"s{seed}__{m.replace('/', '+')}__{a}__{b}"))
    return out


def run_root(bot: str, panel: str) -> Path:
    return RUNS / bot / R.runtime_fingerprint(ROOT / 'bots' / bot)[:8] / panel


def runtime_version(exe: str) -> str:
    p = subprocess.run([exe, '--version'], capture_output=True, text=True)
    return (p.stdout + p.stderr).strip()


def panel_hash(panel: str) -> str:
    maps = panel_maps(panel)
    h = hashlib.sha256()
    for m in maps:
        h.update(m.encode() + b'\0' + (ROOT / 'maps' / f'{m}.map').read_bytes() + b'\0')
    for z in panel_opps(panel):
        h.update(z.encode() + b'\0')
    return h.hexdigest()[:12]


def cmd_run(a):
    seeds = [int(s) for s in a.seeds.split(',')]
    exe = os.environ.get('UNSWBC', str(Path(sys.executable).parent / 'unswbc'))
    jobs = min(a.jobs, int(os.environ.get('ASAHI_MAX_WORKERS', '14')))
    version = runtime_version(exe)
    panels = ['pool', 'gen'] if a.panel == 'both' else [a.panel]
    R.prebuild([a.bot] + sorted({o for p in panels for o in panel_opps(p)}))
    for panel in panels:
        root = run_root(a.bot, panel)
        (root / 'replays').mkdir(parents=True, exist_ok=True)
        fx = fixtures(a.bot, panel, seeds)
        meta = dict(bot=a.bot, fingerprint=R.runtime_fingerprint(ROOT / 'bots' / a.bot), panel=panel,
                    panel_hash=panel_hash(panel), runtime=version, host=os.uname().nodename,
                    maps=panel_maps(panel), zoo=panel_opps(panel), logs=bool(a.logs))
        rj = root / 'run.json'
        old = json.loads(rj.read_text()) if rj.exists() else {}
        if old and (old.get('panel_hash') != meta['panel_hash'] or old.get('runtime') != version):
            raise SystemExit(f'{rj}: panel or runtime changed since earlier games ({old.get("panel_hash")}, '
                             f'{old.get("runtime")}); refusing to mix')
        meta['seeds'] = sorted(set(old.get('seeds', [])) | set(seeds))
        rj.write_text(json.dumps(meta, indent=1))
        todo = [f for f in fx if not (root / 'replays' / (f['game'] + '.replay')).exists()]
        todo.sort(key=lambda f: (f['map'] not in HEAVY_MAPS, f['seed']))
        print(f'[{panel}] {len(fx)} fixtures, {len(todo)} to run, {version}, jobs={jobs}, root={root}', flush=True)
        t0, n, errs = time.time(), 0, 0
        with open(root / 'index.jsonl', 'a') as idx, ThreadPoolExecutor(jobs) as ex:
            futs = [ex.submit(R.run, f, root, exe, version, not a.logs) for f in todo]
            for fut in as_completed(futs):
                n += 1
                try:
                    row = fut.result()
                except Exception as e:  # timeout etc.: the fixture stays missing, never a loss
                    errs += 1
                    print('ERR', type(e).__name__, str(e)[:200], flush=True)
                    continue
                if row:
                    idx.write(json.dumps(row) + '\n'); idx.flush()
                    if row['rc'] != 0:
                        errs += 1
                    if n % 25 == 0 or row['rc'] != 0:
                        print(f"[{panel}] {n}/{len(todo)} {time.time() - t0:.0f}s rc={row['rc']} {row['game']}", flush=True)
        print(f'[{panel}] done {n} in {time.time() - t0:.0f}s, errors {errs}', flush=True)
        if not a.no_extract:
            extract(a.bot, panel, jobs)
            subprocess.run([sys.executable, str(ROOT / 'tools/asahi/queen.py'), a.bot, '--panel', panel, '--jobs', str(jobs)],
                           cwd=ROOT, check=True)


def extract(bot: str, panel: str, jobs: int):
    root = run_root(bot, panel)
    out = root / 'features'
    reps = sorted(glob.glob(str(root / 'replays/*.replay')))
    if (out / 'features.parquet').exists():
        import pandas as pd
        have = set(pd.read_parquet(out / 'features.parquet', columns=['game'])['game'])
        if have >= {Path(p).stem for p in reps}:
            print(f'[{panel}] features up to date ({len(have)} games)', flush=True)
            return
    tmp = root / f'features-tmp-{int(time.time())}'
    subprocess.run([sys.executable, '-m', 'tools.analysis.features', 'extract', str(root / 'replays'),
                    '--index', str(root / 'index.jsonl'), '--out', str(tmp), '--cache', str(root / 'frames'),
                    '--jobs', str(jobs)], cwd=ROOT, check=True)
    if out.exists():
        out.rename(root / f'features-old-{int(time.time())}')
    tmp.rename(out)
    print(f'[{panel}] extracted {len(reps)} -> {out}', flush=True)


def cmd_extract(a):
    for panel in (['pool', 'gen'] if a.panel == 'both' else [a.panel]):
        extract(a.bot, panel, min(a.jobs, int(os.environ.get('ASAHI_MAX_WORKERS', '14'))))


def cmd_fixtures(a):
    seeds = [int(s) for s in a.seeds.split(',')]
    for panel in (['pool', 'gen'] if a.panel == 'both' else [a.panel]):
        fx = fixtures('X', panel, seeds)
        maps = panel_maps(panel)
        print(panel, len(fx), 'fixtures', len(maps), 'maps', panel_hash(panel), maps)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('bot'); r.add_argument('--panel', default='both')
    r.add_argument('--seeds', default='1'); r.add_argument('--jobs', type=int, default=14)
    r.add_argument('--logs', action='store_true', help='keep LOG lines in replays (diagnostic runs)')
    r.add_argument('--no-extract', action='store_true')
    e = sub.add_parser('extract'); e.add_argument('bot'); e.add_argument('--panel', default='both')
    e.add_argument('--jobs', type=int, default=14)
    f = sub.add_parser('fixtures'); f.add_argument('--panel', default='both'); f.add_argument('--seeds', default='1')
    a = ap.parse_args()
    {'run': cmd_run, 'extract': cmd_extract, 'fixtures': cmd_fixtures}[a.cmd](a)


if __name__ == '__main__':
    main()

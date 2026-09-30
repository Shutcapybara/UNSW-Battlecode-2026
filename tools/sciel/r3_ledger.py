#!/usr/bin/env python3
"""R-3 step 1 — the C1-C leak ledger for one local bot's panel run.

Same leak classes and currency as tools/sciel/r3_ledger.py (copied from wt-r3) (definitions on
the F1 per-death rows, overlap allowed): newborn = child died within 10 rounds
of birth; trapped = enclosed at death (<=15 cells reachable in 5 steps, bodies
blocking), suicide excluded; portal = died within 2 cells of a portal;
crowd23 = length <=3 dying into own-side bodies (self / ally_body / h2h_ally).
Currency: length lost per 1k dragon-turns in rounds 0-99, medians over
side-games, pooled and per map — directly comparable with the C1-C reference
table (top 10 / band 55-85 / team 7 live, quoted from
game_stats/efficiency_ledger.json).

    python tools/analysis/r3_ledger.py --features build/zoo/<panel>/features \
        --bot <bot-dir-name> [--out game_stats/runs/r3-<name>-ledger.json]

    python tools/analysis/r3_ledger.py --portal build/zoo/<panel>/replays \
        [--out ...json]     # exact portal steps + deaths within 2 rounds of own step
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.analysis.c1c_ledger import leak_flags, LEAKS, CAUSES  # noqa: E402

WINDOW = 100


def ledger(features_dir: str, bot: str) -> dict:
    d = Path(features_dir)
    feat = pd.read_parquet(d / 'features.parquet')
    rows = feat[feat['bot'] == bot]
    if not len(rows):
        raise SystemExit(f'no side-rows for bot {bot} in {d}')
    ser = pd.read_parquet(d / 'series.parquet', columns=['game', 'side', 'round', 'dragon_turns'])
    dea = leak_flags(pd.read_parquet(d / 'deaths.parquet'))
    games = set(zip(rows['game'], rows['side']))
    ser = ser[pd.Series([(g, s) in games for g, s in zip(ser['game'], ser['side'])], index=ser.index)]
    dt100 = ser[ser['round'] < WINDOW].groupby(['game', 'side'])['dragon_turns'].sum()
    keep = pd.Series([(g, s) in games for g, s in zip(dea['game'], dea['side'])], index=dea.index)
    dea = dea[keep & (dea['round'] < WINDOW)]
    births = rows.set_index(['game', 'side'])['births@100']

    def per_game(flags_col):
        out = {}
        for (g, s), grp in dea.groupby(['game', 'side']):
            dt = dt100.get((g, s), 0)
            if dt > 0:
                out[(g, s)] = 1000 * grp[flags_col].sum() / dt
        return out

    def med_by(map_of, values):
        by = {}
        for k, v in values.items():
            by.setdefault(map_of.get(k, '?'), []).append(v)
        return {m: statistics.median(vs) for m, vs in by.items()}, statistics.median(list(values.values())) if values else None

    map_of = {(r['game'], r['side']): r['map'] for _, r in rows.iterrows()}
    res = {'bot': bot, 'n_side_games': int(len(rows)), 'window': f'0-{WINDOW - 1}', 'per_map': {}}
    pooled = {}
    for lk in LEAKS:
        bymap, pooled_med = med_by(map_of, per_game('lenw_lk_' + lk))
        pooled[f'lk_{lk}_len_per1k'] = round(pooled_med, 1) if pooled_med is not None else None
        res['per_map'][f'lk_{lk}'] = {m: round(v, 1) for m, v in bymap.items()}
    for c in CAUSES:
        bymap, pooled_med = med_by(map_of, per_game('lenw_cause_' + c))
        pooled[f'cause_{c}_len_per1k'] = round(pooled_med, 1) if pooled_med is not None else None
        res['per_map'][f'cause_{c}'] = {m: round(v, 1) for m, v in bymap.items()}
    # counts: newborn deaths per 100 births, wall deaths per 1k dragon-turns (count currency)
    nb = {}
    for (g, s), grp in dea.groupby(['game', 'side']):
        b = births.get((g, s), 0)
        if b > 0:
            nb[(g, s)] = 100 * grp['lk_newborn'].sum() / b
    _, pooled_nb = med_by(map_of, nb)
    pooled['newborn_deaths_per100_births'] = round(pooled_nb, 1) if pooled_nb is not None else None
    cnt_wall = {}
    for (g, s), grp in dea.groupby(['game', 'side']):
        dt = dt100.get((g, s), 0)
        if dt > 0:
            cnt_wall[(g, s)] = 1000 * grp['cause_wall'].sum() / dt
    _, pooled_wall = med_by(map_of, cnt_wall)
    pooled['wall_deaths_per1k'] = round(pooled_wall, 2) if pooled_wall is not None else None
    res['pooled'] = pooled
    return res


# ---------------- portal steps (C1-D instrument on local replays) ----------------
def _portal_one(path: str):
    import os
    from tools.replay_stats.portal_deaths import portal_metrics
    if os.environ.get('R3_PORTAL_CACHE'):
        import tools.replay_stats.portal_deaths as _pd
        _pd.CACHE = Path(os.environ['R3_PORTAL_CACHE'])
    try:
        return portal_metrics(path)
    except Exception as e:
        return dict(error=f'{path}: {type(e).__name__}: {e}')


def portal(replays: str, bot: str | None, jobs: int = 8) -> dict:
    paths = sorted(Path(replays).glob('*.replay'))
    with ProcessPoolExecutor(jobs) as ex:
        results = list(ex.map(_portal_one, [str(p) for p in paths], chunksize=2))
    ok = [r for r in results if 'error' not in r]
    # bot side per game: the replay name encodes the seat order s<seed>__<map>__<botA>__<botB>
    def side_of(p: Path):
        if not bot:
            return None
        parts = p.stem.split('__')
        return 'A' if parts[2] == bot else 'B' if parts[3] == bot else None

    out = {'games': len(ok), 'mismatched_walks': sum(r['mismatched'] for r in ok),
           'verified_walks': sum(r['verified'] for r in ok), 'per_map': {}}
    for label in (('bot',) if bot else ('A', 'B')):
        rows = []
        for p, r in zip(paths, ok):
            s = side_of(p) if bot else label
            if s is None:
                continue
            st = r['steps'][s]
            deaths = [d for d in r['deaths'] if d['team'] == s]
            near = [d for d in deaths if d['near_portal_step']]
            rows.append(dict(map=r['map'], steps=len(st), near=len(near),
                             wall=sum(1 for d in near if d['cause'] == 'wall'),
                             self_=sum(1 for d in near if d['cause'] == 'self'),
                             ally=sum(1 for d in near if d['cause'] == 'ally_body'),
                             h2h=sum(1 for d in near if d['cause'] in ('h2h_enemy', 'h2h_ally')),
                             double=sum(1 for d in near if d['same_pair_double'])))
        agg = {}
        for name, sel in [('ALL', rows)] + [(m, [r for r in rows if r['map'] == m]) for m in sorted({r['map'] for r in rows})]:
            if not sel:
                continue
            ts = sum(r['steps'] for r in sel)
            tn = sum(r['near'] for r in sel)
            agg[name] = dict(games=len(sel), steps_total=ts,
                             steps_per_game_med=statistics.median(r['steps'] for r in sel),
                             near_total=tn, near_per_game_med=statistics.median(r['near'] for r in sel),
                             near_per_100_steps=round(100 * tn / ts, 1) if ts else None,
                             near_wall_self=sum(r['wall'] + r['self_'] for r in sel),
                             same_pair_double=sum(r['double'] for r in sel))
        out['per_map']['bot' if bot else label] = agg
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--features')
    ap.add_argument('--bot')
    ap.add_argument('--portal', help='replays dir; needs --bot to pick the side')
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    res = {}
    if a.features:
        if not a.bot:
            raise SystemExit('--features needs --bot')
        res['ledger'] = ledger(a.features, a.bot)
    if a.portal:
        res['portal'] = portal(a.portal, a.bot, a.jobs)
    if not res:
        ap.error('nothing to do: give --features or --portal')
    print(json.dumps(res, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))
        print(f'wrote {a.out}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())

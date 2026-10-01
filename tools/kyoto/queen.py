"""Kyoto queen/endgame instrument for lane runs (unit 1b).

Row logic adapted from `tools/antioch/queen.py` (antioch, 1 Oct; reused with attribution — the
engine-header read is `tools.antioch.era.header`, the frame decoder is the shared
`tools.analysis.features.frame`). The queen is the team's original lowest-id dragon (antioch:
id parity interleaves teams, so A's queen is id 0 and B's is id 1 at r0; no succession, splits
keep the id and the head end).

  python3 tools/kyoto/queen.py --run kyoto-01-nodevil            # both panels under build/kyoto/runs
  python3 tools/kyoto/queen.py --run kyoto-01-nodevil --panel pool

Writes build/kyoto/queen/<bot>-<panel>.parquet and prints the unit-1b summary:
queen survival to r490, queen length at r490, queen-is-longest rate, death rounds/causes, the
tiebreak level that decided each round-limit game, the engine winner vs frame-inferred winner
(the frame patch has not landed), and the sprint-pricing era check (tools.antioch.era.signals).
"""
from __future__ import annotations

import argparse
import glob
import json
import multiprocessing as mp
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = (100, 250, 400, 490)
GAME = re.compile(r's(\d+)__(.+)__(.+)__(.+)$')


def torus(a, b, W, H):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


def rows_for(path, gid=None):
    from tools.analysis.features import frame as F
    from tools.antioch.era import header
    try:
        h = header(path)
        g = F.decode(path)
    except Exception as e:
        return [dict(game=gid or Path(path).stem, error=f'{type(e).__name__}: {e}')]
    R, ev = g['rounds'], g['events']
    last = len(R) - 1
    teams = sorted({t for t, _ in R[0].values()})
    queen = {t: min(i for i, (tt, _) in R[0].items() if tt == t) for t in teams}
    side_of = {t: s for s, t in zip('AB', teams)}
    out = []
    for t in teams:
        s = side_of[t]
        q = queen[t]
        r_ = dict(game=gid or Path(path).stem, side=s, queen_id=q, last_round=g['last_round'],
                  map=None, seed=None)
        if gid:
            m = GAME.match(gid)
            if m:
                r_['seed'] = int(m.group(1))
                r_['map'] = m.group(2).replace('+', '/')
                r_['seat_bot'] = m.group(3) if s == 'A' else m.group(4)
                r_['opp'] = m.group(4) if s == 'A' else m.group(3)
        for c in CHECK:
            rr = min(c, last)
            own = {i: len(b) for i, (tt, b) in R[rr].items() if tt == t}
            ql = own.get(q, 0)
            r_[f'queen_len@{c}'] = ql
            if c == 490:
                r_['own_units@490'] = len(own)
                r_['own_total@490'] = sum(own.values())
                r_['own_longest@490'] = max(own.values(), default=0)
                r_['queen_rank@490'] = (1 + sum(v > ql for v in own.values())) if ql else None
                r_['queen_is_longest@490'] = int(ql > 0 and ql == r_['own_longest@490'])
                r_['queen_share@490'] = ql / r_['own_total@490'] if r_['own_total@490'] else None
        d = [x for x in ev['deaths'] if x['id'] == q]
        r_['queen_death_round'] = d[0]['round'] if d else None
        r_['queen_death_cause'] = d[0]['cause'] if d else None
        r_['queen_killed_by_enemy'] = int(bool(d) and d[0].get('killer_team') not in (None, t))
        sp = [x for x in ev['splits'] if x['parent'] == q]
        r_['queen_splits'] = len(sp)
        r_['queen_shed'] = sum(x['child_len'] for x in sp)
        mine, theirs = (h['queen_a'], h['longest_a'], h['total_a']), (h['queen_b'], h['longest_b'], h['total_b'])
        if s == 'B':
            mine, theirs = theirs, mine
        r_.update(queen_len_end=mine[0], longest_end=mine[1], total_end=mine[2],
                  opp_queen_len_end=theirs[0], opp_longest_end=theirs[1], opp_total_end=theirs[2],
                  queen_alive_end=int(q in R[last]), end_reason=h['res_reason'],
                  engine_won=1.0 if h['res_winner'] == s else 0.5 if h['res_winner'] == 'draw' else 0.0,
                  frame_won=g['winner'] if isinstance(g.get('winner'), str) else None)
        if h['res_reason'] == 1:
            level = next((k for k, a, b in zip(('queen', 'longest', 'total'), mine, theirs) if a != b), 'tie')
            old = next(((1.0 if a > b else 0.0) for a, b in zip(mine[1:], theirs[1:]) if a != b), 0.5)
            new = next(((1.0 if a > b else 0.0) for a, b in zip(mine, theirs) if a != b), 0.5)
        else:
            level, old, new = 'elimination', None, None
        r_.update(decided_by=level, won_old_rule=old, won_new_rule=new,
                  material_lead_end=(1 if mine[2] > theirs[2] else -1 if mine[2] < theirs[2] else 0))
        out.append(r_)
    return out


def signals_row(path):
    from tools.antioch.era import signals
    try:
        s = signals(path)
        return {k: s.get(k) for k in ('sprint_old', 'sprint_new', 'sprint_amb', 'era', 'sprint_kmax')}
    except Exception as e:
        return {'era': f'error {type(e).__name__}'}


def _job(a):
    return rows_for(*a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', required=True)
    ap.add_argument('--panel', default='both')
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--sprint-check', type=int, default=120, help='replays to run the sprint-era check on')
    a = ap.parse_args()
    import pandas as pd

    panels = ['pool', 'gen'] if a.panel == 'both' else [a.panel]
    outdir = ROOT / 'build/kyoto/queen'
    outdir.mkdir(parents=True, exist_ok=True)
    for panel in panels:
        reps = sorted(glob.glob(str(ROOT / f'build/kyoto/runs/{a.run}/{panel}/replays/*.replay')))
        if not reps:
            print(f'[{panel}] no replays'); continue
        tasks = [(p, Path(p).stem) for p in reps]
        with mp.get_context('fork').Pool(a.jobs) as pool:
            rows = [r for rs in pool.imap_unordered(_job, tasks, chunksize=8) for r in rs]
        df = pd.DataFrame(rows)
        if 'error' in df.columns and df['error'].notna().any():
            print(f"[{panel}] {int(df['error'].notna().sum())} decode errors")
        df = df[df.get('error').isna()] if 'error' in df.columns else df
        out = outdir / f'{a.run}-{panel}.parquet'
        df.to_parquet(out, index=False)

        us = df[df['side'].notna()].copy()
        ours = us[us['game'].str.contains(a.run)] if 'game' in us else us
        print(f'\n=== {a.run} [{panel}] {len(reps)} games, {len(df)} side-rows -> {out.name} ===')
        for name, sub in (('ours', ours), ('opps', us[~us.index.isin(ours.index)])):
            if not len(sub):
                continue
            rl = sub[sub['end_reason'] == 1]
            alive490 = sub['queen_len@490'].gt(0).mean()
            print(f'-- {name}: n={len(sub)}  queen alive@490 {alive490:.3f}  alive_end {sub["queen_alive_end"].mean():.3f}')
            print(f'   queen len@490 (alive only) median {sub.loc[sub["queen_len@490"] > 0, "queen_len@490"].median():.0f} '
                  f'mean {sub.loc[sub["queen_len@490"] > 0, "queen_len@490"].mean():.1f}')
            print(f'   queen is longest@490 {sub["queen_is_longest@490"].mean():.3f}  rank median '
                  f'{sub["queen_rank@490"].median()}  share median {sub["queen_share@490"].median():.3f}')
            dr = sub[sub['queen_death_round'].notna()]
            print(f'   queen death round: median {dr["queen_death_round"].median():.0f} '
                  f'p10 {dr["queen_death_round"].quantile(.1):.0f} p90 {dr["queen_death_round"].quantile(.9):.0f}; '
                  f'enemy {dr["queen_killed_by_enemy"].mean():.2f}')
            print('   causes:', dict(dr['queen_death_cause'].value_counts()))
            print(f'   end reasons: elim {(sub["end_reason"] == 0).mean():.2f} rl {(sub["end_reason"] == 1).mean():.2f}; '
                  f'RL decided by {dict(rl["decided_by"].value_counts())}')
            if len(rl):
                qa = rl['queen_alive_end'].eq(1)
                print(f'   RL games: n={len(rl)} queen alive {qa.mean():.2f} '
                      f'win|alive {rl.loc[qa, "engine_won"].mean():.2f} win|dead {rl.loc[~qa, "engine_won"].mean():.2f}')
                flip = rl[(rl['won_old_rule'] != rl['won_new_rule'])]
                print(f'   RL games where new rule flips old winner: {len(flip)} ({len(flip) / len(rl):.1%})')
        # sprint pricing spot check
        step = max(1, len(reps) // a.sprint_check)
        spot = reps[::step][:a.sprint_check]
        with mp.get_context('fork').Pool(a.jobs) as pool:
            sig = pd.DataFrame(pool.map(signals_row, spot))
        print(f'-- sprint pricing on {len(spot)} replays: era counts {dict(sig["era"].value_counts())}, '
              f'kmax {sig["sprint_kmax"].max() if "sprint_kmax" in sig else "-"}')


if __name__ == '__main__':
    main()

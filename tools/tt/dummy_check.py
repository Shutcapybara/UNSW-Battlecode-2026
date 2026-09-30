"""TT: is the team's unranked play its real bot? (Some teams hide their bot when ranked scrims are not forced and
upload a dummy - reported for Cutlery and possibly others at its university.)

    HB_TEAM=952 HB_BUILD=tt/team952 .venv/bin/python tools/tt/dummy_check.py [--jobs N]

Per game, a behavioural fingerprint from the extracted v5 rows and trajectories: split rate on eligible turns,
self-kill rate, share of forward moves, turns per round (dragons), units / longest / total at r100 and r250, how and
when the game ended. Compares ranked vs unranked games (ranked scrims are forced, so ranked games are the real bot),
flags games whose fingerprint sits outside the ranked distribution, and shows the flagged share by 6-hour window.
Writes build/<HB_BUILD>/dummy_check.parquet and game_stats/runs/<HB_TAG>-dummy-check.json.
"""
import argparse, json, os, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / os.environ.get('HB_BUILD', 'hb1')
TAG = os.environ.get('HB_TAG', 'hb1')
COLS = ['round', 'length', 'split_elig', 'y_family', 'y_first']
FEATS = ['split_rate', 'selfkill_rate', 'fwd_share', 'turns_per_round', 'u100', 'L100', 'T100', 'u250', 'L250', 'T250']


def one(args):
    gid, pq, tj = args
    r = dict(game=gid)
    try:
        d = pd.read_parquet(pq, columns=COLS)
        elig = d.split_elig == 1
        r['split_rate'] = float((d.y_family[elig] == 'split').mean()) if elig.any() else np.nan
        r['selfkill_rate'] = float((~d.y_first.isin(['F', 'R', 'L', 'split'])).mean())
        mv = d.y_first.isin(['F', 'R', 'L'])
        r['fwd_share'] = float((d.y_first[mv] == 'F').mean()) if mv.any() else np.nan
        r['turns_per_round'] = float(len(d) / max(1, d['round'].nunique()))
        t = json.loads(Path(tj).read_text())
        s = t['side']
        tr = {x['round']: x for x in t['traj']}
        for rr in (100, 250):
            if rr in tr:
                r[f'u{rr}'], r[f'L{rr}'], r[f'T{rr}'] = tr[rr][s]['units'], tr[rr][s]['longest'], tr[rr][s]['total']
        r['end_reason'] = t['result'].get('reason')
        r['end_round'] = t['result'].get('rounds')
    except Exception as e:                                   # a game that failed to read is reported, not dropped
        r['error'] = repr(e)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=12)
    a = ap.parse_args()
    g = pd.read_parquet(B / 'games.parquet').query("set == 'corpus'")
    g['game'] = g.game.astype(int)
    work = [(r.game, B / 'v5' / 'corpus' / f'{r.game}.parquet', B / 'v5' / 'corpus' / f'{r.game}.traj.json')
            for r in g.itertuples() if (B / 'v5' / 'corpus' / f'{r.game}.parquet').exists()]
    with Pool(a.jobs) as pool:
        f = pd.DataFrame(pool.map(one, work, chunksize=8))
    d = g[['game', 'ranked', 'won', 't', 'opp', 'map']].merge(f, on='game')
    d.to_parquet(B / 'dummy_check.parquet')
    res = dict(games=len(d), ranked=int(d.ranked.sum()), unranked=int((~d.ranked).sum()))
    comp = {}
    for c in ['won'] + FEATS + ['end_round']:
        x = d.groupby('ranked')[c].agg(['median', 'mean']).astype(float)
        comp[c] = dict(ranked_median=x.loc[True, 'median'] if True in x.index else None,
                       unranked_median=x.loc[False, 'median'] if False in x.index else None,
                       ranked_mean=x.loc[True, 'mean'] if True in x.index else None,
                       unranked_mean=x.loc[False, 'mean'] if False in x.index else None)
    res['ranked_vs_unranked'] = comp
    # outlier score vs the ranked distribution (robust z on each fingerprint feature, max over features)
    R = d[d.ranked]
    z = pd.DataFrame(index=d.index)
    for c in FEATS:
        med = R[c].median()
        mad = (R[c] - med).abs().median() * 1.4826 + 1e-9
        z[c] = ((d[c] - med) / mad).abs()
    d['outlier'] = (z > 4).sum(1) >= 2                       # at least two features far outside ranked play
    res['outlier_share'] = dict(ranked=float(d[d.ranked].outlier.mean()), unranked=float(d[~d.ranked].outlier.mean()))
    t0 = d.t.min().floor('h')
    d['win6h'] = ((d.t - t0) / pd.Timedelta(hours=6)).astype(int)
    by = d.groupby(['win6h', 'ranked']).agg(games=('game', 'size'), outlier=('outlier', 'mean'), won=('won', 'mean'),
                                            split_rate=('split_rate', 'median'), u250=('u250', 'median'))
    res['by_window'] = {f'{int(w)}|{"R" if rk else "U"}': v for (w, rk), v in by.round(3).to_dict('index').items()}
    res['t0'] = str(t0)
    (ROOT / 'game_stats' / 'runs' / f'{TAG}-dummy-check.json').write_text(json.dumps(res, indent=1, default=float))
    print(f"{TAG}: {res['games']} games ({res['ranked']} ranked, {res['unranked']} unranked)")
    print(pd.DataFrame(comp).T.round(3).to_string())
    print('outlier share (≥2 fingerprint features > 4 robust-z from ranked play):', {k: round(v, 3) for k, v in res['outlier_share'].items()})
    print(by.round(3).unstack('ranked').to_string())


if __name__ == '__main__':
    main()

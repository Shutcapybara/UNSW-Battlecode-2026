"""HB-1 Q3: is a training loop still running? Forward/backward transfer over 6-hour windows, behavioural
change-points by hour, and team 62's ladder rating over the same span.

    .venv/bin/python tools/hb1/q3_windows.py [--hours 6]

Uses the Q1 per-decision samples (build/hb1/q1/*.parquet). For consecutive windows i, i+1: a GBT fitted on i
scores i+1 (forward) and one fitted on i+1 scores i (backward); 'within' is a by-game half split inside one
window (the ceiling a static policy would show). An era-set model (27 Sep, submission ids) scores every window.
Writes game_stats/runs/hb1-q3-windows.json.
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'hb1'
OUT = ROOT / 'game_stats' / 'runs' / 'hb1-q3-windows.json'
DEC = ('gate', 'direction', 'alloc')


def gbt(Xa, ya, Xb, yb):
    if len(np.unique(ya)) < 2 or len(yb) == 0:
        return None
    m = Q1._XGB(120).fit(Xa, ya)
    return float((m.predict(Xb) == yb).mean())


def era_samples():
    """Era-set rows for the same decisions (sampled like Q1)."""
    p = B / 'q1' / 'era_samples.pkl'
    if p.exists():
        return pd.read_pickle(p)
    parts = {k: [] for k in Q1.CAP}
    for f in sorted(glob.glob(str(B / 'v5' / 'era' / '*.parquet'))):
        for k, v in Q1._sample(f).items():
            parts[k].append(v)
    out = {k: pd.concat(v, ignore_index=True) for k, v in parts.items()}
    pd.to_pickle(out, p)
    return out


def ladder():
    rows = []
    for f in sorted(glob.glob(str(ROOT / 'public_replays/corpus/ladder/*.json'))):
        t = pd.Timestamp(Path(f).stem.replace('Z', ''), tz='UTC')
        for r in json.load(open(f)):
            if r['id'] == 62:
                rows.append(dict(t=t, elo=r['elo'], rank=r['rank'], wins=r['wins']))
    return pd.DataFrame(rows)


def segment(M, pen):
    """Optimal piecewise-constant segmentation of rows of M (T x k, standardised), cost = SSE + pen per segment."""
    T = len(M)
    cs = np.vstack([np.zeros(M.shape[1]), np.cumsum(M, 0)])
    cs2 = np.concatenate([[0], np.cumsum((M ** 2).sum(1))])

    def cost(i, j):
        n = j - i
        s = cs[j] - cs[i]
        return cs2[j] - cs2[i] - (s ** 2).sum() / n

    F = np.full(T + 1, np.inf); F[0] = -pen
    arg = np.zeros(T + 1, int)
    for j in range(1, T + 1):
        c = [F[i] + cost(i, j) + pen for i in range(j)]
        arg[j] = int(np.argmin(c)); F[j] = c[arg[j]]
    cps, j = [], T
    while j > 0:
        j = arg[j]
        if j > 0:
            cps.append(j)
    return sorted(cps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=int, default=6)
    a = ap.parse_args()
    g = pd.read_parquet(B / 'games.parquet').query("set == 'corpus'")[['game', 't', 'won', 'ranked', 'opp']]
    g['game'] = g.game.astype(int)
    t0 = g.t.min().floor('h')
    g['win'] = ((g.t - t0) / pd.Timedelta(hours=a.hours)).astype(int)
    g['hour'] = ((g.t - t0) / pd.Timedelta(hours=1)).astype(int)
    wins = sorted(g.win.unique())
    res = dict(t0=str(t0), hours=a.hours, windows={int(w): dict(start=str(t0 + pd.Timedelta(hours=a.hours * w)),
               games=int((g.win == w).sum()), win_rate=float(g[g.win == w].won.mean())) for w in wins})
    era = era_samples()
    for k in DEC:
        d = pd.read_parquet(B / 'q1' / f'{k}.parquet')
        d['game'] = d.game.astype(int)
        d = d.merge(g[['game', 'win']], on='game')
        X, y = Q1.xy(k, d)
        Xe, ye = Q1.xy(k, era[k])
        Xe = Xe.reindex(columns=X.columns, fill_value=0)
        w = d.win.to_numpy()
        r = []
        for i in wins:
            a_ = w == i
            row = dict(win=int(i), n=int(a_.sum()))
            gi = np.array(sorted(d.game[a_].unique()))
            half = np.isin(d.game.to_numpy(), gi[::2])
            row['within'] = gbt(X[a_ & half], y[a_ & half], X[a_ & ~half], y[a_ & ~half])
            row['from_era'] = gbt(Xe, ye, X[a_], y[a_])
            if i + 1 in wins:
                b_ = w == i + 1
                row['forward'] = gbt(X[a_], y[a_], X[b_], y[b_])     # fit i, score i+1
                row['backward'] = gbt(X[b_], y[b_], X[a_], y[a_])    # fit i+1, score i
            r.append(row)
            print(k, row, flush=True)
        res[k] = r
        OUT.write_text(json.dumps(res, indent=1, default=str))
    # hourly behaviour metrics -> change-points
    gate = pd.read_parquet(B / 'q1' / 'gate.parquet', columns=['game', 'y_family', 'n_exit_ord'])
    dirn = pd.read_parquet(B / 'q1' / 'direction.parquet', columns=['game', 'y_first', 'cF_block'])
    for d in (gate, dirn):
        d['game'] = d.game.astype(int)
    gate = gate.merge(g[['game', 'hour']], on='game')
    dirn = dirn.merge(g[['game', 'hour']], on='game')
    H = pd.DataFrame(dict(
        open_split=gate[gate.n_exit_ord > 0].assign(s=lambda x: x.y_family == 'split').groupby('hour').s.mean(),
        fwd_when_free=dirn[dirn.cF_block == 0].assign(s=lambda x: x.y_first == 'F').groupby('hour').s.mean(),
        games=g.groupby('hour').size())).dropna()
    H = H[H.games >= 5]
    M = H[['open_split', 'fwd_when_free']].to_numpy()
    M = (M - M.mean(0)) / (M.std(0) + 1e-9)
    cps = segment(M, pen=2 * np.log(len(M)) * M.shape[1])
    res['hourly'] = {int(h): v for h, v in H.round(4).to_dict('index').items()}
    res['change_points'] = [dict(hour=int(H.index[c]), t=str(t0 + pd.Timedelta(hours=int(H.index[c])))) for c in cps]
    L = ladder()
    res['ladder'] = L.assign(t=L.t.astype(str)).to_dict('records')
    OUT.write_text(json.dumps(res, indent=1, default=str))
    print('change-points', res['change_points'])
    print('ladder', L.iloc[[0, len(L) // 2, -1]].to_string())


if __name__ == '__main__':
    main()

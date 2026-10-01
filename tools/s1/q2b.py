"""S1-Q2b: is a map noisy, or complicated? Run from the repo root: python3 tools/s1/q2b.py

Three tests per map (index + ladder; lead/decisiveness from the replay store):
 1. Elo vs map-specific strength. Fit a per-map Bradley-Terry model (one strength per team on that map, L2 ridge, seat
    term) on odd game ids; predict even game ids (and the reverse). Compare held-out log-loss / Brier skill with the
    Elo-gap model fitted the same way. Skill that BT gains over Elo = map-specific ability Elo averages away
    ("complicated"). Skill neither model reaches = noise.
 2. Repeat agreement. The same two teams on the same map within 3 hours (current versions, most likely): how often does
    the same side win both? 1.0 = deterministic, 0.5 = coin flip.
 3. Decisiveness. From the replay store: how well the total-length lead at r50 / r100 / r150 predicts the result (AUC),
    i.e. how early the map's games are decided.
"""
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import numpy as np
import pandas as pd
from scipy.optimize import minimize

S1 = ROOT / 'build' / 's1'
OUT = S1 / 'out' / 'q2b'
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)


def fit_bt(a, b, seat, y, n, ridge=1.0):
    """logit P(A wins) = s[a] - s[b] + c; returns (s, c)"""
    def f(x):
        s, c = x[:n], x[n]
        z = s[a] - s[b] + c
        p = 1 / (1 + np.exp(-z))
        loss = np.sum(np.logaddexp(0, z) - y * z) + 0.5 * ridge * np.sum(s * s)
        e = p - y
        g = np.bincount(a, e, minlength=n) - np.bincount(b, e, minlength=n) + ridge * s
        return loss, np.concatenate([g, [e.sum()]])
    r = minimize(f, np.zeros(n + 1), jac=True, method='L-BFGS-B')
    return r.x[:n], r.x[n]


def fit_elo(gap, y):
    def f(x):
        z = x[0] + x[1] * gap
        p = 1 / (1 + np.exp(-z))
        e = p - y
        return np.sum(np.logaddexp(0, z) - y * z), np.array([e.sum(), (e * gap).sum()])
    return minimize(f, np.zeros(2), jac=True, method='L-BFGS-B').x


def scores(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    ll = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    br = np.mean((p - y) ** 2)
    base = y.mean()
    ll0 = -np.mean(y * np.log(base) + (1 - y) * np.log(1 - base))
    br0 = np.mean((base - y) ** 2)
    acc = np.mean((p > 0.5) == (y == 1))
    return ll, br, 1 - br / br0, 1 - ll / ll0, acc


def test1(g, min_train=8):
    rows = []
    gg = g[(g.result_a != 0.5)].copy()
    gg['half'] = gg.game_id % 2
    allteams = pd.Index(sorted(set(gg.team_a) | set(gg.team_b)))
    gg['ja'], gg['jb'] = allteams.get_indexer(gg.team_a), allteams.get_indexer(gg.team_b)
    for m, d in g.groupby('map'):
        d = d[(d.result_a != 0.5) & d.elo_gap.notna()].copy()
        d['half'] = d.game_id % 2
        teams = pd.Index(sorted(set(d.team_a) | set(d.team_b)))
        d['ia'], d['ib'] = teams.get_indexer(d.team_a), teams.get_indexer(d.team_b)
        pe, pb, po, ys = [], [], [], []
        for h in (0, 1):
            tr, te = d[d.half != h], d[d.half == h]
            # cross-map strength: the same model fitted on the training half of every OTHER map (same data freshness)
            ot = gg[(gg['map'] != m) & (gg.half != h)]
            so, co = fit_bt(ot.ja.values, ot.jb.values, None, ot.result_a.values, len(allteams))
            ntr = pd.concat([tr.team_a, tr.team_b]).value_counts()
            te = te[te.team_a.map(ntr).fillna(0).ge(min_train) & te.team_b.map(ntr).fillna(0).ge(min_train)]
            s, c = fit_bt(tr.ia.values, tr.ib.values, None, tr.result_a.values, len(teams))
            pb.append(1 / (1 + np.exp(-(s[te.ia.values] - s[te.ib.values] + c))))
            ja, jb = allteams.get_indexer(te.team_a), allteams.get_indexer(te.team_b)
            po.append(1 / (1 + np.exp(-(so[ja] - so[jb] + c))))     # other-map strengths + this map's seat term
            gx = tr.elo_gap.clip(-800, 800).values / 100
            k = fit_elo(gx, tr.result_a.values)
            pe.append(1 / (1 + np.exp(-(k[0] + k[1] * te.elo_gap.clip(-800, 800).values / 100))))
            ys.append(te.result_a.values)
        pe, pb, po, ys = np.concatenate(pe), np.concatenate(pb), np.concatenate(po), np.concatenate(ys)
        lo, bo, bso, lso, ao = scores(po, ys)
        le, be, bse, lse, ae = scores(pe, ys)
        lb, bb, bsb, lsb, ab = scores(pb, ys)
        # both: average of the two probabilities (Elo carries cross-map strength, BT carries the map-specific part)
        lc, bc, bsc, lsc, ac = scores((pe + pb) / 2, ys)
        rows.append(dict(map=m, n_test=len(ys), elo_skill=bse, othermaps_bt_skill=bso, thismap_bt_skill=bsb,
                         elo_acc=ae, othermaps_acc=ao, thismap_acc=ab,
                         map_specific_gain=bsb - bso))
    return pd.DataFrame(rows)


def test2(g, hours=3):
    rows = []
    g = g[g.result_a != 0.5].copy()
    g['pair'] = np.where(g.team_a < g.team_b, g.team_a + '|' + g.team_b, g.team_b + '|' + g.team_a)
    g['first'] = np.where(g.team_a < g.team_b, g.team_a, g.team_b)
    g['winner_first'] = np.where(g.result_a == 1, g.team_a == g['first'], g.team_b == g['first']).astype(int)
    g = g.sort_values('started_at')
    for m, d in g.groupby('map'):
        agree = n = 0
        wf = []
        for _, x in d.groupby('pair'):
            if len(x) < 2:
                continue
            t = x.started_at.values
            w = x.winner_first.values
            for i in range(len(x) - 1):
                if (t[i + 1] - t[i]) / np.timedelta64(1, 'h') <= hours:
                    n += 1
                    agree += int(w[i] == w[i + 1])
                    wf.append(w[i])
        # expected agreement if each game were an independent draw at the pair's pooled rate
        rows.append(dict(map=m, repeat_pairs=n, agreement=agree / n if n else np.nan))
    return pd.DataFrame(rows)


def test3():
    import duckdb
    from tools.s1.q import connect
    c = connect('corpus')
    d = c.execute("""select map, round, material_gap_rel as gap, won from series
                     where round in (25, 50, 100, 150) and won != 0.5 and side = 'A'""").df()
    rows = []
    for (m, r), x in d.groupby(['map', 'round']):
        # AUC of the material gap for winning (rank statistic; ties half)
        pos, neg = x[x.won == 1].gap.values, x[x.won == 0].gap.values
        allv = np.concatenate([pos, neg])
        ranks = pd.Series(allv).rank().values
        auc = (ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
        rows.append(dict(map=m, round=r, auc=auc))
    return pd.DataFrame(rows).pivot_table(index='map', columns='round', values='auc').add_prefix('lead_auc_r')


if __name__ == '__main__':
    g = pd.read_parquet(S1 / 'corpus' / 'games.parquet')
    n = g['map'].value_counts()
    g = g[g['map'].isin(n[n >= 500].index)]
    T1, T2 = test1(g), test2(g)
    T = T1.merge(T2, on='map')
    try:
        T3 = test3().reset_index()
        T3['map'] = T3['map'].replace({'Prisoners Dilemma 10': 'Prisoners Dilemma'})
        T3 = T3.groupby('map').mean().reset_index()
        T = T.merge(T3, on='map', how='left')
    except Exception as e:
        print('decisiveness test skipped:', e)
    T = T.sort_values('map_specific_gain')
    OUT.mkdir(parents=True, exist_ok=True)
    T.to_csv(OUT / 'maps.csv', index=False)
    print(T.round(3).to_string(index=False))

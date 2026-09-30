"""HB-1 Q1 follow-up: does memory beyond the v5 row carry signal for direction and the split gate?

    .venv/bin/python tools/hb1/q1_history.py [--jobs N]

Two families, both derived per dragon from its own earlier v5 rows (information the dragon itself had):
  hist_   action history: last K relative actions, turns since it last turned, EWMA turn rate and left/right
          balance, pearls eaten over the last 10 turns.
  trail_  spatial memory as exact decayed recurrences carried in the absolute frame and reported in the current
          egocentric frame (fwd, right): for enemy segments / enemy heads / ally segments / ally heads seen in the
          7x7 window, decayed mass and decayed centroid offset (the density gradient; segment counts weight by
          size), at decay 0.7 and 0.9; the decayed centroid of its own past head positions; EWMAs of the five
          engine echo counts (the protocol gives counts only, no direction); an EWMA of the change in visible
          enemies / allies times the step just taken. Sums shift with the head's own move and reset on a jump
          (portal). Absolute x, y, facing are used only to form these differences, never as features.
The direction and gate rows are re-drawn exactly as q1_decisions (same per-game seed and cap) and fitted with the
same GPU GBT on the same held-out games. Writes game_stats/runs/hb1-q1-history.json.
"""
import argparse, glob, json, sys, os
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / os.environ.get('HB_BUILD', 'hb1')   # HB_BUILD/HB_TEAM/HB_TAG: other teams (lane tt)
TAG = os.environ.get('HB_TAG', 'hb1')
OUT = ROOT / 'game_stats' / 'runs' / f'{TAG}-q1-history.json'
K = 6
CODE = {'F': 0, 'R': 1, 'L': 2, 'split': 3}
FWD = np.array([(0, -1), (1, 0), (0, 1), (-1, 0)], float)     # N E S W, y grows southward
RGT = np.array([(1, 0), (0, 1), (-1, 0), (0, -1)], float)
KINDS = {'eseg': 6, 'ehead': 7, 'aseg': 4, 'ahead': 5}
LAMS = (0.7, 0.9)
ECHO = ('kelp', 'ally', 'allyHead', 'enemy', 'enemyHead')
OFF = [(f, r) for f in range(-3, 4) for r in range(-3, 4) if (f, r) != (0, 0)]


def history(d):
    d = d.sort_values(['dragon', 'round'], kind='stable')
    a = d.y_first.map(CODE).fillna(4).astype(np.int8)
    g = a.groupby(d.dragon)
    h = pd.DataFrame(index=d.index)
    for k in range(1, K + 1):
        h[f'hist_a{k}'] = g.shift(k).fillna(-1)
    turn = a.isin([1, 2]).astype(float)
    lr = np.where(a == 1, 1.0, np.where(a == 2, -1.0, 0.0))
    prev = lambda s: s.groupby(d.dragon).shift(1)
    h['hist_turn_ewm'] = prev(turn.groupby(d.dragon).transform(lambda s: s.ewm(alpha=0.3).mean())).fillna(0)
    h['hist_lr_ewm'] = prev(pd.Series(lr, index=d.index).groupby(d.dragon)
                            .transform(lambda s: s.ewm(alpha=0.3).mean())).fillna(0)
    idx = pd.Series(np.arange(len(d)), index=d.index)
    last_turn = idx.where(turn > 0).groupby(d.dragon).transform(lambda s: s.ffill())
    h['hist_since_turn'] = (idx - prev(last_turn)).fillna(99).clip(upper=99)
    ate = (d.mem_len_delta > 0).astype(float)
    h['hist_eat10'] = ate.groupby(d.dragon).transform(lambda s: s.rolling(10, min_periods=1).sum()).fillna(0)
    return h.loc[d.sort_index().index]


def trail(d):
    """Decayed spatial memory per dragon; returns a frame aligned with d.index."""
    d = d.sort_values(['dragon', 'round'], kind='stable')
    n = len(d)
    occ = np.stack([d[f'g_{f}_{r}_occ'].to_numpy() for f, r in OFF], 1)          # (n, 48)
    offf = np.array([f for f, _ in OFF], float)
    offr = np.array([r for _, r in OFF], float)
    fac = d.facing_abs.to_numpy().astype(int)
    # current-view sums per kind, egocentric -> absolute
    cur = {}
    for k, code in KINDS.items():
        m = occ == code
        sf, sr = (m * offf).sum(1), (m * offr).sum(1)
        cur[k] = (m.sum(1).astype(float), sf[:, None] * FWD[fac] + sr[:, None] * RGT[fac])
    x, y = d.x.to_numpy(), d.y.to_numpy()
    W, H = d.W.to_numpy(), d.H.to_numpy()
    drg, rnd = d.dragon.to_numpy(), d['round'].to_numpy()
    ech = np.stack([d[f'echo_{e}'].to_numpy() for e in ECHO], 1).astype(float)
    vis_e = (cur['eseg'][0] + cur['ehead'][0])
    vis_a = (cur['aseg'][0] + cur['ahead'][0])
    out = {}
    names = []
    for lam in LAMS:
        for k in KINDS:
            names += [f'trail_{k}_m{lam}', f'trail_{k}_f{lam}', f'trail_{k}_r{lam}']
        names += [f'trail_self_f{lam}', f'trail_self_r{lam}']
    names += [f'trail_echo_{e}' for e in ECHO] + ['trail_echo_total', 'trail_grad_e_f', 'trail_grad_e_r',
                                                  'trail_grad_a_f', 'trail_grad_a_r']
    F = np.zeros((n, len(names)))
    st = None
    for i in range(n):
        new = i == 0 or drg[i] != drg[i - 1] or rnd[i] != rnd[i - 1] + 1
        if not new:
            dx = (x[i] - x[i - 1] + W[i] // 2) % W[i] - W[i] // 2
            dy = (y[i] - y[i - 1] + H[i] // 2) % H[i] - H[i] // 2
            new = abs(dx) + abs(dy) > 3                                      # portal jump: memory frame lost
        if new:
            st = {lam: dict(M={k: 0.0 for k in KINDS}, S={k: np.zeros(2) for k in KINDS}, Q=0.0, P=np.zeros(2))
                  for lam in LAMS}
            st['echo'] = ech[i].copy()
            st['ge'], st['ga'] = np.zeros(2), np.zeros(2)
            delta = np.zeros(2)
        else:
            delta = np.array([dx, dy], float)
            st['echo'] = 0.7 * st['echo'] + 0.3 * ech[i]
            st['ge'] = 0.7 * st['ge'] + 0.3 * (vis_e[i] - vis_e[i - 1]) * delta
            st['ga'] = 0.7 * st['ga'] + 0.3 * (vis_a[i] - vis_a[i - 1]) * delta
        fv, rv = FWD[fac[i]], RGT[fac[i]]
        row = []
        for lam in LAMS:
            s = st[lam]
            for k in KINDS:
                m, v = cur[k]
                s['S'][k] = lam * (s['S'][k] - s['M'][k] * delta) + v[i]
                s['M'][k] = lam * s['M'][k] + m[i]
                c = s['S'][k] / s['M'][k] if s['M'][k] > 1e-9 else np.zeros(2)
                row += [s['M'][k], c @ fv, c @ rv]
            s['P'] = lam * (s['P'] - s['Q'] * delta)                          # past heads, relative to now
            s['Q'] = lam * s['Q'] + 1.0
            c = s['P'] / s['Q']
            row += [c @ fv, c @ rv]
        row += list(st['echo']) + [st['echo'].sum(), st['ge'] @ fv, st['ge'] @ rv, st['ga'] @ fv, st['ga'] @ rv]
        F[i] = row
    return pd.DataFrame(F, index=d.index, columns=names).loc[d.sort_index().index]


def _one(path):
    d = pd.read_parquet(path)
    d = pd.concat([d, history(d), trail(d)], axis=1)
    rng = np.random.default_rng(int(Path(path).stem))
    out = {}
    s = d[d.split_elig == 1]                                  # same draw order as q1_decisions._sample
    if len(s) > Q1.CAP['gate']:
        s = s.iloc[np.sort(rng.choice(len(s), Q1.CAP['gate'], replace=False))]
    out['gate'] = s
    s = d[(d.y_family == 'move') & d.y_first.isin(['F', 'R', 'L'])]
    if len(s) > Q1.CAP['direction']:
        s = s.iloc[np.sort(rng.choice(len(s), Q1.CAP['direction'], replace=False))]
    out['direction'] = s
    for k, s in out.items():
        for c in s.columns:
            if not pd.api.types.is_numeric_dtype(s[c]) and c not in Q1.LABELS and c not in Q1.MAP_ID:
                s[c] = s[c].astype(str)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=6)
    a = ap.parse_args()
    paths = {k: B / 'q1' / f'{k}_mem.parquet' for k in ('gate', 'direction')}
    if not all(p.exists() for p in paths.values()):
        parts = {k: [] for k in paths}
        with Pool(a.jobs) as pool:
            for o in pool.imap_unordered(_one, sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet'))), chunksize=4):
                for k, v in o.items():
                    parts[k].append(v)
        for k, p in paths.items():
            pd.concat(parts[k], ignore_index=True).to_parquet(p)
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    for k, p in paths.items():
        d = pd.read_parquet(p)
        ref = pd.read_parquet(B / 'q1' / f'{k}.parquet', columns=['game', 'dragon', 'round'])
        key = lambda x: x[['game', 'dragon', 'round']].astype(int).sort_values(['game', 'dragon', 'round']).to_numpy()
        same = len(ref) == len(d) and bool((key(ref) == key(d)).all())
        te = d.game.astype(int).isin(test_games).to_numpy()
        X, y = Q1.xy(k, d)
        hc = [c for c in X.columns if c.startswith('hist_')]
        tc = [c for c in X.columns if c.startswith('trail_')]
        base = [c for c in X.columns if c not in hc and c not in tc]
        r = dict(rows_match_q1_sample=same, n_train=int((~te).sum()), n_test=int(te.sum()), hist_cols=hc, trail_cols=tc)
        for name, cols in (('v5', base), ('v5+hist', base + hc), ('v5+trail', base + tc), ('v5+hist+trail', base + hc + tc)):
            m, pr = Q1.fit_gbt(X.loc[~te, cols], y[~te], X.loc[te, cols], y[te])
            r[name] = Q1.score(pr, m.classes_, y[te])
            print(k, name, r[name], flush=True)
            if name == 'v5+hist+trail':
                imp = m.m.get_booster().get_score(importance_type='total_gain')
                fn = dict(zip([f'f{i}' for i in range(len(cols))], cols))
                r['top_gain'] = sorted(((fn.get(f, f), g) for f, g in imp.items()), key=lambda t: -t[1])[:25]
        m, pr = Q1.fit_mlp(X.loc[~te], y[~te], X.loc[te], y[te])
        r['mlp_v5+hist+trail'] = Q1.score(pr, m[1], y[te])
        print(k, 'mlp_v5+hist+trail', r['mlp_v5+hist+trail'], flush=True)
        res[k] = r
        OUT.write_text(json.dumps(res, indent=1))
    for k in paths:
        r = res[k]
        print(k, ' '.join(f"{n}={r[n]['acc']:.4f}" for n in ('v5', 'v5+hist', 'v5+trail', 'v5+hist+trail')),
              f"mlp={r['mlp_v5+hist+trail']['acc']:.4f}", 'rows_match', r['rows_match_q1_sample'])


if __name__ == '__main__':
    main()

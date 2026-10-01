"""Verso: hand-built memory features for the direction prior, with the memory length swept (lead, 1 Oct).

    .venv/bin/python tools/verso/memfeat.py build TEAM [--games 1200] [--cap 1200] [--jobs 12]
    .venv/bin/python tools/verso/memfeat.py fit   TEAM [--rounds 1500]

Question: a quarter of the top teams' moves are not determined by their current 7x7 view (direction from the v5
row: cheji bt 0.77, Stockfish 0.79, Heartbreaker 0.86). Do decayed densities of the dragons a dragon has seen, its
echo / message history, and a rolling window of its own path and actions recover them — and at what memory length?
Everything is computed per dragon from its own earlier rows (information it had), in its egocentric frame; absolute
x / y / facing are used only to form differences, never as features.

Families (each at several lengths, so the length is validated, not assumed):
  dens_<kind>_<lam>   EWMA (decay lam per turn) of the visible parts of each kind — enemy segments, enemy heads,
                      ally segments, ally heads; segments count once each, so a dragon weighs by its visible
                      length — as mass plus the decayed centroid (forward, right) relative to the head now
  sonar_<lam>         EWMA of the five echo counts (sonar returns: kelp, ally, ally head, enemy, enemy head) and of
                      messages received
  path_<W>            the last W turns of the dragon's own path and actions: counts of F / R / L / split, left-right
                      balance, pearls eaten, net displacement / W (straightness), distinct cells / W (revisits), turns
                      since the last turn
Lengths: lam in {0.5, 0.7, 0.9, 0.97}; W in {4, 8, 16, 32}.
build writes build/verso/memfeat/<team>.parquet (sampled move rows + all features); fit trains the same GPU GBT
on v5 alone and v5 + each family / length on the same rows, held-out by game, and writes
game_stats/runs/verso-memfeat-<team>.json.
"""
from __future__ import annotations

import argparse, glob, json, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import train_heads as T

OUT = C.B / 'memfeat'
LAMS = (0.5, 0.7, 0.9, 0.97)
WINS = (4, 8, 16, 32)
FWD = np.array([(0, -1), (1, 0), (0, 1), (-1, 0)], float)      # N E S W; y grows southward
RGT = np.array([(1, 0), (0, 1), (-1, 0), (0, -1)], float)
KINDS = {'eseg': 6, 'ehead': 7, 'aseg': 4, 'ahead': 5}
OFF = [(f, r) for f in range(-3, 4) for r in range(-3, 4) if (f, r) != (0, 0)]
ECHO = ('kelp', 'ally', 'allyHead', 'enemy', 'enemyHead')
ROOTS = {62: C.ROOT / 'build/hb1', 70: C.ROOT.parent / 'wt-tt/build/tt/team70', 206: C.ROOT.parent / 'wt-tt/build/tt/team206'}


def features(d):
    """d: one game's v5 rows (all of them, every dragon). -> DataFrame of memory features, aligned with d."""
    d = d.sort_values(['dragon', 'round'], kind='stable')
    n = len(d)
    occ = np.stack([d[f'g_{f}_{r}_occ'].to_numpy() for f, r in OFF], 1)
    offf = np.array([f for f, _ in OFF], float); offr = np.array([r for _, r in OFF], float)
    fac = d.facing_abs.to_numpy().astype(int)
    cur = {}
    for k, code in KINDS.items():
        m = occ == code
        cur[k] = (m.sum(1).astype(float), (m * offf).sum(1)[:, None] * FWD[fac] + (m * offr).sum(1)[:, None] * RGT[fac])
    x, y = d.x.to_numpy(), d.y.to_numpy()
    W, H = d.W.to_numpy(), d.H.to_numpy()
    drg, rnd = d.dragon.to_numpy(), d['round'].to_numpy()
    pm = np.stack([d[f'g_{f}_{r}_pearl'].to_numpy() for f, r in OFF], 1) > 0
    cur['pearl'] = (pm.sum(1).astype(float), (pm * offf).sum(1)[:, None] * FWD[fac] + (pm * offr).sum(1)[:, None] * RGT[fac])
    son = np.concatenate([np.stack([d[f'echo_{e}'].to_numpy() for e in ECHO], 1), d.n_msgs.to_numpy()[:, None]], 1).astype(float)
    act = d.y_first.map({'F': 0, 'R': 1, 'L': 2, 'split': 3}).fillna(4).to_numpy().astype(int)
    ate = (d.mem_len_delta.to_numpy() > 0).astype(float)
    names = []
    for lam in LAMS:
        for k in KINDS:
            names += [f'dens_{k}_m_{lam}', f'dens_{k}_f_{lam}', f'dens_{k}_r_{lam}']
        names += [f'sonar_{e}_{lam}' for e in ECHO] + [f'sonar_msgs_{lam}']
        names += [f'pearl_m_{lam}', f'pearl_f_{lam}', f'pearl_r_{lam}']
    for w in WINS:
        names += [f'path_nF_{w}', f'path_nR_{w}', f'path_nL_{w}', f'path_nS_{w}', f'path_lr_{w}', f'path_eat_{w}',
                  f'path_straight_{w}', f'path_distinct_{w}']
    names += ['path_since_turn']
    for ttl in (20, 40, 80):
        names += [f'known_n_{ttl}', f'known_d_{ttl}', f'known_f_{ttl}', f'known_r_{ttl}']
    F = np.zeros((n, len(names)), np.float32)
    st = None
    for i in range(n):
        new = i == 0 or drg[i] != drg[i - 1] or rnd[i] != rnd[i - 1] + 1
        if not new:
            dx = (x[i] - x[i - 1] + W[i] // 2) % W[i] - W[i] // 2
            dy = (y[i] - y[i - 1] + H[i] // 2) % H[i] - H[i] // 2
            jump = abs(dx) + abs(dy) > 3          # portal: the spatial memory frame is lost
        if new:
            st = dict(M={(lam, k): 0.0 for lam in LAMS for k in list(KINDS) + ['pearl']},
                      S={(lam, k): np.zeros(2) for lam in LAMS for k in list(KINDS) + ['pearl']}, known={},
                      son={lam: son[i].copy() for lam in LAMS}, pos=[np.zeros(2)], acts=[], ate=[], since=99)
            delta = np.zeros(2)
        else:
            delta = np.zeros(2) if jump else np.array([dx, dy], float)
            if jump:
                for key in st['M']:
                    st['M'][key] = 0.0; st['S'][key] = np.zeros(2)
            for lam in LAMS:
                st['son'][lam] = lam * st['son'][lam] + (1 - lam) * son[i]
            st['pos'].append(st['pos'][-1] + delta)
        fv, rv = FWD[fac[i]], RGT[fac[i]]
        row = []
        for lam in LAMS:
            for k in KINDS:
                m, v = cur[k]
                key = (lam, k)
                st['S'][key] = lam * (st['S'][key] - st['M'][key] * delta) + v[i]
                st['M'][key] = lam * st['M'][key] + m[i]
                c = st['S'][key] / st['M'][key] if st['M'][key] > 1e-9 else np.zeros(2)
                row += [st['M'][key], c @ fv, c @ rv]
            row += list(st['son'][lam])
            m, v = cur['pearl']
            key = (lam, 'pearl')
            st['S'][key] = lam * (st['S'][key] - st['M'][key] * delta) + v[i]
            st['M'][key] = lam * st['M'][key] + m[i]
            c = st['S'][key] / st['M'][key] if st['M'][key] > 1e-9 else np.zeros(2)
            row += [st['M'][key], c @ fv, c @ rv]
        # the path window uses actions *before* this turn (the label is this turn's action)
        A, E, P = st['acts'], st['ate'], st['pos']
        for w in WINS:
            a = A[-w:]
            row += [a.count(0), a.count(1), a.count(2), a.count(3), (a.count(1) - a.count(2)) / max(1, len(a)),
                    sum(E[-w:])]
            p = P[-(w + 1):]
            disp = np.abs(p[-1] - p[0]).sum() if len(p) > 1 else 0.0
            row += [disp / max(1, len(p) - 1), len({(round(q[0]), round(q[1])) for q in p}) / len(p)]
        row += [st['since']]
        # remembered pearls, in the dragon's own path frame (positions relative to where it started this sequence;
        # cleared on a portal jump). A cell seen empty forgets its pearl.
        here = st['pos'][-1]
        if not new and jump:
            st['known'] = {}
        for j, (f_, r_) in enumerate(OFF):
            cell = (round(here[0] + f_ * fv[0] + r_ * rv[0]), round(here[1] + f_ * fv[1] + r_ * rv[1]))
            if pm[i, j]:
                st['known'][cell] = rnd[i]
            elif cell in st['known']:
                del st['known'][cell]
        for ttl in (20, 40, 80):
            ks = [(np.array(c_, float) - here, rnd[i] - r0) for c_, r0 in st['known'].items() if rnd[i] - r0 <= ttl]
            if ks:
                dist = [np.abs(v_).sum() for v_, _ in ks]
                j = int(np.argmin(dist)); v_ = ks[j][0]
                row += [len(ks), dist[j], v_ @ fv, v_ @ rv]
            else:
                row += [0, 99, 0, 0]
        F[i] = row
        st['acts'].append(int(act[i])); st['ate'].append(ate[i])
        st['since'] = 0 if act[i] in (1, 2) else min(99, st['since'] + 1)
    return pd.DataFrame(F, index=d.index, columns=names).loc[d.sort_index().index]


def _one(args):
    path, cap, feats = args
    d = pd.read_parquet(path)
    f = features(d)
    keep = ((d.y_family == 'move') & d.y_first.isin(C.RELS)).to_numpy()
    idx = np.flatnonzero(keep)
    if cap and len(idx) > cap:
        idx = np.sort(np.random.default_rng(int(Path(path).stem) + 7).choice(idx, cap, replace=False))
    out = pd.concat([d.iloc[idx][feats].reset_index(drop=True), f.iloc[idx].reset_index(drop=True)], axis=1)
    out['y'] = d.iloc[idx].y_first.map({'F': 0, 'R': 1, 'L': 2}).to_numpy()
    out['game'] = int(Path(path).stem)
    return out


def cmd_build(a):
    root = ROOTS[a.team]
    G = pd.read_parquet(root / 'games.parquet')
    G = G[G.set == 'corpus']
    games = sorted(G.game.astype(int))
    rng = np.random.default_rng(C.SEED)
    pick = sorted(rng.choice(games, min(a.games, len(games)), replace=False).tolist())
    _, names = C.schema('verso-p4-platform')
    feats = [n for n, b in zip(names, C.block(names)) if b == 'v5']
    t0 = time.time()
    with Pool(a.jobs) as pool:
        parts = pool.map(_one, [(str(root / 'v5' / 'corpus' / f'{g}.parquet'), a.cap, feats) for g in pick], chunksize=2)
    OUT.mkdir(parents=True, exist_ok=True)
    D = pd.concat(parts, ignore_index=True)
    D.to_parquet(OUT / f'{a.team}.parquet')
    print(f'team {a.team}: {len(pick)} games, {len(D)} rows, {time.time() - t0:.0f}s')


def cmd_fit(a):
    import xgboost as xgb
    D = pd.read_parquet(OUT / f'{a.team}.parquet')
    games = sorted(D.game.unique())
    te_g = C.holdout(games)
    te = D.game.isin(te_g).to_numpy()
    y = D.y.to_numpy()
    va = (~te) & (np.random.default_rng(C.SEED).random(len(D)) < 0.1)
    tr = (~te) & ~va
    _, names = C.schema('verso-p4-platform')
    base = [n for n, b in zip(names, C.block(names)) if b == 'v5']
    fam = lambda p: [c for c in D.columns if c.startswith(p)]
    sets = {'v5': base}
    for lam in LAMS:
        sets[f'+dens {lam}'] = base + [c for c in fam('dens_') if c.endswith(f'_{lam}')]
        sets[f'+sonar {lam}'] = base + [c for c in fam('sonar_') if c.endswith(f'_{lam}')]
    for w in WINS:
        sets[f'+path {w}'] = base + [c for c in fam('path_') if c.endswith(f'_{w}')] + ['path_since_turn']
    for lam in LAMS:
        sets[f'+pearl {lam}'] = base + [c for c in fam('pearl_') if c.endswith(f'_{lam}')]
    for ttl in (20, 40, 80):
        sets[f'+known {ttl}'] = base + [c for c in fam('known_') if c.endswith(f'_{ttl}')]
    sets['+pearl+known'] = base + fam('pearl_') + fam('known_')
    sets['+all'] = base + fam('dens_') + fam('sonar_') + fam('path_') + fam('pearl_') + fam('known_')
    res = dict(team=a.team, games=len(games), test_games=len(te_g), n_train=int(tr.sum()), n_test=int(te.sum()))
    for name, cols in sets.items():
        X = D[cols].to_numpy(np.float32)
        b = T.fit_softmax(X[tr], y[tr], X[va], y[va], cols, 63, a.rounds)
        p = b.predict(xgb.DMatrix(X[te], feature_names=cols))
        res[name] = dict(acc=float((p.argmax(1) == y[te]).mean()), rounds=int(b.num_boosted_rounds()))
        print(a.team, name, res[name], flush=True)
        if name == '+all':
            g = b.get_score(importance_type='total_gain'); tot = sum(g.values())
            res['top_gain_all'] = sorted(((k, round(v / tot, 4)) for k, v in g.items()), key=lambda t: -t[1])[:30]
    p = C.ROOT / 'game_stats' / 'runs' / f'verso-memfeat-{a.team}.json'
    p.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v['acc'] if isinstance(v, dict) and 'acc' in v else v for k, v in res.items() if k != 'top_gain_all'}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('team', type=int); b.add_argument('--games', type=int, default=1200)
    b.add_argument('--cap', type=int, default=1200); b.add_argument('--jobs', type=int, default=12)
    f = sub.add_parser('fit'); f.add_argument('team', type=int); f.add_argument('--rounds', type=int, default=1500)
    a = ap.parse_args()
    {'build': cmd_build, 'fit': cmd_fit}[a.cmd](a)


if __name__ == '__main__':
    main()

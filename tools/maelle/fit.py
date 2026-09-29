#!/usr/bin/env python3
"""Maelle supervised fits (SF-1 Part 2, fit.py): a prior for each feature weight before the paired scan refines it.

    PY=.venv/bin/python
    # (a) corpus: top-30 sides' target choices. Each such dragon's own grids are rebuilt from its 7x7 views (same
    #     update rules, decays and saturation scales as state.hpp); a decision is a round where the dragon knows >= 2
    #     pearls within BFS 20 and eats one of them within 15 rounds; the label is the one it ate first.
    $PY tools/maelle/fit.py corpus-extract [--corpus DIR] [--top 30] [--jobs 4] [--limit N]
    $PY tools/maelle/fit.py clogit [--features food,ally,enemy,threat,death,food_sat] [--winners-only]
    # (b) self-play: Poisson regression of pearls eaten over the next 20 rounds by the chosen target's features
    #     (maelle-02 dumps, offset by the base log-score), and a logistic model of death within 20 rounds
    $PY tools/maelle/fit.py selfplay --dumps build/maelle/dumps/maelle-02-features/pool

Conditional logit: P(i) ∝ exp(b_t * steps + b_vis * visible + sum_k b_k f_k(i) + controls). The bot's target score
is log-linear, log(value * gamma^t) + sum_k w_k f_k, so the implied weight is w_k = b_k * log(gamma) / b_t
(gamma = 0.93): the corpus's own trade of features against distance, in the bot's units.
"""
from __future__ import annotations

import argparse, glob, json, math, os, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'build/maelle/fit'
GAMMA = 0.93
# state.hpp defaults (maelle-02)
LAM = dict(food=0.98, ally=0.90, enemy=0.90, threat=0.80, death=0.97)
SCALE = dict(food=0.05, ally=0.30, enemy=0.30, threat=0.30, death=0.02)
GRIDS = ['food', 'ally', 'enemy', 'threat', 'death']
BLUR, THREAT_K, VIS, TTL = 2, 2, 3, 40
FEATS = ['food', 'ally', 'enemy', 'threat', 'death', 'food_sat', 'food_clock', 'ally_clock', 'enemy_clock']


def default_corpus():
    for p in (ROOT / 'public_replays/corpus', ROOT.parent / 'wt-hb1/public_replays/corpus',
              ROOT.parent / 'UNSW-Battlecode-2026/public_replays/corpus'):
        if (p / 'index.jsonl').exists():
            return p
    raise SystemExit('no corpus found')


def top_teams(corpus, top):
    snaps = sorted(glob.glob(str(corpus / 'ladder/*.json')))
    lad = json.load(open(snaps[-1]))
    return {r['id'] for r in lad if r['rank'] <= top}


def box_mean(G, W, H, r=BLUR):
    """(k, H, W) -> torus box mean over (2r+1)^2"""
    S = np.zeros_like(G)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            S += np.roll(np.roll(G, dy, axis=1), dx, axis=2)
    return S / (2 * r + 1) ** 2


def extract_game(args):
    path, side = args
    sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))
    from frame import decode
    try:
        g = decode(path)
    except Exception as e:  # noqa: BLE001
        return path, side, None, repr(e)[:200]
    W, H, nbr = g['W'], g['H'], g['nbr']
    NC = W * H
    cidx = lambda c: c[1] * W + c[0]
    # adjacency for BFS (cell index -> list of destinations through open edges and portals)
    adj = [[] for _ in range(NC)]
    for c, ds in nbr.items():
        adj[cidx(c)] = [cidx(d) for d in ds if d is not None]
    view_off = [(dx, dy) for dy in range(-VIS, VIS + 1) for dx in range(-VIS, VIS + 1)]
    lam = np.array([LAM[k] for k in GRIDS], np.float32)[:, None]
    grids, known = {}, {}          # per dragon: (5, NC) float32; {cell: last seen round}
    eats = {}
    for e in g['events']['eats']:
        eats.setdefault(e['id'], []).append((e['round'], cidx(e['cell'])))
    deaths_by_round = {}
    for d in g['events']['deaths']:
        deaths_by_round.setdefault(d['round'], []).append(cidx(d['head']))
    rows = []
    last = g['last_round']
    for r in range(0, last + 1):
        snap, pearls = g['rounds'][r], g['pearls'][r]
        pearl_idx = {cidx(c) for c in pearls}
        mine = {i: b for i, (t, b) in snap.items() if t == side and b}
        # all parts in the world this round
        parts = [(cidx(c), t == side, k == 0, i) for i, (t, b) in snap.items() for k, c in enumerate(b)]
        part_at = {}
        for c, al, hd, i in parts:
            part_at.setdefault(c, []).append((al, hd, i))
        prev_deaths = deaths_by_round.get(r - 1, [])
        for i in list(grids):
            if i not in mine:
                del grids[i]; known.pop(i, None)
        for i, body in mine.items():
            G = grids.get(i)
            if G is None:
                G = grids[i] = np.zeros((5, NC), np.float32); known[i] = {}
            else:
                G *= lam
            hx, hy = body[0]
            head = cidx(body[0])
            K = known[i]
            enemy_heads = []
            for dx, dy in view_off:
                c = ((hy + dy) % H) * W + (hx + dx) % W
                if c in pearl_idx:
                    if c not in K:
                        G[0, c] += 1.0
                    K[c] = r
                else:
                    K.pop(c, None)
                for al, hd, j in part_at.get(c, ()):
                    if j == i:
                        continue
                    G[1 if al else 2, c] += 1.0
                    if hd and not al:
                        enemy_heads.append(c)
                if c in prev_deaths:
                    G[4, c] += 1.0
            for c in enemy_heads:
                ex, ey = c % W, c // W
                for dy in range(-THREAT_K, THREAT_K + 1):
                    for dx in range(-THREAT_K, THREAT_K + 1):
                        G[3, ((ey + dy) % H) * W + (ex + dx) % W] += 1.0
            for c in [c for c, s in K.items() if r - s > TTL]:
                del K[c]
            # decision: >= 2 known pearls within BFS 20, eats one of them first within 15 rounds
            if len(K) < 2 or r >= last - 15:
                continue
            fut = next(((er, ec) for er, ec in eats.get(i, ()) if r <= er <= r + 15), None)
            if fut is None or fut[1] not in K:
                continue
            dist = {head: 0}
            q = [head]
            for c in q:
                if dist[c] >= 20:
                    continue
                for n in adj[c]:
                    if n not in dist:
                        dist[n] = dist[c] + 1; q.append(n)
            cands = [c for c in K if c in dist and c != head]
            if len(cands) < 2 or fut[1] not in cands:
                continue
            B = box_mean(G.reshape(5, H, W), W, H).reshape(5, NC)
            clock = r / 500.0
            ally_heads = [c for c, al, hd, j in parts if al and hd and j != i]
            enemy_heads_all = [c for c, al, hd, j in parts if (not al) and hd]
            for c in cands:
                fo, al_, en = (B[0, c] / (B[0, c] + SCALE['food']) if B[0, c] > 0 else 0.0,
                               B[1, c] / (B[1, c] + SCALE['ally']) if B[1, c] > 0 else 0.0,
                               B[2, c] / (B[2, c] + SCALE['enemy']) if B[2, c] > 0 else 0.0)
                th = B[3, c] / (B[3, c] + SCALE['threat']) if B[3, c] > 0 else 0.0
                de = B[4, c] / (B[4, c] + SCALE['death']) if B[4, c] > 0 else 0.0
                # base-score controls: an ally or enemy head strictly nearer (torus Manhattan, visible heads only)
                def tman(a, b):
                    dx = abs(a % W - b % W); dy = abs(a // W - b // W)
                    return min(dx, W - dx) + min(dy, H - dy)
                d = dist[c]
                vis_ally = [h for h in ally_heads if max(min(abs(h % W - hx), W - abs(h % W - hx)),
                                                         min(abs(h // W - hy), H - abs(h // W - hy))) <= VIS]
                vis_en = [h for h in enemy_heads_all if max(min(abs(h % W - hx), W - abs(h % W - hx)),
                                                            min(abs(h // W - hy), H - abs(h // W - hy))) <= VIS]
                rows.append((r, i, c, int(c == fut[1]), d, int(K[c] == r), int(any(tman(h, c) < d for h in vis_ally)),
                             int(any(tman(h, c) < d for h in vis_en)), fo, al_, en, th, de, fo * al_, fo * clock,
                             al_ * clock, en * clock, len(body)))
    return path, side, rows, None


COLS = ['rnd', 'dragon', 'cell', 'chosen', 'steps', 'visible', 'ally_nearer', 'enemy_nearer'] + FEATS + ['len']


def cmd_corpus_extract(a):
    import pandas as pd
    from concurrent.futures import ProcessPoolExecutor
    corpus = Path(a.corpus) if a.corpus else default_corpus()
    top = top_teams(corpus, a.top)
    have = {p.stem for p in (corpus / 'replays').glob('*.replay')}
    jobs = []
    for line in open(corpus / 'index.jsonl'):
        r = json.loads(line)
        if str(r['game_id']) not in have or r.get('status') != 'completed':
            continue
        for side, team in (('A', r['team_a']), ('B', r['team_b'])):
            if team in top:
                jobs.append((str(corpus / 'replays' / f"{r['game_id']}.replay"), side, r['game_id'], team,
                             r['winner'] == side.lower(), r['map_name']))
    if a.limit:
        jobs = jobs[:a.limit]
    print(f'{len(jobs)} top-{a.top} sides in {len({j[0] for j in jobs})} games', flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    frames = []
    meta = {(j[0], j[1]): j for j in jobs}
    with ProcessPoolExecutor(a.jobs) as ex:
        for k, (path, side, rows, err) in enumerate(ex.map(extract_game, [(j[0], j[1]) for j in jobs], chunksize=1), 1):
            if err:
                print('  skip', path, err); continue
            j = meta[(path, side)]
            if rows:
                df = pd.DataFrame(rows, columns=COLS)
                df['game'] = j[2]; df['side'] = side; df['team'] = j[3]; df['won'] = j[4]; df['map'] = j[5]
                frames.append(df)
            if k % 20 == 0:
                print(f'  {k}/{len(jobs)} sides, {sum(len(f) for f in frames)} rows', flush=True)
    D = pd.concat(frames, ignore_index=True)
    D.to_parquet(OUT / 'corpus_targets.parquet')
    print(f'wrote {len(D)} rows, {D.groupby(["game", "side", "dragon", "rnd"]).ngroups} decisions')


def clogit(X, groups, chosen, l2=1e-3):
    """conditional logit by L-BFGS. X (n, k), groups: decision id per row (sorted), chosen: 0/1."""
    from scipy.optimize import minimize
    starts = np.flatnonzero(np.r_[True, groups[1:] != groups[:-1]])
    def f(b):
        u = X @ b
        mx = np.maximum.reduceat(u, starts)
        e = np.exp(u - np.repeat(mx, np.diff(np.r_[starts, len(u)])))
        Z = np.add.reduceat(e, starts)
        p = e / np.repeat(Z, np.diff(np.r_[starts, len(u)]))
        ll = (u[chosen == 1] - mx - np.log(Z)).sum()
        g = X[chosen == 1].sum(0) - (p[:, None] * X).sum(0)
        return -ll + l2 * b @ b, -g + 2 * l2 * b
    r = minimize(f, np.zeros(X.shape[1]), jac=True, method='L-BFGS-B')
    return r.x, -r.fun


def cmd_clogit(a):
    import pandas as pd
    D = pd.read_parquet(a.data)
    if a.winners_only:
        D = D[D['won']]
    feats = a.features.split(',')
    cols = ['steps', 'visible', 'ally_nearer', 'enemy_nearer'] + feats
    D = D.sort_values(['game', 'side', 'dragon', 'rnd']).reset_index(drop=True)
    gid = D.groupby(['game', 'side', 'dragon', 'rnd']).ngroup().to_numpy()
    order = np.argsort(gid, kind='stable')
    D = D.iloc[order].reset_index(drop=True); gid = gid[order]
    X = D[cols].to_numpy(float); y = D['chosen'].to_numpy()
    b, ll = clogit(X, gid, y)
    # bootstrap by game
    games = D['game'].unique()
    rng = np.random.default_rng(3)
    idx_by_game = {gm: np.flatnonzero(D['game'].to_numpy() == gm) for gm in games}
    B = []
    for _ in range(a.boot):
        pick = rng.choice(games, len(games))
        ix = np.concatenate([idx_by_game[gm] for gm in pick])
        # re-number groups so copies of a game are distinct decisions
        rep = np.concatenate([np.full(len(idx_by_game[gm]), k) for k, gm in enumerate(pick)])
        g2 = gid[ix] + rep * (gid.max() + 1)
        o = np.argsort(g2, kind='stable')
        B.append(clogit(X[ix][o], g2[o], y[ix][o])[0])
    B = np.array(B)
    scale = math.log(GAMMA) / b[0]
    res = dict(n_rows=int(len(D)), n_decisions=int(gid.max() + 1), games=int(len(games)), ll=float(ll),
               winners_only=bool(a.winners_only), coef={c: float(v) for c, v in zip(cols, b)},
               coef_90={c: [float(np.percentile(B[:, k], 5)), float(np.percentile(B[:, k], 95))] for k, c in enumerate(cols)},
               implied_w={c: float(b[k] * scale) for k, c in enumerate(cols) if c in feats},
               implied_w_90={c: sorted([float(np.percentile(B[:, k] * math.log(GAMMA) / B[:, 0], 5)),
                                        float(np.percentile(B[:, k] * math.log(GAMMA) / B[:, 0], 95))])
                             for k, c in enumerate(cols) if c in feats})
    OUT.mkdir(parents=True, exist_ok=True)
    tag = 'winners' if a.winners_only else 'top'
    (OUT / f'clogit-{tag}-{"-".join(feats)}.json').write_text(json.dumps(res, indent=1))
    print(f"conditional logit on {res['n_decisions']} decisions ({res['n_rows']} candidates, {res['games']} games)")
    for k, c in enumerate(cols):
        lo, hi = res['coef_90'][c]
        extra = (f"  -> w = {res['implied_w'][c]:+.3f} [{res['implied_w_90'][c][0]:+.3f}, {res['implied_w_90'][c][1]:+.3f}]"
                 if c in feats else '')
        print(f"  {c:12s} {b[k]:+.4f} [{lo:+.4f}, {hi:+.4f}]{extra}")


def cmd_selfplay(a):
    """Outcome regression on maelle dumps: for every target decision with a chosen candidate, the chosen row's
    features against (i) pearls eaten over the next 20 rounds (Poisson, offset = log base score), (ii) death within
    20 rounds (logistic). Pearls eaten = length change + split sizes + sprint segments, from the same dragon's later
    records."""
    import pandas as pd
    sys.path.insert(0, str(ROOT / 'tools' / 'maelle'))
    from dump import read, TNAMES
    from sklearn.linear_model import PoissonRegressor, LogisticRegression
    files = sorted(glob.glob(str(Path(a.dumps) / '*.bin')))[: a.limit or None]
    R = []
    for fi, p in enumerate(files):
        recs = read(p)
        by = {}
        last_round = max((h['rnd'] for h, _ in recs), default=0)
        for h, rows in recs:
            by.setdefault((h['team'], h['me']), []).append((h, rows))
        for (team, me), lst in by.items():
            lst.sort(key=lambda x: (x[0]['rnd'], x[0]['kind']))
            # per round: length, spent (split size or sprint segments)
            L, spent = {}, {}
            for h, rows in lst:
                L[h['rnd']] = h['len']
                if h['kind'] == 1:
                    if h['chosen'] >= 0:
                        spent[h['rnd']] = spent.get(h['rnd'], 0) + max(0, int(rows[h['chosen'], 1]) - 1)
                    elif h['why'] in 'srt':
                        spent[h['rnd']] = spent.get(h['rnd'], 0) + 2  # split child (production split size)
            rounds = sorted(L)
            last = rounds[-1]
            for h, rows in lst:
                if h['kind'] != 0 or h['chosen'] < 0:
                    continue
                r0 = h['rnd']
                if r0 + 20 > last_round:
                    continue
                r1 = r0 + 20
                died = last < r1 and last < last_round - 1
                end = min(r1, last)
                eaten = L[end] - L[r0] + sum(v for k, v in spent.items() if r0 <= k < end)
                row = rows[h['chosen']]
                R.append(dict(file=fi, me=me, rnd=r0, logscore=float(row[0]), steps=float(row[1]),
                              pearl_now=float(row[2]), memory=float(row[3]), bed=float(row[4]), unseen=float(row[5]),
                              eaten=max(0, eaten), died=int(died), len=h['len'],
                              **{n: float(row[6 + k]) for k, n in enumerate(TNAMES)}))
    D = pd.DataFrame(R)
    OUT.mkdir(parents=True, exist_ok=True)
    D.to_parquet(OUT / 'selfplay_outcomes.parquet')
    feats = a.features.split(',')
    ctrl = ['logscore', 'steps', 'pearl_now', 'memory', 'bed', 'unseen']
    X = D[ctrl + feats].to_numpy(float)
    rng = np.random.default_rng(5)
    files_u = D['file'].unique()
    out = {}
    for name, y, model in (('eaten', D['eaten'].to_numpy(float), lambda: PoissonRegressor(alpha=1e-4, max_iter=500)),
                           ('died', D['died'].to_numpy(int), lambda: LogisticRegression(C=1e4, max_iter=2000))):
        m = model().fit(X, y)
        coef = np.ravel(m.coef_)
        B = []
        for _ in range(a.boot):
            pick = rng.choice(files_u, len(files_u))
            ix = np.concatenate([np.flatnonzero(D['file'].to_numpy() == f) for f in pick])
            B.append(np.ravel(model().fit(X[ix], y[ix]).coef_))
        B = np.array(B)
        out[name] = {c: [float(coef[k]), float(np.percentile(B[:, k], 5)), float(np.percentile(B[:, k], 95))]
                     for k, c in enumerate(ctrl + feats)}
        print(f"== {name} ({'Poisson' if name == 'eaten' else 'logistic'}) on {len(D)} chosen targets, mean {y.mean():.3f}")
        for c, (v, lo, hi) in out[name].items():
            print(f"  {c:12s} {v:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    (OUT / 'selfplay-fit.json').write_text(json.dumps(dict(n=len(D), features=feats, fits=out), indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('corpus-extract'); c.add_argument('--corpus'); c.add_argument('--top', type=int, default=30)
    c.add_argument('--jobs', type=int, default=4); c.add_argument('--limit', type=int, default=0)
    k = sub.add_parser('clogit'); k.add_argument('--data', default=str(OUT / 'corpus_targets.parquet'))
    k.add_argument('--features', default='food,ally,enemy,threat,death'); k.add_argument('--winners-only', action='store_true')
    k.add_argument('--boot', type=int, default=100)
    s = sub.add_parser('selfplay'); s.add_argument('--dumps', required=True); s.add_argument('--limit', type=int, default=0)
    s.add_argument('--features', default='food,food_unseen,ally,enemy,threat,death,age,food_sat')
    s.add_argument('--boot', type=int, default=50)
    a = ap.parse_args()
    {'corpus-extract': cmd_corpus_extract, 'clogit': cmd_clogit, 'selfplay': cmd_selfplay}[a.cmd](a)


if __name__ == '__main__':
    main()

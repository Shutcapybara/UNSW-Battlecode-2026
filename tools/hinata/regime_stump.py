"""Hinata P-6 (P-hinata-04) Amendment A §2 as amended 19:41Z — regime stump selection. TRAINING MAPS ONLY.

  python3 tools/hinata/regime_stump.py [--out build/hinata/p6/stump.json]

Candidates (IO-observable at turn 1, Sugawara 19:30Z): WH = W*H, WpH = W+H, minside = min(W,H) (get_map_size);
win_open = share of non-kelp edges (kind != 1) among edges with both end tiles inside the wrapping 7x7 window centred on
the head (first DRAGON segment); win_portals = portal edges (kind 2) in that window; units = own dragons at turn 1.
Window features are per process (team 0 spawns) reduced by the median over the team (fixed 19:41Z). Labels: C7-03 post-m2
(v0.py ELIM_M2: elimination vs round-limit), label_era printed. Held-out map files (heldout-maps.json) are skipped BY FILE
NAME before opening. Stump: depth 1, threshold at midpoints, direction <= or > means elimination; LOMO: for each map,
threshold and direction chosen on the other 13 (max agreement; ties -> lower threshold, '<=' first); feature chosen by LOMO
agreement (ties -> candidate order). Frozen iff LOMO >= 12/14; else the declared fallback (Phi everywhere before r150).
"""
import argparse, json, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path.cwd()
FILES = {'Schooltime': 'schooltime', 'Portals': 'portals', 'Slithery Fight': 'slithery_fight', 'Queen Of Spades': 'queen_of_spades',
         'Default': 'default', 'Trophy': 'trophy', 'Prisoners Dilemma': 'dilemma', 'Devil': 'devil', 'Australia': 'australia',
         'Islands': 'islands', 'Around UNSW': 'unsw', 'weakhold': 'weakhold', 'Stripes': 'stripes', 'Tower Defense': 'tower_defense'}
ELIM_M2 = ('Devil', 'Trophy', 'Stripes', 'Tower Defense', 'Queen Of Spades', 'Default', 'Autarky')   # = v0.py (asserted)
CANDS = ['WH', 'WpH', 'minside', 'win_open', 'win_portals', 'units']


def parse(p):
    W = H = None; edges = {}; heads = []
    for line in p.read_text().splitlines():
        t = line.split()
        if not t:
            continue
        if t[0] == 'MAP':
            W, H = int(t[1]), int(t[2])
        elif t[0] == 'EDGE':
            i, k = int(t[1]), int(t[2]); col, row = i % (W + 1), i // (W + 1)
            if col < W and row < 2 * H:
                edges[(row % 2, col, row // 2)] = k
        elif t[0] == 'DRAGON' and int(t[1]) == 0:
            heads.append((int(t[3]), int(t[4])))
    return W, H, edges, heads


def feats(p):
    W, H, E, heads = parse(p); op, po = [], []
    for hx, hy in heads:
        win = {((hx + dx) % W, (hy + dy) % H) for dx in range(-3, 4) for dy in range(-3, 4)}; ks = []
        for (o, x, y), k in E.items():
            b = (x, (y + 1) % H) if o == 0 else ((x + 1) % W, y)
            if (x % W, y % H) in win and b in win:
                ks.append(k)
        op.append(sum(k != 1 for k in ks) / len(ks)); po.append(sum(k == 2 for k in ks))
    return dict(WH=W * H, WpH=W + H, minside=min(W, H), win_open=round(statistics.median(op), 4),
                win_portals=statistics.median(po), units=len(heads))


def best(xs, ys):
    vals = sorted(set(xs)); ths = [(a + b) / 2 for a, b in zip(vals, vals[1:])] or [vals[0]]; top = None
    for th in ths:
        for d in ('<=', '>'):
            agree = sum(((x <= th) if d == '<=' else (x > th)) == y for x, y in zip(xs, ys))
            if top is None or agree > top[0]:
                top = (agree, th, d)
    return top


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='build/hinata/p6/stump.json'); a = ap.parse_args()
    import ast, re
    src = (Path(__file__).resolve().parent / 'v0.py').read_text()
    assert tuple(ast.literal_eval(re.search(r'^ELIM_M2 = (\(.*?\))', src, re.M).group(1))) == ELIM_M2
    held = set(json.loads((ROOT / 'docs/learning/splits/heldout-maps.json').read_text())['heldout_maps'])
    maps = [m for m in FILES if m not in held]; assert len(maps) == 14, maps
    F = {m: feats(ROOT / 'maps/live' / f'{FILES[m]}.map') for m in maps}; Y = {m: m in ELIM_M2 for m in maps}
    res = {}
    for c in CANDS:
        xs = [F[m][c] for m in maps]; ys = [Y[m] for m in maps]; ins = best(xs, ys); miss = []; lomo = 0
        for i, m in enumerate(maps):
            ag, th, d = best(xs[:i] + xs[i + 1:], ys[:i] + ys[i + 1:]); pr = (xs[i] <= th) if d == '<=' else (xs[i] > th)
            lomo += pr == ys[i]
            if pr != ys[i]:
                miss.append(m)
        res[c] = dict(in_sample=f'{ins[0]}/14', threshold=ins[1], direction=ins[2] + ' -> elimination', lomo=f'{lomo}/14', lomo_n=lomo, lomo_misses=miss)
    sel = max(CANDS, key=lambda c: (res[c]['lomo_n'], -CANDS.index(c)))
    out = dict(label_era='post-m2 (v0.py ELIM_M2, C7-03)', maps=maps, features=F, labels={m: 'elim' if Y[m] else 'rl' for m in maps},
               candidates=res, selected=sel if res[sel]['lomo_n'] >= 12 else None,
               decision=(f"FROZEN: {sel} {res[sel]['direction']} at {res[sel]['threshold']}" if res[sel]['lomo_n'] >= 12
                         else f"FALLBACK: best LOMO {res[sel]['lomo']} ({sel}) < 12/14 -> Phi everywhere before r150"),
               code='tools/hinata/regime_stump.py', heldout_skipped_by_filename=sorted(held))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(json.dumps(out, indent=1))
    for c in CANDS:
        print(c, res[c])
    print(out['decision'])


if __name__ == '__main__':
    main()

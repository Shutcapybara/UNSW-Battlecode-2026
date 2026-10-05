"""P-hinata-07 stage 2: aggregate build/hinata/curves/g_s*.jsonl -> table.csv (all cells) + ci.csv (our-minus-opp / winner-minus-loser
at r100/200/300/400/end, series bootstrap 1000 x seed 7, linear 5-95 %, running-games view)."""
import json, csv, random, collections
from pathlib import Path
D = Path('build/hinata/curves'); G = [json.loads(l) for q in sorted(D.glob('g_s*.jsonl')) for l in open(q)]
G = [g for g in G if 'err' not in g]
RND = [str(r) for r in range(0, 500, 25)] + ['end']; M = ['units', 'total', 'longest', 'q_alive', 'q_len']
def band(e): return 'na' if e is None else '<1725' if e < 1725 else '1725-1900' if e <= 1900 else '>1900'
rows = []  # (group, band, side_label, game, curveX, curveY) X = ours/winner, Y = opp/loser
for g in G:
    if g['pop'] == 'top10':
        if g['winner'] not in ('A', 'B'): continue
        w = g['winner']; l = 'B' if w == 'A' else 'A'; rows.append(('top10', 'all', g, g['c' + w], g['c' + l]))
    else:
        us = g['us']; th = 'B' if us == 'A' else 'A'; e = g['elo_' + th.lower()]
        for b in (band(e), 'all'): rows.append((g['pop'], b, g, g['c' + us], g['c' + th]))
cells = collections.defaultdict(list)
for grp, b, g, X, Y in rows: cells[(grp, b)].append((g, X, Y))
out = csv.writer(open(D / 'table.csv', 'w')); out.writerow(['group', 'band', 'round', 'view', 'n', 'n_series', 'win_rate'] + [f'{m}_X' for m in M] + [f'{m}_Y' for m in M])
ci = csv.writer(open(D / 'ci.csv', 'w')); ci.writerow(['group', 'band', 'round', 'metric', 'n', 'n_series', 'X', 'Y', 'diff', 'lo5', 'hi95'])
def at(c, r, g):  # running view value or None; carried view value
    if r in c: return c[r], c[r]
    return None, c['end']
rng = random.Random(7)
for (grp, b), L in sorted(cells.items()):
    for r in RND:
        for view in ('running', 'carried'):
            v = [(g, (at(X, r, g)[0 if view == 'running' else 1]), (at(Y, r, g)[0 if view == 'running' else 1])) for g, X, Y in L]
            v = [t for t in v if t[1] is not None]
            if not v: continue
            n = len(v); ns = len({t[0]['series'] for t in v})
            wr = sum((t[0]['winner'] == t[0]['us']) for t in v) / n if grp != 'top10' else ''
            out.writerow([grp, b, r, view, n, ns, wr] + [round(sum(t[1][k] for t in v) / n, 3) for k in range(5)] + [round(sum(t[2][k] for t in v) / n, 3) for k in range(5)])
            if view == 'running' and r in ('100', '200', '300', '400', 'end'):
                bys = collections.defaultdict(list)
                for t in v: bys[t[0]['series']].append(t)
                S = list(bys.values())
                for k, m in enumerate(M):
                    if m == 'longest': continue
                    sx = [(sum(t[1][k] - t[2][k] for t in s), len(s)) for s in S]
                    d = sum(a for a, _ in sx) / n; bs = []
                    for _ in range(1000):
                        pick = [sx[rng.randrange(len(sx))] for _ in sx]; bs.append(sum(a for a, _ in pick) / max(1, sum(c for _, c in pick)))
                    bs.sort(); q = lambda p: bs[0] + 0 if len(bs) < 2 else bs[int(p * 999)] + (p * 999 - int(p * 999)) * (bs[min(999, int(p * 999) + 1)] - bs[int(p * 999)])
                    ci.writerow([grp, b, r, m, n, len(S), round(sum(t[1][k] for t in v) / n, 3), round(sum(t[2][k] for t in v) / n, 3), round(d, 3), round(q(0.05), 3), round(q(0.95), 3)])
print('games', len(G), 'cells', len(cells))

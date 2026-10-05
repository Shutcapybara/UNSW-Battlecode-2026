#!/usr/bin/env python3
"""D-091 §C frozen-row test (Sugawara 22:27Z): of a bot's queen wall deaths on a panel (seed 1), how many had a portal
edge next to the queen's head in the 1-3 rounds before death with the landing out of her sight.
Frame caches only (frozen; no new games). Queen = team's starting dragon (id 0/1), death event cause 'wall'.
Head = body[0] of g['rounds'][R][id]. Portal edge = a neighbour in g['nbr'][head] (N,E,S,W) that is not the plain
wrapped grid neighbour. Landing out of sight = Chebyshev distance (wrapped) from the head to the landing > 3
(helper.hpp VISION_RADIUS = 3; current vision only, memory/sonar not modelled).
    python tools/asahi/qwallportal.py BOT [--panel qk2]
"""
import argparse, glob, gzip, json, pickle, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import panel as P  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument('bot'); ap.add_argument('--panel', default='qk2'); a = ap.parse_args()
root = P.run_root(a.bot, a.panel)
D = ((0, -1), (1, 0), (0, 1), (-1, 0))
tot = hit = hit_any = 0
for l in open(root / 'index.jsonl'):
    r = json.loads(l)
    if r.get('rc') != 0 or r['seed'] != 1:
        continue
    h = glob.glob(str(root / 'frames' / (r['game'] + '.*.pkl.gz')))
    g = pickle.load(gzip.open(h[0]))
    me = r['seat']; W, H = g['W'], g['H']
    qd = [d for d in g['events']['deaths'] if d['id'] in (0, 1) and d['team'] == me]
    if not qd or qd[0]['cause'] != 'wall':
        continue
    tot += 1; R = qd[0]['round']; qid = qd[0]['id']
    def cheb(p, q):
        dx = abs(p[0] - q[0]); dy = abs(p[1] - q[1]); dx = min(dx, W - dx); dy = min(dy, H - dy); return max(dx, dy)
    rows = []
    for k in (1, 2, 3):
        snap = g['rounds'][R - k] if R - k >= 0 else {}
        if qid not in snap:
            continue
        hd = tuple(snap[qid][1][0])
        for di, t in enumerate(g['nbr'].get(hd, ())):
            if t is None:
                continue
            geo = ((hd[0] + D[di][0]) % W, (hd[1] + D[di][1]) % H)
            if tuple(t) != geo:
                rows.append((k, hd, 'NESW'[di], tuple(t), cheb(hd, tuple(t)) > 3))
    blind = [x for x in rows if x[4]]
    hit += bool(blind); hit_any += bool(rows)
    print(f"{r['game']} r{R} head@death {qd[0]['head']} len {qd[0]['length']}: portal edges r-1..3 {rows if rows else 'none'} -> {'BLIND' if blind else ('seen' if rows else '-')}")
print(f"SUMMARY {a.bot} {a.panel}: queen wall deaths {tot}; portal edge beside head in prior 1-3 rounds {hit_any}; with landing out of sight {hit}")

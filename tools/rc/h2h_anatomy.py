#!/usr/bin/env python3
"""rc: anatomy of our ally head-on deaths from a lane run (seed-1 pool replays).

    python3 tools/rc/h2h_anatomy.py BOT

For each collision (counted once, at the non-mover victim): did the mover cross a portal, where was the victim
(already on the landing cell / moved onto it this round / other), was it heading into the portal, was it in view."""
import glob, sys, collections
sys.path.insert(0, '.')
from tools.analysis.features.frame import load
from concurrent.futures import ProcessPoolExecutor
bot = sys.argv[1]
def one(f):
    g = load(f); ev = g['events']; nbr = g['nbr']
    me = 'B' if bot in g['botB'] else 'A'
    acts = {(a['round'], a['id']): a for a in ev['actions']}
    C = collections.Counter()
    for d in ev['deaths']:
        if d['cause'] != 'h2h' or d['team'] != me or d.get('killer_team') != me or d['actor'] == d['id']:
            continue   # count each collision once: the non-actor victim
        A, B, r = d['actor'], d['id'], d['round']
        prev = g['rounds'][r]  # snapshot at round start
        a = acts.get((r, A))
        if A not in prev or B not in prev or not a or not a.get('dirs'):
            C['unknown'] += 1; continue
        pa, pb = prev[A][1][0], prev[B][1][0]
        land = nbr[pa][a['dirs'][0]] if len(a['dirs']) == 1 else None
        dist = abs(pa[0]-pb[0]) + abs(pa[1]-pb[1])
        portal = land is not None and abs(land[0]-pa[0]) + abs(land[1]-pa[1]) > 1 and not (abs(land[0]-pa[0]) in (g['W']-1,) or abs(land[1]-pa[1]) in (g['H']-1,))
        bb = prev[B][1]
        facing_into = None
        if len(bb) >= 2:
            for dd in range(4):
                if nbr[bb[1]][dd] == bb[0] or (nbr[bb[1]][dd] is not None and nbr[bb[1]][dd] == bb[0]):
                    facing_into = nbr[bb[0]][dd] == pa
        b = acts.get((r, B))
        kind = 'B_not_yet'
        if b and b.get('dirs'):
            lb = nbr[pb][b['dirs'][0]] if len(b['dirs']) == 1 else None
            if lb == land:
                bport = abs(lb[0]-pb[0]) + abs(lb[1]-pb[1]) > 1
                kind = 'B_moved_onto_landing(' + ('via portal' if bport else 'walk') + ')'
            else:
                kind = 'B_moved_elsewhere'
        elif pb == land:
            kind = 'B_head_at_landing'
        W, H = g['W'], g['H']
        def jump(c, dd):
            n = nbr[c][dd]
            if n is None: return False
            dx = abs(n[0]-c[0]); dy = abs(n[1]-c[1])
            return (min(dx, W-dx) + min(dy, H-dy)) > 1
        if kind.startswith('B_moved_onto'):
            heading = b['dirs'][-1]
        elif kind == 'B_head_at_landing' and len(bb) >= 2:
            heading = next((dd for dd in range(4) if nbr[bb[1]][dd] == bb[0]), None)
        else:
            heading = None
        kind += '|' + ('heading_into_portal' if heading is not None and jump(land, heading) else 'not_heading_in' if heading is not None else '?')
        near = max(min(abs(pa[0]-pb[0]), g['W']-abs(pa[0]-pb[0])), min(abs(pa[1]-pb[1]), g['H']-abs(pa[1]-pb[1])))
        C[('portal' if portal else 'walk', kind, 'B_in_A_view' if near <= 3 else 'B_out_of_view')] += 1
    return C
fs = sorted(glob.glob(f'build/rc/runs/{bot}/pool/replays/s1__*.replay'))
tot = collections.Counter()
with ProcessPoolExecutor(14) as ex:
    for c in ex.map(one, fs): tot.update(c)
n = sum(tot.values()); print(bot, n, 'collisions')
for k, v in tot.most_common(): print(k, v, round(v / n, 3))

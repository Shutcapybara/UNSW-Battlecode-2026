#!/usr/bin/env python3
"""ASCII frames of a replay at chosen rounds.  python3 frames.py REPLAY r1,r2,... [x0 x1 y0 y1]
Cells: A/B head, a/b body (team A / B), '*' pearl, ':' fast bed, '.' bed; walls/portals as mapview."""
import sys, collections
sys.path.insert(0, 'tools/leviathan'); sys.path.insert(0, 'tools/ouroboros')
from replay import Reader
from mapview import load_map
def frames(path, rounds, box=None):
    r = Reader(path); root = r.object(0, 0); mt = root.text(0); m = load_map(mt); W, H = m['W'], m['H']
    teams = {i: t for i, (t, b) in enumerate(m['dragons'])}
    body = {i: collections.deque(b) for i, (t, b) in enumerate(m['dragons'])}; live = set(body)
    pearls = set(); out = {}; rnd = -1; want = set(rounds)
    def point(o): return (o.num(), o.num(4))
    def snap():
        occ = {}
        for i in live:
            for k, c in enumerate(body[i]):
                occ[c] = (teams[i] if k == 0 else teams[i].lower(), i)
        rows = []
        xs = range(W) if not box else range(box[0], box[1]); ys = range(H) if not box else range(box[2], box[3])
        for y in ys:
            top = []; mid = []
            for x in xs:
                e = m['portal_h'].get((x, y))
                top.append('+' + ('~~' if (x, y) in m['kelp_h'] else ('%2d' % e if e is not None else '  ')))
                e = m['portal_v'].get((x, y))
                wall = '|' if (x, y) in m['kelp_v'] else ('%d' % (e % 10) if e is not None else ' ')
                o = occ.get((x, y)); t = m['tiles'].get((x, y), (0, 0))
                if o: ch = o[0] + ('%d' % (o[1] % 10) if o[0].isupper() else o[0])
                elif (x, y) in pearls: ch = '**'
                elif t[1] > 0: ch = '::' if t[1] <= 30 else '..'
                else: ch = '  '
                mid.append(wall + ch)
            rows.append(''.join(top)); rows.append(''.join(mid))
        return '\n'.join(rows)
    for e in root.items(3):
        k = e.num(0, 'H'); o = e.child(0); i = o.num()
        if k == 0:
            rnd = i
            if rnd in want: out[rnd] = snap()
        elif k == 3:
            c = point(o.child(0))
            if o.num(0, 'B'): pearls.add(c)
            else: pearls.discard(c)
        elif k == 9:
            b = body[i]; head, tail = point(o.child(0)), point(o.child(1))
            if b[0] != head: b.appendleft(head)
            while len(b) > 1 and b[-1] != tail: b.pop()
        elif k == 10:
            child = o.num(4); teams[child] = teams[i]; live.add(child)
            body[i] = collections.deque(point(p) for p in o.items(0)); body[child] = collections.deque(point(p) for p in o.items(1))
        elif k == 11:
            live.discard(i)
    return out
if __name__ == '__main__':
    rs = [int(x) for x in sys.argv[2].split(',')]
    box = [int(x) for x in sys.argv[3:7]] if len(sys.argv) >= 7 else None
    for r, f in sorted(frames(sys.argv[1], rs, box).items()):
        print(f'=== round {r}'); print(f)

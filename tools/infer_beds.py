"""Reconstruct a local .map from a public replay: public map text zeros bed fields,
but replay kind-2 events list every bed at round -1 and each countdown reset.
Bed period estimate = max observed countdown (a lower bound on the true period)."""
import sys, collections
sys.path.insert(0, 'tools/leviathan')
from replay import Reader
def infer(paths):
    beds = collections.defaultdict(list); text = None
    for path in paths:
        root = Reader(path).object(0, 0); t = root.text(0)
        if text is None: text = t
        rnd = -1
        for e in root.items(3):
            k = e.num(0, 'H'); o = e.child(0)
            if k == 0: rnd = o.num()
            elif k == 2:
                c = o.child(0); beds[(c.num(), c.num(4))].append((rnd, o.num()))
    return text, beds
if __name__ == '__main__':
    out = sys.argv[1]; text, beds = infer(sys.argv[2:])
    lines = []
    for l in text.splitlines():
        p = l.split()
        if p and p[0] == 'TILE':
            c = (int(p[1]), int(p[2]))
            if c in beds:
                per = max(v for _, v in beds[c])
                l = f'TILE {c[0]} {c[1]} 1 {per}'
        lines.append(l)
    open(out, 'w').write('\n'.join(lines) + '\n')
    per = collections.Counter(max(v for _, v in b) for b in beds.values())
    print(out, len(beds), 'beds; period histogram', sorted(per.items())[:20])

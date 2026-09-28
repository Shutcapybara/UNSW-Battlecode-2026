import sys, collections, glob
sys.path.insert(0, 'tools'); sys.path.insert(0, 'tools/leviathan')
from infer_beds import infer
from replay import Reader
NICE = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80, 100, 120, 150, 200, 250, 300, 400, 500, 600, 800, 1000]
def estimate(files):
    text, beds = infer(files)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    def partners(c):
        x, y = c
        return {(W-1-x, y), (x, H-1-y), (W-1-x, H-1-y)}
    est = {}
    for c in beds:
        vals = [v for _, v in beds[c]]
        for p in partners(c):
            if p in beds: vals += [v for _, v in beds[p]]
        m, n = max(vals), len(vals)
        e = m if m <= 1 else m * (n + 1) / n
        est[c] = next((s for s in NICE if s >= e - 0.5), NICE[-1])
    return text, est
if __name__ == '__main__':
    name = sys.argv[1]; out = sys.argv[2]; files = sys.argv[3:]
    text, est = estimate(files)
    lines = []
    for l in text.splitlines():
        p = l.split()
        if p and p[0] == 'TILE' and (int(p[1]), int(p[2])) in est:
            l = f'TILE {p[1]} {p[2]} 1 {est[(int(p[1]), int(p[2]))]}'
        lines.append(l)
    open(out, 'w').write('\n'.join(lines) + '\n')
    print(out, len(est), sorted(collections.Counter(est.values()).items()))

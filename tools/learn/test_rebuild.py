"""Block-rebuild parity: rebuilt-from-replay blocks vs the blocks the engine really sent."""
import sys, gzip, pickle, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import block as B, rebuild


def check(path, show=3):
    g = pickle.load(gzip.open(path))
    got = collections.defaultdict(list)
    rebuild.walk(g['replay'], lambda i, sp, txt, ctx: got[i].append(txt))
    n = bad = 0
    shown = 0
    for i, blocks in g['obs'].items():
        for k, raw in enumerate(blocks):
            n += 1
            want = B.canon(raw)
            have = B.canon(got[i][k]) if k < len(got[i]) else '<missing>\n'
            if want != have:
                bad += 1
                if shown < show:
                    shown += 1
                    w, h = want.splitlines(), have.splitlines()
                    diffs = [(j, a, b) for j, (a, b) in enumerate(zip(w, h)) if a != b][:6]
                    print(f'  {Path(path).name} dragon {i} turn {k}: lines {len(w)} vs {len(h)} first diffs {diffs}')
    extra = sum(max(0, len(got[i]) - len(g['obs'].get(i, []))) for i in got)
    return n, bad, extra


if __name__ == '__main__':
    tot = totbad = 0
    for p in sys.argv[1:]:
        n, bad, extra = check(p)
        tot += n; totbad += bad
        print(f'{Path(p).name}: {n - bad}/{n} identical, extra {extra}')
    print(f'TOTAL {tot - totbad}/{tot} identical')

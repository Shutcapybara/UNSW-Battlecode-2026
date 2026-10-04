"""Label agreement vs HB-1 (tools/team_recon_claude/features_v5.py) on Heartbreaker (team 62) replays.
    python test_labels_hb1.py SIDE:replay ...   e.g. B:447104.replay"""
import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1] / 'team_recon_claude'))
import rebuild, labels as LB, block as B
import features_v5 as V5

REL = {'F': 0, 'R': 1, 'B': 2, 'L': 3}


def ours(path, side):
    rows = collections.defaultdict(list)

    def em(i, sp, txt, ctx):
        if sp['team'] != side:
            return
        rows[i].append((ctx['round'], LB.label(ctx, B.parse_block(txt), i, sp['team'])))
    rebuild.walk(Path(path).read_bytes(), em)
    return rows


def theirs(path, side):
    out = V5.extract(path, side, Path(path).stem)
    rows = out[0] if isinstance(out, tuple) else out
    return rows


if __name__ == '__main__':
    agree = collections.Counter(); tot = collections.Counter(); ex = []
    for arg in sys.argv[1:]:
        side, p = arg.split(':', 1)
        mine = ours(p, side)
        hb = theirs(p, side)
        byd = collections.defaultdict(list)
        for r in hb:
            byd[r['dragon']].append(r)
        for d, seq in byd.items():
            m = mine.get(d, [])
            for k, r in enumerate(seq):
                if k >= len(m):
                    tot['missing'] += 1; continue
                rnd, y = m[k]
                fam = r.get('y_family')
                checks = {}
                if fam == 'move':
                    checks['first'] = (REL.get(r['y_first'], -9), y['y_first'])
                    checks['nsteps'] = (r['y_nsteps'], y['y_nsteps'])
                    checks['family'] = ('move', ('move', 'split', 'inv', 'none')[y['y_kind']])
                elif fam == 'split':
                    checks['child'] = (r['y_child'], y['y_child'])
                    checks['family'] = ('split', ('move', 'split', 'inv', 'none')[y['y_kind']])
                else:
                    checks['family'] = (str(fam), ('move', 'split', 'inv', 'none')[y['y_kind']])
                if 'y_sonar_mask' in r:
                    checks['sonar_mask_phys'] = (r['y_sonar_mask'], y['y_sonar_mask_phys'])
                    checks['sonar_n'] = (r['y_sonar_n'], y['y_sonar_n'])
                for kk, (a, b) in checks.items():
                    tot[kk] += 1
                    if a == b:
                        agree[kk] += 1
                    elif len(ex) < 12:
                        ex.append((Path(p).stem, d, k, rnd, kk, a, b))
    for kk in tot:
        print(f'{kk:12s} {agree[kk]}/{tot[kk]} = {agree[kk] / max(1, tot[kk]):.5f}')
    for e in ex:
        print('  disagree', e)

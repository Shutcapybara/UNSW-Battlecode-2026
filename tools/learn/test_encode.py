"""Encoder smoke + invariants on engine truth files; dumps a parity fixture (blocks + expected vectors)."""
import sys, gzip, pickle, json, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import block as B, encode as E


def run(paths, fixture=None, n_fix=1000, seed=7):
    rng = random.Random(seed)
    names = E.names()
    assert len(names) == 49 * E.N_CH + E.N_SC and len(set(names)) == len(names)
    rows = 0
    fix = []
    for p in paths:
        g = pickle.load(gzip.open(p))
        for did, blocks in g['obs'].items():
            sp = B.parse_spawn(g['spawn'][did].decode())
            enc = E.Encoder(sp)
            seq = []
            for raw in blocks:
                b = B.parse_block(raw)
                x = enc.observe(b)
                assert len(x) == len(names)
                assert all(isinstance(v, int) for v in x)
                # invariants: own head never in the grid as a part; centre cell own_seg = 1
                assert x[24 * E.N_CH + E.CH.index('own_seg')] == 1
                ch = {c: j for j, c in enumerate(E.CH)}
                cen = 24 * E.N_CH
                he = {'N': b.hedges[3][3], 'S': b.hedges[4][3], 'W': b.vedges[3][3], 'E': b.vedges[3][4]}
                for k, a in enumerate('NESW'):
                    rel = 'FRBL'[(k - 'NESW'.index(b.dir)) % 4]
                    assert x[cen + ch['kelp_' + rel]] == int(he[a] == 'w'), ('kelp', rel)
                    assert x[cen + ch['portal_' + rel]] == int(he[a] not in '.w'), ('portal', rel)
                # shared edges agree between neighbours (ahead cell's B side == centre's F side, etc.)
                for rel, nb, opp in (('F', 17, 'B'), ('R', 25, 'L'), ('B', 31, 'F'), ('L', 23, 'R')):
                    assert x[cen + ch['kelp_' + rel]] == x[nb * E.N_CH + ch['kelp_' + opp]]
                # the move label direction relative to facing must be a free exit when the walker took a plain step
                rows += 1
                seq.append((B.canon(raw), x))
            fix.append((g['spawn'][did].decode(), seq))
    if fixture:
        # keep whole process sequences (memory features need the history) until >= n_fix turns
        rng.shuffle(fix)
        out, n = [], 0
        for sp, seq in fix:
            if n >= n_fix:
                break
            out.append(dict(spawn=sp, blocks=[s for s, _ in seq], x=[v for _, v in seq]))
            n += len(seq)
        Path(fixture).write_text(json.dumps(dict(enc_version=E.ENC_VERSION, names=names, procs=out)))
        print('fixture', fixture, 'processes', len(out), 'turns', n)
    print('rows', rows, 'cols', len(names))


if __name__ == '__main__':
    fx = None
    args = sys.argv[1:]
    if args and args[0].startswith('--fixture='):
        fx = args.pop(0).split('=', 1)[1]
    run(args, fx)

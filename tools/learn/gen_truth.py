"""Generate ground-truth (spawn blocks, every received block, replay) from the official engine with a cheap
stochastic 'safe walker' policy, for the block-rebuild parity test. Run where unswbc>=1.2.9 is importable."""
import sys, random, pickle, gzip, pathlib
from unswbc.engine import EngineModule
import block as B

MAPS = pathlib.Path(__import__('unswbc').__file__).with_name('templates') / 'maps'
OFF = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


def head_edges(b):
    return {'N': b.hedges[3][3], 'S': b.hedges[4][3], 'W': b.vedges[3][3], 'E': b.vedges[3][4]}


def policy(rng, b, prof):
    occ = {(x, y) for _, _, x, y, _, _ in b.parts}
    win = {i: b.tiles[i] for i in range(49)}
    he = head_edges(b)
    safe, risky = [], []
    W_, H_ = prof['W'], prof['H']
    for d, (dx, dy) in OFF.items():
        e = he[d]
        if e == 'w':
            continue
        if e != '.':
            safe.append(d); continue
        t = win[(3 + dy) * 7 + 3 + dx]
        if (t[0], t[1]) not in occ:
            heads = {(x, y) for _, i, x, y, _, h in b.parts if h}
            near = any(((t[0] + ex) % W_, (t[1] + ey) % H_) in heads - {(b.tiles[24][0], b.tiles[24][1])} for ex, ey in OFF.values())
            (safe if not near else risky).append(d)
    pear = [d for d in safe if win[(3 + OFF[d][1]) * 7 + 3 + OFF[d][0]][2] == 1 and he[d] == '.']
    out = []
    x = rng.random()
    if b.length >= 4 and b.unit_count < 64 and x < prof['split']:
        out.append(f'SPLIT {rng.randint(2, b.length - 2)}')
    elif x < prof['split'] + prof['junk']:
        out.append(rng.choice(['MOVE Q', 'SPLIT 1', 'MOVE', 'SPLIT 99']))
    elif safe:
        d = rng.choice(pear) if pear and rng.random() < 0.7 else rng.choice(safe)
        steps = d
        if b.length >= 5 and rng.random() < prof['sprint']:
            steps += ''.join(rng.choice('NESW') for _ in range(rng.randint(1, 3)))
        out.append('MOVE ' + steps)
    elif risky:
        out.append('MOVE ' + rng.choice(risky))
    else:
        out.append('MOVE ' + rng.choice('NESW'))
    for d in 'NESW':
        if rng.random() < prof['sonar']:
            v = rng.choice([0, rng.randint(0, 2**32 - 1), rng.randint(0, 2**64 - 1)])
            out.append(f'SONAR {d} {v}')
    if rng.random() < 0.1:
        out.append(f'SONAR {rng.randint(0, 2**32 - 1)}')
    if rng.random() < prof['p3']:
        out.append('PROTOCOL 3')
    out.append('ENDTURN')
    return ('\n'.join(out) + '\n').encode()


def run(mapname, seed, prof):
    rng = random.Random(seed * 7919 + sum(map(ord, mapname)))
    txt = (MAPS / f'{mapname}.map').read_text()
    W_, H_ = [int(v) for v in next(l for l in txt.splitlines() if l.startswith('MAP ')).split()[1:3]]
    prof = dict(prof, W=W_, H=H_)
    E = EngineModule()
    obs, spawn = {}, {}

    def reply(did, raw):
        obs.setdefault(did, []).append(raw)
        b = B.parse_block(raw)
        return policy(rng, b, prof)

    res = E.run((MAPS / f'{mapname}.map').read_bytes(), reply, bot_spawn=lambda d, s: spawn.__setitem__(d, s), debug=0, seed=seed)
    return dict(map=mapname, seed=seed, prof=prof, result=res.__dict__, obs=obs, spawn=spawn, replay=E.replay('ta', 'tb'))


if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    maps = sys.argv[2].split(',')
    seeds = [int(s) for s in sys.argv[3].split(',')]
    import os
    prof = dict(split=float(os.environ.get('P_SPLIT', 0.04)), junk=float(os.environ.get('P_JUNK', 0.002)), sprint=0.08, sonar=0.4, p3=float(os.environ.get('P_P3', 1.0)))
    for m in maps:
        for s in seeds:
            g = run(m, s, prof)
            n = sum(len(v) for v in g['obs'].values())
            with gzip.open(out / f'{m}-s{s}.truth.pkl.gz', 'wb') as f:
                pickle.dump(g, f)
            print(m, s, g['result']['rounds'], g['result']['winner'], 'blocks', n, flush=True)

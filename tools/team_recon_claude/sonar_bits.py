"""Which payload bits of the target's 64-bit sonars covary with observable sender state?
Mutual information (bits) per payload bit vs candidate fields; fit on games A, check on games B."""
import sys, glob, collections, json
import numpy as np, pandas as pd
sys.path.insert(0, 'tools')
import recon

m = pd.read_csv('out/corpus/manifest.csv', dtype={'game_id': str})
m = m[m.target_submission == 8264].sort_values('completed_at')
games = list(m.game_id)
side = dict(zip(m.game_id, m.side))


def collect(gids, cap=20000):
    rows = []
    for gid in gids:
        g = recon.Game(f'public_replays/team-306/{gid}.replay')
        st = {'r': 0}
        t = side[gid]

        def cb(kind, **k):
            if kind == 'round':
                st['r'] = k['round']
            elif kind == 'sonar':
                s = g.dragons.get(k['sender'])
                if s and s.team == t and st.setdefault('n', 0) < 3000:
                    st['n'] += 1
                    rel = 'FRBL'[(recon.DIRS.index(k['direction']) - recon.DIRS.index(s.facing)) % 4]
                    rows.append(dict(v=k['value64'], r=st['r'], x=s.body[0][0], y=s.body[0][1], L=len(s.body),
                                     facing=s.facing, dir=k['direction'], rel=rel, hit=k['hitkind'],
                                     units=g.unit_count(t), id=s.id, map=g.board.name))
        g.run(cb)
    return pd.DataFrame(rows)


def mi(bit, f):
    ct = pd.crosstab(f, bit).values.astype(float)
    p = ct / ct.sum()
    px = p.sum(1, keepdims=True); py = p.sum(0, keepdims=True)
    nz = p > 0
    return float((p[nz] * np.log2(p[nz] / (px @ py)[nz])).sum())


A = collect(games[:10]); B = collect(games[10:20])
fields = {'facing': lambda d: d.facing, 'dir': lambda d: d.dir, 'rel': lambda d: d.rel, 'x': lambda d: d.x, 'y': lambda d: d.y,
          'round': lambda d: d.r, 'round//8': lambda d: d.r // 8, 'len': lambda d: d.L.clip(upper=20), 'units': lambda d: d.units,
          'hit(outcome)': lambda d: d.hit, 'id%64': lambda d: d.id % 64}
out = {}
for name, D in (('A', A), ('B', B)):
    v = D.v.astype('uint64').values
    tab = {}
    for f, fn in fields.items():
        col = fn(D).values
        tab[f] = [round(mi((v >> np.uint64(i)) & np.uint64(1), col), 3) for i in range(64)]
    out[name] = tab
    print(name, len(D))
res = pd.DataFrame({f: out['A'][f] for f in fields}, index=[f'b{i}' for i in range(64)])
resB = pd.DataFrame({f: out['B'][f] for f in fields}, index=[f'b{i}' for i in range(64)])
pd.set_option('display.width', 200)
print(res.round(2).to_string())
print('held-out agreement of per-bit argmax field (MI>0.3):')
for i in range(64):
    a = res.iloc[i]; b = resB.iloc[i]
    if a.max() > 0.3:
        print(f'b{i}', a.idxmax(), a.max(), '| B:', b.idxmax(), b.max())
res.to_csv('out/agg/sonar_bit_mi_A.csv'); resB.to_csv('out/agg/sonar_bit_mi_B.csv')

"""Aggregate early.py over a panel: per arm, split by W/L (and by opponent-side for comparison).
usage: early_agg.py OUT [ARM] [CUT]"""
import collections, json, sys, statistics as st
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import early
out = Path(sys.argv[1]); arm = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
cut = int(sys.argv[3]) if len(sys.argv) > 3 else 200
rows = [json.loads(l) for l in open(out / 'results.jsonl')]
G = collections.defaultdict(lambda: dict(n=0, elim=[], snaps=collections.defaultdict(list), deaths=collections.Counter(), nd=0, portal=0, fh=0, ages=[]))
per = []
for r in rows:
    if 'score' not in r or (arm and r['arm'] != arm): continue
    rp = next((p for p in (out / 'replays').glob(r['key'].replace('|', '__') + '*')), None) or next((p for p in (out / 'replays').glob('*') if r['key'].replace('|', '_') in p.name), None)
    if rp is None: print('no replay', r['key']); continue
    a = early.analyse(str(rp), cut); me, th = (a['teams']['A'], a['teams']['B']) if r['seat'] == 'A' else (a['teams']['B'], a['teams']['A'])
    res = 'W' if r['score'] == 1 else ('L' if r['score'] == 0 else 'D')
    per.append((r['map'], r['opp'][:14], r['seat'], res, me['elim'], th['elim'], me['snap'][100], th['snap'][100], me['snap'][200], th['snap'][200], me['n_early_deaths'], th['n_early_deaths']))
    for side, x in (('me_' + res, me), ('opp_' + res, th)):
        g = G[side]; g['n'] += 1; g['elim'].append(x['elim']); g['nd'] += x['n_early_deaths']; g['portal'] += x['near_portal']; g['fh'] += x['friendly_h2h']
        for k, v in x['snap'].items(): g['snaps'][k].append(v)
        g['deaths'].update(x['deaths'])
for side in sorted(G):
    g = G[side]; n = g['n']
    el = [e for e in g['elim'] if e is not None]
    print(f"== {side} games {n}  eliminated {len(el)} (median r{sorted(el)[len(el)//2] if el else '-'})  early deaths/game {g['nd']/n:.1f}  near-portal {g['portal']}  friendly-h2h pairs {g['fh']}")
    print('   units/total medians', {k: (st.median(u for u, t in v), st.median(t for u, t in v)) for k, v in sorted(g['snaps'].items())})
    tot = sum(g['deaths'].values()) or 1
    print('   ', ', '.join(f"{k} {v} ({100*v/tot:.0f}%)" for k, v in g['deaths'].most_common(10)))
print('\nmap opp seat res elim_me elim_op u/t100 me op u/t200 me op deaths me op')
for p in sorted(per): print(*p)

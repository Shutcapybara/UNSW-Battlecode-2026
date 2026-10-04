"""Audit alternative cycle counting on the frozen peer96 sample, retaining approximate snapshots.
No counterfactual engine evaluation. This isolates predicate consistency, not immediate legality.
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path
from entry_contract_check import read_functions

p = argparse.ArgumentParser()
p.add_argument('--repo', type=Path, required=True)
p.add_argument('--index', type=Path, required=True)
p.add_argument('--selection', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
sys.path.insert(0, str(a.repo))
from tools.analysis.features import frame as F
E = {'CAP': 16}
ref = '9b0da8f7848458ebcf2b77aeab293355df741b36'
read_functions(ref, 'tools/kanazawa/q_dose.py', ['reach', 'occupied'], E)
read_functions(ref, 'tools/kanazawa/q_cycle.py', ['longest_cycle'], E)
reach, occupied, cycle = [E[n] for n in ['reach', 'occupied', 'longest_cycle']]
ids = json.loads(a.selection.read_text())['game_ids']
idx = {m['game_id']: m for m in map(json.loads, a.index.read_text().splitlines())}
a.out.mkdir(exist_ok=True, parents=True)
f = a.out/'games.jsonl'
done = {r['game'] for r in map(json.loads, f.read_text().splitlines())} if f.exists() else set()
for gid in ids:
    if gid in done:
        continue
    m = idx[gid]
    path = a.repo/'public_replays/corpus/replays'/f'{gid}.replay'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == m['sha256']
    g = F.decode(path)
    assert g['winner'].lower() == m['winner']
    assert hashlib.sha256(F._reader(path).object(0,0).text(0).encode()).hexdigest() == m['map_hash']
    ours = 'A' if m['team_a'] == 7 else 'B'
    R, nbr = g['rounds'], g['nbr']
    record = dict(game=gid, series=m['series_id'], ranked=m['ranked'], map=g['map'], map_hash=m['map_hash'],
                  own_submission=g['bot'+ours], payload_sha256=m['sha256'], sides=[])
    for side in 'AB':
        q = min(i for i,(tm,_) in R[0].items() if tm == side)
        death = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        dr, cause = (death['round'], death['cause']) if death else (None, None)
        counts = collections.Counter()
        examples = []
        for t in range(len(R)-1):
            if q not in R[t] or q not in R[t+1]:
                break
            b0, b1 = R[t][q][1], R[t+1][q][1]
            u,v = b0[0],b1[0]
            if u == v or v not in nbr.get(u, ()):
                continue
            length = len(b1)
            occ1 = occupied(R[t+1]) - {v}
            P = reach(nbr, u, v, occ1)
            C = len(P)
            if C >= 16 or (C >= 3 and cycle(P+[u], nbr) >= length+1):
                continue
            occ0 = occupied(R[t])
            neck = b0[1] if len(b0)>1 else None
            alts = []
            for w in nbr.get(u, ()):
                if w is None or w == v or w == neck or w in occ0:
                    continue
                Q = reach(nbr,u,w,occ1-{w})
                orb = len(Q) < 16 and len(Q) >= 3 and cycle(Q+[u],nbr) >= length+1
                alts.append((len(Q),orb,w))
            label = cause if dr is not None and t+1 <= dr <= t+6 else 'none'
            for k in [4,8,16]:
                if C >= k:
                    continue
                old = any(c >= k for c,orb,w in alts)
                corrected = any(c >= k or orb for c,orb,w in alts)
                counts[f'{k}:veto'] += 1
                counts[f'{k}:lab:{label}'] += 1
                counts[f'{k}:old_alt'] += old
                counts[f'{k}:same_predicate_alt'] += corrected
                censored = label == 'none' and dr is None and g['last_round'] < t+6
                counts[f'{k}:none_censored'] += censored
                if corrected != old and len(examples)<4:
                    examples.append(dict(round=t,dose=k,capacity=C,queen_length=length,alternatives=alts,label=label))
        record['sides'].append(dict(side=side,ours=side==ours,death_round=dr,death_cause=cause,counts=dict(counts),changed_examples=examples))
    with f.open('a') as out:
        out.write(json.dumps(record)+'\n')
    print(gid, 'complete', flush=True)
rows = [json.loads(x) for x in f.read_text().splitlines()]
total = {x:collections.Counter() for x in ['us','opp']}
strata = collections.Counter()
for r in rows:
    strata[str((r['ranked'],r['own_submission']))] += 1
    for s in r['sides']:
        total['us' if s['ours'] else 'opp'].update(s['counts'])
        if s['death_cause']:
            total['us' if s['ours'] else 'opp']['deaths:'+s['death_cause']] += 1
(a.out/'summary.json').write_text(json.dumps(dict(games=len(rows),series=len({r['series'] for r in rows}),
    strata=dict(strata),totals=total,scope='Same snapshot/tail assumptions as peer. Only alternative-cycle predicate corrected; no exact legality, candidate-body correction, causal value or new sample.'),indent=2)+'\n')

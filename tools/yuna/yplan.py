#!/usr/bin/env python3
"""Yuna fixture plan: cands x opps x maps x sides.  Fixture id hashes (cand sha, opp sha, map sha, side)
so identical sources share ids across plans (deterministic games are never double counted).
python3 tools/yuna/yplan.py --repo R --out plan.json --cand name[=path] ... --opps a,b --maps pub|m1,m2 [--sides AB]"""
import argparse, json, hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from yrun import tree_sha
PUB = ['autarky', 'default', 'devil', 'dilemma', 'queen_of_spades', 'schooltime', 'trauma', 'trophy', 'pub/portals_rec', 'pub/slithery_rec']
SYN = ['mc26_portal_quartet', 'mc26_crossroads', 'mc26_relay_depots', 'mc26_pinwheel', 'md26_orchard_narrow_s0', 'mc26_far_harbors']
EXTRA = ['arena', 'Colosseum', 'default_small', 'stronghold', 'big_empty']
def mpath(R, m):
    for p in (Path('maps') / f'{m}.map', Path('maps/new') / f'{m}.map'):
        if (R / p).exists(): return str(p)
    raise FileNotFoundError(m)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--cand', action='append', required=True); ap.add_argument('--opps', required=True)
    ap.add_argument('--maps', default='pub'); ap.add_argument('--sides', default='AB')
    a = ap.parse_args(); R = Path(a.repo)
    groups = {'pub': PUB, 'syn': SYN, 'extra': EXTRA}
    maps = []
    for tok in a.maps.split(','):
        maps += groups.get(tok, [tok])
    shas = {}
    def sha(p):
        if p not in shas: shas[p] = tree_sha(R / p)
        return shas[p]
    fx = []
    for c in a.cand:
        cn, cp = c.split('=', 1) if '=' in c else (c, f'bots/{c}')
        for o in a.opps.split(','):
            op = f'bots/{o}'
            for m in maps:
                mp = mpath(R, m); ms = hashlib.sha256((R / mp).read_bytes()).hexdigest()
                for s in a.sides:
                    fid = hashlib.sha256(f'{sha(cp)}|{sha(op)}|{ms}|{s}'.encode()).hexdigest()[:16]
                    fx.append(dict(id=fid, map=m, map_path=mp, cand=cn, cand_path=cp, opp=o, opp_path=op, side=s,
                                   cand_sha=sha(cp)[:12], opp_sha=sha(op)[:12]))
    order = {c: i for i, c in enumerate(dict.fromkeys(f['cand'] for f in fx))}
    fx.sort(key=lambda f: (f['map'] in ('pub/slithery_rec', 'schooltime'), f['opp'], f['map'], f['side'], order[f['cand']]))
    json.dump(dict(fixtures=fx), open(a.out, 'w'), indent=0)
    print(len(fx), 'fixtures ->', a.out)
if __name__ == '__main__': main()

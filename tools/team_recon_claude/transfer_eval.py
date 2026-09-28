import sys, json, pandas as pd, numpy as np
sys.path.insert(0, 'tools'); import recon
out = sys.argv[1]; ctl, graft = sys.argv[2], sys.argv[3]
r = pd.read_csv(f'{out}/results.csv')
def stream(path, side):
    g = recon.Game(path); acts = []
    def cb(kind, **k):
        if kind == 'action' and k['dragon'].team == side:
            acts.append((g.round, k['dragon'].id, str(k['action'])))
    res = g.run(cb); return acts, res
rows = []
for (opp, mp, side), grp in r.groupby(['opp', 'map', 'side']):
    x = {a: grp[grp.arm == a].iloc[0] for a in (ctl, graft)}
    pc = f"{out}/replays/{ctl}__{opp}__{mp[:-4]}__{side}.replay"; pg = pc.replace(ctl, graft)
    ac, rc = stream(pc, side); ag, rg = stream(pg, side)
    div = next((i for i, (a, b) in enumerate(zip(ac, ag)) if a != b), None)
    rows.append(dict(opp=opp, map=mp.split('__')[0], side=side, ctl=x[ctl].result, graft=x[graft].result,
                     diverged=div is not None or len(ac) != len(ag), first_div_round=(ac[div][0] if div is not None else None),
                     ctl_longest=rc[side]['longest'], graft_longest=rg[side]['longest'], ctl_total=rc[side]['total'], graft_total=rg[side]['total']))
P = pd.DataFrame(rows); P.to_csv(f'{out}/paired.csv', index=False)
w = lambda s: (s == 'W').sum()
print('fixtures', len(P), 'activation (diverged)', P.diverged.mean().round(3), 'median first divergence round', P.first_div_round.median())
print('control', f"{w(P.ctl)}-{(P.ctl=='L').sum()}", 'graft', f"{w(P.graft)}-{(P.graft=='L').sum()}", 'net', w(P.graft) - w(P.ctl))
print('flips W->L', ((P.ctl=='W')&(P.graft=='L')).sum(), 'L->W', ((P.ctl=='L')&(P.graft=='W')).sum())
print(P.groupby('opp').apply(lambda g: f"{w(g.ctl)}-{w(g.graft)} (ctl-graft wins of {len(g)})"))
bym = P.groupby('map').apply(lambda g: w(g.graft) - w(g.ctl)); print('net by map', bym.to_dict())
print('median final longest ctl/graft', P.ctl_longest.median(), P.graft_longest.median(), 'total', P.ctl_total.median(), P.graft_total.median())
json.dump(dict(fixtures=len(P), activation=float(P.diverged.mean()), ctl_wins=int(w(P.ctl)), graft_wins=int(w(P.graft)),
               net=int(w(P.graft) - w(P.ctl)), net_by_map={k: int(v) for k, v in bym.items()},
               flips_WL=int(((P.ctl=='W')&(P.graft=='L')).sum()), flips_LW=int(((P.ctl=='L')&(P.graft=='W')).sum())),
          open(f'{out}/summary.json', 'w'), indent=1)

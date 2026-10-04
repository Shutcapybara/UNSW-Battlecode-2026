#!/usr/bin/env python3
"""P-A02 preregistered target table: per dose vs parent (pool, seed 1), cluster bootstrap map x opp x seat (1,000, seed 7,
5th-95th): wall deaths/1k on classes C+E; queen alive@end (header) on trauma/portals/maze/weakhold; pearls@50 (raw
paired mean); class-B econ (normalised, card.py); plus queen veto exposure per dose (kz12_summary.json)."""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import card as C, panel as P  # noqa: E402

PARENT = 'carthage-05-free-sprint'
DOSES = [(4, 'asahi-03-kz12-k4'), (8, 'asahi-04-kz12-k8'), (16, 'asahi-05-kz12-k16')]
QMAPS = {'live/trauma', 'live/portals', 'live/maze', 'live/weakhold'}


def boot(m, f, nb=1000):
    g = list(m.groupby(C.CLUSTER).indices.values()); rng = np.random.default_rng(7)
    B = [f(m.iloc[np.concatenate([g[i] for i in rng.integers(0, len(g), len(g))])]) for _ in range(nb)]
    return f(m), float(np.percentile(B, 5)), float(np.percentile(B, 95))


out = []
Fp, _ = C.load_arm(PARENT, 'pool', [1])
for k, bot in DOSES:
    Fc, _ = C.load_arm(bot, 'pool', [1])
    C.normalise(Fc, Fp)
    cols = ['win', 'econ', 'q_alive', 'cls', 'pearls@50', 'death_wall_per1k']
    m = Fc[C.KEY + cols].merge(Fp[C.KEY + cols], on=C.KEY, suffixes=('_c', '_p'))
    ce, qm, b = m[m.cls_c.isin(['C', 'E'])], m[m.mapkey.isin(QMAPS)], m[m.cls_c == 'B']
    row = dict(dose=k, bot=bot,
               wall_CE=boot(ce, lambda x: (x.death_wall_per1k_c - x.death_wall_per1k_p).mean()),
               queen_target=boot(qm, lambda x: (x.q_alive_c - x.q_alive_p).mean()),
               queen_target_counts=f"{int(qm.q_alive_c.sum())}/{len(qm)} vs {int(qm.q_alive_p.sum())}/{len(qm)}",
               pearls50=boot(m, lambda x: (x['pearls@50_c'] - x['pearls@50_p']).mean()),
               econ_B=boot(b, lambda x: (x.econ_c - x.econ_p).mean()))
    sp = P.run_root(bot, 'pool') / 'kz12_summary.json'
    if sp.exists():
        s = json.load(open(sp))['by_map']
        row['veto_per1k'] = round(s['ALL']['queen_fire_per1k'], 1)
        row['veto_per1k_CE'] = {mk.split('/')[1]: round(v['queen_fire_per1k'], 1) for mk, v in s.items()
                                if mk != 'ALL' and P.map_class(mk) in 'CE'}
    out.append(row)
    print(json.dumps(row))
p = ROOT / 'docs/learning/results/asahi/P-A02-kz12-targets-s1.json'
p.write_text(json.dumps(out, indent=1))

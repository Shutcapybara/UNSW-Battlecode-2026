"""K-1: win-probability residual per map for team 7 (actual - expected under a map-free strength model).

Fits tools/performance_model.py with maps=False (team strength + per-map initiative b[map]) on the whole corpus
index, then for each map reports team 7's mean(actual score - predicted), its standard error, and n.
Also reports the map-affinity model (maps=True) t[7,map] for comparison.
"""
import json, os, sys
from pathlib import Path
import numpy as np

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(REPO))
from tools.performance_model import fit, predictions, unpack  # noqa: E402


def main(out):
    rows = [json.loads(l) for l in open(REPO / 'public_replays/corpus/index.jsonl')]
    rows = [r for r in rows if r.get('winner') in ('a', 'b', 'draw') and r.get('status', 'completed') == 'completed']
    teams = sorted({r['team_a'] for r in rows} | {r['team_b'] for r in rows})
    maps = sorted({r['map_name'] for r in rows})
    ti = {t: i for i, t in enumerate(teams)}
    mi = {m: i for i, m in enumerate(maps)}
    a = np.array([ti[r['team_a']] for r in rows])
    c = np.array([ti[r['team_b']] for r in rows])
    b = np.array([mi[r['map_name']] for r in rows])
    y = np.array([1.0 if r['winner'] == 'a' else 0.5 if r['winner'] == 'draw' else 0.0 for r in rows])
    data = (a, c, b, y)
    n, m = len(teams), len(maps)
    m0 = fit(data, n, m, q=0, maps=False)
    p = predictions(m0, data, n, m)
    m1 = fit(data, n, m, q=0, maps=True, start=m0)
    _, t1, _, _, _ = unpack(m1['x'], n, m, 0, True)
    us = ti[7]
    res = {}
    for mp in maps + ['ALL']:
        sel = ((a == us) | (c == us)) & ((b == mi[mp]) if mp != 'ALL' else True)
        act = np.where(a[sel] == us, y[sel], 1 - y[sel])
        pre = np.where(a[sel] == us, p[sel], 1 - p[sel])
        r = act - pre
        res[mp] = dict(n=int(sel.sum()), actual=float(act.mean()), expected=float(pre.mean()), residual=float(r.mean()),
                       se=float(r.std(ddof=1) / np.sqrt(max(sel.sum(), 2))),
                       map_affinity_t=float(t1[us, mi[mp]]) if mp != 'ALL' else None)
    out_d = dict(model='performance_model maps=False (strength + map initiative), fit on the full corpus index',
                 n_games=len(rows), n_teams=n, fit=dict(success=m0['success'], objective=m0['objective']), per_map=res)
    json.dump(out_d, open(out, 'w'), indent=1)
    for k, v in res.items():
        print(f"{k:22s} n={v['n']:4d} act={v['actual']:.2f} exp={v['expected']:.2f} res={v['residual']:+.3f}±{v['se']:.3f} t={v['map_affinity_t']}")


if __name__ == '__main__':
    main(sys.argv[1])

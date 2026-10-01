"""TT: how each top team wins and loses on each map (from the v5 .traj.json files), next to its map residual.

    .venv/bin/python tools/tt/map_mechanism.py

Per team x map: games, win rate, the residual from tools/tt/map_specialists.py (ranked), how games end (elimination /
round limit, as % of games), median own and opponent units and total length at r100 and r300, and in round-limit
games the median own and opponent longest dragon at the end. Writes game_stats/runs/tt-map-mechanism.json.
"""
import glob, json
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TEAMS = {'Heartbreaker': (62, ROOT.parent / 'wt-hb1/build/hb1/v5/corpus'), 'cheji bt': (70, ROOT / 'build/tt/team70/v5/corpus'),
         'Stockfish': (206, ROOT / 'build/tt/team206/v5/corpus'), 'forgot to mention': (264, ROOT / 'build/tt/team264/v5/corpus'),
         'Cache me outside': (952, ROOT / 'build/tt/team952r/v5/corpus')}


def one(f):
    t = json.load(open(f))
    s, o = t['side'], 'B' if t['side'] == 'A' else 'A'
    res = t['result']
    tr = {x['round']: x for x in t['traj']}
    row = dict(map=t['map'], won=res.get('winner') == s, limit=res.get('reason') == 'roundLimit', rounds=res.get('rounds'),
               L_end=tr['end'][s]['longest'], oL_end=tr['end'][o]['longest'])
    for r in (100, 300):
        x = tr.get(r)
        for k, side in (('', s), ('o', o)):
            row[f'{k}U{r}'] = x[side]['units'] if x else None
            row[f'{k}T{r}'] = x[side]['total'] if x else None
    return row


def main():
    spec = json.loads((ROOT / 'game_stats/runs/tt-map-specialists.json').read_text())['teams']
    out = {}
    with Pool(12) as pool:
        for name, (tid, d) in TEAMS.items():
            df = pd.DataFrame(pool.map(one, glob.glob(str(d / '*.traj.json')), chunksize=32))
            res = spec[str(tid)]['maps']
            rows = []
            for m, g in df.groupby('map'):
                lim = g[g.limit]
                rows.append(dict(map=m, n=len(g), resid=round(100 * res[m]['resid']) if m in res else None,
                                 win=round(100 * g.won.mean()), elimW=round(100 * (g.won & ~g.limit).mean()),
                                 elimL=round(100 * (~g.won & ~g.limit).mean()), limW=round(100 * (g.won & g.limit).mean()),
                                 limL=round(100 * (~g.won & g.limit).mean()),
                                 U100=g.U100.median(), oU100=g.oU100.median(), T100=g.T100.median(), oT100=g.oT100.median(),
                                 T300=g.T300.median(), oT300=g.oT300.median(),
                                 L_end_lim=lim.L_end.median(), oL_end_lim=lim.oL_end.median()))
            t = pd.DataFrame(rows).sort_values('resid', ascending=False).set_index('map')
            print(f'== {name}\n{t.to_string()}\n')
            out[name] = t.reset_index().to_dict('records')
    (ROOT / 'game_stats/runs/tt-map-mechanism.json').write_text(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()

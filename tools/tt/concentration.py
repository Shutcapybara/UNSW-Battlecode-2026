"""TT: does culling show up as concentration? Trajectories of the three teams from the v5 .traj.json files.

    .venv/bin/python tools/tt/concentration.py

Per team: how games end (elimination vs round limit, won/lost), and the subject's units / longest / total length at
fixed rounds (medians over games still running), plus longest/total (share of material in the longest dragon).
Heartbreaker's rows come from ../wt-hb1/build/hb1 (corpus set). Writes game_stats/runs/tt-concentration.json.
"""
import glob, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TEAMS = {'Heartbreaker': ROOT.parent / 'wt-hb1/build/hb1/v5/corpus', 'cheji bt': ROOT / 'build/tt/team70/v5/corpus',
         'Stockfish': ROOT / 'build/tt/team206/v5/corpus', 'forgot to mention': ROOT / 'build/tt/team264/v5/corpus',
         'Cache me outside (ranked)': ROOT / 'build/tt/team952r/v5/corpus'}
ROUNDS = (50, 100, 200, 300, 400, 490)

out = {}
for name, d in TEAMS.items():
    ends, rows = [], []
    for f in glob.glob(str(d / '*.traj.json')):
        t = json.load(open(f))
        s, o = t['side'], 'B' if t['side'] == 'A' else 'A'
        res = t['result']
        tr = {x['round']: x for x in t['traj']}
        e = tr['end']
        ends.append(dict(reason=res.get('reason'), won=res.get('winner') == s, L=e[s]['longest'], T=e[s]['total'],
                         U=e[s]['units'], oL=e[o]['longest'], oT=e[o]['total']))
        for r in ROUNDS:
            if r in tr:
                rows.append(dict(round=r, units=tr[r][s]['units'], longest=tr[r][s]['longest'], total=tr[r][s]['total'],
                                 o_units=tr[r][o]['units'], o_longest=tr[r][o]['longest'], o_total=tr[r][o]['total']))
    E, R = pd.DataFrame(ends), pd.DataFrame(rows)
    lim = E[E.reason == 'roundLimit']
    summ = dict(games=len(E), win=float(E.won.mean()), elim_win=int((E.won & (E.reason == 'teamEliminated')).sum()),
                elim_loss=int((~E.won & (E.reason == 'teamEliminated')).sum()), limit_win=int(lim.won.sum()),
                limit_loss=int((~lim.won).sum()), limit_win_rate=float(lim.won.mean()),
                limit_loss_with_material_lead=float((lim[~lim.won]['T'] > lim[~lim.won].oT).mean()),
                end_longest_median_limit=float(lim.L.median()), end_total_median_limit=float(lim['T'].median()),
                end_units_median_limit=float(lim.U.median()), opp_end_longest_median_limit=float(lim.oL.median()))
    R['share'] = R.longest / R.total.clip(lower=1)
    med = R.groupby('round')[['units', 'longest', 'total', 'share', 'o_units', 'o_longest', 'o_total']].median().round(2)
    out[name] = dict(summary=summ, by_round=med.reset_index().to_dict('records'))
    print(f'\n== {name}'); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in summ.items()}); print(med.to_string())
(ROOT / 'game_stats/runs/tt-concentration.json').write_text(json.dumps(out, indent=1))

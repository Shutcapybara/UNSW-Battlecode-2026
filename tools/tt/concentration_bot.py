"""TT: the same concentration trajectory for one of our bots, from panel replays (run_panel naming
s<seed>__<map>__<botA>__<botB>.replay).

    .venv/bin/python tools/tt/concentration_bot.py BOT PANEL_DIR [PANEL_DIR ...]
"""
import json, sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
import recon

ROUNDS = (50, 100, 200, 300, 400, 490)


def one(args):
    path, side = args
    g = recon.Game(str(path))
    o = 'B' if side == 'A' else 'A'
    snaps = {}

    def stat(t):
        al = [d for d in g.dragons.values() if d.alive and d.team == t]
        return len(al), max([len(d.body) for d in al] or [0]), sum(len(d.body) for d in al)

    def cb(kind, **k):
        if kind == 'round' and k['round'] in ROUNDS:
            snaps[k['round']] = (stat(side), stat(o))
    res = g.run(cb)
    e, eo = stat(side), stat(o)
    return [dict(round=r, units=s[0], longest=s[1], total=s[2], o_units=x[0], o_longest=x[1], o_total=x[2])
            for r, (s, x) in snaps.items()], dict(reason=res.get('reason'), won=res.get('winner') == side, L=e[1], T=e[2],
                                                   U=e[0], oL=eo[1], oT=eo[2])


if __name__ == '__main__':
    bot = sys.argv[1]
    work = []
    for d in sys.argv[2:]:
        for p in sorted(Path(d).glob('replays/*.replay')):
            _, _, a, b = p.stem.split('__')
            if bot in (a, b):
                work.append((p, 'A' if a == bot else 'B'))
    rows, ends = [], []
    with Pool(12) as pool:
        for r, e in pool.imap_unordered(one, work):
            rows += r; ends.append(e)
    E, R = pd.DataFrame(ends), pd.DataFrame(rows)
    lim = E[E.reason == 'roundLimit']
    print(bot, 'games', len(E), 'win', round(E.won.mean(), 3), '| elim W/L', int((E.won & (E.reason == 'teamEliminated')).sum()),
          int((~E.won & (E.reason == 'teamEliminated')).sum()), '| limit W/L', int(lim.won.sum()), int((~lim.won).sum()),
          'limit win rate', round(lim.won.mean(), 3), '| limit losses with material lead',
          round((lim[~lim.won]['T'] > lim[~lim.won].oT).mean(), 3))
    R['share'] = R.longest / R.total.clip(lower=1)
    print(R.groupby('round')[['units', 'longest', 'total', 'share', 'o_units', 'o_longest', 'o_total']].median().round(2).to_string())

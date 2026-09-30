"""TT: a bot's panel record by opponent, with how games end and both sides' longest dragon at the end.

    .venv/bin/python tools/tt/by_opponent.py BOT PANEL_DIR [PANEL_DIR ...]
"""
import sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
import recon


def one(args):
    path, side, opp = args
    g = recon.Game(str(path))
    o = 'B' if side == 'A' else 'A'
    res = g.run(lambda kind, **k: None)

    def stat(t):
        al = [d for d in g.dragons.values() if d.alive and d.team == t]
        return len(al), max([len(d.body) for d in al] or [0]), sum(len(d.body) for d in al)
    s, x = stat(side), stat(o)
    lim = res.get('reason') != 'teamEliminated'
    won = res.get('winner') == side
    return dict(opp=opp, out=('limW' if won else 'limL') if lim else ('elimW' if won else 'elimL'),
                L=s[1], T=s[2], oL=x[1], oT=x[2], lim=lim)


if __name__ == '__main__':
    bot = sys.argv[1]
    work = []
    for d in sys.argv[2:]:
        for p in sorted(Path(d).glob('replays/*.replay')):
            _, _, a, b = p.stem.split('__')
            if bot in (a, b):
                work.append((p, 'A' if a == bot else 'B', b if a == bot else a))
    with Pool(12) as pool:
        d = pd.DataFrame(pool.map(one, work))
    t = d.groupby('opp')['out'].value_counts().unstack(fill_value=0).reindex(columns=['elimW', 'limW', 'limL', 'elimL'], fill_value=0)
    lim = d[d.lim].groupby('opp')[['L', 'oL', 'T', 'oT']].median()
    t = t.join(lim.rename(columns=dict(L='our longest (limit games)', oL='their longest', T='our total', oT='their total')))
    print(bot); print(t.to_string())

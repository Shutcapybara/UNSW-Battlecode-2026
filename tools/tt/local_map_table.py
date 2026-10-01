"""TT: our local bots' z1 panel results per map (16 side-games per map per seed), to compare with the ladder map
regimes (tools/tt/map_mechanism.py).

    .venv/bin/python tools/tt/local_map_table.py [BOT ...]       (default: every bot with a z1 run under build/zoo)

Prints wins per map (of the games played) and the share of the bot's wins that came by elimination.
Writes game_stats/runs/tt-local-map-table.json.
"""
import glob, json, re, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ELIM = ['trophy', 'devil', 'queen_of_spades', 'dilemma', 'default', 'autarky']
LIMIT = ['schooltime', 'trauma', 'slithery_fight', 'portals']


def main():
    rows = []
    for d in sorted(glob.glob(str(ROOT / 'build/zoo/z1-*/index.jsonl'))):
        bot = re.sub(r'^z1-(.*)-[0-9a-f]{8}$', r'\1', Path(d).parent.name)
        if len(sys.argv) > 1 and bot not in sys.argv[1:]:
            continue
        x = pd.read_json(d, lines=True)
        x = x[(x.botA == bot) | (x.botB == bot)].drop_duplicates('game')
        if x.empty:
            continue
        side = (x.botA == bot).map({True: 'A', False: 'B'})
        x = x.assign(won=(x.winner == side), elim=x.reason.astype(str).str.contains('elimination'))
        rows.append(x.assign(bot=bot))
    d = pd.concat(rows)
    t = d.groupby(['bot', 'map']).won.mean().unstack()[ELIM + LIMIT]
    n = d.groupby('bot').size()
    t['elim maps'] = d[d['map'].isin(ELIM)].groupby('bot').won.mean()
    t['limit maps'] = d[d['map'].isin(LIMIT)].groupby('bot').won.mean()
    t['all'] = d.groupby('bot').won.mean()
    t['n'] = n
    t = t[t.n >= 100].sort_values('all', ascending=False)
    pd.set_option('display.width', 250)
    print((100 * t.drop(columns='n')).round(0).astype(int).assign(n=t.n).rename(columns=lambda c: c[:9]).to_string())
    (ROOT / 'game_stats/runs/tt-local-map-table.json').write_text(t.to_json(orient='index', indent=1))


if __name__ == '__main__':
    main()

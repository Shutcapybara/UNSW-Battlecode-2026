"""TT: at r250/r300, what observable state tells a bot the game will still be won by elimination?

    .venv/bin/python tools/tt/elim_state.py BOT PANEL_DIR [PANEL_DIR ...]

Per game: the bot's own units / total length at r250 and r300 (observable: UNIT_COUNT is in every round block), the
opponent's units (not observable), and how and when the game ended. Writes game_stats/runs/tt-elim-state-<BOT>.json.
"""
import json, sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
import recon


def one(args):
    path, side = args
    g = recon.Game(str(path))
    o = 'B' if side == 'A' else 'A'
    snap = {}

    def stat(t):
        al = [d for d in g.dragons.values() if d.alive and d.team == t]
        return len(al), sum(len(d.body) for d in al)

    def cb(kind, **k):
        if kind == 'round' and k['round'] in (250, 300):
            snap[k['round']] = (stat(side), stat(o))
    res = g.run(cb)
    row = dict(reason=res.get('reason'), won=res.get('winner') == side, rounds=res.get('rounds'), map=Path(path).stem.split('__')[1])
    for r, (s, x) in snap.items():
        row.update({f'u{r}': s[0], f't{r}': s[1], f'ou{r}': x[0], f'ot{r}': x[1]})
    return row


if __name__ == '__main__':
    bot = sys.argv[1]
    work = []
    for d in sys.argv[2:]:
        for p in sorted(Path(d).glob('replays/*.replay')):
            _, _, a, b = p.stem.split('__')
            if bot in (a, b):
                work.append((p, 'A' if a == bot else 'B'))
    with Pool(12) as pool:
        d = pd.DataFrame(pool.map(one, work))
    d['out'] = d.apply(lambda r: ('elimW' if r.won else 'elimL') if r.reason == 'teamEliminated' else ('limW' if r.won else 'limL'), axis=1)
    print(bot, 'games', len(d), d.out.value_counts().to_dict())
    print('elimination wins by end round:', pd.cut(d[d.out == 'elimW'].rounds, [0, 100, 200, 250, 300, 350, 400, 450, 501]).value_counts().sort_index().to_dict())
    live = d[d.u300.notna()]
    print('games alive at r300:', len(live), live.out.value_counts().to_dict())
    for col, bins in (('u300', [0, 20, 30, 40, 50, 200]), ('ou300', [0, 5, 10, 20, 30, 200])):
        t = live.groupby(pd.cut(live[col], bins))['out'].value_counts().unstack(fill_value=0)
        print(f'outcome by {col} ({"observable" if col[0] == "u" else "NOT observable"}):'); print(t.to_string())
    live = live.assign(ratio=live.u300 / live.ou300.clip(lower=1))
    print('outcome by own/opp units ratio at r300:'); print(live.groupby(pd.cut(live.ratio, [0, 1, 1.5, 2.5, 5, 1000]))['out'].value_counts().unstack(fill_value=0).to_string())
    (ROOT / 'game_stats' / 'runs' / f'tt-elim-state-{bot}.json').write_text(d.to_json(orient='records'))

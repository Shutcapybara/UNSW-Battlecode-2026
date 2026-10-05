#!/usr/bin/env python3
"""D-068 §C.1 fallback count on the server-like (sandbox, judge-clang wasm) build: Kageyama's logging builds print
`LOG p1_fallback` on any turn where `slot.observe` throws. Plays each bot against carthage-05-free-sprint, seed 1, both
seats, on the given maps (Devil and Dilemma first), in the sandbox via tools/cx/arena.run_game, keeps the bot's
transcripts and counts fallback lines against the bot's dragon-turns, per map.

    python tools/asahi/fbcount.py BOT [BOT ...] [--maps live/devil,live/dilemma,...] [--jobs 12] --out PATH
"""
import argparse, json, os, sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'tools/cx')); sys.path.insert(0, str(ROOT / 'tools/asahi'))
os.chdir(ROOT)
OPP = 'carthage-05-free-sprint'
FIRST = ['live/devil', 'live/dilemma']


def one(bot, m, seat, purge):
    from arena import run_game
    a, b = (bot, OPP) if seat == 'A' else (OPP, bot)
    g = run_game(f'maps/{m}.map', f'bots/{a}', f'bots/{b}', seed=1, sandbox=True, record=seat, purge=purge)
    turns = fb = 0
    for t in (g.get('transcripts') or {}).values():
        for turn in t['turns']:
            turns += 1
            fb += turn.get('output', '').count('p1_fallback')
    return dict(bot=bot, map=m, seat=seat, turns=turns, fallback=fb, winner=g.get('winner'), rounds=int(g.get('rounds', 0)),
                errors=[str(e)[:200] for e in g.get('errors', [])])


def main():
    import panel as P
    ap = argparse.ArgumentParser()
    ap.add_argument('bots', nargs='+'); ap.add_argument('--maps', default='')
    ap.add_argument('--jobs', type=int, default=12); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    maps = a.maps.split(',') if a.maps else FIRST + [m for m in P.POOL_MAPS if m not in FIRST]
    jobs = min(a.jobs, int(os.environ.get('ASAHI_MAX_WORKERS', '14')))
    rows = []
    for bot in a.bots:       # one serial game per bot builds the wasm once (purge), the rest reuse it
        rows.append(one(bot, maps[0], 'A', True)); print(json.dumps(rows[-1]), flush=True)
    todo = [(bot, m, s) for bot in a.bots for m in maps for s in 'AB' if not (m == maps[0] and s == 'A')]
    with ProcessPoolExecutor(jobs) as ex:
        futs = [ex.submit(one, b, m, s, False) for b, m, s in todo]
        for fu in as_completed(futs):
            try:
                rows.append(fu.result()); print(json.dumps(rows[-1]), flush=True)
            except Exception as e:  # noqa: BLE001
                print('ERR', type(e).__name__, str(e)[:300], flush=True)
    summ = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    for r in rows:
        for k in (r['map'], 'ALL'):
            s = summ[r['bot']][k]; s[0] += 1; s[1] += r['turns']; s[2] += r['fallback']
    out = {b: {k: dict(games=v[0], turns=v[1], fallback=v[2], per_1k=round(1000 * v[2] / max(v[1], 1), 3))
               for k, v in d.items()} for b, d in summ.items()}
    out['_errors'] = [r for r in rows if r['errors']]
    out['_games'] = len(rows)
    Path(a.out).write_text(json.dumps(dict(summary=out, rows=rows), indent=1))
    print(json.dumps({b: v.get('ALL') for b, v in out.items() if not b.startswith('_')}), flush=True)


if __name__ == '__main__':
    main()

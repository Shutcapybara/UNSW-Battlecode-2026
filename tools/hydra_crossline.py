#!/usr/bin/env python3
"""Aggregate a cross-line round-robin run dir: standings, per-pair matrices,
and replay-derived stats (pearls, splits, death causes, win types).

Usage: python3 tools/hydra_crossline.py build/crossline-rr1 [--pairs]
"""
import collections
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = dict(os.environ, PYTHONPYCACHEPREFIX='/tmp/hydra-pycache')
SHORT = {
    'fry-v14-stateful-size-aware-3': 'fry-v14',
    'hydra-v06-echo': 'hydra-v06',
    'kraken-v04-eval': 'kraken-v04',
    'leviathan-v07-local-cache': 'levi-v07',
    'ouroboros-v05-spread': 'ouro-v05',
}


def short(name):
    return SHORT.get(name, name[:20])


def replay_stats(path):
    out = subprocess.run(['python3', 'tools/leviathan/replay.py', str(path)],
                         capture_output=True, text=True, env=env, timeout=120)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def main():
    run = Path(sys.argv[1])
    results = json.load(open(run / 'results.json'))
    standings = list(open(run / 'standings.csv'))[1:]

    print('== standings (points; win=3 draw=1)')
    for row in standings:
        parts = row.strip().split(',')
        print(f"  {short(parts[0]):12s} {parts[6]:>4s} pts  {parts[2]}W {parts[3]}D {parts[4]}L  err={parts[5]}")

    bots = sorted({g['team_a'] for g in results} | {g['team_b'] for g in results})
    print('\n== head-to-head (W-D-L, focus bot rows)')

    # stats per bot aggregated from replays
    agg = {b: dict(games=0, pearls=0, splits=0, deaths=0, h2h=0, wins_elim=0,
                   wins_len=0, losses_elim=0, losses_len=0, rounds=0, longest=0,
                   longest_wins=0, len_games=0, PearlL=0) for b in bots}
    pair_rows = collections.defaultdict(dict)
    for g in results:
        a, b, w = g['team_a'], g['team_b'], g['winner']
        key = tuple(sorted((a, b)))
        i = 0 if a == key[0] else 1
        if w is None:
            tag = 'D'
        elif w == key[0]:
            tag = 'A'
        else:
            tag = 'B'
        pair_rows[key][g['map']] = pair_rows[key].get(g['map'], '') + tag
        tail = open(run / g['log'], errors='replace').read()[-300:]
        by_elim = 'by elimination' in tail or 'both teams eliminated' in tail
        for me, opp in ((a, b), (b, a)):
            s = agg[me]
            s['games'] += 1
            s['rounds'] += g['rounds']
            won = w == me
            if w is None:
                continue
            if won:
                if by_elim:
                    s['wins_elim'] += 1
                else:
                    s['wins_len'] += 1
            else:
                if by_elim:
                    s['losses_elim'] += 1
                else:
                    s['losses_len'] += 1
        rp = replay_stats(run / g['log'].replace('.log', '.replay')) if \
            (run / g['log'].replace('.log', '.replay')).exists() else None
        if rp:
            for me in (a, b):
                t = 'A' if me == a else 'B'
                s = rp['teams'][t]
                st = agg[me]
                st['pearls'] += s['pearls']
                st['splits'] += s['splits']
                st['deaths'] += sum(s['deaths'].values())
                st['h2h'] += s['deaths'].get('head-to-head', 0)
                if rp['reason'] == 'length':
                    st['len_games'] += 1
                    st['longest'] += s['final']['longest']
                    longest_both = max(rp['teams'][x]['final']['longest'] for x in 'AB')
                    if won and s['final']['longest'] == longest_both:
                        st['longest_wins'] += 1

    for me in bots:
        row = agg[me]
        n = row['games'] or 1
        print(f"\n  {short(me)}: pearls/g {row['pearls']/n:.1f}  splits/g {row['splits']/n:.1f}  "
              f"deaths/g {row['deaths']/n:.1f} (h2h {row['h2h']/n:.1f})")
        print(f"    wins: elim {row['wins_elim']} / length {row['wins_len']};   "
              f"losses: elim {row['losses_elim']} / length {row['losses_len']}")
        print(f"    length games: {row['len_games']}, own longest wins tiebreak "
              f"{row['longest_wins']}/{row['len_games']}")

    if '--pairs' in sys.argv:
        print('\n== per-pair per-map (letters = winner A/B/D, order = maps played)')
        for key, maps in sorted(pair_rows.items()):
            a, b = key
            aw = sum(v.count('A') for v in maps.values())
            bw = sum(v.count('B') for v in maps.values())
            print(f"  {short(a):12s} vs {short(b):12s}  {aw}-{bw}"
                  f"   maps:" )
            for m, tags in sorted(maps.items()):
                print(f"      {m:28s} {tags}")


if __name__ == '__main__':
    main()

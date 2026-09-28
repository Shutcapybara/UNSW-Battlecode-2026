"""Scan `experiment_data/*/` comparison runs for per-round series of the live-source bots (Q4 trajectory matching).

    python -m tools.analysis.scan_runs BOT1,BOT2,... > build/a1_local_series.csv

For every run whose manifest candidate or opponents intersect the bot list, every game on a live-pool map, and both
teams, emit the series values at r100/r250/r400/r499 from `opponents/<opp>/stats/<map>-candidate-<side>.csv`.
Columns: run, candidate, opponent, map, side, runner_version, seed_policy, sandbox, outcome, rounds, team, r, units,
total, longest, deaths, splits, pearls. The candidate's own rows are those with team == side.
"""
import csv
import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'experiment_data')
LIVE = {'devil', 'queen_of_spades', 'trauma', 'schooltime', 'portals', 'slithery_fight', 'default', 'trophy', 'dilemma', 'autarky'}
STAGES = {100, 250, 400, 499}


def main():
    bots = set(sys.argv[1].split(','))
    root = sys.argv[2] if len(sys.argv) > 2 else ROOT
    w = csv.writer(sys.stdout)
    w.writerow(['run', 'candidate', 'opponent', 'map', 'side', 'runner_version', 'seed_policy', 'sandbox', 'outcome', 'rounds', 'team', 'r', 'units', 'total', 'longest', 'deaths', 'splits', 'pearls'])
    runs = 0
    for mp in sorted(glob.glob(os.path.join(root, '*', 'manifest.json'))):
        d = os.path.dirname(mp)
        try:
            m = json.load(open(mp))
        except (OSError, ValueError):
            continue
        cand, opps = m.get('candidate'), m.get('opponents') or []
        if cand not in bots and not (set(opps) & bots):
            continue
        st = m.get('settings') or {}
        gcsv = os.path.join(d, 'games.csv')
        if not os.path.exists(gcsv):
            continue
        runs += 1
        for g in csv.DictReader(open(gcsv)):
            if g.get('map') not in LIVE or (cand not in bots and g.get('opponent') not in bots):
                continue
            sp = (g.get('statistics') or '').replace('.json', '.csv')
            p = os.path.join(d, sp)
            if not sp or not os.path.exists(p):
                continue
            for row in csv.DictReader(open(p)):
                try:
                    r = int(row['round'])
                except (KeyError, ValueError):
                    continue
                if r in STAGES:
                    w.writerow([os.path.basename(d), cand, g.get('opponent'), g['map'], g.get('side'), m.get('runner_version') or '', st.get('seed_policy'), st.get('sandbox'),
                                g.get('outcome'), g.get('rounds'), row['team'], r, row.get('units'), row.get('total'), row.get('longest'), row.get('deaths'), row.get('splits'), row.get('pearls')])
    print('runs scanned', runs, file=sys.stderr)


if __name__ == '__main__':
    main()

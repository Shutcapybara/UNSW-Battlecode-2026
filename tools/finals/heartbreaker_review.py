"""Review downloaded series replays: economy, queen safety and long-dragon losses.

Per-round curves are start-of-round snapshots plus the final post-round state.
Deaths and splits are reported separately; a longest-length drop is not itself a death.
"""
import argparse
from collections import Counter
import csv
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features.frame import decode


def review(directory, output, team_id=7, plots=True):
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    series = json.loads((directory / 'series.json').read_text())
    for game in series['games']:
        replay = directory / f'{game["id"]}.replay'
        metadata = directory / f'{game["id"]}.json'
        if not replay.exists() or not metadata.exists():
            continue
        detail = json.loads(metadata.read_text())
        seat = 'A' if detail['match']['teamAId'] == team_id else 'B'
        other = 'B' if seat == 'A' else 'A'
        frame = decode(replay)
        assert frame['winner'].lower() == detail['match']['winner']
        queens = {t: min(i for i, (side, b) in frame['rounds'][0].items() if side == t)
                  for t in (seat, other)}
        curves = []
        for rnd, state in enumerate(frame['rounds']):
            record = {'round': rnd}
            for t in (seat, other):
                bodies = [b for side, b in state.values() if side == t]
                record[t + '_total'] = sum(map(len, bodies))
                record[t + '_longest'] = max(map(len, bodies), default=0)
                record[t + '_units'] = len(bodies)
                record[t + '_queen'] = len(state[queens[t]][1]) if queens[t] in state else 0
            curves.append(record)
        with (output / f'{game["id"]}-curves.csv').open('w') as f:
            writer = csv.DictWriter(f, fieldnames=list(curves[0]))
            writer.writeheader()
            writer.writerows(curves)
        deaths = [d for d in frame['events']['deaths'] if d['team'] == seat]
        queen_death = next((d for d in deaths if d['id'] == queens[seat]), None)
        drops = []
        for before, after in zip(curves, curves[1:]):
            amount = before[seat + '_longest'] - after[seat + '_longest']
            if amount >= 3:
                rnd = before['round']
                drops.append(dict(round=rnd, drop=amount,
                    before=before[seat + '_longest'], after=after[seat + '_longest'],
                    deaths=[d for d in deaths if d['round'] == rnd],
                    splits=[s for s in frame['events']['splits'] if s['team'] == seat and s['round'] == rnd]))
        samples = {str(r): curves[r] for r in (0, 25, 50, 75, 100, 150, 200, 300, 400, 499)
                   if r < len(curves) - 1}
        events = frame['events']
        economics = {}
        for stop in (50, 100, 200, 300, 500):
            economics[str(stop)] = {t: dict(
                eaten=sum(e['team'] == t and e['round'] < stop for e in events['eats']),
                paid=sum(max(0, e.get('paid', 0)) for e in events['actions'] if e['team'] == t and e['round'] < stop),
                lost_length=sum(e['length'] for e in events['deaths'] if e['team'] == t and e['round'] < stop),
                splits=sum(e['team'] == t and e['round'] < stop for e in events['splits']))
                for t in (seat, other)}
        row = dict(id=game['id'], map=game['mapName'], seat=seat,
                   winner=frame['winner'], reason=frame['reason'], last_round=frame['last_round'],
                   samples=samples, final=frame['final'], queen_death=queen_death,
                   death_causes=dict(Counter(d['cause'] for d in deaths)),
                   largest_deaths=sorted(deaths, key=lambda d: -d['length'])[:12],
                   longest_drops=sorted(drops, key=lambda d: -d['drop'])[:12],
                   economics=economics,
                   tles=sum(e['tle'] for e in events['actions'] if e['team'] == seat),
                   invalid=sum(d['cause'] == 'invalid' for d in deaths))
        rows.append(row)
        if plots and frame['winner'] != seat:
            os.environ.setdefault('MPLCONFIGDIR', '/tmp/akaashi-matplotlib')
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
            for ax, metric in zip(axes, ('total', 'queen', 'longest')):
                for t, label in ((seat, 'Akaashi'), (other, 'Heartbreaker')):
                    ax.plot([r['round'] for r in curves], [r[t + '_' + metric] for r in curves], label=label)
                ax.set_ylabel(metric + ' length')
                ax.grid(alpha=.2)
                if queen_death:
                    ax.axvline(queen_death['round'], color='red', linestyle=':', alpha=.5)
            axes[0].legend(); axes[-1].set_xlabel('Protocol round')
            fig.suptitle(f'{game["mapName"]} — match {game["id"]}, Akaashi seat {seat}')
            fig.tight_layout(); fig.savefig(output / f'{game["id"]}-curves.png', dpi=140)
            plt.close(fig)
    (output / 'summary.json').write_text(json.dumps(rows, indent=2))
    for row in rows:
        t = row['seat']; other = 'B' if t == 'A' else 'A'
        samples = ', '.join(f'r{r}={v[t+"_total"]}/{v[other+"_total"]}'
                            for r, v in row['samples'].items() if r in ('50', '100', '200', '300'))
        print(row['id'], row['map'], 'WIN' if row['winner'] == t else 'LOSS', samples,
              'queen', row['queen_death'], 'large deaths', row['largest_deaths'][:3], flush=True)
    return rows


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--no-plots', action='store_true')
    args = ap.parse_args()
    review(args.directory, args.output, plots=not args.no_plots)

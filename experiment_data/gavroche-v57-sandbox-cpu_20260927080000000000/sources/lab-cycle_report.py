"""Durable cycle summaries and opening autopsies from the standard ledger."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from replay import Reader


def opening(path, end=30):
    root = Reader(path).object(0, 0)
    teams, alive = {}, set()
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            i = len(teams)
            teams[i] = 'AB'[int(p[1])]
            alive.add(i)
    stats = {t: Counter() for t in 'AB'}
    actor = None
    for event in root.items(3):
        kind, obj = event.num(0, 'H'), event.child(0)
        ident = obj.num()
        if kind == 0 and ident >= end:
            break
        if kind == 1:
            actor = ident
        elif kind == 3 and not obj.num(0, 'B') and actor in alive:
            stats[teams[actor]]['pearls'] += 1
        elif kind == 10:
            child = obj.num(4)
            teams[child] = teams[ident]
            alive.add(child)
            stats[teams[ident]]['splits'] += 1
        elif kind == 11:
            stats[teams[ident]]['deaths'] += 1
            alive.discard(ident)
    for team in 'AB':
        stats[team]['units_end'] = sum(teams[i] == team for i in alive)
    return stats


def summarize(folder, phases=False):
    rows = [json.loads(s) for s in (folder / 'ledger.jsonl').read_text().splitlines()]
    groups = defaultdict(Counter)
    for row in rows:
        for key in ('TOTAL', row['map_class'], 'side ' + row['side'],
                    row['map_class'] + ' ' + row['side'], row['opponent']):
            groups[key][row['result']] += 1
    lines = ['# ' + folder.name, '', '| Set | W | L | D | Errors |',
             '|---|---:|---:|---:|---:|']
    for key, counts in groups.items():
        lines.append('| %s | %d | %d | %d | %d |' % (key, *(counts[k] for k in 'WLDE')))
    lines += ['', 'CPU values are runner-rounded per-game percentiles; the ranges below are',
              'not pooled percentiles. Native CPU is unrecorded.']
    for metric in ('cpu_p50', 'cpu_p99', 'cpu_max'):
        values = [r[metric] for r in rows if r.get(metric) is not None]
        if values:
            lines.append('- %s: %.1f–%.1fM' % (metric, min(values) / 1e6, max(values) / 1e6))
    if phases:
        totals, count, evidence = defaultdict(Counter), Counter(), []
        cache_file = folder / 'opening.json'
        cached = {(r['map'], r['opponent'], r['side']): r
                  for r in json.loads(cache_file.read_text())} if cache_file.exists() else {}
        for row in rows:
            if row['result'] == 'E':
                continue
            side, other = row['side'], 'B' if row['side'] == 'A' else 'A'
            prior = cached.get((row['map'], row['opponent'], side))
            stats = ({side: prior['us'], other: prior['them']} if prior else
                     opening(folder / row['replay']))
            key = row['map_class']
            count[key] += 1
            for k, v in stats[side].items():
                totals[key]['us_' + k] += v
            for k, v in stats[other].items():
                totals[key]['them_' + k] += v
            evidence.append(dict(map=row['map'], opponent=row['opponent'], side=side,
                                 result=row['result'], us=dict(stats[side]), them=dict(stats[other])))
        (folder / 'opening.json').write_text(json.dumps(evidence, indent=2) + '\n')
        lines += ['', 'Rounds [0,30); earlier eliminations stop at the final state.', '',
                  '| Class | Games | Pearls us/them | Splits us/them | Units at end us/them |',
                  '|---|---:|---|---|---|']
        for key, n in count.items():
            pairs = ['%.2f / %.2f' % (totals[key]['us_' + k] / n, totals[key]['them_' + k] / n)
                     for k in ('pearls', 'splits', 'units_end')]
            lines.append('| %s | %d | %s |' % (key, n, ' | '.join(pairs)))
    text = '\n'.join(lines) + '\n'
    (folder / 'cycle-summary.md').write_text(text)
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folders', nargs='+', type=Path)
    parser.add_argument('--phases', action='store_true')
    args = parser.parse_args()
    for folder in args.folders:
        print(summarize(folder, args.phases))

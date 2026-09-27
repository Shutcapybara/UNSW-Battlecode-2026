"""Compare complete cycle fixtures, exposing every side/class/opponent and flip.

Usage: python3 tools/leviathan/converge.py BASE_G BASE_V --candidate CAND_G CAND_V
Source and map hashes must agree. No authority to update ACTIVE or promote bots.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def load(folders):
    rows, hashes = {}, {}
    for folder in folders:
        manifest = json.loads((folder / 'manifest.json').read_text())
        for row in map(json.loads, (folder / 'ledger.jsonl').read_text().splitlines()):
            key = (row['opponent'], row['map'], row['side'])
            if key in rows:
                raise ValueError('Duplicate fixture: ' + str(key))
            rows[key] = row
            hashes[key] = (manifest['sandbox'], manifest['hashes'][row['opponent']],
                           manifest['hashes'][row['map'] + '.map'])
    return rows, hashes


def compare(base_dirs, candidate_dirs):
    base, bh = load(base_dirs)
    candidate, ch = load(candidate_dirs)
    if base.keys() != candidate.keys():
        raise ValueError('Fixture sets differ: baseline=%d candidate=%d common=%d' %
                         (len(base), len(candidate), len(base.keys() & candidate.keys())))
    groups = defaultdict(lambda: [Counter(), Counter()])
    flips = []
    points = {'W': 1, 'D': .5, 'L': 0}
    for key, before in base.items():
        after = candidate[key]
        if bh[key] != ch[key]:
            raise ValueError('Changed opponent/map/meter mode: ' + str(key))
        if before['result'] not in points or after['result'] not in points:
            raise ValueError('Resolve failed fixtures before comparison: ' + str(key))
        for group in ('ALL', before['map_class'], 'side ' + before['side'],
                      before['map_class'] + ' ' + before['side'], before['opponent']):
            groups[group][0][before['result']] += 1
            groups[group][1][after['result']] += 1
        delta = points[after['result']] - points[before['result']]
        if delta:
            flips.append(dict(opponent=key[0], map=key[1], side=key[2],
                              before=before['result'], after=after['result'], delta=delta))
    lines = ['| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |',
             '|---|---:|---:|---:|---:|']
    for key, (a, b) in groups.items():
        score = b['W'] + .5*b['D'] - a['W'] - .5*a['D']
        lines.append('| %s | %s | %s | %+.1f | %+.0f |' %
                     (key, '–'.join(str(a[k]) for k in 'WLD'),
                      '–'.join(str(b[k]) for k in 'WLD'), score, 2*score))
    lines += ['', 'Improved: %d; regressed: %d; unchanged: %d. Deterministic fixtures.' %
              (sum(f['delta'] > 0 for f in flips), sum(f['delta'] < 0 for f in flips),
               len(base) - len(flips))]
    return '\n'.join(lines), flips


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline', nargs='+', type=Path)
    p.add_argument('--candidate', nargs='+', type=Path, required=True)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    table, flips = compare(args.baseline, args.candidate)
    print(table)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'comparison.md').write_text(table + '\n')
        (args.output / 'flips.json').write_text(json.dumps(flips, indent=2) + '\n')

"""Reproduce rollback statistics from frozen derived rows, without querying live state."""
import argparse
import json
import math
import random
from pathlib import Path
from statistics import NormalDist


def bootstrap(games, resamples=1000):
    groups = {}
    for game in games:
        groups.setdefault(game['series'], []).append(game['resid'])
    values = [groups[key] for key in sorted(groups)]
    rng = random.Random(7)
    samples = []
    for _ in range(resamples):
        picked = [values[rng.randrange(len(values))] for _ in values]
        samples.append(sum(map(sum, picked)) / sum(map(len, picked)))
    samples.sort()
    return dict(mean=sum(g['resid'] for g in games) / len(games),
                lo5=samples[50], hi95=samples[949], n=len(games), series=len(values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    games = json.loads(args.input.read_text())
    result = {name: bootstrap(rows) for name, rows in
              [('all', games), ('first40', games[:40]), ('last40', games[-40:])]}
    window = games[-40:]
    groups = {}
    for game in window:
        groups.setdefault(game['series'], []).append(game['resid'])
    n, k = len(window), len(groups)
    mean = result['last40']['mean']
    se = math.sqrt(k / (k - 1) * sum((sum(v) - len(v) * mean)**2 for v in groups.values()) / n**2)
    normal = NormalDist()
    difference_se = math.sqrt(2) * se
    absolute_cutoff = min(-0.08, -normal.inv_cdf(.95) * se)
    relative_cutoff = min(-0.08, -normal.inv_cdf(.95) * difference_se)
    result['design'] = dict(se=se, difference_se=difference_se, scenarios=[])
    for base in [0.0, mean]:
        for change in [0.0, -0.08, -0.15, -0.20]:
            result['design']['scenarios'].append(dict(
                baseline=base, change=change,
                absolute_probability=normal.cdf((absolute_cutoff - base - change) / se),
                relative_probability=normal.cdf((relative_cutoff - change) / difference_se)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

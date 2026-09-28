#!/usr/bin/env python3
"""Fit all-map ratings and paired lineage-bootstrap dominance for a frozen panel."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from benchmark import observed, targets
from benchmark_data import aliases
from game_stats import digest, read_parquet

PILOT_RUN_ID = 'bc86c2adc518428f8d77039e11111a97'
MAP_SWEEP_RUN_ID = '549ce497d5e14041bf5321a96787d7a0'
PILOT_MAPS = {'Colosseum', 'arena', 'autarky'}
ELO_SCALE = 400 / math.log(10)


def lineage(name):
    return re.split(r'-[vxs]\d+', name, maxsplit=1)[0]


def score_a(outcome):
    return 1.0 if outcome == 'A' else 0.5 if outcome == 'draw' else 0.0


def choose_one(key, records, campaign_run_id):
    """Keep one result per fixture, preserving pilot outcomes on the six repeats."""
    if len(records) == 1:
        return records[0]
    board = key[2]
    preferred = []
    if board in PILOT_MAPS:
        preferred.append(PILOT_RUN_ID)
    preferred.extend((campaign_run_id, MAP_SWEEP_RUN_ID))
    for run_id in preferred:
        match = [record for record in records if record['run_id'] == run_id]
        if match:
            if len(match) != 1:
                raise ValueError(f'Multiple records in preferred run for fixture {key}')
            return match[0]
    outcomes = {record['outcome'] for record in records}
    if len(outcomes) != 1:
        raise ValueError(f'Unresolved repeated fixture has conflicting outcomes: {key}')
    return min(records, key=lambda record: (record['run_started_at'], record['run_id']))


def fit_elo(records, bots):
    """Bradley–Terry fit with an A-seat term, then center at 1500."""
    index = {name: i for i, name in enumerate(bots)}
    n = len(bots)
    # The first n-1 strengths are free; the last is minus their sum. The final
    # parameter estimates the A-seat effect. Build the equivalent feature rows
    # once, then use a small dense Newton solve (one parameter per bot plus seat).
    observations = []
    for row in records:
        a, b = index[row['bot_a']], index[row['bot_b']]
        feature = [0.0] * n
        if a == n - 1:
            for i in range(n - 1):
                feature[i] -= 1.0
        else:
            feature[a] += 1.0
        if b == n - 1:
            for i in range(n - 1):
                feature[i] += 1.0
        else:
            feature[b] -= 1.0
        feature[-1] = 1.0
        observations.append((feature, score_a(row['outcome'])))

    def logistic(z):
        if z >= 0:
            e = math.exp(-z)
            return 1.0 / (1.0 + e)
        e = math.exp(z)
        return e / (1.0 + e)

    def evaluate(params, with_hessian=True):
        loss = 0.0
        grad = [0.0] * n
        hessian = [[0.0] * n for _ in range(n)] if with_hessian else None
        for feature, y in observations:
            z = sum(value * parameter for value, parameter in zip(feature, params))
            p = logistic(z)
            loss += max(z, 0.0) - y * z + math.log1p(math.exp(-abs(z)))
            error = p - y
            for i, value in enumerate(feature):
                grad[i] += error * value
            if with_hessian:
                weight = p * (1.0 - p)
                for i, left in enumerate(feature):
                    if left == 0.0:
                        continue
                    for j, right in enumerate(feature):
                        if right != 0.0:
                            hessian[i][j] += weight * left * right
        count = len(observations)
        loss /= count
        grad = [value / count for value in grad]
        if with_hessian:
            hessian = [[value / count for value in row] for row in hessian]
        return loss, grad, hessian

    def solve(matrix, vector):
        """Solve a small dense system with partial-pivot Gaussian elimination."""
        size = len(vector)
        augmented = [matrix[i][:] + [vector[i]] for i in range(size)]
        for col in range(size):
            pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
            if abs(augmented[pivot][col]) < 1e-14:
                raise RuntimeError('Bradley–Terry Hessian is singular')
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
            divisor = augmented[col][col]
            for j in range(col, size + 1):
                augmented[col][j] /= divisor
            for row in range(size):
                if row == col:
                    continue
                factor = augmented[row][col]
                if factor == 0.0:
                    continue
                for j in range(col, size + 1):
                    augmented[row][j] -= factor * augmented[col][j]
        return [augmented[i][size] for i in range(size)]

    params = [0.0] * n
    for _ in range(100):
        loss, grad, hessian = evaluate(params)
        if max(abs(value) for value in grad) < 1e-9:
            break
        step = solve(hessian, grad)
        fraction = 1.0
        for _ in range(60):
            candidate = [value - fraction * direction
                         for value, direction in zip(params, step)]
            candidate_loss, _, _ = evaluate(candidate, with_hessian=False)
            if candidate_loss <= loss:
                params = candidate
                break
            fraction *= 0.5
        else:
            if max(abs(value) for value in grad) >= 1e-8:
                raise RuntimeError('Bradley–Terry Newton fit did not converge')
            break
    else:
        raise RuntimeError('Bradley–Terry Newton fit exceeded 100 iterations')

    strength = params[:n - 1] + [-sum(params[:n - 1])]
    seat = params[-1]
    ratings = [1500 + ELO_SCALE * value for value in strength]
    objective, _, _ = evaluate(params, with_hessian=False)
    return ratings, float(ELO_SCALE * seat), float(objective)


def make_side_scores(records, bots, maps):
    """Return the two-side expected score for each bot/opponent/map cell."""
    games = {(row['bot_a'], row['bot_b'], row['map']): row for row in records}
    cells = {}
    for board in maps:
        for i, left in enumerate(bots):
            for right in bots[i + 1:]:
                forward = games.get((left, right, board))
                reverse = games.get((right, left, board))
                if forward is None or reverse is None:
                    continue
                cells[left, right, board] = (score_a(forward['outcome']) +
                                              1 - score_a(reverse['outcome'])) / 2
                cells[right, left, board] = 1 - cells[left, right, board]
    return cells


def profile_score(bot, board, bots, cells):
    by_lineage = defaultdict(list)
    for opponent in bots:
        if opponent == bot:
            continue
        value = cells.get((bot, opponent, board))
        if value is not None:
            by_lineage[lineage(opponent)].append(value)
    lineage_values = {family: sum(values) / len(values)
                      for family, values in by_lineage.items()}
    score = sum(lineage_values.values()) / len(lineage_values) if lineage_values else None
    return score, lineage_values


def compare_pair(left, right, bots, maps, cells, rng, replicates):
    per_map = {}
    for board in maps:
        by_lineage = defaultdict(list)
        opponents = []
        for opponent in bots:
            if opponent in (left, right):
                continue
            lvalue = cells.get((left, opponent, board))
            rvalue = cells.get((right, opponent, board))
            if lvalue is None or rvalue is None:
                continue
            opponents.append(opponent)
            by_lineage[lineage(opponent)].append(lvalue - rvalue)
        qualified = len(opponents) >= 3
        groups = [sum(values) / len(values)
                  for _, values in sorted(by_lineage.items())]
        if not qualified or len(groups) < 2:
            per_map[board] = dict(qualified=False, paired_opponents=len(opponents),
                                  opponent_lineages=len(groups), delta=None, low=None, high=None)
            continue
        draws = []
        for _ in range(replicates):
            draws.append(sum(groups[rng.randrange(len(groups))]
                             for _ in range(len(groups))) / len(groups))
        draws.sort()

        def percentile(q):
            position = (len(draws) - 1) * q
            low_index = int(position)
            high_index = min(low_index + 1, len(draws) - 1)
            weight = position - low_index
            return draws[low_index] * (1.0 - weight) + draws[high_index] * weight

        low, high = percentile(0.025), percentile(0.975)
        per_map[board] = dict(qualified=True, paired_opponents=len(opponents),
            opponent_lineages=len(groups), delta=sum(groups) / len(groups),
            low=float(low), high=float(high))
    qualified = [entry for entry in per_map.values() if entry['qualified']]
    complete = len(qualified) == len(maps)
    left_dominates = complete and all(entry['low'] >= 0 for entry in qualified) and any(
        entry['low'] > 0 for entry in qualified)
    right_dominates = complete and all(entry['high'] <= 0 for entry in qualified) and any(
        entry['high'] < 0 for entry in qualified)
    return dict(left=left, right=right, qualified_maps=len(qualified),
        total_maps=len(maps), left_dominates=left_dominates,
        right_dominates=right_dominates, by_map=per_map)


def main(campaign, output, replicates):
    manifest = json.loads((campaign / 'manifest.json').read_text())
    if manifest.get('benchmark_version') != 1 or manifest['pairing'] != 'round_robin':
        raise ValueError('Expected a version 1 round-robin benchmark campaign')
    bots, maps = manifest['bots'], manifest['maps']
    if not bots or not maps:
        raise ValueError('Campaign roster is empty')

    rows = read_parquet(ROOT / 'game_stats.parquet')
    source_aliases = aliases() | json.loads((campaign / 'aliases.json').read_text())
    grouped = observed(manifest, rows, source_aliases)
    selected = {key: choose_one(key, records, manifest['run_id'])
                for key, records in grouped.items()}
    expected = targets(manifest)
    missing = expected - selected.keys()
    extra = selected.keys() - expected
    if extra:
        raise ValueError(f'Panel includes {len(extra)} unexpected directional fixtures')
    if missing:
        examples = sorted(missing)[:8]
        raise ValueError(f'Panel is incomplete: {len(missing)} fixtures remain; examples: {examples}')

    records = [selected[key] for key in sorted(expected)]
    duplicates = sum(max(0, len(grouped[key]) - 1) for key in grouped)
    conflicting_repeats = [key for key, candidates in grouped.items()
                           if len({record['outcome'] for record in candidates}) > 1]
    cells = make_side_scores(records, bots, maps)
    if len(cells) != len(bots) * (len(bots) - 1) * len(maps):
        raise ValueError('One or more bot/map cells lack both starting sides')

    ratings, seat_advantage, objective = fit_elo(records, bots)
    rating_rows = [dict(bot=bot, elo=float(ratings[i])) for i, bot in enumerate(bots)]
    rating_rows.sort(key=lambda row: (-row['elo'], row['bot']))
    profiles = {bot: {} for bot in bots}
    map_leaders = []
    for board in maps:
        scores = []
        for bot in bots:
            value, by_lineage = profile_score(bot, board, bots, cells)
            profiles[bot][board] = dict(score=value, lineage_scores=by_lineage)
            scores.append((value, bot))
        leader_score, leader = max(scores)
        map_leaders.append(dict(map=board, leader=leader, score=leader_score))

    rng = random.Random(20260928)
    pair_results = []
    dominated = defaultdict(list)
    for i, left in enumerate(bots):
        for right in bots[i + 1:]:
            result = compare_pair(left, right, bots, maps, cells, rng, replicates)
            pair_results.append(result)
            if result['left_dominates']:
                dominated[right].append(left)
            if result['right_dominates']:
                dominated[left].append(right)
    frontier = sorted(bot for bot in bots if not dominated[bot])
    analysis = dict(
        generated_at=datetime.now(timezone.utc).isoformat(),
        campaign=str(campaign), run_id=manifest['run_id'],
        pilot_run_id=PILOT_RUN_ID, map_sweep_run_id=MAP_SWEEP_RUN_ID,
        bots=bots, maps=maps, expected_fixtures=len(expected), selected_fixtures=len(records),
        source_hashes={bot: manifest['effective_hashes'][bot] for bot in bots},
        recorded_bot_hashes={bot: digest(manifest['hashes']['bots/' + bot])
                             for bot in bots},
        map_hashes=manifest['map_hashes'], duplicate_records_discarded=duplicates,
        repeated_fixtures_with_conflicting_outcomes=len(conflicting_repeats),
        elo=dict(scale=400, centered_at=1500, ratings=rating_rows,
                 a_seat_advantage=seat_advantage, objective=objective),
        profiles=profiles, map_leaders=map_leaders, bootstrap=dict(
            method='paired opponent-lineage percentile bootstrap', replicates=replicates,
            interval=0.95, seed=20260928),
        pairwise=pair_results,
        dominated_by={bot: sorted(dominated[bot]) for bot in bots if dominated[bot]},
        frontier=frontier,
        dominance_rule=('Every map must have a qualified paired comparison, its 95% '
                        'lineage-bootstrap interval must stay at or above zero, and at '
                        'least one map interval must be strictly above zero.'))
    output.mkdir(parents=True, exist_ok=True)
    (output / 'frontier.json').write_text(json.dumps(analysis, indent=2, allow_nan=False) + '\n')

    lines = [
        '# All-map frontier panel', '',
        f"Campaign `{manifest['run_id']}`; {len(bots)} bots × {len(maps)} maps, "
        f"{len(records):,} distinct directional fixtures.", '',
        f"The {duplicates} repeated ledger rows were reduced to one result per fixture. "
        f"{len(conflicting_repeats)} repeated fixture had different outcomes; the six "
        'pilot/sweep overlaps use the pilot results.', '',
        '## ELO estimates', '',
        f"Bradley–Terry scores use win = 1, draw = 0.5, loss = 0, a 400-point scale, "
        f"and an A-seat term. Ratings are centered at 1,500. Estimated A-seat effect: "
        f"{seat_advantage:+.1f} ELO.", '',
        '| Rank | Bot | All-map ELO |', '|---:|---|---:|']
    lines += [f"| {i} | {row['bot']} | {row['elo']:.1f} |"
              for i, row in enumerate(rating_rows, 1)]
    lines += ['', '## Point map leaders', '', '| Map | Leader | Equal-lineage score |',
              '|---|---|---:|']
    lines += [f"| {entry['map']} | {entry['leader']} | {entry['score']:.1%} |"
              for entry in map_leaders]
    lines += ['', '## Frontier', '',
              'A candidate is dominated only when the paired lineage-bootstrap interval is '
              'nonnegative on every qualified map and strictly positive on at least one. '
              'Each map needs both sides against at least three shared opponents. The '
              'frontier retains candidates with no supported dominator.', '',
              '| Bot | Dominated by |', '|---|---|']
    lines += [f"| {bot} | {', '.join(dominated[bot]) if dominated[bot] else '—'} |"
              for bot in bots]
    lines += ['', '## Limits', '',
              'The bootstrap resamples opponent lineages as whole clusters. It does not '
              'capture all behavior randomness or correct for the number of pairwise '
              'comparisons. Results describe this frozen 35-map panel and should not be '
              'read as official contest ratings.', '',
              'Full map-by-bot profiles and every pairwise interval are in '
              '[`frontier.json`](frontier.json).', '']
    (output / 'report.md').write_text('\n'.join(lines))
    print(json.dumps(dict(output=str(output), fixtures=len(records),
        duplicates_discarded=duplicates,
        conflicting_repeats=len(conflicting_repeats),
        frontier=frontier, ratings=rating_rows), indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path,
                        help='Frozen experiment_data/benchmark_* directory')
    parser.add_argument('--output', type=Path,
                        help='Output directory (default: campaign/frontier)')
    parser.add_argument('--bootstrap-replicates', type=int, default=2000)
    args = parser.parse_args()
    if args.bootstrap_replicates < 100:
        parser.error('--bootstrap-replicates must be at least 100')
    campaign = args.campaign.resolve()
    output = args.output.resolve() if args.output else campaign / 'frontier'
    main(campaign, output, args.bootstrap_replicates)

#!/usr/bin/env python3
"""Measure the lowest-id queen and check D-040 rules in Rome panel replays.

Reports queen survival and length at r490, how often it is longest at r490
and over recorded rounds, plus replay checks for successful sprint costs and
round-limit tiebreak messages. The run_panel index must be beside replays/.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features.frame import decode


def measure(paths: list[Path], bot_name: str, index_path: Path) -> dict:
    rows = {r['game']: r for r in (json.loads(s) for s in index_path.read_text().splitlines())}
    n = survived = longest490 = longest490_alive = round_checks = round_longest = 0
    lengths490 = []
    round_limit = longest_checks = longest_ties = 0
    queen_checks = queen_wins_consistent = 0
    sprint_actions = sprint_checks = sprint_matches = 0
    sprint_mismatches = []
    for path in paths:
        row = rows.get(path.stem, {})
        g = decode(str(path))
        side = 'A' if Path(g['botA']).name == bot_name else 'B' if Path(g['botB']).name == bot_name else None
        if side is None:
            continue
        first = g['rounds'][0]
        queens = {t: min(i for i, (team, _body) in first.items() if team == t) for t in 'AB'}
        queen = queens[side]
        snaps = g['rounds']
        last_recorded = min(490, len(snaps) - 2)
        for r in range(last_recorded + 1):
            snap = snaps[r]
            mine = [(i, body) for i, (team, body) in snap.items() if team == side]
            if mine:
                top = max(len(body) for _i, body in mine)
                queen_body = next((body for i, body in mine if i == queen), None)
                round_checks += 1
                if queen_body is not None and len(queen_body) == top:
                    round_longest += 1
        n += 1
        if len(snaps) > 490 and queen in snaps[490]:
            survived += 1
            qlen = len(snaps[490][queen][1])
            lengths490.append(qlen)
            own_lengths = [len(body) for team, body in snaps[490].values() if team == side]
            if own_lengths and qlen == max(own_lengths):
                longest490 += 1
                longest490_alive += 1

        result_reason = str(row.get('reason', '')).lower()
        final = snaps[-1]
        qlen = {t: len(final[queens[t]][1]) if queens[t] in final else 0 for t in 'AB'}
        top_len = {t: max((len(b) for tt, b in final.values() if tt == t), default=0) for t in 'AB'}
        winner = row.get('winner')
        if int(row.get('rounds') or 0) >= 500:
            round_limit += 1
        if 'longest dragon' in result_reason:
            longest_checks += 1
            longest_ties += int(qlen['A'] == qlen['B'])
        if 'queen' in result_reason and winner in ('A', 'B'):
            queen_checks += 1
            other = 'B' if winner == 'A' else 'A'
            queen_wins_consistent += int(qlen[winner] > qlen[other])
        if 'total' in result_reason and winner in ('A', 'B'):
            queen_checks += 1
            other = 'B' if winner == 'A' else 'A'
            queen_wins_consistent += int(qlen[winner] == qlen[other] and top_len[winner] == top_len[other]
                                          and sum(len(b) for t, b in final.values() if t == winner)
                                          > sum(len(b) for t, b in final.values() if t == other))

        deaths = {(d['id'], d['round']) for d in g['events']['deaths']}
        for action in g['events']['actions']:
            if action['kind'] != 'move' or action['steps'] < 2:
                continue
            sprint_actions += 1
            # A sprint ending in death has no measurable post-action length.
            if (action['id'], action['round']) in deaths:
                continue
            before = snaps[action['round']].get(action['id'])
            if not before:
                continue
            length = len(before[1])
            expected_paid = max(0, action['steps'] - ((length + 3) // 4))
            sprint_checks += 1
            if action.get('paid') == expected_paid:
                sprint_matches += 1
            elif len(sprint_mismatches) < 10:
                sprint_mismatches.append((action['round'], action['id'], length, action['steps'],
                                          action.get('paid'), expected_paid))
    return {
        'games': n,
        'queen_survival_r490': survived / n if n else float('nan'),
        'queen_mean_length_r490_dead_as_zero': sum(lengths490) / n if n else float('nan'),
        'queen_median_length_r490_dead_as_zero': statistics.median(lengths490 + [0] * (n - len(lengths490))) if n else float('nan'),
        'queen_longest_r490_all_games': longest490 / n if n else float('nan'),
        'queen_longest_r490_when_alive': longest490_alive / survived if survived else float('nan'),
        'queen_longest_round_share_r0_490': round_longest / round_checks if round_checks else float('nan'),
        'round_checks': round_checks,
        'round_limit_games': round_limit,
        'longest_tiebreak_checks': longest_checks,
        'longest_tiebreak_queen_lengths_tied': longest_ties,
        'queen_tiebreak_checks': queen_checks,
        'queen_tiebreak_winners_consistent': queen_wins_consistent,
        'sprint_actions': sprint_actions,
        'successful_sprint_cost_checks': sprint_checks,
        'successful_sprint_cost_matches': sprint_matches,
        'sprint_cost_mismatch_examples': sprint_mismatches,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('replay_root', type=Path)
    ap.add_argument('--index', type=Path)
    ap.add_argument('--bot', default='rome-01-nodevil')
    ap.add_argument('--game', help='measure one replay by its run_panel fixture id')
    args = ap.parse_args()
    paths = sorted(args.replay_root.rglob('*.replay'))
    if args.game:
        paths = [p for p in paths if p.stem == args.game]
    index = args.index or args.replay_root.parent / 'index.jsonl'
    print(f'{len(paths)} replay files discovered under {args.replay_root}')
    for key, value in measure(paths, args.bot, index).items():
        print(f'{key}: {value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Compare the two focused runs of a Hunter small tournament.

Usage: python3 bots/summarize_hunter.py build/new-small build/previous-small
Excludes bot failures from the clean comparison, even when the engine returned
an ordinary winner. Reports duplicate fixtures that changed outcome.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

BOT_FAILURE = re.compile(r'no valid action|exceeded CPU limit|exited with code|timed out|Traceback|Resource temporarily unavailable', re.I)


def summarize(folder):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text())
    results = json.loads((folder / 'results.json').read_text())
    focus = manifest['focus_bot']
    expected = 2 * (len(manifest['bots']) - 1) * len(manifest['maps'])
    raw, clean, excluded, by_map, fixtures = Counter(), Counter(), [], {}, {}
    seen = set()
    for result in results:
        key = (result['map'], result['team_a'], result['team_b'])
        if key in seen:
            raise ValueError(f'duplicate fixture: {key}')
        seen.add(key)
        fixtures[key] = result['outcome']
        outcome = result['outcome']
        label = ('errors' if outcome == 'error' else 'draws' if outcome == 'draw'
                 else 'wins' if result['winner'] == focus else 'losses')
        raw[label] += 1
        log = Path(result['log'])
        if not log.is_absolute():
            log = folder / log
        bad_log = not log.is_file() or BOT_FAILURE.search(log.read_text(errors='replace')) is not None
        if label == 'errors' or bad_log:
            excluded.append({'map': result['map'], 'team_a': result['team_a'],
                             'team_b': result['team_b'], 'reason': 'match error' if label == 'errors' else 'bot failure or missing log'})
        else:
            clean[label] += 1
            by_map.setdefault(result['map'], Counter())[label] += 1
    for tally in (raw, clean):
        for field in ('wins', 'draws', 'losses', 'errors'):
            tally.setdefault(field, 0)
        tally['points'] = tally['wins'] * 3 + tally['draws']
        tally['played'] = tally['wins'] + tally['draws'] + tally['losses']
    return dict(focus=focus, expected=expected, recorded=len(results), complete=len(results) == expected,
                raw=dict(raw), clean=dict(clean), excluded=excluded,
                by_map={name: dict(count) for name, count in sorted(by_map.items())}), manifest, fixtures


def compare(new_folder, previous_folder):
    new, nm, nf = summarize(new_folder)
    previous, pm, pf = summarize(previous_folder)
    if any(nm[key] != pm[key] for key in ('bots', 'maps', 'input_hash', 'script_hash', 'executable', 'replays')):
        raise ValueError('focused runs must use identical pools, maps, source fingerprints, runner and replay settings')
    if new['focus'] == previous['focus']:
        raise ValueError('focused versions must differ')
    disagreements = [{'map': key[0], 'team_a': key[1], 'team_b': key[2],
                      'new_run': nf[key], 'previous_run': pf[key]}
                     for key in sorted(nf.keys() & pf.keys()) if nf[key] != pf[key]]
    # Compare only fixtures without bot failures in BOTH focused runs. Exclude
    # an entire map if either focus encountered a bot failure there, keeping
    # map weights and match counts equal.
    excluded_maps = {item['map'] for summary in (new, previous) for item in summary['excluded']}
    common_maps = set(new['by_map']) & set(previous['by_map']) - excluded_maps
    comparable = []
    for summary in (new, previous):
        tally = Counter()
        for name in common_maps:
            tally.update(summary['by_map'][name])
        comparable.append(dict(focus=summary['focus'], wins=tally['wins'], draws=tally['draws'],
                               losses=tally['losses'], points=3 * tally['wins'] + tally['draws']))
    # With a three-version pool the union of the two focused schedules is a
    # complete round robin. This also compares a new branch with the incumbent
    # when the immediately preceding experiment was rejected.
    pool = {bot: Counter() for bot in nm['bots']}
    for (board, a, b), outcome in (nf | pf).items():
        if board not in common_maps or outcome == 'error':
            continue
        if outcome == 'draw':
            pool[a]['draws'] += 1
            pool[b]['draws'] += 1
        else:
            winner, loser = (a, b) if outcome == 'A' else (b, a)
            pool[winner]['wins'] += 1
            pool[loser]['losses'] += 1
    pool_standings = [dict(bot=bot, wins=row['wins'], draws=row['draws'], losses=row['losses'],
                           played=row['wins'] + row['draws'] + row['losses'],
                           points=3 * row['wins'] + row['draws']) for bot, row in pool.items()]
    pool_standings.sort(key=lambda row: (-row['points'], row['bot']))
    valid = all(s['complete'] and not s['raw']['errors'] for s in (new, previous)) and not disagreements
    improved = valid and comparable[0]['points'] > comparable[1]['points']
    return dict(new=new, previous=previous, comparable_maps=sorted(common_maps), comparable=comparable,
                duplicate_disagreements=disagreements, valid=valid, pool_standings=pool_standings,
                decision='improved on this small sample' if improved else 'not demonstrated')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('new_run', type=Path)
    parser.add_argument('previous_run', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = compare(args.new_run, args.previous_run)
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')
    return 0 if report['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

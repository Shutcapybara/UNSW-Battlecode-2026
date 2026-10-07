"""Collect fresh PPO-vs-field games for winner-action imitation.

This writes training replays only. Use training maps and new seeds; do not point
it at the paired evaluation fixture seeds.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
from threading import Lock

import tools.stats_store as stats_module
from tools.stats_store import StatsStore as BaseStatsStore

from .data import digest
from .evaluate import run_game, source_hash


def collect(args):
    root = Path(__file__).resolve().parents[2]
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out = out.resolve()
    candidate = Path(args.candidate).resolve()
    opponents = [Path(item).resolve() for item in args.opponents.split(',') if item.strip()]
    maps = [root / 'maps/live' / item.strip() for item in args.maps.split(',') if item.strip()]
    if not candidate.is_dir() or not opponents:
        raise ValueError('candidate must be a bot package and at least one opponent is required')
    for path in maps:
        if not path.is_file() or path.parent.resolve() != (root / 'maps/live').resolve():
            raise ValueError(f'training map must be a maps/live/*.map template: {path}')
        if path.stem.casefold() in {'autarky', 'maze', 'trauma'}:
            raise ValueError(f'refusing held-out map: {path.stem}')
    for path in opponents:
        if not path.is_dir():
            raise FileNotFoundError(path)

    candidate_hash = source_hash(candidate)
    opponent_hashes = {str(path): source_hash(path) for path in opponents}
    manifest = dict(candidate=str(candidate), candidate_hash=candidate_hash,
                    opponents=[dict(path=str(path), hash=opponent_hashes[str(path)]) for path in opponents],
                    maps=[dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in maps],
                    seed_start=args.seed_start, seed_count=args.seed_count,
                    sides=['A', 'B'], purpose='winner-action imitation training data')
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / 'manifest.json'
    if manifest_path.exists():
        if json.loads(manifest_path.read_text(encoding='utf-8')) != manifest:
            raise ValueError(f'collection settings differ from existing manifest: {manifest_path}')
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

    stats_root = out / 'stats'
    stats_module.StatsStore = lambda queue_only=False: BaseStatsStore(stats_root, queue_only=queue_only)
    known_hashes = {str(candidate): candidate_hash, **opponent_hashes}
    cache = out / 'cache'
    replay_root = out / 'replays'
    records_path = out / 'records.jsonl'
    completed = {}
    if records_path.exists():
        for line in records_path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                completed[(row['opponent'], row['map'], row['seed'], row['side'])] = row

    target = len(opponents) * len(maps) * args.seed_count * 2
    tasks = []
    for opponent in opponents:
        for board in maps:
            for seed in range(args.seed_start, args.seed_start + args.seed_count):
                for side in 'AB':
                    key = (str(opponent), board.stem, seed, side)
                    if key in completed:
                        continue
                    tasks.append((opponent, board, seed, side, key))

    def play(task):
        opponent, board, seed, side, key = task
        label = f'{opponent.name}-{board.stem}-s{seed}-{side}'
        replay = replay_root / f'{label}.replay'
        log = replay.with_suffix('.log')
        match = None
        if replay.is_file() and log.is_file():
            match = re.search(r'^(?:team ([AB]) wins|draw) after (\d+) rounds\b',
                              log.read_text(encoding='utf-8', errors='replace'), re.MULTILINE)
        if match is None:
            run_game(candidate, opponent, board, side, seed, replay, known_hashes=known_hashes)
            match = re.search(r'^(?:team ([AB]) wins|draw) after (\d+) rounds\b',
                              log.read_text(encoding='utf-8', errors='replace'), re.MULTILINE)
        if match is None:
            raise RuntimeError(f'no completed game result in {log}')
        winner = match[1]
        rounds = int(match[2])
        record = dict(opponent=str(opponent), map=board.stem, seed=seed, side=side,
                      replay=str(replay), game_sha256=digest(replay), winner=winner,
                      rounds=rounds, candidate_hash=candidate_hash,
                      opponent_hash=opponent_hashes[str(opponent)])
        return key, record

    lock = Lock()
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(play, task) for task in tasks]
        for future in as_completed(futures):
            key, record = future.result()
            with lock:
                with records_path.open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(record, separators=(',', ':')) + '\n')
                completed[key] = record
                count = len(completed)
            if count % 16 == 0 or count == target:
                print(json.dumps(dict(games=count, target=target,
                                      latest={k: record[k] for k in ('opponent', 'map', 'seed', 'side', 'winner', 'rounds')}),
                                 separators=(',', ':')), flush=True)

    return dict(games=len(completed), target=target, manifest=str(manifest_path), records=str(records_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, help='candidate bot package directory')
    parser.add_argument('--opponents', required=True, help='comma-separated frozen bot package directories')
    parser.add_argument('--maps', default='default.map,devil.map,islands.map,portals.map')
    parser.add_argument('--seed-start', type=int, required=True)
    parser.add_argument('--seed-count', type=int, required=True)
    parser.add_argument('--jobs', type=int, default=2, help='parallel native games (default: 2)')
    parser.add_argument('--out', default='build/growth_rl/ppo/winner-data')
    args = parser.parse_args()
    if args.seed_count < 1 or args.jobs < 1:
        parser.error('--seed-count and --jobs must be positive')
    try:
        print(json.dumps(collect(args), separators=(',', ':')), flush=True)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()

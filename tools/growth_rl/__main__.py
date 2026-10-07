import argparse
import json
from pathlib import Path
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'ppo':
        from . import ppo as ppo_module
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        ppo_module.main()
        return
    parser = argparse.ArgumentParser(description='Retained-growth RL campaign for the first 100 rounds')
    sub = parser.add_subparsers(dest='command', required=True)
    worker = sub.add_parser('run')
    worker.add_argument('--config', type=Path, required=True)
    worker.add_argument('--once', action='store_true')
    train = sub.add_parser('train')
    train.add_argument('--replays', nargs='+', required=True)
    train.add_argument('--out', type=Path, required=True)
    train.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    train.add_argument('--epochs', type=int, default=12)
    train.add_argument('--max-games', type=int, default=200)
    train.add_argument('--rows-per-side', type=int, default=256)
    train.add_argument('--final-test', action='store_true')
    download = sub.add_parser('collect')
    download.add_argument('--out', type=Path, required=True)
    download.add_argument('--top-n', type=int, default=10)
    download.add_argument('--max-downloads', type=int, default=30)
    inspect = sub.add_parser('inspect-game')
    inspect.add_argument('game', type=int)
    args = parser.parse_args()
    if args.command == 'run':
        from .runner import run
        run(args.config, args.once)
    elif args.command == 'inspect-game':
        from tools.hub.api import Client
        from .data import ROOT
        payload = Client(ROOT).get(f'/api/v1/battles/{args.game}')
        def structure(value, depth=0):
            if isinstance(value, dict):
                return {k: structure(v, depth + 1) if depth < 2 else type(v).__name__ for k, v in value.items()
                        if k not in ('log', 'logs', 'url', 'replayUrl')}
            if isinstance(value, list):
                return [structure(value[0], depth + 1)] if value else []
            return value if isinstance(value, (bool, int, type(None))) else type(value).__name__
        print(json.dumps(structure(payload), indent=2))
    elif args.command == 'collect':
        from .collect import collect
        print(json.dumps(collect(dict(top_n=args.top_n, max_downloads=args.max_downloads), args.out)))
    else:
        from .data import dataset, atomic_json
        from .train import fit
        games, audit = dataset(args.replays, args.out / 'cache', args.max_games,
                               rows_per_side=args.rows_per_side)
        atomic_json(args.out / 'extraction_audit.json', audit)
        fit(games, args.out, device=args.device, epochs=args.epochs, final_test=args.final_test)


if __name__ == '__main__':
    main()

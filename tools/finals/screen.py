"""Run a bounded, serial, seeded finals comparison from explicit maps and opponents.

All artifacts and frozen bot sources stay in --output. Resume refuses changed inputs.
Results are development evidence unless a separate uninspected confirmation set is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
import unswbc

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.benchmarking.tournament import MatchWorkers, play


def source_hash(source):
    digest = hashlib.sha256()
    for p in sorted(source.rglob('*')):
        if p.is_file() and p.suffix in ('.cpp', '.hpp', '.toml', '.h', '.c', '.py') and not any(
                part in ('.unswbc-build', 'build', '__pycache__') for part in p.relative_to(source).parts):
            digest.update(str(p.relative_to(source)).encode() + b'\0' + p.read_bytes() + b'\0')
    return digest.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--candidate-dir', type=Path, help='Explicit generated artifact directory (name must match --candidate)')
    ap.add_argument('--opponents', nargs='+', required=True)
    ap.add_argument('--maps', type=Path, nargs='+', required=True)
    ap.add_argument('--seeds', type=int, nargs='+', required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--timeout', type=float, default=180)
    ap.add_argument('--sandbox', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--resume', action='store_true')
    args = ap.parse_args(argv)
    if args.candidate in args.opponents or len(set(args.opponents)) != len(args.opponents):
        ap.error('Opponents must be distinct and exclude the candidate')
    if len({p.name for p in args.maps}) != len(args.maps) or len(set(args.seeds)) != len(args.seeds):
        ap.error('Map filenames and seeds must be distinct')
    bots = {name: ROOT / 'bots' / name for name in [args.candidate] + args.opponents}
    if args.candidate_dir:
        if args.candidate_dir.name != args.candidate:
            ap.error('Candidate artifact directory name must match --candidate')
        bots[args.candidate] = args.candidate_dir.resolve()
    if any(not (p / 'bot.toml').is_file() for p in bots.values()) or any(not p.is_file() for p in args.maps):
        ap.error('Missing bot project or map')
    fixtures = [(p, opp, seat, seed) for p in args.maps for opp in args.opponents
                for seat in ('A', 'B') for seed in args.seeds]
    if len(fixtures) > 1000:
        ap.error('Limit is 1,000 fixtures per invocation')
    manifest = dict(version=1, candidate=args.candidate, opponents=args.opponents,
                    bots={name: source_hash(p) for name, p in bots.items()},
                    maps=[dict(path=str(p.resolve()), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                          for p in args.maps], seeds=args.seeds, sandbox=args.sandbox,
                    runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    manifest['candidate_dir'] = str(bots[args.candidate].resolve())
    engine = Path(unswbc.__file__).with_name('unswbc_engine.wasm')
    manifest['engine_wasm_sha256'] = hashlib.sha256(engine.read_bytes()).hexdigest()
    print(f'{len(fixtures)} explicit fixtures; one worker; sandbox={args.sandbox}', flush=True)
    if args.dry_run:
        return 0
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    mp = out / 'manifest.json'
    if mp.exists():
        if not args.resume or json.loads(mp.read_text()) != manifest:
            ap.error('Existing output requires --resume with unchanged inputs')
    else:
        mp.write_text(json.dumps(manifest, indent=2) + '\n')
        shutil.copyfile(Path(__file__), out / 'runner-source.py')
        for name, path in bots.items():
            shutil.copytree(path, out / 'sources' / name,
                            ignore=shutil.ignore_patterns('.unswbc-build', 'build', '__pycache__'))
            if source_hash(out / 'sources' / name) != manifest['bots'][name]:
                ap.error('Source changed while freezing input')
        (out / 'maps').mkdir()
        for board, pinned in zip(args.maps, manifest['maps']):
            frozen = out / 'maps' / board.name
            shutil.copyfile(board, frozen)
            if hashlib.sha256(frozen.read_bytes()).hexdigest() != pinned['sha256']:
                ap.error('Map changed while freezing input')
    bots = {name: out / 'sources' / name for name in bots}
    executable = str(ROOT / '.venv/bin/unswbc')
    result_path = out / 'results.json'
    results = json.loads(result_path.read_text()) if result_path.exists() else []
    completed = {r['fixture'] for r in results if r['outcome'] != 'error'}
    workers = MatchWorkers(out / 'workers')
    for p, opp, seat, seed in fixtures:
        label = f'{p.stem}-{opp}-{seat}-s{seed}'
        if label in completed:
            continue
        a, b = (args.candidate, opp) if seat == 'A' else (opp, args.candidate)
        r = play(executable, out / 'maps' / p.name, bots[a], bots[b], out, label, args.timeout, True,
                 workers=workers, sandbox=args.sandbox, seed=seed, board_id=p.stem)
        r.update(fixture=label, seed=seed, candidate_seat=seat, opponent=opp)
        results = [old for old in results if old['fixture'] != label] + [r]
        result_path.write_text(json.dumps(results, indent=2) + '\n')
        print(label, r['outcome'], r['rounds'], r['seconds'], r['error'], flush=True)
    summary = {}
    for opp in args.opponents:
        rr = [r for r in results if r['opponent'] == opp]
        summary[opp] = dict(wins=sum(r['winner'] == args.candidate for r in rr),
                           draws=sum(r['outcome'] == 'draw' for r in rr),
                           losses=sum(r['winner'] == opp for r in rr),
                           errors=sum(r['outcome'] == 'error' for r in rr))
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return int(any(s['errors'] for s in summary.values()))


if __name__ == '__main__':
    sys.exit(main())

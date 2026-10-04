"""Compile and compare H-Q8 encoders on deterministic replayed actor turns.

Example: .venv/bin/python tools/antioch/rl/hq8_parity.py \
  --replay-dir build/carthage/runs/carthage-05-free-sprint/pool/replays \
  --turns 1000 --out build/antioch/rl/hq8-parity.json
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/team_recon_claude'))
import features_view
from hq8_features import Encoder, NAMES


def python_rows(dump):
    actors, rows, metadata = {}, [], []
    lines = dump.splitlines()
    i, current = 0, None
    while i < len(lines):
        parts = lines[i].split()
        i += 1
        if not parts:
            continue
        if parts[0] == 'TURN':
            current = int(parts[1])
            if current not in actors:
                actors[current] = Encoder(current, parts[2], *map(int, parts[3:]))
            block_lines = []
            while lines[i] != 'END':
                block_lines.append(lines[i])
                i += 1
            i += 1
            block, consumed = features_view.parse_block(block_lines)
            if consumed != len(block_lines):
                raise ValueError('trailing Python block input')
            values = actors[current].features(block)
            rows.append(struct.pack('<' + 'i' * len(NAMES), *values))
            metadata.append({'dragon': current, 'round': block['round'], 'team': parts[2],
                             'queen': values[NAMES.index('is_queen')],
                             'own_visible': values[NAMES.index('own_alive')] == 1,
                             'enemy_visible': values[NAMES.index('enemy_alive')] == 1,
                             'own_stale': values[NAMES.index('own_seen_age')] > 0,
                             'split_seen': actors[current].split_round is not None})
        elif parts[:2] == ['ACT', 'split']:
            actors[current].record_split()
    return rows, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-dir', type=Path, required=True)
    parser.add_argument('--turns', type=int, default=1000)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.turns < 1:
        parser.error('--turns must be positive')
    directory = ROOT / 'build/antioch/rl'
    directory.mkdir(parents=True, exist_ok=True)
    executable = directory / 'hq8-parity'
    compile_command = ['g++', '-O2', '-std=c++17', str(Path(__file__).with_suffix('.cpp')), '-o', str(executable)]
    subprocess.run(compile_command, check=True)
    maps = ('default', 'portals', 'trauma', 'schooltime', 'queen_of_spades',
            'autarky', 'slithery_fight', 'dilemma')
    files = sorted(args.replay_dir.glob('*.replay'))
    chosen = []
    for name in maps:
        candidates = [p for p in files if '__' + name + '__' in p.name]
        if candidates:
            chosen.append((name, candidates[0]))
    if not chosen:
        parser.error('no supported pool replays found')
    cases, all_rows = [], []
    for map_name, replay in chosen:
        for side in ('A', 'B'):
            dump_command = [sys.executable, str(ROOT / 'tools/hb1/cpp/dump_blocks.py'), str(replay), side]
            dump_result = subprocess.run(dump_command, capture_output=True, text=True)
            if dump_result.returncode:
                raise RuntimeError(f'replay block reconstruction failed: {dump_result.stderr}')
            dump = dump_result.stdout
            rows, metadata = python_rows(dump)
            cpp = subprocess.run([str(executable)], input=dump.encode(), capture_output=True, check=True).stdout
            expected = b''.join(rows)
            if cpp != expected:
                for i, row in enumerate(rows):
                    actual = cpp[i * len(row):(i + 1) * len(row)]
                    if actual != row:
                        raise RuntimeError(f'parity mismatch {replay} {side} {metadata[i]}')
                raise RuntimeError(f'output length mismatch {replay} {side}')
            case = {'map': map_name, 'path': str(replay), 'side': side,
                    'replay_sha256': hashlib.sha256(replay.read_bytes()).hexdigest(),
                    'turns_verified': len(rows)}
            cases.append(case)
            all_rows.extend((row, dict(meta, map=map_name, case=len(cases) - 1)) for row, meta in zip(rows, metadata))
            print(f'{map_name} {side}: {len(rows)} turns, exact match', flush=True)
    if len(all_rows) < args.turns:
        raise RuntimeError(f'only {len(all_rows)} turns available; requested {args.turns}')
    # Round robin across fixture, queen/nonqueen and early/late strata so the
    # advertised 1,000-turn sample has broad coverage rather than a prefix.
    buckets = {}
    for i, (_, meta) in enumerate(all_rows):
        key = (meta['case'], meta['queen'], meta['round'] >= 250)
        buckets.setdefault(key, []).append(i)
    selected, offsets = [], dict.fromkeys(buckets, 0)
    while len(selected) < args.turns:
        for key in sorted(buckets):
            offset = offsets[key]
            if offset < len(buckets[key]):
                selected.append(buckets[key][offset])
                offsets[key] += 1
                if len(selected) == args.turns:
                    break
    sample = [all_rows[i] for i in selected]
    coverage = {name: sum(bool(meta[name]) for _, meta in sample)
                for name in ('queen', 'own_visible', 'enemy_visible', 'own_stale', 'split_seen')}
    coverage['round_250_plus'] = sum(meta['round'] >= 250 for _, meta in sample)
    report = {'schema': 'H-Q8-v1', 'status': 'PASS', 'comparison': 'packed little-endian signed int32 bytes',
              'local_unswbc_version': importlib.metadata.version('unswbc'),
              'feature_count': len(NAMES), 'features': NAMES, 'sample_turns': len(sample),
              'all_turns_verified': len(all_rows), 'mismatches': 0, 'sample_coverage': coverage,
              'sample_sha256': hashlib.sha256(b''.join(row for row, _ in sample)).hexdigest(),
              'encoder_sha256': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                 for name in ('hq8_features.py', 'hq8_features.hpp')},
              'sources': cases, 'compile_command': compile_command,
              'limitations': 'Conservative observable subset. Latent mode/death inference, sonar schema, map classifier and deployment integration remain open; see tools/antioch/rl/hq8_schema.md.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('status', 'sample_turns', 'all_turns_verified', 'feature_count', 'mismatches', 'sample_coverage')}, indent=2))


if __name__ == '__main__':
    main()

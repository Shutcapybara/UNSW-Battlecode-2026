"""Compare complete protocol replies from two native binaries on legal replay histories.

Checks temporal action/radio parity on every selected dragon, including births/deaths.
Use local unredacted replays only; replay reconstruction of server timers needs an oracle.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/learn'))
import rebuild


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--replays', type=Path, nargs='+', required=True)
    ap.add_argument('--seat', choices=['A', 'B'], default='A')
    ap.add_argument('--suppression-control', action='store_true', help='Reference expectation drops only optional SONAR lines')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = dict(reference_sha256=hashlib.sha256(args.reference.read_bytes()).hexdigest(),
                  candidate_sha256=hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
                  games=[], turns=0, mismatches=0)
    for replay in args.replays:
        sequences = defaultdict(list)
        spawns = {}

        def emit(dragon, spawn, text, ctx):
            if spawn['team'] == args.seat:
                sequences[dragon].append(text)
                spawns[dragon] = spawn

        rebuild.walk(replay.read_bytes(), emit)
        game = dict(replay=str(replay), sha256=hashlib.sha256(replay.read_bytes()).hexdigest(),
                    dragons=len(sequences), turns=0, mismatches=[], reference_seconds=0, candidate_seconds=0)
        for dragon, sequence in sequences.items():
            sp = spawns[dragon]
            text = (f"ID {dragon}\nTEAM {sp['team']}\nMAP {sp['W']} {sp['H']}\n"
                    f"UNIT_LIMIT {sp['unit_limit']}\n" + ''.join(sequence) + 'ENDGAME\n')
            outputs = []
            for name in ('reference', 'candidate'):
                begin = time.monotonic()
                proc = subprocess.run([str(getattr(args, name).resolve())], input=text, capture_output=True,
                                      text=True, timeout=120, check=True)
                game[name + '_seconds'] += time.monotonic() - begin
                # Instrumentation only; actions, sonar, incumbent logs and protocol remain exact.
                lines = [line for line in proc.stdout.splitlines() if not line.startswith(('LOG FO ', 'LOG FC '))]
                if args.suppression_control and name == 'reference':
                    lines = [line for line in lines if not line.startswith('SONAR ') or
                             (int(line.split()[2]) >> 8) & 15 in (1, 3, 7)]
                outputs.append('\n'.join(lines))
            nturns = outputs[0].count('ENDTURN')
            if nturns != len(sequence) or outputs[1].count('ENDTURN') != nturns:
                raise ValueError(f'Incomplete replies for dragon {dragon}')
            game['turns'] += nturns
            if outputs[0] != outputs[1]:
                aa, bb = [s.split('ENDTURN') for s in outputs]
                differing = [i for i, (a, b) in enumerate(zip(aa, bb)) if a != b]
                game['mismatches'].append(dict(id=dragon, turns=differing))
                for i, output in enumerate(outputs):
                    (args.output / f'{replay.stem}-dragon{dragon}-{i}.stdout').write_text(output)
        report['turns'] += game['turns']
        report['mismatches'] += sum(len(r['turns']) for r in game['mismatches'])
        report['games'].append(game)
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(replay.name, game['turns'], 'turns', len(game['mismatches']), 'divergent dragons', flush=True)
    print('TOTAL', report['turns'], 'turns;', report['mismatches'], 'mismatches', flush=True)
    return int(report['mismatches'] > 0)


if __name__ == '__main__':
    sys.exit(main())

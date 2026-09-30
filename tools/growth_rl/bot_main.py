"""Copied into generated bot packages alongside policy and v4 features."""
import json
import os
from pathlib import Path
import random
import sys

import features_view as FV
from policy import ACTIONS, Policy, split_size


def read_block():
    lines = []

    def take(n=1):
        for _ in range(n):
            line = sys.stdin.readline()
            while line and not line.strip():
                line = sys.stdin.readline()
            if not line:
                raise EOFError
            lines.append(line.rstrip('\n'))
    take(5)
    take(int(lines[4].split()[1]))
    take()
    take(49 if lines[-1].startswith('ECHOES') else 48)
    take()
    take(int(lines[-1].split()[1]))
    take(15)
    return lines


def main():
    folder = Path(__file__).resolve().parent
    model = Policy.load(folder / 'policy.json')
    settings = json.loads((folder / 'settings.json').read_text())
    init = {}
    while 'UNIT_LIMIT' not in init:
        line = sys.stdin.readline()
        if not line:
            return
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'MAP':
            init['W'], init['H'] = int(parts[1]), int(parts[2])
        else:
            init[parts[0]] = parts[1]
    proc = FV.Proc(int(init['ID']), init['TEAM'], init['W'], init['H'], int(init['UNIT_LIMIT']))
    rng = random.Random(settings.get('seed', 0) * 65537 + int(init['ID']))
    while True:
        try:
            lines = read_block()
        except EOFError:
            return
        block, _ = FV.parse_block(lines)
        row = proc.features(block)
        choice = ACTIONS[model.choose(row, settings.get('temperature', 0), rng)]
        if choice.startswith('split_'):
            size = split_size(choice, block['length'])
            command = f'SPLIT {size}'
            proc.record_action('split', split=size)
        else:
            facing, directions = block['dir'], []
            for relative in choice:
                facing = FV.rel_to_abs(facing, relative)
                directions.append(facing)
            command = 'MOVE ' + ''.join(directions)
            proc.record_action('move', rels=list(choice))
        sys.stdout.write(command + '\nPROTOCOL 3\nENDTURN\n')
        sys.stdout.flush()


if __name__ == '__main__':
    main()

"""Action-level checks between the V13 Python reference and C++ V14."""
import importlib.util
import io
from pathlib import Path
import random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'bots/hunter-v13-hybrid-route-spacing/main.py'
CPP_EXECUTABLE = sys.argv.pop(1) if len(sys.argv) > 1 else None

argv = sys.argv[:]
sys.argv = ['test_bot.py', 'unused']
from test_bot import turn
sys.argv = argv

spec = importlib.util.spec_from_file_location('hunter_v13', REFERENCE)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


def block_with_enemy(size=4, length=3, units=3):
    block = turn(length=length, units=units, other_heads=[('B', 7, 5)])
    extra = ''.join(f'B 1 7 {5-index} W 0\n' for index in range(1, size))
    return block.replace('DRAGON_BODIES 2\n', f'DRAGON_BODIES {size+1}\n').replace(
        'B 1 7 5 W 1\n', 'B 1 7 5 W 1\n' + extra)


class CppV13Parity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if CPP_EXECUTABLE is None:
            raise RuntimeError('pass the compiled C++ V14 executable path')
        cls.executable = CPP_EXECUTABLE

    def compare(self, blocks, width=11, height=11):
        header = f'ID 0\nTEAM A\nMAP {width} {height}\nUNIT_LIMIT 64\n'
        bot = reference.Bot(io.StringIO(header))
        expected = []
        for block in blocks:
            bot.stream = io.StringIO(block)
            bot.update()
            expected.append(bot.action())
        result = subprocess.run([self.executable], input=header + ''.join(blocks),
                                text=True, capture_output=True, timeout=15, check=True)
        actual = [part.strip() + '\nENDTURN' for part in result.stdout.split('ENDTURN') if part.strip()]
        self.assertEqual(result.stderr, '')
        self.assertEqual(actual, expected)

    def test_streaming_growth_exploration_and_teammate_spacing(self):
        self.compare([
            turn(),
            turn(length=2, pearls=[(6, 5)]).replace('ROUND 1', 'ROUND 2'),
            turn(other_heads=[('A', 7, 5)]).replace('ROUND 1', 'ROUND 3'),
        ])

    def test_reachable_multi_step_attack(self):
        self.compare([block_with_enemy()])

    def test_stale_enemy_lower_bound_does_not_authorize_attack(self):
        self.compare([
            block_with_enemy(4, units=3).replace('ROUND 1', 'ROUND 20'),
            block_with_enemy(2, units=3).replace('ROUND 1', 'ROUND 21'),
        ])

    def test_known_wall_detour_changes_spacing(self):
        block = turn(other_heads=[('A', 7, 5)])
        horizontal = [line.split() for line in block.splitlines()[-15:-7]]
        vertical = [line.split() for line in block.splitlines()[-7:]]
        horizontal[3][3] = 'w'
        horizontal[4][3] = 'w'
        vertical[3][3] = 'w'
        vertical[3][4] = 'w'
        lines = block.splitlines()
        lines[-15:] = [' '.join(row) for row in horizontal + vertical]
        self.compare(['\n'.join(lines) + '\n'])

    def test_portal_trip_and_small_height_map(self):
        block = turn(portals=[('v', 3, 4, '1'), ('v', 3, 6, '1')])
        self.compare([block], width=11, height=8)

    def test_seeded_observation_sequence_matches(self):
        rng = random.Random(1413)
        blocks = []
        for round_number in range(1, 33):
            head_id = rng.randrange(1, 5)
            heads = [('A', 5 + head_id % 3, 4 + (head_id // 2))]
            if round_number % 3 == 0:
                heads.append(('B', 8, 5))
            pearls = [(rng.randrange(3, 8), rng.randrange(3, 8))]
            walls = ''.join(d for d in 'NESW' if rng.randrange(5) == 0)
            block = turn(length=rng.randrange(2, 7), units=rng.randrange(3, 65),
                         other_heads=heads, pearls=pearls, walls=walls)
            blocks.append(block.replace('ROUND 1', f'ROUND {round_number}'))
        self.compare(blocks)


if __name__ == '__main__':
    unittest.main()

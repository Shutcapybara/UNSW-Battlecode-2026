"""Size-aware attack tests for the fry-v11-size-aware variant."""
import subprocess
import sys
import unittest

BOT = sys.argv.pop(1)
_original_argv = sys.argv
sys.argv = ['test_bot.py', BOT]
from test_bot import turn
sys.argv = _original_argv


def run(block):
    result = subprocess.run(
        [BOT],
        input='ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n' + block,
        capture_output=True, text=True, check=True, timeout=2,
    )
    return result.stdout.splitlines()[0]


def run_turns(*blocks):
    result = subprocess.run(
        [BOT],
        input='ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n' + ''.join(blocks),
        capture_output=True, text=True, check=True, timeout=2,
    )
    return result.stdout.splitlines()


def enemy_with_size(block, size):
    extra = ''.join(f'B 1 {7} {5 - index} W 0\n' for index in range(1, size))
    return block.replace('DRAGON_BODIES 2\n', f'DRAGON_BODIES {size + 1}\n', 1).replace(
        'B 1 7 5 W 1\n', 'B 1 7 5 W 1\n' + extra, 1)


class SizeAwareHunter(unittest.TestCase):
    def test_does_not_kamikaze_into_equal_size_enemy(self):
        block = enemy_with_size(turn(length=3, units=3, other_heads=[('B', 7, 5)]), 3)
        self.assertNotIn(run(block), ('MOVE E', 'MOVE EE'))

    def test_uses_full_multi_move_budget_against_larger_enemy(self):
        block = enemy_with_size(turn(length=3, units=3, other_heads=[('B', 7, 5)]), 4)
        self.assertEqual(run(block), 'MOVE EE')

    @unittest.skipUnless('stateful' in BOT, 'stateful-memory test')
    def test_remembers_recently_seen_enemy_size(self):
        first = enemy_with_size(turn(length=3, units=3, other_heads=[('B', 7, 5)]), 5)
        second = turn(length=3, units=3, other_heads=[('B', 7, 5)]).replace(
            'ROUND 1\n', 'ROUND 2\n', 1)
        self.assertEqual(run_turns(first, second)[3], 'MOVE EE')

    @unittest.skipUnless('hunter_v1' in BOT, 'hunter-v01-team-growth team-state test')
    def test_yields_growth_to_larger_teammate(self):
        block = turn(length=6, units=3, pearls=[(6, 5)]).replace(
            'ROUND 1\n', 'ROUND 400\n', 1)
        teammate_status = str(0x80000000 | (2 << 24) | (10 << 12))
        result = run_turns(block.replace('NUM_MSGS 0', 'NUM_MSGS 1\n' + teammate_status, 1))
        self.assertNotEqual(result[0], 'MOVE E')


if __name__ == '__main__':
    unittest.main()

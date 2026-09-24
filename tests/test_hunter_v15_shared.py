"""Focused protocol and first-contact scouting checks for Hunter V15."""
import subprocess
import sys
import unittest

BOT = sys.argv.pop(1)
args = sys.argv[:]
sys.argv = ['test_bot.py', 'unused']
from test_bot import turn
sys.argv = args


def run(block):
    result = subprocess.run(
        [BOT], input='ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n' + block,
        text=True, capture_output=True, timeout=5, check=True)
    assert result.stderr == '', result.stderr
    return result.stdout.splitlines()


def add_message(block, message):
    return block.replace('NUM_MSGS 0', f'NUM_MSGS 1\n{message}', 1)


class SharedState(unittest.TestCase):
    def test_unmatched_portal_is_crossed_to_scout(self):
        lines = run(turn(length=3, units=4, portals=[('h', 3, 3, '1')]))
        self.assertEqual(lines[0], 'MOVE N')

    def test_gossiped_team_max_changes_growth_decision(self):
        block = turn(length=6, units=3, pearls=[(6, 5)]).replace('ROUND 1', 'ROUND 450')
        self.assertEqual(run(block)[0], 'MOVE E')
        summary = (0xA9 << 56) | (449 << 46) | (8 << 36) | (4 << 26) | (3 << 18)
        self.assertEqual(run(add_message(block, summary))[0], 'SPLIT 2')

    def test_hotspot_is_merged_and_rebroadcast(self):
        block = turn(length=3, units=64)
        hotspot = (0xAA << 56) | (1 << 46) | (8 << 40) | (5 << 34) | (10 << 26)
        lines = run(add_message(block, hotspot))
        messages = [int(line.split()[2]) for line in lines if line.startswith('SONAR ')]
        self.assertTrue(any((value >> 56) == 0xAA and ((value >> 40) & 63) == 8 and
                            ((value >> 34) & 63) == 5 for value in messages))

    def test_safe_portal_endpoint_is_rebroadcast(self):
        block = turn(length=3, units=64).replace('ROUND 1', 'ROUND 2')
        portal = ((0xAB << 56) | (1 << 46) | (8 << 40) | (5 << 34) |
                  (ord('1') << 24) | (1 << 23))
        lines = run(add_message(block, portal))
        messages = [int(line.split()[2]) for line in lines if line.startswith('SONAR ')]
        self.assertTrue(any((value >> 56) == 0xAB and ((value >> 40) & 63) == 8 and
                            ((value >> 23) & 1) == 1 for value in messages))


if __name__ == '__main__':
    unittest.main()

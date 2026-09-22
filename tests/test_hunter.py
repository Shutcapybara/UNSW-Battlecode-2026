"""Protocol tests for the dragon-hunter variant."""
import subprocess
import sys
import unittest

BOT = sys.argv.pop(1)
original_argv = sys.argv
sys.argv = ["test_bot.py", BOT]
from test_bot import turn
sys.argv = original_argv


def run(block, dragon_id=0):
    block = block.replace("A 0 ", f"A {dragon_id} ")
    result = subprocess.run(
        [BOT],
        input=f"ID {dragon_id}\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" + block,
        capture_output=True, text=True, check=True, timeout=2,
    )
    return result.stdout.splitlines()


class DragonHunter(unittest.TestCase):
    def test_rams_adjacent_enemy_before_splitting(self):
        self.assertEqual(run(turn(length=6, other_heads=[("B", 6, 5)]))[0], "MOVE E")

    def test_sprints_into_enemy_head(self):
        self.assertEqual(run(turn(length=6, other_heads=[("B", 7, 5)]))[0], "MOVE EE")

    def test_splits_before_collecting_pearl(self):
        self.assertEqual(run(turn(length=6, pearls=[(6, 5)]))[0], "SPLIT 2")

    def test_respects_team_limit_and_collects_pearl(self):
        self.assertEqual(run(turn(length=6, units=64, pearls=[(6, 5)]))[0], "MOVE E")

    def test_lower_id_signals_close_facing_friend(self):
        block = turn(length=3, units=2, other_heads=[("A", 5, 3)])
        block = block.replace("A 1 5 3 W 1", "A 8 5 3 S 1")
        self.assertEqual(run(block)[:2], ["MOVE N", "SONAR 1146242894"])

    def test_sonar_receiver_moves_aside(self):
        block = turn(length=3, units=2, other_heads=[("A", 5, 3)])
        block = block.replace("NUM_MSGS 0", "NUM_MSGS 1\n1146242894")
        self.assertIn(run(block, dragon_id=8)[0], ("MOVE E", "MOVE W"))

    def test_does_not_signal_unaligned_friend(self):
        block = turn(length=3, units=2, other_heads=[("A", 6, 3)])
        block = block.replace("A 1 6 3 W 1", "A 8 6 3 S 1")
        self.assertNotIn("SONAR 1146242894", run(block))


if __name__ == "__main__":
    unittest.main()

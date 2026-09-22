"""Protocol tests for the separate escort strategy."""
import subprocess
import unittest
from test_bot import BOT, turn


def run(*blocks, dragon_id=0):
    blocks = [block.replace("A 0 ", f"A {dragon_id} ") for block in blocks]
    result = subprocess.run([BOT], input=f"ID {dragon_id}\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" +
                            "".join(blocks), capture_output=True, text=True, check=True, timeout=2)
    return [line for line in result.stdout.splitlines() if line.startswith(("MOVE ", "SPLIT "))]


class Escorts(unittest.TestCase):
    def test_captain_eats_near_its_escort(self):
        self.assertEqual(run(turn(length=3, units=2, pearls=[(6, 5)],
                                  other_heads=[("A", 6, 4)])), ["MOVE E"])

    def test_captain_eats_after_its_one_birth(self):
        self.assertEqual(run(turn(length=6), turn(length=6, pearls=[(6, 5)])), ["SPLIT 2", "MOVE E"])

    def test_captain_still_avoids_enemy_contested_pearl(self):
        self.assertNotEqual(run(turn(length=3, pearls=[(6, 5)],
                                     other_heads=[("B", 7, 5)]))[0], "MOVE E")

    def test_captain_does_not_eat_covered_pearl(self):
        self.assertEqual(run(turn(length=3, pearls=[(6, 5), (4, 5)], bodies=[(6, 5)])), ["MOVE W"])

    def test_captain_does_not_enter_dead_end_for_pearl(self):
        self.assertNotEqual(run(turn(length=3, pearls=[(6, 5)],
                                     bodies=[(6, 4), (7, 5), (6, 6)]))[0], "MOVE E")

    def test_captain_makes_only_one_child(self):
        self.assertEqual(run(turn(length=6), turn(length=4, units=2, pearls=[(6, 5)]),
                             turn(length=2, units=3, pearls=[(6, 5)])),
                         ["SPLIT 2", "MOVE E", "MOVE E"])

    def test_losing_escort_does_not_reset_birth_allowance(self):
        actions = run(turn(length=6, units=3, other_heads=[("A", 2, 2), ("A", 8, 2)]),
                      turn(length=6, units=2, other_heads=[("A", 2, 2)]))
        self.assertEqual(actions[0], "SPLIT 2")
        self.assertTrue(actions[1].startswith("MOVE "))

    def test_guard_intercepts_enemy_near_captain(self):
        self.assertEqual(run(turn(length=2, units=2,
                                  other_heads=[("A", 5, 3), ("B", 6, 5)]), dragon_id=10), ["MOVE E"])

    def test_guard_does_not_hit_friendly_head(self):
        action = run(turn(length=2, units=2, other_heads=[("A", 6, 5)]), dragon_id=10)[0]
        self.assertTrue(action.startswith("MOVE "))
        self.assertNotEqual(action, "MOVE E")

    def test_guard_leaves_captain_exits_clear(self):
        action = run(turn(length=2, units=2, other_heads=[("A", 5, 3)]), dragon_id=10)[0]
        self.assertIn(action, ("MOVE E", "MOVE S", "MOVE W"))

    def test_guard_births_once_then_resumes_escort_role(self):
        actions = run(turn(length=8, units=2, other_heads=[("A", 5, 3)]),
                      turn(length=6, units=3, other_heads=[("A", 5, 3)]), dragon_id=10)
        self.assertEqual(actions[0], "SPLIT 2")
        self.assertTrue(actions[1].startswith("MOVE "))

    def test_lost_guard_does_not_elect_itself(self):
        self.assertTrue(run(turn(length=2, units=2), dragon_id=10)[0].startswith("MOVE "))

    def test_last_survivor_becomes_captain(self):
        self.assertEqual(run(turn(length=4, units=1), dragon_id=10), ["SPLIT 2"])

    def test_team_limit_is_respected(self):
        block = turn(length=6, units=64)
        self.assertTrue(run(block)[0].startswith("MOVE "))


if __name__ == "__main__":
    unittest.main()

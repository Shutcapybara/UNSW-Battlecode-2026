"""Protocol-level behaviour tests; no third-party dependencies."""
import subprocess
import sys
import unittest

BOT = sys.argv.pop(1)


def turn(pearls=(), bodies=(), walls=(), portals=(), head=(5, 5), length=6, units=1,
         other_heads=()):
    x, y = head
    rows = ["ROUND 1", "DIR N", f"LENGTH {length}", f"UNIT_COUNT {units}", "NUM_MSGS 0"]
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            p = ((x + dx) % 11, (y + dy) % 11)
            rows.append(f"{p[0]} {p[1]} {int(p in pearls)} -1")
    parts = [(x, y), *bodies]
    rows.append(f"DRAGON_BODIES {len(parts) + len(other_heads)}")
    rows.extend(f"A 0 {a} {b} N {int(i == 0)}" for i, (a, b) in enumerate(parts))
    rows.extend(f"{team} {i + 1} {a} {b} W 1"
                for i, (team, a, b) in enumerate(other_heads))
    horizontal = [["."] * 7 for _ in range(8)]
    vertical = [["."] * 8 for _ in range(7)]
    for direction in walls:
        array, row, col = {"N": (horizontal, 3, 3), "S": (horizontal, 4, 3),
                           "W": (vertical, 3, 3), "E": (vertical, 3, 4)}[direction]
        array[row][col] = "w"
    for orientation, row, col, portal in portals:
        (horizontal if orientation == "h" else vertical)[row][col] = str(portal)
    rows.extend(" ".join(row) for row in horizontal + vertical)
    return "\n".join(rows) + "\n"


def run_new_dragon(*turns):
    result = subprocess.run([BOT], input="ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" +
                            "".join(turns), text=True, capture_output=True, timeout=2, check=True)
    return result.stdout.splitlines()


def run(*turns):
    # Existing movement/survival checks exercise a parent that has already
    # produced its child. Reproduction itself is tested separately below.
    return run_new_dragon(turn(length=6), *turns)[2:]

class Behaviour(unittest.TestCase):
    def test_two_step_escape_from_short_sprint_threat(self):
        self.assertIn(run(turn(walls="NSW", other_heads=[("B", 8, 5)]))[0],
                      ("MOVE EN", "MOVE ES"))

    def test_cannot_pay_for_escape_at_length_two(self):
        self.assertEqual(run(turn(length=2, walls="NSW",
                                  other_heads=[("B", 8, 5)]))[0], "MOVE E")

    def test_first_step_pearl_can_pay_for_escape(self):
        self.assertIn(run(turn(length=2, walls="NSW", pearls=[(6, 5)],
                               other_heads=[("B", 8, 5)]))[0], ("MOVE EN", "MOVE ES"))

    def test_sprint_does_not_cross_body_or_reverse_into_neck(self):
        self.assertEqual(run(turn(walls="NSW", other_heads=[("B", 8, 5)],
                                  bodies=[(6, 4), (6, 6), (7, 5)]))[0], "SPLIT 4")

    def test_sprint_requires_visible_safe_onward_space(self):
        self.assertEqual(run(turn(walls="NSW", other_heads=[("B", 8, 5)],
                                  bodies=[(6, 3), (7, 4), (6, 6)],
                                  portals=[("v", 2, 4, "w")]))[0], "MOVE E")

    def test_keep_buffer_instead_of_chasing_contested_pearl(self):
        self.assertIn(run(turn(pearls=[(6, 5)], other_heads=[("B", 8, 4)]))[0],
                      ("MOVE S", "MOVE W"))

    def test_safe_normal_move_does_not_spend_segment(self):
        self.assertEqual(len(run(turn(other_heads=[("B", 8, 5)]))[0]), len("MOVE N"))

    def test_one_child_as_soon_as_possible(self):
        self.assertEqual(run_new_dragon(turn(length=6), turn(length=4, units=2, pearls=[(6, 5)]),
                                         turn(length=6, units=3, pearls=[(6, 5)])),
                         ["SPLIT 2", "ENDTURN", "MOVE E", "ENDTURN", "MOVE E", "ENDTURN"])

    def test_waits_for_growth_before_child(self):
        self.assertEqual(run_new_dragon(turn(length=2, pearls=[(6, 5)]), turn(length=4)),
                         ["MOVE E", "ENDTURN", "SPLIT 2", "ENDTURN"])

    def test_reproduction_waits_for_team_capacity(self):
        self.assertEqual(run_new_dragon(turn(length=6, units=64, pearls=[(6, 5)]),
                                         turn(length=6, units=63)),
                         ["MOVE E", "ENDTURN", "SPLIT 2", "ENDTURN"])

    def test_new_child_starts_its_own_reproduction(self):
        self.assertEqual(run_new_dragon(turn(length=2, pearls=[(6, 5)]), turn(length=4)),
                         ["MOVE E", "ENDTURN", "SPLIT 2", "ENDTURN"])

    def test_ignore_pearl_target_under_own_body(self):
        # Even conflicting pearl/body input must never make us chase our tail.
        self.assertEqual(run(turn(pearls=[(6, 5), (4, 5)],
                                  bodies=[(6, 5)]))[0], "MOVE W")

    def test_cleared_body_tile_can_be_targeted_next_turn(self):
        self.assertEqual(run(turn(pearls=[(6, 5), (4, 5)], bodies=[(6, 5)]),
                             turn(pearls=[(6, 5)])),
                         ["MOVE W", "ENDTURN", "MOVE E", "ENDTURN"])

    def test_avoidance_prediction_is_preserved(self):
        for team in ("A", "B"):
            for x, y in ((7, 5), (6, 4), (8, 5)):
                action = run(turn(pearls=[(6, 5)], other_heads=[(team, x, y)]))[0]
                self.assertTrue(action.startswith("MOVE "))
                self.assertNotEqual(action, "MOVE E")

    def test_nearby_head_does_not_trigger_split(self):
        for team in ("A", "B"):
            self.assertEqual(run(turn(walls="NSW",
                                      other_heads=[(team, 7, 5)]))[0], "MOVE E")

    def test_all_directions_threatened_still_moves(self):
        self.assertTrue(run(turn(other_heads=[("B", 6, 4), ("B", 4, 6)]))[0].startswith("MOVE "))

    def test_physical_dead_end_still_triggers_early_split(self):
        self.assertEqual(run(turn(walls="NSW", pearls=[(6, 5)],
                                  bodies=[(6, 4), (7, 5), (6, 6)]))[0], "SPLIT 4")

    def test_actual_head_still_blocks_movement(self):
        self.assertEqual(run(turn(walls="NSW", other_heads=[("B", 6, 5)]))[0], "SPLIT 4")

    def test_seek_nearest_pearl(self):
        self.assertEqual(run(turn(pearls=[(6, 5), (5, 2)])), ["MOVE E", "ENDTURN"])

    def test_detour_around_kelp(self):
        self.assertEqual(run(turn(pearls=[(7, 5)], walls="NES"))[0], "MOVE W")

    def test_wrap_to_pearl(self):
        self.assertEqual(run(turn(head=(0, 5), pearls=[(10, 5)]))[0], "MOVE W")

    def test_occupied_tail_is_not_safe(self):
        self.assertEqual(run(turn(walls="NEW", bodies=[(5, 6)]))[0], "SPLIT 4")

    def test_split_leaves_two(self):
        for length in (4, 6, 20):
            self.assertEqual(run(turn(walls="NESW", length=length))[0], f"SPLIT {length - 2}")

    def test_split_limits(self):
        for kwargs in ({"length": 2}, {"length": 3}, {"units": 64}):
            self.assertTrue(run(turn(walls="NESW", **kwargs))[0].startswith("MOVE "))

    def test_explore(self):
        self.assertEqual(run(turn(walls="NSW"))[0], "MOVE E")

    def test_known_portal(self):
        self.assertEqual(run(turn(pearls=[(7, 5)], walls="NSW",
                                 portals=[("v", 3, 4, 12), ("v", 3, 5, 12)]))[0], "MOVE E")

    def test_portal_destination_occupied(self):
        self.assertEqual(run(turn(walls="NSW", bodies=[(7, 5)],
                                 portals=[("v", 3, 4, 12), ("v", 3, 5, 12)]))[0], "SPLIT 4")

    def test_unknown_portal_split_or_escape(self):
        options = dict(walls="NSW", portals=[("v", 3, 4, 12)])
        self.assertEqual(run(turn(**options))[0], "SPLIT 4")
        self.assertEqual(run(turn(length=3, **options))[0], "MOVE E")

    def test_multiple_turns(self):
        self.assertEqual(run(turn(pearls=[(6, 5)]), turn(pearls=[(4, 5)])),
                         ["MOVE E", "ENDTURN", "MOVE W", "ENDTURN"])


if __name__ == "__main__":
    unittest.main()

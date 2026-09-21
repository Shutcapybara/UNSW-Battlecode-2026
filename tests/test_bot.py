"""Protocol-level behaviour tests; no third-party dependencies."""
import subprocess
import sys
import unittest

BOT = sys.argv.pop(1)


def turn(pearls=(), bodies=(), walls=(), portals=(), head=(5, 5), length=6, units=1):
    x, y = head
    rows = ["ROUND 1", "DIR N", f"LENGTH {length}", f"UNIT_COUNT {units}", "NUM_MSGS 0"]
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            p = ((x + dx) % 11, (y + dy) % 11)
            rows.append(f"{p[0]} {p[1]} {int(p in pearls)} -1")
    parts = [(x, y), *bodies]
    rows.append(f"DRAGON_BODIES {len(parts)}")
    rows.extend(f"A 0 {a} {b} N {int(i == 0)}" for i, (a, b) in enumerate(parts))
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


def run(*turns):
    result = subprocess.run([BOT], input="ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" +
                            "".join(turns), text=True, capture_output=True, timeout=2, check=True)
    return result.stdout.splitlines()


class Behaviour(unittest.TestCase):
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

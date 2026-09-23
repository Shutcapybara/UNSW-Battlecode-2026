"""Directional 64-bit sonar tests for hunter v4."""
import subprocess
import sys
import unittest

BOT = sys.argv[1]
sys.path.insert(0, "tests")
from test_bot import turn


def run(block):
    result = subprocess.run(
        [BOT],
        input="ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" + block,
        capture_output=True, text=True, check=True, timeout=2,
    )
    return result.stdout.splitlines()


class HunterV4Sonar(unittest.TestCase):
    def test_broadcasts_64_bit_state_on_each_direction(self):
        output = run(turn(length=6))
        expected = str((0xA7 << 56) | (6 << 38) | (5 << 32) | (5 << 26) | (1 << 10))
        self.assertEqual(output[1:5], [f"SONAR {direction} {expected}"
                                       for direction in "NESW"])

    def test_consumes_echoes_before_vision(self):
        block = turn(length=6).replace("NUM_MSGS 0\n", "NUM_MSGS 0\nECHOES 0 0 0 0 0\n", 1)
        self.assertTrue(run(block)[0].startswith(("MOVE ", "SPLIT ")))

    def test_move_aside_only_overrides_forward_channel(self):
        block = turn(head=(5, 5), other_heads=[("A", 7, 5)]).replace("DIR N", "DIR E", 1)
        output = run(block)
        self.assertEqual(output[1], "SONAR N " + str((0xA7 << 56) | (6 << 38) | (5 << 32) | (5 << 26) | (1 << 10)))
        self.assertEqual(output[2], "SONAR E 1146242894")
        self.assertTrue(output[3].startswith("SONAR S "))
        self.assertTrue(output[4].startswith("SONAR W "))


if __name__ == "__main__":
    unittest.main()

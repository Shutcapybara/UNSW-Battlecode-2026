"""Smoke tests for the Python semantic port."""

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BOT = ROOT / "bots/formatted-hunter-v22-python/main.py"

saved = sys.argv[:]
sys.argv = ["test_bot.py", "unused"]
from test_bot import turn
sys.argv = saved


def run(block: str) -> list[str]:
    payload = "ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" + block
    result = subprocess.run([sys.executable, str(BOT)], cwd=BOT.parent,
                            input=payload, text=True, capture_output=True,
                            timeout=4, check=True)
    return result.stdout.splitlines()


class PythonHunter(unittest.TestCase):
    def test_emits_protocol_three_and_four_directional_packets(self):
        output = run(turn(length=3, units=2))
        self.assertTrue(output[0].startswith("MOVE "))
        self.assertEqual(sum(line.startswith("SONAR ") for line in output), 4)
        self.assertIn("PROTOCOL 3", output)
        self.assertEqual(output[-1], "ENDTURN")

    def test_attacks_visible_larger_enemy(self):
        block = turn(length=3, units=3, other_heads=[("B", 6, 5)])
        block = block.replace("DRAGON_BODIES 2", "DRAGON_BODIES 5")
        block = block.replace(
            "B 1 6 5 W 1",
            "B 1 6 5 W 1\nB 1 7 5 W 0\nB 1 8 5 W 0\nB 1 9 5 W 0",
        )
        output = run(block)
        self.assertEqual(output[0], "MOVE E")

    def test_splits_when_safe_and_splittable(self):
        output = run(turn(length=4, units=2))
        self.assertEqual(output[0], "SPLIT 2")


if __name__ == "__main__":
    unittest.main()

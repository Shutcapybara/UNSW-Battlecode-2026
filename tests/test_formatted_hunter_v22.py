"""Compile the modular Hunter V22 and verify its default policy is unchanged."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "bots/hunter-v22-frontier-exploration/main.cpp"
MODULAR = ROOT / "bots/formatted-hunter-v22/main.cpp"

saved_argv = sys.argv[:]
sys.argv = ["test_bot.py", "unused"]
from test_bot import turn
sys.argv = saved_argv


class FormattedHunterV22(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="hunter-v22-test-")
        directory = Path(cls.temp.name)
        cls.original = directory / "original"
        cls.modular = directory / "modular"
        flags = ["-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-O2"]
        subprocess.run(["g++", *flags, str(ORIGINAL), "-o", str(cls.original)],
                       cwd=ROOT, check=True)
        subprocess.run(["g++", *flags, str(MODULAR), "-o", str(cls.modular)],
                       cwd=ROOT, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def run_bot(bot, block, dragon_id=0):
        payload = (f"ID {dragon_id}\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" + block)
        return subprocess.run([bot], input=payload, text=True, capture_output=True,
                              timeout=3, check=True).stdout

    def test_representative_turns_match_original_byte_for_byte(self):
        fixtures = [
            turn(),
            turn(length=6, units=3, other_heads=[("B", 6, 5)]),
            turn(length=6, units=64, pearls=[(6, 5)]),
            turn(length=3, units=2, walls="N"),
            turn(length=8, units=5, pearls=[(4, 5), (7, 5)],
                 other_heads=[("A", 8, 8), ("B", 5, 8)]),
        ]
        for index, block in enumerate(fixtures):
            with self.subTest(index=index):
                expected = self.run_bot(self.original, block)
                actual = self.run_bot(self.modular, block)
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()

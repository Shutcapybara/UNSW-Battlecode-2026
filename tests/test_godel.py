"""Contract checks for the Godel lineage (docs/godel.md):

1. The frozen baseline still matches its SHA-256 manifest.
2. Parameter arms differ from the frozen baseline only by params.py (+README).
3. The mechanism master touches only ladder.py/defaults.py (+README) and its
   switches default to off.
4. Mechanism cells differ from the master only by params.py (+README).

File-discipline checks only; behavioural parity is established by the
deterministic screen reproductions recorded in docs/godel.md section 5.
"""
from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
BOTS = ROOT / "bots"
X01 = BOTS / "godel-x01-frozen"
X21 = BOTS / "godel-x21-mech"
CODE = (".py", ".toml")


def code_files(d):
    return {f.name for f in d.iterdir() if f.suffix in CODE}


class GodelDisciplineTests(unittest.TestCase):
    def test_frozen_baseline_hashes(self):
        manifest = json.loads((ROOT / "tools/godel/frozen.json").read_text())
        self.assertEqual(manifest["mismatches"], [])
        for name, sha in manifest["sha256_by_file"].items():
            actual = hashlib.sha256((X01 / name).read_bytes()).hexdigest()
            self.assertEqual(actual, sha, f"godel-x01-frozen/{name} drifted from the frozen manifest")

    def test_parameter_arms_are_params_only(self):
        arms = ["godel-x02-pacifist", "godel-x03-berserk"] + [
            f"godel-x{n:02d}-{s}" for n, s in [
                (4, "attackunits4"), (5, "margin1"), (6, "strikebonus2"), (7, "tradebias25"),
                (8, "pstrike06"), (9, "midhunt55"), (10, "crownkill340"), (11, "tradebias35"),
                (12, "tb25-margin1"), (13, "tb25-au4"), (14, "tb25-ps2-05"), (15, "tb25-gs4"),
                (16, "ps2only"), (17, "ps2-065"), (18, "ps3-030"), (19, "ps1-090"),
                (20, "inc-margin1")]]
        base = code_files(X01)
        for arm in arms:
            d = BOTS / arm
            with self.subTest(arm=arm):
                self.assertTrue(d.is_dir(), f"{arm} missing")
                extra = code_files(d) - base
                self.assertEqual(extra, {"params.py"}, f"{arm} adds files beyond params.py: {extra}")
                for name in base:
                    self.assertEqual((d / name).read_bytes(), (X01 / name).read_bytes(),
                                     f"{arm}/{name} differs from the frozen baseline")

    def test_mech_master_surface(self):
        for name in code_files(X01):
            if name in ("ladder.py", "defaults.py"):
                continue
            self.assertEqual((X21 / name).read_bytes(), (X01 / name).read_bytes(),
                             f"godel-x21-mech/{name} must not differ from x01")
        defaults = (X21 / "defaults.py").read_text()
        for key in ("strike_support_radius=0", "strike_gate_supported=0", "strike_relax_supported=0"):
            self.assertIn(key, defaults, f"mechanism switch must default off: {key}")

    def test_mechanism_cells_are_params_only(self):
        base = code_files(X21)
        for cell in ["godel-x22-incumbent", "godel-x23-gm1", "godel-x24-gm2", "godel-x25-gm12"]:
            d = BOTS / cell
            with self.subTest(cell=cell):
                self.assertTrue(d.is_dir(), f"{cell} missing")
                extra = code_files(d) - base
                self.assertEqual(extra, {"params.py"}, f"{cell} adds files beyond params.py: {extra}")
                for name in base:
                    self.assertEqual((d / name).read_bytes(), (X21 / name).read_bytes(),
                                     f"{cell}/{name} differs from the mech master")


if __name__ == "__main__":
    unittest.main()

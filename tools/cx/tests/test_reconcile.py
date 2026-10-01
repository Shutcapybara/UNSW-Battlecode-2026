"""Part-1 reconciliation tests: the union of the cx/b and cx/f tool features.

Run with the unswbc 1.2.2 venv so arena.py imports:
    ~/.venvs/bc122/bin/python -m pytest tools/cx/tests -q
or plainly (the arena tests skip without unswbc):
    python3 -m pytest tools/cx/tests -q
ablate.py and bench.py have no unswbc dependency.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
CX = HERE.parent
sys.path.insert(0, str(CX))


def load_module(name: str):
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


def write_rows(path: pathlib.Path, rows: list[dict]) -> None:
    with path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def game_row(m, side, seed, opp, us_len, them_len=10, result="win"):
    return {"map": m, "side": side, "seed": seed, "cand": "c", "opp": opp, "sandbox": False,
            "result": result, "rounds": 250,
            "us": {"len_r100": us_len, "units_r100": 5, "eaten_r100": 20, "deaths": {},
                   "deaths_cause_r100": {}, "turns": 400},
            "them": {"len_r100": them_len}}


class TestAblate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module("ablate")

    def setUp(self):
        if self.mod is None:
            self.skipTest("ablate import failed")

    def _run(self, a, b, extra):
        buf = io.StringIO()
        old = sys.argv
        sys.argv = ["ablate", str(a), str(b)] + extra
        try:
            with contextlib.redirect_stdout(buf):
                self.mod.main()
        finally:
            sys.argv = old
        return buf.getvalue()

    def test_filter_and_exclude(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = pathlib.Path(td)
            a = tdp / "a.jsonl"
            b = tdp / "b.jsonl"
            write_rows(a, [game_row("portals", "A", 1, "yuna", 30), game_row("var/x_tr", "A", 1, "yuna", 30),
                           game_row("pub/y_rec", "A", 1, "yuna", 30)])
            write_rows(b, [game_row("portals", "A", 1, "yuna", 20), game_row("var/x_tr", "A", 1, "yuna", 20),
                           game_row("pub/y_rec", "A", 1, "yuna", 20)])
            out_all = self._run(a, b, [])
            out_live = self._run(a, b, ["--filter", "live"])
            out_panel = self._run(a, b, ["--filter", "panel"])
            out_nopub = self._run(a, b, ["--exclude", "pub/"])
        self.assertIn("3 common fixtures", out_all)
        self.assertIn("1 common fixtures (live)", out_live)
        self.assertIn("2 common fixtures (panel)", out_panel)
        self.assertIn("2 common fixtures", out_nopub)  # pub/ dropped, live + var kept
        # pairs print as b-a (later arm minus earlier): arm b (len 20) is worse than a (30)
        # on both kept fixtures, fixed-width columns
        for line in out_nopub.splitlines():
            if line.strip().startswith("len_r100"):
                self.assertIn("  0/  0/  2", line)
                break
        else:
            self.fail("len_r100 row missing")


class TestBenchNaming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module("bench")

    def setUp(self):
        if self.mod is None:
            self.skipTest("bench import failed")

    def test_replay_name(self):
        mod = self.mod
        self.assertEqual(mod.replay_name("portals", "B", 3, "bots/yuna-v03-core", "/tmp/r"),
                         "/tmp/r/portals_B_s3_yuna-v03-core.replay")
        self.assertEqual(mod.replay_name("var/portals_tr", "A", 1, "bots/fenrir-v18", "/tmp/r"),
                         "/tmp/r/var_portals_tr_A_s1_fenrir-v18.replay")

    def test_replay_dir_flag_and_plumbing(self):
        src = (CX / "bench.py").read_text()
        self.assertIn('"--replay-dir"', src)
        self.assertIn('"replay_dir": args.replay_dir', src)  # passed into every job
        self.assertIn("job.get(\"replay_dir\")", src)


class TestArenaPortalWalk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module("arena")

    def setUp(self):
        if self.mod is None:
            self.skipTest("arena needs unswbc (use ~/.venvs/bc122/bin/python)")

    def test_walk_no_portal(self):
        f = self.mod._walk_portals
        pe = (10, 10, set(), set())
        self.assertEqual(f((3, 3), "NNES", pe), (False, 4))

    def test_walk_first_step_portal(self):
        f = self.mod._walk_portals
        # portal on the north edge of (3, 0): stepping N from (3,0) crosses it.
        # _portal_edges returns (W, H, {(x,y)}, {(x,y)}); the h/v marker is added here.
        pe = (10, 10, {(3, 0)}, set())
        self.assertEqual(f((3, 0), "NN", pe), (True, 1))

    def test_walk_mid_path_portal_stops(self):
        f = self.mod._walk_portals
        # portal on the west edge of (4, 2): crossed stepping W *from* (4,2)
        pe = (10, 10, set(), {(4, 2)})
        crossed, n = f((5, 2), "WWE", pe)
        self.assertTrue(crossed)
        self.assertEqual(n, 2)  # second step crosses; the E is never walked

    def test_wrap_edges_are_not_portals(self):
        f = self.mod._walk_portals
        pe = (10, 10, set(), set())
        self.assertEqual(f((0, 4), "W", pe), (False, 1))   # wraps with no portal declared
        self.assertEqual(f((9, 4), "E", pe), (False, 1))

    def test_summary_fields_present_in_source(self):
        src = (CX / "arena.py").read_text()
        for k in ('"eaten_r{r}"', '"sprint_segs"', '"sprint_segs_r100"', '"portal_steps"', '"portal_deaths"'):
            self.assertIn(k, src)


if __name__ == "__main__":
    unittest.main()

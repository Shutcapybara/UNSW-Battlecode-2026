"""Part-2 C++ parity tests: a C++ bot moves through arena/bench/meter/golden
exactly like a Python one. Uses the cxmeter-bot fixture (the unswbc C++
template + CX_METER instrumentation). Needs the unswbc 1.2.2 venv:

    ~/.venvs/bc122/bin/python -m unittest tools.cx.tests.test_cxx_parity -v
"""
from __future__ import annotations

import importlib
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
CX = HERE.parent
REPO = CX.parents[1]
sys.path.insert(0, str(CX))

FIXTURE = CX / "tests" / "fixtures" / "cxmeter-bot"
MAP = str(REPO / "maps" / "trauma.map")


def module(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


def have_unswbc():
    try:
        import unswbc  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(have_unswbc(), "needs the unswbc 1.2.2 venv")
class TestArenaCxx(unittest.TestCase):
    """One native game, C++ vs C++: stats, replay-out and meter collection all
    work for a bot.toml-language c++ directory exactly as for main.py bots."""

    @classmethod
    def setUpClass(cls):
        import arena
        import meter
        cls.arena = arena
        out = tempfile.mkdtemp(prefix="cx-parity-")
        cls.metered = meter.cxx_variant(FIXTURE)  # the plain fixture prints no meter lines
        rep = str(pathlib.Path(out) / "game.replay")
        r = arena.run_game(MAP, str(cls.metered), str(cls.metered), 1, False, replay_out=rep,
                           meter_prefix="CX_METER")
        cls.r = r
        cls.rep = pathlib.Path(rep)

    def test_game_ran(self):
        self.assertEqual(self.r["map"], "trauma")
        self.assertGreater(self.r["rounds"], 50)
        self.assertIn("rounds", self.r)

    def test_replay_written(self):
        self.assertTrue(self.rep.exists() and self.rep.stat().st_size > 1000)

    def test_meter_lines_collected(self):
        m = self.r["meter"]
        for t in "AB":
            self.assertGreater(len(m[t]), 50)
            for ln in m[t][:5]:
                for k in ("parse=", "sense=", "policy=", "bfs="):
                    self.assertIn(k, ln)

    def test_summary_portal_fields(self):
        for t in "AB":
            s = self.r["stats"][t]
            for k in ("eaten_r50", "eaten_r100", "eaten_r150", "eaten_r250",
                      "sprint_segs", "sprint_segs_r100", "portal_steps", "portal_deaths"):
                self.assertIn(k, s)


@unittest.skipUnless(have_unswbc(), "needs the unswbc 1.2.2 venv")
class TestMeterCxx(unittest.TestCase):
    def test_mentions_macro(self):
        meter = module("meter")
        self.assertTrue(meter.mentions_macro(FIXTURE, "CX_METER"))
        self.assertFalse(meter.mentions_macro(FIXTURE, "ANNA_MEASURE"))
        ares = REPO / "bots" / "ares-v06-expanded-search-support"
        if ares.is_dir():
            self.assertFalse(meter.mentions_macro(ares, "CX_METER"))  # auto mode -> anna for ares

    def test_phases_from_lines(self):
        meter = module("meter")
        ph = meter.phases_from_lines(["parse=10 sense=20 policy=30 bfs=5",
                                      "parse=11 sense=21 policy=31 bfs=6",
                                      "parse=12 sense=22 policy=32 bfs=7"])
        self.assertEqual(ph["parse"], {"p50": 11, "p99": 12, "max": 12, "n": 3})
        self.assertEqual(ph["bfs"]["p50"], 6)

    def test_cxx_variant_defines_meter(self):
        meter = module("meter")
        dst = meter.cxx_variant(FIXTURE)
        self.addCleanup(shutil.rmtree, dst.parent, ignore_errors=True)
        self.assertTrue(dst.name.endswith("-cxmeter"))
        head = (dst / "main.cpp").read_text().splitlines()[0]
        self.assertEqual(head, "#define CX_METER 1")


@unittest.skipUnless(have_unswbc(), "needs the unswbc 1.2.2 venv")
class TestGoldenCxx(unittest.TestCase):
    """record a C++ bot, replay it against its own transcript (0 divergences),
    then run the suite command over the recordings directory."""

    @classmethod
    def setUpClass(cls):
        import golden
        cls.golden = golden
        cls.tmp = tempfile.mkdtemp(prefix="cx-golden-")

        class A:  # minimal args namespace for record
            map, bot, opp = MAP, str(FIXTURE), str(FIXTURE)
            side, seed, sandbox, out, gzip = "A", 1, False, str(pathlib.Path(cls.tmp) / "t" / "cxmeter-bot.jsonl"), True
        golden.record(A())
        # a second short recording so suite() has two files
        rec2 = pathlib.Path(cls.tmp) / "t" / "cxmeter-bot.jsonl.gz"
        out2 = rec2.with_name("second.jsonl.gz")
        out2.write_bytes(rec2.read_bytes())
        cls.dir = pathlib.Path(cls.tmp) / "t"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def args(self, **kw):
        return type("A", (), dict({"all": False, "ignore_sonar": False, "free_sonar": False,
                                   "keep_debug": False, "dragons": None}, **kw))()

    def test_replay_self_zero_divergence(self):
        g = self.golden
        tr = str(next(self.dir.glob("cxmeter-bot.jsonl.gz")))
        argv, cwd = g.launcher(str(FIXTURE))
        n, div, _ = g.replay_one(tr, argv, cwd, self.args())
        self.assertGreater(n, 100)
        self.assertEqual(div, 0)

    def test_suite_aggregates(self):
        g = self.golden
        argv, cwd = g.launcher(str(FIXTURE))
        import contextlib, io
        buf = io.StringIO()
        import types
        a = self.args(all=True)
        a.bot, a.transcripts = str(FIXTURE), str(self.dir)
        with contextlib.redirect_stdout(buf):
            rc = g.suite(a)
        self.assertEqual(rc, 0)
        self.assertIn("2 transcripts", buf.getvalue())


@unittest.skipUnless(have_unswbc(), "needs the unswbc 1.2.2 venv")
class TestRunPanelPrebuild(unittest.TestCase):
    def test_prebuild_ok_and_loud_failure(self):
        from tools.analysis.features.run_panel import prebuild
        prebuild([str(FIXTURE)])  # compiles (cached), no exception
        with tempfile.TemporaryDirectory() as td:
            bad = pathlib.Path(td) / "broken"
            bad.mkdir()
            (bad / "main.cpp").write_text("int main() { this does not compile")
            (bad / "bot.toml").write_text('[project]\nlanguage = "c++"\ninclude = ["*.cpp"]\n')
            with self.assertRaises(SystemExit) as cm:
                prebuild([str(bad)])
            self.assertIn("BUILD FAILED", str(cm.exception))


@unittest.skipUnless(have_unswbc(), "needs the unswbc 1.2.2 venv")
class TestBenchPrebuildLoud(unittest.TestCase):
    def test_run_aborts_on_build_failure(self):
        bench = module("bench")
        with tempfile.TemporaryDirectory() as td:
            bad = pathlib.Path(td) / "broken"
            bad.mkdir()
            (bad / "main.cpp").write_text("int main() { nope")
            (bad / "bot.toml").write_text('[project]\nlanguage = "c++"\ninclude = ["*.cpp"]\n')
            a = type("A", (), dict(cand=str(bad), opp=str(FIXTURE), maps="trauma", seeds="1",
                                   sides="A", jobs=1, sandbox=False, out=str(pathlib.Path(td) / "o.jsonl"),
                                   shard=None, replay_dir=None))()
            rc = bench.run(a)
            self.assertEqual(rc, 2)
            self.assertFalse(pathlib.Path(a.out).exists())  # nothing scored


if __name__ == "__main__":
    unittest.main()

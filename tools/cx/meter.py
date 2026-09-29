#!/usr/bin/env python3
"""Sandbox CPU-point breakdown for a cx/anna C++ bot.

    python3 tools/cx/meter.py bots/<bot> [--opp bots/<opp>] [--fixtures schooltime:A,portals:B]
        [--mode auto|anna|cxx]

Two ways to get the parse/sense/policy/BFS breakdown, one per bot family:

- anna (default for the anna/cx chassis): builds copies of the bot under
  build/cx/meter/ with ANNA_MEASURE = 1 (helper parse only), 2 (parse +
  World::sense) and 3 (full turn + 10 extra whole-map BFS), plays each fixture
  under --sandbox, and derives: parse = m1, sense = m2 - m1, policy = full -
  m2, BFS = (m3 - full) / 10. Every figure includes the judge's fixed write
  cost (2.5 M + 4 k/byte).

- cxx (any C++ bot whose sources mention CX_METER; auto picks it when they do):
  builds one copy with `#define CX_METER 1` prepended to main.cpp and collects
  the phase lines that the bot then prints to stderr once per turn:

      CX_METER parse=<us> sense=<us> policy=<us> bfs=<us>

  (integer microseconds; bfs optional). arena.py hands the lines out of the
  game and the runner's stderr never reaches the engine or the replay, so the
  timing build plays the same game as the plain one. Phase figures are the
  bot's own timings, not sandbox points; the whole-turn p50/p99/max points and
  the boot turn still come from the sandbox metering next to them.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
from arena import run_game  # noqa: E402

PROBE = "schooltime:A,portals:B,slithery_fight:A,trauma:B"
SOURCE_SUFFIXES = (".c", ".cc", ".cpp", ".cxx", ".c++", ".h", ".hh", ".hpp", ".hxx")


def variant(bot: pathlib.Path, k: int) -> pathlib.Path:
    dst = REPO / "build" / "cx" / "meter" / f"{bot.name}-m{k}"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(bot, dst, ignore=shutil.ignore_patterns(".unswbc-build", "__pycache__"))
    main = dst / "main.cpp"
    main.write_text(f"#define ANNA_MEASURE {k}\n" + main.read_text())
    return dst


def cxx_variant(bot: pathlib.Path) -> pathlib.Path:
    dst = REPO / "build" / "cx" / "meter" / f"{bot.name}-cxmeter"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(bot, dst, ignore=shutil.ignore_patterns(".unswbc-build", "__pycache__"))
    main = dst / "main.cpp"
    main.write_text("#define CX_METER 1\n" + main.read_text())
    return dst


def mentions_macro(bot: pathlib.Path, macro: str) -> bool:
    pat = re.compile(rf"\b{macro}\b")
    for p in sorted(bot.rglob("*")):
        if p.is_file() and p.suffix in SOURCE_SUFFIXES and ".unswbc-build" not in p.parts:
            if pat.search(p.read_text(errors="replace")):
                return True
    return False


def phases_from_lines(lines: list[str]) -> dict:
    """CX_METER payloads -> per-phase {p50, p99, max, n} in microseconds."""
    vals: dict[str, list[int]] = {}
    for ln in lines:
        for tok in ln.split():
            k, _, v = tok.partition("=")
            if k and v.isdigit():
                vals.setdefault(k, []).append(int(v))
    out = {}
    for k, v in vals.items():
        v.sort()
        out[k] = {"p50": v[len(v) // 2], "p99": v[max(0, -(-99 * len(v) // 100) - 1)],
                  "max": v[-1], "n": len(v)}
    return out


def pct(a: list[int], q: int) -> int:
    a = sorted(a)
    return a[max(0, -(-q * len(a) // 100) - 1)] if a else 0


def run_anna(bot, opp, fixtures, seed):
    variants = {"full": bot, "m1_parse": variant(bot, 1), "m2_sense": variant(bot, 2),
                "m3_bfs10": variant(bot, 3)}
    out = {}
    for fx in fixtures:
        m, side = fx.split(":")
        mp = str(REPO / "maps" / f"{m}.map")
        row = {}
        for name, path in variants.items():
            a, b = (str(path), opp) if side == "A" else (opp, str(path))
            r = run_game(mp, a, b, seed, sandbox=True)
            st = r["stats"][side]
            row[name] = {"points": st.get("points"), "boot": st.get("boot"),
                         "errors": len([e for e in r["errors"] if e[2] == side])}
        out[fx] = row
        f = row["full"]["points"]
        p1, p2, p3 = (row[k]["points"] for k in ("m1_parse", "m2_sense", "m3_bfs10"))
        print(f"{fx:>18}  full p50 {f['p50']/1e6:.2f}M p99 {f['p99']/1e6:.2f}M max {f['max']/1e6:.2f}M"
              f"  boot max {row['full']['boot']['max']/1e6:.2f}M  errors {row['full']['errors']}")
        print(f"{'':>18}  parse p50 {p1['p50']/1e6:.2f}M  sense +{(p2['p50']-p1['p50'])/1e6:.2f}M"
              f"  policy +{(f['p50']-p2['p50'])/1e6:.2f}M  BFS {(p3['p50']-f['p50'])/10/1e6:.3f}M each"
              f"  (boot parse-only {row['m1_parse']['boot']['max']/1e6:.2f}M)")
    return out


def run_cxx(bot, opp, fixtures, seed):
    metered = cxx_variant(bot)
    out = {}
    for fx in fixtures:
        m, side = fx.split(":")
        mp = str(REPO / "maps" / f"{m}.map")
        a, b = (str(metered), opp) if side == "A" else (opp, str(metered))
        r = run_game(mp, a, b, seed, sandbox=True, meter_prefix="CX_METER")
        st = r["stats"][side]
        ph = phases_from_lines(r["meter"][side])
        f = st.get("points")
        row = {"points": f, "boot": st.get("boot"),
               "errors": len([e for e in r["errors"] if e[2] == side]), "phases_us": ph}
        out[fx] = row
        if f:
            print(f"{fx:>18}  full p50 {f['p50']/1e6:.2f}M p99 {f['p99']/1e6:.2f}M max {f['max']/1e6:.2f}M"
                  f"  boot max {(st.get('boot') or {}).get('max', 0)/1e6:.2f}M  errors {row['errors']}")
        if ph:
            bits = "  ".join(f"{k} p50 {v['p50']/1e3:.1f}ms p99 {v['p99']/1e3:.1f}ms max {v['max']/1e3:.1f}ms"
                             for k, v in sorted(ph.items()))
            print(f"{'':>18}  {bits}")
        else:
            print(f"{'':>18}  no CX_METER lines on stderr (bot does not instrument this build?)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bot")
    ap.add_argument("--opp", default=None, help="opponent (default: the full bot itself)")
    ap.add_argument("--fixtures", default=PROBE)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--mode", choices=["auto", "anna", "cxx"], default="auto",
                    help="auto: cxx when the sources mention CX_METER, else anna")
    ap.add_argument("--json")
    args = ap.parse_args()
    bot = pathlib.Path(args.bot).resolve()
    opp = args.opp or str(bot)
    fixtures = args.fixtures.split(",")
    mode = args.mode
    if mode == "auto":
        mode = "cxx" if mentions_macro(bot, "CX_METER") else "anna"
    out = (run_cxx if mode == "cxx" else run_anna)(bot, opp, fixtures, args.seed)
    out = {"mode": mode, "bot": str(bot), "fixtures": out}
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

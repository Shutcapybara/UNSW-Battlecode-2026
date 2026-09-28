#!/usr/bin/env python3
"""kbench - kraken iteration harness.

Implements the adapt/test/benchmark loop from docs/kraken-design-framework.md.

  variant BASE NAME --set key=value ...   copy a bot, patch CFG values
  run PRESET --bots NAME [...]            benchmark via tournament.py presets
  analyze DIR [--focus NAME]              death causes, phases, CPU safety
  compare DIR_A DIR_B                     per-opponent diff of two runs

Presets:
  screen  fast smoke: 4 maps x 3 opponents, no sandbox, no replays
  bench   sandbox confirmation: 6 maps x 6 opponents
  pool    full regression: every map x the stable bot pool

Hydra bots are GLM's; presets include the stable hydra-v03-grower as a
benchmark but never hydra-v06-echo (actively edited upstream). Add it to a
run explicitly with --bots if you want that matchup.
"""

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOTS = ROOT / "bots"

PRESETS = {
    # These opponents match the reference roster in FRONTIER.md, first set for
    # the cycle-0 gauntlet: ouroboros-v10, hunter-v14, hunter-v20, fry-v14,
    # kraken-v04.
    "screen": dict(
        maps=["arena", "default_small", "trophy", "queen_of_spades"],
        opponents=["kraken-v04-eval", "fry-v14-stateful-size-aware-3",
                   "hunter-v14-cpp-hybrid-route-spacing"],
        sandbox=False, timeout=1200, jobs=8,
    ),
    "bench": dict(
        maps=["arena", "default_small", "trophy", "queen_of_spades",
              "big_empty", "schooltime"],
        opponents=["kraken-v04-eval", "fry-v14-stateful-size-aware-3",
                   "hunter-v14-cpp-hybrid-route-spacing",
                   "hunter-v20-portal-scouts", "ouroboros-v10-beacon",
                   "hydra-v10-farmclean"],
        sandbox=True, timeout=1200, jobs=8,
    ),
    "pool": dict(
        maps=None,  # every map
        opponents=["fry-v01-danger-levels", "fry-v02-dragon-hunters",
                   "fry-v03-portal-hunters", "fry-v04-escorts",
                   "fry-v05-kamikaze-swarm", "fry-v06-one-child",
                   "fry-v07-two-children", "fry-v08-pre-swarm-defense",
                   "fry-v09-pearl-seeker", "fry-v10-pearl-seeker-center",
                   "fry-v11-size-aware-hunters",
                   "fry-v12-stateful-size-aware-hunters",
                   "fry-v13-stateful-size-aware-2",
                   "fry-v14-stateful-size-aware-3",
                   "hunter-v01-team-growth", "hunter-v02-team-growth",
                   "hunter-v03-team-growth", "hunter-v04-team-state-sonar",
                   "kraken-v01-roles", "kraken-v02-bigmap",
                   "kraken-v03-judge-safe", "hydra-v03-grower"],
        sandbox=True, timeout=900, jobs=8,
    ),
}

CFG_KEY_RE = re.compile(r"^\s{4}(\w+)=", re.M)
DEATH_RE = re.compile(r"round (\d+): bot \d+ \(team ([AB])\) died: (.+)")
CPU_RE = re.compile(
    r"team (\w) points per turn:\s*p50\s+([\d.]+)M\s+p99\s+([\d.]+)M\s+"
    r"mean\s+([\d.]+)M\s+max\s+([\d.]+)M")


# ---------------------------------------------------------------------
# variant
# ---------------------------------------------------------------------
def cmd_variant(args):
    src = BOTS / args.base
    dst = BOTS / args.name
    if not (src / "bot.toml").is_file():
        sys.exit(f"no such base bot: {args.base}")
    if dst.exists():
        sys.exit(f"already exists: {args.name} (variants are new directories)")
    sets = dict(kv.split("=", 1) for kv in args.set)
    main = (src / "main.py").read_text()
    known = set(CFG_KEY_RE.findall(main))
    for key in sets:
        if key not in known:
            sys.exit(f"unknown CFG key {key!r}; known: {', '.join(sorted(known))}")
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", "build", "*.replay"))

    if sets:
        body = ", ".join(f'"{k}": {v}' for k, v in sorted(sets.items()))
        override = f"CFG.update({{{body}}})  # kbench variant params\n"
        main_path = dst / "main.py"
        text = main_path.read_text()
        marker = re.search(r"# KBENCH-PARAMS-BEGIN.*?# KBENCH-PARAMS-END\n",
                           text, re.S)
        if marker:
            text = (text[:marker.start()]
                    + "# KBENCH-PARAMS-BEGIN\n" + override
                    + "# KBENCH-PARAMS-END\n" + text[marker.end():])
        else:
            anchor = re.search(r"^VISIT_SCORE = .*$", text, re.M)
            if not anchor:
                sys.exit("base main.py has no CFG anchor; add one first")
            text = text[:anchor.end()] + "\n" + override + text[anchor.end():]
        main_path.write_text(text)

    note = args.note or ("variant of %s" % args.base)
    with open(dst / "README.md", "a") as fh:
        fh.write("\n\n## %s\n\nbase: %s; params: %s\nhypothesis: %s\n"
                 % (args.name, args.base,
                    json.dumps(sets, sort_keys=True) if sets else "unchanged",
                    note))
    print(f"created bots/{args.name} from {args.base} "
          f"with {len(sets)} override(s): {json.dumps(sets, sort_keys=True)}")


# ---------------------------------------------------------------------
# run
# ---------------------------------------------------------------------
def cmd_run(args):
    preset = PRESETS[args.preset]
    focus = args.focus or args.bots[0]
    bots = list(dict.fromkeys(args.bots + preset["opponents"]))
    cmd = [sys.executable, str(ROOT / "tools" / "benchmarking" / "tournament.py"),
           "--focus-bot", focus, "--bots", *bots,
           "--no-replays", "--jobs", str(args.jobs or preset["jobs"]),
           "--timeout", str(args.timeout or preset["timeout"])]
    if preset["maps"]:
        cmd += ["--maps", *preset["maps"]]
    if preset["sandbox"] or args.sandbox:
        cmd.append("--sandbox")
    out = args.output or (ROOT / "build" / f"kbench-{args.preset}-{focus}")
    cmd += ["--output", str(out)]
    if args.resume:
        cmd.append("--resume")
    print(" ".join(cmd), flush=True)
    os.execvp(cmd[0], cmd)


# ---------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------
def load_results(out):
    data = json.loads((Path(out) / "results.json").read_text())
    return data if isinstance(data, list) else data.get("matches", [])


def pick_focus(matches, focus):
    if focus:
        return focus
    played = Counter()
    for m in matches:
        played[m["team_a"]] += 1
        played[m["team_b"]] += 1
    return played.most_common(1)[0][0]


def cmd_analyze(args):
    out = Path(args.dir)
    matches = load_results(out)
    focus = pick_focus(matches, args.focus)
    wl = Counter()
    per_opp = defaultdict(Counter)
    deaths_loss = defaultdict(Counter)
    deaths_win = Counter()
    rounds_lost, cpu = [], []
    errors = []
    for m in matches:
        if focus not in (m["team_a"], m["team_b"]):
            continue
        opp = m["team_b"] if m["team_a"] == focus else m["team_a"]
        side = "A" if m["team_a"] == focus else "B"
        if m["outcome"] == "error":
            wl["E"] += 1
            errors.append(f"{m['map']}: {m['team_a']} vs {m['team_b']}: "
                          f"{(m.get('error') or '')[:80]}")
            continue
        won = m.get("winner") == focus
        drew = m.get("winner") is None or m["outcome"] == "draw"
        wl["D" if drew else ("W" if won else "L")] += 1
        per_opp[opp]["D" if drew else ("W" if won else "L")] += 1
        log = out / m["log"]
        if not log.is_file():
            continue
        for line in open(log, errors="replace"):
            dm = DEATH_RE.search(line)
            if dm and dm.group(2) == side and not drew:
                (deaths_win if won else deaths_loss[opp])[dm.group(3)] += 1
            cm = CPU_RE.search(line)
            if cm and cm.group(1) == side:
                cpu.append(tuple(map(float, cm.groups()[1:])) +
                           (m["map"], opp))
        if not won and not drew:
            rounds_lost.append(m["rounds"])
    print(f"focus: {focus}   W{wl['W']} D{wl['D']} L{wl['L']} E{wl['E']}")
    print("\nper-opponent:")
    for opp, c in sorted(per_opp.items()):
        print(f"  {opp:40s} W{c['W']} D{c['D']} L{c['L']}")
    if rounds_lost:
        elim = sum(1 for r in rounds_lost if r < 480)
        print(f"\nlosses: {len(rounds_lost)}  median round "
              f"{statistics.median(rounds_lost):.0f}  "
              f"eliminations {elim}  round-limit {len(rounds_lost) - elim}")
    print("\ndeath causes in losses (per opponent):")
    for opp, c in sorted(deaths_loss.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {opp:40s} {dict(c)}")
    print(f"\ndeath causes in wins: {dict(deaths_win)}")
    if cpu:
        p50, p99, mx = zip(*((c[0], c[1], c[3]) for c in cpu))
        print(f"\nCPU: p50 median {statistics.median(p50):.1f}M  "
              f"worst p99 {max(p99):.1f}M  worst max {max(mx):.1f}M")
        for c in sorted(cpu, key=lambda v: -v[3])[:3]:
            print(f"  max {c[3]:.1f}M p99 {c[1]:.1f}M  {c[4]} vs {c[5]}")
        over = [c for c in cpu if c[3] > 100]
        print(f"turns over 100M budget: {len(over)}")
    if errors:
        print(f"\nerrors ({len(errors)}):")
        for e in errors:
            print(" ", e)
    if args.json:
        (out / "analysis.json").write_text(json.dumps(dict(
            focus=focus, record=dict(wl),
            per_opponent={k: dict(v) for k, v in per_opp.items()},
            rounds_lost=rounds_lost), indent=2) + "\n")


# ---------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------
def cmd_compare(args):
    def per_opp(out):
        matches = load_results(out)
        focus = pick_focus(matches, args.focus)
        rec = defaultdict(Counter)
        for m in matches:
            if focus not in (m["team_a"], m["team_b"]):
                continue
            opp = m["team_b"] if m["team_a"] == focus else m["team_a"]
            if m["outcome"] == "error":
                rec[opp]["E"] += 1
            elif m.get("winner") == focus:
                rec[opp]["W"] += 1
            elif m.get("winner") is None or m["outcome"] == "draw":
                rec[opp]["D"] += 1
            else:
                rec[opp]["L"] += 1
        return focus, rec
    fa, ra = per_opp(args.dir_a)
    fb, rb = per_opp(args.dir_b)
    print(f"{'opponent':40s} {fa:>22s}   {fb:>22s}")
    for opp in sorted(set(ra) | set(rb)):
        a, b = ra.get(opp, Counter()), rb.get(opp, Counter())
        pa, pb = 3 * a["W"] + a["D"], 3 * b["W"] + b["D"]
        print(f"{opp:40s} {a['W']}W-{a['D']}D-{a['L']}L ({pa:3d})   "
              f"{b['W']}W-{b['D']}D-{b['L']}L ({pb:3d})   {pb - pa:+d}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("variant", help="copy a bot with CFG overrides")
    pv.add_argument("base")
    pv.add_argument("name")
    pv.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    pv.add_argument("--note", default="")
    pv.set_defaults(fn=cmd_variant)

    pr = sub.add_parser("run", help="run a benchmark preset")
    pr.add_argument("preset", choices=sorted(PRESETS))
    pr.add_argument("--bots", nargs="+", required=True,
                    help="variant(s) under test; first is the focus bot")
    pr.add_argument("--focus")
    pr.add_argument("--jobs", type=int)
    pr.add_argument("--timeout", type=float)
    pr.add_argument("--sandbox", action="store_true",
                    help="force sandbox even for the screen preset")
    pr.add_argument("--resume", action="store_true")
    pr.add_argument("--output")
    pr.set_defaults(fn=cmd_run)

    pa = sub.add_parser("analyze", help="death causes and CPU for a run")
    pa.add_argument("dir")
    pa.add_argument("--focus")
    pa.add_argument("--json", action="store_true")
    pa.set_defaults(fn=cmd_analyze)

    pc = sub.add_parser("compare", help="per-opponent diff of two runs")
    pc.add_argument("dir_a")
    pc.add_argument("dir_b")
    pc.add_argument("--focus")
    pc.set_defaults(fn=cmd_compare)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

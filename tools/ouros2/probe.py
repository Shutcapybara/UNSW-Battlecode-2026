"""Metered probes (S1 §7.2 / S2 §3): sandbox -v games, max / p99 points of our team's turns.

    python3 probe.py --bot bots/X --unswbc ~/bc122/bin/unswbc --out DIR [--fixtures schooltime:A portals:B ...]

Parses `round N: bot M (team X) points P ...` lines of the verbose log and counts faults
(exceeded CPU, MC_ERROR, no valid action by our team).
"""
import argparse
import json
import re
import subprocess
import time
from pathlib import Path

LINE = re.compile(r"round (\d+): bot (\d+) \(team ([AB])\) points (\d+)")
DEFAULT = ["schooltime:A", "portals:B", "slithery_fight:A", "trauma:B"]


def run(bot, opp, mapname, side, unswbc, out, seed):
    A, B = (bot, opp) if side == "A" else (opp, bot)
    log = out / ("%s_%s.log" % (mapname, side))
    cmd = [unswbc, "run", "--sandbox", "-v", "-o", str(out / ("%s_%s.replay" % (mapname, side))),
           "maps/%s.map" % mapname, A, B]
    if seed is not None:
        cmd[2:2] = ["--seed", str(seed)]
    t0 = time.time()
    with log.open("w") as fh:
        subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT)
    pts = []
    faults = 0
    text = re.sub(r"\x1b\[[0-9;]*m", "", log.read_text(errors="replace"))
    for m in LINE.finditer(text):
        if m.group(3) == side:
            pts.append(int(m.group(4)))
    for line in text.splitlines():
        if ("exceeded" in line or "MC_ERROR" in line or "no valid action" in line) and ("team %s" % side) in line:
            faults += 1
    res = re.findall(r"(team [AB] wins[^\n]*|draw[^\n]*)", text)
    pts.sort()
    return dict(map=mapname, side=side, turns=len(pts), max=pts[-1] / 1e6 if pts else None,
                p99=pts[int(len(pts) * 0.99)] / 1e6 if pts else None,
                p50=pts[len(pts) // 2] / 1e6 if pts else None, faults=faults,
                result=res[-1] if res else None, secs=round(time.time() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bot", required=True)
    ap.add_argument("--opp", default="bots/sinbad-v07-divecap")
    ap.add_argument("--unswbc", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--fixtures", nargs="*", default=DEFAULT)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in a.fixtures:
        m, s = f.split(":")
        r = run(a.bot, a.opp, m, s, a.unswbc, out, a.seed)
        print(json.dumps(r), flush=True)
        rows.append(r)
    (out / "probes.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()

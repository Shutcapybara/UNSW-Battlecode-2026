"""Metered probes (S1 §7.2 / P1 §4): four fixtures vs sinbad-v07, --sandbox --verbose.

  probe.py BOT [--unswbc PATH ...] --out DIR

Fixtures: Schooltime (BOT as A), Portals (B), Slithery Fight (A), Trauma (B).
Reports per fixture and toolkit: our turns, max and p99 points, faults
(exceeded CPU / MC_ERROR / no valid action lines naming our team), ACT marker
counts by round window.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
FIX = [("schooltime", "A"), ("portals", "B"), ("slithery_fight", "A"), ("trauma", "B")]
OPP = "sinbad-v07-divecap"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
PTS = re.compile(r"round (\d+): bot (\d+) \(team ([AB])\) points (\d+)")


def run(unswbc, bot, m, side, out, seed=1):
    a, b = (REPO / "bots" / bot, REPO / "bots" / OPP)
    if side == "B":
        a, b = b, a
    rp = out / ("%s_%s_%s.replay" % (Path(unswbc).parent.parent.name, m, side))
    cmd = [unswbc, "run", "--sandbox", "--verbose", "-o", str(rp), str(REPO / "maps" / (m + ".map")), str(a), str(b)]
    if "1.2" in subprocess.run([unswbc, "--version"], capture_output=True, text=True).stdout:
        cmd += ["--seed", str(seed)]
    pr = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    log = ANSI.sub("", pr.stdout + pr.stderr)
    pts = [int(p) for r, i, t, p in PTS.findall(log) if t == side]
    pts.sort()
    faults = [l for l in log.splitlines() if ("team %s" % side) in l and re.search(r"exceeded|MC_ERROR|no valid action|crash", l)]
    mcerr = len(re.findall(r"MC_ERROR", log))
    acts = {}
    cur = None
    for l in log.splitlines():
        hd = re.match(r"round (\d+): bot \d+ \(team ([AB])\)", l)
        if hd:
            cur = (int(hd.group(1)), hd.group(2))
            continue
        mm = re.search(r"(ACT:\S+)", l)
        if mm and cur and cur[1] == side:
            k = mm.group(1); r = cur[0]
            acts.setdefault(k, [0, 0]); acts[k][0] += 1
            if r <= 100:
                acts[k][1] += 1
    res = re.findall(r"team ([AB]) wins[^\n]*|draw[^\n]*", log)
    return dict(map=m, side=side, turns=len(pts), max=pts[-1] if pts else None,
                p99=pts[int(0.99 * (len(pts) - 1))] if pts else None, p50=pts[len(pts) // 2] if pts else None,
                faults=len(faults), fault_lines=faults[:5], mc_error=mcerr, acts=acts,
                result=(re.search(r"team [AB] wins[^\n]*|draw[^\n]*", log) or [None])[0])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("bot"); ap.add_argument("--unswbc", nargs="+", default=["unswbc"])
    ap.add_argument("--out", required=True); ap.add_argument("--fix", nargs="*", default=None)
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for u in a.unswbc:
        ver = subprocess.run([u, "--version"], capture_output=True, text=True).stdout.strip()
        for m, side in FIX:
            if a.fix and m not in a.fix:
                continue
            r = run(u, a.bot, m, side, out)
            r["toolkit"] = ver; r["bot"] = a.bot
            print(json.dumps(r), flush=True)
            with (out / "probes.jsonl").open("a") as fh:
                fh.write(json.dumps(r) + "\n")

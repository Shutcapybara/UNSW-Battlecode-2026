#!/usr/bin/env python3
"""Parse a `unswbc run --sandbox -v` log: CPU points for one team, faults.

Usage: probe_parse.py TEAM A|B LOGFILE [LOGFILE...]
Prints max/p99/p50 points, turn count, and any fault lines.
"""
import re
import sys

PTS = re.compile(r"^round (\d+): bot (\d+) \(team ([AB])\) points (\d+) memory (\d+)")
FAULT = re.compile(r"(exceeded CPU limit|MC_ERROR|ran out of time|timed out|exited|broken pipe|failed)", re.I)
DIED = re.compile(r"^round (\d+): bot (\d+) \(team ([AB])\) died: (.+)$", re.M)


def one(team, path):
    pts = []
    faults = []
    deaths = {}
    for line in open(path, errors="replace"):
        m = PTS.match(line)
        if m and m.group(3) == team:
            pts.append(int(m.group(4)))
        if FAULT.search(line):
            faults.append(line.strip())
    for m in DIED.finditer(open(path, errors="replace").read()):
        if m.group(3) == team:
            deaths[m.group(4)] = deaths.get(m.group(4), 0) + 1
    pts.sort()
    n = len(pts)
    out = {
        "log": path.rsplit("/", 1)[-1],
        "team": team,
        "turns": n,
        "max_M": round(pts[-1] / 1e6, 2) if n else None,
        "p99_M": round(pts[min(n - 1, int(n * 0.99))] / 1e6, 2) if n else None,
        "p50_M": round(pts[n // 2] / 1e6, 2) if n else None,
        "faults": faults[:5],
        "deaths": deaths,
    }
    return out


if __name__ == "__main__":
    team = sys.argv[1]
    for path in sys.argv[2:]:
        print(one(team, path))

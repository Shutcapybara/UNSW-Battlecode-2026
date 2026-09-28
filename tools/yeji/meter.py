#!/usr/bin/env python3
"""Metered probe report: CPU points per turn from an `unswbc run --sandbox -v`
log, plus the activation contract checked against the replay's LOG ACT:<tag>
lines.

    meter.py LOG REPLAY TEAM [BOT_DIR]      (BOT_DIR/CANDIDATE.toml: [activation_contract] markers)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ystats  # noqa: E402

PTS = re.compile(r"round (\d+): bot (\d+) \(team ([AB])\) points (\d+)")


def main():
    log, replay, team = sys.argv[1], sys.argv[2], sys.argv[3]
    text = Path(log).read_text(errors="replace")
    pts = sorted(int(m.group(4)) for m in PTS.finditer(text) if m.group(3) == team)
    exceeded = len(re.findall(r"team %s\) exceeded CPU" % team, text))
    mcerr = text.count("MC_ERROR")
    n = len(pts)
    summ = re.search(r"team %s points per turn: .*" % team, text)
    print("turns %d  max %.1fM  p99 %.1fM  p50 %.1fM  exceeded %d  MC_ERROR %d" % (
        n, pts[-1] / 1e6 if n else 0, pts[int(n * 0.99)] / 1e6 if n else 0, pts[n // 2] / 1e6 if n else 0,
        exceeded, mcerr))
    if summ:
        print("engine summary:", summ.group(0))
    res = re.search(r"team [AB] wins.*|draw.*", text)
    print("result:", res.group(0) if res else "?")
    st = ystats.analyse(replay)
    me = st["teams"][team]
    print("ACT counts:", me["act"])
    if len(sys.argv) > 4:
        try:
            import tomllib
        except ImportError:
            return
        cand = tomllib.loads((Path(sys.argv[4]) / "CANDIDATE.toml").read_text())
        rep = ystats.load(replay)
        # rounds per tag
        team_of = {}
        nid = 0
        for line in rep.map.splitlines():
            if line.startswith("DRAGON "):
                team_of[nid] = "AB"[int(line.split()[1])]
                nid += 1
        rounds = {}
        rnd = 0
        for ev in rep.events:
            w = ev.which()
            if w == "roundStart":
                rnd = ev.roundStart.round
            elif w == "dragonSplit":
                s = ev.dragonSplit
                team_of[s.childId] = "A" if str(s.team) == "a" else "B"
            elif w == "dragonLog" and team_of.get(ev.dragonLog.id) == team:
                for tok in ev.dragonLog.text.split():
                    if tok.startswith("ACT:"):
                        rounds.setdefault(tok[4:], []).append(rnd)
        for tag, lo, hi, need in cand["activation_contract"]["markers"]:
            t = tag[4:] if tag.startswith("ACT:") else tag
            got = sum(1 for r in rounds.get(t, ()) if lo <= r <= hi)
            print("  contract %-10s r%d-%d need>=%d got %d  %s" % (tag, lo, hi, need, got, "PASS" if got >= need else "FAIL"))


if __name__ == "__main__":
    main()

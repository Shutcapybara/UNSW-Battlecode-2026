"""sakura probe: one metered game, CPU profile for our team's turns (7.2).

    python3 tools/sakura/probe.py TOOLKIT MAP A_BOT B_BOT OUR_TEAM
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

def main():
    toolkit, mapname, a, b, ours = sys.argv[1:6]
    cmd = [toolkit, "run", "--sandbox", "-v", str(ROOT / "maps" / ("%s.map" % mapname)),
           str(ROOT / a), str(ROOT / b), "-o", "/tmp/probe.replay"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    log = proc.stdout + proc.stderr
    pts = []
    for ln in log.splitlines():
        m = re.search(r"round (\d+): bot (\d+) \(team ([AB])\) points (\d+)", ln)
        if m and m[3] == ours:
            pts.append(int(m[4]))
    faults = [ln for ln in log.splitlines()
              if "exceeded CPU" in ln or "MC_ERROR" in ln or "no valid action" in ln]
    rounds = re.findall(r"after (\d+) rounds", log)
    pts.sort()
    if not pts:
        print("NO POINTS PARSED. rc=%d tail:" % proc.returncode)
        print("\n".join(log.splitlines()[-8:]))
        return 1
    print("%s %s as %s: turns=%d p50=%.1fM p99=%.1fM max=%.1fM faults=%d rounds=%s" % (
        mapname, b if ours == "B" else a, ours, len(pts), pts[len(pts)//2]/1e6,
        pts[int(len(pts)*.99)]/1e6, pts[-1]/1e6, len(faults), rounds[-1] if rounds else "?"))
    for f in faults[:5]:
        print("  FAULT:", f)
    return 0

if __name__ == "__main__":
    sys.exit(main())

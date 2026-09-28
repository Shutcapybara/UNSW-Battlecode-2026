"""Per-arm pace attainment and contract statistics over panel results.

  summary.py DIR [DIR...] [--by opp]
"""
import argparse, collections, json, statistics as S, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from panel import load, score

TARGET = {"compact": {25: 6, 50: 9, 100: 18, 250: 80}, "open": {25: 6, 50: 11, 100: 19, 250: 100}}


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))] if v else float("nan")


def summarise(rs, label):
    if not rs:
        return
    me = [r["me"] for r in rs]
    at = lambda st, i: [m["at"][str(st)][i] for m in me]
    turns = sum(m["turns"] for m in me)
    ws = sum(m["deaths"].get("wall", 0) + m["deaths"].get("self", 0) for m in me)
    births = sum(m["births"] for m in me)
    nb = sum(m["newborn10"] for m in me)
    cls = rs[0]["cls"]
    on = sum(1 for r in rs if r["me"]["at"]["100"][0] >= TARGET[r["cls"]][100]) / len(rs)
    alive = {st: sum(1 for m in me if m["at"][str(st)][0] > 0) / len(me) for st in (100, 250, 400, 499)}
    acts = collections.Counter()
    for m in me:
        acts.update(m["acts"])
    print("%-34s n=%3d score %.3f | u25 %4.1f u50 %4.1f u100 %4.1f (q25 %2d) t250 %5.1f (q25 %3d) l400 %4.1f | on-pace@100 %.2f | alive r100/250/400/499 %.2f/%.2f/%.2f/%.2f | ws/1k %.1f nb/100b %.1f births/g %.0f | %s" % (
        label, len(rs), sum(map(score, rs)) / len(rs), S.median(at(25, 0)), S.median(at(50, 0)), S.median(at(100, 0)),
        q(at(100, 0), .25), S.median(at(250, 1)), q(at(250, 1), .25), S.median(at(400, 2)), on,
        alive[100], alive[250], alive[400], alive[499], 1000 * ws / max(1, turns), 100 * nb / max(1, births),
        births / len(rs), " ".join("%s=%.1f" % (k, v / len(rs)) for k, v in sorted(acts.items()) if not k.endswith("@100"))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--by", default=None)
    ap.add_argument("--opp-exclude-self", action="store_true")
    a = ap.parse_args()
    rows = load(a.dirs)
    arms = sorted({r["arm"] for r in rows})
    for arm in arms:
        ra = [r for r in rows if r["arm"] == arm]
        for cl in ("compact", "open"):
            summarise([r for r in ra if r["cls"] == cl], "%s/%s" % (arm[:24], cl))
        if a.by:
            for k in sorted({r[a.by] for r in ra}):
                summarise([r for r in ra if r[a.by] == k], "  %s=%s" % (a.by, str(k)[:24]))
    # opponents' curves (the field in this panel)
    print("-- opponents (as seen from each arm's games) --")
    for o in sorted({r["opp"] for r in rows}):
        ro = [dict(r, me=r["op"]) for r in rows if r["opp"] == o]
        for cl in ("compact", "open"):
            sel = [r for r in ro if r["cls"] == cl]
            if sel:
                u = [r["me"]["at"]["100"][0] for r in sel]; t = [r["me"]["at"]["250"][1] for r in sel]
                print("%-34s n=%3d u100 %.1f t250 %.1f" % (o[:24] + "/" + cl, len(sel), S.median(u), S.median(t)))

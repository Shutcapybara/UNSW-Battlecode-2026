"""Markdown tables for the P1 findings: attainment, survival, paired deltas, constraint statistics.

  report.py DIR --base chaewon-y04-probe --arms pace-v01 pace-v01-nolimit pace-v02 pace-v03
"""
import argparse, statistics as S, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from panel import load, score, sign_p

CLASS_T = {"compact": {25: 6, 50: 9, 100: 18, 250: 80}, "open": {25: 6, 50: 11, 100: 19, 250: 100}}
MAP_T = {  # (u25, u50, u100, t250): 29 Sep corpus, teams >= 1950 excl. 306 (same as pace-v02 params)
    "autarky": (13, 14, 19, 80.5), "default": (8, 12, 19, 69.5), "devil": (7, 10, 23, 103),
    "portals": (7, 11, 20.5, 80), "dilemma": (6, 7, 5.5, 4), "queen_of_spades": (4, 5, 9.5, 33),
    "schooltime": (6, 10, 26, 168), "slithery_fight": (30, 47.5, 61.5, 173.5), "trauma": (4, 7, 15.5, 102),
    "trophy": (5, 12, 18, 29)}


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))] if v else float("nan")


def attainment(rows, arms):
    print("| arm | class | n | u25 med/q25 | u50 med/q25 | u100 med/q25 | t250 med/q25 | on pace r100 (class) | on pace r100 (per map) | alive r100/250/400/499 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for arm in arms:
        for cl in ("compact", "open"):
            rs = [r for r in rows if r["arm"] == arm and r["cls"] == cl]
            if not rs:
                continue
            at = lambda st, i: [r["me"]["at"][str(st)][i] for r in rs]
            cells = ["%s/%s" % (S.median(at(st, i)), q(at(st, i), .25)) for st, i in ((25, 0), (50, 0), (100, 0), (250, 1))]
            onc = sum(r["me"]["at"]["100"][0] >= CLASS_T[cl][100] for r in rs) / len(rs)
            onm = sum(r["me"]["at"]["100"][0] >= MAP_T[r["map"]][2] for r in rs) / len(rs)
            al = [sum(r["me"]["at"][str(st)][0] > 0 for r in rs) / len(rs) for st in (100, 250, 400, 499)]
            print("| %s | %s | %d | %s | %.2f | %.2f | %s |" % (arm, cl, len(rs), " | ".join(cells), onc, onm, "/".join("%.2f" % a for a in al)))
    print("\nTargets (class): compact u25 6, u50 9, u100 18, t250 80; open 6, 11, 19, 100.\n")


def paired(rows, base, arms):
    idx = {(r["map"], r["seed"], r["opp"], r["side"], r["arm"]): r for r in rows}
    print("| arm vs %s | subset | pairs | base | arm | delta | better | worse | sign p |" % base)
    print("|---|---|---|---|---|---|---|---|---|")
    for arm in arms:
        ps = [(idx[k[:4] + (base,)], r) for k, r in idx.items() if k[4] == arm and k[:4] + (base,) in idx and r["opp"] != arm]
        for label, sel in (("all", ps), ("compact", [p for p in ps if p[0]["cls"] == "compact"]),
                           ("open", [p for p in ps if p[0]["cls"] == "open"])):
            if not sel:
                continue
            d = [score(c) - score(b) for b, c in sel]
            bt, wr = sum(x > 0 for x in d), sum(x < 0 for x in d)
            seeds = sorted({p[0]["seed"] for p in sel})
            print("| %s | %s (seeds %s) | %d | %.3f | %.3f | %+.3f | %d | %d | %.2f |" % (
                arm, label, ",".join(map(str, seeds)), len(sel), sum(score(b) for b, _ in sel) / len(sel),
                sum(score(c) for _, c in sel) / len(sel), sum(d) / len(d), bt, wr, sign_p(bt, wr)))
    print()


def contract(rows, arms):
    print("| arm | games | wall+self /1k turns | h2h /1k | body /1k | newborn deaths /100 births | births/game | splits r<=100 ACT:pace+ /game | ACT:pace- /game | portal steps /game |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for arm in arms:
        rs = [r for r in rows if r["arm"] == arm]
        if not rs:
            continue
        me = [r["me"] for r in rs]
        turns = sum(m["turns"] for m in me) / 1000.0
        dd = lambda c: sum(m["deaths"].get(c, 0) for m in me) / turns
        births = sum(m["births"] for m in me)
        print("| %s | %d | %.1f | %.1f | %.1f | %.1f | %.0f | %.1f | %.1f | %.0f |" % (
            arm, len(rs), dd("wall") + dd("self"), dd("h2h"), dd("body"), 100.0 * sum(m["newborn10"] for m in me) / max(1, births),
            births / len(rs), sum(m["acts"].get("ACT:pace+@100", 0) for m in me) / len(rs),
            sum(m["acts"].get("ACT:pace-", 0) for m in me) / len(rs), sum(m["portal_steps"] for m in me) / len(rs)))
    print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--base", required=True)
    ap.add_argument("--arms", nargs="+", required=True); ap.add_argument("--seeds", nargs="*", type=int)
    a = ap.parse_args()
    rows = load(a.dirs)
    if a.seeds:
        rows = [r for r in rows if r["seed"] in a.seeds]
    allarms = [a.base] + a.arms
    attainment(rows, allarms)
    paired(rows, a.base, a.arms)
    contract(rows, allarms)

"""Chaewon panel runner: seeded, paired, both sides, unswbc 1.2.2.

  panel.py run  --cands A B --opps X Y --maps live10 --seeds 1 2 3 --out DIR [-j 2] [--sandbox]
  panel.py report DIR [--cands A B]         score, per opp/map, contract statistics
  panel.py pair DIR --base A --cand B       paired delta, better/worse pairs, sign-test p

Bots are directory names under bots/ (or paths).  A fixture is
(map, side, seed, opponent); pairing uses exactly that key.  Rows go to
DIR/results.jsonl (one per game, resumable).  Replays are deleted after
analysis unless --keep.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
import cstats  # noqa: E402

UNSWBC = os.environ.get("UNSWBC", str(Path.home() / "bc/bin/unswbc"))
LIVE10 = ["schooltime", "portals", "slithery_fight", "queen_of_spades", "default", "trophy",
          "dilemma", "autarky", "devil", "trauma"]
OUTCOME = re.compile(r"(?:team ([AB]) wins|draw)[^\n]*?after (\d+) rounds")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def map_path(m):
    p = Path(m)
    if p.suffix == ".map" and p.exists():
        return p
    return REPO / "maps" / (m + ".map")


def bot_path(b):
    p = Path(b)
    if p.exists():
        return p.resolve()
    return (REPO / "bots" / b).resolve()


def maps_of(spec):
    if spec == "live10":
        return LIVE10
    return spec.split(",")


def play(mapname, seed, a, b, replay, sandbox, work, timeout=900):
    cmd = [UNSWBC, "run", str(map_path(mapname)), str(a), str(b), "--seed", str(seed), "-o", str(replay)]
    if sandbox:
        cmd.append("--sandbox")
    t0 = time.time()
    try:
        pr = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(work))
        log = ANSI.sub("", pr.stdout + pr.stderr)
    except subprocess.TimeoutExpired:
        return dict(error="timeout"), time.time() - t0
    m = list(OUTCOME.finditer(log))
    if not m or not Path(replay).exists():
        return dict(error=log[-500:]), time.time() - t0
    return dict(winner=m[-1][1] or "draw", rounds=int(m[-1][2]),
                faults=len(re.findall(r"exceeded CPU|MC_ERROR|no valid action", log))), time.time() - t0


def cmd_run(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "replays").mkdir(exist_ok=True)
    res_path = out / "results.jsonl"
    done = set()
    if res_path.exists():
        for line in res_path.read_text().splitlines():
            r = json.loads(line)
            if "error" not in r:
                done.add((r["map"], r["seed"], r["cand"], r["opp"], r["side"]))
    meta = dict(cands=a.cands, opps=a.opps, maps=maps_of(a.maps), seeds=a.seeds, sandbox=a.sandbox,
                toolkit=subprocess.run([UNSWBC, "--version"], capture_output=True, text=True).stdout.strip())
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    jobs = []
    for seed in a.seeds:
        for m in maps_of(a.maps):
            for opp in a.opps:
                for cand in a.cands:
                    if opp == cand:
                        continue
                    for side in "AB":
                        if (m, seed, cand, opp, side) not in done:
                            jobs.append((m, seed, cand, opp, side))
    print("%d games -> %s" % (len(jobs), out), flush=True)
    lock = threading.Lock()
    t0 = time.time()
    n = [0]
    tally = collections.Counter()
    work = out / "work"
    work.mkdir(exist_ok=True)

    def one(job):
        m, seed, cand, opp, side = job
        ca, co = bot_path(cand), bot_path(opp)
        A, B = (ca, co) if side == "A" else (co, ca)
        rp = out / "replays" / ("%s_s%d_%s_%s_%s.replay" % (m, seed, cand, opp, side))
        r, secs = play(m, seed, A, B, rp, a.sandbox, work)
        row = dict(map=m, seed=seed, cand=cand, opp=opp, side=side, secs=round(secs, 1))
        row.update(r)
        if "error" not in r:
            w = r["winner"]
            row["res"] = "D" if w == "draw" else ("W" if w == side else "L")
            try:
                st = cstats.analyse(rp)
                other = "B" if side == "A" else "A"
                me = st["teams"][side]
                me.pop("act_rounds", None)
                op = st["teams"][other]
                row["end"] = st["end"]
                row["standing"] = [st["standing"][side], st["standing"][other]]
                row["me"] = me
                row["op"] = {k: op[k] for k in ("at", "deaths", "wall_self_per_1k", "splits", "cpu_max")}
            except Exception as exc:
                row["stats_error"] = repr(exc)
            if not (a.keep == "all" or (a.keep == "losses" and row["res"] != "W")):
                rp.unlink(missing_ok=True)
        with lock:
            with res_path.open("a") as fh:
                fh.write(json.dumps(row) + "\n")
            n[0] += 1
            tally[row.get("res", "E")] += 1
            print("[%d/%d %.0fs] %-15s s%d %-28s vs %-28s %s -> %s r%s" % (
                n[0], len(jobs), time.time() - t0, m, seed, cand[:28], opp[:28], side,
                row.get("res", "E"), row.get("rounds")), flush=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        list(ex.map(one, jobs))
    shutil.rmtree(work, ignore_errors=True)
    print(dict(tally))


def load(dirs):
    rows = {}
    for d in dirs:
        p = Path(d) / "results.jsonl"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if "error" in r:
                continue
            rows[(r["map"], r["seed"], r["cand"], r["opp"], r["side"])] = r
    return list(rows.values())


def score(r):
    return 1.0 if r["res"] == "W" else 0.5 if r["res"] == "D" else 0.0


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return float("nan")
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def sign_p(b, w):
    n = b + w
    if n == 0:
        return 1.0
    k = min(b, w)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2.0 ** n
    return min(1.0, 2 * p)


COMPACT = {"trophy", "devil", "default_small", "arena", "Colosseum"}


def contract(rs):
    me = [r["me"] for r in rs if "me" in r]
    at = lambda k, i: [m["at"].get(k, [None] * 3)[i] for m in me]
    turns = sum(m["turns"] for m in me)
    ws = sum(m["deaths"].get("wall", 0) + m["deaths"].get("self", 0) for m in me)
    births = sum(m["births"] for m in me)
    nb = sum(m["newborn_deaths10"] for m in me)
    acts = collections.Counter()
    for m in me:
        acts.update(m["act"])
    return dict(n=len(rs), score=sum(map(score, rs)) / max(1, len(rs)),
                units_r100=med(at("100", 0)), units_r250=med(at("250", 0)),
                longest_r400=med(at("400", 2)), longest_r499=med(at("499", 2)),
                total_r499=med(at("499", 1)),
                wall_self_per_1k=1000.0 * ws / max(1, turns),
                newborn_d10_per100=100.0 * nb / max(1, births),
                first_pearl=med([m["first_pearl_median"] for m in me]),
                splits_r100=med([m["splits_per_decision_r0_r100"] for m in me]),
                diss=sum(m["diss"] for m in me), diss_pearls=sum(m["diss_pearls"] for m in me),
                diss_eaten_crown=sum(m["diss_eaten_crown"] for m in me),
                diss_eaten_ally=sum(m["diss_eaten_ally"] for m in me),
                crown_alive=sum(1 for m in me if m["crown_alive_end"]),
                cpu_max=max([m["cpu_max"] for m in me] or [0]) / 1e6,
                tle=sum(m["tle"] for m in me), acts=dict(acts))


def cmd_report(a):
    rows = load(a.dirs)
    cands = a.cands or sorted({r["cand"] for r in rows})
    for c in cands:
        rs = [r for r in rows if r["cand"] == c]
        if not rs:
            continue
        k = contract(rs)
        print("\n== %s  n=%d  score %.3f" % (c, k["n"], k["score"]))
        print("   units r100 %.1f r250 %.1f | longest r400 %.1f r499 %.1f | total r499 %.1f" % (
            k["units_r100"], k["units_r250"], k["longest_r400"], k["longest_r499"], k["total_r499"]))
        print("   wall+self/1k %.2f | newborn d10 /100 births %.1f | first pearl %.1f | split/dec r0-100 %.3f" % (
            k["wall_self_per_1k"], k["newborn_d10_per100"], k["first_pearl"], k["splits_r100"]))
        print("   diss %d pearls %d eaten crown %d ally %d | crown alive %d | cpu max %.1fM tle %d" % (
            k["diss"], k["diss_pearls"], k["diss_eaten_crown"], k["diss_eaten_ally"], k["crown_alive"],
            k["cpu_max"], k["tle"]))
        print("   acts %s" % k["acts"])
        by = collections.defaultdict(list)
        for r in rs:
            by["opp:" + r["opp"]].append(score(r))
        for r in rs:
            by["map:" + r["map"]].append(score(r))
        for r in rs:
            by["side:" + r["side"]].append(score(r))
        for r in rs:
            by["class:" + ("compact" if r["map"] in COMPACT else "open")].append(score(r))
        for key in sorted(by):
            v = by[key]
            print("   %-40s %5.3f (%d)" % (key, sum(v) / len(v), len(v)))


def cmd_pair(a):
    rows = load(a.dirs)
    idx = {}
    for r in rows:
        idx[(r["cand"], r["map"], r["seed"], r["opp"], r["side"])] = r
    for cand in a.cand:
        better = worse = 0
        diffs = []
        permap = collections.defaultdict(list)
        peropp = collections.defaultdict(list)
        for (c, m, s, o, sd), r in idx.items():
            if c != cand:
                continue
            b = idx.get((a.base, m, s, o, sd))
            if b is None:
                continue
            d = score(r) - score(b)
            diffs.append(d)
            permap[m].append(d)
            peropp[o].append(d)
            if d > 0:
                better += 1
            elif d < 0:
                worse += 1
        n = len(diffs)
        if not n:
            print("%s: no pairs" % cand)
            continue
        print("\n%s vs %s: n=%d  delta %+.3f  better/worse %d/%d  sign p=%.3f" % (
            cand, a.base, n, sum(diffs) / n, better, worse, sign_p(better, worse)))
        for m, v in sorted(permap.items()):
            print("   map %-16s %+.3f (%d)" % (m, sum(v) / len(v), len(v)))
        for o, v in sorted(peropp.items()):
            print("   opp %-34s %+.3f (%d)" % (o, sum(v) / len(v), len(v)))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("--cands", nargs="+", required=True)
    p.add_argument("--opps", nargs="+", required=True)
    p.add_argument("--maps", default="live10")
    p.add_argument("--seeds", nargs="+", type=int, default=[1])
    p.add_argument("--out", required=True)
    p.add_argument("-j", "--jobs", type=int, default=2)
    p.add_argument("--sandbox", action="store_true")
    p.add_argument("--keep", default="none", choices=("all", "losses", "none"))
    p = sub.add_parser("report")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--cands", nargs="*")
    p = sub.add_parser("pair")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--base", required=True)
    p.add_argument("--cand", nargs="+", required=True)
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report, "pair": cmd_pair}[a.cmd](a)


if __name__ == "__main__":
    main()

"""sakura panel: seeded paired games on the live-pool maps (7.1).

Runs `unswbc run --seed S map A B -o replay` in parallel, then derives from
each replay the result, the replaystats metrics, the ACT:* marker counts and
the activation-contract statistics (units_r100, longest_r400, deaths per 1k
dragon-turns, newborn deaths, first pearl round, splits).

    python3 tools/sakura/panel.py run  --cand bots/sakura-s01-swarm-dissolve \
        --pool bots/yuna-v02-core bots/sinbad-v07-divecap ... \
        --maps schooltime,portals,... --seeds 1 --jobs 4 \
        --toolkit ~/.venvs/bc122/bin/unswbc --out DIR
    python3 tools/sakura/panel.py report DIR_CONTROL DIR_ARM [DIR_ARM2 ...]

Each run writes results.jsonl (one row per game) + meta.json; report prints
paired deltas vs the control by (map, side, seed, opponent) with a sign test.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "ouroboros"))
import replaystats  # noqa: E402
import mapview  # noqa: E402

LIVE_MAPS = ["schooltime", "portals", "slithery_fight", "queen_of_spades", "default",
             "trophy", "dilemma", "autarky", "devil", "trauma"]
OUTCOME = re.compile(r"^(?:team ([AB]) wins|draw) after (\d+) rounds", re.MULTILINE)
DIRNUM = {"north": 0, "east": 1, "south": 2, "west": 3}
ANSI = re.compile(r"\x1b\[[0-9;]*m")


# ---------------------------------------------------------------- contract stats
def contract_stats(rep):
    """Per-team activation-contract statistics from a replay event stream."""
    team_of = {}
    body = {}
    headxy = {}
    lastact = {}
    nid = 0
    for line in rep.map.splitlines():
        if line.startswith("DRAGON "):
            parts = line.split()
            team = "AB"[int(parts[1])]
            n = int(parts[2])
            cells = [(int(parts[3 + 2 * i]), int(parts[4 + 2 * i])) for i in range(n)]
            team_of[nid] = team
            body[nid] = collections.deque(cells)
            headxy[nid] = cells[0]
            nid += 1
    out = {t: dict(turns=0, deaths_wall=0, deaths_self=0, deaths_body=0, deaths_h2h=0,
                   deaths_noaction=0, splits=0, newborn_deaths10=0, births=0,
                   first_pearl=10 ** 9, pearls=0, portal_deaths=0, mc_errors=0,
                   act=collections.Counter(), act_first={}, act_last={},
                   diss_delivered=0, curve=[]) for t in "AB"}
    mv = mapview.load_map(rep.map)
    PH, PV = mv["portal_h"], mv["portal_v"]
    W_, H_ = mv["W"], mv["H"]

    def portal_step(hx, hy, d):
        # did a move in direction d from (hx, hy) enter a portal edge?
        if d == 0:
            return (hx, hy) in PH
        if d == 2:
            return (hx, (hy + 1) % H_) in PH
        if d == 3:
            return (hx, hy) in PV
        return ((hx + 1) % W_, hy) in PV
    rnd = 0
    actor = -1
    born = {}
    alive = set(body)
    reasons = {"hitWall": "deaths_wall", "hitSelf": "deaths_self",
               "hitOtherBody": "deaths_body", "hitHeadToHead": "deaths_h2h",
               "noValidAction": "deaths_noaction"}
    last_sample = -1

    def sample(r):
        for t in "AB":
            lens = [len(body[i]) for i in alive if team_of.get(i) == t]
            out[t]["curve"].append((r, len(lens), sum(lens), max(lens) if lens else 0))

    def cell_id(p):
        return p.y * rep.header.width + p.x if hasattr(rep, "header") else None

    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
            if rnd // 25 != last_sample:
                last_sample = rnd // 25
                sample(rnd)
        elif w == "turnStart":
            actor = ev.turnStart.id
            t = team_of.get(actor)
            if t:
                out[t]["turns"] += 1
        elif w == "dragonLog":
            txt = str(ev.dragonLog.text)
            if txt.startswith("MC_ERROR"):
                out[team_of.get(ev.dragonLog.id, "A")]["mc_errors"] = \
                    out[team_of.get(ev.dragonLog.id, "A")].get("mc_errors", 0) + 1
            if txt.startswith("ACT:"):
                t = team_of.get(ev.dragonLog.id)
                if t:
                    tag = txt[4:]
                    out[t]["act"][tag] += 1
                    if tag not in out[t]["act_first"]:
                        out[t]["act_first"][tag] = rnd
                    out[t]["act_last"][tag] = rnd
        elif w == "dragonAction":
            a = ev.dragonAction
            la = None
            try:
                if a.action.which() == "move" and len(a.action.move):
                    la = DIRNUM[str(a.action.move[0])]
            except Exception:
                la = None
            lastact[a.id] = la
        elif w == "dragonUpdate":
            u = ev.dragonUpdate
            headxy[u.id] = (u.head.x, u.head.y)
        elif w == "tileChange":
            tc = ev.tileChange
            if not tc.hasPearl:
                t = team_of.get(actor)
                if t and actor in alive:
                    out[t]["pearls"] += 1
                    if rnd < out[t]["first_pearl"]:
                        out[t]["first_pearl"] = rnd
        elif w == "dragonSplit":
            s = ev.dragonSplit
            team = "AB"[0 if str(s.team) == "a" else 1]
            team_of[s.childId] = team
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            if s.parentBody:
                headxy[s.parentId] = (s.parentBody[0].x, s.parentBody[0].y)
            if s.childBody:
                headxy[s.childId] = (s.childBody[0].x, s.childBody[0].y)
            alive.add(s.childId)
            born[s.childId] = rnd
            out[team]["splits"] += 1
            out[team]["births"] += 1
        elif w == "dragonDeath":
            d = ev.dragonDeath
            i = d.id
            team = team_of.get(i)
            if team:
                key = reasons.get(str(d.reason))
                if key:
                    out[team][key] += 1
                la = lastact.get(i)
                if la is not None and key in ("deaths_wall", "deaths_self",
                                              "deaths_body", "deaths_h2h"):
                    hh = headxy.get(i)
                    if hh and portal_step(hh[0], hh[1], la):
                        out[team]["portal_deaths"] += 1
                b = born.get(i)
                if b is not None and rnd - b <= 10:
                    out[team]["newborn_deaths10"] += 1
            alive.discard(i)
    sample(rnd + 1)
    for t in "AB":
        d = out[t]
        deaths = d["deaths_wall"] + d["deaths_self"] + d["deaths_body"] + d["deaths_h2h"] + d["deaths_noaction"]
        d["wall_self_per_1k"] = round(1000.0 * (d["deaths_wall"] + d["deaths_self"])
                                      / max(1, d["turns"]), 2)
        d["all_deaths_per_1k"] = round(1000.0 * deaths / max(1, d["turns"]), 2)
        d["newborn_deaths_per_100"] = round(100.0 * d["newborn_deaths10"]
                                            / max(1, d["births"]), 1)
        d["first_pearl"] = d["first_pearl"] if d["first_pearl"] < 10 ** 9 else -1
        cv = d.pop("curve")
        for want, key in ((25, "units_r25"), (50, "units_r50"),
                          (100, "units_r100"), (250, "units_r250")):
            row = next((r for r in cv if r[0] == want), None)
            d[key] = row[1] if row else -1
        row = next((r for r in cv if r[0] == 250), None)
        d["total_r250"] = row[2] if row else -1
        for want, key in ((400, "longest_r400"), (500, "longest_r499")):
            row = next((r for r in cv if r[0] == want), cv[-1] if cv else None)
            d[key] = row[3] if row else -1
        d["act"] = dict(d["act"])
    return out


# ---------------------------------------------------------------- runner
def resolve(spec):
    """bot spec 'name' or 'name@k=v,...' -> (label, folder)."""
    name, _, over = spec.partition("@")
    path = Path(name)
    if not path.is_dir():
        path = ROOT / "bots" / name
    if not (path / "bot.toml").exists():
        sys.exit("no bot at %s" % path)
    if not over:
        return path.name, path
    base = {}
    if (path / "params.py").exists():
        scope = {}
        exec((path / "params.py").read_text(), scope)
        base = dict(scope.get("PARAMS", {}))
    import hashlib
    for item in over.split(","):
        k, _, v = item.partition("=")
        try:
            base[k.strip()] = int(v)
        except ValueError:
            base[k.strip()] = float(v) if "." in v else v
    digest = hashlib.sha1(json.dumps(base, sort_keys=True).encode()).hexdigest()[:8]
    target = ROOT / "build" / "sakura-variants" / ("%s__%s" % (path.name, digest))
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(path, target, ignore=shutil.ignore_patterns(
        ".unswbc-build", "__pycache__", ".git", "build"))
    (target / "params.py").write_text("PARAMS = %r\n" % (dict(sorted(base.items())),))
    return "%s@%s" % (path.name, over), target


def play(toolkit, mappath, a_path, b_path, replay, seed, sandbox, timeout):
    cmd = [str(toolkit), "run"] + (["--seed", str(seed)] if seed else []) + \
          [str(mappath), str(a_path), str(b_path), "-o", str(replay)]
    if sandbox:
        cmd.append("--sandbox")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        log = ANSI.sub("", proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired:
        return dict(winner="error", rounds=0, log_tail="timeout")
    found = list(OUTCOME.finditer(log))
    if proc.returncode != 0 or not found:
        return dict(winner="error", rounds=0, log_tail=log[-600:])
    m = found[-1]
    winner = m[1] if m[1] in "AB" else "draw"
    return dict(winner=winner, rounds=int(m[2]))


def cmd_run(args):
    maps = {}
    for name in (args.maps.split(",") if args.maps != "live" else LIVE_MAPS):
        mp = ROOT / "maps" / ("%s.map" % name)
        if not mp.exists():
            sys.exit("no map %s" % mp)
        maps[name] = mp
    cand = resolve(args.cand)
    pool = [resolve(p) for p in args.pool]
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "replays").mkdir(exist_ok=True)
    meta = dict(cand=cand[0], pool=[p[0] for p in pool], maps=list(maps),
                seeds=args.seeds, toolkit=str(args.toolkit), sandbox=args.sandbox,
                started=time.strftime("%Y%m%d-%H%M%S"))
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    jobs = []
    for opp in pool:
        if opp[0] == cand[0]:
            continue
        for mname, mpath in maps.items():
            for seed in args.seeds:
                for a, b, side in ((cand, opp, "A"), (opp, cand, "B")):
                    jobs.append((mname, mpath, a, b, side, opp[0], seed))
    results = out / "results.jsonl"
    done = set()
    if results.exists():
        for line in results.read_text().splitlines():
            try:
                r = json.loads(line)
                if r["winner"] != "error":
                    done.add((r["map"], r["side"], r["opp"], r["seed"]))
            except Exception:
                pass
    jobs = [j for j in jobs if (j[0], j[4], j[5], j[6]) not in done]
    print("%d games -> %s (skipped %d done)" % (len(jobs), out, len(done) - (len(jobs))))
    lock = threading.Lock()
    qi = [0]
    tally = collections.Counter()
    t0 = time.time()

    def work():
        while True:
            with lock:
                if qi[0] >= len(jobs):
                    return
                job = jobs[qi[0]]
                qi[0] += 1
            mname, mpath, a, b, side, opp, seed = job
            key = "%s__%s__s%d__%s" % (mname, opp, seed, side)
            rp = out / "replays" / ("%s.replay" % key)
            row = play(args.toolkit, mpath, a[1], b[1], rp, seed, args.sandbox, args.timeout)
            row.update(map=mname, side=side, opp=opp, seed=seed, cand=cand[0])
            try:
                st = replaystats.analyse(str(rp))
                row["end"] = st["end"]
                row["standing"] = st["standing"]
                row["rs"] = {t: {k: v for k, v in st["teams"][t].items() if k != "curve"}
                             for t in "AB"}
                row["contract"] = contract_stats(replaystats.load(str(rp)))
            except Exception as exc:
                row["stats_error"] = repr(exc)
            res = "D" if row["winner"] == "draw" else ("E" if row["winner"] == "error" else
                                                       ("W" if row["winner"] == side else "L"))
            row["res"] = res
            if not args.keep:
                try:
                    rp.unlink()
                except OSError:
                    pass
            with lock:
                tally[res] += 1
                with results.open("a") as fh:
                    fh.write(json.dumps(row) + "\n")
                n = sum(tally.values())
                if n % 20 == 0 or n == len(jobs):
                    print("  %d/%d  W%d L%d D%d E%d  %.1fs" % (
                        n, len(jobs), tally["W"], tally["L"], tally["D"], tally["E"],
                        time.time() - t0), flush=True)

    threads = [threading.Thread(target=work, daemon=True) for _ in range(args.jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("done %s  W%d L%d D%d E%d" % (out, tally["W"], tally["L"], tally["D"], tally["E"]))


# ---------------------------------------------------------------- report
def load_rows(d):
    rows = []
    for line in (Path(d) / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["winner"] != "error":
            rows.append(r)
    return rows


def score(rows, who):
    return sum(1.0 if r["res"] == "W" else 0.5 if r["res"] == "D" else 0.0
               for r in rows if r["cand"] == who)


def cmd_report(args):
    dirs = [Path(d) for d in args.dirs]
    ctrl_rows = load_rows(dirs[0])
    ctrl = {}
    for r in ctrl_rows:
        ctrl[(r["map"], r["side"], r["opp"], r["seed"])] = r
    print("control %s: %d games, score %.1f (%.1f%%)" % (
        dirs[0].name, len(ctrl_rows), score(ctrl_rows, ctrl_rows[0]["cand"]),
        100 * score(ctrl_rows, ctrl_rows[0]["cand"]) / max(1, len(ctrl_rows))))
    for d in dirs[1:]:
        rows = load_rows(d)
        pairs, better, worse, eq = [], 0, 0, 0
        per_map = collections.defaultdict(lambda: [0, 0.0, 0.0])
        for r in rows:
            c = ctrl.get((r["map"], r["side"], r["opp"], r["seed"]))
            if c is None:
                continue
            def pts(x):
                return 1.0 if x["res"] == "W" else 0.5 if x["res"] == "D" else 0.0
            dp = pts(r) - pts(c)
            pairs.append(dp)
            pm = per_map[r["map"]]
            pm[0] += 1
            pm[1] += pts(r)
            pm[2] += pts(c)
            if dp > 0:
                better += 1
            elif dp < 0:
                worse += 1
            else:
                eq += 1
        n = len(pairs)
        if not n:
            print("%s: no pairs" % d.name)
            continue
        # two-sided sign test on better vs worse
        try:
            from math import comb
            k, m = min(better, worse), better + worse
            p = sum(comb(m, i) for i in range(0, k + 1)) / (2.0 ** m) * 2
            p = min(1.0, p)
        except Exception:
            p = float("nan")
        print("\n%s: %d pairs  better/worse/equal %d/%d/%d  net %+.1f  sign-p=%.4f" % (
            d.name, n, better, worse, eq, sum(pairs), p))
        for m in sorted(per_map):
            pm = per_map[m]
            print("  %-16s n=%-3d arm %.1f  ctrl %.1f  delta %+.1f" % (
                m, pm[0], pm[1], pm[2], pm[1] - pm[2]))
        # contract medians for the arm's own team
        med = collections.defaultdict(list)
        for r in rows:
            ct = r.get("contract", {}).get(r["side"])
            if ct:
                for k in ("units_r25", "units_r50", "units_r100", "units_r250",
                          "total_r250", "longest_r400", "longest_r499",
                          "wall_self_per_1k", "all_deaths_per_1k", "newborn_deaths_per_100",
                          "first_pearl", "pearls", "portal_deaths"):
                    med[k].append(ct[k])
        if med:
            print("  medians: " + "  ".join("%s=%s" % (k, sorted(v)[len(v) // 2])
                                            for k, v in sorted(med.items())))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cand", required=True)
    r.add_argument("--pool", nargs="+", required=True)
    r.add_argument("--maps", default="live")
    r.add_argument("--seeds", nargs="+", type=int, default=[1])
    r.add_argument("--jobs", type=int, default=4)
    r.add_argument("--toolkit", default=os.path.expanduser("~/.venvs/bc122/bin/unswbc"))
    r.add_argument("--out", required=True)
    r.add_argument("--sandbox", action="store_true")
    r.add_argument("--keep", action="store_true")
    r.add_argument("--timeout", type=int, default=600)
    r.set_defaults(fn=cmd_run)
    p = sub.add_parser("report")
    p.add_argument("dirs", nargs="+")
    p.set_defaults(fn=cmd_report)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

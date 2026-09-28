#!/usr/bin/env python3
"""Yeji harness: seeded, paired, both-sides local panels + paired reports.

  run     yrun.py run --cands BOT[@k=v,...] ... --pool BOT ... --maps live10|m1,m2
                   --seeds 1,2,3 --jobs 2 --out DIR [--sandbox] [--keep losses|all|none]
  report  yrun.py report DIR [DIR...] --cand X --control Y      (paired by map, side, seed, opp)
  stats   yrun.py stats DIR [DIR...]                            (contract statistics medians per cand)

A candidate `name@k=v,k2=v2` is a params variant: a copy of bots/name with
params.py PARAMS updated (keys must exist in the bot's params).  Results:
DIR/results.jsonl, one line per game, with ystats per team.  Resumable.
Toolkit: UNSWBC env var or ~/.venvs/bc122/bin/unswbc (1.2.2), recorded per row.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ystats  # noqa: E402

UNSWBC = os.environ.get("UNSWBC", os.path.expanduser("~/.venvs/bc122/bin/unswbc"))
LIVE10 = ["schooltime", "portals", "slithery_fight", "queen_of_spades", "default", "trophy",
          "dilemma", "autarky", "devil", "trauma"]
COMPACT = {"portals", "trophy", "dilemma", "devil", "default_small", "arena", "Colosseum"}
OUTCOME = re.compile(r"team ([AB]) wins after (\d+) rounds|draw after (\d+) rounds|(draw)")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def toolkit_version():
    try:
        return subprocess.run([UNSWBC, "--version"], capture_output=True, text=True).stdout.strip()
    except Exception:
        return "?"


def resolve_maps(spec):
    names = LIVE10 if spec == "live10" else spec.split(",")
    return {n: ROOT / "maps" / (n + ".map") for n in names}


def parse_value(v):
    try:
        return json.loads(v)
    except Exception:
        return v


def resolve_bot(spec, build):
    name, _, over = spec.partition("@")
    src = ROOT / "bots" / name
    if not src.exists():
        raise SystemExit("no bot " + name)
    if not over:
        return spec, src
    kv = {}
    for item in over.split(","):
        k, _, v = item.partition("=")
        kv[k.strip()] = parse_value(v.strip())
    digest = hashlib.sha1(json.dumps(kv, sort_keys=True).encode()).hexdigest()[:8]
    tgt = build / "variants" / ("%s__%s" % (name, digest))
    if tgt.exists():
        shutil.rmtree(tgt)
    shutil.copytree(src, tgt, ignore=shutil.ignore_patterns(".unswbc-build", "__pycache__"))
    scope = {}
    exec((src / "params.py").read_text(), scope)
    base = dict(scope["PARAMS"])
    for k in kv:
        if k not in base:
            raise SystemExit("unknown param %s for %s" % (k, name))
    base.update(kv)
    (tgt / "params.py").write_text("PARAMS = %r\n" % (base,))
    (tgt / "VARIANT").write_text(spec + "\n")
    return spec, tgt


class Runner:
    def __init__(self, work, sandbox, timeout):
        self.work, self.sandbox, self.timeout = Path(work), sandbox, timeout

    def copy(self, label, src):
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", label)[:50] + "-" + hashlib.sha1(label.encode()).hexdigest()[:8]
        tgt = self.work / str(threading.get_ident()) / safe
        if not tgt.exists():
            shutil.copytree(src, tgt, ignore=shutil.ignore_patterns(".unswbc-build", "__pycache__"))
        return tgt

    def play(self, mpath, a, b, seed, replay):
        ca, cb = self.copy(*a), self.copy(*b)
        cmd = [UNSWBC, "run", "--seed", str(seed), "-o", str(replay), str(mpath), str(ca), str(cb)]
        if self.sandbox:
            cmd.insert(2, "--sandbox")
        t0 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout, cwd=str(self.work))
            log, rc = ANSI.sub("", p.stdout + p.stderr), p.returncode
        except subprocess.TimeoutExpired:
            log, rc = "timeout", -1
        row = dict(secs=round(time.time() - t0, 1))
        m = list(OUTCOME.finditer(log))
        if rc != 0 or not m:
            row.update(winner="error", log_tail=log[-800:])
            return row
        m = m[-1]
        row["winner"] = m.group(1) or "draw"
        row["cpu_exceeded"] = len(re.findall(r"exceeded", log))
        row["mc_error"] = log.count("MC_ERROR")
        for t, p50, p99, mx, n in re.findall(r"team ([AB]) points per turn: p50 ([\d.]+)M\s+p99 ([\d.]+)M.*?max ([\d.]+)M\s+\((\d+) turns\)", log):
            row.setdefault("points", {})[t] = dict(p50=float(p50), p99=float(p99), max=float(mx), turns=int(n))
        try:
            st = ystats.analyse(replay)
            row.update(end=st["end"], rounds=st["rounds"], standing=st["standing"], teams=st["teams"])
        except Exception as exc:
            row["stats_error"] = repr(exc)
        return row


def cmd_run(args):
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "replays").mkdir(exist_ok=True)
    build = out / "build"
    cands = [resolve_bot(c, build) for c in args.cands]
    pool = [resolve_bot(p, build) for p in args.pool]
    maps = resolve_maps(args.maps)
    seeds = [int(s) for s in args.seeds.split(",")]
    tk = toolkit_version()
    (out / "meta.json").write_text(json.dumps(dict(cands=args.cands, pool=args.pool, maps=list(maps),
                                                   seeds=seeds, sandbox=args.sandbox, toolkit=tk), indent=1))
    rp = out / "results.jsonl"
    done = set()
    if rp.exists():
        for line in rp.read_text().splitlines():
            r = json.loads(line)
            if r["winner"] != "error":
                done.add((r["map"], r["A"], r["B"], r["seed"]))
    jobs = []
    for seed in seeds:
        for mname, mpath in maps.items():
            for cand in cands:
                for opp in pool:
                    if opp[0] == cand[0]:
                        continue
                    for a, b in ((cand, opp), (opp, cand)):
                        k = (mname, a[0], b[0], seed)
                        if k not in done:
                            done.add(k)
                            jobs.append((mname, mpath, a, b, seed, cand[0]))
    print("%d games -> %s (toolkit %s)" % (len(jobs), out, tk), flush=True)
    runner = Runner(out / "work", args.sandbox, args.timeout)
    lock = threading.Lock()
    t0 = time.time()
    n = [0]

    def one(job):
        mname, mpath, a, b, seed, cand = job
        key = "%s__%s__%s__s%d" % (mname, a[0], b[0], seed)
        safe = re.sub(r"[^A-Za-z0-9_.@=,-]+", "_", key)[:150] + "-" + hashlib.sha1(key.encode()).hexdigest()[:6]
        replay = out / "replays" / (safe + ".replay")
        row = dict(map=mname, A=a[0], B=b[0], seed=seed, cand=cand, toolkit=tk, sandbox=args.sandbox)
        row.update(runner.play(mpath, a, b, seed, replay))
        side = "A" if a[0] == cand else "B"
        row["side"] = side
        row["opp"] = b[0] if side == "A" else a[0]
        w = row["winner"]
        row["res"] = "E" if w == "error" else "D" if w == "draw" else "W" if w == side else "L"
        keep = args.keep == "all" or (args.keep == "losses" and row["res"] in "LDE")
        if keep and replay.exists():
            row["replay"] = str(replay.relative_to(out))
        elif replay.exists():
            replay.unlink()
        with lock:
            with rp.open("a") as fh:
                fh.write(json.dumps(row) + "\n")
            n[0] += 1
            print("[%d/%d %4.0fs] %-15s s%d %-30s %-30s %s" % (n[0], len(jobs), time.time() - t0, mname, seed,
                                                              a[0][:30], b[0][:30], row["res"]), flush=True)

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        list(ex.map(one, jobs))
    shutil.rmtree(out / "work", ignore_errors=True)


def load_rows(dirs):
    rows = {}
    for d in dirs:
        p = Path(d) / "results.jsonl"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            r = json.loads(line)
            k = (r["map"], r["A"], r["B"], r["seed"])
            if k not in rows or rows[k]["winner"] == "error":
                rows[k] = r
    return [r for r in rows.values() if r["winner"] != "error"]


def score(res):
    return 1.0 if res == "W" else 0.5 if res == "D" else 0.0


def sign_p(better, worse):
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def cmd_report(args):
    rows = load_rows(args.dirs)
    by = collections.defaultdict(dict)
    for r in rows:
        by[r["cand"]][(r["map"], r["side"], r["seed"], r["opp"])] = r
    cands = sorted(by) if not args.cand else args.cand
    for c in cands:
        rs = list(by[c].values())
        s = sum(score(r["res"]) for r in rs)
        print("%-50s n=%3d score=%.3f  W%d L%d D%d" % (c, len(rs), s / max(1, len(rs)),
              sum(r["res"] == "W" for r in rs), sum(r["res"] == "L" for r in rs), sum(r["res"] == "D" for r in rs)))
    if args.control:
        ctl = by[args.control]
        for c in cands:
            if c == args.control:
                continue
            keys = [k for k in by[c] if k in ctl]
            if not keys:
                continue
            d = [score(by[c][k]["res"]) - score(ctl[k]["res"]) for k in keys]
            b = sum(x > 0 for x in d)
            w = sum(x < 0 for x in d)
            print("\n%s vs %s: n=%d  delta=%+.3f  better %d worse %d  sign p=%.3f" % (
                c, args.control, len(keys), sum(d) / len(d), b, w, sign_p(b, w)))
            pm = collections.defaultdict(list)
            po = collections.defaultdict(list)
            for k, x in zip(keys, d):
                pm[k[0]].append(x)
                po[k[3]].append(x)
            print("  per map: " + "  ".join("%s %+.2f" % (m, sum(v) / len(v)) for m, v in sorted(pm.items())))
            print("  per opp: " + "  ".join("%s %+.2f" % (m[:18], sum(v) / len(v)) for m, v in sorted(po.items())))
    if args.detail:
        for c in cands:
            print("\n" + c)
            tab = collections.defaultdict(lambda: [0, 0])
            for r in by[c].values():
                tab[(r["opp"], r["map"])][0] += score(r["res"])
                tab[(r["opp"], r["map"])][1] += 1
            opps = sorted({k[0] for k in tab})
            mapsn = sorted({k[1] for k in tab})
            print("%-22s" % "" + " ".join("%6s" % m[:6] for m in mapsn))
            for o in opps:
                print("%-22s" % o[:22] + " ".join("%6s" % ("%.1f/%d" % tuple(tab[(o, m)]) if (o, m) in tab else "")
                                                  for m in mapsn))


STAT_KEYS = ("units_r100", "units_r250", "longest_r400", "longest_r499", "total_r499", "wall_self_per_1k",
             "births", "nb_dead10", "sw_per_100", "child_first_pearl_med", "first_pearl", "cpu_p99", "cpu_max")


def cmd_stats(args):
    rows = load_rows(args.dirs)
    by = collections.defaultdict(list)
    for r in rows:
        if "teams" in r:
            by[r["cand"]].append(r)
    for c, rs in sorted(by.items()):
        print("\n%s (n=%d)" % (c, len(rs)))
        for cls in ("all", "compact", "open"):
            sub = [r for r in rs if cls == "all" or (cls == "compact") == (r["map"] in COMPACT)]
            if not sub:
                continue
            me = [r["teams"][r["side"]] for r in sub]
            op = [r["teams"]["B" if r["side"] == "A" else "A"] for r in sub]
            line = []
            for k in STAT_KEYS:
                v = [m.get(k) for m in me if m.get(k) is not None]
                o = [m.get(k) for m in op if m.get(k) is not None]
                if v:
                    line.append("%s %s|%s" % (k, _fmt(ystats.median(v)), _fmt(ystats.median(o))))
            nb = sum(m["nb_dead10"] for m in me)
            bi = sum(m["births"] for m in me)
            line.append("nb_dead10/100births %.1f" % (100.0 * nb / max(1, bi)))
            acts = collections.Counter()
            for m in me:
                acts.update(m.get("act", {}))
            fun = [sum(m.get(k, 0) for m in me) for k in ("diss_deaths", "corpse", "corpse_ally", "corpse_crown")]
            ca = sum(1 for m in me if m.get("crown_alive_end"))
            line.append("ACT %s" % dict(acts))
            line.append("funnel diss/corpse/ally/crown %s crown_alive %d/%d" % (fun, ca, len(me)))
            print("  [%s n=%d] " % (cls, len(sub)) + "; ".join(line))


def _fmt(x):
    return ("%.1f" % x) if isinstance(x, float) else str(x)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    r = sp.add_parser("run")
    r.add_argument("--cands", nargs="+", required=True)
    r.add_argument("--pool", nargs="+", required=True)
    r.add_argument("--maps", default="live10")
    r.add_argument("--seeds", default="1")
    r.add_argument("--jobs", type=int, default=2)
    r.add_argument("--out", required=True)
    r.add_argument("--sandbox", action="store_true")
    r.add_argument("--keep", default="none")
    r.add_argument("--timeout", type=int, default=900)
    rr = sp.add_parser("report")
    rr.add_argument("dirs", nargs="+")
    rr.add_argument("--cand", nargs="*")
    rr.add_argument("--control")
    rr.add_argument("--detail", action="store_true")
    st = sp.add_parser("stats")
    st.add_argument("dirs", nargs="+")
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()

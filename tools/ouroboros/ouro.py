#!/usr/bin/env python3
"""ouro: the ouroboros adapt -> test -> benchmark -> improve harness.

    python3 tools/ouroboros/ouro.py run  CANDIDATE [CANDIDATE...] --pool P [P...]
            [--maps quick|full|name,name] [--jobs N] [--sandbox] [--out DIR]
            [--keep all|losses|none] [--tag TEXT]
    python3 tools/ouroboros/ouro.py report DIR [DIR...]
    python3 tools/ouroboros/ouro.py autopsy DIR [--n 5] [--opp NAME] [--map NAME]
    python3 tools/ouroboros/ouro.py sweep BASE --param key=v1,v2,v3 --pool ... (same flags as run)

A CANDIDATE is a bot folder name under bots/ (or a path), optionally with
parameter overrides:  ouroboros-v01@w_danger=-900,hunter_trade=1
Overrides are written to params.py (PARAMS = {...}) in a generated copy under
build/ouro-variants/, so sweeps never touch a committed bot.

Every match stores one JSON line in DIR/results.jsonl with the result and
replay-derived stats (see replaystats.py).  `report` aggregates it.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
# where runs and generated variants go (override when the repo is not writable/deletable)
BUILD = Path(os.environ.get("OURO_BUILD", str(ROOT / "build")))

ANSI = re.compile(r"\x1b\[[0-9;]*m")
OUTCOME = re.compile(r"^(?:team ([AB]) wins|draw) after (\d+) rounds", re.MULTILINE)
CPU = re.compile(r"team ([AB]) points per turn: p50 ([\d.]+)M\s+p99 ([\d.]+)M.*?max ([\d.]+)M")

MAPSETS = {
    "quick": ["arena", "default_small", "default", "devil", "queen_of_spades", "trophy"],
    "full": None,  # every original map (maps/, bots/maps/)
    "wide": None,  # full + the transposed / flipped variants from mapgen.py
    "variants": None,  # only the variants
    "widefast": None,  # wide without the 64x64 maps (help, big_empty): 33 maps
}
EXTRA_MAP_DIRS = [ROOT / "maps", ROOT / "bots" / "maps"]
VARIANT_DIR = HERE / "maps"
HOLDOUT_DIR = HERE / "holdout"
# Colloseum duplicates Colosseum; small is degenerate (both sides die in round 1)
SKIP_MAPS = {"Colloseum", "small", "small_T", "small_FX"}


def all_maps(variants=False):
    found = {}
    for d in EXTRA_MAP_DIRS + ([VARIANT_DIR] if variants else []):
        if d.is_dir():
            for p in sorted(d.glob("*.map")):
                if p.stem not in found and p.stem not in SKIP_MAPS:
                    found[p.stem] = p
    return found


def resolve_maps(spec):
    maps = all_maps(variants=True)
    base = all_maps()
    if spec in ("ho", "hoc", "hoo"):
        # hold-out: _TFX / _FY variants of the maps/ set (no 64x64); never tune on these
        maps = {p.stem: p for p in sorted(HOLDOUT_DIR.glob("*.map")) if not p.stem.startswith("big_empty")}
        names = sorted(maps)
        if spec != "ho":
            def tiles(n):
                with open(maps[n]) as fh:
                    w, h = map(int, fh.readline().split()[1:3])
                return w * h
            names = [n for n in names if (tiles(n) <= 625) == (spec == "hoc")]
        return {n: maps[n] for n in names}
    if spec in MAPSETS and MAPSETS[spec] is not None:
        names = MAPSETS[spec]
    elif spec in (None, "full"):
        names = sorted(base)
    elif spec == "wide":
        names = sorted(maps)
    elif spec == "variants":
        names = sorted(set(maps) - set(base))
    elif spec in ("gv", "gvc", "gvo", "gvb"):
        # the cycle-0 gauntlet maps (maps/) + their _T/_FX variants, no 64x64
        # gv: all 30; gvc: compact (<=625 tiles); gvo: open; gvb: base 10 only
        keep = sorted(n for n in base if not n.startswith("big_empty"))
        names = []
        for n in keep:
            for v in ("", "_T", "_FX"):
                if n + v in maps and (spec != "gvb" or not v):
                    names.append(n + v)
        if spec in ("gvc", "gvo"):
            def tiles(n):
                with open(maps[n]) as fh:
                    w, h = map(int, fh.readline().split()[1:3])
                return w * h
            names = [n for n in names if (tiles(n) <= 625) == (spec == "gvc")]
    elif spec == "widefast":
        names = sorted(n for n in maps if not n.startswith(("help", "big_empty")))
    else:
        names = [n.strip() for n in spec.split(",") if n.strip()]
    missing = [n for n in names if n not in maps]
    if missing:
        sys.exit("unknown maps: %s (have %s)" % (missing, sorted(maps)))
    return {n: maps[n] for n in names}


def parse_value(text):
    try:
        return json.loads(text)
    except ValueError:
        return text


def resolve_bot(spec):
    """'name' or 'name@k=v,k=v' -> (label, folder Path)."""
    name, _, over = spec.partition("@")
    path = Path(name)
    if not path.is_dir():
        path = ROOT / "bots" / name
    if not (path / "bot.toml").exists():
        sys.exit("no bot at %s" % path)
    if not over:
        return path.name, path
    overrides = {}
    items, depth, cur = [], 0, ""
    for ch in over:  # split on commas outside brackets: k=[1,2],j=3
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            items.append(cur)
            cur = ""
        else:
            cur += ch
    items.append(cur)
    for item in items:
        k, _, v = item.partition("=")
        overrides[k.strip()] = parse_value(v.strip())
    base = {}
    if (path / "params.py").exists():
        scope = {}
        exec((path / "params.py").read_text(), scope)
        base = dict(scope.get("PARAMS", {}))
    base.update(overrides)
    digest = hashlib.sha1(json.dumps(overrides, sort_keys=True).encode()).hexdigest()[:8]
    label = "%s@%s" % (path.name, ",".join("%s=%s" % kv for kv in sorted(overrides.items())))
    target = BUILD / "ouro-variants" / ("%s__%s" % (path.name, digest))
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(path, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
        ".unswbc-build", "__pycache__", ".git", "build"))
    (target / "params.py").write_text("PARAMS = %r\n" % (dict(sorted(base.items())),))
    (target / "VARIANT").write_text(label + "\n")
    return label, target


class Runner:
    def __init__(self, workspace, sandbox, keep, timeout):
        self.workspace = Path(workspace)
        self.sandbox = sandbox
        self.keep = keep
        self.timeout = timeout
        self.lock = threading.Lock()

    def worker_copy(self, label, src):
        # truncated names must stay unique: long variant labels share prefixes
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", label)[:60] + "-" + \
            hashlib.sha1(label.encode()).hexdigest()[:8]
        target = self.workspace / str(threading.get_ident()) / safe
        if not target.exists():
            shutil.copytree(src, target, ignore=shutil.ignore_patterns(
                ".unswbc-build", "__pycache__", ".git", "build"))
        return target

    def play(self, mapname, mappath, a, b, replay_path):
        (la, pa), (lb, pb) = a, b
        ca = self.worker_copy(la, pa)
        cb = self.worker_copy(lb, pb)
        cmd = ["unswbc", "run", str(mappath), str(ca), str(cb), "-o", str(replay_path)]
        if self.sandbox:
            cmd.append("--sandbox")
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout,
                                  cwd=str(self.workspace))
            log = ANSI.sub("", proc.stdout + proc.stderr)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            log, rc = "timeout", -1
        found = list(OUTCOME.finditer(log))
        row = dict(map=mapname, A=la, B=lb, secs=round(time.time() - t0, 1))
        if rc != 0 or not found:
            row.update(winner="error", rounds=0, log_tail=log[-600:])
            return row
        m = found[-1]
        row.update(winner=m[1] or "draw", rounds=int(m[2]))
        cpu = {}
        for c in CPU.finditer(log):
            cpu[c[1]] = dict(p50=float(c[2]), p99=float(c[3]), max=float(c[4]))
        if cpu:
            row["cpu"] = cpu
        try:
            import replaystats
            st = replaystats.analyse(replay_path)
            row["end"] = st["end"]
            row["standing"] = st["standing"]
            row["teams"] = {t: {k: v for k, v in st["teams"][t].items() if k != "curve"}
                            for t in "AB"}
            row["curve"] = {t: st["teams"][t]["curve"][::2] for t in "AB"}
        except Exception as exc:  # stats are optional; results are not
            row["stats_error"] = repr(exc)
        return row


def cmd_run(args, candidates=None):
    maps = resolve_maps(args.maps)
    cands = candidates or [resolve_bot(c) for c in args.candidates]
    pool = [resolve_bot(p) for p in args.pool]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = Path(args.out) if args.out else BUILD / "ouro" / (stamp + ("-" + args.tag if args.tag else ""))
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "replays").mkdir(exist_ok=True)
    meta = dict(candidates=[c[0] for c in cands], pool=[p[0] for p in pool], maps=list(maps),
                sandbox=args.sandbox, started=stamp, tag=args.tag)
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    done = set()
    results_path = out / "results.jsonl"
    if results_path.exists():
        for line in results_path.read_text().splitlines():
            r = json.loads(line)
            if r["winner"] != "error":
                done.add((r["map"], r["A"], r["B"]))
    jobs = []
    seen_pairs = set()
    for cand in cands:
        for opp in pool:
            if opp[0] == cand[0]:
                continue
            for mname, mpath in maps.items():
                for a, b in ((cand, opp), (opp, cand)):
                    key = (mname, a[0], b[0])
                    if key not in done and key not in seen_pairs:
                        seen_pairs.add(key)
                        jobs.append((mname, mpath, a, b, cand[0]))
    print("%d matches -> %s" % (len(jobs), out), flush=True)
    runner = Runner(out / "work", args.sandbox, args.keep, args.timeout)
    lock = threading.Lock()
    t0 = time.time()
    tally = collections.Counter()

    big_gate = threading.Semaphore(max(1, args.jobs // 2))

    def is_big(mpath):
        with open(mpath) as fh:
            w, h = map(int, fh.readline().split()[1:3])
        return w * h > 2000

    def one(job):
        mname, mpath, a, b, cand = job
        if is_big(mpath):
            # 128 python processes per big-map match: cap concurrency (memory)
            with big_gate:
                return one_inner(job)
        return one_inner(job)

    def one_inner(job):
        mname, mpath, a, b, cand = job
        key = "%s__%s__vs__%s" % (mname, a[0], b[0])
        safe = re.sub(r"[^A-Za-z0-9_.@=,-]+", "_", key)[:160] + "-" + hashlib.sha1(key.encode()).hexdigest()[:8]
        rp = out / "replays" / (safe + ".replay")
        row = runner.play(mname, mpath, a, b, rp)
        row["cand"] = cand
        side = "A" if a[0] == cand else "B"
        row["side"] = side
        res = "D" if row["winner"] == "draw" else ("E" if row["winner"] == "error" else
                                                   ("W" if row["winner"] == side else "L"))
        row["res"] = res
        keep = args.keep == "all" or (args.keep == "losses" and res in "LDE")
        if not keep and rp.exists():
            try:
                rp.unlink()
            except OSError:
                pass
        else:
            row["replay"] = str(rp.relative_to(out))
        with lock:
            with results_path.open("a") as fh:
                fh.write(json.dumps(row) + "\n")
            tally[res] += 1
            n = sum(tally.values())
            print("[%d/%d %.0fs] %-16s %-28s %-28s -> %s (%s r%s)" % (
                n, len(jobs), time.time() - t0, mname, a[0][:28], b[0][:28], res,
                row["winner"], row["rounds"]), flush=True)
        return row

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        list(ex.map(one, jobs))
    shutil.rmtree(out / "work", ignore_errors=True)
    print()
    report([out])
    return out


def load_rows(dirs):
    """All result rows; a match retried after an error (e.g. an interrupted
    chunk) keeps only its latest successful row."""
    rows = {}
    for d in dirs:
        p = Path(d) / "results.jsonl"
        if p.exists():
            for line in p.read_text().splitlines():
                r = json.loads(line)
                r["_dir"] = str(d)
                key = (str(d), r["map"], r["A"], r["B"])
                old = rows.get(key)
                if old is None or old["winner"] == "error" or r["winner"] != "error":
                    rows[key] = r
    return list(rows.values())


def report(dirs):
    rows = load_rows(dirs)
    if not rows:
        print("no results")
        return
    by_cand = collections.defaultdict(list)
    for r in rows:
        by_cand[r["cand"]].append(r)
    for cand, rs in by_cand.items():
        opp_of = lambda r: r["B"] if r["side"] == "A" else r["A"]
        c = collections.Counter(r["res"] for r in rs)
        score = (c["W"] + 0.5 * c["D"]) / max(1, c["W"] + c["D"] + c["L"])
        print("=" * 78)
        print("%s   %dW %dD %dL %dE   score %.3f" % (cand, c["W"], c["D"], c["L"], c["E"], score))
        print("-" * 78)
        per_opp = collections.defaultdict(collections.Counter)
        per_map = collections.defaultdict(collections.Counter)
        for r in rs:
            per_opp[opp_of(r)][r["res"]] += 1
            per_map[r["map"]][r["res"]] += 1
        print("%-34s  W  D  L  E" % "opponent")
        for o, cc in sorted(per_opp.items(), key=lambda kv: -(kv[1]["W"] - kv[1]["L"])):
            print("%-34s %2d %2d %2d %2d" % (o[:34], cc["W"], cc["D"], cc["L"], cc["E"]))
        print("%-34s  W  D  L  E" % "map")
        for m, cc in sorted(per_map.items()):
            print("%-34s %2d %2d %2d %2d" % (m, cc["W"], cc["D"], cc["L"], cc["E"]))
        # why we lose
        losses = [r for r in rs if r["res"] == "L"]
        elim = sum(1 for r in losses if r.get("end") == "teamEliminated")
        print("losses: %d  (elimination %d, round-limit %d)  median loss round %s" % (
            len(losses), elim, len(losses) - elim,
            sorted(r["rounds"] for r in losses)[len(losses) // 2] if losses else "-"))
        deaths = collections.Counter()
        tdeaths = collections.Counter()
        h2h = collections.Counter()
        cpu99 = []
        cpumax = []
        tle = 0
        n = 0
        for r in rs:
            if "teams" not in r:
                continue
            n += 1
            me = r["teams"][r["side"]]
            them = r["teams"]["B" if r["side"] == "A" else "A"]
            deaths.update(me["deaths"])
            tdeaths.update(them["deaths"])
            for k in ("h2h_up", "h2h_even", "h2h_down", "h2h_struck", "h2h_hit"):
                h2h[k] += me[k]
            if "cpu" in r and r["side"] in r["cpu"]:
                cpu99.append(r["cpu"][r["side"]]["p99"] * 1e6)
                cpumax.append(r["cpu"][r["side"]]["max"] * 1e6)
            tle += me["tle"]
        if n:
            print("our deaths/match:   " + "  ".join("%s %.1f" % (k, v / n) for k, v in sorted(deaths.items())))
            print("their deaths/match: " + "  ".join("%s %.1f" % (k, v / n) for k, v in sorted(tdeaths.items())))
            print("our h2h trades: up %d even %d down %d | we struck %d, were hit %d" % (
                h2h["h2h_up"], h2h["h2h_even"], h2h["h2h_down"], h2h["h2h_struck"], h2h["h2h_hit"]))
            if any(cpumax):
                print("cpu: worst p99 %.1fM  worst max %.1fM  tle %d" % (
                    max(cpu99) / 1e6, max(cpumax) / 1e6, tle))
        bad = [r for r in rs if r["res"] in "LE"]
        if bad:
            print("non-wins:")
            for r in sorted(bad, key=lambda r: (opp_of(r), r["map"])):
                st = r.get("standing", {})
                me, op = r["side"], "B" if r["side"] == "A" else "A"
                print("  %-26s %-16s side %s %s r%-3s %s  us %s them %s" % (
                    opp_of(r)[:26], r["map"], r["side"], r["res"], r["rounds"],
                    (r.get("end") or "")[:9],
                    st.get(me), st.get(op)))
    print("=" * 78)


def standings(dirs):
    """Points table over every bot seen, crediting both sides of each match."""
    rows = [r for r in load_rows(dirs) if r["res"] != "E"]
    tab = collections.defaultdict(collections.Counter)
    h2h = collections.defaultdict(collections.Counter)
    for r in rows:
        for side, other in (("A", "B"), ("B", "A")):
            me, op = r[side], r[other]
            if r["winner"] == "draw":
                res = "D"
            else:
                res = "W" if r["winner"] == side else "L"
            tab[me][res] += 1
            h2h[me][op] += {"W": 1.0, "D": 0.5, "L": 0.0}[res]
            h2h[me]["n:" + op] += 1
    bots = sorted(tab, key=lambda b: -(tab[b]["W"] + 0.5 * tab[b]["D"]) / max(1, sum(tab[b].values())))
    short = [b[:10] for b in bots]
    print("%-32s %5s %4s %4s %4s  " % ("bot", "score", "W", "D", "L") + " ".join("%10s" % s for s in short))
    for b in bots:
        t = tab[b]
        n = max(1, sum(t.values()))
        cells = []
        for o in bots:
            m = h2h[b]["n:" + o]
            cells.append("%10s" % ("-" if not m else "%.0f%%" % (100 * h2h[b][o] / m)))
        print("%-32s %5.3f %4d %4d %4d  " % (b[:32], (t["W"] + 0.5 * t["D"]) / n, t["W"], t["D"], t["L"]) + " ".join(cells))


def compare(dirs, maps=None):
    """Side-by-side W-L of each run's candidate on the matchups all runs share."""
    runs = []
    names = []
    for d in dirs:
        rows = [r for r in load_rows([d]) if r["res"] != "E"]
        if maps:
            rows = [r for r in rows if r["map"] in maps]
        for cand in sorted(set(r["cand"] for r in rows)):
            names.append(cand)
            runs.append({(r["map"], r["A"] if r["side"] == "B" else r["B"], r["side"]): r
                         for r in rows if r["cand"] == cand})
    common = set(runs[0])
    for r in runs[1:]:
        common &= set(r)
    print("%d common matchups" % len(common))
    for key_name, keyf in (("map", lambda k: k[0]), ("opponent", lambda k: k[1])):
        groups = sorted(set(keyf(k) for k in common))
        if key_name == "map":
            for i, n in enumerate(names):
                print("  [%d] %s" % (i, n))
        print("%-34s " % key_name + " ".join("%14s" % ("[%d]" % i) for i in range(len(names))))
        for g in groups:
            cells = []
            for run in runs:
                w = sum(1 for k in common if keyf(k) == g and run[k]["res"] == "W")
                l = sum(1 for k in common if keyf(k) == g and run[k]["res"] == "L")
                cells.append("%14s" % ("%d-%d" % (w, l)))
            print("%-34s " % g[:34] + " ".join(cells))
    tot = []
    for run in runs:
        w = sum(1 for k in common if run[k]["res"] == "W")
        tot.append("%14s" % ("%d-%d" % (w, len(common) - w)))
    print("%-34s " % "TOTAL" + " ".join(tot))
    flips = [k for k in sorted(common) if len(set(run[k]["res"] for run in runs)) > 1]
    print("flipped matchups: %d" % len(flips))
    for k in flips:
        print("  %-16s %-30s side %s: %s" % (k[0], k[1][:30], k[2], " ".join(run[k]["res"] for run in runs)))


def cmd_autopsy(args):
    import replaystats
    rows = [r for r in load_rows(args.dirs) if r["res"] in "LD" and r.get("replay")]
    if args.opp:
        rows = [r for r in rows if args.opp in (r["A"] + r["B"])]
    if args.map:
        rows = [r for r in rows if r["map"] == args.map]
    for r in rows[: args.n]:
        st = replaystats.analyse(Path(r["_dir"]) / r["replay"])
        print(replaystats.describe(st, r["side"]))
        print()


def cmd_sweep(args):
    key, _, values = args.param.partition("=")
    cands = [resolve_bot("%s@%s=%s" % (args.base, key, v)) for v in values.split(",")]
    if args.include_base:
        cands.insert(0, resolve_bot(args.base))
    return cmd_run(args, candidates=cands)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--pool", nargs="+", required=True)
        p.add_argument("--maps", default="quick")
        p.add_argument("--jobs", "-j", type=int, default=max(1, (os.cpu_count() or 2)))
        p.add_argument("--sandbox", action="store_true")
        p.add_argument("--out")
        p.add_argument("--tag", default="")
        p.add_argument("--keep", default="losses", choices=("all", "losses", "none"))
        p.add_argument("--timeout", type=int, default=600)

    p = sub.add_parser("run")
    p.add_argument("candidates", nargs="+")
    common(p)
    p = sub.add_parser("sweep")
    p.add_argument("base")
    p.add_argument("--param", required=True)
    p.add_argument("--include-base", action="store_true")
    common(p)
    p = sub.add_parser("report")
    p.add_argument("dirs", nargs="+")
    p = sub.add_parser("standings")
    p.add_argument("dirs", nargs="+")
    p = sub.add_parser("compare")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--maps")
    p = sub.add_parser("autopsy")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--n", type=int, default=3)
    p.add_argument("--opp")
    p.add_argument("--map")
    a = ap.parse_args()
    if a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "sweep":
        cmd_sweep(a)
    elif a.cmd == "report":
        report(a.dirs)
    elif a.cmd == "standings":
        standings(a.dirs)
    elif a.cmd == "compare":
        compare(a.dirs, a.maps.split(",") if a.maps else None)
    elif a.cmd == "autopsy":
        cmd_autopsy(a)


if __name__ == "__main__":
    main()

"""Pace panel runner (lineage `pace`): seeded, paired, both sides, unswbc 1.2.2.

  panel.py run --arms A B --opps X Y --maps live10 --seeds 1 2 3 --out DIR [-j 2] [--keep none|losses|all]
  panel.py pair DIR --base A --cand B      paired delta, better/worse, sign-test p, per map class

A fixture is (map, side, seed, opponent). One row per game in DIR/results.jsonl
(resumable). Per-team stage statistics come from tools/pace/pstats.py (a copy of
tools/hub/vendor/public_replay_review.py that also counts ACT:<tag> log markers).
"""
from __future__ import annotations
import argparse, collections, json, math, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
UNSWBC = os.environ.get("UNSWBC", "unswbc")
LIVE10 = ["schooltime", "portals", "slithery_fight", "queen_of_spades", "default", "trophy",
          "dilemma", "autarky", "devil", "trauma"]
TILES = {"schooltime": 2400, "portals": 512, "slithery_fight": 1701, "queen_of_spades": 875, "default": 1024,
         "trophy": 625, "dilemma": 512, "autarky": 972, "devil": 512, "trauma": 1152}
OUTCOME = re.compile(r"(?:team ([AB]) wins|draw)[^\n]*?after (\d+) rounds")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
STAGES = (25, 50, 100, 150, 200, 250, 300, 400, 499)


def mclass(m):
    return "compact" if TILES.get(m, 9999) <= 625 else "open"


def team_stats(a, t):
    c = a["curve"]
    last = c[-1][t]
    at = {}
    for r in STAGES:
        row = c[r][t] if r < len(c) else (last if last["units"] else dict(units=0, total=0, longest=0))
        at[r] = (row["units"], row["total"], row["longest"])
    st = a["stats"][t]
    deaths = {k[6:]: v for k, v in st.items() if k.startswith("death_")}
    born = sum(1 for s in a["splits"] if s["team"] == t)
    return dict(at=at, turns=st.get("turns", 0), deaths=deaths, splits=st.get("splits", 0), births=born,
                newborn10=st.get("newborn_deaths_10", 0), portal_steps=st.get("portal_steps", 0),
                sonar=st.get("sonar", 0), pearls=st.get("pearls", 0), sprints=st.get("sprints", 0),
                friendly_h2h=st.get("friendly_h2h", 0), body_ally=st.get("body_ally", 0),
                cpu_max=st.get("cpu_max", 0), tle=st.get("tle", 0), acts=dict(a["acts"][t]),
                final=a["final"][t])


def play(mapname, seed, A, B, replay, work, sandbox=False, timeout=1500):
    cmd = [UNSWBC, "run", str(REPO / "maps" / (mapname + ".map")), str(A), str(B), "--seed", str(seed), "-o", str(replay)]
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
        return dict(error=log[-400:]), time.time() - t0
    return dict(winner=m[-1][1] or "draw", rounds=int(m[-1][2]),
                errs=len(re.findall(r"MC_ERROR|exceeded CPU", log))), time.time() - t0


def cmd_run(a):
    import pstats
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); (out / "replays").mkdir(exist_ok=True)
    res = out / "results.jsonl"
    done = set()
    if res.exists():
        for line in res.read_text().splitlines():
            r = json.loads(line)
            if "error" not in r:
                done.add((r["map"], r["seed"], r["arm"], r["opp"], r["side"]))
    ver = subprocess.run([UNSWBC, "--version"], capture_output=True, text=True).stdout.strip()
    (out / "meta.json").write_text(json.dumps(dict(arms=a.arms, opps=a.opps, maps=a.maps, seeds=a.seeds, toolkit=ver), indent=1))
    maps = LIVE10 if a.maps == ["live10"] else a.maps
    jobs = [(m, s, arm, o, side) for s in a.seeds for o in a.opps for m in maps for arm in a.arms for side in "AB"
            if (m, s, arm, o, side) not in done]
    print("%d games -> %s (%s)" % (len(jobs), out, ver), flush=True)
    lock = threading.Lock(); t0 = time.time(); n = [0]; work = out / "work"; work.mkdir(exist_ok=True)

    def one(job):
        m, s, arm, o, side = job
        ab = [REPO / "bots" / arm, REPO / "bots" / o]
        A, B = ab if side == "A" else ab[::-1]
        rp = out / "replays" / ("%s_s%d_%s_%s_%s.replay" % (m, s, arm, o, side))
        r, secs = play(m, s, A, B, rp, work)
        row = dict(map=m, cls=mclass(m), seed=s, arm=arm, opp=o, side=side, secs=round(secs, 1), toolkit=ver)
        row.update(r)
        if "error" not in r:
            w = r["winner"]
            row["res"] = "D" if w == "draw" else ("W" if w == side else "L")
            try:
                an = pstats.analyse(rp)
                row["reason"] = an["reason"]
                row["me"] = team_stats(an, side)
                row["op"] = team_stats(an, "B" if side == "A" else "A")
            except Exception as exc:
                row["stats_error"] = repr(exc)
            if not (a.keep == "all" or (a.keep == "losses" and row["res"] != "W")):
                rp.unlink(missing_ok=True)
        with lock:
            with res.open("a") as fh:
                fh.write(json.dumps(row) + "\n")
            n[0] += 1
            print("[%d/%d %.0fs] %-15s s%d %-22s vs %-30s %s -> %s r%s" % (
                n[0], len(jobs), time.time() - t0, m, s, arm[:22], o[:30], side, row.get("res", "E"), row.get("rounds")), flush=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        list(ex.map(one, jobs))


def load(dirs):
    rows = {}
    for d in dirs:
        p = Path(d) / "results.jsonl"
        if p.exists():
            for line in p.read_text().splitlines():
                r = json.loads(line)
                if "error" not in r and "me" in r:
                    rows[(r["map"], r["seed"], r["arm"], r["opp"], r["side"])] = r
    return list(rows.values())


def score(r):
    return {"W": 1.0, "D": 0.5}.get(r["res"], 0.0)


def sign_p(b, w):
    n = b + w
    if not n:
        return 1.0
    k = min(b, w)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2.0 ** n)


def cmd_pair(a):
    rows = load(a.dirs)
    idx = {(r["map"], r["seed"], r["opp"], r["side"], r["arm"]): r for r in rows}
    for cand in a.cand:
        pairs = [(idx[k[:4] + (a.base,)], r) for k, r in idx.items() if k[4] == cand and k[:4] + (a.base,) in idx
                 and r["opp"] != cand]
        def rep(ps, label):
            if not ps:
                return
            d = [score(c) - score(b) for b, c in ps]
            bt, wr = sum(x > 0 for x in d), sum(x < 0 for x in d)
            print("  %-22s n=%3d base %.3f cand %.3f delta %+.3f  better %d worse %d  p=%.3f" % (
                label, len(ps), sum(score(b) for b, _ in ps) / len(ps), sum(score(c) for _, c in ps) / len(ps),
                sum(d) / len(d), bt, wr, sign_p(bt, wr)))
        print("%s vs %s" % (cand, a.base))
        rep(pairs, "all")
        for cl in ("compact", "open"):
            rep([p for p in pairs if p[0]["cls"] == cl], cl)
        for o in sorted({p[0]["opp"] for p in pairs}):
            rep([p for p in pairs if p[0]["opp"] == o], "opp " + o[:18])
        if a.maps:
            for m in LIVE10:
                rep([p for p in pairs if p[0]["map"] == m], "map " + m)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run"); r.add_argument("--arms", nargs="+", required=True); r.add_argument("--opps", nargs="+", required=True)
    r.add_argument("--maps", nargs="+", default=["live10"]); r.add_argument("--seeds", nargs="+", type=int, default=[1])
    r.add_argument("--out", required=True); r.add_argument("-j", "--jobs", type=int, default=2)
    r.add_argument("--keep", default="none")
    p = sp.add_parser("pair"); p.add_argument("dirs", nargs="+"); p.add_argument("--base", required=True)
    p.add_argument("--cand", nargs="+", required=True); p.add_argument("--maps", action="store_true")
    a = ap.parse_args()
    {"run": cmd_run, "pair": cmd_pair}[a.cmd](a)

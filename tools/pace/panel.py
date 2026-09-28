#!/usr/bin/env python3
"""P1 pace panel: seeded paired fixtures, arms vs opponents on the ten live maps.

Arms (same seeded fixtures, paired by map/side/seed/opponent):
  host     = bots/chaewon-y04-probe (the control)
  pace     = bots/pace-v01 (controller on)
  nolimit  = bots/pace-v01 + override pace_nolimit=1 (survival constraints off)

Every game runs under unswbc 1.2.2 with --seed, so exact pairs are comparable
across arms.  Stats come from the replay (vendored decoder, gzip-tolerant).
Results: one JSON line per game in OUT/results.jsonl (resumable).
"""
import argparse
import gzip
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools/hub/vendor"))
from public_replay_review import analyse  # noqa: E402

TEN = ["schooltime", "portals", "slithery_fight", "queen_of_spades", "default",
       "trophy", "dilemma", "autarky", "devil", "trauma"]
OPPONENTS = ["fenrir-v18-arrival-ready-beds", "sinbad-v07-divecap",
             "gavroche-v32-supported-divecap", "ouroboros-m01-vibing-mimic",
             "yuna-v05-core", "chaewon-y04-probe"]
ARMS = [("host", "chaewon-y04-probe", None),
        ("pace", "pace-v01", None),
        ("nolimit", "pace-v01", {"pace_nolimit": 1})]
UNSWBC = Path.home() / ".venvs/bc122/bin/unswbc"
OUTCOME = re.compile(r"^(?:team ([AB]) wins|draw) after (\d+) rounds", re.MULTILINE)
STAGES = [25, 50, 100, 250, 400]
MAP_TILES = {}  # name -> tiles, for the compact/open split in analysis


def bot_dir(name):
    p = ROOT / "bots" / name
    if not (p / "bot.toml").exists():
        sys.exit("no bot at %s" % p)
    return p


def make_arm(label, name, overrides, workspace):
    """Copy the bot; merge arm overrides into override.py (never touch the original)."""
    src = bot_dir(name)
    tgt = workspace / "arms" / label
    if tgt.exists():
        shutil.rmtree(tgt)
    shutil.copytree(src, tgt, ignore=shutil.ignore_patterns(
        ".unswbc-build", "__pycache__", ".git", "build"))
    if overrides:
        with open(tgt / "override.py", "a") as fh:
            fh.write("OVERRIDE.update(%r)  # pace arm\n" % (dict(overrides),))
    return tgt


def decode(replay_path):
    raw = Path(replay_path).read_bytes()
    if raw[:2] == b"\x1f\x8b":
        import tempfile
        tf = tempfile.NamedTemporaryFile(suffix=".replay", delete=False)
        tf.write(gzip.decompress(raw))
        tf.close()
        return analyse(tf.name)
    return analyse(str(replay_path))


def stage_stats(a, side):
    by_round = {c["round"]: c for c in a["curve"]}
    out = {}
    for st in STAGES:
        c = by_round.get(st)
        if c is None:
            cands = [r for r in a["curve"] if r["round"] <= st]
            c = cands[-1] if cands else None
        if c is not None:
            out["u%d" % st] = c[side]["units"]
            out["t%d" % st] = c[side]["total"]
            out["l%d" % st] = c[side]["longest"]
    out["final"] = a["final"][side]
    st = a["stats"][side]
    turns = max(1, st.get("turns", 1))
    out["turns"] = turns
    for k in ("wall", "self", "body", "h2h", "invalid"):
        out["d_" + k] = 1000.0 * st.get("death_" + k, 0) / turns
    out["newborn10"] = st.get("newborn_deaths_10", 0)
    out["splits"] = st.get("splits", 0)
    out["portal_steps"] = st.get("portal_steps", 0)
    out["sonar"] = st.get("sonar", 0)
    out["sprints"] = st.get("sprints", 0)
    out["pearls"] = st.get("pearls", 0)
    out["tle"] = st.get("tle", 0)
    acts = {}
    for txt, n in a.get("log_samples", {}).items():
        t = txt.strip()
        if t.startswith("ACT:"):
            acts[t] = acts.get(t, 0) + n
    out["acts"] = acts
    return out


def play(game, workspace, keep):
    mapname, seed, arm, opp, arm_side = game
    mappath = ROOT / "maps" / ("%s.map" % mapname)
    label = "%s__%s__%s__s%d__as_%s" % (mapname, arm, opp, seed, arm_side)
    # each worker thread owns its private bot copies (the toolkit writes
    # .unswbc-build into the bot folder it runs)
    wa = workspace / "work" / str(threading.get_ident()) / arm
    wo = workspace / "work" / str(threading.get_ident()) / opp
    for w, src in ((wa, workspace / "arms" / arm), (wo, bot_dir(opp))):
        if w.exists():
            shutil.rmtree(w)
        shutil.copytree(src, w, ignore=shutil.ignore_patterns(
            ".unswbc-build", "__pycache__", ".git", "build"))
    replay = workspace / "replays" / (label + ".replay")
    a, b = (wa, wo) if arm_side == "A" else (wo, wa)
    cmd = [str(UNSWBC), "run", str(mappath), str(a), str(b),
           "--seed", str(seed), "-o", str(replay)]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        log = proc.stdout + proc.stderr
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        log, rc = "timeout", -1
    row = dict(map=mapname, arm=arm, opp=opp, side=arm_side, seed=seed,
               secs=round(time.time() - t0, 1))
    found = list(OUTCOME.finditer(log))
    if rc != 0 or not found:
        row.update(winner="error", rounds=0, log_tail=log[-400:])
        return row
    m = found[-1]
    row["winner"] = m[1] or "draw"
    row["rounds"] = int(m[2])
    try:
        a2 = decode(replay)
        row["reason"] = a2["reason"]
        mine = arm_side
        theirs = "B" if mine == "A" else "A"
        row["mine"] = stage_stats(a2, mine)
        row["theirs"] = stage_stats(a2, theirs)
    except Exception as exc:
        row["stats_error"] = repr(exc)
    if not keep and replay.exists():
        try:
            replay.unlink()
        except OSError:
            pass
    else:
        row["replay"] = str(replay.relative_to(workspace))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--arms", nargs="+", default=[a[0] for a in ARMS])
    ap.add_argument("--maps", nargs="+", default=TEN)
    ap.add_argument("--opps", nargs="+", default=OPPONENTS)
    ap.add_argument("--keep", action="store_true", help="keep replays")
    args = ap.parse_args()

    workspace = Path(args.out).resolve()
    (workspace / "replays").mkdir(parents=True, exist_ok=True)
    for label, name, overrides in ARMS:
        if label in args.arms:
            make_arm(label, name, overrides, workspace)
    results = workspace / "results.jsonl"
    done = set()
    if results.exists():
        for line in results.read_text().splitlines():
            r = json.loads(line)
            if r["winner"] != "error":
                done.add((r["map"], r["arm"], r["opp"], r["side"], r["seed"]))
    games = []
    for label, _n, _o in ARMS:
        if label not in args.arms:
            continue
        for opp in args.opps:
            for mapname in args.maps:
                for side in "AB":
                    for seed in args.seeds:
                        if (mapname, label, opp, side, seed) not in done:
                            games.append((mapname, seed, label, opp, side))
    meta = dict(arms=args.arms, opponents=args.opps, maps=args.maps, seeds=args.seeds,
                toolkit="unswbc 1.2.2 (scratch venv)", started=time.strftime("%Y%m%d-%H%M%S"))
    (workspace / "meta.json").write_text(json.dumps(meta, indent=1))
    print("%d games -> %s" % (len(games), workspace), flush=True)
    tally = {}
    t0 = time.time()
    lock = threading.Lock()

    def one(game):
        row = play(game, workspace, args.keep)
        with lock:
            with results.open("a") as fh:
                fh.write(json.dumps(row) + "\n")
            key = (row["arm"], row["winner"] == row["side"] and "W"
                   or row["winner"] == "error" and "E"
                   or row["winner"] == "draw" and "D" or "L")
            tally[key] = tally.get(key, 0) + 1
            n = sum(tally.values())
            if n % 20 == 0 or n == len(games):
                print("[%d/%d %.0fs] %s" % (n, len(games), time.time() - t0, tally), flush=True)

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for _ in ex.map(one, games):
            pass
    print("done", tally)


if __name__ == "__main__":
    main()

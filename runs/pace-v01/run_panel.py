#!/usr/bin/env python3
"""Seeded local panel for pace-v01; replay payloads stay in /tmp."""
import argparse, concurrent.futures, json, os, re, shutil, subprocess, tempfile, threading, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "hub" / "vendor"))
import public_replay_review
UNSWBC = os.environ.get("UNSWBC", "/tmp/bc122/bin/unswbc")
MAPS = ["schooltime", "portals", "slithery_fight", "queen_of_spades", "default", "trophy", "dilemma", "autarky", "devil", "trauma"]
OPPONENTS = ["fenrir-v18-arrival-ready-beds", "sinbad-v07-divecap", "gavroche-v32-supported-divecap", "ouroboros-m01-vibing-mimic", "yuna-v05-core", "chaewon-y04-probe"]
ARMS = {"host": Path("/tmp/pace-host"), "pace": Path("/tmp/pace-bot"), "pace-nolimit": Path("/tmp/pace-nolimit")}
LOCK = threading.Lock()
PATH_LOCK = threading.Lock()
THREAD_BOTS = {}

def worker_bots():
    ident=threading.get_ident()
    with PATH_LOCK:
        if ident not in THREAD_BOTS:
            root=Path(tempfile.gettempdir())/f"pace-panel-worker-{ident}"
            shutil.rmtree(root,ignore_errors=True)
            root.mkdir(parents=True)
            arms={}
            for name,src in ARMS.items():
                dst=root/name; shutil.copytree(src,dst,ignore=shutil.ignore_patterns(".unswbc-build","__pycache__")); arms[name]=dst
            opponents={}
            for name in OPPONENTS:
                dst=root/name; shutil.copytree(ROOT/"bots"/name,dst,ignore=shutil.ignore_patterns(".unswbc-build","__pycache__")); opponents[name]=dst
            THREAD_BOTS[ident]=(arms,opponents)
        return THREAD_BOTS[ident]

def run_one(arm, opponent, map_name, seed, side, out_path):
    arms,opponents=worker_bots()
    candidate, enemy = arms[arm], opponents[opponent]
    bots = [candidate, enemy] if side == "A" else [enemy, candidate]
    with tempfile.NamedTemporaryFile(prefix="pace-", suffix=".replay", delete=False) as f:
        replay_path = Path(f.name)
    replay_path.unlink(missing_ok=True)
    try:
        cmd = [UNSWBC, "run", "--seed", str(seed), "--no-draw", "--no-indicator", "-o", str(replay_path), str(ROOT / "maps" / (map_name + ".map")), str(bots[0]), str(bots[1])]
        env=os.environ.copy(); env.setdefault("PYTHONPYCACHEPREFIX", "/tmp/pace-engine-pycache")
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600, env=env)
        match = re.search(r"team ([AB]) wins after (\d+) rounds|draw after (\d+) rounds", proc.stdout)
        if proc.returncode or not match:
            row = {"arm": arm, "opponent": opponent, "map": map_name, "seed": seed, "side": side, "winner": "error", "returncode": proc.returncode, "output_tail": proc.stdout[-2000:]}
        else:
            winner = "draw" if match.group(1) is None else match.group(1)
            stats = public_replay_review.analyse(str(replay_path))
            checkpoints = {}
            for stage in (25, 50, 100, 250, 400):
                snap = next((x for x in stats["curve"] if x["round"] == stage), None)
                if snap: checkpoints[str(stage)] = snap[side]
            row = {"arm": arm, "opponent": opponent, "map": map_name, "seed": seed, "side": side, "winner": winner, "rounds": int(match.group(2) or match.group(3)), "score": 0.5 if winner == "draw" else float(winner == side), "checkpoints": checkpoints, "stats": stats["stats"][side], "activation": {k:v for k,v in stats["log_samples"].items() if "ACT:pace" in k}}
    except Exception as exc:
        row = {"arm": arm, "opponent": opponent, "map": map_name, "seed": seed, "side": side, "winner": "error", "error": repr(exc)}
    finally:
        replay_path.unlink(missing_ok=True)
    with LOCK:
        with out_path.open("a") as out: out.write(json.dumps(row, separators=(",", ":")) + "\n")
        print(f"{arm} seed={seed} {map_name} side={side} vs {opponent}: {row['winner']}", flush=True)
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[1])
    ap.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--maps", nargs="+", default=MAPS)
    ap.add_argument("--opponents", nargs="+", default=OPPONENTS)
    ap.add_argument("--out", default="runs/pace-v01/results.jsonl")
    args = ap.parse_args()
    out = (ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {"toolkit": "unswbc 1.2.2", "seeds": args.seeds, "maps": args.maps,
            "opponents": args.opponents, "arms": args.arms, "jobs": min(args.jobs, 4)}
    (out.parent / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    jobs = [(a,o,m,s,side) for a in args.arms for o in args.opponents for m in args.maps for s in args.seeds for side in ("A","B")]
    print(f"{len(jobs)} seeded games, unswbc 1.2.2, {args.jobs} concurrent", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(args.jobs,4)) as pool:
        futures = [pool.submit(run_one, *job, out) for job in jobs]
        for future in concurrent.futures.as_completed(futures): future.result()

if __name__ == "__main__": main()

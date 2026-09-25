#!/usr/bin/env python3
"""equiv: action-stream equivalence between two bot folders.

    python3 tools/ouroboros/equiv.py BOT_REF BOT_NEW [--cases N] [--maps a,b] [--opp X,Y] [-j 2]

The engine is deterministic and replays are byte-identical for identical
games, so two bots are action-stream equivalent on a case iff the replays of
(map, side, opponent) have the same hash.  Default: 16 cases over compact and
open maps, both sides, against a C++ swarm and a python bot.  Any mismatch is
printed with the first differing round (from the replay stats).

A refactor ships only with 16/16 equal (HANDOFF §7).
"""
import argparse
import hashlib
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

DEFAULT_MAPS = ["arena", "devil", "trophy", "Colosseum", "default", "stronghold", "trauma", "queen_of_spades"]
DEFAULT_OPP = ["fry-v14-stateful-size-aware-3", "kraken-v04-eval"]


def bot_path(name):
    p = Path(name)
    return p if p.is_dir() else ROOT / "bots" / name


def map_path(name):
    for d in (ROOT / "maps", HERE / "maps"):
        p = d / (name + ".map")
        if p.exists():
            return p
    sys.exit("no map " + name)


def stream_digest(path):
    """Hash of every replay event except per-turn instruction counts (those
    differ between equivalent programs).  Returns (digest, per-round digests)."""
    sys.path.insert(0, str(HERE))
    import replaystats
    rep = replaystats.load(path)
    total = hashlib.md5()
    rounds = []
    cur = hashlib.md5()
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rounds.append(cur.hexdigest())
            cur = hashlib.md5()
        if w == "dragonAction":
            a = ev.dragonAction
            key = "A%d %s %s" % (a.id, a.action if a.tle is False else "", a.tle)
        else:
            key = str(ev)
        total.update(key.encode())
        cur.update(key.encode())
    rounds.append(cur.hexdigest())
    return total.hexdigest(), rounds


def play(mp, a, b, work):
    out = Path(tempfile.mkstemp(suffix=".replay", dir=work)[1])
    r = subprocess.run(["unswbc", "run", str(mp), str(a), str(b), "-o", str(out)],
                       capture_output=True, text=True, timeout=1800, cwd=work)
    tail = (r.stdout + r.stderr).strip().splitlines()[-2:] if r.returncode == 0 else ["error"]
    if out.exists() and out.stat().st_size:
        h, rounds = stream_digest(out)
    else:
        h, rounds = "none", []
    return h, " | ".join(tail)[:120], rounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("new")
    ap.add_argument("--maps", default=",".join(DEFAULT_MAPS))
    ap.add_argument("--opp", default=",".join(DEFAULT_OPP))
    ap.add_argument("--cases", type=int, default=16)
    ap.add_argument("-j", "--jobs", type=int, default=2)
    args = ap.parse_args()
    ref, new = bot_path(args.ref), bot_path(args.new)
    maps, opps = args.maps.split(","), args.opp.split(",")
    # each map both sides, opponents alternating across maps
    cases = [(m, opps[i % len(opps)], side) for i, m in enumerate(maps) for side in "AB"]
    cases = cases[: args.cases]
    work = tempfile.mkdtemp(prefix="equiv-")
    # replays carry the bot folder names: run both under the same name
    import shutil
    ign = shutil.ignore_patterns(".unswbc-build", "__pycache__", "build")
    ref = shutil.copytree(ref, Path(work) / "ref" / "cand", ignore=ign)
    new = shutil.copytree(new, Path(work) / "new" / "cand", ignore=ign)

    def one(case):
        m, opp, side = case
        mp, o = map_path(m), bot_path(opp)
        res = []
        for bot in (ref, new):
            a, b = (bot, o) if side == "A" else (o, bot)
            res.append(play(mp, a, b, work))
        return case, res

    same = 0
    with ThreadPoolExecutor(args.jobs) as ex:
        for (m, opp, side), ((h1, t1, r1), (h2, t2, r2)) in ex.map(one, cases):
            ok = h1 == h2 and h1 != "none"
            if not ok:
                first = next((i for i, (x, y) in enumerate(zip(r1, r2)) if x != y), min(len(r1), len(r2)))
                t2 = t2 + "  [first differing round %d]" % (first - 1)
            same += ok
            print("%-4s %-16s %-30s %s  %s" % ("OK" if ok else "DIFF", m, opp[:30], side,
                                               t1 if ok else "\n     ref: %s\n     new: %s" % (t1, t2)),
                  flush=True)
    print("%d/%d equivalent" % (same, len(cases)))
    sys.exit(0 if same == len(cases) else 1)


if __name__ == "__main__":
    main()

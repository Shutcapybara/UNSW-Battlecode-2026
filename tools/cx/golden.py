#!/usr/bin/env python3
"""Golden-decision harness: record one team's full stdin/stdout transcript in a
local game, then replay those inputs into any bot, dragon by dragon, and diff
the replies turn by turn.

  record:  python3 tools/cx/golden.py record MAP BOT OPP --side A --seed 1 [--sandbox]
           -> build/cx/golden/<map>-<side>-<seed>/<bot>.jsonl[.gz]
  replay:  python3 tools/cx/golden.py replay build/cx/golden/<map>-<side>-<seed>/<bot>.jsonl BOT2
           [--all] [--ignore-sonar | --free-sonar] [--keep-debug] [--dragons 0,2]

Recording runs the game through unswbc 1.2.2's own engine and bot pools
(tools/cx/arena.py), so the recorded bot is launched exactly as `unswbc run`
launches it and is not modified or copied. Replay starts one fresh process
per recorded dragon (C/C++ bots are compiled by unswbc from bot.toml; Python
bots run `python3 main.py` with PYTHONHASHSEED=0), writes the recorded init
and turn blocks, and compares canonical replies: LOG/INDICATOR/DOT/LINE lines
dropped unless --keep-debug, whitespace collapsed, and SONAR payloads replaced
by * (--free-sonar) or SONAR lines dropped (--ignore-sonar). Exit status 1 on
the first divergence (or after all of them with --all), 0 if identical.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

DEBUG = ("LOG", "INDICATOR", "DOT", "LINE")


# ------------------------------------------------------------------ record
def record(args) -> int:
    from arena import run_game
    a, b = (args.bot, args.opp) if args.side == "A" else (args.opp, args.bot)
    r = run_game(args.map, a, b, args.seed, args.sandbox, record=args.side)
    mapname = pathlib.Path(args.map).stem
    out = pathlib.Path(args.out or REPO / "build" / "cx" / "golden" / f"{mapname}-{args.side}-{args.seed}"
                       / f"{pathlib.Path(args.bot).name}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    tr = r["transcripts"]
    with out.open("w") as fh:
        fh.write(json.dumps({"meta": {"map": mapname, "side": args.side, "seed": args.seed,
                                      "bot": args.bot, "opp": args.opp, "sandbox": args.sandbox,
                                      "winner": r["winner"], "rounds": r["rounds"],
                                      "dragons": len(tr)}}) + "\n")
        for did in sorted(tr, key=int):
            fh.write(json.dumps({"dragon": int(did), "init": tr[did]["init"]}) + "\n")
            for k, t in enumerate(tr[did]["turns"]):
                fh.write(json.dumps({"dragon": int(did), "turn": k, "round": t["round"],
                                     "input": t["input"], "output": t["output"]}) + "\n")
    if args.gzip:
        gz = out.with_name(out.name + ".gz")
        gz.write_bytes(gzip.compress(out.read_bytes(), 9))
        out.unlink()
        out = gz
    turns = sum(len(v["turns"]) for v in tr.values())
    print(f"recorded {len(tr)} dragons, {turns} turns -> {out}")
    return 0


# ------------------------------------------------------------------ replay
def load(path: str) -> tuple[dict, dict]:
    meta, dragons = {}, {}
    text = (gzip.decompress(pathlib.Path(path).read_bytes()).decode() if path.endswith(".gz")
            else pathlib.Path(path).read_text())
    for line in text.splitlines():
        d = json.loads(line)
        if "meta" in d:
            meta = d["meta"]
        elif "init" in d:
            dragons[d["dragon"]] = {"init": d["init"], "turns": []}
        else:
            dragons[d["dragon"]]["turns"].append(d)
    return meta, dragons


def canon(reply: str, keep_debug: bool, sonar: str) -> list[str]:
    out = []
    for line in reply.splitlines():
        f = line.split()
        if not f or f[0] == "ENDTURN":
            continue
        if not keep_debug and f[0] in DEBUG:
            continue
        if f[0] == "SONAR":
            if sonar == "ignore":
                continue
            if sonar == "free":
                f = f[:-1] + ["*"]
        out.append(" ".join(f))
    return out


def launcher(bot: str) -> tuple[list[str], str]:
    p = pathlib.Path(bot)
    if p.is_file() and os.access(p, os.X_OK):
        return [str(p.resolve())], str(p.parent)
    if (p / "main.py").is_file():
        return [sys.executable if "python" in pathlib.Path(sys.executable).name else "python3",
                "main.py"], str(p)
    from unswbc.project import Project
    built = Project.from_dir(str(p)).compile()
    from unswbc.run import _inspect
    argv, cwd, _kind = _inspect(built)
    return argv, str(cwd)


class Proc:
    def __init__(self, argv, cwd):
        env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1", TERM="dumb")
        self.p = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, env=env, bufsize=0)

    def ask(self, data: str) -> str | None:
        if not data.endswith("\n"):
            data += "\n"
        try:
            self.p.stdin.write(data.encode())
            self.p.stdin.flush()
        except (BrokenPipeError, OSError):
            return None
        lines = []
        while True:
            line = self.p.stdout.readline()
            if not line:
                return None if not lines else "\n".join(lines)
            s = line.decode(errors="replace").rstrip("\r\n")
            if s == "READY":
                continue
            if s == "ENDTURN":
                return "\n".join(lines)
            lines.append(s)

    def close(self):
        try:
            self.p.kill()
            self.p.wait(1)
        except Exception:
            pass


def replay_one(transcript: str, argv, cwd, args) -> tuple[int, int, str | None]:
    """replay one transcript file; returns (turns, divergences, first divergence)."""
    meta, dragons = load(transcript)
    sonar = "ignore" if args.ignore_sonar else "free" if args.free_sonar else "exact"
    want = set(int(x) for x in args.dragons.split(",")) if args.dragons else None
    n_turns = n_div = 0
    first = None
    for did in sorted(dragons):
        if want is not None and did not in want:
            continue
        d = dragons[did]
        proc = Proc(argv, cwd)
        try:
            for k, t in enumerate(d["turns"]):
                block = (d["init"] if k == 0 else "") + t["input"]
                got = proc.ask(block)
                n_turns += 1
                exp_c = canon(t["output"], args.keep_debug, sonar)
                got_c = canon(got, args.keep_debug, sonar) if got is not None else ["<no reply>"]
                if exp_c != got_c:
                    n_div += 1
                    msg = (f"DIVERGE dragon {did} turn {k} round {t['round']}: "
                           f"recorded {' | '.join(exp_c) or '<empty>'}  vs  replayed {' | '.join(got_c) or '<empty>'}")
                    print(msg)
                    if first is None:
                        first = msg
                    if not args.all:
                        proc.close()
                        return n_turns, n_div, first
                    if got is None:
                        break
        finally:
            proc.close()
    return n_turns, n_div, first


def replay(args) -> int:
    argv, cwd = launcher(args.bot)
    n_turns, n_div, _ = replay_one(args.transcript, argv, cwd, args)
    meta, dragons = load(args.transcript)
    print(f"replayed {n_turns} turns of {len(dragons)} dragons "
          f"({meta.get('map')}-{meta.get('side')}-{meta.get('seed')}): {n_div} divergent")
    return 1 if n_div else 0


def suite(args) -> int:
    """Replay a bot against every recorded transcript in a directory (the
    Ares V04 parity run as one command: a C++ bot against Python-recorded
    transcripts). Aggregates turns and divergences; exit 1 if any diverged."""
    root = pathlib.Path(args.transcripts)
    files = sorted(p for p in root.rglob("*.jsonl*") if p.name != "index.jsonl")
    if not files:
        print(f"no transcripts under {root}")
        return 2
    argv, cwd = launcher(args.bot)
    tot_turns = tot_div = 0
    bad = []
    for p in files:
        n_turns, n_div, _ = replay_one(str(p), argv, cwd, args)
        tot_turns += n_turns
        tot_div += n_div
        mark = "OK" if not n_div else f"{n_div} DIVERGENT"
        print(f"{mark:>12}  {p.relative_to(root)}  ({n_turns} turns)", flush=True)
        if n_div:
            bad.append(str(p))
            if not args.all:
                print(f"stopping at first divergent transcript; use --all to keep going")
                break
    print(f"suite: {len(files)} transcripts, {tot_turns} turns, {tot_div} divergent "
          f"({pathlib.Path(args.bot).name} vs {root})")
    return 1 if tot_div else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("map")
    r.add_argument("bot")
    r.add_argument("opp")
    r.add_argument("--side", default="A", choices="AB")
    r.add_argument("--seed", type=int, default=1)
    r.add_argument("--sandbox", action="store_true")
    r.add_argument("--out")
    r.add_argument("--gzip", action="store_true", help="write <bot>.jsonl.gz (replay reads both)")
    p = sub.add_parser("replay")
    p.add_argument("transcript")
    p.add_argument("bot")
    p.add_argument("--all", action="store_true")
    p.add_argument("--ignore-sonar", action="store_true")
    p.add_argument("--free-sonar", action="store_true")
    p.add_argument("--keep-debug", action="store_true")
    p.add_argument("--dragons")
    s = sub.add_parser("suite", help="replay a bot against every transcript under a directory "
                                    "(default: the Python reference recordings in build/cx/golden)")
    s.add_argument("bot")
    s.add_argument("--transcripts", default=str(REPO / "build" / "cx" / "golden"))
    s.add_argument("--all", action="store_true")
    s.add_argument("--ignore-sonar", action="store_true")
    s.add_argument("--free-sonar", action="store_true")
    s.add_argument("--keep-debug", action="store_true")
    s.add_argument("--dragons")
    args = ap.parse_args()
    if args.cmd == "record":
        return record(args)
    if args.cmd == "suite":
        return suite(args)
    return replay(args)


if __name__ == "__main__":
    sys.exit(main())

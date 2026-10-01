#!/usr/bin/env python3
"""cx arena: play one local game through unswbc 1.2.2's own engine and bot
pools (the same code path as `unswbc run`, optionally `--sandbox`) and return
early-game statistics, deaths by cause, CPU points per turn and, on request,
the full stdin/stdout transcript of every dragon of one team.

The bots are launched exactly as `unswbc run` launches them (bot.toml, same
compile), so a recorded bot is unchanged. Nothing here edits a bot.

    python3 tools/cx/arena.py MAP BOT_A BOT_B [--seed N] [--sandbox] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

from unswbc.bot import Bot, Pool
from unswbc.engine import DEBUG_ALL, EngineModule
from unswbc.run import _resolve

CHECK_ROUNDS = (25, 50, 100, 250)
CAUSE = {"W": "wall", "S": "self", "O": "body", "H": "h2h", "A": "no_action"}


def _parse_block(block: bytes) -> dict:
    """Round header of a turn block: round, length, unit count."""
    out = {}
    for line in block.split(b"\n", 6)[:6]:
        f = line.split()
        if len(f) >= 2 and f[0] in (b"ROUND", b"LENGTH", b"UNIT_COUNT", b"DIR"):
            out[f[0].decode()] = f[1].decode()
    return out


def _reply_cost(reply: bytes) -> tuple[str, int]:
    """(action, segments spent by the action itself): sprint n-1, split k."""
    act, spent = "", 0
    for line in reply.split(b"\n"):
        f = line.split()
        if not f:
            continue
        if f[0] == b"MOVE" and len(f) > 1:
            act, spent = "M" + f[1].decode(), len(f[1]) - 1
        elif f[0] == b"SPLIT" and len(f) > 1:
            act, spent = "S" + f[1].decode(), int(f[1])
    return act, spent


def purge_wasm_cache(bot: str) -> None:
    """unswbc 1.2.2 keys its sandbox wasm cache on .c/.cpp contents only, so a
    header-only edit reuses a stale build. Drop this bot's cached builds."""
    from unswbc.sandbox import _cache_dir
    name = pathlib.Path(bot).resolve().name
    for p in (_cache_dir() / "wasmbots").glob(f"{name}-*.wasm"):
        if len(p.stem) == len(name) + 33:  # name-<32 hex>
            p.unlink(missing_ok=True)


def _portal_edges(map_path: str):
    """(W, H, set of ('h', x, y) north sides, set of ('v', x, y) west sides) that are portals."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "ouroboros"))
    try:
        from mapview import load_map
    except ImportError:
        return None
    m = load_map(pathlib.Path(map_path).read_text())
    return m["W"], m["H"], set(m["portal_h"]), set(m["portal_v"])


def _own_head(block: bytes, did: int):
    sid = str(did).encode()
    for line in block.split(b"\n"):
        f = line.split()
        if len(f) == 6 and f[1] == sid and f[5] == b"1":
            return int(f[2]), int(f[3])
    return None


def _walk_portals(head, dirs, pe):
    """Walk a MOVE reply from head over dirs (NESW); return (crossed, rounds_walked).

    crossed is True when any stepped edge is a portal edge (wrapping the map).
    After a transit the geometric walk is wrong, so it stops there: one transit
    per reply is counted, which is what portal_steps means.
    """
    W, H, ph, pv = pe
    x, y = head
    for n, d in enumerate(dirs):
        key = (("h", x, y) if d == "N" else ("h", x, (y + 1) % H) if d == "S" else
               ("v", x, y) if d == "W" else ("v", (x + 1) % W, y))
        if (key[0] == "h" and key[1:] in ph) or (key[0] == "v" and key[1:] in pv):
            return True, n + 1
        if d == "N":
            y = (y - 1) % H
        elif d == "S":
            y = (y + 1) % H
        elif d == "W":
            x = (x - 1) % W
        else:
            x = (x + 1) % W
    return False, len(dirs)


def run_game(map_path: str, bot_a: str, bot_b: str, seed: int = 1, sandbox: bool = False,
             record: str | None = None, purge: bool = True, replay_out: str | None = None,
             meter_prefix: str | None = None) -> dict:
    """record: 'A' or 'B' to keep that team's transcripts (by dragon id).
    meter_prefix: collect stderr lines starting with this prefix from each bot
    (one list per team, payload after the prefix). Used by meter.py's -DCX_METER
    builds; stderr never reaches the engine or the replay, so it is free."""
    if sandbox:
        from unswbc.sandbox import SandboxBot, SandboxPool, WasmPool, warm_interpreter
        pool_type, bot_type = SandboxPool, SandboxBot
    else:
        pool_type, bot_type = Pool, Bot
    if sandbox and purge:
        for b in {bot_a, bot_b}:
            if not (pathlib.Path(b) / "main.py").is_file():
                purge_wasm_cache(b)
    ra = _resolve(bot_a, sandbox)
    rb = ra if bot_b == bot_a else _resolve(bot_b, sandbox)
    if sandbox and "python" in (ra[2], rb[2]):
        warm_interpreter()
    pools = {}
    for team, (argv, botdir, kind) in (("A", ra), ("B", rb)):
        maker = pool_type
        if sandbox and kind == "wasm":
            maker = WasmPool
        pools[team] = maker(argv, cwd=str(botdir), key=f"{seed:016x}-{team.lower()}")

    live, teams = {}, {}
    trans: dict[int, dict] = {}
    rows: dict[int, dict] = {}          # round -> team -> [units_seen, total_len]
    last: dict[int, tuple] = {}         # dragon -> (length, spent_by_action)
    sprint = {"A": 0, "B": 0}           # segments spent on sprints (MOVE n>1), whole game
    sprint100 = {"A": 0, "B": 0}
    eaten = {"A": 0, "B": 0}
    eaten100 = {"A": 0, "B": 0}
    eaten_cp = {"A": {}, "B": {}}   # cumulative pearls at r50/r100/r150/r250
    portal_steps = {"A": 0, "B": 0}
    sprint_extra = {"A": 0, "B": 0}
    sprint_actions = {"A": 0, "B": 0}
    first_pearl = {"A": None, "B": None}
    turns = {"A": 0, "B": 0}
    points = {"A": [], "B": []}
    boot = {"A": [], "B": []}   # first turn of each dragon (setup is charged)
    booted = set()
    meter_lines = {"A": [], "B": []}
    deaths = []
    errors = []
    pe = _portal_edges(map_path)
    dst: dict[int, dict] = {}           # per dragon: born, len, first_eat, last_portal, moves/turns r100
    cur = {"round": -1}

    def spawn(did: int, init: bytes) -> None:
        team = next((l.split()[1] for l in init.decode().splitlines() if l.startswith("TEAM")), "A")
        teams[did] = team
        live[did] = bot_type(pools[team], init=init, name=str(did))
        dst[did] = {"born": cur["round"], "len": 0, "first_eat": None, "portal": -99, "moves100": 0}
        if record == team:
            trans[did] = {"init": init.decode(), "turns": []}

    def reply(did: int, block: bytes) -> bytes:
        bot = live[did]
        out = bot.ask(block)
        team = teams[did]
        h = _parse_block(block)
        rnd = int(h.get("ROUND", 0))
        ln = int(h.get("LENGTH", 0))
        cur["round"] = rnd
        ds = dst.get(did)
        if ds is not None:
            ds["len"] = ln
        row = rows.setdefault(rnd, {"A": [0, 0], "B": [0, 0]})
        row[team][0] += 1
        row[team][1] += ln
        turns[team] += 1
        if did in last:
            pl, spent = last[did]
            got = ln - pl + spent
            if got > 0:
                eaten[team] += got
                if rnd <= 100:
                    eaten100[team] += got
                if first_pearl[team] is None:
                    first_pearl[team] = rnd
                if ds is not None and ds["first_eat"] is None:
                    ds["first_eat"] = rnd
        act, spent = _reply_cost(out)
        if ds is not None and act.startswith("M") and len(act) > 1:
            if rnd <= 100:
                ds["moves100"] += len(act) - 1
            if pe is not None:
                hp = _own_head(block, did)
                if hp is not None:
                    crossed, _ = _walk_portals(hp, act[1:], pe)
                    if crossed:
                        portal_steps[team] += 1
                        ds["portal"] = rnd
        if spent > 0:
            sprint_extra[team] += spent
            sprint_actions[team] += 1
        last[did] = (ln, spent)
        if spent and act.startswith("M"):
            sprint[team] += spent
            if rnd <= 100:
                sprint100[team] += spent
        if rnd in (50, 100, 150, 250):
            eaten_cp[team][rnd] = eaten[team]
        if bot.error is not None:
            errors.append((rnd, did, team, bot.error))
        if meter_prefix is not None:
            drain = getattr(bot, "take_stderr", None)
            if drain is not None:
                for mline in drain().decode(errors="replace").splitlines():
                    if mline.startswith(meter_prefix):
                        meter_lines[team].append(mline[len(meter_prefix):].strip())
        m = getattr(bot, "live", None)
        if m and m[0]:
            points[team].append(m[0])
            if did not in booted:
                boot[team].append(m[0])
        booted.add(did)
        if did in trans:
            trans[did]["turns"].append({"round": rnd, "input": block.decode(), "output": out.decode()})
        return out

    def death(did: int, rnd: int, reason: str) -> None:
        ds = dst.get(did, {})
        deaths.append({"round": rnd, "id": did, "team": teams.get(did, "?"),
                       "cause": CAUSE.get(reason, reason), "len": ds.get("len", 0),
                       "born": ds.get("born", -1), "portal": rnd - ds.get("portal", -99) <= 2})
        b = live.pop(did, None)
        if b is not None:
            b.stop()

    t0 = time.time()
    engine = EngineModule()
    try:
        res = engine.run(pathlib.Path(map_path).read_bytes(), reply, death, spawn,
                         lambda line: None, DEBUG_ALL, seed)
        if replay_out:
            pathlib.Path(replay_out).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(replay_out).write_bytes(engine.replay(pathlib.Path(bot_a).name, pathlib.Path(bot_b).name))
    finally:
        for b in live.values():
            b.stop()
        for p in pools.values():
            p.close()

    def at(r, team, k):
        # last round <= r that has a row (team may be dead -> 0)
        if r in rows:
            return rows[r][team][k]
        return 0

    stats = {}
    for team in "AB":
        s = {"eaten": eaten[team], "eaten_r100": eaten100[team], "first_pearl": first_pearl[team],
             "turns": turns[team], "sprint_extra": sprint_extra[team],
             "sprint_actions": sprint_actions[team],
             "sprint_per_eaten": sprint_extra[team] / max(1, eaten[team]),
             "sprint_per_eaten_r100": sprint_extra[team] / max(1, eaten100[team])}
        for r in CHECK_ROUNDS:
            s[f"units_r{r}"] = at(r, team, 0)
            s[f"len_r{r}"] = at(r, team, 1)
        dc = {}
        for d in deaths:
            if d["team"] == team:
                dc[d["cause"]] = dc.get(d["cause"], 0) + 1
        s["deaths"] = dc
        s["deaths_r100"] = sum(1 for d in deaths if d["team"] == team and d["round"] <= 100)
        # early-game ledger (C1): causes by r100, portal-step deaths, newborns, length lost
        mine = [d for d in deaths if d["team"] == team]
        c100 = {}
        for d in mine:
            if d["round"] <= 100:
                c100[d["cause"]] = c100.get(d["cause"], 0) + 1
        s["deaths_cause_r100"] = c100
        s["portal_deaths_r100"] = sum(1 for d in mine if d["round"] <= 100 and d["portal"])
        s["lenlost_r150"] = sum(d["len"] for d in mine if d["round"] <= 150)
        kids = [v for k, v in dst.items() if teams.get(k) == team and v["born"] >= 0]
        kid_ids = {k for k, v in dst.items() if teams.get(k) == team and v["born"] >= 0}
        s["births_r100"] = sum(1 for v in kids if v["born"] <= 100)
        s["newborn_dead10_r100"] = sum(1 for d in mine if d["id"] in kid_ids and d["born"] <= 100
                                       and d["round"] - d["born"] <= 10)
        lags = sorted(v["first_eat"] - v["born"] for v in kids if v["first_eat"] is not None and v["born"] <= 100)
        s["child_first_pearl_lag"] = lags[len(lags) // 2] if lags else None
        turns100 = sum(rows[r][team][0] for r in rows if r <= 100)
        moves100 = sum(v["moves100"] for k, v in dst.items() if teams.get(k) == team)
        s["turns_r100"] = turns100
        for r in (50, 100, 150, 250):
            s[f"eaten_r{r}"] = eaten_cp[team].get(r, 0)
        s["sprint_segs"] = sprint[team]
        s["sprint_segs_r100"] = sprint100[team]
        s["portal_steps"] = portal_steps[team]
        s["portal_deaths"] = sum(1 for d in mine if d["portal"])
        s["pearls_per_100dt"] = round(100 * eaten100[team] / turns100, 2) if turns100 else 0
        s["moves_per_pearl"] = round(moves100 / eaten100[team], 2) if eaten100[team] else None
        pts = sorted(points[team])
        if pts:
            def pc(q):
                return pts[max(0, -(-q * len(pts) // 100) - 1)]
            s["points"] = {"p50": pc(50), "p99": pc(99), "max": pts[-1], "n": len(pts)}
        if boot[team]:
            b = sorted(boot[team])
            s["boot"] = {"p50": b[len(b) // 2], "max": b[-1], "n": len(b)}
        stats[team] = s
    return {
        "map": pathlib.Path(map_path).stem, "a": bot_a, "b": bot_b, "seed": seed,
        "sandbox": sandbox, "winner": res.winner, "end_reason": res.end_reason,
        "rounds": res.rounds + 1, "a_length": res.a_length, "b_length": res.b_length,
        "stats": stats, "deaths": deaths, "errors": errors[:50], "secs": round(time.time() - t0, 1),
        "meter": meter_lines if meter_prefix else None,
        "transcripts": trans if record else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("map")
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--sandbox", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()
    r = run_game(args.map, args.a, args.b, args.seed, args.sandbox)
    r.pop("transcripts", None)
    txt = json.dumps(r, indent=1)
    if args.json:
        pathlib.Path(args.json).write_text(txt)
    print(json.dumps({k: r[k] for k in ("map", "winner", "rounds", "a_length", "b_length", "secs")}))
    for t in "AB":
        print(t, json.dumps(r["stats"][t]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

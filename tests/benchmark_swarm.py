"""Run with the Python interpreter from the installed unswbc tool environment.

Uses the official engine and process runner; saves six side-swapped matchups
per defender, along with replays and per-dragon observations.
"""
from pathlib import Path
from collections import Counter
import json
import re
import argparse
from unswbc.bot import Bot, Pool
from unswbc.engine import EngineModule
from unswbc.project import Project

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--escorts", action="store_true", help="Compare baseline and escorts instead of sprint defense")
args = parser.parse_args()
OUT = ROOT / "build" / ("escort-benchmark" if args.escorts else "swarm-benchmark")
OUT.mkdir(parents=True, exist_ok=True)
projects = {"baseline": ROOT / "bots/pre-swarm-defense",
            "defense": ROOT / "bots/danger-levels", "swarm": ROOT / "bots/kamikaze-swarm"}
if args.escorts:
    projects.pop("defense")
    projects["escorts"] = ROOT / "bots/escorts"
binaries = {name: str(Project.from_dir(str(path)).compile() / "bot") for name, path in projects.items()}
engine = EngineModule()
results = []


def play(board, defender, side):
    names = {side: defender, "B" if side == "A" else "A": "swarm"}
    pools = {team: Pool([binaries[name]], cwd=str(projects[name]), team=team.lower())
             for team, name in names.items()}
    live, teams = {}, {}
    peak, deaths = {"A": 0, "B": 0}, Counter()
    original_death = None
    original_id = 0 if side == "A" else 1
    sprints = 0

    def spawn(dragon, block):
        team = re.search(rb"TEAM ([AB])", block)[1].decode()
        teams[dragon] = team
        live[dragon] = Bot(pools[team], init=block, name=str(dragon))

    def reply(dragon, block):
        nonlocal sprints
        length = int(re.search(rb"LENGTH (\d+)", block)[1])
        peak[teams[dragon]] = max(peak[teams[dragon]], length)
        answer = live[dragon].ask(block)
        if live[dragon].error:
            raise RuntimeError(live[dragon].error)
        if teams[dragon] == side and re.search(rb"MOVE [NESW]{2}", answer):
            sprints += 1
        return answer

    def death(dragon, round_number, reason):
        nonlocal original_death
        if teams[dragon] == side:
            deaths[reason] += 1
        if dragon == original_id:
            original_death = round_number
        bot = live.pop(dragon, None)
        if bot:
            bot.stop()

    try:
        result = engine.run((ROOT / "maps" / f"{board}.map").read_bytes(), reply, death, spawn)
        label = f"{board}-{defender}-as-{side}"
        (OUT / f"{label}.replay").write_bytes(engine.replay(names['A'], names['B']))
        return dict(map=board, defender=defender, side=side,
                    outcome="draw" if result.winner is None else "win" if result.winner == side else "loss",
                    rounds=result.rounds + 1, peak_observed_length=peak[side],
                    final_total_length=result.a_length if side == "A" else result.b_length,
                    original_dragon_death_round=original_death,
                    deaths=dict(deaths), sprints=sprints)
    finally:
        for bot in live.values():
            bot.stop()
        for pool in pools.values():
            pool.close()


for board in ("arena", "default_small", "big_empty"):
    for defender in ("baseline", "escorts" if args.escorts else "defense"):
        for side in ("A", "B"):
            result = play(board, defender, side)
            results.append(result)
            (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
            print(json.dumps(result), flush=True)

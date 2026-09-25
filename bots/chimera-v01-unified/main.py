"""Chimera v01: a cross-family policy on the newer scaffold.

The turn loop keeps the scaffold's information -> state -> features -> intent ->
command -> sonar stages.  The bounded world model and evaluator are adapted
from Ouroboros v13; the compact-map doctrine is its Hunter-derived ladder.
"""
from enum import Enum, auto
import gc
import os
import sys

import protocol as io

gc.disable()


class Intent(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
    SPLIT = auto()
    ATTACK = auto()
    FEED_ALLY = auto()
    SCOUT = auto()


state = {}   # Per-dragon persistent evidence and policy memory.
work = {}    # Cleared at each turn; messages, features, choices and output.
first_turn = True
MODULES = ("defaults", "world", "comms", "safety", "targets", "roles",
           "evaluate", "ladder")
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    """Load source locally or the judge's legacy bytecode after packaging."""
    path = os.path.join(HERE, name + ".py")
    if os.path.exists(path):
        with open(path) as fh:
            return compile(fh.read(), path, "exec")
    import marshal
    with open(path + "c", "rb") as fh:
        return marshal.loads(fh.read()[16:])


for _module in MODULES:
    exec(_load(_module), globals())
del _module


def emit(line):
    """Strategy-side output buffer; protocol.py performs the single write."""
    work.setdefault("raw_output", []).append(line)


def flush():
    # The strategy modules call emit only.  The adapter writes once at
    # the end of the turn, after command and sonar lines have been separated.
    return


def commit_path(path):
    """Commit a simulated route to the own-body trail and command buffer."""
    global MOVED_DIR
    MOVED_DIR = path[-1]
    cell = HEAD
    for direction in path:
        nxt = dest(cell)[direction]
        if nxt < 0:
            break
        cell = nxt
        trail.append(cell)
    emit("MOVE " + "".join(DIRS[direction] for direction in path))


def initialize_state():
    global W, H, MY_ID, TEAM, UNIT_LIMIT, SALT
    MY_ID = io.game["id"]
    TEAM = io.game["team"]
    W, H = io.game["size"]
    UNIT_LIMIT = io.game["unit_limit"]
    SALT = 0x5A if TEAM == "A" else 0xC3
    setup()
    state.update(
        terrain=ek, unknown_edges=unk, seen=seen, fertile=fertile,
        visits=visits, pearls=pearls, spawn_at=spawn_at, enemies=enemies,
        allies=allies, trail=trail, role=ROLE, born_round=0,
    )


def decode_messages():
    """Validate incoming 64-bit reports before folding them into evidence."""
    global RND, echo
    RND = io.observation["round"]
    echo = io.observation["echoes"]
    for message in io.observation["messages"]:
        parsed = unpack(message)
        if parsed is not None:
            work["reports"].append(parsed)
        hear(message)


def update_state():
    """Merge the fresh 7x7 view and terrain edges into persistent memory."""
    global RND, LEN, UNITS, FACING, BORN, ROLE
    obs = io.observation
    RND = obs["round"]
    LEN = obs["length"]
    UNITS = obs["units"]
    FACING = DIRS.index(obs["direction"][0])
    mine = sense(obs["tiles"], obs["bodies"],
                 obs["horizontal_edges"], obs["vertical_edges"])

    if first_turn:
        BORN = RND
        seed_trail(mine)
        if RND == 0:
            ROLE = GATHER
        elif handoff is not None:
            ROLE = handoff[0]
        elif P["orphan_role"]:
            ROLE = orphan_role()
        else:
            ROLE = HUNT if LEN <= 2 else GATHER
        state["born_round"] = RND

    if trail and trail[-1] != HEAD:
        trail.append(HEAD)
    if len(trail) > 400:
        del trail[:-300]
    work["mine"] = mine
    state["round"] = RND
    state["head"] = HEAD
    state["length"] = LEN
    state["units"] = UNITS
    state["role"] = ROLE


def build_features():
    """Update compact perception features used by targets and the evaluator."""
    visits[HEAD] = min(255, visits[HEAD] + 1)
    broadcast_sightings()
    if RND % 16 == 0:
        prune()
    work["features"] = {
        "visible_enemies": len(enemy_heads),
        "visible_allies": len(ally_heads),
        "visible_pearls": sum(1 for cell, seen_round in pearls.items()
                               if seen_round == RND),
        "map_area": NC,
        "compact": NC <= 625,
    }


def _intent_for(kind, action):
    if kind == "split":
        return Intent.SPLIT
    if kind == "strike":
        return Intent.ATTACK
    if kind == "dive":
        return Intent.SCOUT
    if kind == "feed":
        return Intent.FEED_ALLY
    if isinstance(action, list) and action:
        return (Intent.NORTH, Intent.EAST, Intent.SOUTH, Intent.WEST)[action[0]]
    return Intent.SCOUT


def _append_option(options, score, action, kind, target=-1):
    options.append((_intent_for(kind, action), {
        "score": score, "action": action, "kind": kind, "target": target,
    }))


def _boot_option():
    """Use a cheap safe move on a newborn's first turn after interpreter boot."""
    body = body_list()
    best = -1
    best_value = -1e9
    for direction in range(4):
        result = simulate([direction], body)
        if not result[0]:
            continue
        cell = result[1]
        value = 0.0
        for neighbour in dest(cell):
            if neighbour < 0:
                value -= 0.3
                continue
            occupant = occ.get(neighbour)
            if occupant is not None:
                if occupant[2] and not occupant[1]:
                    value -= 5.0
                elif occupant[2]:
                    value -= 2.0
                else:
                    value -= 0.5
        if cell in pearls:
            value += 1.0
        if handoff is not None and handoff[1] >= 0:
            value -= 0.05 * tdist(cell, handoff[1])
        if value > best_value:
            best_value = value
            best = direction
    if best < 0:
        best = fallback_move()
    return [(0.0, [best], "move", handoff[1] if handoff else -1)]


def _emergency_portal(options):
    """Escape through a portal when every ordinary first step is fatal."""
    body = body_list()
    ordinary_survival = False
    portal_directions = []
    for direction in range(4):
        result = simulate([direction], body)
        if result[0]:
            ordinary_survival = True
        elif ek[ekey(HEAD, direction)] == 3:
            portal_directions.append(direction)
    if ordinary_survival or not portal_directions:
        return
    direction = portal_directions[(MY_ID + RND) % len(portal_directions)]
    _append_option(options, 10000.0, [direction], "dive")


def _safe_child_split():
    """Keep the ladder's fast split only when the newborn has an exit."""
    count = P["child_size"]
    if LEN < count + 2 or UNITS >= UNIT_LIMIT:
        return False
    body = body_list()
    if len(body) < LEN:
        return False
    child_head, child_neck = body[0], body[1]
    parent_body = set(body[count:])
    for cell in dest(child_head):
        if cell < 0 or cell == child_neck or cell in parent_body or cell in occ:
            continue
        if tunnel_heads(cell, child_head):
            continue
        if doom(cell, [child_head, cell]) >= 0:
            continue
        return True
    return False


def build_actions():
    """Build available execution options from the selected policy family."""
    actions = []
    if first_turn and RND > 0:
        for score, action, kind, target in _boot_option():
            _append_option(actions, score, action, kind, target)
    elif update_role():
        _append_option(actions, 100000.0, [], "feed", FEED[0])
    else:
        ladder_choice = ladder_decide() if ladder_active() else None
        if ladder_choice is not None and ladder_choice[0][2] == "split" \
                and not _safe_child_split():
            ladder_choice = None
        if ladder_choice is not None:
            ((score, action, kind), target) = ladder_choice
            _append_option(actions, score, action, kind, target)
        else:
            for score, action, kind, target in decide():
                _append_option(actions, score, action, kind, target)
        _emergency_portal(actions)

    if not actions:
        direction = fallback_move()
        _append_option(actions, -1e6, [direction], "move")
    work["actions"] = actions


def choose_action():
    """Select the highest-valued option; ladder actions already encode priority."""
    work["selected"] = max(work["actions"], key=lambda item: item[1]["score"])


def execute_action():
    """Translate the chosen intent into the engine's MOVE/SPLIT interface."""
    global ROLE
    intent, parameters = work["selected"]
    kind = parameters["kind"]
    action = parameters["action"]
    target = parameters.get("target", -1)
    work["state_updates"]["last_intent"] = intent.name

    if kind == "feed":
        # Missing action is the game's deliberate feeding/death mechanic.
        work["feeding"] = True
        return
    if kind == "split":
        count = int(action)
        child = child_role()
        if ROLE == CROWN and count > LEN - count:
            child = CROWN
            ROLE = GATHER
        emit("SPLIT %d" % count)
        back = neck_dir()
        work["split_message"] = handoff_packet(child, target)
        work["split_direction"] = back
        del trail[:-(LEN - count)]
        return

    path = action if isinstance(action, list) else [int(action)]
    commit_path(path)


def construct_messages():
    """Choose sonar payloads and directions after the surviving action."""
    if work.get("feeding"):
        return
    send_sonars(work.get("split_direction"), work.get("split_message"))


def encode_messages():
    """Convert strategy text lines into protocol commands and sonar fields."""
    command = None
    argument = ""
    sonar = {}
    for line in work.get("raw_output", ()):
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "MOVE" and len(fields) >= 2:
            command, argument = io.Command.MOVE, fields[1]
        elif fields[0] == "SPLIT" and len(fields) >= 2:
            command, argument = io.Command.SPLIT, fields[1]
        elif fields[0] == "SONAR" and len(fields) >= 3:
            sonar[fields[1]] = int(fields[2])
    io.reply.clear()
    io.reply.update(command=command, argument=argument, sonar=sonar)


def record_diagnostics():
    """Keep a compact selected-action record in memory without stdout noise."""
    if "selected" in work:
        state["last_action_round"] = RND
        state["last_action"] = work["selected"][0].name


def main():
    global first_turn
    if not io.read_init():
        return
    initialize_state()
    while io.read_turn():
        work.clear()
        work.update(reports=[], actions=[], selected=None, messages=[],
                    state_updates={}, raw_output=[])
        io.reply.clear()
        decode_messages()
        update_state()
        build_features()
        build_actions()
        choose_action()
        execute_action()
        construct_messages()
        encode_messages()
        record_diagnostics()
        state.update(work["state_updates"])
        io.write_reply()
        first_turn = False


if __name__ == "__main__":
    main()

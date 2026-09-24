import helper as unswbc
from helper import Direction, EdgeType
import random
from collections import deque

ct: unswbc.Controller
game: unswbc.Game

# =====================================================================
# CONFIG - every tunable lives here so sweeps only touch this block.
# =====================================================================
W = dict(
    pearl_now=60.0,       # per pearl eaten on this turn's path
    pearl_dist=-4.0,      # per BFS step from end tile to nearest remaining pearl
    space=2.0,            # per reachable tile after the move (capped)
    trap=-500.0,          # reachable space < own length: likely dead soon
    head_threat=-80.0,    # another head can step onto this tile next turn
    unseen=-30.0,         # landing outside vision (portal exit): occupancy unknown
    visits=-3.0,          # per previous visit of the end tile (this process only)
    straight=2.0,         # small momentum bonus to stop dithering
    sprint=-15.0,         # per extra step (on top of the segment it costs)
    split_want=1000.0,    # strategic split, when the strategy layer wants one
    split_emergency=-200.0,  # beats trapped moves, loses to any open move
    jitter=0.01,          # random tie-break
)
SPRINT_MAX = 1            # 1 disables sprinting; 2-3 to test sprints
SPACE_CAP_EXTRA = 6       # flood fill stops at length + this
SPLIT_MIN_LENGTH = 6
SPLIT_SIZE = 2

DIRS = Direction.get_direction_list()
WIDTH = HEIGHT = 0


# =====================================================================
# MEMORY - persists across turns for this process only.
# Split children start from scratch (new process).
# =====================================================================
class Memory:
    def __init__(self):
        self.edges = {}     # canonical edge -> "kelp" | "empty" | portal id (int)
        self.portals = {}   # portal id -> set of canonical edges
        self.visits = {}    # (x, y) -> times our head was here
        self.inbox = []     # sonar values received this turn
        self.turns = 0


mem = Memory()


# =====================================================================
# GEOMETRY - positions are (x, y) tuples so they hash.
# =====================================================================
def xy(pos):
    return (pos.x, pos.y)   # adjust here if Position exposes x/y differently


def adj(p, d):
    dx, dy = d.get_offset()
    return ((p[0] + dx) % WIDTH, (p[1] + dy) % HEIGHT)


def canon(p, d):
    # One key per physical edge: stored as the N or W side of a tile.
    if d == Direction.NORTH: return (p, "N")
    if d == Direction.WEST:  return (p, "W")
    if d == Direction.SOUTH: return (adj(p, d), "N")
    return (adj(p, d), "W")


def step(p, d):
    """Tile reached by leaving p towards d, ignoring bodies. None if kelp or
    an unresolved portal. Unknown edges (outside memory) are assumed open."""
    key = canon(p, d)
    e = mem.edges.get(key)
    if e == "kelp":
        return None
    if e is None or e == "empty":
        return adj(p, d)
    others = [x for x in mem.portals.get(e, ()) if x != key]
    if not others:
        return None
    q, _ = others[0]
    # Direction is preserved through a portal.
    return q if d in (Direction.SOUTH, Direction.EAST) else adj(q, d)


# =====================================================================
# 1. PERCEIVE - raw helper objects -> World snapshot + memory update.
# =====================================================================
class World:
    pass


def perceive():
    w = World()
    w.round = game.get_round_num()
    w.limit = game.get_unit_limit()
    w.me, w.team = ct.get_id(), ct.get_team()
    w.length, w.units = ct.get_length(), ct.get_unit_count()
    w.head, w.facing = xy(ct.get_position()), ct.get_dir()
    w.vision, w.blocked, w.pearls, w.heads = set(), set(), set(), []

    for t in ct.get_tiles():
        p = xy(t.get_position())
        w.vision.add(p)
        part = t.get_dragon()
        if part is not None:
            w.blocked.add(p)
            if part.is_head() and part.get_id() != w.me:
                w.heads.append((p, part.get_team() == w.team))
        elif t.has_pearl():
            w.pearls.add(p)
        for d in DIRS:  # terrain is static: remember it forever
            e = t.get_edge(d)
            key = canon(p, d)
            et = e.get_edge_type()
            if et == EdgeType.KELP:
                mem.edges[key] = "kelp"
            elif et == EdgeType.PORTAL:
                mem.edges[key] = e.get_portal_id()
                mem.portals.setdefault(e.get_portal_id(), set()).add(key)
            else:
                mem.edges[key] = "empty"

    mem.visits[w.head] = mem.visits.get(w.head, 0) + 1
    mem.inbox = ct.get_sonar_messages()
    mem.turns += 1
    return w


# =====================================================================
# 2. ANALYSE - fields computed once per turn or per candidate.
# =====================================================================
def threat_map(w):
    """Tiles any other head (either team) could enter next turn."""
    threat = {}
    for p, _friendly in w.heads:
        for d in DIRS:
            n = step(p, d)
            if n is not None and n not in w.blocked:
                threat[n] = threat.get(n, 0) + 1
    return threat


def bfs(start, blocked):
    """Distances over visible tiles; tiles outside vision are not expanded."""
    dist = {start: 0}
    q = deque([start])
    while q:
        p = q.popleft()
        for d in DIRS:
            n = step(p, d)
            if n is None or n in blocked or n in dist:
                continue
            dist[n] = dist[p] + 1
            if n in W_VISION:
                q.append(n)
    return dist


def flood(start, blocked, cap):
    """Reachable tile count, stopping at cap. Outside vision counts as open."""
    seen = {start}
    q = deque([start])
    while q and len(seen) < cap:
        p = q.popleft()
        for d in DIRS:
            n = step(p, d)
            if n is None or n in blocked or n in seen:
                continue
            seen.add(n)
            q.append(n)
    return len(seen)


W_VISION = set()  # set each turn; used by bfs to bound expansion


# =====================================================================
# 3. STRATEGY - game-level intent. Sets permissions/targets, not moves.
# =====================================================================
def strategy(w):
    s = dict(want_split=False, split_size=SPLIT_SIZE)
    if w.length >= SPLIT_MIN_LENGTH and w.units < w.limit:
        s["want_split"] = True
    return s


# =====================================================================
# 4. CANDIDATES - every action worth considering this turn.
# =====================================================================
def move_paths(w):
    """All legal step sequences of length 1..SPRINT_MAX."""
    out = []

    def rec(path, dirs):
        if dirs:
            out.append((list(dirs), list(path)))
        steps = len(dirs) + 1
        if steps > SPRINT_MAX or w.length - (steps - 1) < 2:
            return
        here = path[-1] if path else w.head
        for d in DIRS:
            n = step(here, d)
            if n is None or n in w.blocked or n in path:
                continue
            rec(path + [n], dirs + [d])

    rec([], [])
    return out


# =====================================================================
# 5. SCORE
# =====================================================================
def score_move(w, dirs, path, threat):
    end = path[-1]
    blocked = w.blocked | set(path[:-1])
    s = 0.0

    eaten = sum(1 for p in path if p in w.pearls)
    s += W["pearl_now"] * eaten
    s += W["sprint"] * (len(path) - 1)

    cap = w.length + SPACE_CAP_EXTRA
    space = flood(end, blocked, cap)
    s += W["space"] * space
    if space < w.length:
        s += W["trap"]

    s += W["head_threat"] * threat.get(end, 0)
    if end not in w.vision:
        s += W["unseen"]

    remaining = w.pearls - set(path)
    if remaining:
        dist = bfs(end, blocked)
        ds = [dist[p] for p in remaining if p in dist]
        if ds:
            s += W["pearl_dist"] * min(ds)

    s += W["visits"] * mem.visits.get(end, 0)
    if dirs[0] == w.facing:
        s += W["straight"]
    return s + random.random() * W["jitter"]


def score_splits(w, strat, threat):
    out = []
    if strat["want_split"] and threat.get(w.head, 0) == 0:
        n = strat["split_size"]
        if ct.can_split(n):
            out.append((W["split_want"], ("split", n)))
    n = w.length - 2  # emergency: child takes most of the body
    if n >= 2 and ct.can_split(n):
        out.append((W["split_emergency"], ("split", n)))
    return out


# =====================================================================
# 6. ACT
# =====================================================================
def execute_turn() -> None:
    global W_VISION
    w = perceive()
    W_VISION = w.vision
    threat = threat_map(w)
    strat = strategy(w)

    options = []
    for dirs, path in move_paths(w):
        options.append((score_move(w, dirs, path, threat), ("move", dirs)))
    options += score_splits(w, strat, threat)

    if not options:
        ct.set_indicator_string("no options")
        ct.make_move(w.facing)  # doomed anyway; head straight
        return

    options.sort(key=lambda o: o[0], reverse=True)
    score, (kind, arg) = options[0]

    # Debug: top options in the replay log.
    ct.output_log(" | ".join(f"{k}:{fmt(a)}={s:.0f}" for s, (k, a) in options[:4]))
    ct.set_indicator_string(f"{kind} {fmt(arg)} {score:.0f}")

    if kind == "split":
        ct.do_split(arg)
    elif len(arg) == 1:
        ct.make_move(arg[0])
    else:
        ct.make_moves(arg)

    # Sonar: send after choosing the action, e.g. ct.send_sonar(encode(...)).


def fmt(a):
    if isinstance(a, list):
        return "".join(d.value() if callable(d.value) else str(d.value) for d in a)
    return str(a)


def main() -> None:
    global ct, game, WIDTH, HEIGHT
    ct, game = unswbc.init()
    WIDTH, HEIGHT = game.get_map_size()
    seeded = False

    while unswbc.update(ct, game):
        if not seeded:  # per-dragon seed, so dragons don't move in lockstep
            random.seed(ct.get_id())
            seeded = True
        execute_turn()
        unswbc.end_turn()


if __name__ == "__main__":
    main()
"""hydra-v01: role-based swarm with a persistent shared map.

Each dragon is a separate process with a 7x7 window. Everything beyond the
window lives in three stores: terrain (static, learned once), pearls (visible
state plus spawn predictions from pearl countdowns), and gossip (ally self
reports, enemy sightings and portal edges relayed over sonar with a TTL, so
facts diffuse dragon-to-dragon).

Roles are decided at creation time and encoded in the split size: a 2-segment
child is a scout, a 3-segment child is a hunter, anything else is a gatherer.
Map-spawned dragons are gatherers. Scouts chase the frontier, hunters chase
known enemies, gatherers chase pearls in safe fertile ground.
"""

from __future__ import annotations

import random

import helper as unswbc
from helper import Direction, EdgeType, Team

ct: unswbc.Controller
game: unswbc.Game

# =====================================================================
# CONFIG - every tunable lives here so parameter sweeps only touch this.
# =====================================================================
CFG = dict(
    # ---- split policy ----
    scout_until=110,        # children born before this round are scouts (size 2)
    hunter_until=330,       # children born before this round are hunters (size 3)
    early_team_target=12,   # desired team size during the scouting phase
    mid_team_target=14,     # desired team size during the hunting phase
    big_map_units=14,       # team target floor scales up on large maps
    big_map_divisor=150,    # n_cells // this, capped at big_map_units
    grow_after=240,         # after this round the team stops expanding
    grow_floor=8,           # ...and only replaces losses below this size
    split_len=4,            # min length before a voluntary split
    late_round=360,         # no voluntary splits after this round
    late_team_floor=3,      # ... unless the team has dropped below this
    # ---- target scoring ----
    w_pearl=100.0,          # remembered pearl on a tile
    w_fertile=6.0,          # tile that can spawn pearls at all (camp the field)
    block_dist_pen=2.0,     # per torus tile from us to a candidate block
    block_floor=20.0,       # a block trip must beat this to override the compass
    w_spawn=28.0,           # predicted spawn, scaled by how soon it lands
    w_frontier=12.0,        # unseen tile, gatherer weight
    w_frontier_scout=48.0,  # unseen tile, scout weight
    w_enemy_hunt=140.0,     # recent enemy sighting (hunters)
    w_dist=-2.2,            # per BFS step to the target
    w_visit=-5.0,           # per visit of the target tile by this dragon
    w_spread=-1.6,          # penalty for crowding a known ally head
    # ---- move safety ----
    w_danger=-1200.0,        # stepping into a threatened tile
    w_soft=-26.0,           # stepping into a 2-step enemy reach tile
    w_space=2.4,            # per reachable tile after the move
    trap_pen=-500.0,        # reachable space smaller than our length
    space_slack=8,          # flood fill stops at length + this
    # ---- combat ----
    hunter_trade_gap=3,     # strike enemy heads at least this much longer
    attack_range=11,        # how far to chase a known enemy head
    attack_fresh=24,        # rounds a gossip sighting stays worth chasing
    min_units_attack=4,     # keep a floor of units before picking fights
    scout_strikes=True,     # length-2 scouts trade themselves into any head
    strike_gap_units=2,     # or strike freely when we outnumber them this much
    # ---- sonar ----
    relay_ttl=2,            # hops a forwarded packet may still take
    self_every=1,           # rounds between self reports
    pearl_digest_every=12,  # rounds between block fertility reports
    # ---- compute ----
    plan_every=1,           # rounds a target-search verdict is reused
    bfs_cap=800,            # cells the target search may visit
)

DIRS = Direction.get_direction_list()
N, E, S, W = DIRS

ROLE_G, ROLE_H, ROLE_S = 0, 1, 2  # gatherer, hunter, scout
ROLE_NAME = "GHS"

# Every stdout write is charged 2.5M CPU points by the judge, so a turn's
# whole output is assembled here and leaves in a single write.
import sys
_lines: list[str] = []


def out_move(direction: Direction) -> None:
    _lines.append(f"MOVE {direction.value}")


def out_sprint(direction: Direction) -> None:
    _lines.append(f"MOVE {direction.value}{direction.value}")


def out_split(child: int) -> None:
    _lines.append(f"SPLIT {child}")


def out_sonar(direction: Direction, value: int) -> None:
    _lines.append(f"SONAR {direction.value} {value}")


def out_indicator(text: str) -> None:
    _lines.append(f"INDICATOR {text}")


def flush_turn() -> None:
    _lines.append("PROTOCOL 3")  # per-turn protocol handshake, as in the helper
    _lines.append("ENDTURN")
    sys.stdout.write("\n".join(_lines) + "\n")
    sys.stdout.flush()
    _lines.clear()


_sonar_out: list[tuple[Direction, int]] = []  # this turn's sonar slots
turns_done = 0


def boot_turn() -> None:
    """A fresh process spends most of its first-turn budget on interpreter
    boot and imports, so a mid-game child's first turn does almost nothing:
    parse just the 3x3 around the head and take the safest passable step,
    snacking on an adjacent pearl if one is there.  Full machinery starts on
    the second turn."""
    facing = ct.get_dir()
    vision = ct.get_vision()
    here = ct.get_position()
    best, best_score = None, -100.0
    for direction in DIRS:
        pos = here.add_dir(direction)
        tile = vision.get_tile(pos)
        if tile is None or tile.get_dragon() is not None \
                or not tile.get_edge(direction.get_opposite()).is_passable():
            continue  # the edge that matters is on our side of the tile
        danger = 0
        for side in DIRS:
            near = vision.get_tile(pos.add_dir(side))
            if near is None:
                continue
            part = near.get_dragon()
            if part is not None:
                danger += 2 if part.get_team() != my_team else (
                    1 if part.is_head() else 0)
        score = -4.0 * danger + (1.0 if tile.pearl else 0.0) \
            + (0.5 if direction == facing else 0.0)
        if score > best_score:
            best, best_score = direction, score
    out_move(best if best is not None else facing)
    out_sonar(DIRS[game.get_round_num() & 3],
              pack(K_SELF, self_payload(game.get_round_num())))

width = height = 0
n_cells = 0
steps: list[tuple[int, ...] | None] = []  # neighbour table, filled on demand

# ---- terrain memory (static once seen) ----
edge_kind = bytearray()          # per canonical edge: 0 unknown 1 open 2 kelp 3 portal
portal_id: dict[int, int] = {}   # canonical edge -> portal id
portal_pair: dict[int, list[int]] = {}  # portal id -> known edges (<= 2)
seen = bytearray()               # tile ever observed
fertile = bytearray()            # tile can spawn pearls (pearl_time >= 0 once)
visits = bytearray()             # times this dragon's head stood here (cap 255)

# ---- dynamic memory ----
pearls: dict[int, int] = {}      # cell -> round last confirmed on the tile
spawn_at: dict[int, int] = {}    # cell -> round a pearl is expected
allies: dict[int, tuple] = {}    # id -> (cell, dir_index, length, role, round)
enemies: dict[int, tuple] = {}   # cell -> (round seen, visible length)
seen_blocks: dict[int, int] = {} # 6x6-tile block index -> fertile tile count

# ---- sonar io ----
relay: list[tuple[int, int]] = []     # (kind, payload) waiting to go out
relayed_stamp: dict[int, int] = {}    # payload -> round we last relayed it
portal_sent: set[int] = set()         # portal ids we already broadcast

trail: list[int] = []            # our head cells, oldest first (exact body)
role = ROLE_G
my_id = -1
my_team: Team = None


def setup() -> None:
    global width, height, n_cells, steps, edge_kind, seen, fertile, visits
    width, height = game.get_map_size()
    n_cells = width * height
    steps = [None] * n_cells
    edge_kind = bytearray(4 * n_cells)
    seen = bytearray(n_cells)
    fertile = bytearray(n_cells)
    visits = bytearray(n_cells)
    step_cache.extend([None] * n_cells)


def around(cell: int) -> tuple[int, int, int, int]:
    x = cell % width
    return (
        cell - width if cell >= width else cell - width + n_cells,
        cell + 1 if x + 1 < width else cell + 1 - width,
        cell + width if cell < n_cells - width else cell + width - n_cells,
        cell - 1 if x else cell - 1 + width,
    )


def neighbours(cell: int) -> tuple[int, ...]:
    got = steps[cell]
    if got is None:
        steps[cell] = got = around(cell)
    return got


def canon(cell: int, d: int) -> int:
    """Canonical edge id for the edge on side d of cell (N/W sides only)."""
    if d == 1:
        return around(cell)[1] * 4 + 3
    if d == 2:
        return around(cell)[2] * 4 + 0
    return cell * 4 + d


def dest(cell: int, d: int) -> int:
    """Cell reached leaving cell towards d, or -1 if the way is blocked.
    Unknown edges read as open; the immediate step is always known because
    adjacent tiles are visible."""
    ck = canon(cell, d)
    kind = edge_kind[ck]
    if kind == 2:
        return -1
    if kind == 3:
        ends = portal_pair.get(portal_id[ck])
        if not ends or len(ends) < 2:
            return -1  # partner unseen: cannot compute the exit
        other = ends[0] if ends[1] == ck else ends[1]
        base = other >> 2
        if (other & 3) == 3:  # vertical edge: west side of base
            if d == 1:            # emerge from the east side of the partner
                return base
            return around(base)[3]
        if d == 2:            # horizontal edge: north side of base
            return base
        return around(base)[0]
    return neighbours(cell)[d]


# Terrain is static, so each cell's four step-destinations are computed once
# and cached; completing a portal pairing is the only event that changes them.
step_cache: list[tuple | None] = []


def cell_steps(cell: int) -> tuple:
    got = step_cache[cell]
    if got is None:
        got = step_cache[cell] = (dest(cell, 0), dest(cell, 1),
                                  dest(cell, 2), dest(cell, 3))
    return got


def invalidate_steps() -> None:
    for i in range(len(step_cache)):
        step_cache[i] = None


# =====================================================================
# PERCEIVE
# =====================================================================
def fold_vision(round_now: int) -> dict:
    """Merge the 7x7 window into memory; return this round's local snapshot."""
    heads = []         # (cell, id, is_ally, will_act_after_us)
    blocked = set()    # every dragon part we can see, our own included
    vision_pearls = set()
    head_cell = -1
    my_parts = {}      # our own segments, to seed the trail on turn one
    for tile in ct.get_vision().get_tiles():
        pos = tile.get_position()
        cell = pos.y * width + pos.x
        seen[cell] = 1
        pt = tile.get_pearl_time()
        if pt >= 0:
            fertile[cell] = 1
            if not tile.pearl and pt > 0:
                spawn_at[cell] = round_now + pt
        part = tile.get_dragon()
        if part is not None:
            if part.get_id() != my_id:  # our own body is tracked by the trail
                blocked.add(cell)
            pearls.pop(cell, None)
            spawn_at.pop(cell, None)
            if part.is_head():
                if part.get_id() == my_id:
                    head_cell = cell
                else:
                    heads.append((cell, part.get_id(),
                                  part.get_team() == my_team, part.get_id() > my_id))
            elif part.get_id() == my_id:
                my_parts[cell] = part
        elif tile.pearl:
            vision_pearls.add(cell)
            pearls[cell] = round_now
        else:
            pearls.pop(cell, None)
        for d, direction in enumerate(DIRS):
            ck = canon(cell, d)
            edge = tile.get_edge(direction)
            et = edge.get_edge_type()
            if et == EdgeType.KELP:
                edge_kind[ck] = 2
            elif et == EdgeType.PORTAL:
                edge_kind[ck] = 3
                pid = edge.get_portal_id()
                portal_id[ck] = pid
                ends = portal_pair.setdefault(pid, [])
                if ck not in ends:
                    ends.append(ck)
                    if len(ends) == 2:
                        invalidate_steps()
                if pid not in portal_sent:
                    portal_sent.add(pid)
                    relay.insert(0, (K_PORTAL, portal_payload(pid)))
            elif edge_kind[ck] == 0:
                edge_kind[ck] = 1

    for cell, p_round in list(pearls.items()):
        if p_round < round_now - 40:
            pearls.pop(cell)  # stale: eaten or collected long ago

    snap = dict(heads=heads, blocked=blocked, pearls=vision_pearls,
                head_cell=head_cell, my_parts=my_parts, enemy_parts=0)
    for tile in ct.get_vision().get_tiles():
        part = tile.get_dragon()
        if part is not None and part.get_team() != my_team:
            snap["enemy_parts"] += 1
    seed_trail(snap)
    return snap


def seed_trail(snap: dict) -> None:
    """On our first turn the trail starts as our visible segments, ordered
    from tail to head; after that every move appends."""
    if trail:
        return
    head = snap["head_cell"]
    if head < 0:
        return
    ordered = [head]
    parts = snap["my_parts"]
    while True:
        cur = ordered[-1]
        nxt = next((n for n in around(cur) if n in parts and n not in ordered), None)
        if nxt is None:
            break
        ordered.append(nxt)
    # execute_turn appends the head itself; seed only the segments behind it
    trail.extend(reversed(ordered[1:]))


# =====================================================================
# DANGER
# =====================================================================
def threat_map(heads, blocked) -> dict:
    """cell -> danger weight. Enemy heads that act after us (higher id) get a
    two-step reservation; everything else one step."""
    danger = {}
    for cell, _pid, is_ally, will_act in heads:
        if not is_ally:
            danger[cell] = max(danger.get(cell, 0), 2)
        for n in cell_steps(cell):
            if n < 0:
                continue
            danger[n] = max(danger.get(n, 0), 1 if is_ally else 2)
            if not is_ally and will_act:
                for m in cell_steps(n):
                    if m >= 0:
                        danger[m] = max(danger.get(m, 0), 1)
    return danger


# =====================================================================
# SONAR PROTOCOL  (uint64: tag 12 | kind 4 | payload 48)
# =====================================================================
MAGIC = 0x5B7
K_SELF, K_ENEMY, K_PORTAL, K_PEARL = 1, 2, 3, 4
TTL_SHIFT = 46

# K_SELF:   id(8) cell(12) facing(2) length(6) role(2) round(9)
# K_ENEMY:  ttl(2) cell(12) length(6) round(9)
# K_PORTAL: ttl(2) pid(32) cell(12) side(1)
# K_PEARL:  ttl(2) block(7) fertile(6)


def pack(kind: int, payload: int) -> int:
    tag = (MAGIC ^ kind ^ (payload & 0xFFF) ^ ((payload >> 24) & 0xFFF)) & 0xFFF
    return (tag << 52) | (kind << 48) | payload


def unpack(value: int):
    tag, body = value >> 52, value & ((1 << 52) - 1)
    kind, payload = body >> 48, body & ((1 << 48) - 1)
    check = (MAGIC ^ kind ^ (payload & 0xFFF) ^ ((payload >> 24) & 0xFFF)) & 0xFFF
    return (kind, payload) if tag == check else None


def with_ttl(kind: int, payload: int) -> int:
    # portal pairings are static gold and their partner can be far away:
    # they travel much further than the volatile enemy/pearl packets
    ttl = 6 if kind == K_PORTAL else CFG["relay_ttl"]
    return (ttl << TTL_SHIFT) | payload


def portal_payload(pid: int) -> int:
    ends = portal_pair.get(pid) or []
    ck = ends[0]
    side = (ck & 3) >> 1  # 3 (west) -> 1, 0 (north) -> 0
    return with_ttl(K_PORTAL, ((pid & 0xFFFFFFFF) << 13) | ((ck >> 2) << 1) | side)


def enemy_payload(cell: int, length: int, round_now: int) -> int:
    return with_ttl(K_ENEMY, (cell << 15) | (length << 9) | (round_now & 0x1FF))


def self_payload(round_now: int) -> int:
    facing = DIRS.index(ct.get_dir())
    cell = trail[-1] if trail else ct.get_position().y * width + ct.get_position().x
    return (((my_id & 0xFF) << 31) | ((cell & 0xFFF) << 19)
            | (facing << 17) | ((ct.get_length() & 0x3F) << 11)
            | (role << 9) | (round_now & 0x1FF))


def apply_packet(kind: int, payload: int, round_now: int) -> None:
    if kind == K_SELF:
        pid_ = (payload >> 31) & 0xFF
        allies[pid_] = ((payload >> 19) & 0xFFF, (payload >> 17) & 3,
                        (payload >> 11) & 0x3F, (payload >> 9) & 3, payload & 0x1FF)
        return
    if kind == K_ENEMY:
        cell = (payload >> 15) & 0xFFF
        when = payload & 0x1FF
        if (round_now - when) & 0x1FF < 60 and (
                cell not in enemies or enemies[cell][0] < when):
            enemies[cell] = (when, (payload >> 9) & 0x3F)
    elif kind == K_PORTAL:
        pid_ = (payload >> 13) & 0xFFFFFFFF
        ck = (((payload >> 1) & 0xFFF) << 2) | (3 if payload & 1 else 0)
        ends = portal_pair.setdefault(pid_, [])
        if ck not in ends and len(ends) < 2:
            # only trust gossip whose orientation matches what it claims
            ends.append(ck)
            portal_id[ck] = pid_
            if edge_kind[ck] == 0:
                edge_kind[ck] = 3
            if len(ends) == 2:
                invalidate_steps()
    elif kind == K_PEARL:
        block = (payload >> 6) & 0x7F
        seen_blocks[block] = max(seen_blocks.get(block, 0), payload & 0x3F)
    forward(kind, payload, round_now)


def forward(kind: int, payload: int, round_now: int) -> None:
    """Give a heard packet one more hop if its TTL and dedup allow."""
    key = (kind << 48) | payload
    if relayed_stamp.get(key, -99) > round_now - 30:
        return
    ttl = (payload >> TTL_SHIFT) & 3
    if ttl <= 1 or len(relay) > 6:
        return
    relayed_stamp[key] = round_now
    relay.append((kind, ((payload & ((1 << TTL_SHIFT) - 1))
                         | ((ttl - 1) << TTL_SHIFT))))


def pearl_digest(round_now: int) -> tuple[int, int] | None:
    """Our current 6x6 block of fertility knowledge; receivers keep the max."""
    bsize = 6
    head = trail[-1]
    bx, by = (head % width) // bsize, (head // width) // bsize
    nbx = (width + bsize - 1) // bsize
    count = 0
    for dy in range(bsize):
        row = (by * bsize + dy) * width
        if by * bsize + dy >= height:
            break
        for dx in range(bsize):
            if bx * bsize + dx < width:
                count += fertile[row + bx * bsize + dx]
    block = by * nbx + bx
    seen_blocks[block] = count
    return (K_PEARL, with_ttl(K_PEARL, (block << 6) | count))


# =====================================================================
# MOVEMENT
# =====================================================================
def blocked_for_step(cell: int, eating: bool, length: int) -> bool:
    """Own body blocks its CURRENT cells: collision is checked before any
    segment moves, so even the tail tile is fatal (eating or not)."""
    return cell in trail[-length:]


def own_body_map(length: int) -> dict[int, int]:
    """cell -> smallest distance j from our head over the current body.  A
    cell at distance j stays lethal until future step k satisfies k + j > L+1
    (the body vacates from the tail as we move; eating delays it, so callers
    stay conservative by ignoring pearls on the path)."""
    own = {}
    for j in range(1, min(length, len(trail)) + 1):
        c = trail[-j]
        if c not in own or own[c] > j:
            own[c] = j
    return own


def flood_space(start: int, length: int, danger: dict, blocked: set,
                own: dict[int, int]) -> int:
    cap = length + CFG["space_slack"]
    got = {start: 0}
    queue = [start]
    qi = 0
    while qi < len(queue) and len(got) < cap:
        cell = queue[qi]
        qi += 1
        depth = got[cell] + 1
        for n in cell_steps(cell):
            if n < 0 or n in got or n in blocked or danger.get(n, 0) >= 2:
                continue
            j = own.get(n)
            if j is not None and depth + j <= length + 1:
                continue  # our body is still there at this depth
            got[n] = depth
            queue.append(n)
    return len(got)


def bfs_target(head: int, danger: dict, blocked: set, round_now: int,
               own: dict[int, int], length: int) -> int:
    """One capped breadth-first pass scoring targets in place; returns the
    best first direction, or -1 when nothing is worth walking to."""
    cap = CFG["bfs_cap"] if n_cells > CFG["bfs_cap"] else n_cells
    dist = [-1] * n_cells
    first = [-1] * n_cells
    dist[head] = 0
    queue = [head]
    best_d, best_score = -1, -1e18
    frontier_w = CFG["w_frontier_scout"] if role == ROLE_S else CFG["w_frontier"]
    qi = 0
    while qi < len(queue) and len(queue) < cap:
        cell = queue[qi]
        qi += 1
        steps_to = dist[cell] + 1
        for d in range(4):
            n = cell_steps(cell)[d]
            if n < 0 or dist[n] >= 0 or n in blocked:
                continue
            j = own.get(n)
            if j is not None and steps_to + j <= length + 1:
                continue  # our own body still occupies it at this depth
            dist[n] = steps_to
            first[n] = d if cell == head else first[cell]
            queue.append(n)
            score = CFG["w_dist"] * steps_to
            if n in pearls:
                score += CFG["w_pearl"]
            elif fertile[n]:
                score += CFG["w_fertile"]
            when = spawn_at.get(n)
            if when is not None and fertile[n]:
                if when <= round_now:
                    score += CFG["w_spawn"]
                else:
                    score += CFG["w_spawn"] * max(0.0, 1.0 - (when - round_now) / 30.0)
            if not seen[n]:
                score += frontier_w
            if role == ROLE_H and n in enemies:
                age = round_now - enemies[n][0]
                if age < 40:
                    score += CFG["w_enemy_hunt"] * (1.0 - age / 40.0)
            score += CFG["w_visit"] * min(visits[n], 12)
            if score > best_score:
                best_score = score
                best_d = first[n]
    return best_d


# The full-map target search is the most expensive part of a turn, so its
# verdict is kept for a few rounds: the plan only matters as a compass
# heading, and every step is still checked for safety fresh each turn.
plan_cache = {"dir": -1, "until": -1}


def plan_direction(head: int, length: int, danger: dict, blocked: set,
                   snap: dict, round_now: int, own: dict) -> int:
    if round_now < plan_cache["until"]:
        return plan_cache["dir"]
    want = bfs_target(head, danger, blocked, round_now, own, length)
    plan_cache["dir"] = want
    plan_cache["until"] = round_now + CFG["plan_every"]
    return want


def choose_move(head: int, length: int, danger: dict, blocked: set,
                snap: dict, round_now: int) -> Direction | None:
    """Safety first: filter lethal steps, then steer by target + space."""
    own = own_body_map(length)
    options = []
    for d in range(4):
        n = dest(head, d)
        if n < 0:
            continue
        if blocked_for_step(n, n in snap["pearls"], length):
            continue
        if n in blocked:  # any other dragon's part sits there now
            continue
        danger_here = danger.get(n, 0)
        space = flood_space(n, length, danger, blocked, own)
        score = (CFG["w_danger"] if danger_here >= 2 else CFG["w_soft"] * danger_here)
        score += CFG["w_space"] * space
        if space < length:
            score += CFG["trap_pen"]
        options.append((score, d, n))
    if not options:
        return None

    want = plan_direction(head, length, danger, blocked, snap, round_now, own)
    if want < 0 and seen_blocks:
        # nothing worth walking to in radius: steer toward the best fertility
        # block we know of (own sight or sonar gossip) beyond the horizon
        bs = 6
        nbx = (width + bs - 1) // bs
        hx, hy = head % width, head // width
        best_block, best_score = None, -1e18
        for block, fert in seen_blocks.items():
            bx = (block % nbx) * bs + bs // 2
            by = (block // nbx) * bs + bs // 2
            dx = abs(hx - bx)
            dy = abs(hy - by)
            dist = min(dx, width - dx) + min(dy, height - dy)
            score = fert * 3.0 - CFG["block_dist_pen"] * dist
            if score > best_score:
                best_block, best_score = (bx, by), score
        if best_block is not None and best_score > CFG["block_floor"]:
            bx, by = best_block
            dx = (bx - hx) % width
            dy = (by - hy) % height
            want = 1 if min(dx, width - dx) == dx and dx else (
                3 if dx <= width - dx else 3)
            want = (1 if dx <= width - dx else 3) if dx >= dy else (
                2 if dy <= height - dy else 0)
    spread_of = {}
    for aid, (acell, _ad, _alen, _arole, _arnd) in allies.items():
        if aid == my_id:
            continue
        ax, ay = acell % width, acell // width
        for _s, _d, n in options:
            dx = abs(n % width - ax)
            dy = abs(n // width - ay)
            dist = min(dx, width - dx) + min(dy, height - dy)
            spread_of[n] = max(spread_of.get(n, 0), min(dist, 12))
    best = None
    for score, d, n in options:
        total = score + (30.0 if d == want else 0.0) + CFG["w_spread"] * spread_of.get(n, 0)
        total += random.random() * 0.01
        if best is None or total > best[0]:
            best = (total, d)
    return DIRS[best[1]]


def emergency_move(head: int, length: int, blocked: set) -> Direction | None:
    """No safe option: any step that is neither kelp nor our own body.  Even
    our own tail tile is fatal (collision checks precede movement)."""
    fallback = None
    for d in range(4):
        n = dest(head, d)
        if n < 0 or blocked_for_step(n, False, length):
            continue
        if n not in blocked:
            return DIRS[d]
        if fallback is None:
            fallback = DIRS[d]
    return fallback


# =====================================================================
# STRATEGY
# =====================================================================
def want_split(length: int, units: int, round_now: int, danger_here: int) -> int:
    """Child size if we should split voluntarily now, else 0."""
    if units >= game.get_unit_limit() or length < CFG["split_len"]:
        return 0  # the child forms at our tail: combat is no reason to stall
    if round_now > CFG["late_round"] and units >= CFG["late_team_floor"]:
        return 0
    if round_now > CFG["grow_after"] and units >= CFG["grow_floor"]:
        return 0
    target = (CFG["early_team_target"] if round_now < CFG["scout_until"]
              else CFG["mid_team_target"])
    target = max(target, min(CFG["big_map_units"], n_cells // CFG["big_map_divisor"]))
    if units >= target:
        return 0
    if round_now < CFG["scout_until"]:
        return 2  # scout
    if round_now < CFG["hunter_until"]:
        return 3 if length >= 5 else 2  # hunter, but the parent must keep 2
    return 2


def strike(head: int, snap: dict) -> Direction | None:
    """Trade into an enemy head standing next to us: both heads die, theirs
    drops pearls for the team.  Worth it when they are clearly longer, when
    we are an expendable scout, or when we simply outnumber them."""
    length = ct.get_length()
    enemy_units = len({c for c, (t, _l) in enemies.items()
                       if game.get_round_num() - t < CFG["attack_fresh"]})
    for cell, _pid, is_ally, _will in snap["heads"]:
        if is_ally:
            continue
        for d in range(4):
            if dest(head, d) != cell:
                continue
            if (role == ROLE_S and CFG["scout_strikes"]
                    and snap["enemy_parts"] - length >= 4):
                return DIRS[d]
            if snap["enemy_parts"] - length >= CFG["hunter_trade_gap"]:
                return DIRS[d]
            if (enemy_units and ct.get_unit_count() >= enemy_units + CFG["strike_gap_units"]
                    and snap["enemy_parts"] >= length):
                return DIRS[d]
            return None
    return None


def execute_turn() -> None:
    round_now = game.get_round_num()
    length = ct.get_length()
    units = ct.get_unit_count()
    snap = fold_vision(round_now)
    head = snap["head_cell"] if snap["head_cell"] >= 0 else (
        trail[-1] if trail else 0)
    if not trail or trail[-1] != head:
        # one entry per actual move: split turns inject no duplicate, or the
        # body reconstruction (trail[-length:]) drifts off the real segments
        trail.append(head)
    if len(trail) > 256:
        del trail[:-256]
    visits[head] = min(255, visits[head] + 1)

    for value in ct.get_sonar_messages():
        got = unpack(value)
        if got:
            apply_packet(got[0], got[1], round_now)

    # fresh enemy sightings go on the radio; combat also invalidates the plan
    for cell, _pid, is_ally, _will in snap["heads"]:
        if not is_ally:
            plan_cache["until"] = -1
            if cell not in enemies or round_now - enemies[cell][0] >= 8:
                enemies[cell] = (round_now, 0)
                relay.append((K_ENEMY, enemy_payload(cell, 0, round_now)))

    # keep the per-turn dict lookups small: drop what has gone stale
    if round_now % 16 == 0:
        for cell in [c for c, w in spawn_at.items() if w < round_now - 60]:
            del spawn_at[cell]
        for cell in [c for c, (t, _l) in enemies.items() if round_now - t > 60]:
            del enemies[cell]
        for aid in [a for a, r in allies.items() if round_now - r[4] > 90]:
            del allies[aid]

    danger = threat_map(snap["heads"], snap["blocked"])
    acted = False
    child = want_split(length, units, round_now, danger.get(head, 0))
    if child and not ct.can_split(child):
        child = 0
    if child:
        out_split(child)
        acted = True
    else:
        move = strike(head, snap) or choose_move(
            head, length, danger, snap["blocked"], snap, round_now)
        if move is None:
            move = emergency_move(head, length, snap["blocked"])
        if move is None and length >= 4 and units < game.get_unit_limit():
            out_split(length - 2)  # cornered: shed most of the body
            acted = True
    if not acted:
        if move is not None:
            # a straight second step through clear, unthreatened tiles when
            # the far tile actually gains something: double speed toward
            # food, the frontier, or prey (fry's whole-game tempo trick)
            d = DIRS.index(move)
            nxt = cell_steps(head)[d]
            beyond = cell_steps(nxt)[d]
            gain = (beyond in snap["pearls"] or beyond in pearls
                    or not seen[beyond] if beyond >= 0 else False)
            hunted = any(round_now - t < CFG["attack_fresh"]
                         for t, _l in enemies.values())
            if ((gain or (role == ROLE_H and hunted)) and length >= 4
                    and nxt >= 0 and nxt not in snap["blocked"]
                    and beyond >= 0 and beyond not in snap["blocked"]
                    and danger.get(nxt, 0) == 0 and danger.get(beyond, 0) == 0
                    and not blocked_for_step(nxt, nxt in snap["pearls"], length)
                    and not blocked_for_step(beyond, beyond in snap["pearls"], length)):
                out_sprint(move)
                trail.append(nxt)
            else:
                out_move(move)
        else:  # every step is lethal; prefer one that is not kelp
            out_move(next((DIRS[d] for d in range(4)
                           if dest(head, d) >= 0), N))

    # ---- sonar out: relay first, then our own report and a fertility digest
    while relay and len(_sonar_out) < 3:
        _sonar_out.append((DIRS[len(_sonar_out)], pack(*relay.pop(0))))
    if round_now % CFG["self_every"] == 0:
        _sonar_out.append((DIRS[round_now & 3], pack(K_SELF, self_payload(round_now))))
    if trail and round_now % CFG["pearl_digest_every"] == 0:
        _sonar_out.append((DIRS[(round_now + 1) & 3], pack(*pearl_digest(round_now))))
    for direction, value in _sonar_out:
        out_sonar(direction, value)
    _sonar_out.clear()

    echoes = ct.get_sonar_echoes()
    out_indicator(f"{ROLE_NAME[role]}{length} u{units} e{echoes.enemy_head}")


def main() -> None:
    global ct, game, my_id, my_team, role, turns_done
    ct, game = unswbc.init()
    my_id, my_team = ct.get_id(), ct.get_team()
    setup()
    random.seed(my_id * 7919)
    while unswbc.update(ct, game):
        if game.get_round_num() <= 1:
            role = ROLE_G  # map-spawned dragon
        elif not trail:
            role = {2: ROLE_S, 3: ROLE_H}.get(ct.get_length(), ROLE_G)
        if turns_done == 0 and game.get_round_num() > 1:
            boot_turn()  # mid-game child: spend the boot turn on almost nothing
        else:
            execute_turn()
        turns_done += 1
        flush_turn()


if __name__ == "__main__":
    main()

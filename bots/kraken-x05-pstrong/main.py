"""kraken-v05-safety: v04-eval + subsystem S5 (threat & safety).

Hypothesis (docs/kraken-macro-spec.md): a probabilistic strike model with
initiative and trade pricing, a persistent doom map for cells that killed
allies, exit counting and traffic terms cut kraken's measured leak of
~100 body-crash and ~29 wall deaths per game, at equal unit volume.

Changes vs v04 (all weights in CFG):
- build_danger() now returns a threat COST field (expected loss in points)
  plus a hard threshold, replacing the binary lethal/soft levels.  An enemy
  head at distance k prices p_strike[k] x my value, scaled by initiative
  (enemies acting after me this round can react to my move) and by how
  much the mutual-kill trade favours them (my_len / their_len).
- Doom memory: an ally seen inside the inner 5x5 last round that is gone
  now died there; the death cell (w_doom) and its approaches (w_doom_adj)
  stay marked for doom_ttl rounds.
- Exit counting: destinations leaving 0/1 survivable continuations pay
  w_exit0/w_exit1.  Traffic: ally-adjacent and blocked-neighbour costs.
- Brawl mode discounts the whole threat field by brawl_threat_scale
  instead of using a flat -150.

Base: kraken-v04-eval.  Original v01 docstring follows.

kraken-v01-roles: role-based swarm on protocol 3, written from scratch.

Each dragon is its own process with a 7x7 window.  Everything beyond the
window lives in persistent memory: static terrain (kelp / portal pairings),
pearl beds with spawn predictions from observed countdowns, remembered
pearls, enemy sightings, and ally self-reports relayed over sonar.

Roles are fixed at creation time and encoded in the split size: a 2-segment
child is a scout (frontier + radar), a 3-segment child is a hunter (chases
sightings, sprint-strikes enemy heads), anything larger is a gatherer
(grows on pearls in safe fertile ground).  Map-spawned dragons are gatherers.

Sonar policy: ONE rotating directional sonar per turn.  Echo counts are
aggregated over all sonars sent, so a single cast is the only way to
attribute an echo to a direction - the cast doubles as a radar sweep and as
the gossip carrier.

Judge budget: one stdout write per turn (assembled here), a cheap boot turn
for mid-game split children, and capped searches.
"""

import os
import sys

# Local debugging: `touch /tmp/kraken-trace-on` before a non-sandbox run and
# every dragon writes a trace file under /tmp/ktrace/.  Never set on the judge.
DEBUG = "/tmp/ktrace/t" if os.path.exists("/tmp/kraken-trace-on") else ""


def trace(text):
    if DEBUG:
        with open("%s-id%d.log" % (DEBUG, my_id), "a") as fh:
            fh.write(text + "\n")

# =====================================================================
# CONFIG - every tunable lives here so parameter sweeps only touch this.
# =====================================================================
CFG = dict(
    # ---- split policy ----
    scout_until=110,        # children born before this round are scouts
    hunter_until=330,       # ... before this round are hunters, then none
    team_target_early=20,   # desired unit count while scouting
    team_target_mid=28,     # desired unit count while hunting
    split_len=4,            # min parent length for a voluntary split
    late_round=380,         # no voluntary splits after this round ...
    late_team_floor=6,      # ... unless the team has dropped below this
    # ---- big-map production (64x64 and up: elimination races, never stop) ----
    big_map_cells=3000,     # maps with more cells than this use big targets
    big_target_early=32,    # desired unit count while scouting on big maps
    big_target_mid=64,      # desired unit count while hunting on big maps
    big_late_target=48,     # keep replacing losses up to this after late_round
    growth_round=400,       # after this round on big maps: eat, don't split
    # ---- combat ----
    strike_steps=3,         # max sprint length when striking a head
    scout_trade=2,          # scout strikes if enemy len >= my len + this
    hunter_trade=0,         # hunter strikes if enemy len >= my len + this
    threat_soft=3,          # threat field extends to this many steps
    p_strike1=0.75,         # P(enemy strikes me | tile adjacent to its head)
    p_strike2=0.35,         # ... at 2 steps (sprint reach)
    p_strike3=0.15,         # ... at 3 steps
    p_newborn=0.5,          # P(a splittable enemy's newborn strikes me)
    w_danger_base=120.0,    # threat = p x (base + seg x my_len) x scalars
    w_danger_seg=60.0,      # points of value per body segment at risk
    ini_moved=0.85,         # threat scale: enemy already acted this round
    ini_notmoved=1.0,       # threat scale: enemy acts after me this round
    trade_min=0.35,         # clamp on my_len/their_len threat scaling
    trade_max=1.6,
    hard_frac=0.55,         # threat >= this fraction of my value = lethal
    brawl_threat_scale=0.2, # brawl mode discounts the whole threat field
    # ---- doom memory (cells that killed allies) ----
    doom_ttl=200,           # rounds a doom mark stays hot
    w_doom=500.0,           # cost of the exact cell an ally died on
    w_doom_adj=120.0,       # cost of cells adjacent to a death cell
    # ---- movement scoring ----
    w_exit0=-260.0,         # destination leaves no survivable continuation
    w_exit1=-70.0,          # destination leaves exactly one
    w_ally_move=8.0,        # soft cost next to an ally head (it may move)
    w_ally_adj=-12.0,       # per ally part adjacent to the destination
    w_crowd=-6.0,           # per blocked neighbour of the destination
    w_space=2.0,            # per reachable tile after the move
    space_slack=6,          # flood fill stops at length + this
    trap_pen=-350.0,        # reachable space smaller than our length
    w_pearl_here=40.0,      # pearl on the immediate destination
    w_compass=30.0,         # step agrees with the target search
    w_visit=-4.0,           # per past visit of the destination
    w_spread=1.5,           # per tile of distance from nearest ally head
    spread_cap=10,          # spread distance cap
    # ---- target search (BFS compass) ----
    bfs_cap=450,            # cells the target search may visit
    w_dist=-2.0,            # per BFS step
    w_pearl=110.0,          # remembered pearl
    w_spawn=30.0,           # predicted spawn, scaled by how soon
    spawn_horizon=25.0,     # rounds over which a spawn prediction decays
    w_frontier=10.0,        # cell bordering unknown terrain, gatherer
    w_frontier_scout=46.0,  # ... scout
    w_hunt=130.0,           # recent enemy sighting cell (hunters)
    hunt_decay=45.0,        # rounds over which a sighting cools off
    w_ray=55.0,             # cell on an enemy radar ray (hunters)
    ray_decay=30.0,         # rounds a radar ray stays hot
    pearl_stale=48,         # rounds after which a remembered pearl fades
    # ---- sonar gossip ----
    relay_ttl=2,            # hops a forwarded packet may still take
    relay_max=4,            # relay queue cap
)
# KBENCH-PARAMS-BEGIN
CFG.update({"p_strike1": 1.1, "p_strike2": 0.55, "p_strike3": 0.2})  # kbench variant params
# KBENCH-PARAMS-END
VISIT_SCORE = tuple(CFG["w_visit"] * min(i, 12) for i in range(256))

# =====================================================================
# LOW LEVEL IO - one write per turn, minimal parsing.
# =====================================================================
READ = sys.stdin.readline
_out = []


def emit(text):
    _out.append(text)


def flush_turn():
    _out.append("PROTOCOL 3")
    _out.append("ENDTURN")
    sys.stdout.write("\n".join(_out) + "\n")
    sys.stdout.flush()
    del _out[:]




def read_parts():
    """Next non-blank, non-comment line as tokens; [] at EOF."""
    while True:
        line = READ()
        if line == "":
            return []
        hash_at = line.find("#")
        if hash_at >= 0:
            line = line[:hash_at]
        parts = line.split()
        if parts:
            return parts


# =====================================================================
# STATE
# =====================================================================
W = H = NC = 0
my_id = -1
my_team = ""
unit_limit = 64
round_now = 0
my_len = 3
units = 1
facing = 0          # direction index N=0 E=1 S=2 W=3
head = 0            # our head cell
role = 0            # 0 gatherer, 1 hunter, 2 scout
boot_done = False   # a mid-game child spends turn one on almost nothing

DIR_CH = "NESW"

ek = bytearray()        # 2*NC edge kinds: 0 unknown 1 open 2 kelp 3 portal
epid = {}               # edge key -> portal id
pends = {}              # portal id -> [edge keys]
seen = bytearray()      # tile ever observed
fertile = bytearray()   # tile can spawn pearls
visits = bytearray()    # times our head stood here (cap 255)
NB = []                 # lazy neighbour table
dcache = []             # lazy per-cell destination table
unknown_edges = bytearray()  # count of unknown sides per cell
bfs_mark = []           # reusable BFS visit stamps
bfs_dist = []           # reusable BFS distances
bfs_first = bytearray() # reusable BFS first-step directions
bfs_stamp = 0

pearls = {}             # cell -> round last confirmed
spawn_at = {}           # cell -> round a pearl is expected
enemies = {}            # enemy id (or -cell-1 for gossip) -> (cell, round, len)
ally = {}               # ally id -> (cell, length, role, round)
ray_hot = {}            # cell -> round an enemy radar ray crossed it
doom = {}               # cell -> round an ally died here (exact death cell)
doom_n = {}             # cell -> round, approaches to a death cell
ally_direct = {}        # ally id -> (cell, round) seen with our own window
inner_now = set()       # inner 5x5 of this turn's window (death detection)
heads_allies_now = set()  # ally ids visible this turn

trail = []              # our head cells, oldest first; body = last my_len
radar = None            # (origin cell, dir) of last turn's sonar cast
echoes = (0, 0, 0, 0, 0)

relay_q = []            # packed uint64 waiting to go out
relayed = {}            # packet body -> round last relayed
portal_sent = set()
bed_sent = {}           # cell -> round last gossiped

# ---- brawl mode (small pearl-scarce combat maps: default_small) ----
pearl_ever = 0          # a live pearl was observed at least once
pearls_wit = 0          # total live-pearl sightings across all turns
portal_seen = 0         # any portal edge observed or gossiped
bed_count = 0           # distinct pearl beds seen
min_cd = 1 << 30        # smallest spawn countdown ever seen
brawl = 0               # once set: pure combat economy, harvest the dead

blocked = set()         # every other dragon's visible parts
ally_cells = set()      # visible ally parts (subset of blocked)
ally_heads = set()      # visible ally heads: stepping here kills TWO of ours
heads_seen = []         # (cell, id, is_ally) for visible heads
enemy_tails = []        # (tail-most cell, id) of splittable enemy dragons
elen = {}               # enemy id -> visible segment count this turn
my_parts = {}           # our own visible segments: cell -> facing index
head_edges = (".", ".", ".", ".")  # raw tokens for our head tile's sides


def setup():
    global ek, seen, fertile, visits, NB, dcache, NC
    global unknown_edges, bfs_mark, bfs_dist, bfs_first
    NC = W * H
    ek = bytearray(2 * NC)
    seen = bytearray(NC)
    fertile = bytearray(NC)
    visits = bytearray(NC)
    NB = [None] * NC
    dcache = [None] * NC
    unknown_edges = bytearray(b"\x04") * NC
    bfs_mark = [0] * NC
    bfs_dist = [0] * NC
    bfs_first = bytearray(NC)


def edge_now_known(k):
    """One edge left the unknown state; update the one/two cells it borders."""
    if k < NC:
        cells = (k, k - W if k >= W else k - W + NC)
    else:
        c = k - NC
        x = c % W
        cells = (c, c - 1 if x else c + W - 1)
    for cell in cells:
        if unknown_edges[cell]:
            unknown_edges[cell] -= 1


def nbr(c):
    got = NB[c]
    if got is None:
        x = c % W
        got = NB[c] = (
            c - W if c >= W else c - W + NC,
            c + 1 if x + 1 < W else c + 1 - W,
            c + W if c < NC - W else c + W - NC,
            c - 1 if x else c - 1 + W,
        )
    return got


def ekey(c, d):
    """Canonical key of the edge on side d of cell c (2*NC space)."""
    x = c % W
    if d == 0:
        return c
    if d == 2:
        return c + W if c < NC - W else c + W - NC
    if d == 3:
        return NC + c
    return NC + (c + 1 if x + 1 < W else c + 1 - W)


def dest_raw(c, d):
    """Cell reached leaving c towards d; -1 blocked, -2 unknown edge."""
    if d == 0:
        k = c
    elif d == 2:
        k = c + W if c < NC - W else c + W - NC
    elif d == 3:
        k = NC + c
    else:
        x = c % W
        k = NC + (c + 1 if x + 1 < W else c + 1 - W)
    t = ek[k]
    if t == 1:
        return nbr(c)[d]
    if t == 0:
        return -2
    if t == 2:
        return -1
    ends = pends.get(epid[k])
    if not ends or len(ends) < 2:
        return -1
    pk = ends[0] if ends[1] == k else ends[1]
    if pk >= NC:                # partner is a vertical edge
        px = (pk - NC) % W
        py = (pk - NC) // W
        if d == 1:              # heading east: emerge east of the partner
            return py * W + px
        return py * W + (px - 1 if px else W - 1)
    px = pk % W
    py = pk // W
    if d == 2:                  # heading south: emerge south of the partner
        return pk
    return (py - 1 if py else H - 1) * W + px


def dest(c, d=None):
    got = dcache[c]
    if got is not None:
        return got if d is None else got[d]
    if d is not None:
        return dest_raw(c, d)
    got = (dest_raw(c, 0), dest_raw(c, 1), dest_raw(c, 2), dest_raw(c, 3))
    # only cache when all four edges are known: edge values never change
    # once seen, but an unknown->known transition must not stay poisoned
    if not unknown_edges[c]:
        dcache[c] = got
    return got


def invalidate_portal_edge(k):
    """Drop cached destinations only for cells touching a newly paired portal."""
    if k < NC:
        cells = (k, k - W if k >= W else k - W + NC)
    else:
        c = k - NC
        x = c % W
        cells = (c, c - 1 if x else c + W - 1)
    for cell in cells:
        dcache[cell] = None


# =====================================================================
# SONAR PACKETS (uint64: tag 12 | kind 4 | payload 48)
# =====================================================================
MAGIC = 0x3A9
K_SELF, K_ENEMY, K_PORTAL, K_BED = 1, 2, 3, 4
TTL_SHIFT = 46


def pack(kind, payload):
    body = (kind << 48) | payload
    tag = MAGIC
    for shift in (0, 13, 26, 39):
        tag = (tag * 131 + ((body >> shift) & 0x1FFF)) & 0xFFF
    return (tag << 52) | body


def unpack(value):
    tag = value >> 52
    body = value & ((1 << 52) - 1)
    check = MAGIC
    for shift in (0, 13, 26, 39):
        check = (check * 131 + ((body >> shift) & 0x1FFF)) & 0xFFF
    if tag != check:
        return None
    return body >> 48, body & ((1 << 48) - 1)


def self_payload():
    return (((my_id & 0xFF) << 22) | ((head & 0xFFF) << 10)
            | ((my_len & 0xFF) << 2) | (role & 3))


def enemy_payload(cell, len_est):
    return ((2 << TTL_SHIFT) | ((cell & 0xFFF) << 8) | (len_est & 0xFF))


def portal_payload(pid):
    ends = pends.get(pid) or []
    k = ends[0]
    orient = 1 if k >= NC else 0
    cell = (k - NC) if orient else k
    return ((2 << TTL_SHIFT) | ((pid & 0xFF) << 14) | (orient << 13)
            | (cell & 0x1FFF))


def bed_payload(cell):
    when = spawn_at.get(cell, 0) & 0x1FF
    return (2 << TTL_SHIFT) | ((cell & 0xFFF) << 9) | when


def apply_packet(kind, payload):
    global portal_seen
    if kind == K_SELF:
        pid = (payload >> 22) & 0xFF
        if pid != (my_id & 0xFF):
            ally[pid] = ((payload >> 10) & 0xFFF, (payload >> 2) & 0xFF,
                         payload & 3, round_now)
        return
    ttl = payload >> TTL_SHIFT
    if kind == K_ENEMY:
        cell = (payload >> 8) & 0xFFF
        if cell < NC:
            enemies[-cell - 1] = (cell, round_now, payload & 0xFF)
    elif kind == K_PORTAL:
        pid = (payload >> 14) & 0xFF
        orient = (payload >> 13) & 1
        cell = payload & 0x1FFF
        if cell < NC:
            k = NC + cell if orient else cell
            if ek[k] == 0:
                ek[k] = 3
                edge_now_known(k)
                epid[k] = pid
                portal_seen = 1
                if DEBUG:
                    trace("gossip-portal k%d pid%d (round %d)" % (k, pid, round_now))
            ends = pends.setdefault(pid, [])
            if k not in ends and len(ends) < 2:
                ends.append(k)
                if len(ends) == 2:
                    invalidate_portal_edge(ends[0])
                    invalidate_portal_edge(ends[1])
    elif kind == K_BED:
        cell = (payload >> 9) & 0xFFF
        when = payload & 0x1FF
        if cell < NC and not seen[cell]:
            fertile[cell] = 1
            if when:
                spawn_at.setdefault(cell, when)
    # forward with one less hop
    if ttl > 1 and len(relay_q) < CFG["relay_max"]:
        key = (kind << 48) | payload
        if relayed.get(key, -99) < round_now - 25:
            relayed[key] = round_now
            relay_q.append(pack(kind, payload - (1 << TTL_SHIFT)))


# =====================================================================
# PERCEIVE
# =====================================================================
def fold_tiles(tile_lines):
    global head, pearl_ever, pearls_wit, bed_count, min_cd
    inner_now.clear()
    for i in range(49):
        parts = tile_lines[i]
        x = int(parts[0])
        y = int(parts[1])
        cell = y * W + x
        if i == 24:
            head = cell
        if 1 <= i // 7 <= 5 and 1 <= i % 7 <= 5:
            inner_now.add(cell)  # inner 5x5: a 1-step mover cannot leave it
        seen[cell] = 1
        pearl = parts[2] == "1"
        pt = int(parts[3])
        if pearl:
            pearl_ever = 1
            pearls_wit += 1
        if pt >= 0:
            if pt < min_cd:
                min_cd = pt
            if not fertile[cell]:
                bed_count += 1
                fertile[cell] = 1
                if len(relay_q) < CFG["relay_max"] and \
                        bed_sent.get(cell, -99) < round_now - 60:
                    bed_sent[cell] = round_now
                    relay_q.append(pack(K_BED, bed_payload(cell)))
            if not pearl:
                spawn_at[cell] = round_now + max(pt, 1)
        if pearl:
            pearls[cell] = round_now
        elif cell in pearls:
            del pearls[cell]


def fold_bodies(body_lines):
    blocked.clear()
    ally_cells.clear()
    ally_heads.clear()
    heads_allies_now.clear()
    del heads_seen[:]
    del enemy_tails[:]
    elen.clear()
    my_parts.clear()
    foe_parts = {}
    for parts in body_lines:
        pid = int(parts[1])
        cell = int(parts[3]) * W + int(parts[2])
        is_head = parts[5] == "1"
        if pid == my_id:
            if not is_head:
                my_parts[cell] = DIR_CH.index(parts[4][0])
            pearls.pop(cell, None)
            spawn_at.pop(cell, None)
            continue
        blocked.add(cell)
        pearls.pop(cell, None)
        spawn_at.pop(cell, None)
        is_ally = parts[0] == my_team
        if is_ally:
            ally_cells.add(cell)
        else:
            elen[pid] = elen.get(pid, 0) + 1
            foe_parts.setdefault(pid, {})[cell] = DIR_CH.index(parts[4][0])
        if is_head:
            heads_seen.append((cell, pid, is_ally))
            if is_ally:
                ally_heads.add(cell)
                heads_allies_now.add(pid)
                ally_direct[pid] = (cell, round_now)
    # A split child is born at the parent's tail and acts the same round.
    # fry-style parents are length 4-6 and often only partially visible, so
    # any enemy showing 3+ segments may be splittable: reserve the
    # neighbourhood of its tail-most visible segment.
    for pid, parts in foe_parts.items():
        if elen.get(pid, 0) < 3:
            continue
        cells = set(parts)
        ends = [cell for cell, d in parts.items() if nbr(cell)[d] not in cells]
        if ends:
            enemy_tails.append((ends[0], pid))


def learn_edge(k, token):
    global portal_seen
    if token == "w":
        if DEBUG and ek[k] in (1, 3):
            trace("EDGE-CONTRADICTION k%d was %d now kelp (round %d)" % (k, ek[k], round_now))
        if ek[k] == 0:
            edge_now_known(k)
        ek[k] = 2
        return
    if token == ".":
        if DEBUG and ek[k] in (2, 3):
            trace("EDGE-CONTRADICTION k%d was %d now open (round %d)" % (k, ek[k], round_now))
        if ek[k] == 0:
            ek[k] = 1
            edge_now_known(k)
        return
    pid = int(token)
    if DEBUG and ek[k] == 2:
        trace("EDGE-CONTRADICTION k%d was kelp now portal %d (round %d)" % (k, pid, round_now))
    if ek[k] == 3 and epid.get(k) != pid:
        if DEBUG:
            trace("EDGE-CONTRADICTION k%d portal %d->%d (round %d)" % (k, epid.get(k, -9), pid, round_now))
        pass
    if ek[k] == 0:
        edge_now_known(k)
    ek[k] = 3
    epid[k] = pid
    portal_seen = 1
    ends = pends.setdefault(pid, [])
    if k not in ends and len(ends) < 2:
        ends.append(k)
        if len(ends) == 2:
            invalidate_portal_edge(ends[0])
            invalidate_portal_edge(ends[1])
    if pid not in portal_sent:
        portal_sent.add(pid)
        relay_q.append(pack(K_PORTAL, portal_payload(pid)))


def fold_edges(rows_h, rows_v):
    """rows_h: 8 rows x 7 cols of horizontal edges; rows_v: 7 x 8 vertical."""
    global head_edges
    hx = head % W
    hy = head // W
    # ground truth for the head tile's own four sides, straight from the wire
    head_edges = (rows_h[3][3], rows_v[3][4], rows_h[4][3], rows_v[3][3])
    for r in range(8):
        y = hy - 3 + r
        if y < 0:
            y += H
        elif y >= H:
            y -= H
        base = y * W
        row = rows_h[r]
        for c in range(7):
            x = hx - 3 + c
            if x < 0:
                x += W
            elif x >= W:
                x -= W
            learn_edge(base + x, row[c])
    for r in range(7):
        y = hy - 3 + r
        if y < 0:
            y += H
        elif y >= H:
            y -= H
        base = NC + y * W
        row = rows_v[r]
        for c in range(8):
            x = hx - 3 + c
            if x < 0:
                x += W
            elif x >= W:
                x -= W
            learn_edge(base + x, row[c])


def seed_trail():
    """First turn: rebuild our body from visible own segments, tail first."""
    if trail:
        return
    chain = [head]
    while len(chain) < my_len:
        cur = chain[-1]
        nxt = -1
        for cell, d in my_parts.items():
            if cell in chain:
                continue
            step = dest(cell, d)
            if step < 0:
                step = nbr(cell)[d]
            if step == cur:
                nxt = cell
                break
        if nxt < 0:
            break
        chain.append(nxt)
    trail.extend(reversed(chain[1:]))


# =====================================================================
# DANGER
# =====================================================================
def build_danger():
    """Threat field: cell -> expected loss in points, plus the hard line.

    Probabilistic strike model: an enemy head at BFS distance k prices
    p_strike[k] x my value (base + seg x my_len), scaled by initiative
    (an enemy acting after me this round can react to my move; one that
    already moved only threatens me next round) and by how much the
    mutual-kill trade favours it (my_len / their_len, clamped).  Cells at
    or above `hard` count as lethal for space and search purposes.
    Splittable enemies add a newborn-strike term around the tail.
    """
    threat = {}
    value = CFG["w_danger_base"] + CFG["w_danger_seg"] * my_len
    hard = CFG["hard_frac"] * value
    p1 = CFG["p_strike1"]
    p2 = CFG["p_strike2"]
    p3 = CFG["p_strike3"]
    soft_cap = CFG["threat_soft"]
    ini_m = CFG["ini_moved"]
    ini_n = CFG["ini_notmoved"]
    tmin = CFG["trade_min"]
    tmax = CFG["trade_max"]
    w_ally = CFG["w_ally_move"]
    for cell, pid, is_ally in heads_seen:
        if is_ally:
            for n in dest(cell):
                if n >= 0 and threat.get(n, 0.0) < w_ally:
                    threat[n] = w_ally
            continue
        their = elen.get(pid, 2)
        scale = my_len / (their if their > 2 else 2.0)
        if scale < tmin:
            scale = tmin
        elif scale > tmax:
            scale = tmax
        unit = value * scale * (ini_m if pid < my_id else ini_n)
        layer = [cell]
        dist = {cell: 0}
        while layer:
            nxt = []
            for c in layer:
                d0 = dist[c]
                if d0 >= soft_cap:
                    continue
                for n in dest(c):
                    if n < 0 or n in dist or n in blocked:
                        continue
                    dn = d0 + 1
                    dist[n] = dn
                    p = p1 if dn == 1 else (p2 if dn == 2 else p3)
                    threat[n] = threat.get(n, 0.0) + p * unit
                    nxt.append(n)
            layer = nxt
    nb = CFG["p_newborn"] * value
    for cell, pid in enemy_tails:
        # a split child appears here and can immediately strike one step
        add = nb * (ini_m if pid < my_id else ini_n)
        for n in dest(cell):
            if n >= 0:
                threat[n] = threat.get(n, 0.0) + add
    return threat, hard


# =====================================================================
# MOVEMENT
# =====================================================================
def own_map():
    """cell -> steps back from our head (1 = head) over the current body."""
    own = {}
    for j in range(1, min(my_len, len(trail)) + 1):
        c = trail[-j]
        if c not in own:
            own[c] = j
    return own


def flood_space(start, threat, own, hard):
    cap = my_len + CFG["space_slack"]
    got = {start: 0}
    queue = [start]
    qi = 0
    while qi < len(queue) and len(got) < cap:
        cell = queue[qi]
        qi += 1
        depth = got[cell] + 1
        for n in dest(cell):
            if n < 0 or n in got or n in blocked or threat.get(n, 0.0) >= hard:
                continue
            j = own.get(n)
            if j is not None and depth + j <= my_len + 1:
                continue
            got[n] = depth
            queue.append(n)
    return len(got)


def borders_unknown(cell):
    for d in range(4):
        if ek[ekey(cell, d)] == 0:
            return True
    return False


def bfs_compass(threat, own, hard):
    """Capped BFS scoring targets in place; returns the best first step."""
    global bfs_stamp
    cap = CFG["bfs_cap"] if NC > CFG["bfs_cap"] else NC
    if NC > CFG["big_map_cells"]:
        cap = 500  # big rich maps: longer sightlines, but stay judge-safe
    bfs_stamp += 1
    stamp = bfs_stamp
    dist = bfs_dist
    mark = bfs_mark
    first = bfs_first
    mark[head] = stamp
    dist[head] = 0
    queue = [head]
    qlen = 1
    qi = 0
    _qappend = queue.append
    best_dir = -1
    best_score = -1e18
    frontier_w = CFG["w_frontier_scout"] if role == 2 else CFG["w_frontier"]
    hunt = role == 1
    w_dist = CFG["w_dist"]
    w_spawn = CFG["w_spawn"]
    horizon = CFG["spawn_horizon"]
    # locals: the inner loop is the bot's hottest code under the judge meter
    _dest = dest
    _dget = threat.get
    _oget = own.get
    _sget = spawn_at.get
    _fertile = fertile
    _visits = visits
    _vscore = VISIT_SCORE
    _pearls = pearls
    _blocked = blocked
    _unknown = unknown_edges
    _rget = ray_hot.get
    w_pearl = CFG["w_pearl"]
    w_ray = CFG["w_ray"]
    ray_decay = CFG["ray_decay"]
    # a cell's score can never beat best_score once steps alone cost more
    # than every bonus combined (pearl + frontier + spawn + ray)
    max_bonus = w_pearl + frontier_w + w_spawn + (w_ray if hunt else 0.0)
    while qi < qlen and qlen < cap:
        cell = queue[qi]
        qi += 1
        steps_to = dist[cell] + 1
        step_cost = w_dist * steps_to
        if step_cost + max_bonus <= best_score:
            continue  # this subtree cannot hold a winning target
        ds = _dest(cell)
        for d in range(4):
            n = ds[d]
            if n < 0 or mark[n] == stamp or n in _blocked or _dget(n, 0.0) >= hard:
                continue
            if step_cost + max_bonus <= best_score:
                continue  # cannot win itself, and cannot ancestor a winner
            j = _oget(n)
            if j is not None and steps_to + j <= my_len + 1:
                continue
            mark[n] = stamp
            dist[n] = steps_to
            first[n] = d if cell == head else first[cell]
            _qappend(n)
            qlen += 1
            score = step_cost + _vscore[_visits[n]]
            if n in _pearls:
                score += w_pearl
            when = _sget(n)
            if when is not None and _fertile[n]:
                if when <= round_now:
                    score += w_spawn
                else:
                    lag = when - round_now
                    if lag < horizon:
                        score += w_spawn * (1.0 - lag / horizon)
            if frontier_w and _unknown[n]:
                score += frontier_w
            if hunt:
                hot = _rget(n)
                if hot is not None:
                    age = round_now - hot
                    if age < ray_decay:
                        score += w_ray * (1.0 - age / ray_decay)
            if score > best_score:
                best_score = score
                best_dir = first[n]
    if hunt:
        # sighting cells pull even if their raw tile score was mediocre
        w_hunt = CFG["w_hunt"]
        decay = CFG["hunt_decay"]
        for pid, (cell, when, _l) in enemies.items():
            age = round_now - when
            if mark[cell] == stamp and age < decay:
                steps = dist[cell]
                if 0 < steps:
                    score = w_hunt * (1.0 - age / decay) + w_dist * steps
                    if score > best_score:
                        best_score = score
                        best_dir = first[cell]
    return best_dir


def nearest_ally_dist(cell, axy):
    best = 99
    x = cell % W
    y = cell // W
    for ax, ay in axy:
        dx = abs(x - ax)
        dy = abs(y - ay)
        d = min(dx, W - dx) + min(dy, H - dy)
        if d < best:
            best = d
    return best


def choose_move(threat, hard, own, compass, axy):
    options = []
    ds = dest(head)
    w_doom = CFG["w_doom"]
    w_doom_adj = CFG["w_doom_adj"]
    doom_ttl = CFG["doom_ttl"]
    for d in range(4):
        n = ds[d]
        if n < 0 or n in blocked:
            continue
        if n in own:  # collision precedes tail movement: always fatal
            continue
        cost = threat.get(n, 0.0)
        dm = doom.get(n)
        if dm is not None and round_now - dm < doom_ttl:
            cost += w_doom  # an ally died on this exact cell
        if brawl:
            # strikes are mutual kills anyway: a threatened tile only costs
            # us if the enemy chooses to trade, and the corpse pearls feed
            # the swarm.  Push hard, harvest hard.
            score = -CFG["brawl_threat_scale"] * cost
        else:
            score = -cost
        # exit counting and traffic: how does the destination breathe?
        exits = 0
        crowd = 0
        for m in dest(n):
            if m < 0:
                continue
            if m in blocked:
                crowd += 1
                if m in ally_cells:
                    score += CFG["w_ally_adj"]
                continue
            j = own.get(m)
            if j is not None and 2 + j <= my_len + 2:
                continue  # still body when we would arrive (pearl slack)
            if threat.get(m, 0.0) >= hard:
                continue
            exits += 1
        if exits == 0:
            score += CFG["w_exit0"]
        elif exits == 1:
            score += CFG["w_exit1"]
        score += CFG["w_crowd"] * crowd
        dm = doom_n.get(n)
        if dm is not None and round_now - dm < doom_ttl:
            score -= w_doom_adj  # approach to a cell that killed an ally
        space = flood_space(n, threat, own, hard)
        score += CFG["w_space"] * space
        if space < my_len:
            score += CFG["trap_pen"] * (0.3 if brawl else 1.0)
        if n in pearls:
            score += CFG["w_pearl_here"] * (5.0 if brawl else 1.0)
        if d == compass:
            score += CFG["w_compass"]
        score += VISIT_SCORE[visits[n]]
        spread = nearest_ally_dist(n, axy)
        if spread < 99:
            w_sp = (-1.5 if NC <= 300 else -3.0) if brawl else CFG["w_spread"]
            score += w_sp * min(spread, CFG["spread_cap"])
        score += ((my_id * 31 + round_now * 7 + d * 13) % 10) * 0.01
        options.append((score, d))
    if not options:
        return -1
    options.sort(reverse=True)
    if threat.get(ds[options[0][1]], 0.0) >= hard and len(options) > 1:
        # the favourite is likely lethal; take the best non-lethal step
        for score, d in options:
            if threat.get(ds[d], 0.0) < hard:
                return d
    return options[0][1]


def emit_move(path):
    """Emit a MOVE and commit every stepped cell to the trail.  If a step
    kills us the process ends anyway; survivors keep an exact body model."""
    cell = head
    for d in path:
        nxt = dest(cell, d)
        if nxt < 0:
            break  # cannot happen for checked paths
        cell = nxt
        trail.append(cell)
    emit("MOVE " + "".join(DIR_CH[d] for d in path))


def escape_path(threat, own, hard):
    """A sprint of 2-3 steps to a safe tile, when every 1-step move is
    threatened.  Own-body margin has one extra tile of slack to stay safe
    even if we eat a pearl en route.  Returns a direction list or None."""
    max_steps = min(my_len - 1, CFG["strike_steps"])
    if max_steps < 2:
        return None
    best = None
    best_key = None
    prev = {}
    depths = {head: 0}
    queue = [head]
    qi = 0
    while qi < len(queue):
        cell = queue[qi]
        qi += 1
        depth = depths[cell]
        if depth >= max_steps:
            continue
        for d, n in enumerate(dest(cell)):
            if n < 0 or n in blocked or n in depths:
                continue
            nd = depth + 1
            j = own.get(n)
            if j is not None and nd + j <= my_len + 2:
                continue
            depths[n] = nd
            prev[n] = (d, cell)
            queue.append(n)
            if nd >= 2:
                t = threat.get(n, 0.0)
                if t < hard:
                    space = flood_space(n, threat, own, hard)
                    key = (0 if t < hard * 0.35 else 1, -space, nd)
                    if best_key is None or key < best_key:
                        best_key = key
                        best = n
    if best is None:
        return None
    path = []
    cur = best
    while cur != head:
        d, cur = prev[cur]
        path.append(d)
    path.reverse()
    return path


def strike_path():
    """Shortest safe sprint onto a visible enemy head, if worth trading.

    Stepping onto the tile an enemy head currently occupies kills both
    dragons regardless of turn order, and our MOVE resolves atomically,
    so the target cannot dodge.  Intermediate tiles must be clear now.
    """
    want = []
    desperate = units <= 2
    endgame = round_now > CFG["growth_round"]
    for cell, pid, is_ally in heads_seen:
        if is_ally:
            continue
        their = elen.get(pid, 2)
        margin = CFG["scout_trade"] if role == 2 else CFG["hunter_trade"]
        if not desperate:
            if brawl:
                # dead dragons are the only pearl income: trade unless we
                # are strictly longer by 2+ (don't waste length on stubs)
                if their < my_len - 1:
                    continue
            elif endgame:
                # length race: a mutual kill only pays if they are longer
                if their <= my_len:
                    continue
            elif role == 0:
                continue  # gatherers keep growing; endgame they fight too
            elif their < my_len + margin:
                continue
        want.append(cell)
    if not want:
        return None
    max_steps = min(my_len - 1, CFG["strike_steps"])
    if max_steps < 1:
        return None
    own = own_map()
    prev = {}
    depths = {head: 0}
    queue = [head]
    qi = 0
    while qi < len(queue):
        cell = queue[qi]
        qi += 1
        depth = depths[cell]
        if depth >= max_steps:
            continue
        for d, n in enumerate(dest(cell)):
            if n < 0:
                continue
            nd = depth + 1
            if n in want:
                path = [d]
                cur = cell
                while cur != head:
                    pd, cur = prev[cur]
                    path.append(pd)
                path.reverse()
                return path
            if n in blocked or n in depths:
                continue
            j = own.get(n)
            if j is not None and nd + j <= my_len + 1:
                continue
            depths[n] = nd
            prev[n] = (d, cell)
            queue.append(n)
    return None


def emergency_step():
    """Every option looks lethal: pick the least bad non-kelp step.  Never
    step onto an ally - that kills TWO of ours.  Ranking: open cell, then
    an enemy part (a head trades), then an unpaired portal dive, and only
    then an ally body.  An ally head is worse than standing still."""
    fallback = -1
    ally_fb = -1
    portal = -1
    own = own_map()
    for d, n in enumerate(dest(head)):
        if n == -2 or n in own:
            continue
        if n < 0:
            if ek[ekey(head, d)] == 3:
                portal = d  # unpaired portal: unknown but open edge
            continue
        if n not in blocked:
            return d
        if n in ally_heads:
            continue  # stepping here kills two of ours: never an option
        if n in ally_cells:
            if ally_fb < 0:
                ally_fb = d
        elif fallback < 0:
            fallback = d
    if fallback >= 0:
        return fallback
    if portal >= 0:
        return portal
    return ally_fb  # -1 when even that is impossible: caller splits/sits


def portal_dive():
    """Direction of an adjacent unpaired portal, or -1."""
    for d in range(4):
        if ek[ekey(head, d)] == 3 and dest(head, d) < 0:
            return d
    return -1


# =====================================================================
# STRATEGY
# =====================================================================
def want_split(danger_here):
    if units >= unit_limit or my_len < CFG["split_len"] or not boot_done:
        return 0
    big = NC > CFG["big_map_cells"]
    if big:
        t_early = CFG["big_target_early"]
        t_mid = CFG["big_target_mid"]
        t_late = CFG["big_late_target"]
    else:
        t_early = CFG["team_target_early"]
        # fry never caps below the unit limit and wins numbers wars on
        # medium-large maps; scale our ceiling with room to breathe
        t_mid = max(CFG["team_target_mid"], min(64, NC // 50))
        t_late = CFG["late_team_floor"]
    if round_now > CFG["late_round"]:
        if not big:
            return 0
        if round_now > CFG["growth_round"] and units >= CFG["late_team_floor"]:
            return 0  # length race: length in the body beats heads on the map
        if units >= t_late:
            return 0
        return 3 if my_len >= 5 else 2
    if round_now < CFG["scout_until"]:
        if units >= t_early:
            return 0
        return 2
    if round_now < CFG["hunter_until"] or big:
        if units >= t_mid:
            return 0
        return 3 if my_len >= 5 else 2
    return 0


# =====================================================================
# SONAR OUT
# =====================================================================
def send_sonar():
    global radar
    d = round_now & 3
    if relay_q:
        value = relay_q.pop(0)
    else:
        value = pack(K_SELF, self_payload())
    emit("SONAR %s %d" % (DIR_CH[d], value))
    radar = (head, d)


def handle_echoes():
    _kelp, _a, _ah, enemy, eh = echoes
    if radar is None or not (enemy or eh):
        return
    origin, d = radar
    cell = origin
    for _ in range(W + H):
        n = dest(cell, d)
        if n < 0:
            break
        ray_hot[n] = round_now
        cell = n
    if len(ray_hot) > 4000:
        for c in [c for c, t in ray_hot.items()
                  if round_now - t > CFG["ray_decay"]]:
            del ray_hot[c]


# =====================================================================
# TURN
# =====================================================================
def boot_turn():
    """Mid-game child's first turn: interpreter boot ate the budget, so just
    take the safest passable step and say hello."""
    seed_trail()
    trail.append(head)  # the boot move's origin stays a body segment
    best_d = -1
    best_score = -1e9
    for d, n in enumerate(dest(head)):
        if n < 0 or n in blocked or n in my_parts:
            continue
        score = 0.0
        if d == facing:
            score += 0.5
        if n in pearls:
            score += 1.0
        for m in dest(n):
            if m >= 0 and m in blocked:
                score -= 2.0
        if score > best_score:
            best_score = score
            best_d = d
    if best_d < 0:
        best_d = portal_dive()
    if best_d < 0:
        best_d = facing
        if dest(head, facing) in ally_heads:
            for d, n in enumerate(dest(head)):
                if n not in ally_heads:
                    best_d = d  # die alone rather than kill an ally
                    break
    emit("MOVE " + DIR_CH[best_d])
    send_sonar()


def take_turn():
    seed_trail()
    if not trail or trail[-1] != head:
        trail.append(head)
    if len(trail) > 600:
        del trail[:-600]
    visits[head] = min(255, visits[head] + 1)

    # fresh enemy sightings update memory and go on the radio
    for cell, pid, is_ally in heads_seen:
        if not is_ally:
            enemies[pid] = (cell, round_now, elen.get(pid, 2))
            if len(relay_q) < CFG["relay_max"]:
                relay_q.append(pack(K_ENEMY, enemy_payload(cell, elen.get(pid, 2))))

    # prune stale memory
    if round_now % 16 == 0:
        for c in [c for c, r in pearls.items() if round_now - r > CFG["pearl_stale"]]:
            del pearls[c]
        for c in [c for c, w in spawn_at.items() if w < round_now - 60]:
            del spawn_at[c]
        for p in [p for p, v in enemies.items() if round_now - v[1] > 60]:
            del enemies[p]
        for p in [p for p, v in ally.items() if round_now - v[3] > 90]:
            del ally[p]
        for c in [c for c, t in ray_hot.items() if round_now - t > CFG["ray_decay"]]:
            del ray_hot[c]
        for c in [c for c, t in doom.items() if round_now - t > CFG["doom_ttl"]]:
            del doom[c]
        for c in [c for c, t in doom_n.items() if round_now - t > CFG["doom_ttl"]]:
            del doom_n[c]

    # doom memory: an ally whose head was inside our inner 5x5 last round
    # and is nowhere to be seen now died there; mark the cell for doom_ttl
    for pid, (cell, when) in list(ally_direct.items()):
        if when <= round_now - 2:
            del ally_direct[pid]
        elif when == round_now - 1:
            if pid not in heads_allies_now and cell in inner_now:
                doom[cell] = round_now
                for m in dest(cell):
                    if m >= 0:
                        doom_n[m] = round_now
            del ally_direct[pid]

    threat, hard = build_danger()
    own = own_map()

    global brawl
    if not brawl and round_now >= 30 and NC <= 600 and not portal_seen \
            and bed_count >= 20 and pearls_wit * 20 <= bed_count:
        brawl = 1
        trace("BRAWL MODE r%d beds=%d wit=%d" % (round_now, bed_count, pearls_wit))

    child = want_split(threat.get(head, 0.0))
    if child and my_len - child >= 2 and units < unit_limit:
        emit("SPLIT %d" % child)
        send_sonar()
        return

    path = strike_path()
    if path:
        emit_move(path)
        send_sonar()
        return

    compass = bfs_compass(threat, own, hard)
    axy = [(c % W, c // W) for c, _l, _r, _w in ally.values()]
    move = choose_move(threat, hard, own, compass, axy)
    via = "choose"
    if move < 0 or (not brawl and threat.get(dest(head, move), 0.0) >= hard):
        esc = escape_path(threat, own, hard)
        if esc:
            emit_move(esc)
            send_sonar()
            return
    if move < 0:
        move = emergency_step()
        via = "emergency"
    if move < 0:
        if my_len >= 4 and units < unit_limit:
            emit("SPLIT %d" % (my_len - 2))  # cornered: shed the body
            send_sonar()
            return
        move = -1
        for d, n in enumerate(dest(head)):
            if n >= 0 and n not in own and n not in blocked:
                move = d
                break
        if move < 0:
            for d, n in enumerate(dest(head)):
                if n >= 0 and n in ally_cells and n not in ally_heads:
                    move = d  # die alone rather than take an ally with us
                    break
        if move < 0:
            move = facing
            if dest(head, facing) in ally_heads:
                for d, n in enumerate(dest(head)):
                    if n not in ally_heads:
                        move = d  # die alone on kelp/own body, spare the ally
                        break
        via = "facing-fallback"
    if DEBUG:
        n = dest(head, move)
        if n < 0 or n in blocked or n in own:
            trace("ILLEGAL-CHOICE r%d via=%s d%d n%d" % (round_now, via, move, n))
    if DEBUG:
        k = ekey(head, move)
        if ek[k] == 3:
            trace("r%d PORTAL-STEP k%d -> %d" % (round_now, k, dest(head, move)))
        trace("r%d h%d len%d mv%s dg%.0f he=%s ek=%d%d%d%d body=%s eh=%s blk=%s" % (
            round_now, head, my_len, DIR_CH[move], threat.get(dest(head, move), 0.0),
            "/".join(head_edges),
            ek[ekey(head, 0)], ek[ekey(head, 1)], ek[ekey(head, 2)], ek[ekey(head, 3)],
            ",".join(str(c) for c in trail[-my_len:]),
            ";".join("%d@%d%s" % (pid, c, "A" if al else "E")
                     for c, pid, al in heads_seen),
            ",".join(str(c) for c in sorted(blocked))))
    emit("MOVE " + DIR_CH[move])
    send_sonar()


# =====================================================================
# MAIN
# =====================================================================
def main():
    global W, H, my_id, my_team, unit_limit, round_now, my_len, units
    global facing, echoes, boot_done, role

    parts = read_parts()
    if not parts:
        return
    my_id = int(parts[1])
    my_team = read_parts()[1]
    dims = read_parts()
    W = int(dims[1])
    H = int(dims[2])
    unit_limit = int(read_parts()[1])
    setup()

    while True:
        parts = read_parts()
        if not parts or parts[0] == "ENDGAME":
            return
        round_now = int(parts[1])
        facing = DIR_CH.index(read_parts()[1][0])
        my_len = int(read_parts()[1])
        units = int(read_parts()[1])
        n_msg = int(read_parts()[1])
        for _ in range(n_msg):
            got = unpack(int(read_parts()[0]))
            if got:
                apply_packet(got[0], got[1])

        first = read_parts()
        echoes = (0, 0, 0, 0, 0)
        if first[0] == "ECHOES":
            echoes = tuple(int(v) for v in first[1:6])
            first = read_parts()
        tile_lines = [first] + [read_parts() for _ in range(48)]
        n_bodies = int(read_parts()[1])
        body_lines = [read_parts() for _ in range(n_bodies)]
        rows_h = [read_parts() for _ in range(8)]
        rows_v = [read_parts() for _ in range(7)]

        if round_now == 0:
            role = 0  # map-spawned dragon
        elif not boot_done and not trail:
            role = {2: 2, 3: 1}.get(my_len, 0)  # split child: size encodes role

        fold_tiles(tile_lines)
        fold_bodies(body_lines)
        fold_edges(rows_h, rows_v)
        handle_echoes()

        if round_now > 0 and not boot_done:
            boot_turn()
            boot_done = True
        else:
            boot_done = True
            take_turn()
        flush_turn()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        if DEBUG:
            import traceback
            trace("CRASH:\n" + traceback.format_exc())
        raise

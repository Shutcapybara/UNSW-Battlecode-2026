"""kraken-v01-roles: role-based swarm on protocol 3, written from scratch.

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
    big_target_mid=48,      # desired unit count while hunting on big maps
    big_late_target=32,     # keep replacing losses up to this after late_round
    # ---- combat ----
    strike_steps=3,         # max sprint length when striking a head
    scout_trade=2,          # scout strikes if enemy len >= my len + this
    hunter_trade=0,         # hunter strikes if enemy len >= my len + this
    threat_reach=2,         # hard reservation: sprint reach of enemy heads
    threat_soft=3,          # soft reservation out to this many steps
    # ---- movement scoring ----
    w_danger=-700.0,        # candidate step into a threatened tile
    w_soft=-30.0,           # candidate step into a mildly threatened tile
    w_space=2.0,            # per reachable tile after the move
    space_slack=6,          # flood fill stops at length + this
    trap_pen=-350.0,        # reachable space smaller than our length
    w_pearl_here=40.0,      # pearl on the immediate destination
    w_compass=30.0,         # step agrees with the target search
    w_visit=-4.0,           # per past visit of the destination
    w_spread=1.5,           # per tile of distance from nearest ally head
    spread_cap=10,          # spread distance cap
    # ---- target search (BFS compass) ----
    bfs_cap=600,            # cells the target search may visit
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

pearls = {}             # cell -> round last confirmed
spawn_at = {}           # cell -> round a pearl is expected
enemies = {}            # enemy id (or -cell-1 for gossip) -> (cell, round, len)
ally = {}               # ally id -> (cell, length, role, round)
ray_hot = {}            # cell -> round an enemy radar ray crossed it

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
heads_seen = []         # (cell, id, is_ally) for visible heads
enemy_tails = []        # visible tail-end cells of enemy dragons
elen = {}               # enemy id -> visible segment count this turn
my_parts = {}           # our own visible segments: cell -> facing index
head_edges = (".", ".", ".", ".")  # raw tokens for our head tile's sides


def setup():
    global ek, seen, fertile, visits, NB, dcache, NC
    NC = W * H
    ek = bytearray(2 * NC)
    seen = bytearray(NC)
    fertile = bytearray(NC)
    visits = bytearray(NC)
    NB = [None] * NC
    dcache = [None] * NC


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
    k = ekey(c, d)
    t = ek[k]
    if t == 2:
        return -1
    if t == 3:
        ends = pends.get(epid[k])
        if not ends or len(ends) < 2:
            return -1
        pk = ends[0] if ends[1] == k else ends[1]
        if pk >= NC:            # partner is a vertical edge
            px = (pk - NC) % W
            py = (pk - NC) // W
            if d == 1:          # heading east: emerge east of the partner
                return py * W + px
            return py * W + (px - 1 if px else W - 1)
        px = pk % W
        py = pk // W
        if d == 2:              # heading south: emerge south of the partner
            return pk
        return (py - 1 if py else H - 1) * W + px
    if t == 0:
        return -2
    return nbr(c)[d]


def dest(c, d=None):
    got = dcache[c]
    if got is None:
        got = (dest_raw(c, 0), dest_raw(c, 1), dest_raw(c, 2), dest_raw(c, 3))
        # only cache when all four edges are known: edge values never change
        # once seen, but an unknown->known transition must not stay poisoned
        if ek[ekey(c, 0)] and ek[ekey(c, 1)] and ek[ekey(c, 2)] and ek[ekey(c, 3)]:
            dcache[c] = got
    return got if d is None else got[d]


def invalidate_dest():
    for i in range(NC):
        dcache[i] = None


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
                epid[k] = pid
                portal_seen = 1
                if DEBUG:
                    trace("gossip-portal k%d pid%d (round %d)" % (k, pid, round_now))
            ends = pends.setdefault(pid, [])
            if k not in ends and len(ends) < 2:
                ends.append(k)
                if len(ends) == 2:
                    invalidate_dest()
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
    for i in range(49):
        parts = tile_lines[i]
        if round_now < 2 and i in (0, 24):
            trace("RAW r%d i%d %s" % (round_now, i, " ".join(parts)))
        x = int(parts[0])
        y = int(parts[1])
        cell = y * W + x
        if i == 24:
            head = cell
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
        if not is_ally:
            elen[pid] = elen.get(pid, 0) + 1
            foe_parts.setdefault(pid, {})[cell] = DIR_CH.index(parts[4][0])
        if is_head:
            heads_seen.append((cell, pid, is_ally))
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
            enemy_tails.append(ends[0])


def learn_edge(k, token):
    global portal_seen
    if token == "w":
        if DEBUG and ek[k] in (1, 3):
            trace("EDGE-CONTRADICTION k%d was %d now kelp (round %d)" % (k, ek[k], round_now))
        ek[k] = 2
        return
    if token == ".":
        if DEBUG and ek[k] in (2, 3):
            trace("EDGE-CONTRADICTION k%d was %d now open (round %d)" % (k, ek[k], round_now))
        if ek[k] == 0:
            ek[k] = 1
        return
    pid = int(token)
    if DEBUG and ek[k] == 2:
        trace("EDGE-CONTRADICTION k%d was kelp now portal %d (round %d)" % (k, pid, round_now))
    if ek[k] == 3 and epid.get(k) != pid:
        if DEBUG:
            trace("EDGE-CONTRADICTION k%d portal %d->%d (round %d)" % (k, epid.get(k, -9), pid, round_now))
        pass
    ek[k] = 3
    epid[k] = pid
    portal_seen = 1
    ends = pends.setdefault(pid, [])
    if k not in ends and len(ends) < 2:
        ends.append(k)
        if len(ends) == 2:
            invalidate_dest()
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
    """cell -> 2 (lethal risk) or 1 (soft).

    Every visible enemy head reserves its whole sprint reach, whatever the
    id order: my destination persists into next round, where a lower-id
    enemy moves before me, so its reach matters just as much.
    """
    danger = {}
    reach_cap = CFG["threat_reach"]
    soft_cap = CFG["threat_soft"]
    for cell, pid, is_ally in heads_seen:
        if is_ally:
            for n in dest(cell):
                if n >= 0 and danger.get(n, 0) < 1:
                    danger[n] = 1
            continue
        danger[cell] = 2
        layer = [cell]
        dist = {cell: 0}
        while layer:
            nxt = []
            for c in layer:
                if dist[c] >= soft_cap:
                    continue
                for n in dest(c):
                    if n < 0 or n in dist or n in blocked:
                        continue
                    dist[n] = dist[c] + 1
                    if dist[n] <= reach_cap:
                        danger[n] = 2
                    elif not danger.get(n):
                        danger[n] = 1
                    nxt.append(n)
            layer = nxt
    for cell in enemy_tails:
        # a split child appears here and can immediately strike one step
        for n in dest(cell):
            if n >= 0:
                danger[n] = 2
    return danger


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


def flood_space(start, danger, own):
    cap = my_len + CFG["space_slack"]
    got = {start: 0}
    queue = [start]
    qi = 0
    while qi < len(queue) and len(got) < cap:
        cell = queue[qi]
        qi += 1
        depth = got[cell] + 1
        for n in dest(cell):
            if n < 0 or n in got or n in blocked or danger.get(n, 0) >= 2:
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


def bfs_compass(danger, own):
    """Capped BFS scoring targets in place; returns the best first step."""
    cap = CFG["bfs_cap"] if NC > CFG["bfs_cap"] else NC
    dist = [-1] * NC
    first = [-1] * NC
    dist[head] = 0
    queue = [head]
    qi = 0
    best_dir = -1
    best_score = -1e18
    frontier_w = CFG["w_frontier_scout"] if role == 2 else CFG["w_frontier"]
    hunt = role == 1
    w_dist = CFG["w_dist"]
    w_visit = CFG["w_visit"]
    w_spawn = CFG["w_spawn"]
    horizon = CFG["spawn_horizon"]
    while qi < len(queue) and len(queue) < cap:
        cell = queue[qi]
        qi += 1
        steps_to = dist[cell] + 1
        ds = dest(cell)
        for d in range(4):
            n = ds[d]
            if n < 0 or dist[n] >= 0 or n in blocked or danger.get(n, 0) >= 2:
                continue
            j = own.get(n)
            if j is not None and steps_to + j <= my_len + 1:
                continue
            dist[n] = steps_to
            first[n] = d if cell == head else first[cell]
            queue.append(n)
            score = w_dist * steps_to + w_visit * min(visits[n], 12)
            if n in pearls:
                score += CFG["w_pearl"]
            when = spawn_at.get(n)
            if when is not None and fertile[n]:
                if when <= round_now:
                    score += w_spawn
                else:
                    lag = when - round_now
                    if lag < horizon:
                        score += w_spawn * (1.0 - lag / horizon)
            if frontier_w and borders_unknown(n):
                score += frontier_w
            if hunt and n in ray_hot:
                age = round_now - ray_hot[n]
                if age < CFG["ray_decay"]:
                    score += CFG["w_ray"] * (1.0 - age / CFG["ray_decay"])
            if score > best_score:
                best_score = score
                best_dir = first[n]
    if hunt:
        # sighting cells pull even if their raw tile score was mediocre
        w_hunt = CFG["w_hunt"]
        decay = CFG["hunt_decay"]
        for pid, (cell, when, _l) in enemies.items():
            age = round_now - when
            if 0 < dist[cell] and age < decay:
                score = w_hunt * (1.0 - age / decay) + w_dist * dist[cell]
                if score > best_score:
                    best_score = score
                    best_dir = first[cell]
    return best_dir


def nearest_ally_dist(cell):
    best = 99
    x = cell % W
    y = cell // W
    for pid, (acell, _l, _r, _round) in ally.items():
        dx = abs(x - acell % W)
        dy = abs(y - acell // W)
        d = min(dx, W - dx) + min(dy, H - dy)
        if d < best:
            best = d
    return best


def choose_move(danger, own, compass):
    options = []
    ds = dest(head)
    for d in range(4):
        n = ds[d]
        if n < 0 or n in blocked:
            continue
        if n in own:  # collision precedes tail movement: always fatal
            continue
        level = danger.get(n, 0)
        if brawl:
            # strikes are mutual kills anyway: a threatened tile only costs
            # us if the enemy chooses to trade, and the corpse pearls feed
            # the swarm.  Push hard, harvest hard.
            score = -150.0 if level >= 2 else CFG["w_soft"] * level
        else:
            score = CFG["w_danger"] if level >= 2 else CFG["w_soft"] * level
        space = flood_space(n, danger, own)
        score += CFG["w_space"] * space
        if space < my_len:
            score += CFG["trap_pen"] * (0.3 if brawl else 1.0)
        if n in pearls:
            score += CFG["w_pearl_here"] * (5.0 if brawl else 1.0)
        if d == compass:
            score += CFG["w_compass"]
        score += CFG["w_visit"] * min(visits[n], 12)
        spread = nearest_ally_dist(n)
        if spread < 99:
            w_sp = -3.0 if brawl else CFG["w_spread"]
            score += w_sp * min(spread, CFG["spread_cap"])
        score += ((my_id * 31 + round_now * 7 + d * 13) % 10) * 0.01
        options.append((score, d))
    if not options:
        return -1
    options.sort(reverse=True)
    if options[0][0] < CFG["w_danger"] * 0.5 and len(options) > 1:
        # the favourite is likely lethal; take the best non-lethal step
        for score, d in options:
            if danger.get(ds[d], 0) < 2:
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


def escape_path(danger, own):
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
            if nd >= 2 and danger.get(n, 0) < 2:
                space = flood_space(n, danger, own)
                key = (0 if danger.get(n, 0) == 0 else 1, -space, nd)
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
    desperate = units <= 2 or round_now >= CFG["late_round"]
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
    """Every option looks lethal: pick the least bad non-kelp step.  Last
    resort: dive through an unpaired portal - anywhere beats certain death."""
    fallback = -1
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
        if fallback < 0:
            fallback = d
    if fallback >= 0:
        return fallback
    return portal if portal >= 0 else -1


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
        t_mid = CFG["team_target_mid"]
        t_late = CFG["late_team_floor"]
    if round_now > CFG["late_round"]:
        if not big:
            return 0
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
    emit("MOVE " + DIR_CH[best_d if best_d >= 0 else facing])
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

    danger = build_danger()
    own = own_map()

    global brawl
    trace("chk r%d beds=%d mincd=%d wit=%d" % (round_now, bed_count, min_cd, pearls_wit))
    if not brawl and round_now >= 30 and NC <= 400 and not portal_seen \
            and bed_count >= 20 and pearls_wit * 20 <= bed_count:
        brawl = 1
        trace("BRAWL MODE r%d beds=%d wit=%d" % (round_now, bed_count, pearls_wit))

    child = want_split(danger.get(head, 0))
    if child and my_len - child >= 2 and units < unit_limit:
        emit("SPLIT %d" % child)
        send_sonar()
        emit("INDICATOR %s%d u%d" % ("GHS"[role], my_len, units))
        return

    path = strike_path()
    if path:
        emit_move(path)
        send_sonar()
        emit("INDICATOR %s%d u%d STRIKE" % ("GHS"[role], my_len, units))
        return

    compass = bfs_compass(danger, own)
    move = choose_move(danger, own, compass)
    via = "choose"
    if move < 0 or (not brawl and danger.get(dest(head, move), 0) >= 2):
        esc = escape_path(danger, own)
        if esc:
            emit_move(esc)
            send_sonar()
            emit("INDICATOR %s%d u%d FLEE" % ("GHS"[role], my_len, units))
            return
    if move < 0:
        move = emergency_step()
        via = "emergency"
    if move < 0:
        if my_len >= 4 and units < unit_limit:
            emit("SPLIT %d" % (my_len - 2))  # cornered: shed the body
            send_sonar()
            return
        move = facing
        via = "facing-fallback"
    if DEBUG:
        n = dest(head, move)
        if n < 0 or n in blocked or n in own:
            trace("ILLEGAL-CHOICE r%d via=%s d%d n%d" % (round_now, via, move, n))
    if DEBUG:
        k = ekey(head, move)
        if ek[k] == 3:
            trace("r%d PORTAL-STEP k%d -> %d" % (round_now, k, dest(head, move)))
        trace("r%d h%d len%d mv%s dg%d he=%s ek=%d%d%d%d body=%s eh=%s blk=%s" % (
            round_now, head, my_len, DIR_CH[move], danger.get(dest(head, move), 0),
            "/".join(head_edges),
            ek[ekey(head, 0)], ek[ekey(head, 1)], ek[ekey(head, 2)], ek[ekey(head, 3)],
            ",".join(str(c) for c in trail[-my_len:]),
            ";".join("%d@%d%s" % (pid, c, "A" if al else "E")
                     for c, pid, al in heads_seen),
            ",".join(str(c) for c in sorted(blocked))))
    emit("MOVE " + DIR_CH[move])
    send_sonar()
    emit("INDICATOR %s%d u%d" % ("GHS"[role], my_len, units))


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

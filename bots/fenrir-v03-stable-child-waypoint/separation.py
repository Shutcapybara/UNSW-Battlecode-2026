"""Short-lived newborn objective for escaping narrow split locations.

The parent keeps its existing target.  A split packet gives only the new child
its spawn anchor; the child then follows known map topology toward an open,
separate region.  The objective expires after escape or a small time limit.
"""
import world as w
from params import P

ACTIVE = False
PARENT_ID = -1
ORIGIN = -1
START = -1
ORIGIN_DIST = {}
PLAN_MASK = {}
PLAN_TARGET = -1
WAYPOINT = -1
LAST_NOTE = None
PENDING_HANDOFF = None
BIRTH_PACKET_SEEN = False


def init():
    global ACTIVE, PARENT_ID, ORIGIN, START, ORIGIN_DIST, PLAN_MASK, PLAN_TARGET, WAYPOINT, LAST_NOTE, PENDING_HANDOFF, BIRTH_PACKET_SEEN
    ACTIVE = False
    PARENT_ID = ORIGIN = START = -1
    ORIGIN_DIST = {}
    PLAN_MASK = {}
    PLAN_TARGET = -1
    WAYPOINT = -1
    LAST_NOTE = None
    PENDING_HANDOFF = None
    BIRTH_PACKET_SEEN = False


def _edges(cell):
    """Known open/paired-portal edges plus optimistic unknown edges."""
    g = w.step_opt(cell)
    return [(d, n) for d, n in enumerate(g) if n >= 0 and n != cell]


def _topology(cell, depth=2, cap=48):
    """Count local reachable cells and branch points without hard-coded maps."""
    dist = {cell: 0}
    q = [cell]
    branches = 0
    max_degree = 0
    qi = 0
    while qi < len(q):
        c = q[qi]
        qi += 1
        edges = _edges(c)
        degree = len({n for _, n in edges})
        max_degree = max(max_degree, degree)
        if degree >= 3:
            branches += 1
        if dist[c] >= depth:
            continue
        for _, n in edges:
            if n in dist:
                continue
            dist[n] = dist[c] + 1
            q.append(n)
            if len(q) >= cap:
                return len(dist), branches, max_degree
    return len(dist), branches, max_degree


def should_escape_spawn(cell):
    """Activate only where a short topology probe looks like a corridor."""
    global LAST_NOTE
    area, branches, degree = _topology(cell, depth=3, cap=64)
    direct_degree = len({n for _, n in _edges(cell)})
    escape = direct_degree <= 2 and (area <= P["escape_spawn_area"] or branches <= P["escape_spawn_branches"])
    if P.get("escape_trace", 0) and escape:
        LAST_NOTE = "BIF_SPLIT_ESCAPE area=%d branches=%d exits=%d" % (
            area, branches, direct_degree)
    return escape


def observe_birth():
    """Infer a constrained split birth from local topology if no packet arrived."""
    global ACTIVE, PARENT_ID, ORIGIN, START, WAYPOINT, LAST_NOTE
    initial_dragon = (w.ME & 4095) < P["opening_initial_id_limit"]
    if (ACTIVE or BIRTH_PACKET_SEEN or w.BORN != w.RND or
            (w.RND == 0 and initial_dragon)):
        return False
    if not should_escape_spawn(w.HEAD):
        return False
    ACTIVE = True
    ORIGIN = w.HEAD
    START = w.RND
    WAYPOINT = -1
    PARENT_ID = -1
    # If the parent is visible, retain a short repulsion from its head.
    nearby = [(w.tdist(c, w.HEAD), did & 4095)
              for c, did in w.ally_heads if w.tdist(c, w.HEAD) <= 2]
    if nearby:
        PARENT_ID = min(nearby)[1]
    if P.get("escape_trace", 0):
        LAST_NOTE = "BIF_BIRTH_ESCAPE"
    return True


def queue_handoff(packet, rnd):
    """Remember a just-sent split packet for two follow-up transmissions."""
    global PENDING_HANDOFF
    PENDING_HANDOFF = (packet, rnd, P.get("escape_handoff_retries", 2))


def retry_handoff(messages, rnd, face):
    """Repeat a split packet briefly on the ray behind the parent."""
    global PENDING_HANDOFF
    pending = PENDING_HANDOFF
    if pending is None:
        return
    packet, sent_round, retries = pending
    age = rnd - sent_round
    if age <= 0:
        return
    if age > retries:
        PENDING_HANDOFF = None
        return
    messages[w.DIRS[(face + 2) % 4]] = packet
    if age >= retries:
        PENDING_HANDOFF = None


def receive(parent_id, cell, rnd, escape, inherit_crown):
    """Accept a split message only on the newly created child process."""
    global ACTIVE, PARENT_ID, ORIGIN, START, WAYPOINT, LAST_NOTE, BIRTH_PACKET_SEEN
    def reject(reason):
        global LAST_NOTE
        if P.get("escape_trace", 0):
            LAST_NOTE = "BIF_REJECT " + reason
        return False

    if (w.ME & 4095) == parent_id:
        return reject("sender")
    if not (escape or inherit_crown):
        return reject("flags")
    if w.BORN not in (rnd, rnd + 1):
        return reject("born")
    age = w.RND - rnd
    if age < 0 or age > P.get("escape_handoff_retries", 2):
        return reject("round")
    if w.tdist(w.HEAD, cell) > max(1, age):
        return reject("position")
    if (BIRTH_PACKET_SEEN and PARENT_ID == parent_id and ORIGIN == cell and
            START == rnd):
        return True  # a repeated delivery must not restart the child's route
    PARENT_ID = parent_id
    BIRTH_PACKET_SEEN = True
    ORIGIN = cell
    START = rnd
    WAYPOINT = -1
    ACTIVE = bool(escape and not inherit_crown)
    if P.get("escape_trace", 0):
        LAST_NOTE = "BIF_RECEIVE escape=%d inherit=%d" % (
            int(escape), int(inherit_crown))
    return True


def active():
    return ACTIVE


def _bfs(start, max_depth, cap, body=None, temporal=False):
    """Return bounded topology distances and first-step masks from start."""
    own_idx = {c: i for i, c in enumerate(body or ())}
    dist = {start: 0}
    mask = {start: 0}
    q = [start]
    qi = 0
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        nd = dist[c] + 1
        if nd > max_depth:
            continue
        for d, n in _edges(c):
            if temporal:
                i = own_idx.get(n)
                if i is not None and nd < i + 2:
                    continue
                vacates = w.vac.get(n)
                if vacates is not None and nd < vacates:
                    continue
            m = (1 << d) if c == start else mask[c]
            old = dist.get(n)
            if old is not None:
                if old == nd:
                    mask[n] |= m
                continue
            dist[n] = nd
            mask[n] = m
            q.append(n)
    return dist, mask


def _resource_value(cell):
    rnd = w.RND
    r = w.pearls.get(cell)
    if r is not None:
        if r == rnd:
            return P["v_pearl"]
        if rnd - r <= P["mem_ttl"]:
            return P["v_mem"]
    if w.bed[cell] == 2:
        spawn = w.spawn.get(cell)
        if spawn is not None and spawn >= rnd:
            return P["v_bed"] * max(0.0, 1.0 - (spawn - rnd) / P["bed_wait"])
    if w.seen[cell] == 0:
        return P["v_unseen"] * 0.35
    return 0.0


def _local_resource(cell):
    best = _resource_value(cell)
    for _, n in _edges(cell):
        best = max(best, _resource_value(n))
    return best


def _waypoint_score(cell, route_distance, minimum):
    area, branch_count, exits = _topology(cell, depth=2, cap=40)
    away = ORIGIN_DIST.get(cell, 0) - minimum
    resource = _local_resource(cell)
    return (P["escape_open_weight"] * min(area, 16) +
            P["escape_branch_weight"] * min(branch_count, 4) +
            P["escape_exit_weight"] * max(0, exits - 2) +
            P["escape_distance_weight"] * min(max(0, away), 8) +
            P["escape_resource_weight"] * resource -
            P["escape_route_cost"] * route_distance)


def plan(body, normal_target, normal_dist, normal_mask):
    """Choose a stable escape waypoint or keep a nearby valuable resource."""
    global ACTIVE, ORIGIN_DIST, PLAN_MASK, PLAN_TARGET, WAYPOINT
    PLAN_MASK = {}
    PLAN_TARGET = -1
    if not ACTIVE:
        WAYPOINT = -1
        return None
    age = max(0, w.RND - START)
    if age >= P["escape_max_turns"]:
        ACTIVE = False
        WAYPOINT = -1
        return None

    ORIGIN_DIST, _ = _bfs(ORIGIN, P["escape_origin_depth"], P["escape_origin_nodes"])
    current_od = ORIGIN_DIST.get(w.HEAD, w.tdist(w.HEAD, ORIGIN))
    room, branches, degree = _topology(w.HEAD, depth=2, cap=48)
    in_open_area = degree >= 3 or room >= P["escape_open_area"] or branches >= 2
    if age >= 1 and current_od >= P["escape_min_distance"] and in_open_area:
        ACTIVE = False
        WAYPOINT = -1
        return None

    dist, mask = _bfs(w.HEAD, P["escape_target_depth"], P["escape_target_nodes"],
                      body=body, temporal=True)

    # A nearby real pearl or ready bed is worth taking before resuming escape.
    if normal_target >= 0:
        nt = normal_dist.get(normal_target)
        if (nt is not None and nt <= P["escape_valuable_distance"] and
                _resource_value(normal_target) >= P["escape_valuable_threshold"]):
            PLAN_MASK = normal_mask
            PLAN_TARGET = normal_target
            return normal_target, normal_dist, normal_mask

    minimum = P["escape_min_distance"]
    eligible = [c for c, _ in dist.items()
                if ORIGIN_DIST.get(c, -1) >= minimum]
    if not eligible:
        # Unknown or newly learned terrain may temporarily break the anchor
        # route; keep separation pressure but let a shorter waypoint lead.
        eligible = [c for c, _ in dist.items()
                    if ORIGIN_DIST.get(c, -1) >= max(2, minimum // 2)]
    if not eligible:
        ACTIVE = False
        WAYPOINT = -1
        return None

    best = -1
    best_score = -1e30
    for c in eligible:
        t = dist[c]
        score = _waypoint_score(c, t, minimum)
        if score > best_score:
            best_score = score
            best = c
    if best < 0:
        return None
    if (WAYPOINT in dist and WAYPOINT in eligible and WAYPOINT != w.HEAD):
        old_score = _waypoint_score(WAYPOINT, dist[WAYPOINT], minimum)
        if old_score >= best_score - P["escape_waypoint_hysteresis"]:
            best = WAYPOINT
    else:
        WAYPOINT = -1
    WAYPOINT = best
    PLAN_MASK = mask
    PLAN_TARGET = best
    return best, dist, mask


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def action_bonus(cell, first_dir):
    """Decaying pressure toward the chosen waypoint and away from the split."""
    if not ACTIVE:
        return 0.0
    age = max(0, w.RND - START)
    pressure = P["escape_decay"] ** age
    m = PLAN_MASK.get(PLAN_TARGET, 0)
    route = 1.0 if (m >> first_dir) & 1 else -1.0
    score = P["escape_route_weight"] * pressure * route

    before = ORIGIN_DIST.get(w.HEAD, w.tdist(w.HEAD, ORIGIN))
    after = ORIGIN_DIST.get(cell, w.tdist(cell, ORIGIN))
    score += P["escape_push"] * pressure * _clamp(after - before, -2, 2)
    if age >= 2 and after <= 2:
        score -= P["escape_origin_cost"] * pressure

    for hc, hid in w.ally_heads:
        if (hid & 4095) == PARENT_ID:
            d = w.tdist(cell, hc)
            if d < P["escape_parent_radius"]:
                score -= P["escape_parent_cost"] * pressure * (P["escape_parent_radius"] - d)
            break
    return score


def portal_bonus():
    if not ACTIVE:
        return 0.0
    age = max(0, w.RND - START)
    return P["escape_portal_bonus"] * (P["escape_decay"] ** age)


def indicator():
    """Compact replay trace, disabled in normal submissions."""
    global LAST_NOTE
    if not P.get("escape_trace", 0):
        return None
    if ACTIVE:
        LAST_NOTE = None
        age = max(0, w.RND - START)
        distance = ORIGIN_DIST.get(w.HEAD, w.tdist(w.HEAD, ORIGIN))
        return "BIF_ESCAPE age=%d dist=%d" % (age, distance)
    note = LAST_NOTE
    LAST_NOTE = None
    return note

"""EXECUTION layer (E0): the frozen executor dependency closure.

Owns candidate generation, movement simulation, routing, internal target
choice, tie-breaks, availability thresholds, search budgets, role rules for
execution and fallback behaviour.  Everything below is extracted verbatim
from monte_christo-v01-core policy.py/main.py: no policy feature vector
reaches this module, and decision-layer scoring changes must not leak here.
Version any change to this closure explicitly (E0 -> E1 ...).

Executors by intention:
  plan_route / far_target / cell_value   GATHER+SCOUT targeting (route planner)
  feeder_sacrifice                       FEED_ALLY immediate donation
  move_proposals / move_preview / move_execute   shared movement mechanics
  split_proposal / split_execute         REPRODUCE
  escape_split / emergency_move          RETREAT fallback infrastructure

`plan_route` fuses search mechanics with v01's P-valued field (internal
target choice is part of this frozen closure by contract); decision.py only
consumes its result.  MEM is executor script state (target hysteresis).
"""
import protocol as io
import world as w
import tactics as tx
import roles
from params import P

MEM = {"target": -1, "tval": 0.0}   # planner script state (survives turns)


# ------------------------------------------------------------------ targeting
def cell_value(c, t, ally, enemy):
    """Value of reaching cell c after t steps (0 if nothing there)."""
    rnd = w.RND
    v = 0.0
    pr = w.pearls.get(c)
    if pr is not None:
        if pr == rnd:
            v = P["v_pearl"]
        elif rnd - pr <= P["mem_ttl"]:
            v = P["v_mem"]
    elif w.bed[c] == 2:
        s = w.spawn.get(c)
        if s is not None:
            arr = rnd + t
            if s > arr:
                v = P["v_bed"] * (1.0 - (s - arr) / P["bed_wait"])
            elif s > rnd:
                v = P["v_bed"]
            else:  # predicted to have spawned while out of view
                age = rnd - s
                if age <= P["bed_stale"]:
                    v = P["v_bed"] * (1.0 - 0.5 * age / P["bed_stale"])
                else:
                    v = P["v_bed"] * 0.3
    elif w.seen[c] == 0:
        v = P["v_unseen"]
    if v <= 0:
        return 0.0
    role = roles.ROLE[0]
    if role == "crown":
        return v
    if w.crown is not None and roles.fresh() and w.RND >= P["crown_from"]:
        rad = P["crown_food"] if w.RND >= roles.feed_from() else P["crown_food_early"]
        if w.tdist(c, w.crown[1]) <= rad:
            return 0.0  # the crown's surroundings are its food
    # ownership: a clearly closer head takes it first
    for hc, hid in ally:
        dd = w.tdist(hc, c)
        if dd < t or (dd == t and hid < w.ME):
            v *= P["own_disc"]
            break
    for hc in enemy:
        if w.tdist(hc, c) < t:
            v *= P["enemy_disc"]
            break
    return v


def far_target():
    """Nothing valuable within the search: a remembered pearl, else the
    nearest sector with unseen tiles."""
    best = -1
    bv = 0.0
    gamma = P["gamma"]
    for c, r in w.pearls.items():
        if w.RND - r <= P["mem_ttl"] and c != w.HEAD:
            v = P["v_mem"] * gamma ** w.tdist(c, w.HEAD)
            if v > bv:
                bv = v
                best = c
    if best < 0:
        best = w.sector_target()
    return best


def plan_route(own_idx):
    """Route search from the head that scores every reached cell as it is
    discovered (value x gamma^t) and stops once no farther cell can beat the
    best found (or at the node cap: CPU).  Returns (target, dist, mask, kind)
    where mask[c] is the bitmask of first moves that start a shortest route
    to c and kind reports the selection branch:
    "search" (scored cell), "prey" (hunt override), "fallback" (far_target),
    "feeder" (route to the crown)."""
    feeder = roles.ROLE[0] == "feeder"
    crown = roles.ROLE[0] == "crown"
    ally = w.ally_heads
    enemy = [c for c, _ in w.enemy_heads]
    gamma = P["gamma"]
    # the best value any unexplored cell could still hold (tight bound -> early stop)
    vmax = P["v_unseen"]
    if w.pearls:
        vmax = P["v_pearl"]
    elif w.spawn and P["v_bed"] > vmax:
        vmax = P["v_bed"]
    if w.pends and P["v_dive"] > vmax:
        vmax = P["v_dive"]
    prev = MEM["target"]
    prev_val = 0.0
    best = -1
    bval = 0.0
    dive = -1
    kind = "search"
    vac = w.vac
    OPT = w.OPT
    step_opt = w.step_opt
    pearls = w.pearls
    bed = w.bed
    seen = w.seen
    src = w.HEAD
    goal = w.crown[1] if feeder else -1
    dist = {src: 0}
    mask = {src: 0}
    q = [src]
    qi = 0
    cap = P["big_cap"] if w.RND - w.BORN >= 2 else P["born_cap"]
    disc = 1.0
    last_t = 0
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        t = dist[c] + 1
        mc = mask[c]
        if t != last_t:
            last_t = t
            disc = gamma ** t
            if t > 3 and not feeder and vmax * disc <= bval:
                break  # nothing farther can beat the best target
        g = OPT[c]
        if g is None:
            g = step_opt(c)
        for d in range(4):
            n = g[d]
            if n < 0:
                if n == -3 and not crown and not feeder:
                    v = P["v_dive"]
                    for hc, hid in ally:
                        if w.tdist(hc, c) < t - 1:
                            v *= P["own_disc"]
                            break
                    sc = v * disc
                    if sc > bval:
                        bval = sc
                        best = c
                        dive = d
                        kind = "search"
                continue
            m = mc if c != src else (1 << d)
            tn = dist.get(n)
            if tn is not None:
                if tn == t:
                    mask[n] |= m
                continue
            i = own_idx.get(n)
            if i is not None and t < i + 2:
                continue
            v = vac.get(n)
            if v is not None and t < v:
                continue
            dist[n] = t
            mask[n] = m
            q.append(n)
            if feeder:
                continue
            if n not in pearls and bed[n] != 2 and seen[n]:
                continue  # nothing there (fast path)
            v = cell_value(n, t, ally, enemy)
            if v > 0:
                sc = v * disc
                if n == prev:
                    prev_val = sc
                if sc > bval:
                    bval = sc
                    best = n
                    dive = -1
                    kind = "search"
        if feeder and goal in dist:
            break
    if feeder:
        MEM["target"] = goal
        MEM["dive"] = -1
        return goal, dist, mask, "feeder"
    if dive < 0 and prev >= 0 and prev_val > 0 and prev != best and prev_val * P["hyst"] >= bval:
        best = prev
        bval = prev_val
        kind = "search"
    pr = w.prey
    if pr is not None and roles.ROLE[0] == "forager" and w.RND >= P["hunt_from"] \
            and w.LEN <= P["hunt_max_len"] and w.RND - pr[3] <= P["prey_ttl"]:
        t = dist.get(pr[1])
        if t is None:
            t = w.tdist(w.HEAD, pr[1]) + 2
        sc = P["v_hunt"] * min(pr[2], 40) * gamma ** t
        if sc > bval:
            bval = sc
            best = pr[1]
            dive = -1
            kind = "prey"
    if best < 0:
        best = far_target()
        kind = "fallback"
    MEM["target"] = best
    MEM["tval"] = bval
    MEM["dive"] = dive
    return best, dist, mask, kind


# ------------------------------------------------------------------ movement
def move_proposals(body):
    """Move paths worth evaluating: single steps always; 2-3 step sprints only
    with an enemy head near (strike / escape) or a pearl two steps away."""
    out = [[d] for d in range(4)]
    L = w.LEN
    if L < 3:
        return out
    near_threat = False
    for ec, eid in w.enemy_heads:
        if w.cheb(ec, w.HEAD) <= 4:
            near_threat = True
            break
    if not near_threat:
        # E1 (x03): sprints also for a visible pearl within chebyshev 2 --
        # the trigger E0's docstring documents but does not implement.
        fresh = w.RND
        for c, r in w.pearls.items():
            if r == fresh and w.cheb(c, w.HEAD) <= 2:
                for d1 in range(4):
                    for d2 in range(4):
                        if d2 == (d1 + 2) % 4:
                            continue
                        out.append([d1, d2])
                break
        return out
    for d1 in range(4):
        for d2 in range(4):
            if d2 == (d1 + 2) % 4:
                continue
            out.append([d1, d2])
            if 4 <= L < P["sprint3_limit"]:
                for d3 in range(4):
                    if d3 == (d2 + 2) % 4:
                        continue
                    out.append([d1, d2, d3])
    return out


def move_need():
    """Flood-fill room requirement for this body (executor budget rule)."""
    L = w.LEN
    need = max(L + P["slack"], P["min_area"])
    if L >= 10:  # long bodies need margin: others fill in behind them
        need = min(need + L // 3, P["flood_cap_long"])
    else:
        need = min(need, P["flood_cap"])
    return need


def move_preview(path, body, need):
    """Mechanical facts of one move candidate: exact engine simulation plus
    reachable-room audit.  Pure: never mutates world/tactics state."""
    st, nb, eaten, hit = tx.sim(path, body)
    area = None
    pocket = 0
    if st == "ok":
        area = tx.flood(nb, need, 0)
        pocket = tx.POCKET[0]
    return {"path": path, "status": st, "body": nb, "eaten": eaten, "hit": hit,
            "blind": tx.BLIND[0], "area": area, "pocket": pocket}


def move_execute(path):
    """Serialize a nominated move; returns (command, argument, trail_cells).
    Re-simulates exactly like the v01 executor did (CPU profile unchanged)."""
    arg = "".join(w.DIRS[d] for d in path)
    cells = ()
    if len(arg) > 1:
        st, nb, _, _ = tx.sim(path, w.body)
        if st == "ok":
            cells = nb[-len(arg):-1]
    return (io.Command.MOVE, arg, cells)


# ------------------------------------------------------------------ FEED_ALLY
def feeder_sacrifice(body):
    """A feeder within feed_dist of the visible crown head may nominate an
    immediate donation: the first move that dies (tail-first direction
    preferred).  Returns the dying [direction] or None.  This is the
    explicit intentional sacrifice path -- never a generic safety filter."""
    if roles.ROLE[0] != "feeder":
        return None
    ch = roles.crown_visible()
    if ch < 0 or w.tdist(ch, w.HEAD) > P["feed_dist"]:
        return None
    back = (w.FACE + 2) % 4
    for d in [back, 0, 1, 2, 3]:
        if tx.sim([d], body)[0] == "dead":
            return [d]
    return None


# ------------------------------------------------------------------ REPRODUCE
def split_proposal(body):
    """Production split availability + mechanical facts, or None.
    Gates and geometry exactly as v01 split_option; scoring lives in
    decision.py."""
    L = w.LEN
    n = P["child"]
    if L < P["split_min"] or L - n < 2 or w.UNITS >= w.LIMIT:
        return None
    if w.RND >= P["split_stop"] or w.RND >= P["grow_from"]:
        return None
    if roles.ROLE[0] != "forager":
        return None
    if len(body) < L:
        return None  # body not fully known
    # child: head = old tail, body reversed rear n segments
    child = body[:n][::-1]
    ch = child[-1]
    cown = set(child)
    pown = set(body[n:])
    ok = 0
    for x in w.dest(ch):
        if x >= 0 and x not in cown and x not in pown and x not in w.occ:
            ok += 1
    if not ok:
        return None
    if tx.flood(child, P["child_area"], 0) < P["child_area"]:
        return None
    parent = body[n:]
    pneed = min(max(L - n + P["slack"], P["min_area"]), P["flood_cap"])
    return {"n": n, "child": child, "child_head": ch, "parent": parent,
            "pneed": pneed, "parent_area": tx.flood(parent, pneed, 0)}


def split_execute(n):
    """Serialize a nominated split; returns (command, argument)."""
    return (io.Command.SPLIT, str(n))


# ------------------------------------------------------------------ RETREAT
def escape_split(body):
    """Every move dies: shed the rear (all but 2 segments) as a child that
    starts at our tail facing away -- it keeps most of our length."""
    L = w.LEN
    if L < 4 or w.UNITS >= w.LIMIT or len(body) < L:
        return None
    n = L - 2
    child = body[:n][::-1]
    ch = child[-1]
    cown = set(child)
    pown = set(body[n:])
    for x in w.dest(ch):
        if x >= 0 and x not in cown and x not in pown and x not in w.occ:
            return ("split", n)
    return None


def emergency_move():
    """Last-resort valid command when the pipeline itself failed: first
    single step whose simulation survives (direction order 0..3)."""
    for d in range(4):
        if tx.sim([d], w.body)[0] == "ok":
            return d
    return None

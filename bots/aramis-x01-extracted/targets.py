"""DECISION layer: target field + candidate evaluation.

V(candidate) = material + position (route distance to target) - trap - threat
              - crowding - dithering (+ strike value, + split value)
All weights live in params.P.
"""
import world as w
import tactics as tx
import roles
from params import P

MEM = {"target": -1, "tval": 0.0}
DBG = []  # (path, score, area) per candidate when tracing


def lv_now():
    if roles.ROLE[0] == "crown":
        return P["lv_crown"]
    g = P["grow_from"]
    if w.RND < g:
        return P["lv"]
    f = (w.RND - g) / max(1, 500 - g)
    return P["lv"] + (P["lv_end"] - P["lv"]) * f


def unit_value():
    return P["unit"]


def dragon_value(length):
    return unit_value() + lv_now() * length


# ------------------------------------------------------------------ targets
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


def choose_target(own_idx):
    """Route search from the head that scores every reached cell as it is
    discovered (value x gamma^t) and stops once no farther cell can beat the
    best found (or at the node cap: CPU).  Returns (target, dist, mask) where
    mask[c] is the bitmask of first moves that start a shortest route to c."""
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
        if feeder and goal in dist:
            break
    if feeder:
        MEM["target"] = goal
        MEM["dive"] = -1
        return goal, dist, mask
    if dive < 0 and prev >= 0 and prev_val > 0 and prev != best and prev_val * P["hyst"] >= bval:
        best = prev
        bval = prev_val
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
    if best < 0:
        best = far_target()
    MEM["target"] = best
    MEM["tval"] = bval
    MEM["dive"] = dive
    return best, dist, mask



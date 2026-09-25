"""DECISION layer: target field + candidate evaluation.

V(candidate) = material + position (route distance to target) - trap - threat
              - crowding - dithering (+ strike value, + split value)
All weights live in params.P.
"""
import world as w
import tactics as tx
from params import P

MEM = {"target": -1, "tval": 0.0}


def lv_now():
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


def choose_target(own_idx):
    """Search from the head; return (target cell, first-step dir, value)."""
    dist, first = tx.bfs_from(w.HEAD, P["big_cap"], P["t_other"], own_idx)
    ally = w.ally_heads
    enemy = [c for c, _ in w.enemy_heads]
    gamma = P["gamma"]
    best = -1
    bval = 0.0
    disc = 1.0
    last_t = 0
    prev = MEM["target"]
    prev_val = 0.0
    # dist is in BFS order, so t is non-decreasing
    for c, t in dist.items():
        if t == 0:
            continue
        if t != last_t:
            disc = gamma ** t
            last_t = t
        v = cell_value(c, t, ally, enemy)
        if v <= 0:
            continue
        s = v * disc
        if c == prev:
            prev_val = s
        if s > bval:
            bval = s
            best = c
    if prev >= 0 and prev_val > 0 and prev != best and prev_val * P["hyst"] >= bval:
        best = prev
        bval = prev_val
    MEM["target"] = best
    MEM["tval"] = bval
    return best, dist, first


# --------------------------------------------------------------- candidates
def candidates(body):
    """Move paths worth evaluating: single steps always, 2-3 step sprints
    when they eat, strike, or escape."""
    out = [[d] for d in range(4)]
    L = w.LEN
    if L >= 3:
        near_threat = False
        for ec, eid in w.enemy_heads:
            if w.cheb(ec, w.HEAD) <= 4:
                near_threat = True
                break
        for d1 in range(4):
            for d2 in range(4):
                if d2 == (d1 + 2) % 4:
                    continue
                out.append([d1, d2])
                if L >= 4 and near_threat:
                    for d3 in range(4):
                        if d3 == (d2 + 2) % 4:
                            continue
                        out.append([d1, d2, d3])
    return out


def evaluate(threat):
    """Return (score, action) with action = ('move', path) or ('split', n)."""
    body = w.body
    L = w.LEN
    lv = lv_now()
    own_idx = {c: i for i, c in enumerate(body)}
    target, dist, first = choose_target(own_idx)
    firsts = set()
    for d in range(4):
        n = w.dest(w.HEAD)[d]
        if n >= 0:
            firsts.add(n)
    rd = None
    if target >= 0:
        # distances from every cell a candidate may end on (up to 3 steps)
        stop = [c for c, t in dist.items() if 0 < t <= 3]
        rd = tx.rev_dist(target, P["big_cap"] * 2, stop)
        base_d = dist.get(target, 99)
    else:
        base_d = 0
    need = L + P["slack"]
    best = None
    best_s = -1e18
    ally = w.ally_heads
    for path in candidates(body):
        st, nb, eaten, hit = tx.sim(path, body)
        steps = len(path)
        if st == "dead":
            s = -1000.0 - steps
        elif st == "h2h":
            s = strike_value(hit, steps)
            if s is None:  # a bad trade still beats dying alone; a friend never
                s = -950.0 if hit in w.elen else -1100.0
        else:
            h = nb[-1]
            dl = len(nb) - L
            s = lv * dl - P["w_sprint"] * (steps - 1)
            if eaten:
                s += 0.5 * eaten  # tie-break towards material now
            # position: progress towards the target
            if rd is not None:
                dh = rd.get(h)
                if dh is None:
                    dh = base_d + 3
                s += P["w_goal"] * (base_d - dh) / max(1, steps) * (1.0 if steps == 1 else 0.7)
            # trap
            area = tx.flood(nb, need, P["t_other"])
            if area < need:
                s -= P["w_trap"] * (need - area) / need
                if area < len(nb):
                    s -= P["w_trap"]
            # threat
            s -= threat_cost(h, len(nb), threat)
            # crowding
            for hc, hid in ally:
                dd = w.tdist(hc, h)
                if dd <= 2:
                    s -= P["w_crowd"] * (3 - dd)
            s -= P["w_visit"] * w.visits[h]
            if w.bed[h] == 2 and w.spawn.get(h, -9) == w.RND + 1:
                s -= P["w_bed_block"]
        if s > best_s:
            best_s = s
            best = ("move", path)
    sp = split_option(body, threat, need)
    if sp is not None and sp[0] > best_s:
        best_s, best = sp
    return best_s, best


def threat_cost(h, newlen, threat):
    ts = threat.get(h)
    if not ts:
        return 0.0
    mine = dragon_value(newlen)
    cost = 0.0
    for steps, eid, el in ts:
        theirs = dragon_value(el)
        p = P["p_adj"] if steps == 1 else P["p_sprint"]
        loss = mine - theirs
        c = P["threat_base"] + (loss if loss > 0 else 0.0)
        c *= p
        if c > cost:
            cost = c
    return P["w_threat"] * cost


def strike_value(eid, steps):
    if eid not in w.elen:
        return None  # an ally head
    if not P["attack"] or w.UNITS < P["atk_units"]:
        return None
    theirs = dragon_value(w.elen.get(eid, 1))
    mine = dragon_value(w.LEN)
    gain = theirs - mine - P["w_sprint"] * (steps - 1)
    if gain < P["atk_margin"]:
        return None
    return 2.0 + gain


def split_option(body, threat, need):
    L = w.LEN
    n = P["child"]
    if L < P["split_min"] or L - n < 2 or w.UNITS >= w.LIMIT:
        return None
    if w.RND >= P["split_stop"] or w.RND >= P["grow_from"]:
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
    parent = body[n:]
    s = P["split_val"]
    area = tx.flood(parent, L - n + P["slack"], P["t_other"])
    pneed = L - n + P["slack"]
    if area < pneed:
        s -= P["w_trap"] * (pneed - area) / pneed
    s -= threat_cost(w.HEAD, L - n, threat)
    if threat.get(ch):
        s -= 1.0
    return s, ("split", n)

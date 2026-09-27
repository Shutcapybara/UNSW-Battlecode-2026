"""DECISION layer: target field + candidate evaluation.

V(candidate) = material + position (route distance to target) - trap - threat
              - crowding - dithering (+ strike value, + split value)
All weights live in params.P.
"""
import world as w
import tactics as tx
import roles
import density
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
    if P["density_policy"] == 1:
        v *= density.resource_factor(c)
    return v


def blind_risk(c):
    """Estimate an unseen portal exit's risk from recent body sightings."""
    fresh = P["blind_fresh"]
    if w.body_seen.get(c, -999) >= w.RND - fresh:
        return P["r_body"]
    for n in w.nbr(c):
        if w.body_seen.get(n, -999) >= w.RND - fresh:
            return P["r_body"]
    seen = w.seen[c]
    if seen and w.RND - (seen - 1) <= fresh:
        return P["r_seen"]
    return P["r_unseen"]


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
    if (
        w.RND - w.BORN >= 2
        and P["density_policy"] == 1
        and w.UNITS / max(1, w.LIMIT) >= P["info_aggro_sat"]
    ):
        cap = min(cap, P["big_cap_saturated"])
    if w.RND >= P.get("big_cap_late_from", 501):
        cap = min(cap, P.get("big_cap_late", cap))
    if (
        w.RND - w.BORN >= 2
        and w.RND >= P.get("big_cap_sparse_from", 501)
        and w.UNITS <= P.get("big_cap_sparse_units", 0)
    ):
        cap = max(cap, P.get("big_cap_sparse", cap))
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


# --------------------------------------------------------------- candidates
def candidates(body, sprint3_limit=None):
    """Move paths worth evaluating: single steps always; 2-3 step sprints only
    with an enemy head near (strike / escape) or a pearl two steps away."""
    out = [[d] for d in range(4)]
    L = w.LEN
    if sprint3_limit is None:
        sprint3_limit = P["sprint3_limit"]
    if L < 3:
        return out
    near_threat = False
    for ec, eid in w.enemy_heads:
        if w.cheb(ec, w.HEAD) <= 4:
            near_threat = True
            break
    if not near_threat:
        return out
    for d1 in range(4):
        for d2 in range(4):
            if d2 == (d1 + 2) % 4:
                continue
            out.append([d1, d2])
            if 4 <= L < sprint3_limit:
                for d3 in range(4):
                    if d3 == (d2 + 2) % 4:
                        continue
                    out.append([d1, d2, d3])
    return out


def rank_actions(threat):
    """Return scored legal/executable intentions; selection lives in main.py."""
    body = w.body
    L = w.LEN
    lv = lv_now()
    own_idx = {c: i for i, c in enumerate(body)}
    target, dist, mask = choose_target(own_idx)
    if roles.ROLE[0] == "feeder":
        ch = roles.crown_visible()
        if ch >= 0 and w.tdist(ch, w.HEAD) <= P["feed_dist"]:
            back = (w.FACE + 2) % 4
            for d in [back, 0, 1, 2, 3]:
                st = tx.sim([d], body)[0]
                if st == "dead":
                    return [(0.0, ("move", [d]))]
    # progress of each first move towards the target: +1 on a shortest
    # route, -1 otherwise; beyond the search, torus distance steers
    prog = [0, 0, 0, 0]
    if target >= 0 and target != w.HEAD:
        tm = mask.get(target)
        if tm is not None:
            for d in range(4):
                prog[d] = 1 if (tm >> d) & 1 else -1
        else:
            # beyond the search: head for the searched cell that best trades
            # remaining torus distance against route length (a waypoint)
            wp = -1
            wv = 1 << 30
            for c, t in dist.items():
                if t:
                    v = 3 * w.tdist(c, target) + t
                    if v < wv:
                        wv = v
                        wp = c
            if wp >= 0:
                tm = mask[wp]
                for d in range(4):
                    prog[d] = 1 if (tm >> d) & 1 else -1
    # feeders keep off the crown's flanks (they would box it in)
    crown_flank = set()
    if roles.ROLE[0] == "feeder" and w.crown is not None:
        cid = w.crown[0]
        for c, o in w.occ.items():
            if o[1] and (o[0] & 4095) == cid:
                for n in w.dest(c):
                    if n >= 0:
                        crown_flank.add(n)
    need = max(L + P["slack"], P["min_area"])
    if L >= 10:  # long bodies need margin: others fill in behind them
        long_cap = P["flood_cap_long"]
        if w.RND >= P.get("flood_cap_late_from", 501):
            long_cap = min(long_cap, P.get("flood_cap_long_late", long_cap))
        if (
            w.RND >= P.get("flood_cap_late_from", 501)
            and w.UNITS <= P.get("big_cap_sparse_units", 0)
        ):
            long_cap = max(long_cap, P.get("flood_cap_long_sparse", long_cap))
        need = min(need + L // 3, long_cap)
    else:
        need = min(need, P["flood_cap"])
    ranked = []
    best_s = -1e18
    roomy_moves = 0
    ally = w.ally_heads
    info_aggro = (
        P["info_aggro_push"] > 0.0
        and P["density_policy"] == 1
        and roles.ROLE[0] == "forager"
        and w.RND < P["info_aggro_until"]
        and w.UNITS / max(1, w.LIMIT) >= P["info_aggro_sat"]
    )
    # Keep the proven v17 sprint range while the team is sparse. At high
    # population, bound long-body three-step enumeration for the whole dense
    # phase, including late Big Empty turns. This CPU guard is independent of
    # the optional information-gradient push (disabled in this policy line).
    saturated_density = (
        P["density_policy"] == 1
        and w.UNITS / max(1, w.LIMIT) >= P["info_aggro_sat"]
    )
    sprint_limit = P["sprint3_saturated_limit"] if saturated_density else P["sprint3_limit"]
    if w.RND >= P.get("sprint3_late_from", 501):
        sprint_limit = min(sprint_limit, P.get("sprint3_late_limit", sprint_limit))
    if (
        w.RND >= P.get("sprint3_late_from", 501)
        and w.UNITS <= P.get("big_cap_sparse_units", 0)
    ):
        sprint_limit = max(sprint_limit, P.get("sprint3_sparse_limit", sprint_limit))
    for path in candidates(body, sprint_limit):
        st, nb, eaten, hit = tx.sim(path, body)
        steps = len(path)
        if st == "dead":
            s = -1000.0 - steps
        elif st == "dive":  # unknown landing: risk grows with what we carry
            s = P["dive_base"] - P["p_dive"] * dragon_value(L)
            if MEM.get("dive", -1) == path[0] and target == w.HEAD:
                s += P["v_dive"] * 0.5
            s -= threat_cost(w.HEAD, L, threat) * 0.5
        elif st == "h2h":
            s = strike_value(hit, steps)
            if s is None:  # a bad trade still beats dying alone; a friend never
                s = -950.0 if hit in w.elen else -1100.0
        else:
            h = nb[-1]
            dl = len(nb) - L
            s = lv * dl - P["w_sprint"] * (steps - 1)
            if tx.BLIND[0]:  # a portal exit we cannot see may hold a head
                if P["blind_mem"] and tx.BLINDCELL[0] >= 0:
                    risk = blind_risk(tx.BLINDCELL[0])
                else:
                    risk = P["p_blind"]
                s -= risk * dragon_value(len(nb))
            if eaten:
                s += 0.5 * eaten  # tie-break towards material now
            # position: progress towards the target
            s += P["w_goal"] * prog[path[0]] * (1.0 if steps == 1 else 0.7)
            # trap
            area = tx.flood(nb, need, 0)
            if area >= len(nb) + 2 and tx.exits(nb) > 0:
                roomy_moves += 1
            if area < need:
                pen = P["w_trap"] * (need - area) / need
                if area < len(nb):
                    pen += P["w_trap"]
                # a farm: enough pearls inside to grow, and a tail long enough
                # to be outside when we get stuck -> escape split at the end
                k = tx.POCKET[0]
                if len(nb) + k >= P["split_min"] and len(nb) + k > area + 1 \
                        and w.UNITS < w.LIMIT:
                    pen *= P["farm_factor"]
                # what a trap can cost scales with what we carry
                vs = dragon_value(len(nb)) / P["v_ref"]
                if vs > 1.0:
                    pen *= vs
                s -= pen
            # threat
            s -= threat_cost(h, len(nb), threat)
            # crowding
            for hc, hid in ally:
                dd = w.tdist(hc, h)
                if dd <= 2:
                    s -= P["w_crowd"] * (3 - dd)
            s -= P["w_visit"] * w.visits[h]
            if P["density_policy"] == 2 and roles.ROLE[0] == "forager":
                s += density.gradient_score(h)
            if info_aggro:
                room = tx.flood(nb, P["info_room_cap"], 0)
                room_factor = min(1.0, room / max(1.0, P["info_room_norm"]))
                # Gavroche stores allied-minus-enemy counts; invert to push
                # toward enemy control, matching Von Neumann's sign convention.
                s -= P["info_aggro_push"] * density.gradient_score(h) * room_factor
            if h in crown_flank:
                s -= P["w_flank"]
            if DBG is not None:
                DBG.append((path, round(s, 1), area))
            if w.bed[h] == 2 and w.spawn.get(h, -9) == w.RND + 1:
                s -= P["w_bed_block"]
        ranked.append((s, ("move", path)))
        best_s = max(best_s, s)
    sp = split_option(body, threat, need)
    if sp is not None:
        ranked.append(sp)
        best_s = max(best_s, sp[0])
    rescue = opening_rescue_split(body)
    if rescue is not None:
        ranked.append(rescue)
        best_s = max(best_s, rescue[0])
    if best_s < -900:
        esc = escape_split(body)
        if esc is not None:
            ranked.append((-500.0, esc))
    elif roomy_moves == 0 and best_s < P.get("escape_split_trigger", 0.0):
        # Do not wait for every move to become lethal if every move enters a
        # pocket too small to route the current body through safely.
        esc = escape_split(body)
        if esc is not None:
            ranked.append((P.get("escape_split_value", 8.5), esc))
    return ranked


def opening_rescue_split(body):
    """Prioritize long-tail rescue, then reproduce through the opening.

    Initial long dragons can extend beyond the local body view, preventing the
    fully checked split path from running. First transfer the large tail to a
    new head, leaving a two-segment decoy. Once that rescue window passes,
    permit ordinary two-segment production while the body remains incomplete.
    """
    L = w.LEN
    if w.UNITS >= w.LIMIT or roles.ROLE[0] != "forager":
        return None
    if w.RND >= P["split_stop"] or w.RND >= P["grow_from"]:
        return None
    if len(body) >= L:
        return None  # the ordinary, fully checked split path owns this case

    initial = (w.ME & 4095) < P["opening_initial_id_limit"]
    moved_since_birth = w.RND > w.BORN
    if (L >= P["opening_rescue_min_len"]
            and w.RND <= P["opening_rescue_until"]
            and w.BORN <= P["opening_rescue_until"]
            and (initial or moved_since_birth)):
        n = L - 2
        value = P["opening_rescue_value"] + 0.1 * (L - P["opening_rescue_min_len"])
        return value, ("split", n)

    if not (P["opening_production_start"] <= w.RND <= P["opening_production_until"]):
        return None
    if L < P["split_min"] or w.UNITS >= P["opening_production_unit_cap"]:
        return None
    return P["opening_production_value"], ("split", P["child"])


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


def threat_cost(h, newlen, threat):
    """Expected loss from enemy heads that can reach h before our next turn.
    Opponents in the pool trade into LONGER targets, so the chance depends
    on the length comparison."""
    ts = threat.get(h)
    if not ts:
        return 0.0
    mine = dragon_value(newlen)
    cost = 0.0
    for steps, eid, el in ts:
        if newlen > el:
            p = P["p_long"]
        elif newlen == el:
            p = P["p_eq"]
        else:
            p = P["p_short"]
        if steps > 1:
            p *= P["p_sprint"]
        loss = mine - P["k_their"] * dragon_value(el)
        if loss < P["threat_base"]:
            loss = P["threat_base"]
        c = p * loss
        if c > cost:
            cost = c
    return P["w_threat"] * cost


def support_count():
    """Visible allied heads close enough to support a head-to-head trade."""
    radius = P["support_r"]
    return sum(1 for hc, _hid in w.ally_heads if w.tdist(hc, w.HEAD) <= radius)


def strike_value(eid, steps):
    if eid not in w.elen:
        return None  # an ally head
    if not P["attack"] or w.UNITS < P["atk_units"]:
        return None
    theirs = dragon_value(w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0))
    mine = dragon_value(w.LEN)
    gain = theirs - mine - P["w_sprint"] * (steps - 1)
    if P["w_support"]:
        gain += P["w_support"] * min(support_count(), P["support_cap"])
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
    s = P["split_val"]
    pneed = min(max(L - n + P["slack"], P["min_area"]), P["flood_cap"])
    area = tx.flood(parent, pneed, 0)
    if area < pneed:
        s -= P["w_trap"] * (pneed - area) / pneed
    s -= threat_cost(w.HEAD, L - n, threat)
    if threat.get(ch):
        s -= 1.0
    return s, ("split", n)

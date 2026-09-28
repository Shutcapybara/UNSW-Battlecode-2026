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


def opening():
    """TIDUS: the scouting phase of the three-phase structure."""
    return P["phase_open"] > 0 and w.RND < P["phase_open"]


def midgame():
    """TIDUS: the frontier phase -- density at the frontier is allowed."""
    return P["crowd_mid"] != 1.0 and P["phase_open"] <= w.RND < P["grow_from"]
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
            if s > arr:  # not there yet when we arrive
                if P["bed_wait"] > 0:
                    v = P["v_bed"] * (1.0 - (s - arr) / P["bed_wait"])
                # bed_wait 0: arrival-only (waiting for beds made dragons dither)
            elif s > rnd:
                v = P["v_bed"]
            elif w.bper.get(c, 99) <= P["fast_per"]:  # fast bed: regrows while out of view
                v = P["v_bed"] * P["fast_mult"]
            else:  # predicted to have spawned while out of view
                age = rnd - s
                if age <= P["bed_stale"]:
                    v = P["v_bed"] * (1.0 - 0.5 * age / P["bed_stale"])
                else:
                    v = P["v_bed"] * 0.3
        if P["bed_per_k"] > 0:  # a fast bed is worth many pearls, not one
            per = w.bper.get(c, 0)
            if 0 < per < P["bed_per_ref"]:  # boost only: slow beds keep full value
                v *= min(P["bed_per_cap"], 1.0 + P["bed_per_k"] * (P["bed_per_ref"] / per - 1.0))
    elif w.seen[c] == 0:
        v = P["v_unseen"] + (P["unseen_open"] if opening() else 0.0)
    if v <= 0:
        return 0.0
    role = roles.ROLE[0]
    if role == "crown":
        return v
    if w.crown is not None and roles.fresh() and w.RND >= P["crown_from"]:
        rad = P["crown_food"] if w.RND >= roles.feed_from() else P["crown_food_early"]
        if w.tdist(c, w.crown[1]) <= rad:
            return 0.0  # the crown's surroundings are its food
    edisc = P["enemy_disc"]
    if P["fast_edisc"] > 0 and w.bed[c] == 2 and w.bper.get(c, 99) <= P["fast_edisc_per"] \
            and (P["fast_edisc_nc"] <= 0 or P["fast_edisc_nc_min"] <= w.NC <= P["fast_edisc_nc"]):
        edisc = P["fast_edisc"]  # arriving first does not monopolise a fast bed
    # ownership: a clearly closer head takes it first
    own = P["own_disc"] * (P["own_open"] if opening() else 1.0)
    for hc, hid in ally:
        dd = w.tdist(hc, c)
        if dd < t or (dd == t and hid < w.ME):
            v *= own
            break
    for hc in enemy:
        if w.tdist(hc, c) < t:
            v *= edisc
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
    vmax = P["v_unseen"] + (P["unseen_open"] if opening() else 0.0)
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
                if n == -3 and not crown and not feeder and w.UNITS < P["dive_units"]:
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
def candidates(body):
    """Move paths worth evaluating: single steps always; 2-3 step sprints only
    with an enemy head near (strike / escape).  Long dragons (CPU: every
    candidate costs a body copy and a flood) sprint 2 steps at most, and only
    with an enemy head within 3."""
    out = [[d] for d in range(4)]
    L = w.LEN
    if L < 3:
        return out
    near = 9
    for ec, eid in w.enemy_heads:
        dd = w.cheb(ec, w.HEAD)
        if dd < near:
            near = dd
    if near > 4:
        return out
    long_body = L >= P["long_len"]
    out.extend(strike_paths(body))
    if long_body and near > 3:
        return out
    for d1 in range(4):
        for d2 in range(4):
            if d2 == (d1 + 2) % 4:
                continue
            out.append([d1, d2])
            if L >= 4 and not long_body:
                for d3 in range(4):
                    if d3 == (d2 + 2) % 4:
                        continue
                    out.append([d1, d2, d3])
    return out


def local_superiority(ec):
    """More allied heads than enemy heads within atk_space_rad of the target
    cell: a trade here frees space we can refill faster than they can."""
    na = sum(1 for hc, hid in w.ally_heads if w.tdist(hc, ec) <= P["atk_space_rad"])
    ne = sum(1 for hc, _ in w.enemy_heads if w.tdist(hc, ec) <= P["atk_space_rad"])
    return na > ne


def strike_admits(el, ec):
    """Material trade-up (always), or a space trade on compact maps: a short
    dragon of ours trading any small enemy while allies outnumber enemies
    around the target (atk_space, default off)."""
    mine = dragon_value(w.LEN)
    gain = dragon_value(el) - mine
    if gain >= P["atk_margin"]:
        return True
    if P["atk_space"] and compact_prod() and w.LEN <= P["atk_space_len"] \
            and gain >= P["atk_space_margin"] and local_superiority(ec):
        SPLITSTAT["space_strike_admitted"] = SPLITSTAT.get("space_strike_admitted", 0) + 1
        return True
    return False


def strike_paths(body):
    """Shortest free paths (up to len-1 steps, max strike_reach) onto the head
    of a visible enemy that is worth a trade; sims verify them exactly."""
    L = w.LEN
    if not P["attack"] or w.UNITS < P["atk_units"] or L < 3:
        return []
    reach = min(L - 1, P["strike_reach"])
    if reach <= 3:
        return []  # covered by the ordinary sprint candidates
    goals = {}
    for ec, eid in w.enemy_heads:
        if w.tdist(ec, w.HEAD) > reach:
            continue
        el = w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0)
        if strike_admits(el, ec):
            goals[ec] = eid
    if not goals:
        return []
    own = set(body)
    occ = w.occ
    prev = {w.HEAD: (-1, -1)}
    q = [w.HEAD]
    qi = 0
    depth = {w.HEAD: 0}
    out = []
    while qi < len(q):
        c = q[qi]
        qi += 1
        dc = depth[c]
        if dc >= reach:
            continue
        g = w.dest(c)
        for d in range(4):
            n = g[d]
            if n < 0 or n in depth:
                continue
            if n in goals:
                path = [d]
                x = c
                while x != w.HEAD:
                    px, pd = prev[x]
                    path.append(pd)
                    x = px
                path.reverse()
                out.append(path)
                depth[n] = dc + 1
                continue
            if n in own or n in occ:
                continue
            depth[n] = dc + 1
            prev[n] = (c, d)
            q.append(n)
    return out


def evaluate(threat):
    """Return (score, action) with action = ('move', path) or ('split', n)."""
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
                    return 0.0, ("move", [d])
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
    if P["crowd_need"]:  # allies around us fill freed cells: ask for more room
        near = 0
        for hc, hid in w.ally_heads:
            if w.tdist(hc, w.HEAD) <= P["crowd_rad"]:
                near += 1
        need += int(P["crowd_need"] * near)
    if L >= 10:  # long bodies need margin: others fill in behind them
        need = min(need + L // 3, P["flood_cap_long"])
    else:
        need = min(need, P["flood_cap"])
    best = None
    best_s = -1e18
    ally = w.ally_heads
    strikes = []
    firsts = {}
    for path in candidates(body):
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
                    s -= blind_risk(tx.BLINDCELL[0]) * dragon_value(len(nb))
                else:
                    s -= P["p_blind"] * dragon_value(len(nb))
            if eaten:
                s += 0.5 * eaten  # tie-break towards material now
            # position: progress towards the target
            s += P["w_goal"] * prog[path[0]] * (1.0 if steps == 1 else 0.7)
            # trap
            area = tx.flood(nb, need, 0)
            if area < need:
                # soft shortfall (room for our body, not for the margin) vs a real trap
                wt = P["w_trap"] if area <= len(nb) else P["w_trap_soft"]
                pen = wt * (need - area) / need
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
            # crowding (opening: scouting posture -- spread out; mid: the
            # frontier wants density, so relax the repulsion)
            if opening():
                wc = P["w_crowd"] * P["crowd_open"]
            elif midgame():
                wc = P["w_crowd"] * P["crowd_mid"]
            else:
                wc = P["w_crowd"]
            for hc, hid in ally:
                dd = w.tdist(hc, h)
                if dd <= 2:
                    s -= wc * (3 - dd)
            s -= P["w_visit"] * w.visits[h]
            if P["wall_open"] > 0 and opening() and steps == 1:
                kelp = sum(1 for n in w.dest(h) if n == -1)
                if kelp >= P["wall_open_min"]:
                    s -= P["wall_open"] * (kelp - P["wall_open_min"] + 1)
            if h in crown_flank:
                s -= P["w_flank"]
            if DBG is not None:
                DBG.append((path, round(s, 1), area))
            if w.bed[h] == 2 and w.spawn.get(h, -9) == w.RND + 1:
                s -= P["w_bed_block"]
        if s > best_s:
            best_s = s
            best = ("move", path)
        if LADDER[0]:
            if st == "h2h" and s > -900:
                strikes.append((s, path))
            elif st == "ok" and len(path) == 1:
                firsts[(path[0],)] = s
    sp = split_option(body, threat, need)
    if sp is not None and sp[0] > best_s:
        best_s, best = sp
        SPLITSTAT["chosen"] = SPLITSTAT.get("chosen", 0) + 1
    elif sp is not None:
        SPLITSTAT["argmax_lost"] = SPLITSTAT.get("argmax_lost", 0) + 1
    if LADDER[0] and roles.ROLE[0] == "forager" and best_s > -900:
        lad = ladder(sp, strikes, firsts, dist, mask)
        if lad is not None:
            return lad
    if best_s < -900:
        esc = escape_split(body)
        if esc is not None:
            return -500.0, esc
    return best_s, best


LADDER = [False]  # set at start-up: compact maps use the priority ladder


def ladder(sp, strikes, firsts, dist, mask):
    """Hunter-style priority ladder over the evaluated candidates (compact
    maps): strike a longer head, else split, else step towards the nearest
    visible pearl we own -- each only if the evaluator does not price it as
    dangerous (score above ladder_floor)."""
    floor = P["ladder_floor"]
    if strikes:
        strikes.sort(reverse=True)
        return strikes[0][0], ("move", strikes[0][1])
    if sp is not None and sp[0] > P["split_val"] + floor:
        return sp
    ally = w.ally_heads
    best = -1
    bt = 1 << 30
    rnd = w.RND
    for c, t in dist.items():
        if t == 0 or t >= bt or w.pearls.get(c) != rnd:
            continue
        mine = True
        for hc, hid in ally:
            dd = w.tdist(hc, c)
            if dd < t or (dd == t and hid < w.ME):
                mine = False
                break
        if mine:
            bt = t
            best = c
    if best < 0:
        return None
    m = mask.get(best, 0)
    choice = None
    cs = -1e18
    for d in range(4):
        if (m >> d) & 1:
            sc = firsts.get((d,), None)
            if sc is not None and sc > floor and sc > cs:
                cs = sc
                choice = d
    if choice is None:
        return None
    return cs, ("move", [choice])


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


def blind_risk(c):
    """Portal-exit risk from sighting memory (valjean-v01): a body seen near
    the exit recently is near-certain death; a surveyed quiet exit is cheap;
    an unknown exit is half risk."""
    r = w.RND
    fresh = P["blind_fresh"]
    if w.body_seen.get(c, -999) >= r - fresh:
        return P["r_body"]
    for n in w.nbr(c):
        if w.body_seen.get(n, -999) >= r - fresh:
            return P["r_body"]
    s = w.seen[c]
    if s and r - (s - 1) <= fresh:  # we looked at the exit and it was quiet
        return P["r_seen"]
    return P["r_unseen"]


def threat_cost(h, newlen, threat):
    """Expected loss from enemy heads that can reach h before our next turn.
    Opponents in the pool trade into LONGER targets, so the chance depends
    on the length comparison.  Nearby allied heads discount the risk: a
    supported dragon is expensive to trade into (the neighbour counters)."""
    ts = threat.get(h)
    if not ts:
        return 0.0
    mine = dragon_value(newlen)
    cost = 0.0
    young = P["guard_age"] > 0 and w.RND - w.BORN < P["guard_age"]
    for steps, eid, el, ec in ts:
        if newlen > el:
            p = P["p_long"]
        elif newlen == el:
            p = P["p_eq"]
        else:
            p = P["p_short"]
        if young:
            p = max(p, P["guard_p"])  # a newborn assumes everyone will bother
            SPLITSTAT["guard_priced"] = SPLITSTAT.get("guard_priced", 0) + 1
        if steps > 1:
            p *= P["p_sprint"]
        loss = mine - P["k_their"] * dragon_value(el)
        if loss < P["threat_base"]:
            loss = P["threat_base"]
        c = p * loss
        if c > cost:
            cost = c
    if P["threat_ally"] > 0 and cost > 0 and (P["threat_ally_all"] or compact_prod()):
        if P["threat_ally_foe"]:
            # support counts around the ATTACKER, and only allies long enough
            # to hurt it: a small feeder beside a crown deters nobody
            n = sum(1 for hc, hid in w.ally_heads
                    if any(w.alen.get(hid, 1) >= el2 and w.tdist(hc, ec) <= P["support_rad"]
                           for _, eid2, el2, ec in ts))
        else:
            n = sum(1 for hc, hid in w.ally_heads if w.tdist(hc, h) <= P["support_rad"])
        cost *= max(0.25, (1.0 - P["threat_ally"]) ** n)
    return P["w_threat"] * cost


def strike_value(eid, steps):
    if eid not in w.elen:
        return None  # an ally head
    if not P["attack"] or w.UNITS < P["atk_units"]:
        return None
    theirs = dragon_value(w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0))
    mine = dragon_value(w.LEN)
    gain = theirs - mine  # we die anyway: sprint cost is irrelevant
    if gain < P["atk_margin"]:
        ec = -1
        for c, i in w.enemy_heads:
            if i == eid:
                ec = c
                break
        if ec < 0 or not (P["atk_space"] and compact_prod() and w.LEN <= P["atk_space_len"]
                          and gain >= P["atk_space_margin"] and local_superiority(ec)):
            return None
        SPLITSTAT["space_strike_scored"] = SPLITSTAT.get("space_strike_scored", 0) + 1
    sup = 0.0
    if P["strike_support"] > 0:  # friends nearby can pounce on the corpse
        ec = -1
        for c, i in w.enemy_heads:
            if i == eid:
                ec = c
                break
        if ec >= 0:
            n = sum(1 for hc, hid in w.ally_heads if w.tdist(hc, ec) <= P["support_rad"])
            sup = min(P["support_cap"], P["strike_support"] * n)
    return P["strike_bonus"] + gain + sup


def compact_prod():
    """Compact-map production doctrine (ouroboros-v13): below the unit
    target the team keeps producing even in the endgame (until unit_stop_round)."""
    return (P["compact_nc"] > 0 and w.NC <= P["compact_nc"] and w.UNITS < P["unit_target"]
            and w.RND < P["unit_stop_round"])


SPLITSTAT = {}  # Newton instrumentation: split-decision funnel (counters only)


def split_option(body, threat, need):
    L = w.LEN
    n = P["child"]
    if L >= P["split_min"]:
        SPLITSTAT["eligible"] = SPLITSTAT.get("eligible", 0) + 1
    if L < P["split_min"] or L - n < 2 or w.UNITS >= w.LIMIT:
        return None
    if (w.RND >= P["split_stop"] or w.RND >= P["grow_from"]) and not compact_prod():
        SPLITSTAT["stop"] = SPLITSTAT.get("stop", 0) + 1
        return None
    if roles.ROLE[0] != "forager":
        if P["crown_split"] and roles.ROLE[0] == "crown" and compact_prod():
            SPLITSTAT["crown_split_admitted"] = SPLITSTAT.get("crown_split_admitted", 0) + 1
        else:
            SPLITSTAT["role:" + roles.ROLE[0]] = SPLITSTAT.get("role:" + roles.ROLE[0], 0) + 1
            return None
    if len(body) < L:
        SPLITSTAT["body_unknown"] = SPLITSTAT.get("body_unknown", 0) + 1
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
        SPLITSTAT["no_exit"] = SPLITSTAT.get("no_exit", 0) + 1
        return None
    carea = P["child_area"]
    if compact_prod() and P["compact_child"]:
        carea = min(carea, 3)  # dense compact maps: a 3-cell pocket still lets
        # the newborn turn around; waiting for 4 cedes the fast beds
    if tx.flood(child, carea, 0) < carea:
        SPLITSTAT["child_area"] = SPLITSTAT.get("child_area", 0) + 1
        return None
    parent = body[n:]
    s = P["split_val"]
    if compact_prod():
        s += P["prod_boost"]
        if P["split_nothreat"]:
            threat = {}  # the parent faces this threat on every branch:
            # splitting spreads the risk to two units instead of adding it
    pneed = min(max(L - n + P["slack"], P["min_area"]), P["flood_cap"])
    area = tx.flood(parent, pneed, 0)
    if area < pneed:
        wt = P["w_trap"]
        if compact_prod() and P["compact_child"]:
            wt *= 0.5  # the swarm doctrine accepts tighter parents
        s -= wt * (pneed - area) / pneed
    s -= threat_cost(w.HEAD, L - n, threat)
    if threat.get(ch):
        s -= 1.0
    SPLITSTAT["proposed"] = SPLITSTAT.get("proposed", 0) + 1
    return s, ("split", n)

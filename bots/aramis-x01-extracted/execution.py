"""Exact extracted Monte Christo mechanisms; not yet semantic intentions."""
import world as w
import tactics as tx
import roles
from params import P
from targets import MEM, choose_target, lv_now, dragon_value
DBG = None

# --------------------------------------------------------------- candidates
def candidates(body):
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
        need = min(need + L // 3, P["flood_cap_long"])
    else:
        need = min(need, P["flood_cap"])
    ranked = []
    best_s = -1e18
    ally = w.ally_heads
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
                s -= P["p_blind"] * dragon_value(len(nb))
            if eaten:
                s += 0.5 * eaten  # tie-break towards material now
            # position: progress towards the target
            s += P["w_goal"] * prog[path[0]] * (1.0 if steps == 1 else 0.7)
            # trap
            area = tx.flood(nb, need, 0)
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
    if best_s < -900:
        esc = escape_split(body)
        if esc is not None:
            ranked.append((-500.0, esc))
    return ranked


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


def strike_value(eid, steps):
    if eid not in w.elen:
        return None  # an ally head
    if not P["attack"] or w.UNITS < P["atk_units"]:
        return None
    theirs = dragon_value(w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0))
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

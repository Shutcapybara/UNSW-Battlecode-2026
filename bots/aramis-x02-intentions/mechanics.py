"""Sinbad/Monte Christo move enumeration, risk and split mechanics."""
import world as w
import tactics as tx
import roles
from params import P

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

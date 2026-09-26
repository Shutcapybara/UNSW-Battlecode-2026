"""DECISION policy P1+CM (version 3): P1 plus two default-off combat
mechanisms.  Von Neumann x02 is the combat master source: with both
mechanism weights at their defaults (0) the scoring path is expression-for-
expression P1, so every behaviour change is a named switch measured against
the frozen x01 baseline.

  CM-1  LENGTH-BALANCE MARGIN (w_margin_balance > 0).  The h2h strike margin
        shifts with the local enemy-minus-ally LENGTH balance from the swarm
        field at our head (evidence-gated: no confidence, no shift).  Enemy-
        heavy waters tighten the margin (harder to trade); allied-heavy waters
        relax it.  Rounds/saturation still gate via P1's aggression term.

  CM-2  SUPPORT-WEIGHTED TRADE GAIN (w_support > 0).  strike_value adds
        w_support per allied head within support_r torus steps of our head
        (capped): a trade next to allies leaves recoverable pearls and a
        punished enemy, so the same material trade is worth more with support.
        Support counts visible allied heads only -- evidence, not faith.

Everything else -- candidates, previews, weights, order, tie-breaks, despair
gate, executors -- is P1's, unchanged.
"""
import world as w
import roles
import targets
from params import P

POLICY_VERSION = 3
DBG = None  # list -> per-candidate (arg, score, area) trace rows when set

DESPAIR = -900.0      # below every ordinary score: admit the emergency split
ESCAPE_SCORE = -500.0


def threat_cost(tlist, newlen):
    """Expected loss from enemy heads that can reach a cell before our next
    turn.  Opponents in the pool trade into LONGER targets, so the chance
    depends on the length comparison."""
    if not tlist:
        return 0.0
    mine = targets.dragon_value(newlen)
    cost = 0.0
    for steps, eid, el in tlist:
        if newlen > el:
            p = P["p_long"]
        elif newlen == el:
            p = P["p_eq"]
        else:
            p = P["p_short"]
        if steps > 1:
            p *= P["p_sprint"]
        loss = mine - P["k_their"] * targets.dragon_value(el)
        if loss < P["threat_base"]:
            loss = P["threat_base"]
        c = p * loss
        if c > cost:
            cost = c
    return P["w_threat"] * cost


def support_count():
    """Visible allied heads within support_r torus steps of our head."""
    r = P["support_r"]
    return sum(1 for hc, _hid in w.ally_heads if w.tdist(hc, w.HEAD) <= r)


def strike_value(eid, steps, margin):
    """Score of ramming enemy head eid, or None when the trade is not
    allowed/worth it (a friend, attacks off, too few units, gain below the
    -- possibly phase-relaxed / balance-shifted / support-weighted -- margin)."""
    if eid not in w.elen:
        return None  # an ally head
    if not P["attack"] or w.UNITS < P["atk_units"]:
        return None
    theirs = targets.dragon_value(w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0))
    mine = targets.dragon_value(w.LEN)
    gain = theirs - mine - P["w_sprint"] * (steps - 1)
    if P["w_support"]:
        gain += P["w_support"] * min(support_count(), P["support_cap"])
    if gain < margin:
        return None
    return 2.0 + gain


def aggression(gf):
    """Early + saturated -> frontier dragons contest space aggressively."""
    if gf["early"] and gf["sat"] >= P["aggro_sat"] and roles.ROLE[0] == "forager":
        return True
    return False


def balance_at_head(gf):
    """CM-1 input: enemy-minus-ally LENGTH balance at our head from the swarm
    field, 0.0 without usable evidence.  Positive = enemy-heavy."""
    a, e, conf = gf["lengths"]
    if conf <= 0.0:
        return 0.0
    return (e - a) / (a + e + P["swarm_damp"])


def score(cand, tf, gf, threat):
    """V(candidate); P1's branches with the CM adjustments behind switches."""
    lv = targets.lv_now()
    L = w.LEN
    if cand["mode"] == "split":
        if cand["emergency"]:
            return ESCAPE_SCORE
        pv = cand["preview"]
        n = cand["arg"]
        s = P["split_val"]
        # P1-2: graded confinement of BOTH bodies scales the split's value;
        # a scarce team values children more.
        room = pv["child_room"] + pv["parent_area"]
        rf = room / P["split_room_norm"]
        if rf < 1.0:
            s *= max(P["split_room_floor"], rf)
        s += P["split_sat_w"] * (0.5 - gf["sat"])
        if pv["parent_area"] < pv["pneed"]:
            s -= P["w_trap"] * (pv["pneed"] - pv["parent_area"]) / pv["pneed"]
        s -= threat_cost(pv["threat_at_head"], L - n)
        if pv["threat_at_child"]:
            s -= 1.0
        return s
    pv = cand["preview"]
    path = cand["arg"]
    steps = pv["steps"]
    st = pv["outcome"]
    if cand["exclusive"]:
        return 0.0  # FEED_ALLY donation: the legacy short-circuit score
    if st == "dead":
        return -1000.0 - steps
    if st == "dive":  # unknown landing: risk grows with what we carry
        s = P["dive_base"] - P["p_dive"] * targets.dragon_value(L)
        if targets.MEM.get("dive", -1) == path[0] and cand["target"] == w.HEAD:
            s += P["v_dive"] * 0.5
        s -= threat_cost(pv["threat_at_head"], L) * 0.5
        return s
    aggro = aggression(gf)
    if st == "h2h":
        # P1-1: the strike margin relaxes when trades buy space; CM-1 shifts
        # it with the local length balance (evidence-gated).
        margin = P["atk_margin"] - (P["aggro_relax"] if aggro else 0.0)
        if P["w_margin_balance"]:
            margin += P["w_margin_balance"] * balance_at_head(gf)
        s = strike_value(pv["hit"], steps, margin)
        if s is not None:
            return s
        # a bad trade still beats dying alone; a friend never
        return -950.0 if pv["hit"] in w.elen else -1100.0
    nb = pv["body_after"]
    dl = pv["len_after"] - L
    s = lv * dl - P["w_sprint"] * (steps - 1)
    if pv["blind"]:  # a portal exit we cannot see may hold a head
        s -= P["p_blind"] * targets.dragon_value(pv["len_after"])
    if pv["eaten"]:
        s += 0.5 * pv["eaten"]  # tie-break towards material now
    # position: progress towards the target, discounted by its density
    # evidence (P1-3: contested or crowded targets are worth less)
    s += P["w_goal"] * pv["prog"] * (1.0 if steps == 1 else 0.7) * tf["res_factor"]
    # P1-1b: saturated opening dragons push toward enemy length density
    if aggro:
        s += P["aggro_push"] * pv["swarm_gain"]
    # trap
    need = tf["need"]
    area = pv["area"]
    if area < need:
        pen = P["w_trap"] * (need - area) / need
        if area < pv["len_after"]:
            pen += P["w_trap"]
        # a farm: enough pearls inside to grow, and a tail long enough
        # to be outside when we get stuck -> escape split at the end
        k = pv["pocket"]
        if pv["len_after"] + k >= P["split_min"] and pv["len_after"] + k > area + 1 \
                and w.UNITS < w.LIMIT:
            pen *= P["farm_factor"]
        # what a trap can cost scales with what we carry
        vs = targets.dragon_value(pv["len_after"]) / P["v_ref"]
        if vs > 1.0:
            pen *= vs
        s -= pen
    # threat
    s -= threat_cost(pv["threat_at_head"], pv["len_after"])
    # crowding
    for hc, hid in w.ally_heads:
        dd = w.tdist(hc, pv["head_after"])
        if dd <= 2:
            s -= P["w_crowd"] * (3 - dd)
    s -= P["w_visit"] * pv["visits"]
    if pv["flank"]:
        s -= P["w_flank"]
    if pv["bed_block"]:
        s -= P["w_bed_block"]
    return s


def choose(cands, tf, gf):
    """Score every available candidate and select the maximum, first-in on
    ties.  Emergency RETREAT candidates are admitted only when no ordinary
    candidate beats the despair threshold (the legacy escape-split gate)."""
    threat = gf["threat"]
    ordinary = [c for c in cands if not c["emergency"]]
    emergency = [c for c in cands if c["emergency"]]
    ranked = []
    best_s = -1e18
    for c in ordinary:
        s = score(c, tf, gf, threat)
        c["score"] = s
        ranked.append(c)
        best_s = max(best_s, s)
        if DBG is not None:
            DBG.append((c["arg"], round(s, 1), c["preview"].get("area", -1)))
    if best_s < DESPAIR:
        for c in emergency:
            c["score"] = score(c, tf, gf, threat)
            ranked.append(c)
    best = None
    for c in ranked:
        if best is None or c["score"] > best["score"]:
            best = c
    return best, ranked

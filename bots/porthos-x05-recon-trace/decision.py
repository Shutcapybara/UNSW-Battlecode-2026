"""DECISION policy P0+recon (version 3): P0's field + recon objective scoring.

The scoring is the legacy Monte Christo v01 field, decomposed over the
candidate/preview records but numerically identical: same weights from
params.P, same expression order, same candidate order, first-in tie-break.
P0 does not change pathing, legality, target generation or any executor's
search cap; it only maps (candidate, preview, features) -> score.

V(candidate) = material + position (route progress to target) - trap - threat
              - crowding - dithering (+ strike value, + split value)

v3 ADDS one branch: mode "recon" candidates (portal reconnaissance, C2/E2)
are scored from the bounded executor preview -- route distance and a safe
first step -- plus the information value of the portal's unseen sector and
the honest unknown-landing risk.  All other candidates score exactly as P0.
"""
import world as w
import targets
import executors
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


def strike_value(eid, steps):
    """Score of ramming enemy head eid, or None when the trade is not
    allowed/worth it (a friend, attacks off, too few units, margin too small)."""
    if eid not in w.elen:
        return None  # an ally head
    if not P["attack"] or w.UNITS < P["atk_units"]:
        return None
    theirs = targets.dragon_value(w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0))
    mine = targets.dragon_value(w.LEN)
    gain = theirs - mine - P["w_sprint"] * (steps - 1)
    if gain < P["atk_margin"]:
        return None
    return 2.0 + gain


def score(cand, tf, threat):
    """V(candidate); mirrors the legacy rank_actions branches one for one.
    v3: recon objectives score from their bounded executor preview."""
    if cand["mode"] == "recon":
        rp = cand.get("recon_preview")
        if rp is None:
            rp = executors.preview_recon(cand)   # bounded, commits nothing
            cand["recon_preview"] = rp
        if not rp["available"]:
            return -1e18
        c = cand["target"]
        sec = ((c // w.W) // w.SEC) * w.SW + (c % w.W) // w.SEC
        frac = w.sec_unseen[sec] / 64.0   # information value of the region
        s = P["recon_val"] * (P["gamma"] ** rp["steps"])
        s += P["recon_info_w"] * frac
        s -= P["p_dive"] * targets.dragon_value(w.LEN) * 0.5
        return s
    lv = targets.lv_now()
    L = w.LEN
    if cand["mode"] == "split":
        if cand["emergency"]:
            return ESCAPE_SCORE
        pv = cand["preview"]
        n = cand["arg"]
        s = P["split_val"]
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
    if st == "h2h":
        s = strike_value(pv["hit"], steps)
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
    # position: progress towards the target
    s += P["w_goal"] * pv["prog"] * (1.0 if steps == 1 else 0.7)
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


def choose(cands, tf, threat):
    """Score every available candidate and select the maximum, first-in on
    ties.  Emergency RETREAT candidates are admitted only when no ordinary
    candidate beats the despair threshold (the legacy escape-split gate)."""
    ordinary = [c for c in cands if not c["emergency"]]
    emergency = [c for c in cands if c["emergency"]]
    ranked = []
    best_s = -1e18
    for c in ordinary:
        s = score(c, tf, threat)
        c["score"] = s
        ranked.append(c)
        best_s = max(best_s, s)
        if DBG is not None:
            DBG.append((c["arg"], round(s, 1), c["preview"].get("area", -1)))
    if best_s < DESPAIR:
        for c in emergency:
            c["score"] = score(c, tf, threat)
            ranked.append(c)
    best = None
    for c in ranked:
        if best is None or c["score"] > best["score"]:
            best = c
    return best, ranked

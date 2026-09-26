"""DECISION policy P1+INFO (version 4): P1 plus three default-off consumers
of the x06 information layer (dual-window EWMA fields, room-normalised
spatial gains).  With every information weight at its default the scoring
path is expression-for-expression P1.

  INFO-1  ROOM-NORMALISED GRADIENT PUSH (w_grad = 1): the early-saturation
          push toward enemy length density follows the gradient damped by
          the bounded room at the landing cell -- the same enemy control in
          a tight corridor is worse to push into than in open water.
  INFO-2  SELF-RELATIVE BALANCE MARGIN (w_mb2 > 0): the strike margin shifts
          with the SHORT-window enemy-minus-ally balance, damped by our own
          length and by game phase.  Evidence-gated (no confidence, no shift).
  INFO-3  CONTACT-SCALES THREAT (w_tf > 0): threat_cost scales up when the
          short-window field confirms enemy length near our head.

The original P1 docstring follows:
P0's field, re-parameterised on game state.

P0 (version 1, porthos-x02/x03) scores candidates with fixed weights.  P1
keeps P0's structure and candidate/executor behaviour byte-for-byte, but
conditions four choices on the v2 game-relative features (phase, population
saturation, confinement, density evidence).  All directions come from the
evidence (targets, density fields); no compass constant appears.

  V(candidate) = material + position - trap - threat - crowding - dithering
                 (+ strike value, + split value)         [P0, unchanged]

  P1 adjustments:
  1. EARLY-SATURATION AGGRESSION.  In the opening (round < aggro_until) with
     a near-saturated team (units/limit >= aggro_sat), extra dragons cannot
     become children, so their marginal value is the space they contest:
     the strike margin relaxes by aggro_relax (even-ish trades become
     acceptable) and surviving moves gain aggro_push x swarm_gain (a push
     toward enemy length density).  Foragers only; the crown never pushes.
  2. CONFINEMENT-GATED PRODUCTION.  A split's base value scales with the
     GRADED room available to both bodies (child_room + parent_area over
     split_room_norm, floored): the same length in a pocket is not the same
     as in the open, so confined dragons split less eagerly.  A scarce team
     (low saturation) adds split_sat_w x (0.5 - sat).
  3. DENSITY-DISCOUNTED PROGRESS.  The positional term toward the nominated
     target is multiplied by the target's resource_factor (v07's selected
     hook): pushing toward ally-crowded or enemy-contested cells is worth
     less; direct vision still takes precedence inside resource_factor.

Everything else -- candidate set, target search, previews, weights, order,
tie-breaks, despair gate -- is P0's, so x03 (P0) vs x04 (P1) isolates these
feature consumers.
"""
import world as w
import roles
import targets
from params import P

POLICY_VERSION = 4
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


def strike_value(eid, steps, margin):
    """Score of ramming enemy head eid, or None when the trade is not
    allowed/worth it (a friend, attacks off, too few units, gain below the
    -- possibly phase-relaxed -- margin)."""
    if eid not in w.elen:
        return None  # an ally head
    if not P["attack"] or w.UNITS < P["atk_units"]:
        return None
    theirs = targets.dragon_value(w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0))
    mine = targets.dragon_value(w.LEN)
    gain = theirs - mine - P["w_sprint"] * (steps - 1)
    if gain < margin:
        return None
    return 2.0 + gain


def aggression(gf):
    """Early + saturated -> frontier dragons contest space aggressively."""
    if gf["early"] and gf["sat"] >= P["aggro_sat"] and roles.ROLE[0] == "forager":
        return True
    return False


def self_balance(gf):
    """INFO-2 input: SHORT-window enemy-minus-ally length balance at our
    head, damped by our own length (capped) and faded by game phase; 0.0
    without usable evidence."""
    a, e, conf = gf.get("lengths_short", (0.0, 0.0, 0.0))
    if conf <= 0.0:
        return 0.0
    season = 1.0 - 0.5 * gf["phase"]          # evidence ages in value late
    return season * (e - a) / (a + e + min(w.LEN, P["self_len_cap"]))


def _threat_scale(gf):
    """INFO-3 multiplier for threat_cost: >1 only when the short-window field
    confirms enemy length near us; exactly 1.0 when the switch is off."""
    if not P["w_tf"]:
        return 1.0
    return 1.0 + P["w_tf"] * gf.get("contact", 0.0)


def score(cand, tf, gf, threat):
    """V(candidate); P0's branches with the three P1 adjustments."""
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
        s -= threat_cost(pv["threat_at_head"], L - n) * _threat_scale(gf)
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
        s -= threat_cost(pv["threat_at_head"], L) * 0.5 * _threat_scale(gf)
        return s
    aggro = aggression(gf)
    if st == "h2h":
        # P1-1: the strike margin relaxes when trades buy space; INFO-2
        # shifts it with the short-window self-relative balance.
        margin = P["atk_margin"] - (P["aggro_relax"] if aggro else 0.0)
        if P["w_mb2"]:
            margin += P["w_mb2"] * self_balance(gf)
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
    # P1-1b: saturated opening dragons push toward enemy length density;
    # INFO-1 swaps in the room-normalised gradient when enabled.
    if aggro:
        gain = pv["spatial_gain"] if (P["w_grad"] and "spatial_gain" in pv) \
            else pv["swarm_gain"]
        s += P["aggro_push"] * gain
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
    # threat (INFO-3: scaled by confirmed short-window contact)
    s -= threat_cost(pv["threat_at_head"], pv["len_after"]) * _threat_scale(gf)
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

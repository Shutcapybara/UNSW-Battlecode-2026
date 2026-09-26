"""DECISION layer (P0): scores executor previews and nominates one action.

V(candidate) = material + position (route distance to target) - trap - threat
              - crowding - dithering (+ strike value, + split value)
All weights live in params.P.  Extracted verbatim from monte_christo-v01-core
policy.rank_actions / main.choose_action: candidate generation, previews and
search budgets are requested through executors' fixed interface and are never
modified here.  Intention labels classify the nomination for diagnostics;
in this release they do not influence selection (that is the next generation's
deliberate, recorded change).

Candidates are (score, action, intent, note, facts) records (facts = the
executor preview / split facts; None when not applicable); selection is
max(score) with first-occurrence tie-break, exactly like v01's max() over
its list.
"""
import world as w
import executors as ex
import roles
from params import P

DBG = []  # (path, score, area) per candidate when tracing; None in releases

GATHER = "GATHER"
SCOUT = "SCOUT"
ATTACK = "ATTACK"
RETREAT = "RETREAT"
FEED_ALLY = "FEED_ALLY"
REPRODUCE = "REPRODUCE"


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


def progress(target, dist, mask):
    """Progress of each first move towards the target: +1 on a shortest
    route, -1 otherwise; beyond the search, torus distance steers."""
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
    return prog


def ally_reach():
    """Cells an allied head can step into on its next action (1 step, up to
    3 with sprint).  A friendly-fire crossing hazard map for move scoring."""
    out = set()
    for hc, hid in w.ally_heads:
        el = w.alen.get(hid, 2)
        reach = 1 if el < 3 else min(3, el - 1)
        seen = {hc: 0}
        q = [hc]
        qi = 0
        while qi < len(q):
            c = q[qi]
            qi += 1
            dc = seen[c]
            if dc >= reach:
                continue
            for n in w.dest(c):
                if n < 0 or n in seen:
                    continue
                seen[n] = dc + 1
                q.append(n)
                out.add(n)
    return out


def crown_flank():
    """Feeder penalty set: tiles next to the crown's body (would box it in)."""
    flank = set()
    if roles.ROLE[0] == "feeder" and w.crown is not None:
        cid = w.crown[0]
        for c, o in w.occ.items():
            if o[1] and (o[0] & 4095) == cid:
                for n in w.dest(c):
                    if n >= 0:
                        flank.add(n)
    return flank


def rank(threat, plan, moves, split):
    """Score the candidates staged by main.py; returns the ranked records.
    Order of records and arithmetic match v01's rank_actions exactly."""
    body = w.body
    L = w.LEN
    lv = lv_now()
    target = plan["target"]
    dist = plan["dist"]
    mask = plan["mask"]
    prog = progress(target, dist, mask)
    flank = crown_flank()
    need = ex.move_need()
    ally = w.ally_heads
    areach = ally_reach()
    ranked = []
    best_s = -1e18
    for path in moves:
        pv = ex.move_preview(path, body, need)
        steps = len(path)
        st = pv["status"]
        if st == "dead":
            s = -1000.0 - steps
        elif st == "dive":  # unknown landing: risk grows with what we carry
            s = P["dive_base"] - P["p_dive"] * dragon_value(L)
            if ex.MEM.get("dive", -1) == path[0] and target == w.HEAD:
                s += P["v_dive"] * 0.5
            s -= threat_cost(w.HEAD, L, threat) * 0.5
        elif st == "h2h":
            s = strike_value(pv["hit"], steps)
            if s is None:  # a bad trade still beats dying alone; a friend never
                s = -950.0 if pv["hit"] in w.elen else -1100.0
        else:
            nb = pv["body"]
            h = nb[-1]
            dl = len(nb) - L
            s = lv * dl - P["w_sprint"] * (steps - 1)
            if pv["blind"]:  # a portal exit we cannot see may hold a head
                s -= P["p_blind"] * dragon_value(len(nb))
            if pv["eaten"]:
                s += 0.5 * pv["eaten"]  # tie-break towards material now
            # position: progress towards the target
            s += P["w_goal"] * prog[path[0]] * (1.0 if steps == 1 else 0.7)
            # trap
            area = pv["area"]
            if area < need:
                pen = P["w_trap"] * (need - area) / need
                if area < len(nb):
                    pen += P["w_trap"]
                # a farm: enough pearls inside to grow, and a tail long enough
                # to be outside when we get stuck -> escape split at the end
                k = pv["pocket"]
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
            if h in areach:
                s -= P.get("w_ally_reach", 0.35)  # friendly-fire crossing risk
            if h in flank:
                s -= P["w_flank"]
            if DBG is not None:
                DBG.append((path, round(s, 1), area))
            if w.bed[h] == 2 and w.spawn.get(h, -9) == w.RND + 1:
                s -= P["w_bed_block"]
        ranked.append((s, ("move", path), None, "", pv))
        best_s = max(best_s, s)
    if split is not None:
        s = P["split_val"]
        if split["parent_area"] < split["pneed"]:
            s -= P["w_trap"] * (split["pneed"] - split["parent_area"]) / split["pneed"]
        s -= threat_cost(w.HEAD, L - split["n"], threat)
        if threat.get(split["child_head"]):
            s -= 1.0
        ranked.append((s, ("split", split["n"]), REPRODUCE, "production", split))
        best_s = max(best_s, s)
    if best_s < -900:
        esc = ex.escape_split(body)
        if esc is not None:
            ranked.append((-500.0, esc, RETREAT, "escape_split", None))
    return ranked


def select(ranked):
    """v01 selection: max score, first occurrence wins ties."""
    return max(ranked, key=lambda rec: rec[0])


def classify(rec, plan):
    """Diagnostic intention label of the nominated record.  Labels classify
    the chosen action's objective from facts already computed for scoring;
    they do not feed back into selection."""
    score, action, intent, note, pv = rec
    if intent is not None:
        return intent, note
    st = pv["status"]
    if st == "h2h":
        if pv["hit"] in w.elen:
            return ATTACK, "strike" if score > -900 else "forced_contact"
        return RETREAT, "forced_ally_contact"
    if plan["kind"] == "prey":
        base, inote = ATTACK, "hunt"
    elif plan["kind"] == "feeder":
        base, inote = FEED_ALLY, "approach"
    else:
        target = plan["target"]
        if target < 0:
            base, inote = SCOUT, "no_target"
        else:
            pr = w.pearls.get(target)
            if target != w.HEAD and pr is not None and w.RND - pr <= P["mem_ttl"]:
                base, inote = GATHER, "remembered_pearl" if plan["kind"] == "fallback" else ""
            elif w.bed[target] == 2 or target in w.spawn:
                base, inote = GATHER, ""
            elif plan["kind"] == "fallback":
                base, inote = SCOUT, "sector"
            else:
                base, inote = SCOUT, ""    # unseen-cell / portal-dive targets
    if st == "dead":
        return base, "no_surviving_move"
    if st == "dive":
        return SCOUT, "portal_dive"
    return base, inote

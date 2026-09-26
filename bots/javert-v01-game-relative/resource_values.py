"""Inherited resource valuation; executor dependency, never policy features."""
import world as w
import roles
from params import P

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



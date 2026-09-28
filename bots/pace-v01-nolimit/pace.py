"""P1 pace controller (lineage `pace`, v01).

Each turn a dragon compares the team's unit count (UNIT_COUNT from the header)
with P["pace_target"] interpolated at the current round for its map class
(compact <= 625 tiles, else open) and shifts the production/foraging balance:

  MODE +1 (behind by >= pace_push_gap units): production split value raised by
          pace_gain per missing unit (capped).  With pace_limits on, the raised
          value is only granted to splits that pass stricter survival checks
          (child flood >= pace_child_area, no enemy head in reach of the child,
          parent pocket not a trap); a split failing them keeps the host's value.
          With pace_limits off (arm `nolimit`) the checks are skipped and the
          opening production path (no body/exit check) is extended to
          pace_open_until with the unit cap at the target.
  MODE -1 (ahead by >= pace_hold_gap units, from pace_hold_from): production
          held (split value - pace_hold) so dragons grow length instead.
  MODE  0 on pace: the host's parameters.

Total length is not observed by a dragon; the r250 total target is pursued
through its per-dragon share: while pace_food_from <= round <= pace_until and our
length is below target_total / target_units, visible pearls and due beds are
worth (1 + pace_food) x the host's value.

Everything is restored to the host's values when pace_on = 0.
"""
import world as w
import roles
from params import P

KEYS = ("split_val", "opening_production_until", "opening_production_unit_cap",
        "opening_production_value", "v_pearl", "v_bed")
BASE = {k: P[k] for k in KEYS}
MODE = [0]
INFO = [0.0, 0.0]   # target units now, gap


def _interp(pts, r):
    """pts: sorted (round, value); flat outside."""
    if r <= pts[0][0]:
        return pts[0][1]
    for (r0, v0), (r1, v1) in zip(pts, pts[1:]):
        if r <= r1:
            return v0 + (v1 - v0) * (r - r0) / float(r1 - r0)
    return pts[-1][1]


def cls_index():
    return 0 if w.W * w.H <= P["pace_compact_tiles"] else 1


def target_units(r):
    k = cls_index()
    t = P["pace_target"]
    pts = [(0, 1.0)] + [(st, t[st][k]) for st in (25, 50, 100)] + [(P["pace_until"], t[100][k])]
    return _interp(pts, r)


def target_mean_len(r):
    k = cls_index()
    t = P["pace_target"]
    return t["t250"][k] / float(t[100][k])


def update():
    for k in KEYS:
        P[k] = BASE[k]
    MODE[0] = 0
    if not P["pace_on"] or roles.ROLE[0] != "forager":
        return
    r = w.RND
    if r > P["pace_until"]:
        return
    tu = target_units(r)
    gap = tu - w.UNITS
    INFO[0], INFO[1] = tu, gap
    if gap >= P["pace_push_gap"] and w.UNITS < w.LIMIT:
        MODE[0] = 1
        if not P["pace_limits"] and r <= P["pace_open_until"]:
            P["opening_production_until"] = max(BASE["opening_production_until"], P["pace_open_until"])
            P["opening_production_unit_cap"] = max(BASE["opening_production_unit_cap"], int(tu + 0.999))
    elif -gap >= P["pace_hold_gap"] and r >= P["pace_hold_from"]:
        MODE[0] = -1
        P["split_val"] = BASE["split_val"] - P["pace_hold"]
        P["opening_production_value"] = BASE["opening_production_value"] - P["pace_hold"]
    if r >= P["pace_food_from"] and MODE[0] >= 0 and w.LEN < target_mean_len(r):
        f = 1.0 + P["pace_food"]
        P["v_pearl"] = BASE["v_pearl"] * f
        P["v_bed"] = BASE["v_bed"] * f


def split_bonus():
    """Extra production value while behind (MODE +1)."""
    if MODE[0] <= 0:
        return 0.0
    return P["pace_gain"] * min(INFO[1], P["pace_gap_cap"])


def marker(actions, score, selected):
    """ACT:pace+ when a split is chosen under the push; ACT:pace- when the hold
    turned a split the host would have chosen into a move."""
    if MODE[0] > 0 and selected[0] == "split":
        return "ACT:pace+"
    if MODE[0] < 0 and selected[0] == "move":
        for s, act in actions:
            if act[0] == "split" and s + P["pace_hold"] >= score:
                return "ACT:pace-"
    return None

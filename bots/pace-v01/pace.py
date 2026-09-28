"""PACE controller (P1): keep the team's material on the field's curve.

The only new policy on top of the host.  Each turn a dragon compares the
team's material against params.pace_target[stage] = (compact, open) --
units at r25/r50/r100, total length at r25/r50/r100/r250, linearly
interpolated between anchors and self-anchored at the observed round-0
material -- and shifts the production/foraging balance:

  behind on units  -> split_val up, opening production window extended
                      ("push"; the split itself stays child=2, split_min=4,
                      and still needs a free child exit)
  ahead on units but behind on total -> split_val down ("hold"), pearl/bed
                      values up, confirmed-pearl sprints enabled
  on pace          -> the host's default knobs

Team total length is estimated by sampling: mean length of self + visible
allies (+ the crown beacon if fresh) times UNIT_COUNT, EWMA-smoothed.
Units are exact from the header.

Survival constraints the controller never touches (unless pace_nolimit,
the arm that measures what they cost): exact 1-3 step simulation (no
certain-death step), the split child-exit/child-area gates, and -- in the
nolimit arm only -- the trap/threat/blind-portal penalty weights.

Activation contract: LOG ACT:pace+ on a production split while pushing
(rate-limited), LOG ACT:pace- while holding back (rate-limited).
"""
import world as w
import roles
from params import P

KNOBS = ("split_val", "v_pearl", "v_mem", "v_bed", "opening_production_until",
         "w_trap", "w_threat", "p_blind", "p_dive", "w_bed_block")
BASE = {k: P[k] for k in KNOBS}

TOT = [0.0]        # EWMA of estimated team total length
INIT = [False]     # curve anchors + estimator initialised?
U0 = [1]           # units observed in the opening (curve anchor at r=0)
T0 = [2.0]         # estimated total at r=0 (curve anchor)
UG = [0.0]         # last unit deficit fraction (+ behind)
TG = [0.0]         # last total deficit fraction (+ behind)
MODE = [""]        # "", "push", "hold"
OUT = []           # LOG ACT lines to flush with this turn's reply
LAST = {"pace+": -99, "pace-": -99}


def _cls():
    return 0 if w.W * w.H <= 625 else 1


def _anchors(kind):
    t = P["pace_target"]
    if kind == "u":
        return ((0, U0[0]), (25, t["u25"][_cls()]), (50, t["u50"][_cls()]),
                (100, t["u100"][_cls()]))
    return ((0, T0[0]), (25, t["t25"][_cls()]), (50, t["t50"][_cls()]),
            (100, t["t100"][_cls()]), (250, t["t250"][_cls()]))


def _curve(kind, r):
    a = _anchors(kind)
    if r <= a[0][0]:
        return float(a[0][1])
    for i in range(1, len(a)):
        if r <= a[i][0]:
            r0, v0 = a[i - 1]
            r1, v1 = a[i]
            return v0 + (v1 - v0) * (r - r0) / float(r1 - r0)
    return float(a[-1][1])


def est_total():
    """Sampled team total: mean length of self + visible allies (+ crown
    beacon), times UNIT_COUNT.  Caller blends it only when the sample has
    at least one ally in it, clamped against the smoothed value."""
    n = 1 + len(w.alen)
    s = float(w.LEN + sum(w.alen.values()))
    if w.crown is not None and roles.fresh():
        s += w.crown[2]
        n += 1
    est = s * w.UNITS / n
    floor = 2.0 * w.UNITS
    return est if est > floor else floor, n


def act(tag, gap):
    r = w.RND
    if r - LAST[tag] >= gap:
        LAST[tag] = r
        OUT.append("ACT:" + tag)


def update():
    if not P["pace_on"]:
        return
    r = w.RND
    est, n = est_total()
    if not INIT[0]:
        INIT[0] = True
        TOT[0] = est
        if r <= 2:   # an initial dragon: anchor the curve at what we start with
            U0[0] = max(1, w.UNITS)
            T0[0] = est
        return
    if n >= 2:   # blend only samples that saw at least one ally
        lo, hi = 0.7 * TOT[0], 1.4 * TOT[0]
        if est < lo:
            est = lo
        elif est > hi:
            est = hi
        TOT[0] += P["pace_ewma"] * (est - TOT[0])
    floor = 2.0 * w.UNITS   # no dragon is shorter than 2 segments
    if TOT[0] < floor:
        TOT[0] = floor
    tu = _curve("u", r)
    tt = _curve("t", r)
    ug = (tu - w.UNITS) / max(1.0, tu)
    tg = (tt - TOT[0]) / max(1.0, tt)
    UG[0], TG[0] = ug, tg
    push = ug > P["pace_u_band"] and r < P["split_stop"]
    hold = ug < -P["pace_u_band"] and tg > P["pace_t_band"]
    # foraging side: pull pearls/beds harder whenever the total lags the curve
    grow = tg > P["pace_t_band"]
    MODE[0] = "push" if push else ("hold" if hold else ("grow" if grow else ""))
    # production side
    if push:
        P["split_val"] = BASE["split_val"] + P["pace_split_gain"] * min(ug, 0.8)
        P["opening_production_until"] = BASE["opening_production_until"] + \
            int(P["pace_open_ext"] * min(ug, 1.0))
    elif hold:
        P["split_val"] = BASE["split_val"] - P["pace_split_hold"] * min(-ug, 0.6)
        P["opening_production_until"] = BASE["opening_production_until"]
    else:
        P["split_val"] = BASE["split_val"]
        P["opening_production_until"] = BASE["opening_production_until"]
    if grow:
        # class-conditioned: a full pearl-value boost collapses the compact
        # churn economy (trophy seed-1 isolation, 2026-09-29: u100 33 -> 11)
        gain = P["pace_forage_c"] if _cls() == 0 else P["pace_forage_o"]
        f = 1.0 + gain * min(tg, 0.6)
        P["v_pearl"] = BASE["v_pearl"] * f
        P["v_bed"] = BASE["v_bed"] * f
        P["v_mem"] = BASE["v_mem"] * f
        P["pace_sprint_pearl"] = 1 if (tg > 0.15 and r < 300) else 0
    else:
        P["v_pearl"] = BASE["v_pearl"]
        P["v_bed"] = BASE["v_bed"]
        P["v_mem"] = BASE["v_mem"]
        P["pace_sprint_pearl"] = 0
    # nolimit arm: survival constraints off (measures what they cost)
    if P["pace_nolimit"]:
        for k in ("w_trap", "w_threat", "p_blind", "p_dive", "w_bed_block"):
            P[k] = 0.0
    if MODE[0] in ("push", "grow"):
        act("pace+", 8)   # heartbeat: the knob shift is active this turn
    if P.get("pace_trace") and r % 16 == (w.ME & 15):
        OUT.append("PACE r%d u%d/%.1f t%.0f/%.0f %s" %
                   (r, w.UNITS, tu, TOT[0], tt, MODE[0] or "-"))

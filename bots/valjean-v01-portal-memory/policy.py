"""DECISION: executor-conditioned value of each objective; pick one.

    Q(c) = objective_value(c, features) + executor_value(c)

executor_value is the executor's own preview score (the Monte Christo move/
split evaluation, in segment units): what executing this objective right now
is predicted to be worth. objective_value is the policy's long-horizon value of
pursuing c INSTEAD OF the economy objective, in the same units. P0 sets it to
0 for the economy, contact, reproduction and escape objectives: with no macro
candidates, argmax Q equals Monte Christo v01's argmax (parity). The escape
split is only admissible when every other option is below the despair gate.

Policy reads features (topology.F, mass.F, valuation.saturation, round) and the
candidate record; it never routes, simulates or mutates.
"""
import world as w
import valuation as val
import topology
import mass
from params import P

DESPAIR = -900.0


def objective_value(c, ctx):
    kind = c["kind"]
    p = c["params"]
    if kind == "REPRODUCE":
        return split_adjust()
    if kind == "GATHER" and p.get("region"):
        v = P["reg_w"] * (p["value"] - ctx["econ_value"]) - P["reg_margin"]
        if p.get("persist"):
            v += P["reg_persist"]
        return v
    if p.get("press"):    # ATTACK:pressure
        F = mass.F
        sat = val.saturation()
        v = P["press_base"] + P["press_sat"] * sat - P["press_econ"] * ctx["econ_value"]
        ed = F.get("e_dist")
        if ed is not None:
            v -= P["press_dist"] * ed
        return v
    if p.get("support"):  # RETREAT:support
        F = mass.F
        v = -P["sup_base"] + P["sup_balance"] * max(0.0, F.get("balance", 0.0)) \
            - P["sup_econ"] * ctx["econ_value"]
        return v
    return 0.0


def split_adjust():
    """Feature `confine`: splitting where the space is already full of bodies.

    crowd = local segments per reachable cell within room_r; open_frac = room
    relative to an open torus. Penalty grows linearly past crowd0 and when the
    space is confined (open_frac below open0). Off when both weights are 0."""
    F = topology.F
    adj = 0.0
    if P["w_crowd_split"]:
        adj -= P["w_crowd_split"] * max(0.0, F["crowd"] - P["crowd0"])
    if P["w_confine_split"]:
        adj -= P["w_confine_split"] * max(0.0, P["open0"] - F["open_frac"])
    return adj


def is_escape(c):
    return c["kind"] == "RETREAT" and c["params"].get("emergency_split") and c["target"] < 0


def escape_gate():
    return P["escape_gate"] if P["escape_eval"] else DESPAIR


def best_other(cands, results, ctx):
    """Best Q among executed non-escape options (decides whether the escape
    preview is requested at all: a bounded, on-demand preview)."""
    b = -1e18
    for c, r in zip(cands, results):
        if r is None or r["command"] is None or is_escape(c):
            continue
        q = 1e9 if r.get("donate") else objective_value(c, ctx) + r["value"]
        if q > b:
            b = q
    return b


def rank(cands, results, ctx):
    rows = []
    best_other = -1e18
    for c, r in zip(cands, results):
        if r is None or r["command"] is None:
            continue
        if r.get("donate"):
            q = 1e9  # deliberate donation next to a fresh crown pre-empts all (inherited)
        else:
            q = objective_value(c, ctx) + r["value"]
        r["q"] = q
        if is_escape(c):
            rows.append((q, 1, c, r))
            continue
        rows.append((q, 0, c, r))
        if q > best_other:
            best_other = q
    out = []
    gate = escape_gate()
    for q, esc, c, r in rows:
        if esc and best_other >= gate:
            continue
        out.append((q, c, r))
    return out


def choose(cands, results, ctx):
    ranked = rank(cands, results, ctx)
    if not ranked:
        return None, None
    best = None
    for row in ranked:  # first maximum wins (stable, candidate order)
        if best is None or row[0] > best[0]:
            best = row
    return best[1], best[2]

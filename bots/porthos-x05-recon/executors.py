"""EXECUTION (executor set E2, version 2): E0 executors + self-routing recon.

An executor receives the nominated candidate, the permitted world facts and
its fixed parameters, and returns one execution record:

    {"command": ("move", path) | ("split", n),
     "predicted": "ok" | "dead" | "h2h" | "dive" | "split",
     "status": "completed" | "active" | "fallback",
     "reason": short stable string,
     "trade": None | "favourable" | "unfavourable" | "donation",
     "path_cells": intermediate cells to commit to the trail (moves only),
     "report": None | {"handoff": n},
     "diag": {...cost/progress facts...}}

E0 executors are deliberately thin: the decision policy picked a concrete
path/argument and the executor validates and serialises it, re-checking the
mechanical outcome with the exact simulation.

E2 changes ONE intention's implementation: SCOUT mode "recon" (portal
reconnaissance).  The candidate nominates an objective -- an unpaired portal
CELL; no compass direction crosses the decision/execution boundary.  The
executor routes over optimistic terrain (bounded BFS), picks a first step on
a shortest route whose exact simulation survives (or is the dive itself),
and reports progress as remaining route distance.  A dive is predicted
"dive": an honest unknown landing, never silently called safe.

preview_recon is the bounded executor preview the policy may consult; it
commits nothing.
"""
import world as w
import tactics as tx
from params import P

EXECUTORS_VERSION = 2


def _move_record(cand, reason, trade=None, status="completed"):
    path = cand["arg"]
    st, nb, _, _ = tx.sim(path, w.body)
    rec = {"command": ("move", path), "predicted": st, "status": status,
           "reason": reason, "trade": trade, "path_cells": (),
           "report": None,
           "diag": {"kind": cand["kind"], "target": cand["target"],
                    "steps": len(path), "score": round(cand["score"], 3)}}
    if st == "ok" and len(path) > 1:
        rec["path_cells"] = nb[-len(path):-1]
    return rec


def gather(cand):
    """Reach a useful resource (pearl/bed/remembered cell) on a bounded
    route; the nominated path already respects the shared movement model."""
    rec = _move_record(cand, "route-to-resource")
    rec["diag"]["eaten"] = cand["preview"].get("eaten", 0)
    return rec


# --------------------------------------------------------------- recon (E2)
def preview_recon(cand):
    """Bounded preview of a portal-recon objective: optimistic route to the
    nominated portal cell, then the dive step.  Returns availability, total
    steps including the dive, and a surviving first step if one exists.
    Pure: no world state, trails or scripts are touched."""
    portal = cand["target"]
    if w.HEAD == portal:
        # Standing on the portal cell: the dive step itself is the route.
        for d in range(4):
            if w.dest(w.HEAD)[d] == -3 and w.epid.get(w.ekey(w.HEAD, d)) == cand["pid"]:
                if tx.sim([d], w.body)[0] == "dive":
                    return {"available": True, "steps": 1, "first": d, "dive": True}
        return {"available": False}
    rd = tx.rev_dist(portal, P["recon_cap"], {w.HEAD})
    best = None
    for d in range(4):
        n = w.step_opt(w.HEAD)[d]
        if n < 0:
            continue
        t = rd.get(n)
        if t is None or t + 2 > P["recon_reach"] + 1:   # steps include the dive
            continue
        if tx.sim([d], w.body)[0] != "ok":
            continue
        if best is None or t < best[0]:
            best = (t, d)
    if best is None:
        return {"available": False}
    t, d = best
    return {"available": True, "steps": t + 2, "first": d, "dive": False}


def _scout_recon(cand):
    """Self-route to the nominated unpaired portal and dive it.  The
    objective is a cell; the route and the dive direction are the
    executor's own bounded choice."""
    rp = cand.get("recon_preview")
    if rp is None:
        rp = preview_recon(cand)
    if not rp["available"]:
        return {"command": ("move", [w.FACE]), "predicted": "unknown",
                "status": "fallback", "reason": "recon-route-unavailable",
                "trade": None, "path_cells": (), "report": None,
                "diag": {"kind": "scout", "target": cand["target"],
                         "score": round(cand["score"], 3)}}
    d = rp["first"]
    st = tx.sim([d], w.body)[0]
    return {"command": ("move", [d]), "predicted": st,
            "status": "completed" if rp["dive"] else "active",
            "reason": "portal-dive" if rp["dive"] else "portal-approach",
            "trade": None, "path_cells": (), "report": None,
            "diag": {"kind": "scout", "target": cand["target"],
                     "steps": rp["steps"], "score": round(cand["score"], 3)}}


def scout(cand):
    """Traverse toward unexplored/useful coverage.  E0 path: the nominated
    path is validated (unseen cell, sector waypoint, or an adjacent unpaired
    portal dive).  E2 recon objectives self-route instead."""
    if cand["mode"] == "recon":
        return _scout_recon(cand)
    rec = _move_record(cand, "explore")
    rec["diag"]["predicted_detail"] = cand["preview"]["outcome"]
    return rec


def attack(cand):
    """Strike a nominated enemy head, or chase the prey target.  The trade
    class is explicit: 'favourable' when the strike margin held at decision
    time, 'unfavourable' when the trade was accepted only because every
    alternative was worse (still a deliberate trade, not an accident)."""
    pv = cand["preview"]
    if pv["outcome"] == "h2h":
        trade = "favourable" if cand["score"] > -900.0 else "unfavourable"
        rec = _move_record(cand, "strike", trade=trade)
        rec["diag"]["hit"] = pv["hit"]
        return rec
    return _move_record(cand, "chase")


def retreat(cand):
    """Emergency split: shed the rear as a child facing away, keeping most
    of our length.  Admitted by the policy only in despair states."""
    n = cand["arg"]
    return {"command": ("split", n), "predicted": "split",
            "status": "completed", "reason": "emergency-split",
            "trade": None, "path_cells": (), "report": None,
            "diag": {"kind": "retreat", "child": n,
                     "score": round(cand["score"], 3)}}


def feed_ally(cand):
    """Donate to the crown: an explicit, intentional sacrifice -- die into
    an ally BODY (never the head) so pearls deposit on the corpse segments.
    Predicted outcome 'dead' is the objective here, not a failure."""
    rec = _move_record(cand, "donate", trade="donation")
    rec["predicted"] = "dead"
    return rec


def reproduce(cand):
    """Create a viable child.  Legality was probed at candidate time; the
    executor re-checks the hard engine invariants (both bodies >= 2, unit
    limit).  A crown handoff report, when required, is requested at the
    commit stage for ANY split command (see main), matching the legacy
    message behaviour exactly."""
    n = cand["arg"]
    L = w.LEN
    if L - n < 2 or n < 2 or w.UNITS >= w.LIMIT:
        # should not happen after a frozen availability probe; stay legal
        return {"command": ("move", [w.FACE]), "predicted": "unknown",
                "status": "fallback", "reason": "split-legality-recheck",
                "trade": None, "path_cells": (), "report": None,
                "diag": {"kind": "reproduce", "child": n}}
    return {"command": ("split", n), "predicted": "split",
            "status": "completed", "reason": "production",
            "trade": None, "path_cells": (), "report": None,
            "diag": {"kind": "reproduce", "child": n,
                     "score": round(cand["score"], 3)}}


EXECUTORS = {"gather": gather, "scout": scout, "attack": attack,
             "retreat": retreat, "feed_ally": feed_ally,
             "reproduce": reproduce}


def execute(cand):
    """Dispatch the nominated candidate to its intention's executor.
    Records the no-surviving-move fact when the selected move is predicted
    fatal without being an intentional trade/donation."""
    rec = EXECUTORS[cand["kind"]](cand)
    if rec["predicted"] == "dead" and rec["trade"] is None:
        rec["status"] = "fallback"
        rec["reason"] = "no-surviving-move"
    return rec

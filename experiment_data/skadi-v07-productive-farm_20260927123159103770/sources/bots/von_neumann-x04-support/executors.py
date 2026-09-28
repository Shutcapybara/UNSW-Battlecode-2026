"""EXECUTION (executor set E0, version 1): one executor per intention.

An executor receives the nominated candidate, the permitted world facts and
its fixed parameters, and returns one execution record:

    {"command": ("move", path) | ("split", n),
     "predicted": "ok" | "dead" | "h2h" | "dive" | "split",
     "status": "completed" | "fallback",
     "reason": short stable string,
     "trade": None | "favourable" | "unfavourable" | "donation",
     "path_cells": intermediate cells to commit to the trail (moves only),
     "report": None | {"handoff": n},
     "diag": {...cost/progress facts...}}

E0 executors are deliberately thin: the decision policy picked a concrete
path/argument and the executor validates and serialises it, re-checking the
mechanical outcome with the exact simulation.  Replacing path-following with
self-routing inside one executor is an E0 -> E1 implementation change: the
interface above is what survives it.

A syntactically valid command, predicted survival and an intentional trade
are distinguished explicitly: no generic "safe move" filter removes attack
or feed actions.
"""
import world as w
import tactics as tx

EXECUTORS_VERSION = 1


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


def scout(cand):
    """Traverse toward unexplored/useful coverage (unseen cell, sector
    waypoint, or an unpaired portal dive)."""
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

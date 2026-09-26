"""INTENTIONS (contract menu, version 1): stable executable intentions.

Six kinds: gather, scout, attack, retreat, feed_ally, reproduce.  Each
intention owns cheap, frozen AVAILABILITY checks and proposes stable
candidate records:

    {"id", "kind", "target", "mode", "arg", "exclusive", "emergency"}

mode "move": arg = direction-id path; mode "split": arg = child length.
"exclusive" candidates (an intentional feed donation) replace the whole
candidate set, mirroring the legacy short-circuit.  "emergency" candidates
(retreat's escape split) are only admitted by the decision policy when no
ordinary candidate scores above its despair threshold.

Candidate construction does NOT score and does NOT commit anything; target
hysteresis lives in targets.MEM and is updated once per turn by the target
search, never per candidate.
"""
import world as w
import tactics as tx
import roles
import targets
from params import P

INTENTIONS_VERSION = 1
KINDS = ("gather", "scout", "attack", "retreat", "feed_ally", "reproduce")


# ------------------------------------------------------------- availability
def donation_move():
    """FEED_ALLY sacrifice probe (frozen): a feeder next to its visible crown
    deliberately steps to its death beside it -- feeding works by dying into
    an ally BODY.  Returns the first dying direction in the legacy probe
    order [back, N, E, S, W], else None.  Predicted outcome is 'dead' and the
    intent is explicit: this is never inferred from replay suicide labels."""
    if roles.ROLE[0] != "feeder":
        return None
    ch = roles.crown_visible()
    if ch < 0 or w.tdist(ch, w.HEAD) > P["feed_dist"]:
        return None
    back = (w.FACE + 2) % 4
    for d in [back, 0, 1, 2, 3]:
        if tx.sim([d], w.body)[0] == "dead":
            return d
    return None


def reproduce_available():
    """REPRODUCE legality probe (frozen): both bodies viable, unit limit,
    production window, forager role, known body, a legal child exit and
    enough room for the newborn.  Returns child length n or None."""
    L = w.LEN
    n = P["child"]
    if L < P["split_min"] or L - n < 2 or w.UNITS >= w.LIMIT:
        return None
    if w.RND >= P["split_stop"] or w.RND >= P["grow_from"]:
        return None
    if roles.ROLE[0] != "forager":
        return None
    body = w.body
    if len(body) < L:
        return None  # body not fully known
    # child: head = old tail, body reversed rear n segments
    child = body[:n][::-1]
    ch = child[-1]
    cown = set(child)
    pown = set(body[n:])
    ok = 0
    for x in w.dest(ch):
        if x >= 0 and x not in cown and x not in pown and x not in w.occ:
            ok += 1
    if not ok:
        return None
    if tx.flood(child, P["child_area"], 0) < P["child_area"]:
        return None
    return n


def escape_available():
    """RETREAT emergency-split probe (frozen): shed the rear (all but 2
    segments) as a child that starts at our tail facing away -- it keeps
    most of our length.  Returns child length n or None."""
    L = w.LEN
    body = w.body
    if L < 4 or w.UNITS >= w.LIMIT or len(body) < L:
        return None
    n = L - 2
    child = body[:n][::-1]
    ch = child[-1]
    cown = set(child)
    pown = set(body[n:])
    for x in w.dest(ch):
        if x >= 0 and x not in cown and x not in pown and x not in w.occ:
            return n
    return None


def move_paths():
    """Move paths worth evaluating (frozen): single steps always; 2-3 step
    sprints only with an enemy head near (strike / escape)."""
    out = [[d] for d in range(4)]
    L = w.LEN
    if L < 3:
        return out
    near_threat = False
    for ec, eid in w.enemy_heads:
        if w.cheb(ec, w.HEAD) <= 4:
            near_threat = True
            break
    if not near_threat:
        return out
    for d1 in range(4):
        for d2 in range(4):
            if d2 == (d1 + 2) % 4:
                continue
            out.append([d1, d2])
            if 4 <= L < P["sprint3_limit"]:
                for d3 in range(4):
                    if d3 == (d2 + 2) % 4:
                        continue
                    out.append([d1, d2, d3])
    return out


# ------------------------------------------------------------------ propose
def propose():
    """Stage 2 of the contract: candidate construction.

    Runs the target search once (commits this turn's target hysteresis),
    then builds the candidate set in the legacy evaluation order: the four
    single steps, conditional sprints, one REPRODUCE split, one emergency
    RETREAT split.  An available FEED_ALLY donation is exclusive.
    """
    body = w.body
    own_idx = {c: i for i, c in enumerate(body)}
    target, dist, mask, kind = targets.choose_target(own_idx)
    ctx = {
        "own_idx": own_idx,
        "target": target,
        "target_kind": kind,
        "dist": dist,
        "mask": mask,
    }
    cands = []
    d = donation_move()
    if d is not None:
        cands.append({"id": 0, "kind": "feed_ally", "target": target,
                      "mode": "move", "arg": [d], "exclusive": True,
                      "emergency": False})
        return cands, ctx
    i = 0
    ikind = "feed_ally" if kind == "feed" else kind
    for path in move_paths():
        cands.append({"id": i, "kind": ikind, "target": target,
                      "mode": "move", "arg": path, "exclusive": False,
                      "emergency": False})
        i += 1
    n = reproduce_available()
    if n is not None:
        cands.append({"id": i, "kind": "reproduce", "target": -1,
                      "mode": "split", "arg": n, "exclusive": False,
                      "emergency": False})
        i += 1
    n = escape_available()
    if n is not None:
        cands.append({"id": i, "kind": "retreat", "target": -1,
                      "mode": "split", "arg": n, "exclusive": False,
                      "emergency": True})
    return cands, ctx

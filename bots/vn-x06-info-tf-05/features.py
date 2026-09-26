"""FEATURES (version 2): named, unit-documented facts for scoring.

v1 facts (unchanged semantics): threat map, head-near set, progress table,
crown-flank set, flood need, and the per-candidate mechanical previews
(exact simulation outcome, post-action body/length, pearls eaten, flood
area, pocket pearls, progress class, crowding, flank, bed-block, visits,
blind steps).

v2 ADDS game-relative facts (computed here in x03; consumed only by policy
versions >= 2, so P0 behaviour is untouched):

  global (per turn, before candidates -- contract-sanctioned):
    phase        round / 500 in [0, 1)
    early        round < aggro_until (the opening, where trades buy space)
    sat          units / unit_limit in [0, 1] (team population saturation)
    area_here    credited flood area from our current head (topology-aware
                 confinement: the same length in a pocket vs in the open)
    room_ratio   min(1, area_here / need); need = max(len + slack, min_area)
    counts       (ally, enemy, confidence) aggregate counts at our head
                 (density.py field)
    lengths      (ally, enemy, confidence) directional lengths at our head
                 (swarm.py field)

  per candidate (previews; never commit anything):
    child_room   (splits) credited flood area from the CHILD's head --
                 graded confinement of the newborn, not just a binary gate
    swarm_gain   (ok moves) balance(head_after) - balance(HEAD) from
                 length evidence; positive = toward enemy control
    res_factor   (target-level) 1 / (1 + crowding) of the nominated target
                 from aggregate count evidence (v07's one proven hook)

Previews never commit simulated bodies, trails or scripts; only the
selected execution commits (see executors + main).
"""
import world as w
import tactics as tx
import roles
import targets
import density
import swarm
from params import P

FEATURES_VERSION = 2


def global_features():
    """Stage 3a (before candidates): enemy reach, head-near set, and the
    game-relative global facts (phase, saturation, confinement, density)."""
    threat = tx.threat_map()
    tx.set_head_near()
    area = tx.flood(w.body, P["flood_cap_long"], 0)
    need = max(w.LEN + P["slack"], P["min_area"])
    gf = {
        "threat": threat,
        "phase": w.RND / 500.0,
        "early": w.RND < P["aggro_until"],
        "sat": w.UNITS / max(1, w.LIMIT),
        "area_here": area,
        "room_ratio": min(1.0, area / max(1, need)),
        "counts": density.field(w.HEAD),
        "lengths": swarm.field(w.HEAD),
    }
    # x06 dual-window facts: short-window length field at the head and the
    # normalised local contact level it implies (build switch or consumer).
    if P["field_dual"] or P["w_mb2"] or P["w_tf"]:
        _a, e_short, _c = swarm.field_short(w.HEAD)
        gf["lengths_short"] = swarm.field_short(w.HEAD)
        gf["contact"] = min(1.0, e_short / P["contact_norm"])
    if P["field_dual"]:
        gf["counts_short"] = density.field_short(w.HEAD)
    return gf


def target_features(ctx):
    """Stage 3b (after candidates): progress table, crown-flank set, flood
    need.  Mirrors the legacy one-per-turn computations exactly; v2 adds the
    nominated target's density facts (res_factor, target swarm balance)."""
    target = ctx["target"]
    mask = ctx["mask"]
    dist = ctx["dist"]
    # progress of each first move towards the target: +1 on a shortest
    # route, -1 otherwise; beyond the search, torus distance steers
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
    # feeders keep off the crown's flanks (they would box it in)
    crown_flank = set()
    if roles.ROLE[0] == "feeder" and w.crown is not None:
        cid = w.crown[0]
        for c, o in w.occ.items():
            if o[1] and (o[0] & 4095) == cid:
                for n in w.dest(c):
                    if n >= 0:
                        crown_flank.add(n)
    L = w.LEN
    need = max(L + P["slack"], P["min_area"])
    if L >= 10:  # long bodies need margin: others fill in behind them
        need = min(need + L // 3, P["flood_cap_long"])
    else:
        need = min(need, P["flood_cap"])
    tf = {"prog": prog, "crown_flank": crown_flank, "need": need}
    if target >= 0:
        tf["res_factor"] = density.resource_factor(target)
        tf["target_lengths"] = swarm.field(target)
    else:
        tf["res_factor"] = 1.0
        tf["target_lengths"] = (0.0, 0.0, 0.0)
    return tf


def preview(cand, gf, tf):
    """Stage 3c: mechanical preview of one candidate.  For moves: exact
    engine simulation plus the local facts scoring needs.  For splits: the
    parent-body flood area and (v2) the child's graded room.  Attaches the
    preview to the candidate dict and returns it.  No world state is
    committed here."""
    if cand["mode"] == "split":
        if cand["emergency"]:
            # RETREAT's escape split takes a fixed despair score; the legacy
            # code never flood-fills it, so the preview stays minimal.
            cand["preview"] = {"outcome": "split"}
            return cand["preview"]
        body = w.body
        L = w.LEN
        n = cand["arg"]
        parent = body[n:]
        pneed = min(max(L - n + P["slack"], P["min_area"]), P["flood_cap"])
        area = tx.flood(parent, pneed, 0)
        ch = body[:n][0] if n <= len(body) else -1
        child = body[:n][::-1]
        cand["preview"] = {
            "outcome": "split", "parent_area": area, "pneed": pneed,
            "child_head": body[0] if body else -1,
            "child_room": tx.flood(child, P["child_room_cap"], 0),
            "threat_at_head": gf["threat"].get(w.HEAD),
            "threat_at_child": gf["threat"].get(ch),
        }
        return cand["preview"]
    path = cand["arg"]
    body = w.body
    L = w.LEN
    st, nb, eaten, hit = tx.sim(path, body)
    pv = {"outcome": st, "body_after": nb, "eaten": eaten, "hit": hit,
          "blind": tx.BLIND[0], "steps": len(path)}
    if st == "dive":
        pv["threat_at_head"] = gf["threat"].get(w.HEAD)
    if st == "ok":
        h = nb[-1]
        area = tx.flood(nb, tf["need"], 0)
        pv["head_after"] = h
        pv["len_after"] = len(nb)
        pv["area"] = area
        pv["pocket"] = tx.POCKET[0]
        pv["threat_at_head"] = gf["threat"].get(h)
        pv["visits"] = w.visits[h]
        pv["flank"] = h in tf["crown_flank"]
        pv["prog"] = tf["prog"][path[0]]
        pv["bed_block"] = w.bed[h] == 2 and w.spawn.get(h, -9) == w.RND + 1
        pv["swarm_gain"] = swarm.gain(h)
        # x06: room-normalised spatial gain and the short-window gradient.
        # Same enemy control in a tight corridor is worse to push into, so
        # the gain is damped by the bounded room at the landing cell.
        if P["field_room"] or P["w_grad"]:
            room = tx.flood(nb, P["room_cap"], 0)
            pv["room"] = room
            pv["spatial_gain"] = pv["swarm_gain"] * min(1.0, room / P["room_norm"])
        if P["field_dual"] or P["w_mb2"]:
            pv["swarm_gain_short"] = swarm.gain_short(h)
    cand["preview"] = pv
    return pv

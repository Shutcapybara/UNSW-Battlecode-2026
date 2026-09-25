"""FEATURES (version 1): named, unit-documented mechanical facts for scoring.

Global features (threat map, head-near set) are built before candidate
construction -- the contract explicitly allows this, and the REPRODUCE
legality probe's flood fill reads the head-near set.

Per-candidate PREVIEWS expose mechanical facts only: exact move simulation
outcome, post-action body/length, pearls eaten, flood area, trap pocket
pearls, progress class toward the target, crowding distance, crown-flank
membership, bed-block flag, visit count, sprint blind steps.  Previews never
commit simulated bodies, trails or scripts; only the selected execution
commits (see executors + main).
"""
import world as w
import tactics as tx
import roles
import targets
from params import P

FEATURES_VERSION = 1


def global_features():
    """Stage 3a (before candidates): enemy reach and head-near set."""
    threat = tx.threat_map()
    tx.set_head_near()
    return {"threat": threat}


def target_features(ctx):
    """Stage 3b (after candidates): progress table, crown-flank set, flood
    need.  Mirrors the legacy one-per-turn computations exactly."""
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
    return {"prog": prog, "crown_flank": crown_flank, "need": need}


def preview(cand, gf, tf):
    """Stage 3c: mechanical preview of one candidate.  For moves: exact
    engine simulation plus the local facts scoring needs.  For splits: the
    parent-body flood area.  Attaches the preview to the candidate dict and
    returns it.  No world state is committed here."""
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
        cand["preview"] = {
            "outcome": "split", "parent_area": area, "pneed": pneed,
            "child_head": body[0] if body else -1,
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
    cand["preview"] = pv
    return pv

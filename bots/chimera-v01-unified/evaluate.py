"""evaluate.py -- candidate generation and the evaluation function.

candidates(): single steps, sprints, strikes.  decide(): score every
candidate (material, threat, space, doom, tunnels, exits, goal progress,
traffic, crowd, spread, sprint cost) plus dive / split / emergency split
options, and return the argmax.
"""

# ======================================================================
# DECIDE
# ======================================================================
def candidates(body):
    """Single steps always; sprints (2..sprint_max) only when they can matter:
    a visible enemy head is close (strike / escape), every single step looks
    dangerous, or step one eats a pearl (a free second step)."""
    out = []
    for d in range(4):
        out.append(([d], simulate([d], body)))
    maxk = min(P["sprint_max"], LEN - 1)
    if maxk < 2:
        return out
    near = False
    for c, eid in enemy_heads:
        if tdist(HEAD, c) <= maxk + 1:
            near = True
            break
    grow = []
    if near:
        grow = [p for p, r in out if r[0]]
    else:
        for p, r in out:
            if r[0] and r[1] in pearls:
                grow.append(p)
    # depth 2: full candidates.  depth 3: strikes only (cheap to score, and
    # the only reason to pay two segments in one turn)
    for path in grow:
        for d in range(4):
            p2 = path + [d]
            res = simulate(p2, body)
            if res[0] or res[4] is not None:
                out.append((p2, res))
            if res[0] and maxk >= 3 and near:
                for d3 in range(4):
                    p3 = p2 + [d3]
                    r3 = simulate(p3, body)
                    if r3[4] is not None:
                        out.append((p3, r3))
    return out


def decide():
    global ROLE
    body = body_list()
    if TRACE:
        import time
        _t = [time.perf_counter()]
    tm = threat_map()
    sc = split_threat_cells()
    rp = RP[ROLE]
    lvv = lv()

    if TRACE:
        _t.append(time.perf_counter())
    target, far, tscore = choose_target(tm)
    if FEED[0] >= 0:
        target = FEED[0]
        far = FEED[0]
    if TRACE:
        _t.append(time.perf_counter())
    cands = candidates(body)
    ends = [res[1] for p, res in cands if res[0]]
    if TRACE:
        _t.append(time.perf_counter())
    rdist = reverse_dist(target, ends + [HEAD]) if target >= 0 else {}
    if TRACE:
        _t.append(time.perf_counter())
    base_d = rdist.get(HEAD)

    # ally head positions (visible) for traffic avoidance
    best = None
    best_v = -1e18
    my_v = dragon_value(LEN)
    need = LEN + P["space_slack"]
    if need > 40:
        need = 40
    scored = []
    n_ok = 0
    ally_segs = [(c % W, c // W) for c, o in occ.items() if o[1]]
    near_allies = [c for c, ln, r, when in allies.values()
                   if RND - when <= 3 and tdist(c, HEAD) <= 12]
    contested = set()
    for c, v in occ.items():
        if v[2]:
            for m in dest(c):
                if m >= 0 and m not in occ:
                    contested.add(m)
    w_eat = P["w_eat_prod"]
    for path, res in cands:
        alive, cell, ln, eaten, struck, nb = res
        k = len(path)
        if not alive:
            if struck is not None:
                # trade: both die; they lose their value, we lose ours
                their = enemy_len.get(struck, 2)
                their_v = dragon_value(their)
                margin = rp["trade_margin"]
                if RND >= P["end_start"]:
                    margin = max(margin, 1)
                v = their_v - my_v + rp["strike_bonus"] - 0.3 * (k - 1)
                if RND >= P["crown_kill_round"] and ROLE != CROWN and \
                        their >= max(LEN + 1, longest_known_ally()):
                    margin = 0  # their crown outgrows ours: take it off the board
                    v += 10.0
                if their < LEN + margin and UNITS > 2:
                    v -= 50.0  # below this role's trade threshold
                v -= 20.0      # losing the unit's future is never free
                v += 20.0 * (1 if their >= LEN + margin else 0)
                scored.append((v, path, "strike"))
            continue
        v = lvv * (ln - LEN)                      # sprint cost, pearls eaten
        if eaten and w_eat and ROLE != CROWN and RND < P["split_stop"]:
            v += w_eat * eaten                    # production: a pearl is part of a future unit
        v -= head_risk(cell, ln, tm, sc)
        sp = flood(cell, nb, need + 1, NOSET)
        if sp < need:
            v -= P["w_trap"] * (need - sp) / float(need) * (1.0 + ln * 0.1)
        v += P["w_space"] * sp
        ex = 0.0
        nfree = 0
        nbs = set(nb)
        for m in dest(cell):
            if m >= 0 and m not in occ and m not in nbs:
                nfree += 1
                ex += 0.5 if m in contested else 1.0
        # the permanent-trap test is the expensive one: skip it where the
        # flood found room and the head has two ways on (not a corridor)
        dm = -1
        if not P["doom_skip"] or sp < need or nfree < 2:
            dm = doom(cell, nb)
        if dm < 0:
            n_ok += 1
        elif ln + dm >= P["farm_len"] and UNITS < UNIT_LIMIT and LEN <= P["farm_max_len"] \
                and ROLE != CROWN:
            # a dead end with pearls enough to grow and split our way out:
            # the child walks out of the corridor, the stub stays.  A farm.
            v -= P["w_doom_farm"]
            n_ok += 1
        else:
            v -= P["w_doom"] * (dragon_value(ln) + 2.0)
        th = tunnel_heads(cell, nb[-2] if len(nb) > 1 else HEAD)
        if th:
            v -= P["w_tunnel_head"] if th == 2 else (P["w_tunnel_body"] if th == 1 else
                                                     P["w_tunnel_unknown"])
        if cell in doomed and RND - doomed[cell] < P["doom_memory"]:
            v -= P["w_doomed"]
        if ex < 0.5:
            v -= P["w_exit0"]
        elif ex < 1.5:
            v -= P["w_exit1"] * (1.5 - ex)
        # goal potential
        if target >= 0:
            d = rdist.get(cell)
            if d is not None and base_d is not None:
                prog = base_d - d
                if prog > 1:
                    v += P["w_goal"] + P["w_goal_sprint"] * (prog - 1)
                else:
                    v += P["w_goal"] * prog
            elif far >= 0:
                v += P["goal_far_w"] * (tdist(HEAD, far) - tdist(cell, far))
        # traffic
        for m in dest(cell):
            if m in ally_heads:
                v -= P["w_ally_head_adj"]
            else:
                o = occ.get(m)
                if o is not None and o[1]:
                    v -= P["w_ally_body_adj"]
        if ally_segs:
            cx = cell % W
            cy = cell // W
            crowd = 0
            for ax, ay in ally_segs:
                dx = ax - cx
                if dx < 0:
                    dx = -dx
                if dx * 2 > W:
                    dx = W - dx
                if dx > 2:
                    continue
                dy = ay - cy
                if dy < 0:
                    dy = -dy
                if dy * 2 > H:
                    dy = H - dy
                if dy <= 2:
                    crowd += 1
            v -= P["w_crowd"] * crowd
        if blind_portal(path):
            v -= P["w_blind_portal"]
        v -= P["w_visit"] * visits[cell]
        # spread from nearby allies (gossip positions)
        v += spread_term(cell, near_allies) * rp["w_spread"]
        # sprinting burns production: extra cost per extra step
        v -= P["w_sprint"] * (k - 1)
        v += ((MY_ID * 31 + RND * 7 + path[0] * 13) % 10) * 0.001
        scored.append((v, path, "move"))
    if TRACE:
        _t.append(time.perf_counter())
        trace("PH r%d threat=%.2f target=%.2f cands=%.2f(n%d) rdist=%.2f(n%d) eval=%.2f" % (
            RND, (_t[1] - _t[0]) * 1e3, (_t[2] - _t[1]) * 1e3, (_t[3] - _t[2]) * 1e3, len(cands),
            (_t[4] - _t[3]) * 1e3, len(rdist), (_t[5] - _t[4]) * 1e3))
    if n_ok == 0 and len(trail) > 2:
        report_doom()
        es = emergency_split()
        if es:
            scored.append((P["w_emergency_split"], es, "split"))
    ds0 = dest(HEAD)
    for d in range(4):
        if ds0[d] == -1 and ek[ekey(HEAD, d)] == 3:
            # unpaired portal: an unknown destination, worth a look when
            # nothing better is on offer (scouts like it more)
            v = P["w_dive"] * (1.5 if ROLE == SCOUT else 1.0) - P["dive_risk"]
            if tscore < 1.0:
                v += P["w_dive_idle"]
            scored.append((v, [d], "dive"))
    risk_here = head_risk(HEAD, LEN, tm, sc)
    sv = split_value(risk_here)
    if sv is not None:
        v, n = sv
        v -= risk_here * 0.5
        scored.append((v, n, "split"))
    if not scored:
        return []
    scored.sort(key=lambda t: t[0], reverse=True)
    if TRACE:
        trace("r%d id%d role%d len%d head%d tgt%d far%d top=%s" % (
            RND, MY_ID, ROLE, LEN, HEAD, target, far,
            [(round(s[0], 2), s[1], s[2]) for s in scored[:4]]))
    return [(v, act, kind, target) for v, act, kind in scored]


def spread_term(cell, near):
    best = 99
    for c in near:
        d = tdist(cell, c)
        if d < best:
            best = d
    if best >= 99:
        return 0.0
    return best if best < 8 else 8

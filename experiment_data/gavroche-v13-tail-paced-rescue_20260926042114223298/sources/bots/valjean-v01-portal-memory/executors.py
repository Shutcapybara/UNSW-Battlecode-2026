"""EXECUTION: turn a nominated objective into a concrete command + prediction.

Never reads policy settings. One shared movement preview per turn (<= 52 paths:
4 single steps, sprints only with an enemy head within Chebyshev 4, 3-step
sprints only for lengths 4..sprint3_limit-1). Each preview row has the
objective-free STATIC score S (material, portal-exit risk, trap, threat,
crowding, dithering, bed blocking) -- the Monte Christo move evaluation minus
its progress term. Executors add objective terms:

  movement(GATHER/SCOUT/ATTACK approach/RETREAT/FEED approach):
      S + w_goal * progress(first step toward target) (x0.7 for sprints)
  contact ATTACK: head-on rows with the nominated enemy, valued by strike value
      under the permitted trade margin
  REPRODUCE: the inherited split geometry/room/threat score
  FEED_ALLY donation: deliberate collision within feed_dist of the crown
  RETREAT emergency: rear-body escape split when nothing else survives

Result: command | None, outcome, status, reason, value (the executor's own
preview score, used by the policy as executor-conditioned value), progress,
path cells, diagnostics. Unchosen results commit nothing.
"""
import world as w
import tactics as tx
import valuation as val
import roles
from params import P

OUT_SURVIVE = "predicted_survive"
OUT_PORTAL = "unknown_portal"
OUT_TRADE = "intentional_head_trade"
OUT_DONATE = "intentional_donation"
OUT_SPLIT = "predicted_split_survive"
OUT_ESCAPE = "child_escape_parent_at_risk"
OUT_DEATH = "predicted_death"


def sprint_paths(body):
    out = [[d] for d in range(4)]
    L = w.LEN
    if L < 3:
        return out
    near = False
    for ec, eid in w.enemy_heads:
        if w.cheb(ec, w.HEAD) <= 4:
            near = True
            break
    if not near:
        return out
    if P["strike_reach"] > 3:
        out.extend(strike_paths(body))
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


def strike_paths(body):
    """Sinbad v06: shortest free paths (up to len-1 steps, max strike_reach)
    onto the head of a visible enemy worth a trade; sim verifies them."""
    L = w.LEN
    if not P["attack"] or w.UNITS < P["atk_units"] or L < 3:
        return []
    reach = min(L - 1, P["strike_reach"])
    if reach <= 3:
        return []
    mine = val.dragon_value(L)
    goals = {}
    for ec, eid in w.enemy_heads:
        if w.tdist(ec, w.HEAD) > reach:
            continue
        el = w.elen.get(eid, 1) + (P["cut_extra"] if eid in w.cut else 0)
        if val.enemy_value(el) - mine >= P["atk_margin"]:
            goals[ec] = eid
    if not goals:
        return []
    own = set(body)
    occ = w.occ
    prev = {w.HEAD: (-1, -1)}
    q = [w.HEAD]
    qi = 0
    depth = {w.HEAD: 0}
    out = []
    while qi < len(q):
        c = q[qi]
        qi += 1
        dc = depth[c]
        if dc >= reach:
            continue
        g = w.dest(c)
        for d in range(4):
            n = g[d]
            if n < 0 or n in depth:
                continue
            if n in goals:
                path = [d]
                x = c
                while x != w.HEAD:
                    px, pd = prev[x]
                    path.append(pd)
                    x = px
                path.reverse()
                if len(path) > 3:
                    out.append(path)
                depth[n] = dc + 1
                continue
            if n in own or n in occ:
                continue
            depth[n] = dc + 1
            prev[n] = (c, d)
            q.append(n)
    return out


def need_area():
    L = w.LEN
    need = max(L + P["slack"], P["min_area"])
    if L >= 10:
        return min(need + L // 3, P["flood_cap_long"])
    return min(need, P["flood_cap"])


def previews(ctx):
    """Shared, objective-free movement previews (turn-local cache in ctx)."""
    rows = ctx.get("rows")
    if rows is not None:
        return rows
    body = w.body
    L = w.LEN
    lv = val.lv_now()
    threat = ctx["threat"]
    need = need_area()
    crown_flank = ctx.get("crown_flank", ())
    rows = []
    for path in sprint_paths(body):
        st, nb, eaten, hit = tx.sim(path, body)
        steps = len(path)
        row = dict(path=path, state=st, hit=hit, eaten=eaten, body=nb, area=None, exposure=0.0,
                   blind=0)
        if st == "dead":
            row["S"] = -1000.0 - steps
        elif st == "dive":
            row["S"] = P["dive_base"] - P["p_dive"] * val.dragon_value(L) \
                - val.threat_cost(w.HEAD, L, threat) * 0.5
        elif st == "h2h":
            row["S"] = None  # valued by the contact executor / bad-trade floor
        else:
            h = nb[-1]
            s = lv * (len(nb) - L) - P["w_sprint"] * (steps - 1)
            if tx.BLIND[0]:
                row["blind"] = 1
                s -= P["p_blind"] * blind_risk(nb[-steps:]) * val.dragon_value(len(nb))
            if eaten:
                s += 0.5 * eaten
            row["pre_goal"] = s
            area = tx.flood(nb, need, 0)
            row["area"] = area
            pen = 0.0
            if area < need:
                wt = P["w_trap"] if area <= len(nb) else P["w_trap_soft"]
                pen = wt * (need - area) / need
                if area < len(nb):
                    pen += P["w_trap"]
                k = tx.POCKET[0]
                if len(nb) + k >= P["split_min"] and len(nb) + k > area + 1 \
                        and w.UNITS < w.LIMIT:
                    pen *= P["farm_factor"]
                vs = val.dragon_value(len(nb)) / P["v_ref"]
                if vs > 1.0:
                    pen *= vs
                if P["trap_cap"]:
                    pen = min(pen, P["trap_cap"] * val.dragon_value(len(nb)))
            risk = val.threat_cost(h, len(nb), threat)
            row["exposure"] = risk
            post = [pen, risk]  # subtracted in this order (Monte Christo float order)
            for hc, hid in w.ally_heads:
                dd = w.tdist(hc, h)
                if dd <= 2:
                    post.append(P["w_crowd"] * (3 - dd))
            post.append(P["w_visit"] * w.visits[h])
            flank = P["w_flank"] if h in crown_flank else 0.0
            bedb = P["w_bed_block"] if (w.bed[h] == 2 and w.spawn.get(h, -9) == w.RND + 1) else 0.0
            row["post"] = post
            row["flank"] = flank
            row["bedb"] = bedb
            row["S"] = None  # composed with the objective term (float order kept)
        rows.append(row)
    ctx["rows"] = rows
    return rows


def blind_risk(cells):
    """Feature `blind_mem` (0 = inherited constant 1): chance-scale that a
    portal exit outside our view is occupied, from remembered occupancy:
    1 if any exit cell or its neighbours held another dragon within
    blind_recent rounds, blind_unseen if the exit was not seen within that
    time, else blind_floor."""
    if not P["blind_mem"]:
        return 1.0
    rnd = w.RND
    rec = P["blind_recent"]
    risk = P["blind_floor"]
    for c in cells:
        if w.cheb(c, w.HEAD) <= 3:
            continue
        if rnd + 1 - w.seen[c] > rec:
            risk = max(risk, P["blind_unseen"])
        for x in (c,) + tuple(w.nbr(c)):
            r = w.body_seen.get(x)
            if r is not None and rnd - r <= rec:
                return 1.0
    return risk


def progress_vector(target, ctx):
    prog = [0, 0, 0, 0]
    if target < 0 or target == w.HEAD:
        return prog
    mask = ctx["mask"]
    tm = mask.get(target)
    if tm is None:
        wp = -1
        wv = 1 << 30
        for c, t in ctx["dist"].items():
            if t:
                v = 3 * w.tdist(c, target) + t
                if v < wv:
                    wv = v
                    wp = c
        if wp < 0:
            return prog
        tm = mask[wp]
    for d in range(4):
        prog[d] = 1 if (tm >> d) & 1 else -1
    return prog


def result(c, command=None, outcome="none", status="unavailable", reason="", value=None,
           row=None, **extra):
    target = c["target"]
    end = w.HEAD
    if row is not None and row["state"] == "ok":
        end = row["body"][-1]
    prog = w.tdist(w.HEAD, target) - w.tdist(end, target) if target >= 0 else 0
    path_cells = []
    if row is not None and row["state"] == "ok" and len(row["path"]) > 1:
        path_cells = row["body"][-len(row["path"]):-1]
    r = dict(command=command, outcome=outcome, status=status, reason=reason, value=value,
             progress=prog, path_cells=path_cells, fallback=False, reports=[],
             exposure=row["exposure"] if row else None, area=row["area"] if row else None)
    r.update(extra)
    return r


def movement(c, ctx, goal_weight=None):
    """Best previewed move toward c's target. Includes the inherited floors:
    unfavourable trades (-950) and ally collisions (-1100) beat dying (-1000-)."""
    rows = previews(ctx)
    prog = progress_vector(c["target"], ctx)
    wg = P["w_goal"] if goal_weight is None else goal_weight
    dive = c["params"].get("dive", -1)
    kind = c["kind"]
    best = None
    bs = -1e18
    for row in rows:
        st = row["state"]
        path = row["path"]
        steps = len(path)
        if st == "ok":
            s = row["pre_goal"]
            s += wg * prog[path[0]] * (1.0 if steps == 1 else 0.7)
            for x in row["post"]:
                s -= x
            if row["flank"]:
                s -= row["flank"]
            if row["bedb"]:
                s -= row["bedb"]
            if kind == "RETREAT" and c["params"].get("support"):
                s -= P["support_exposure"] * row["exposure"]
        elif st == "dive":
            s = row["S"]
            if dive == path[0] and c["target"] == w.HEAD:
                s += P["v_dive"] * 0.5
        elif st == "h2h":
            sv = val.strike_value(row["hit"], steps)
            if sv is not None:
                continue  # a favourable trade belongs to the contact objective
            s = -950.0 if row["hit"] in w.elen else -1100.0
        else:
            s = row["S"]
        if s > bs:
            bs = s
            best = row
    if best is None:
        return result(c, reason="no_moves")
    st = best["state"]
    outcome = OUT_SURVIVE if st == "ok" else OUT_PORTAL if st == "dive" else OUT_DEATH
    if st == "ok" and best["blind"]:
        outcome = OUT_PORTAL
    done = st == "ok" and best["body"][-1] == c["target"]
    return result(c, ("move", best["path"]), outcome, "completed" if done else "active", "route",
                  bs, best)


def contact(c, ctx, margin=None):
    rows = previews(ctx)
    best = None
    bs = -1e18
    for row in rows:
        if row["state"] == "h2h" and row["hit"] == c["subject"]:
            sv = val.strike_value(row["hit"], len(row["path"]), margin)
            if sv is not None and sv > bs:
                bs = sv
                best = row
    if best is None:
        return result(c, reason="no_favourable_contact")
    return result(c, ("move", best["path"]), OUT_TRADE, "completed", "contact", bs, best)


def reproduce(c, ctx):
    body = w.body
    L = w.LEN
    n = c["params"]["child"]
    if L < P["split_min"] or L - n < 2 or w.UNITS >= w.LIMIT or len(body) < L:
        return result(c, reason="illegal")
    if w.RND >= P["split_stop"] or w.RND >= P["grow_from"] or roles.ROLE[0] != "forager":
        return result(c, reason="phase_or_role")
    child = body[:n][::-1]
    ch = child[-1]
    cown = set(child)
    pown = set(body[n:])
    ok = 0
    for x in w.dest(ch):
        if x >= 0 and x not in cown and x not in pown and x not in w.occ:
            ok += 1
    if not ok:
        return result(c, reason="child_blocked")
    if tx.flood(child, P["child_area"], 0) < P["child_area"]:
        return result(c, reason="child_room")
    parent = body[n:]
    s = P["split_val"]
    pneed = min(max(L - n + P["slack"], P["min_area"]), P["flood_cap"])
    area = tx.flood(parent, pneed, 0)
    if area < pneed:
        pen = P["w_trap"] * (pneed - area) / pneed
        if P["trap_cap"]:
            pen = min(pen, P["trap_cap"] * val.dragon_value(L - n))
        s -= pen
    s -= val.threat_cost(w.HEAD, L - n, ctx["threat"])
    if ctx["threat"].get(ch):
        s -= 1.0
    return result(c, ("split", n), OUT_SPLIT, "completed", "viable_child", s)


def feed(c, ctx):
    if not roles.fresh() or w.crown is None or w.crown[0] != c["subject"]:
        return result(c, reason="ally_expired")
    ch = roles.crown_visible()
    if ch >= 0 and w.tdist(ch, w.HEAD) <= P["feed_dist"]:
        back = (w.FACE + 2) % 4
        for d in [back, 0, 1, 2, 3]:
            if tx.sim([d], w.body)[0] == "dead":
                r = result(c, ("move", [d]), OUT_DONATE, "completed", "crown_nearby", 0.0)
                r["donate"] = True
                return r
    return movement(c, ctx)


def trap_pen(bd, need, other=()):
    """Trap penalty of a body (tail..head) as in the move preview, and the area.
    `other`: a sibling body (tail..head) that vacates from its tail (segment i
    free from move i + 2), temporarily added to world vacancy."""
    saved = {}
    for i, x in enumerate(other):
        saved[x] = w.vac.get(x)
        w.vac[x] = i + 2
    try:
        area = tx.flood(bd, need, 0)
    finally:
        for x, v in saved.items():
            if v is None:
                del w.vac[x]
            else:
                w.vac[x] = v
    if area >= need:
        return 0.0, area
    L = len(bd)
    wt = P["w_trap"] if area <= L else P["w_trap_soft"]
    pen = wt * (need - area) / need
    if area < L:
        pen += P["w_trap"]
    vs = val.dragon_value(L) / P["v_ref"]
    if vs > 1.0:
        pen *= vs
    if P["trap_cap"]:
        pen = min(pen, P["trap_cap"] * val.dragon_value(L))
    return pen, area


def body_need(L):
    need = max(L + P["slack"], P["min_area"])
    if L >= 10:
        return min(need + L // 3, P["flood_cap_long"])
    return min(need, P["flood_cap"])


def escape(c, ctx):
    """E0: inherited last resort (value -500, admitted below the despair gate).
    E1 (P["escape_eval"]): evaluate cutting the body at several points; the
    child is the reversed rear, its head at the old tail. Value = -(trap and
    threat penalties of both bodies); a child we cannot see (body only partly
    known) is charged blind_child x its value. No production bonus: this is
    material preservation, compared against the best move by the policy."""
    body = w.body
    L = w.LEN
    if L < 4 or w.UNITS >= w.LIMIT:
        return result(c, reason="illegal")
    if not P["escape_eval"]:
        if len(body) < L:
            return result(c, reason="illegal")
        n = L - 2
        child = body[:n][::-1]
        ch = child[-1]
        cown = set(child)
        pown = set(body[n:])
        for x in w.dest(ch):
            if x >= 0 and x not in cown and x not in pown and x not in w.occ:
                return result(c, ("split", n), OUT_ESCAPE, "active", "emergency_split", -500.0)
        return result(c, reason="no_escape_split")
    known = len(body)  # body = trail[-LEN:] or the visible chain (head side)
    sizes = sorted(set([L - 2, L // 2, 2]), reverse=True)
    threat = ctx["threat"]
    best = None
    for n in sizes:
        if n < 2 or L - n < 2:
            continue
        if L - n > known:
            continue  # the parent itself is not fully known
        parent = body[-(L - n):]
        if known >= L:
            child = body[:n][::-1]
            ch = child[-1]
            cown = set(child)
            pown = set(parent)
            if not any(x >= 0 and x not in cown and x not in pown and x not in w.occ
                       for x in w.dest(ch)):
                continue
            cpen, _ = trap_pen(child, body_need(n), parent)
            cpen += val.threat_cost(ch, n, threat)
            blind = False
            sib = child
        else:
            cpen = P["blind_child"] * val.dragon_value(n)
            blind = True
            sib = body[:known - (L - n)][::-1]  # the visible part of the child
        ppen, _ = trap_pen(parent, body_need(L - n), sib)
        ppen += val.threat_cost(w.HEAD, L - n, threat)
        v = -ppen - cpen
        if best is None or v > best[0]:
            best = (v, n, blind)
    if best is None:
        return result(c, reason="no_escape_split")
    return result(c, ("split", best[1]), OUT_ESCAPE, "active",
                  "evaluated_split_blind" if best[2] else "evaluated_split", best[0])


def execute(c, ctx):
    kind = c["kind"]
    p = c["params"]
    if kind == "REPRODUCE":
        return reproduce(c, ctx)
    if kind == "FEED_ALLY":
        return feed(c, ctx)
    if kind == "ATTACK" and p.get("contact"):
        return contact(c, ctx, p.get("margin"))
    if kind == "RETREAT" and p.get("emergency_split") and c["target"] < 0:
        return escape(c, ctx)
    if kind == "GATHER" and c["target"] not in w.pearls and w.bed[c["target"]] != 2:
        return result(c, reason="resource_gone")
    return movement(c, ctx)


def fallback(ctx, reason):
    """No WAIT exists: first predicted-surviving single step, else keep facing."""
    for d in range(4):
        if tx.sim([d], w.body)[0] == "ok":
            return dict(command=("move", [d]), outcome=OUT_SURVIVE, status="interrupted",
                        reason=reason, value=None, progress=0, path_cells=[], fallback=True,
                        reports=[])
    return dict(command=("move", [w.FACE]), outcome=OUT_DEATH, status="interrupted",
                reason=reason + ":no_surviving_move", value=None, progress=0, path_cells=[],
                fallback=True, reports=[])

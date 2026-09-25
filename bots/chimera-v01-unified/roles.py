"""roles.py -- doctrine: production (split value, team size), child role
mix, crown election / feeding, emergency split.
"""

# ======================================================================
# PRODUCTION
# ======================================================================
def team_target():
    if NC <= 600:
        t = P["team_target_small"]
    elif NC <= 2000:
        t = P["team_target_mid"]
    else:
        t = P["team_target_big"]
    return min(t, UNIT_LIMIT)


def child_role():
    if RND < P["early_end"]:
        mix = P["mix_early"]
    elif RND < P["mid_end"]:
        mix = P["mix_mid"]
    else:
        mix = P["mix_late"]
    if NC <= P["scout_min_cells"]:
        if RND < P["early_end"]:
            mix = P["mix_early_small"]
        elif RND < P["mid_end"]:
            mix = P["mix_mid_small"]
        else:
            mix = (mix[0] + mix[2] * 0.5, mix[1] + mix[2] * 0.5, 0.0)
    counts = [0.0, 0.0, 0.0]
    n = 0
    for aid, (c, ln, r, when) in allies.items():
        if RND - when < 25 and r < 3:
            counts[r] += 1
            n += 1
    # deterministic: the most under-represented role
    best = 0
    bd = -1e9
    for r in range(3):
        deficit = mix[r] * (n + 1) - counts[r]
        if mix[r] <= 0:
            continue
        if deficit > bd:
            bd = deficit
            best = r
    return best


def phase_mix():
    """The doctrine's child role mix (gather, hunt, scout) for this round and map."""
    if RND < P["early_end"]:
        mix = P["mix_early"]
    elif RND < P["mid_end"]:
        mix = P["mix_mid"]
    else:
        mix = P["mix_late"]
    if NC <= P["scout_min_cells"]:
        if RND < P["early_end"]:
            mix = P["mix_early_small"]
        elif RND < P["mid_end"]:
            mix = P["mix_mid_small"]
        else:
            mix = (mix[0] + mix[2] * 0.5, mix[1] + mix[2] * 0.5, 0.0)
    return mix


def orphan_role():
    """A newborn whose hand-off ray missed (the parent's body bent at its new
    tail, so the refracted ray left in another direction: about half of all
    splits).  Draw the role from the doctrine mix with a hash of our id."""
    mix = phase_mix()
    tot = mix[0] + mix[1] + mix[2]
    if tot <= 0:
        return GATHER
    u = ((MY_ID * 2654435761) & 0xFFFF) / 65536.0 * tot
    for r in range(3):
        u -= mix[r]
        if u < 0:
            return r
    return GATHER


def emergency_split():
    """Every way forward is death: shed the body so the tail end lives on.
    The newborn (head on our tail, facing away) takes all but 2 segments."""
    if LEN < 4 or UNITS >= UNIT_LIMIT:
        return 0
    body = body_list()
    if len(body) < LEN:
        return 0
    n = LEN - 2
    ch = body[0]
    ch2 = body[1]
    parent = set(body[n:])
    for m in dest(ch):
        if m >= 0 and m != ch2 and m not in parent and m not in occ:
            return n
    return 0


def split_value(head_risk_now):
    if ROLE == CROWN:
        return None
    if RND >= P["split_stop"] or LEN < P["split_min"] or UNITS >= UNIT_LIMIT:
        return None
    n = P["child_size"]
    if LEN - n < 2:
        return None
    target = team_target()
    if UNITS >= target:
        return None
    if head_risk_now > P["split_danger_max"] * P["unit_value"]:
        return None
    # a newborn in a packed window is a future traffic death, not a unit
    crowd = 0
    for o in occ.values():
        if o[1]:
            crowd += 1
    if crowd > P["split_crowd_max"]:
        return None
    # the newborn: head on our tail, facing away from our body.  It must
    # have somewhere to go, and not straight into a tunnel with a head in it.
    body = body_list()
    if len(body) < LEN:
        return None
    ch = body[0]
    ch2 = body[1]
    parent = set(body[n:])
    ok = 0
    for m in dest(ch):
        if m < 0 or m == ch2 or m in parent or m in occ:
            continue
        if tunnel_heads(m, ch):
            continue
        if doom(m, [ch2, ch, m][-2:] if n == 2 else [ch, m]) >= 0:
            continue
        ok += 1
    if ok == 0:
        return None
    # value of a unit falls as we approach target
    frac = UNITS / float(target)
    return P["w_split"] * (1.2 - frac) - (1.0 if ok == 1 else 0.0), n


def update_role():
    """Crown election / demotion, crown beacon, endgame feeding.
    Returns True when this dragon should take no action (feed: die here)."""
    global ROLE
    best_crown = -1
    for aid, (c, ln, r, when) in allies.items():
        if r == CROWN and RND - when < P["crown_memory"] and ln > best_crown:
            best_crown = ln
    if CROWN_INFO[0] >= 0 and RND - CROWN_INFO[2] < P["crown_memory"] and CROWN_INFO[1] > best_crown:
        best_crown = CROWN_INFO[1]
    if ROLE != CROWN and RND >= P["crown_start"] and LEN >= P["crown_min_len"]:
        # the length race: one dragon stops splitting and banks length.  We
        # volunteer when no ally crown is known, or the known ones are clearly
        # shorter than us (they may be dying).
        if best_crown < 0 or LEN >= best_crown + 3:
            ROLE = CROWN
    elif ROLE == CROWN and best_crown >= LEN + P["crown_demote"]:
        # a clearly longer crown exists: stand down, grow / split / feed it
        ROLE = GATHER
    FEED[0] = -1
    if ROLE == CROWN and RND >= P["crown_start"] and (RND & 1) == 0:
        # crowns beacon (relayed a few hops) so that there is one crown, and
        # so that feeders can find it at the end
        relay_q.insert(0, crown_packet(P["beacon_ttl"]))
    if RND >= P["feed_start"] and ROLE != CROWN and LEN <= P["feed_max_len"]:
        # endgame: only the longest dragon counts at round 500.  A small
        # dragon near our crown dies next to it; its corpse is pearls the
        # crown eats (ceil(len/2) of them).
        cc = -1
        cl = 0
        for aid, (c, ln, r, when) in allies.items():
            if r == CROWN and RND - when <= 3 and ln > cl:
                cc = c
                cl = ln
        if CROWN_INFO[0] >= 0 and RND - CROWN_INFO[2] <= P["beacon_memory"] \
                and CROWN_INFO[1] > cl:
            cc = CROWN_INFO[0]
            cl = CROWN_INFO[1]
        if cc >= 0 and cl > LEN:
            d = tdist(HEAD, cc)
            if d <= P["feed_dist"]:
                direct = visible_crown()
                if direct is not None:
                    direct_len, _direct_id, direct_cell = direct
                    if direct_len > LEN and tdist(HEAD, direct_cell) <= P["feed_dist"] \
                            and UNITS >= P["feed_min_units"] \
                            and not enemy_near(direct_cell, P["feed_enemy_radius"],
                                               P["feed_enemy_memory"]):
                        return True  # verified no-action death beside the visible crown
            if d <= P["feed_range"]:
                FEED[0] = cc
    return False


def neck_dir():
    """Direction from the head into our own neck segment (-1 if unknown)."""
    body = body_list()
    if len(body) < 2:
        return None
    neck = body[-2]
    ds = dest(HEAD)
    for d in range(4):
        if ds[d] == neck or nbr(HEAD)[d] == neck:
            return d
    return None


def longest_known_ally():
    best = 0
    for aid, (c, ln, r, when) in allies.items():
        if RND - when < 30 and ln > best:
            best = ln
    return best


def visible_crown():
    """Return a fresh crown report only while that dragon is in direct view.

    A relayed beacon may guide a feeder toward the crown, but it cannot by
    itself authorize a deliberate death.
    """
    best = None
    for cell, (aid, ours, is_head, _facing) in occ.items():
        if not ours or not is_head:
            continue
        report = allies.get(aid)
        if report is None:
            continue
        report_cell, ln, role, when = report
        if role != CROWN or RND - when > 2 or ln <= LEN:
            continue
        item = (ln, aid, cell)
        if best is None or item[0] > best[0]:
            best = item
    return best


def enemy_near(cell, radius, memory):
    for enemy_cell, _eid in enemy_heads:
        if tdist(cell, enemy_cell) <= radius:
            return True
    for enemy_cell, when, _ln in enemies.values():
        if RND - when <= memory and tdist(cell, enemy_cell) <= radius:
            return True
    return False

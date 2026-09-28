"""Directional echo radar with a low-cost, short-lived enemy lane warning.

Echoes aggregate all rays, so a directional reading is only trusted when
Heimdall deliberately casts one ray and suppresses lower-priority packets.
Critical crown, prey, and split-handoff messages keep their slots.
"""
import comms
import world as w

SCAN_PERIOD = 4
ECHO_TTL = 2
HEAD_LANE_COST = 1.6
BODY_LANE_COST = 0.35
LAST_SCAN = None  # (round, post-action origin, absolute direction)
LEADS = []        # (origin, direction, observed round, kind)


def init():
    global LAST_SCAN
    LAST_SCAN = None
    del LEADS[:]


def observe_echo():
    """Associate this turn's echo with last turn's single-ray scan."""
    if LAST_SCAN is None or LAST_SCAN[0] != w.RND - 1:
        return
    kelp, ally, ally_head, enemy, enemy_head = w.echo
    kind = "head" if enemy_head else "body" if enemy else None
    if kind is not None:
        LEADS.append((LAST_SCAN[1], LAST_SCAN[2], w.RND, kind))
    LEADS[:] = [lead for lead in LEADS if 0 <= w.RND - lead[2] <= ECHO_TTL]


def _critical(messages):
    for packet in messages.values():
        decoded = comms.unpack(packet)
        if decoded is not None and decoded[0] in (comms.T_CROWN, comms.T_PREY, comms.T_HANDOFF):
            return True
    return False


def schedule(messages, post_body):
    """Use one isolated echo scan every fourth action when critical radio is idle."""
    global LAST_SCAN
    if (w.RND + w.ME) % SCAN_PERIOD or _critical(messages):
        return
    body = post_body
    head = body[-1] if body else w.HEAD
    turn = (w.RND + w.ME) // SCAN_PERIOD
    directions = [(turn + k) % 4 for k in range(4)]
    neck = body[-2] if len(body) > 1 else -1
    for direction in directions:
        adjacent = w.dest(head)[direction]
        if adjacent == -2:
            adjacent = w.nbr(head)[direction]
        if adjacent == neck:
            continue  # own-body refraction would make the ray direction ambiguous
        # A single zero-payload ray still casts and returns an echo. Receivers
        # reject zero as an invalid packet, so no message format is consumed.
        messages.clear()
        messages[w.DIRS[direction]] = 0
        LAST_SCAN = (w.RND, head, direction)
        return


def lane_penalty(cell):
    """Small route cost for stepping into a freshly pinged enemy ray lane."""
    best = 0.0
    for origin, direction, rnd, kind in LEADS:
        age = w.RND - rnd
        if not 0 <= age <= ECHO_TTL:
            continue
        ox, oy = origin % w.W, origin // w.W
        x, y = cell % w.W, cell // w.W
        if direction in (0, 2):
            delta = abs(x - ox)
            across = min(delta, w.W - delta)
            forward = (oy - y) % w.H if direction == 0 else (y - oy) % w.H
            transverse = across
        else:
            delta = abs(y - oy)
            across = min(delta, w.H - delta)
            forward = (x - ox) % w.W if direction == 1 else (ox - x) % w.W
            transverse = across
        if forward == 0 or transverse > 1:
            continue
        base = HEAD_LANE_COST if kind == "head" else BODY_LANE_COST
        cost = base * (0.55 ** age) * (1.0 if transverse == 0 else 0.25)
        if cost > best:
            best = cost
    return best

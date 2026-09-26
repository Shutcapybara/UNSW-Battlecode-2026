"""comms.py -- sonar packets (check 8 | kind 4 | payload 52), hearing,
relay queue and the 4-ray scheduler.

Consumers: K_SELF -> allies (traffic, ownership, role census, crown);
K_ENEMY -> enemies/zone heat (hunter targeting, danger); K_PORTAL -> terrain;
K_BED -> spawn_at (targeting); K_HANDOFF -> newborn role/target;
K_DOOM -> doomed (w_doomed); K_CROWN -> CROWN_INFO (election, feeding).
"""

# ======================================================================
# SONAR PACKETS  (check 8 | kind 4 | payload 52)
# ======================================================================
K_SELF, K_ENEMY, K_PORTAL, K_BED, K_HANDOFF, K_DOOM, K_CROWN = 1, 2, 3, 4, 5, 6, 7
K_HOT = 8          # pearl hotspot (hunter-v15 style): consumer = ladder explore pull
SALT = 0
HOT = {}           # cell -> [round observed, strength 1..12] heard from allies
HOTC = [-1, None]  # per-turn cache of hotspots()


def chk(body):
    h = SALT
    b = body
    for _ in range(4):
        h = (h * 167 + (b & 0x3FFF)) & 0xFFFF
        b >>= 14
    return (h ^ (h >> 8)) & 0xFF


def pack(kind, payload):
    body = (kind << 52) | (payload & ((1 << 52) - 1))
    return (chk(body) << 56) | body


def unpack(v):
    body = v & ((1 << 56) - 1)
    if (v >> 56) != chk(body):
        return None
    return body >> 52, body & ((1 << 52) - 1)


def self_packet():
    return pack(K_SELF, (MY_ID & 0xFFF) << 40 | (HEAD & 0xFFF) << 28 | (min(LEN, 255) << 20)
                | (ROLE & 3) << 18 | (min(UNITS, 127) << 11) | (MOVED_DIR & 3) << 9)


def enemy_packet(cell, ln, eid, ttl):
    return pack(K_ENEMY, (ttl & 3) << 50 | (eid & 0xFFF) << 36 | (cell & 0xFFF) << 24
                | (min(ln, 255) << 16) | (RND & 0x1FF))


def portal_packet(pid):
    a, b = pends[pid][0], pends[pid][1]
    return pack(K_PORTAL, (2 << 50) | (pid & 0xFF) << 32 | (a & 0xFFFF) << 16 | (b & 0xFFFF))


def bed_packet(cell, when, ttl):
    return pack(K_BED, (ttl & 3) << 50 | (cell & 0xFFF) << 20 | (when & 0x3FF))


def handoff_packet(role, target):
    return pack(K_HANDOFF, (role & 3) << 40 | ((target + 1) & 0x1FFF) << 24 | (RND & 0x1FF))


def crown_packet(ttl):
    return pack(K_CROWN, (ttl & 3) << 50 | (HEAD & 0xFFF) << 20 | (min(LEN, 255) << 12)
                | (RND & 0x1FF))


def doom_packet(cell, ttl):
    return pack(K_DOOM, (ttl & 3) << 50 | (cell & 0xFFF) << 20 | (RND & 0x1FF))


def report_doom():
    """Every way forward is a dead end: tell the team where the trap starts
    (the first corridor cell after the last junction on our trail)."""
    global doom_told
    if doom_told:
        return
    cells = trail[-40:]
    entrance = cells[-1]
    for i in range(len(cells) - 2, -1, -1):
        c = cells[i]
        exits = 0
        for n in dest(c):
            if n >= 0:
                exits += 1
        if exits >= 3:
            entrance = cells[i + 1]
            break
        entrance = c
    doom_told = True
    doomed[entrance] = RND
    relay_q.insert(0, doom_packet(entrance, 2))
    relay_q.insert(0, doom_packet(entrance, 2))


def hot_packet(cell, obs, strength):
    return pack(K_HOT, (cell & 0xFFF) << 20 | (strength & 0xF) << 12 | (obs & 0x1FF))


def hotspots():
    """(cell, round observed, strength) we know of, fresh within 8 rounds:
    pearls in view (12), beds in view due within 8 rounds (6 - due/2, min 1),
    and hotspots heard from allies (dropped once we see the cell empty).
    Cached per turn (the ladder and the sonar scheduler both ask)."""
    if HOTC[0] == RND:
        return HOTC[1]
    out = {}
    for c, r in pearls.items():
        if r == RND:
            out[c] = (RND, 12)
    for c, w in spawn_at.items():
        cd = w - RND
        if 0 <= cd <= 8 and c not in out:
            st = 6 - cd // 2
            out[c] = (RND, st if st > 1 else 1)
    for c in list(HOT):
        obs, st = HOT[c]
        if RND - obs > 8 or (seen[c] == RND + 1 and c not in out):
            del HOT[c]
        elif c not in out:
            out[c] = (obs, st)
    HOTC[0] = RND
    HOTC[1] = out
    return out


def pick_hot():
    """hunter's rotation over the 8 strongest hotspots."""
    hs = hotspots()
    if not hs:
        return None
    top = sorted(hs.items(), key=lambda kv: (-kv[1][1], kv[0]))[:8]
    c, (obs, st) = top[(RND // 4 + MY_ID) % len(top)]
    return hot_packet(c, obs, st)


def relay(kind, payload, ttl):
    if ttl <= 1 or len(relay_q) >= P["relay_max"]:
        return
    key = (kind, payload & ~(3 << 50))
    if relayed.get(key, -99) > RND - 20:
        return
    relayed[key] = RND
    relay_q.append(pack(kind, (payload & ~(3 << 50)) | ((ttl - 1) << 50)))


def hear(v):
    global handoff
    got = unpack(v)
    if got is None:
        return
    kind, pl = got
    if kind == K_SELF:
        aid = (pl >> 40) & 0xFFF
        if aid != (MY_ID & 0xFFF):
            cell = (pl >> 28) & 0xFFF
            if cell < NC:
                allies[aid] = (cell, (pl >> 20) & 0xFF, (pl >> 18) & 3, RND)
                ally_face[aid] = (pl >> 9) & 3
    elif kind == K_ENEMY:
        cell = (pl >> 24) & 0xFFF
        if cell < NC:
            eid = (pl >> 36) & 0xFFF
            ln = (pl >> 16) & 0xFF
            cur = enemies.get(eid)
            if cur is None or cur[1] < RND - 1:
                enemies[eid] = (cell, RND - 1, ln)
                heat_zone(cell, 1.0)
            relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_PORTAL:
        a = (pl >> 16) & 0xFFFF
        b = pl & 0xFFFF
        pid = (pl >> 32) & 0xFF
        for k in (a, b):
            if k < 2 * NC and ek[k] == 0:
                ek[k] = 3
                epid[k] = pid
                edge_known(k)
        if a < 2 * NC and b < 2 * NC:
            ends = pends.setdefault(pid, [])
            for k in (a, b):
                if k not in ends and len(ends) < 2:
                    ends.append(k)
            if len(ends) == 2:
                portal_paired(ends[0])
                portal_paired(ends[1])
        relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_BED:
        cell = (pl >> 20) & 0xFFF
        if cell < NC and not fertile[cell]:
            fertile[cell] = 1
            when = pl & 0x3FF
            if when > RND:
                spawn_at[cell] = when
            relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_CROWN:
        cell = (pl >> 20) & 0xFFF
        if cell < NC:
            ln = (pl >> 12) & 0xFF
            if CROWN_INFO[2] < RND - 1 or ln >= CROWN_INFO[1]:
                CROWN_INFO[0] = cell
                CROWN_INFO[1] = ln
                CROWN_INFO[2] = RND
            relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_DOOM:
        cell = (pl >> 20) & 0xFFF
        if cell < NC:
            if cell not in doomed:
                doomed[cell] = RND
                relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_HOT:
        cell = (pl >> 20) & 0xFFF
        if cell < NC:
            obs = RND - ((RND - (pl & 0x1FF)) & 0x1FF)
            st = (pl >> 12) & 0xF
            cur = HOT.get(cell)
            if RND - obs <= 8 and (cur is None or obs > cur[0] or (obs == cur[0] and st > cur[1])):
                HOT[cell] = [obs, st]
    elif kind == K_HANDOFF:
        if handoff is None and RND - (pl & 0x1FF) <= 1:
            handoff = ((pl >> 40) & 3, ((pl >> 24) & 0x1FFF) - 1)


def broadcast_sightings():
    """Remember every visible enemy head, heat its zone, queue a relayed report."""
    for c, eid in enemy_heads:
        ln = enemy_len.get(eid, 2)
        enemies[eid] = (c, RND, ln)
        heat_zone(c, 0.5)
        if len(relay_q) < P["relay_max"] and told.get(eid, -99) < RND - 3:
            told[eid] = RND
            relay_q.append(enemy_packet(c, ln, eid, P["enemy_ttl"]))


def send_sonars(split_dir=None, handoff_msg=None):
    """Four rays.  Gossip (relay queue) takes up to `gossip_slots` of them,
    rotating; every other ray carries our self report (position + heading),
    which is what lets allies keep out of the tunnel we are in."""
    sp = self_packet()
    start = RND & 3
    ng = P["gossip_slots"]
    nh = P["hot_slots"] if P["hot_slots"] and ladder_active() else 0
    hp = pick_hot() if nh else None
    for j in range(4):
        d = (start + j) & 3
        if d == split_dir and handoff_msg is not None:
            emit("SONAR %s %d" % (DIRS[d], handoff_msg))
        elif ng > 0 and relay_q:
            emit("SONAR %s %d" % (DIRS[d], relay_q.pop(0)))
            ng -= 1
        elif nh > 0 and hp is not None:
            emit("SONAR %s %d" % (DIRS[d], hp))
            nh -= 1
        else:
            emit("SONAR %s %d" % (DIRS[d], sp))

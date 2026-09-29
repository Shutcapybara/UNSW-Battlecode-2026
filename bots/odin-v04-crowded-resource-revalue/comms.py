"""ENCODING layer: 64-bit sonar packets.

Layout (bit 0 = least significant):
   0..7   tag      team-specific constant (rejects most foreign payloads)
   8..11  type     packet version / kind
  12..55  payload  44 bits, per type below
  56..63  check    8-bit checksum of bits 0..55

Types
  1 CROWN  x:7 y:7 len:8 round:9 id:12 (= 43 bits)
           "dragon <id> of length <len> had its head at (x, y) in <round>"
  4 PREY   same layout as CROWN: a long ENEMY head (hunt target)
  5 PORTAL edge key a:13 edge key b:13 portal id:8 (keys < 2*W*H <= 8192)
  3 HANDOFF payload = crown length:8 round:9; sent back through our own
           body on a split so it reaches the child: "you are the crown now"
  2 FOOD   two entries of x:6 y:6 round:9 (= 42 bits), maps up to 64 x 64
           round <= now: "a pearl was at (x, y) in <round>"
           round >  now: "the bed at (x, y) spawns in <round>"
           an entry with x = y = 63 and round = 511 is empty
  6 DENSITY x:6 y:6 round:9 ally:5 enemy:5 sender:13 (= 44 bits)
           "near (x, y) in <round>, sender saw <ally>/<enemy> unique dragons"
           (aggregate COUNTS, allies include the observer, saturated at 31)
  7 SWARM  x:6 y:6 round:9 ally:4 enemy:4 quadrant:2 sender:13 (= 44 bits)
           "near (x, y) in <round>, sender saw <ally>/<enemy> visible
           SEGMENTS in its sender-relative quadrant <quadrant>" (saturated
           at 15; quadrant geometry in swarm.py -- directional LENGTH density)

The checksum is a mixing hash, not authentication; tag + check reject a
random uint64 with probability 1 - 2^-16.  Ranges: x, y < 128, len capped at
255, round mod 512 (rounds < 500), id mod 4096.
"""
import world as w

T_CROWN = 1
T_FOOD = 2
T_HANDOFF = 3
T_PREY = 4
T_PORTAL = 5
T_DENSITY = 6
T_SWARM = 7
EMPTY21 = 63 | (63 << 6) | (511 << 12)
MASK56 = (1 << 56) - 1


def _tag():
    return 0xF1 if w.TEAM == "A" else 0x0E


def _check(v):
    h = (v * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    return (h >> 56) ^ ((h >> 17) & 0xFF)


def pack(typ, payload):
    v = _tag() | (typ << 8) | ((payload & ((1 << 44) - 1)) << 12)
    return v | (_check(v) << 56)


def unpack(v):
    """-> (type, payload) or None."""
    if v < 0 or v >= (1 << 64):
        return None
    low = v & MASK56
    if (low & 0xFF) != _tag():
        return None
    if (v >> 56) != _check(low):
        return None
    return (low >> 8) & 0xF, low >> 12


def crown_packet(did, cell, length, rnd, typ=T_CROWN):
    x = cell % w.W
    y = cell // w.W
    p = x | (y << 7) | (min(length, 255) << 14) | ((rnd & 511) << 22) | ((did & 4095) << 31)
    return pack(typ, p)


def crown_decode(p):
    x = p & 127
    y = (p >> 7) & 127
    length = (p >> 14) & 255
    r9 = (p >> 22) & 511
    did = (p >> 31) & 4095
    if x >= w.W or y >= w.H or length < 2:
        return None
    # rounds are < 512, so r9 is the round itself; reject reports from the future
    if r9 > w.RND:
        return None
    return did, y * w.W + x, length, r9


def food_packet(entries):
    """entries: up to two (cell, round)."""
    p = 0
    for k in range(2):
        if k < len(entries):
            c, r = entries[k]
            e = (c % w.W) | ((c // w.W) << 6) | ((r & 511) << 12)
        else:
            e = EMPTY21
        p |= e << (21 * k)
    return pack(T_FOOD, p)


def food_decode(p):
    out = []
    for k in range(2):
        e = (p >> (21 * k)) & ((1 << 21) - 1)
        if e == EMPTY21:
            continue
        x = e & 63
        y = (e >> 6) & 63
        r = (e >> 12) & 511
        if x >= w.W or y >= w.H:
            return []  # malformed: reject the packet
        out.append((y * w.W + x, r))
    return out


def handoff_packet(length, rnd):
    return pack(T_HANDOFF, min(length, 255) | ((rnd & 511) << 8))


def handoff_decode(p):
    return p & 255, (p >> 8) & 511


def portal_packet(pid, k1, k2):
    return pack(T_PORTAL, (k1 & 8191) | ((k2 & 8191) << 13) | ((pid & 255) << 26))


def portal_decode(p):
    return p & 8191, (p >> 13) & 8191, (p >> 26) & 255


def density_packet(did, x, y, allies, enemies, rnd):
    """v6: x:6 y:6 round:9 ally:5 enemy:5 sender:13 = 44 bits.

    Counts are rounded unique visible dragons (allies include the observer),
    saturated at 31.  Unsupported coordinates/IDs disable sending instead of
    aliasing identities.  (From the monte_christo-v07 radio study.)"""
    if not (0 <= did < 8192 and w.W <= 64 and w.H <= 64 and 0 <= rnd < 500):
        return None
    xx = int(x + 0.5) % w.W
    yy = int(y + 0.5) % w.H
    aa = min(31, max(1, int(allies + 0.5)))
    ee = min(31, max(0, int(enemies + 0.5)))
    return pack(T_DENSITY, xx | (yy << 6) | (rnd << 12) |
                (aa << 21) | (ee << 26) | (did << 31))


def density_decode(p):
    x, y = p & 63, (p >> 6) & 63
    rnd = (p >> 12) & 511
    allies, enemies = (p >> 21) & 31, (p >> 26) & 31
    did = (p >> 31) & 8191
    if x >= w.W or y >= w.H or allies < 1 or rnd > w.RND or rnd >= 500:
        return None
    return did, x, y, float(allies), float(enemies), rnd


def swarm_packet(did, x, y, quad, ally_len, enemy_len, rnd):
    """v7: x:6 y:6 round:9 ally:4 enemy:4 quadrant:2 sender:13 = 44 bits.

    Lengths are rounded visible segments (allies include the observer's own
    visible body) in ONE sender-relative quadrant, saturated at 15.  Senders
    rotate quadrants (swarm.packet_now), so one sender's full directional
    picture arrives over four turns; receivers key by (sender, quadrant)."""
    if not (0 <= did < 8192 and w.W <= 64 and w.H <= 64 and 0 <= rnd < 500):
        return None
    xx = int(x + 0.5) % w.W
    yy = int(y + 0.5) % w.H
    aa = min(15, max(0, int(ally_len + 0.5)))
    ee = min(15, max(0, int(enemy_len + 0.5)))
    return pack(T_SWARM, xx | (yy << 6) | (rnd << 12) | (aa << 21) |
                (ee << 25) | ((quad & 3) << 29) | (did << 31))


def swarm_decode(p):
    x, y = p & 63, (p >> 6) & 63
    rnd = (p >> 12) & 511
    ally_len, enemy_len = (p >> 21) & 15, (p >> 25) & 15
    quad = (p >> 29) & 3
    did = (p >> 31) & 8191
    if x >= w.W or y >= w.H or rnd > w.RND or rnd >= 500:
        return None
    return did, x, y, quad, float(ally_len), float(enemy_len), rnd

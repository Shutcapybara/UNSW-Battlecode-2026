#!/usr/bin/env python3
"""hydra-v11-macro: observe -> assess -> generate -> evaluate -> act.

Fresh implementation of docs/macro-spec.md phases P0-P2: exact candidate
simulation, one linear evaluation in segment units over simulated end
states, an explicit production schedule, and bed/corpse economy. There is
no priority ladder for movement and no radio yet (radio is P3).

Base: leviathan-v07-local-cache; borrowed: the raw single-write I/O
discipline and the invalidated terrain graph cache (world.py).
"""
import os
import sys

from weights import weights_for
from world import World, DIRS, est_len

DEBUG = os.path.exists('/tmp/hydra_debug')


def read_line():
    line = sys.stdin.readline()
    while line and line[0] in '\r\n':
        line = sys.stdin.readline()
    return line.split()


# ---------------------------------------------------------------- searches

def threat_map(world, W):
    """Cells an enemy head can reach with one action before our next turn,
    priced by sprint distance (p ~ .75/.35/.15). Bodies block: stepping
    into one is a death the enemy will not usually choose."""
    danger = {}
    budget = W['threat_cap']
    dest = world.dest
    occupied = world.occupied
    probs = (0.75, 0.35, 0.15)
    for ident, hc in world.enemy_heads.items():
        elen = est_len(world.enemy_len, ident, 2, world.round)
        depth = 3 if elen >= 4 else (2 if elen >= 3 else 1)
        visited = {hc}
        frontier = [hc]
        for step in range(depth):
            p = probs[step]
            nxt_frontier = []
            for cell in frontier:
                for nb in dest(cell):
                    if nb < 0 or nb in visited or nb in occupied:
                        continue
                    visited.add(nb)
                    nxt_frontier.append(nb)
                    old = danger.get(nb)
                    if old is None or old < p:
                        danger[nb] = p
            frontier = nxt_frontier
            budget -= len(nxt_frontier)
            if budget <= 0 or not frontier:
                break
        if budget <= 0:
            break
    return danger


def torus_dist(world, a, b):
    w, hh = world.w, world.h
    dx = a % w - b % w
    if dx < 0:
        dx = -dx
    if dx > w - dx:
        dx = w - dx
    dy = a // w - b // w
    if dy < 0:
        dy = -dy
    if dy > hh - dy:
        dy = hh - dy
    return dx + dy


def compass(world, W, danger, bed_mult=1.0, danger_mult=1.0):
    """One bounded BFS: pull value per first direction toward fresh pearls,
    predicted bed spawns and the frontier, discounted by 1/d^0.65."""
    w, hh = world.w, world.h
    head = world.head
    rnd = world.round
    dest = world.dest
    seen = world.seen
    beds = world.beds
    contested = set()
    pearls = set(world.pearls_now)
    age_ok = []
    pr = world.pearls
    for c in pr:
        age = rnd - pr[c]
        if 0 <= age < W['pearl_age']:
            pearls.add(c)
            age_ok.append((c, 1.0 / (1.0 + age * 0.08)))
    if world.ally_heads:
        ally_cells = world.ally_heads.values()
        # right-of-way: yield pearls near a much bigger ally (emergent feeding;
        # the swarm funnels food to its length candidates without a radio)
        big_allies = []
        for ident, ac in world.ally_heads.items():
            al = est_len(world.ally_len, ident, 0, rnd)
            if al >= world.length + W['yield_gap']:
                big_allies.append((ac, W['yield_radius']))
        for c in pearls:
            cx, cy = c % w, c // w
            md = torus_dist(world, c, head)
            for ac, ar in big_allies:
                if torus_dist(world, c, ac) <= ar:
                    contested.add(c)
                    break
            if c in contested:
                continue
            for ac in ally_cells:
                if torus_dist(world, c, ac) < md:
                    contested.add(c)
                    break
    fresh = {}
    for c, decay in age_ok:
        if c not in contested:
            fresh[c] = decay

    values = [0.0, 0.0, 0.0, 0.0]
    visited = {head}
    occupied = world.occupied
    bodyset = set(world.body)
    live = world.pearls_now
    hd = dest(head)
    queue = []
    for d in range(4):
        nb = hd[d]
        if nb >= 0 and nb not in visited and nb not in occupied and nb not in bodyset:
            visited.add(nb)
            queue.append((nb, 1, d))
    cap = W['compass_cap']
    camp = W['camp']
    c_pearl = W['c_pearl']
    c_live = W['c_live']
    c_bed = W['c_bed']
    c_frontier = W['c_frontier']
    c_danger = W['c_danger']
    expanded = 0
    for cell, dist, first in queue:
        g = 0.0
        if cell not in contested:
            if cell in live:
                g += c_live
            decay = fresh.get(cell)
            if decay is not None:
                g += c_pearl * decay
            t = beds.get(cell, -1000) - rnd
            if 0 <= t <= dist + camp:
                g += c_bed * bed_mult * (1.0 if t >= dist else 0.5)
            for nb in dest(cell):
                if nb >= 0 and nb not in seen:
                    g += c_frontier
                    break
            # id-seeded decorrelation: the swarm should not share one target
            g *= 0.85 + 0.3 * (((cell * 2654435761 + world.id * 40503) >> 7) & 7) / 7.0
        g -= c_danger * danger_mult * danger.get(cell, 0.0)
        if g > 0.0:
            v = g / dist ** 0.65
            if v > values[first]:
                values[first] = v
        expanded += 1
        if expanded >= cap:
            break
        dd = dest(cell)
        for nb in dd:
            if nb >= 0 and nb not in visited and nb not in occupied and nb not in bodyset:
                visited.add(nb)
                queue.append((nb, dist + 1, first))
    return values


def space(world, head, blocked, cap):
    """Flood-fill freedom, capped; the count is the mobility feature."""
    if cap < 6:
        cap = 6
    visited = {head}
    queue = [head]
    dest = world.dest
    for cell in queue:
        for nb in dest(cell):
            if nb >= 0 and nb not in visited and nb not in blocked:
                visited.add(nb)
                if len(visited) >= cap:
                    return cap
                queue.append(nb)
    return len(visited)


# ---------------------------------------------------------------- decision

def decide(world, W):
    rnd = world.round
    food_w = W['food']  # real multiplier set after the crown election
    dest = world.dest
    head = world.head
    body = world.body
    length = world.length
    occupied = world.occupied
    oset = frozenset(occupied)
    bodyset = set(body)
    pearls_now = world.pearls_now
    w, hh = world.w, world.h
    late = rnd >= W['late_round']

    uv = W['uv0'] + (W['uv_end'] - W['uv0']) * (1.0 if rnd >= W['uv_ramp'] else rnd / W['uv_ramp'])
    danger = threat_map(world, W)

    # -- crown election (before the compass: the crown farms beds) --
    crown = False
    crown_kill = late or rnd >= W['crown_kill_round']
    biggest_ally = 0
    for ident in world.ally_heads:
        biggest_ally = max(biggest_ally, est_len(world.ally_len, ident, 0, rnd))
    if rnd >= W['crown_start']:
        crown = length > biggest_ally + 1
    if crown_kill:
        biggest_enemy = 0
        for ident in world.enemy_heads:
            biggest_enemy = max(biggest_enemy, est_len(world.enemy_len, ident, 0, rnd))
        crown_kill = biggest_enemy >= max(length, biggest_ally) - W['ck_within']
    bed_mult = W['crown_bed_mult'] if crown else 1.0
    risk_mult = W['crown_risk_mult'] if crown else 1.0
    food_mult = W['crown_food_mult'] if crown else (W['late_food_mult'] if late else 1.0)
    food_w = W['food'] * food_mult
    enemy_cells = list(world.enemy_heads.values())
    values = compass(world, W, danger, bed_mult,
                     W['crown_danger_mult'] if crown else 1.0)

    head_id = {}
    for ident, cell in world.enemy_heads.items():
        head_id[cell] = ident
    ally_cells = list(world.ally_heads.values())

    enemy_near = False
    reach = W['sprint_enemy_dist'] + 1
    for eh in world.enemy_heads.values():
        if torus_dist(world, eh, head) <= reach:
            enemy_near = True
            break

    target = W['cap']
    if target > world.limit:
        target = world.limit
    if target * 3 > world.n:  # tiny maps: fry runs ~28 units on 81 tiles
        target = world.n // 3
    tcur = W['t0'] + W['slope'] * rnd
    if tcur < target:
        target = tcur
    urgency = 1.0 - world.units / target if world.units < target else 0.0

    cands = []  # (score, kind, out, cells, len_after)
    hd = dest(head)
    parity_ok = (not W['trade_parity']) or len(ally_cells) + 1 >= len(world.enemy_heads)


    def score_end(b2, l2, eaten, paid, first):
        hc = b2[0]
        s = food_w * (eaten - paid)
        s += values[first]
        if crown and enemy_cells:
            for eh in enemy_cells:
                if torus_dist(world, eh, hc) <= W['crown_spacing']:
                    s -= W['crown_space_pen']
                    break
        if hc not in world.seen:
            s += W['frontier']
        v = world.visits.get(hc, 0)
        s += W['visit'] * (v if v < 10 else 10)
        dng = danger.get(hc, 0.0)
        if dng:
            s -= W['risk'] * risk_mult * dng * (l2 + uv)
        blocked = oset | set(b2)
        sp = space(world, hc, blocked, l2 + 8)
        s += W['mobility'] * (sp if sp < l2 + 6 else l2 + 6)
        ex = 0
        hcd = dest(hc)
        for nb in hcd:
            if nb >= 0 and nb not in blocked:
                ex += 1
        if sp < l2 or ex == 0:
            s += W['trap']
            world.doom[hc] = rnd
        s += W['exits'] * ex
        for ac in ally_cells:
            if ac in hcd:
                s += W['crowd']
                break
        if hc in world.doom:
            s += W['doom']
        if first == world.facing:
            s += W['momentum']
        s += W['jitter'] * (((hc * 2654435761 + rnd * 40503 + world.id) >> 5) & 7)
        return s

    for d0 in range(4):
        nxt = hd[d0]
        if nxt < 0 or nxt in bodyset:
            continue
        other = occupied.get(nxt)
        if other is not None:
            eid = head_id.get(nxt)
            if eid is not None and not crown:
                elen = est_len(world.enemy_len, eid, 3, rnd)
                # normal posture: only trade up-or-equal; crown-kill posture:
                # strike the enemy's big dragons on sight regardless of size
                margin = W['ck_margin'] if (crown_kill and elen >= length) else W['trade_margin']
                if (length >= W['trade_min_len']
                        and elen + margin >= length
                        and world.units >= W['trade_min_units'] and parity_ok):
                    corpse = (length + elen + 1) // 2
                    s = (W['trade'] * (elen - length) + W['trade_unit'] * uv
                         + W['trade_corpse'] * corpse)
                    if crown_kill and elen >= length:
                        s += W['ck_bonus']
                    cands.append((s, 'trade', DIRS[d0], [nxt], 0))
            continue  # any other body: moving there kills only us
        ate = nxt in pearls_now
        # a plain step pushes head and pops tail: length changes only with a
        # pearl (+1); sprint payment (steps 2+) is the -1
        l1 = length + 1 if ate else length
        b1 = [nxt] + body if ate else [nxt] + body[:-1]
        s = score_end(b1, l1, 1 if ate else 0, 0, d0)
        cands.append((s, 'move', DIRS[d0], [nxt], l1))
        # sprints: gated on food at step 1 or a near enemy head (spec section 2).
        # A paying step pops the tail even when it eats: net 0 with a pearl,
        # -1 without; a dragon of length <= 2 that must pay dies.
        if l1 > 2 and (ate or enemy_near):
            h1 = dest(nxt)
            for d1 in range(4):
                nx1 = h1[d1]
                if nx1 < 0 or nx1 in b1 or nx1 in occupied:
                    continue
                ate1 = nx1 in pearls_now
                l2 = l1 - 1 + (1 if ate1 else 0)
                b2 = [nx1] + b1[:-1] if ate1 else [nx1] + b1[:-2]
                s2 = score_end(b2, l2, (1 if ate else 0) + (1 if ate1 else 0), 1, d0)
                cands.append((s2, 'move', DIRS[d0] + DIRS[d1], [nxt, nx1], l2))
                if l2 > 2 and (ate1 or enemy_near) and len(cands) < W['candidates_cap']:
                    h2 = dest(nx1)
                    for d2 in range(4):
                        nx2 = h2[d2]
                        if nx2 < 0 or nx2 in b2 or nx2 in occupied:
                            continue
                        ate2 = nx2 in pearls_now
                        l3 = l2 - 1 + (1 if ate2 else 0)
                        b3 = [nx2] + b2[:-1] if ate2 else [nx2] + b2[:-2]
                        e = (1 if ate else 0) + (1 if ate1 else 0) + (1 if ate2 else 0)
                        s3 = score_end(b3, l3, e, 2, d0)
                        cands.append((s3, 'move', DIRS[d0] + DIRS[d1] + DIRS[d2],
                                      [nxt, nx1, nx2], l3))
                if len(cands) >= W['candidates_cap']:
                    break

    if (urgency > 0.0 and not crown and length >= W['split_min_len']
            and world.units < world.limit and rnd < W['split_stop']):
        free_nb = 0
        for nb in hd:
            if nb >= 0 and nb not in oset and nb not in bodyset:
                free_nb += 1
        # no pocket ban: compact maps are won by churning into the crowd
        # (fry-v14 style); a newborn in a packed pocket can still trade
        s = W['split'] * (W['split_base'] + urgency)
        if free_nb < 2:
            s += W['split_pocket']
        dng = danger.get(head, 0.0)
        if dng:
            s -= W['risk'] * risk_mult * dng * (length + uv)
        for ac in ally_cells:
            if ac in hd:
                s += W['split_crowd']
                break
        cands.append((s, 'split', '2', [], length - 2))

    if not cands:
        # boxed: trade an adjacent enemy head if one exists, else open water,
        # else anything walkable (we are dead either way; take someone with us)
        for d0 in range(4):
            nxt = hd[d0]
            if nxt >= 0 and nxt in head_id:
                return 'MOVE ' + DIRS[d0], [nxt], 0, 'trade'
        for d0 in range(4):
            nxt = hd[d0]
            if nxt >= 0 and nxt not in bodyset and nxt not in occupied:
                return 'MOVE ' + DIRS[d0], [nxt], length, 'panic'
        for d0 in range(4):
            if hd[d0] >= 0 and hd[d0] not in bodyset:
                return 'MOVE ' + DIRS[d0], [hd[d0]], length, 'panic'
        return 'SPLIT 2', [], length - 2, 'panic'

    best = cands[0]
    for c in cands:
        if c[0] > best[0]:
            best = c
    s, kind, out, cells, len_after = best
    if kind == 'trade':
        return 'MOVE ' + out, cells, 0, 'trade'  # we die; no state to keep
    if kind == 'move':
        return 'MOVE ' + out, cells, len_after, 'move'
    return 'SPLIT ' + out, [], len_after, 'split'


def main():
    words = read_line()
    if not words:
        return
    ident = int(words[1])
    team = read_line()[1]
    dims = read_line()
    wid, hei = int(dims[1]), int(dims[2])
    limit = int(read_line()[1])
    world = World(wid, hei, ident, team)
    world.limit = limit
    W = weights_for(wid * hei)
    out = sys.stdout
    while True:
        words = read_line()
        if not words or words[0] == 'ENDGAME':
            return
        rnd = int(words[1])
        facing = DIRS.index(read_line()[1][0])
        length = int(read_line()[1])
        units = int(read_line()[1])
        nmsgs = int(read_line()[1])
        for _ in range(nmsgs):
            read_line()  # protocol 3 payloads; consumed when radio ships (P3)
        first = read_line()
        if first and first[0] == 'ECHOES':
            first = read_line()
        if not first:
            return
        tiles = [first]
        for _ in range(48):
            tiles.append(read_line())
        nparts = int(read_line()[1])
        parts = [read_line() for _ in range(nparts)]
        horiz = [read_line() for _ in range(8)]
        vert = [read_line() for _ in range(7)]
        world.observe(rnd, tiles, parts, horiz, vert, facing, length, units)
        action, cells, len_after, kind = decide(world, W)
        if kind in ('move', 'panic', 'split'):
            if kind == 'split':
                world.commit_split(len_after)
            else:
                world.commit_move(cells, len_after)
        if DEBUG:
            b = world.body
            sys.stderr.write('DBG r%d id%d l%d head=%d body=%s pos=%d\n' % (
                rnd, world.id, world.length, world.head,
                ','.join(str(c) for c in b[:8]), len(world.positions)))
        lines = [action, 'PROTOCOL 3']
        if W['indicator']:
            lines.append('INDICATOR %s r%d l%d u%d' % (kind, rnd, len_after, world.units))
        lines.append('ENDTURN')
        out.write('\n'.join(lines) + '\n')
        out.flush()


if __name__ == '__main__':
    main()

"""STATE/FEATURES: regional resource value (sector grid of REG x REG cells).

Every `reg_period` rounds (and on a dragon's first turn) the known beds
(world.spawn) and remembered fresh pearls are binned into sectors:

  beds[s]     list of bed cells
  pearls[s]   remembered pearls younger than mem_ttl
  ally[s]     allied segments reported there (mass reports + our view), others only
  enemy[s]    enemy segments reported there

Per query from our head (distance d = toroidal distance to the sector's
nearest bed / pearl):
  avail  = pearls + sum over beds of due-by-arrival (1) or partial (linear in
           rounds still to wait after arrival, bed_wait)            [pearls]
  value  = v_bed * min(avail, reg_cap) / (1 + reg_claim * ally_units)
           * exp(-reg_enemy * enemy_segments) * reg_gamma ** d       [value units]
The sector containing our head and sectors closer than reg_min are excluded
(the local target search already covers them). Pure: never writes world state.
"""
import math
import world as w
import mass
import topology
from params import P

REG = 8
SW = SH = 0
BEDS = []
PEARLS = []
LAST = [-99]


def _sector(c):
    return ((c // w.W) // REG) * SW + (c % w.W) // REG


def refresh():
    global SW, SH, BEDS, PEARLS
    if w.RND - LAST[0] < P["reg_period"] and SW:
        return
    LAST[0] = w.RND
    SW = (w.W + REG - 1) // REG
    SH = (w.H + REG - 1) // REG
    n = SW * SH
    BEDS = [[] for _ in range(n)]
    PEARLS = [[] for _ in range(n)]
    for c in w.spawn:
        if w.bed[c] == 2:
            BEDS[_sector(c)].append(c)
    for c, r in w.pearls.items():
        if w.RND - r <= P["mem_ttl"] and w.bed[c] != 2:
            PEARLS[_sector(c)].append(c)


def presence():
    """Allied and enemy segments per sector from mass reports (others only)."""
    n = SW * SH
    ally = [0.0] * n
    enemy = [0.0] * n
    for x, y, aa, ee, dec in mass.ACTIVE:
        s = (int(y) // REG) * SW + int(x) // REG
        if 0 <= s < n:
            ally[s] += aa * dec
            enemy[s] += ee * dec
    for c, eid in w.enemy_heads:
        enemy[_sector(c)] += w.elen.get(eid, 1)
    return ally, enemy


def best(exclude_cell=-1):
    """-> (value, target cell, sector, distance, avail) or None."""
    refresh()
    if not SW:
        return None
    ally, enemy = presence()
    here = _sector(w.HEAD)
    rnd = w.RND
    top = None
    for s in range(SW * SH):
        if s == here:
            continue
        cells = BEDS[s]
        pcs = PEARLS[s]
        if not cells and not pcs:
            continue
        near = -1
        nd = 1 << 30
        for c in cells:
            if P["dead_end_disc"] < 1.0 and topology.dead_end(c):
                continue
            d = w.tdist(w.HEAD, c)
            if d < nd:
                nd = d
                near = c
        for c in pcs:
            d = w.tdist(w.HEAD, c)
            if d < nd:
                nd = d
                near = c
        if near < 0 or nd < P["reg_min"]:
            continue
        avail = float(len(pcs))
        dd = P["dead_end_disc"]
        for c in cells:
            if dd < 1.0 and topology.dead_end(c):
                avail -= 1.0 - dd  # such a bed counts dd, not 1
            sp = w.spawn.get(c, rnd)
            arr = rnd + nd
            if sp <= arr:
                avail += 1.0
            elif P["bed_wait"] > 0:
                avail += max(0.0, 1.0 - (sp - arr) / P["bed_wait"])
        if avail <= 0:
            continue
        units = ally[s] / 4.0  # ~segments per allied dragon (coarse)
        v = P["v_bed"] * min(avail, P["reg_cap"]) / (1.0 + P["reg_claim"] * units)
        v *= math.exp(-P["reg_enemy"] * enemy[s]) * P["reg_gamma"] ** nd
        if top is None or v > top[0]:
            top = (v, near, s, nd, avail)
    return top

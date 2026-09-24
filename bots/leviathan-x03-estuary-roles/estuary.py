"""Estuary's three-job doctrine over the inherited v09 mechanics.

The core module is an explicit interface: observed state plus geometry,
packet primitives and evaluator hooks. No filesystem/network work per turn.
CROWN is the inherited wire code for a gatherer in its protected banking state.
"""
from continuation import survives

GATHER, HUNT, SCOUT, CROWN = range(4)
K_ZONE = 8


class Colony:
    def __init__(self, core):
        self.c = core
        self.p = core.P
        self.known = [0] * (core.ZW * core.ZH)
        self.beds = [0] * len(self.known)
        self.bed_cells = set()
        self.zone_reports = {}
        self.crowns = {}  # id -> cell, length, original observation round
        self.last_role = -100
        self.last_zone = -100
        self.bank = 0.0
        self.coverage = 0.0
        self.danger = False
        self.budget = [0]
        self.base_roles = {r: dict(v) for r, v in core.RP.items()}

    def observed(self, cell, new_cell, new_bed):
        z = self.c.zone_of(cell)
        self.known[z] += bool(new_cell)
        if new_bed and cell not in self.bed_cells:
            self.beds[z] += 1
            self.bed_cells.add(cell)

    def region(self, z):
        known, beds = self.known[z], self.beds[z]
        report = self.zone_reports.get(z)
        if report and self.c.RND - report[2] <= self.p['estuary.zone_ttl']:
            known, beds = max(known, report[0]), max(beds, report[1])
        return known, beds

    def progress(self):
        return max(0.0, min(1.0, (self.c.RND - self.p['estuary.bank_start']) /
                           max(1, self.p['estuary.bank_full'] - self.p['estuary.bank_start'])))

    def near_enemy(self, cell):
        c = self.c
        radius = self.p['estuary.feed_radius']
        return any(c.tdist(cell, p) <= radius for p, _ in c.enemy_heads) or any(
            c.RND - rnd <= 6 and c.tdist(cell, p) <= radius
            for p, rnd, ln in c.enemies.values())

    def mix(self):
        c = self.c
        scout = self.p['estuary.scout_share'] * max(0.0, 1.0 - self.coverage)
        if c.NC <= 625 or c.RND >= self.p['estuary.scout_until'] or \
                self.coverage >= self.p['estuary.scout_retire']:
            scout = 0.0
        hunter = self.p['estuary.hunter_share'] + (0.15 if self.danger else 0)
        return (max(0.0, 1.0 - scout - hunter), hunter, scout)

    def choose_role(self, child=False):
        c = self.c
        mix = self.mix()
        counts = [0, 0, 0]
        for aid, (cell, ln, role, rnd) in c.allies.items():
            if c.RND - rnd <= 12 and role < 3 and aid != c.MY_ID:
                counts[role] += 1
        if child and c.ROLE < 3:
            counts[c.ROLE] += 1
        total = sum(counts) + 1
        # Deterministic salt prevents identical unseen colonies making every
        # assignment identical; observed deficits still dominate.
        return max((r for r in range(3) if mix[r] > 0), key=lambda r:
                   mix[r] * total - counts[r] + ((c.MY_ID * 17 + c.RND + r * 13) % 19) / 190.0)

    def begin(self):
        c = self.c
        self.bank = self.progress()
        self.budget[0] = self.p['estuary.nodes']
        self.coverage = min(1.0, sum(self.region(z)[0] for z in range(len(self.known))) / float(c.NC))
        self.danger = self.near_enemy(c.HEAD)
        c.FEED[0] = -1
        if self.p['estuary.roles']:
            retire = c.ROLE == SCOUT and self.mix()[SCOUT] == 0
            if c.ROLE != CROWN and (retire or c.RND - self.last_role >= self.p['estuary.role_period']):
                c.ROLE = self.choose_role()
                self.last_role = c.RND
            c.RP[SCOUT] = dict(self.base_roles[SCOUT])
            c.RP[SCOUT]['w_enemy'] = 0.0
            for name in ('w_pearl', 'w_spawn'):
                c.RP[SCOUT][name] *= self.p['estuary.scout_food']
        self.elect()
        if c.ROLE == CROWN and c.RND % 2 == 0:
            c.relay_q.insert(0, self.crown_packet(c.P['beacon_ttl']))
        if self.p['estuary.regions'] and c.ROLE == SCOUT and \
                c.RND - self.last_zone >= self.p['estuary.zone_period']:
            z = c.zone_of(c.HEAD)
            pl = (2 << 50) | (z << 42) | (min(127, self.known[z]) << 35) | \
                 (min(127, self.beds[z]) << 28) | (c.RND & 511)
            c.relay_q.insert(0, c.pack(K_ZONE, pl))
            self.last_zone = c.RND
        if self.p['estuary.indicators']:
            c.emit('INDICATOR estuary role=%s bank=%.2f units=%d' %
                   (c.ROLE_NAMES[c.ROLE], self.bank, c.UNITS))

    def elect(self):
        c = self.c
        if c.RND < self.p['estuary.bank_start']:
            return
        fresh = self.p['estuary.crown_fresh']
        known = {i: v for i, v in self.crowns.items() if 0 <= c.RND - v[2] <= fresh and i != c.MY_ID}
        for i, (cell, ln, role, rnd) in c.allies.items():
            if role == CROWN and c.RND - rnd <= min(fresh, 6):
                known[i] = (cell, ln, rnd)
        best = max(known, key=lambda i: (known[i][1], -i)) if known else None
        if c.ROLE == CROWN:
            if best is not None and (known[best][1] >= c.LEN + c.P['crown_demote'] or
                                    (known[best][1] == c.LEN and best < c.MY_ID)):
                c.ROLE = GATHER
            return
        minimum = 4 if self.bank >= 1 else self.p['estuary.bank_min']
        if c.LEN < minimum:
            return
        if best is not None and known[best][1] + c.P['crown_demote'] > c.LEN:
            return
        candidates = [(c.LEN, -c.MY_ID)] + [(ln, -aid) for aid, (cell, ln, role, rnd) in c.allies.items()
                                          if c.RND - rnd <= 6]
        if (c.LEN, -c.MY_ID) == max(candidates):
            c.ROLE = CROWN

    def population_target(self):
        c = self.c
        maximum = self.p['estuary.compact_units'] if c.NC <= 625 else self.p['estuary.open_units']
        # Sparse observed food lowers the target only after enough information;
        # early ignorance must not masquerade as a low-resource map.
        known_beds = sum(self.region(z)[1] for z in range(len(self.beds)))
        if self.coverage > 0.5:
            maximum = min(maximum, max(maximum * 0.65, known_beds * 0.8))
        target = maximum * (1 - self.bank * (1 - self.p['estuary.late_units']))
        reserve = self.p['estuary.guard_reserve'] if self.danger else self.p['estuary.feed_reserve']
        return min(c.UNIT_LIMIT, max(reserve, int(target)))

    def split_allowed(self):
        c = self.c
        if c.ROLE == CROWN or c.RND >= 490:
            return False
        return self.bank < 1.0 or (c.ROLE == HUNT and c.UNITS < self.population_target())

    def split_multiplier(self):
        floor = 0.5 if self.c.ROLE == HUNT else 0.05
        return self.p['estuary.split_gain'] * max(floor, 1.0 - self.bank)

    def region_reward(self, cell):
        if not self.p['estuary.regions'] or self.c.ROLE not in (GATHER, CROWN):
            return 0.0
        known, beds = self.region(self.c.zone_of(cell))
        return self.p['estuary.density'] * beds / max(8, known) / (1 + self.c.zone_danger(cell))

    def waypoint_reward(self, cell):
        c = self.c
        value = self.region_reward(cell)
        if not self.p['estuary.regions']:
            return value
        z = c.zone_of(cell)
        known, beds = self.region(z)
        if c.ROLE == SCOUT:
            value -= c.RP[SCOUT]['w_frontier'] * known / 64.0
        heads = sum(c.zone_of(p) == z and c.RND - rnd <= 8 for p, ln, role, rnd in c.allies.values())
        return value - self.p['estuary.crowd'] * heads

    def bed_cost(self, body):
        c = self.c
        if not self.p['estuary.regions']:
            return 0.0
        return self.p['estuary.bed_block'] * sum(c.spawn_at.get(p) == c.RND + 1 for p in body)

    def continuation(self, body, removed=(), extra=(), depth=None):
        c = self.c
        if not self.p['estuary.safety']:
            return None
        # A long newborn can see only part of itself. Do not claim a complete
        # geometry proof from that partial body reconstruction.
        if not body:
            return None
        def neighbors(cell):
            return tuple(-2 if n == -1 and c.ek[c.ekey(cell, d)] == 3 else n
                         for d, n in enumerate(c.dest(cell)))
        pearls = {p for p in c.pearls if c.seen[p] == c.RND + 1} - set(removed)
        return survives(body, neighbors, set(c.occ) | set(extra), pearls,
                        self.p['estuary.depth'] if depth is None else depth, self.budget)

    def move_survives(self, path, body):
        c = self.c
        if not self.p['estuary.safety'] or (c.ROLE != CROWN and c.LEN < self.p['estuary.long_min']):
            return None
        if len(c.body_list()) < c.LEN:
            return None
        removed = []; cell = c.HEAD
        for d in path:
            cell = c.dest(cell)[d]; removed.append(cell)
        return self.continuation(body, removed)

    def child_survives(self, n):
        c = self.c
        body = c.body_list()
        if len(body) < c.LEN:
            return None
        return self.continuation(list(reversed(body[:n])), extra=body[n:],
                                 depth=self.p['estuary.depth'] if n >= self.p['estuary.long_min'] else 2)

    def route_near(self, start, goals, distance):
        c = self.c
        frontier = {start}; seen = set(frontier)
        for _ in range(distance + 1):
            if frontier & goals:
                return True
            frontier = {p for cell in frontier for p in c.dest(cell)
                        if p >= 0 and p not in seen and p not in c.occ}
            seen.update(frontier)
        return False

    def feed(self):
        c = self.c
        if c.ROLE in (HUNT, CROWN) or c.RND < self.p['estuary.feed_start'] or c.LEN > c.P['feed_max_len']:
            return False
        if c.UNITS <= self.p['estuary.feed_reserve'] or (c.RND + c.MY_ID) % self.p['estuary.feed_period']:
            return False
        choices = [(ln, -i, cell) for i, (cell, ln, rnd) in self.crowns.items()
                   if 0 <= c.RND - rnd <= 3 and ln >= c.LEN + self.p['estuary.feed_gap']]
        choices += [(ln, -i, cell) for i, (cell, ln, role, rnd) in c.allies.items()
                    if role == CROWN and c.RND - rnd <= 3 and ln >= c.LEN + self.p['estuary.feed_gap']]
        if not choices:
            return False
        ln, neg_id, old_cell = max(choices)
        ident = -neg_id
        # A beacon can guide approach, but suicide requires seeing this head.
        visible = next((cell for cell, o in c.occ.items() if o[0] == ident and o[1] and o[2]), None)
        cell = old_cell if visible is None else visible
        if self.near_enemy(cell) or self.danger:
            return False
        if c.tdist(c.HEAD, cell) <= c.P['feed_range']:
            c.FEED[0] = cell
        if visible is None or c.UNITS <= self.p['estuary.feed_reserve']:
            return False
        drops = set(c.body_list()[::-1][::2])
        if not self.route_near(cell, drops, c.P['feed_dist']):
            return False
        # Exact unit count is refreshed for each acting dragon. ID staggering
        # reduces simultaneous donors; the reserve is still enforced per turn.
        c.emit('INDICATOR estuary feed recipient=%d len=%d' % (ident, ln))
        return True  # no MOVE/SPLIT: explicit, attributable default death

    def self_packet(self):
        c = self.c
        return c.pack(c.K_SELF, (c.MY_ID & 65535) << 36 | (c.HEAD & 4095) << 24 |
                      min(c.LEN, 511) << 15 | c.ROLE << 13 | min(c.UNITS, 127) << 6 | c.MOVED_DIR << 4)

    def enemy_packet(self, cell, ln, ident, ttl):
        return self.c.pack(self.c.K_ENEMY, (ttl & 3) << 50 | (ident & 65535) << 34 |
                           (cell & 4095) << 22 | min(ln, 511) << 13 | (self.c.RND & 511))

    def crown_packet(self, ttl):
        c = self.c
        return c.pack(c.K_CROWN, (ttl & 3) << 50 | (c.MY_ID & 65535) << 34 |
                      (c.HEAD & 4095) << 22 | min(c.LEN, 511) << 13 | (c.RND & 511))

    def hear(self, kind, pl):
        c = self.c
        if kind == c.K_SELF:
            ident, cell = (pl >> 36) & 65535, (pl >> 24) & 4095
            if ident != c.MY_ID and cell < c.NC:
                c.allies[ident] = (cell, (pl >> 15) & 511, (pl >> 13) & 3, c.RND)
                c.ally_face[ident] = (pl >> 4) & 3
            return True
        if kind in (c.K_ENEMY, c.K_CROWN):
            ident, cell, ln, rnd = (pl >> 34) & 65535, (pl >> 22) & 4095, (pl >> 13) & 511, pl & 511
            limit = self.p['estuary.crown_fresh'] if kind == c.K_CROWN else 8
            if cell < c.NC and 0 <= c.RND - rnd <= limit:
                if kind == c.K_CROWN:
                    old = self.crowns.get(ident)
                    if old is None or rnd > old[2]:
                        self.crowns[ident] = (cell, ln, rnd)
                else:
                    old = c.enemies.get(ident)
                    if old is None or rnd > old[1]:
                        c.enemies[ident] = (cell, rnd, ln)
                        c.heat_zone(cell, 1.0)
                c.relay(kind, pl, (pl >> 50) & 3)
            return True
        if kind == K_ZONE:
            if self.p['estuary.regions']:
                z, known, beds, rnd = (pl >> 42) & 255, (pl >> 35) & 127, (pl >> 28) & 127, pl & 511
                if z < len(self.known) and 0 <= c.RND - rnd <= self.p['estuary.zone_ttl'] and beds <= known <= 64:
                    old = self.zone_reports.get(z)
                    if old is None or rnd > old[2]:
                        self.zone_reports[z] = (known, beds, rnd)
                    c.relay(kind, pl, (pl >> 50) & 3)
            return True
        return False

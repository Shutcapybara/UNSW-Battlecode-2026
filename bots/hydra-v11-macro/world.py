"""World model for hydra-v11-macro: terrain memory, pearls, beds, occupancy.

Base: leviathan-v07-local-cache; borrowed: canonical edge keys, portal
pairing with a graph cache invalidated on new edges, and chain-based body
reconstruction. Everything else follows the engine sources
(unswbc/engine/src/{actions,pearls,helpers}.cc), read 2026-09-25:

  - a step into kelp dies (HitWall); into any body cell of the moving
    dragon dies (HitSelf, checked before the tail vacates); into another
    dragon's body kills only the mover; into a head kills both;
  - a pearl on the entered tile grows the dragon (tail does not vacate);
  - sprint steps after the first each pay one segment, and a dragon of
    length <= 2 that must pay dies;
  - a bed tile with countdown k (shown post-tick) attempts its spawn at
    the start of round r + k, then redraws its gap; mirror tiles share
    the countdown;
  - a dead dragon leaves a pearl on every second body segment.

Canonical edge keys: k < n is the north edge of cell k; k >= n is the
west edge of cell k - n. Cells are y * w + x on the wrapping board.
"""

DIRS = 'NESW'


class World:
    __slots__ = ('w', 'h', 'n', 'id', 'team', 'edges', 'portals', 'graph',
                 'seen', 'pearls', 'pearls_now', 'beds', 'visits', 'corpses',
                 'doom', 'round', 'head', 'length', 'units', 'facing',
                 'occupied', 'enemy_heads', 'ally_heads', 'enemy_len',
                 'ally_len', 'positions', 'body', 'prune', 'limit')

    def __init__(self, wid, hei, ident, team):
        self.w = wid
        self.h = hei
        self.n = wid * hei
        self.id = ident
        self.team = team
        self.edges = {}         # canonical key -> '.' | 'w' | portal id
        self.portals = {}       # portal id -> [key, key]
        self.graph = {}         # cell -> tuple of 4 destination cells (-1 blocked/unknown)
        self.seen = {}          # cell -> last round seen
        self.pearls = {}        # cell -> round last seen with a pearl
        self.pearls_now = set()
        self.beds = {}          # cell -> round of next spawn attempt
        self.visits = {}        # cell -> head visit count
        self.corpses = {}       # cell -> last round a body segment stood here
        self.doom = {}          # cell -> round flagged trap-ish (flood fill)
        self.round = 0
        self.head = 0
        self.length = 3
        self.units = 1
        self.facing = 0
        self.occupied = {}      # cell -> dragon id (visible this turn)
        self.enemy_heads = {}   # id -> cell
        self.ally_heads = {}    # id -> cell
        self.enemy_len = {}     # id -> [longest visible count, round seen]
        self.ally_len = {}      # id -> [longest visible count, round seen]
        self.positions = []     # my head cells, oldest first
        self.body = []          # my body, head first (exact by construction)
        self.prune = 16
        self.limit = 64

    # -- terrain ---------------------------------------------------------

    def inval_edge(self, k):
        g = self.graph
        n, w = self.n, self.w
        if k < n:
            g.pop(k, None)
            c2 = k + w
            g.pop(c2 - n if c2 >= n else c2, None)
        else:
            j = k - n
            g.pop(j, None)
            x = j % w
            g.pop(j + 1 - w if x + 1 >= w else j + 1, None)

    def learn(self, k, token):
        if self.edges.get(k) == token:
            return
        self.edges[k] = token
        self.inval_edge(k)
        if token != '.' and token != 'w':
            ends = self.portals.setdefault(token, [])
            if k not in ends:
                ends.append(k)
                if len(ends) == 2:
                    self.inval_edge(ends[0])
                    self.inval_edge(ends[1])

    def dest(self, c):
        """Destination cell for each of NESW, -1 when blocked or unknown.
        Unknown edges are blocked: one wasted step beats a wall death."""
        got = self.graph.get(c)
        if got is not None:
            return got
        w, n = self.w, self.n
        x = c % w
        edges = self.edges
        portals = self.portals
        out = []
        for d in range(4):
            if d == 0:
                k = c
                nb = c - w + n if c < w else c - w
            elif d == 2:
                nb = c + w - n if c >= n - w else c + w
                k = nb
            elif d == 3:
                k = n + c
                nb = c - 1 + w if x == 0 else c - 1
            else:
                nb = c + 1 - w if x + 1 >= w else c + 1
                k = n + nb
            t = edges.get(k)
            if t == 'w':
                out.append(-1)
            elif t is None or t == '.':
                out.append(nb)
            else:
                ends = portals.get(t)
                if ends is not None and len(ends) == 2:
                    pk = ends[1] if ends[0] == k else ends[0]
                    if pk < n:
                        # horizontal partner (north edge of cell pk):
                        # heading N exits north of it, heading S onto it
                        out.append((pk - w + n if pk < w else pk - w) if d == 0 else pk)
                    else:
                        # vertical partner (west edge of cell pk-n):
                        # heading E exits onto it, heading W west of it
                        j = pk - n
                        out.append(j if d == 1 else (j - 1 + w if j % w == 0 else j - 1))
                else:
                    out.append(-1)  # half-known portal: never step through blind
        out = tuple(out)
        self.graph[c] = out
        return out

    # -- observation -----------------------------------------------------

    def observe(self, rnd, tiles, parts, horiz, vert, facing, length, units):
        self.round = rnd
        w, n = self.w, self.n
        self.units = units
        self.facing = facing
        self.length = length

        head = int(tiles[24][1]) * w + int(tiles[24][0])
        self.head = head
        self.visits[head] = self.visits.get(head, 0) + 1

        seen = self.seen
        pearls = self.pearls
        pearls_now = set()
        beds = self.beds
        for row in tiles:
            c = int(row[1]) * w + int(row[0])
            seen[c] = rnd
            if row[2] == '1':
                pearls_now.add(c)
                pearls[c] = rnd
            elif c in pearls:
                del pearls[c]
            pit = int(row[3])
            if pit >= 0:
                beds[c] = rnd + pit
        self.pearls_now = pearls_now

        hx, hy = head % w, head // w
        learn = self.learn
        hh = self.h
        for r in range(8):
            y = hy - 3 + r
            if y < 0:
                y += hh
            elif y >= hh:
                y -= hh
            base = y * w
            row = horiz[r]
            for cix in range(7):
                x = hx - 3 + cix
                if x < 0:
                    x += w
                elif x >= w:
                    x -= w
                learn(base + x, row[cix])
        for r in range(7):
            y = hy - 3 + r
            if y < 0:
                y += hh
            elif y >= hh:
                y -= hh
            base = y * w
            row = vert[r]
            for cix in range(8):
                x = hx - 3 + cix
                if x < 0:
                    x += w
                elif x >= w:
                    x -= w
                learn(n + base + x, row[cix])

        occupied = {}
        enemy_heads = {}
        ally_heads = {}
        segs = {}
        corpses = self.corpses
        for row in parts:
            ident = int(row[1])
            c = int(row[3]) * w + int(row[2])
            occupied[c] = ident
            corpses[c] = rnd
            cells = segs.get(ident)
            if cells is None:
                segs[ident] = [c, row[0], row[4], row[5]]
            else:
                cells.append(c)
        self.occupied = occupied
        for ident, info in segs.items():
            nvis = len(info) - 4
            if info[3] == '1':  # the first-listed part of a dragon is its head
                if info[1] == self.team:
                    if ident != self.id:
                        ally_heads[ident] = info[0]
                        rec = self.ally_len.get(ident)
                        if rec is None or nvis >= rec[0]:
                            self.ally_len[ident] = [nvis, rnd]
                        else:
                            rec[1] = rnd
                else:
                    enemy_heads[ident] = info[0]
                    rec = self.enemy_len.get(ident)
                    if rec is None or nvis >= rec[0]:
                        self.enemy_len[ident] = [nvis, rnd]
                    else:
                        rec[1] = rnd
        self.enemy_heads = enemy_heads
        self.ally_heads = ally_heads

        self.reconcile(segs.get(self.id))

    def reconcile(self, mine):
        """Keep `body` exact: every visible cell of mine must sit on it."""
        if mine is None:
            return
        head_cell = mine[0]
        body = self.body
        if body and head_cell == self.head:
            bset = set(body)
            if set(mine[4:]) <= bset:
                return
        length = self.length
        chain = [self.head]
        remaining = set(mine[4:])
        cur = self.head
        while len(chain) < length and remaining:
            nxt = None
            for m in remaining:
                if dest_to(self, m, cur) >= 0:
                    nxt = m
                    break
            if nxt is None:
                break
            chain.append(nxt)
            remaining.discard(nxt)
            cur = nxt
        if len(chain) < length:
            self.extend_chain(chain, length)
        self.adopt_chain(chain)

    def extend_chain(self, chain, length):
        """Grow a head-first chain tail-ward, straight and wrapping."""
        while len(chain) < length:
            prev = chain[-2] if len(chain) > 1 else None
            chain.append(cont(self, prev, chain[-1]))

    def adopt_chain(self, chain):
        """Make `chain` (head-first) the body and rebuild position history."""
        pos = chain[::-1]  # oldest first
        older = []
        cur = pos[0]
        prev = pos[1] if len(pos) > 1 else None
        while len(pos) + len(older) < self.length + 4:
            nxt = cont(self, prev, cur)
            older.append(nxt)
            prev, cur = cur, nxt
        older.reverse()
        self.positions = older + pos
        self.body = chain

    def periodic(self, rnd):
        if rnd < self.prune:
            return
        self.prune = rnd + 32
        r = self.round
        self.pearls = {c: t for c, t in self.pearls.items() if r - t < 40}
        beds = self.beds
        for c in [c for c, t in beds.items() if t <= r]:
            beds[c] = r + 14  # prediction expired unseen: re-arm on the mean gap
        self.corpses = {c: t for c, t in self.corpses.items() if r - t < 6}
        self.doom = {c: t for c, t in self.doom.items() if r - t < 200}
        if len(self.enemy_len) > 24:
            self.enemy_len = {i: v for i, v in self.enemy_len.items() if i in self.enemy_heads}

    def commit_move(self, cells, new_length):
        """Record the head cells visited this turn and the resulting length."""
        pos = self.positions
        pos.extend(cells)
        if len(pos) > 96:
            del pos[:-96]
        self.length = new_length
        self.body = self.body_cells()

    def commit_split(self, new_length):
        pos = self.positions
        self.length = new_length
        self.body = self.body_cells()

    def body_cells(self):
        """Body, head first, from the position history (exact when long enough)."""
        length = self.length
        pos = self.positions
        if len(pos) >= length:
            return pos[-length:][::-1]
        older = []
        cur = pos[0]
        prev = pos[1] if len(pos) > 1 else None
        while len(pos) + len(older) < length:
            nxt = cont(self, prev, cur)
            older.append(nxt)
            prev, cur = cur, nxt
        older.reverse()
        return older + pos


def dest_to(world, frm, to):
    """Direction index that steps from `frm` onto `to`, or -1."""
    dd = world.dest(frm)
    for d in range(4):
        if dd[d] == to:
            return d
    return -1


def est_len(recs, ident, default, rnd):
    """Best estimate of a dragon's length now: last seen count, shrinking by
    one segment per 8 rounds unseen (so dead dragons fade out of elections)."""
    rec = recs.get(ident)
    if rec is None:
        return default
    return max(2, rec[0] - (rnd - rec[1]) // 8)


def cont(world, prev, cur):
    """The cell continuing the step prev -> cur one further, wrapped."""
    w, n, hh = world.w, world.n, world.h
    if prev is None:
        d = world.dest(cur)[(world.facing + 2) % 4]
        return d if d >= 0 else (cur + w) % n
    dx = cur % w - prev % w
    dy = cur // w - prev // w
    if dx > 1:
        dx = -1
    elif dx < -1:
        dx = 1
    if dy > 1:
        dy = -1
    elif dy < -1:
        dy = 1
    if dx:
        x = cur % w
        nx = x + dx
        if nx < 0:
            nx += w
        elif nx >= w:
            nx -= w
        return cur - x + nx
    y = cur // w
    ny = y + dy
    if ny < 0:
        ny += hh
    elif ny >= hh:
        ny -= hh
    return ny * w + cur % w

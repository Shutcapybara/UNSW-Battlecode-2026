"""Legal decision features computed ONLY from the engine's text protocol.

The same class runs (a) offline on round blocks rebuilt from replays by
roundblock.build_block (validated byte-exact against tapped bot input) and
(b) online inside a bot on its real stdin, so offline training features and
deployed features share one code path.

Per process (dragon) state: init block + own history.  Nothing is shared
between dragons.  v4 feature set.
"""
import collections

DIRS = ('N', 'E', 'S', 'W')
DXY = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
REL = ('F', 'R', 'B', 'L')


def rel_to_abs(facing, rel):
    return DIRS[(DIRS.index(facing) + REL.index(rel)) % 4]


def abs_to_rel(facing, d):
    return REL[(DIRS.index(d) - DIRS.index(facing)) % 4]


def ego(facing, dx, dy):
    if facing == 'N':
        return -dy, dx
    if facing == 'S':
        return dy, -dx
    if facing == 'E':
        return dx, dy
    return -dx, -dy


def parse_block(lines, i=0):
    """Parse one round block starting at lines[i]. Returns (dict, next_index)."""
    def kv(k):
        nonlocal i
        p = lines[i].split()
        assert p[0] == k, (k, lines[i])
        i += 1
        return p[1:]
    blk = {}
    blk['round'] = int(kv('ROUND')[0])
    blk['dir'] = kv('DIR')[0]
    blk['length'] = int(kv('LENGTH')[0])
    blk['units'] = int(kv('UNIT_COUNT')[0])
    n = int(kv('NUM_MSGS')[0])
    blk['msgs'] = [int(lines[i + k]) for k in range(n)]
    i += n
    blk['echoes'] = None
    if lines[i].startswith('ECHOES'):
        blk['echoes'] = [int(x) for x in lines[i].split()[1:]]
        i += 1
    tiles = []
    for k in range(49):
        x, y, p, cd = map(int, lines[i + k].split())
        tiles.append((x, y, p, cd))
    i += 49
    nb = int(kv('DRAGON_BODIES')[0])
    bodies = []
    for k in range(nb):
        t, did, x, y, f, h = lines[i + k].split()
        bodies.append((t, int(did), int(x), int(y), f, h == '1'))
    i += nb
    H = [lines[i + k].split() for k in range(8)]
    i += 8
    V = [lines[i + k].split() for k in range(7)]
    i += 7
    blk.update(tiles=tiles, bodies=bodies, H=H, V=V)
    return blk, i


class Proc:
    """One dragon process: memory + feature computation."""

    def __init__(self, my_id, team, W, H, unit_limit):
        self.id, self.team, self.W, self.Hh, self.unit_limit = my_id, team, W, H, unit_limit
        self.turns = 0
        self.last_family, self.last_rel, self.last_len = 'none', 'none', None
        self.last_split_turn, self.n_splits, self.last_eat_turn = None, 0, None
        self.visited = collections.Counter()
        self.msgs_total = 0
        self.seen_portals = set()
        self.last_enemy_heads = self.last_pearls_vis = 0
        self.start = None
        self.max_len = 0
        self.bed_next = {}     # abs bed -> predicted round a pearl can appear (seen_round + countdown)
        self.bed_seen = {}     # abs bed -> last round seen
        self.pearl_seen = {}   # abs tile -> last round a pearl was seen there

    # ---------------------------------------------------------------
    def features(self, blk):
        W, H = self.W, self.Hh
        R = blk['round']
        facing = blk['dir']
        L = blk['length']
        tiles = blk['tiles']
        cell = {}          # (r,c) -> abs
        info = {}          # abs -> (pearl, cd)
        for k, (x, y, p, cd) in enumerate(tiles):
            r, c = divmod(k, 7)
            cell[(r, c)] = (x, y)
            info[(x, y)] = (p, cd)
        rc_of = {v: k for k, v in cell.items()}
        head = cell[(3, 3)]
        occ = {}
        for t, did, x, y, f, h in blk['bodies']:
            if did == self.id:
                code = 3 if h else 2
            elif t == self.team:
                code = 5 if h else 4
            else:
                code = 7 if h else 6
            occ[(x, y)] = code
        Hm, Vm = blk['H'], blk['V']

        def edge(r, c, d):
            if d == 'N':
                return Hm[r][c]
            if d == 'S':
                return Hm[r + 1][c]
            if d == 'W':
                return Vm[r][c]
            return Vm[r][c + 1]

        def step(r, c, d):
            """-> ('out'|'kelp'|'portal'|'in', (r2,c2)|None)"""
            e = edge(r, c, d)
            if e == 'w':
                return 'kelp', None
            if e != '.':
                return 'portal', None
            dx, dy = DXY[d]
            r2, c2 = r + dy, c + dx
            if 0 <= r2 < 7 and 0 <= c2 < 7:
                return 'in', (r2, c2)
            return 'out', None

        # memory update from what is visible now
        for (x, y), (p, cd) in info.items():
            if cd >= 0:
                self.bed_next[(x, y)] = R + cd
                self.bed_seen[(x, y)] = R
            if p:
                self.pearl_seen[(x, y)] = R
            elif (x, y) in self.pearl_seen:
                del self.pearl_seen[(x, y)]
        row = dict(round=R, length=L, units=blk['units'], unit_limit=self.unit_limit,
                   units_frac=blk['units'] / self.unit_limit, W=W, H=H, x=head[0], y=head[1],
                   xn=head[0] / W, yn=head[1] / H, facing_abs='NESW'.index(facing))
        row['n_msgs'] = len(blk['msgs'])
        ech = blk['echoes'] or [0] * 5
        for k, nm in enumerate(('kelp', 'ally', 'allyHead', 'enemy', 'enemyHead')):
            row['echo_' + nm] = ech[k]
        # window scan
        cnt = collections.Counter()
        near = dict(pearl=99, enemy_head=99, ally_head=99, enemy_body=99, bed_ready=99)
        min_cd = 999
        bodies_off = []
        for (r, c), t in cell.items():
            dy, dx = r - 3, c - 3
            f, rr = ego(facing, dx, dy)
            code = occ.get(t, 0)
            p, cd = info[t]
            dist = abs(dx) + abs(dy)
            row[f'g_{f}_{rr}_occ'] = code
            row[f'g_{f}_{rr}_pearl'] = p
            row[f'g_{f}_{rr}_cd'] = cd
            if dist:
                cnt['code%d' % code] += 1
                if code >= 4:
                    bodies_off.append(((dx, dy), code))
                if code in (6, 7):
                    near['enemy_body'] = min(near['enemy_body'], dist)
                if code == 7:
                    near['enemy_head'] = min(near['enemy_head'], dist)
                if code == 5:
                    near['ally_head'] = min(near['ally_head'], dist)
            if p:
                cnt['pearl'] += 1
                if dist:
                    near['pearl'] = min(near['pearl'], dist)
                cnt['pearl_front' if f > 0 else ('pearl_back' if f < 0 else 'pearl_side')] += 1
                cnt['pearl_right' if rr > 0 else ('pearl_left' if rr < 0 else 'pearl_mid')] += 1
            if cd >= 0:
                cnt['bed'] += 1
                min_cd = min(min_cd, cd)
                if cd <= 3 and not p:
                    near['bed_ready'] = min(near['bed_ready'], dist)
            if code in (6, 7):
                cnt['enemy_front' if f > 0 else ('enemy_back' if f < 0 else 'enemy_side')] += 1
            if code in (4, 5):
                cnt['ally_front' if f > 0 else ('ally_back' if f < 0 else 'ally_side')] += 1
        kelp = portals = 0
        for row_e in Hm + Vm:
            for e in row_e:
                if e == 'w':
                    kelp += 1
                elif e != '.':
                    portals += 1
                    self.seen_portals.add(e)
        row.update(vis_pearls=cnt['pearl'], vis_beds=cnt['bed'], vis_min_cd=min_cd if min_cd < 999 else -1,
                   vis_enemy_seg=cnt['code6'] + cnt['code7'], vis_enemy_heads=cnt['code7'],
                   vis_ally_seg=cnt['code4'] + cnt['code5'], vis_ally_heads=cnt['code5'], vis_own_seg=cnt['code2'],
                   vis_kelp=kelp, vis_portal=portals, pearl_front=cnt['pearl_front'], pearl_back=cnt['pearl_back'],
                   pearl_left=cnt['pearl_left'], pearl_right=cnt['pearl_right'], enemy_front=cnt['enemy_front'],
                   enemy_back=cnt['enemy_back'], ally_front=cnt['ally_front'], ally_back=cnt['ally_back'])
        for k, v in near.items():
            row['near_' + k] = v

        # BFS inside the window from a cell (portals not traversed)
        def bfs(start):
            seen = {start: 0}
            q = collections.deque([start])
            while q:
                a = q.popleft()
                for d in DIRS:
                    kind, b = step(a[0], a[1], d)
                    if kind != 'in' or b in seen or cell[b] in occ:
                        continue
                    seen[b] = seen[a] + 1
                    q.append(b)
            return seen

        free = 0
        for rel in ('F', 'R', 'L', 'B'):
            ad = rel_to_abs(facing, rel)
            kind, dst = step(3, 3, ad)
            P = 'c' + rel + '_'
            base = dict(block=0, portal=0, pearl=0, cd=-1, eh_adj=0, area=0, pdist=99, pmass=0, pc3=0, bedsoon=0,
                        unvisited=0, allyh2=0, eseg2=0, run=0, mem_bed=99, mem_bed_n=0, mem_pearl=99)
            if kind == 'kelp':
                base['block'] = 1
            elif kind in ('portal', 'out'):
                base.update(block=-1, portal=int(kind == 'portal'), pearl=-1, cd=-2, eh_adj=-1, area=-1,
                            pmass=-1, pc3=-1, bedsoon=-1, unvisited=-1)
                if kind == 'portal':
                    free += 1
            else:
                t = cell[dst]
                code = occ.get(t, 0)
                base['block'] = code
                p, cd = info[t]
                base['pearl'], base['cd'] = p, cd
                eh = 0
                for d2 in DIRS:
                    k2, n2 = step(dst[0], dst[1], d2)
                    if k2 == 'in' and n2 != (3, 3) and occ.get(cell[n2]) == 7:
                        eh += 1
                base['eh_adj'] = eh
                if code == 0:
                    free += 1
                    seen = bfs(dst)
                    base['area'] = len(seen)
                    pm = pc3 = bs = unv = 0
                    pdist = 99
                    for b, dd in seen.items():
                        tb = cell[b]
                        pb, cdb = info[tb]
                        if pb:
                            pdist = min(pdist, dd)
                            pm += 1.0 / (1 + dd)
                            pc3 += dd <= 3
                        elif cdb >= 0 and cdb <= dd + 1:
                            bs += 1
                        if dd <= 3 and tb not in self.visited:
                            unv += 1
                    base.update(pdist=pdist, pmass=pm, pc3=pc3, bedsoon=bs, unvisited=unv)
                    ddx, ddy = DXY[ad]
                    ah = es = 0
                    for (bx, by), kd in bodies_off:
                        if abs(bx - ddx) + abs(by - ddy) <= 2:
                            if kd == 5:
                                ah += 1
                            elif kd >= 6:
                                es += 1
                    base['allyh2'], base['eseg2'] = ah, es
                    run, a = 0, (3, 3)
                    for _ in range(3):
                        k3, n3 = step(a[0], a[1], ad)
                        if k3 != 'in' or cell[n3] in occ:
                            break
                        run += 1
                        a = n3
                    base['run'] = run
            # memory-based long-range pull (wrapped Manhattan, ignores kelp): remembered beds/pearls out of view
            if base['block'] in (0, -1):
                dx0, dy0 = DXY[ad]
                sx, sy = (head[0] + dx0) % W, (head[1] + dy0) % H
                best_b, nb, best_p = 99, 0, 99
                for (bx, by), nxt in self.bed_next.items():
                    if (bx, by) in info:
                        continue
                    dd = min((bx - sx) % W, (sx - bx) % W) + min((by - sy) % H, (sy - by) % H)
                    if dd <= 20 and nxt <= R + dd + 1:
                        nb += 1
                        best_b = min(best_b, dd)
                for (px, py), sr in self.pearl_seen.items():
                    if (px, py) in info or R - sr > 30:
                        continue
                    dd = min((px - sx) % W, (sx - px) % W) + min((py - sy) % H, (sy - py) % H)
                    best_p = min(best_p, dd)
                base.update(mem_bed=best_b, mem_bed_n=nb, mem_pearl=best_p)
            for k, v in base.items():
                row[P + k] = v
        row['free_dirs'] = free
        # own-process memory
        if self.start is None:
            self.start = head
        if self.last_len is not None and L > self.last_len:
            self.last_eat_turn = self.turns
        row.update(mem_age=self.turns, mem_len_delta=(L - self.last_len) if self.last_len is not None else 0,
                   mem_since_split=(self.turns - self.last_split_turn) if self.last_split_turn is not None else 999,
                   mem_n_splits=self.n_splits,
                   mem_since_eat=(self.turns - self.last_eat_turn) if self.last_eat_turn is not None else 999,
                   mem_visited=len(self.visited), mem_revisit=self.visited[head],
                   mem_msgs_total=self.msgs_total, mem_portals_seen=len(self.seen_portals),
                   mem_enemy_heads_prev=self.last_enemy_heads, mem_pearls_prev=self.last_pearls_vis,
                   mem_disp=min((head[0] - self.start[0]) % W, (self.start[0] - head[0]) % W) +
                   min((head[1] - self.start[1]) % H, (self.start[1] - head[1]) % H),
                   mem_max_len=max(self.max_len, L), mem_beds_known=len(self.bed_next),
                   mem_last_family={'none': 0, 'move': 1, 'sprint': 2, 'split': 3, 'suicide': 4}.get(self.last_family, 0),
                   mem_last_rel={'none': 0, 'F': 1, 'R': 2, 'L': 3, 'B': 4}.get(self.last_rel, 0))
        self.visited[head] += 1
        self.msgs_total += len(blk['msgs'])
        self.last_enemy_heads = row['vis_enemy_heads']
        self.last_pearls_vis = row['vis_pearls']
        self.max_len = max(self.max_len, L)
        self.last_len = L
        self.turns += 1
        return row

    def record_action(self, kind, rels=None, split=None):
        """kind: move|split; rels: relative steps; split: child size."""
        if kind == 'move':
            self.last_family = 'move' if len(rels) == 1 else 'sprint'
            self.last_rel = rels[0]
        elif kind == 'split':
            if split == 1:
                self.last_family = 'suicide'
            else:
                self.last_family = 'split'
                self.n_splits += 1
                self.last_split_turn = self.turns - 1

"""Legal pre-action decision rows for one team (policy-learning namespace).

    python3 features.py OUTDIR TEAM_SIDE_JSON replay [replay ...]

TEAM_SIDE_JSON maps game-id -> 'A'|'B' (verified target side).  Each row is
one target-dragon decision built ONLY from what that dragon's round block
contains (7x7 wrapped vision, own length/facing/unit count, delivered sonar
messages, echoes if protocol>=3) plus causal memory of its OWN process
(birth, previous observations/actions).  Analyst-only columns are prefixed
'priv_' and must never enter a deployable model.

Ego frame: facing is 'F'; relative directions F,R,B,L.  Ego grid coords
(f, r): f = steps forward, r = steps right, both in -3..3.
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recon  # noqa: E402

REL = ('F', 'R', 'B', 'L')
DIRS = recon.DIRS  # north east south west (clockwise)


def rel_of(facing, d):
    return REL[(DIRS.index(d) - DIRS.index(facing)) % 4]


def abs_of(facing, rel):
    return DIRS[(DIRS.index(facing) + REL.index(rel)) % 4]


def ego_offset(facing, dx, dy):
    """absolute offset -> (f, r) in ego frame."""
    if facing == 'north':
        return -dy, dx
    if facing == 'south':
        return dy, -dx
    if facing == 'east':
        return dx, dy
    return -dx, -dy  # west


class Memory:
    """Causal per-process memory (never shared between dragons)."""
    __slots__ = ('birth_round', 'initial', 'turns', 'last_family', 'last_rel', 'last_len', 'last_split_turn',
                 'n_splits', 'last_eat_turn', 'visited', 'msgs_total', 'seen_portals', 'last_enemy_heads',
                 'last_pearls_vis', 'start_xy', 'max_len')

    def __init__(self, birth_round, initial):
        self.birth_round, self.initial = birth_round, initial
        self.turns = 0
        self.last_family = 'none'
        self.last_rel = 'none'
        self.last_len = None
        self.last_split_turn = None
        self.n_splits = 0
        self.last_eat_turn = None
        self.visited = collections.Counter()
        self.msgs_total = 0
        self.seen_portals = set()
        self.last_enemy_heads = 0
        self.last_pearls_vis = 0
        self.start_xy = None
        self.max_len = 0


class Extractor:
    def __init__(self, game, side, game_id):
        self.g, self.side, self.gid = game, side, game_id
        self.mem = {}
        self.rows = []
        self.pending = None
        self.round = -1

    # --- window helpers -------------------------------------------------
    def window(self, d):
        g, b = self.g, self.g.board
        hx, hy = d.body[0]
        cells = {}
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                t = b.wrap(hx + dx, hy + dy)
                cells[(dx, dy)] = t
        return cells

    def occupant(self, t, me):
        """code: 0 empty, 2 own body, 3 own head, 4 ally body, 5 ally head, 6 enemy body, 7 enemy head"""
        oid = self.g.occ.get(t)
        if oid is None:
            return 0, None
        o = self.g.dragons[oid]
        head = o.body[0] == t
        if oid == me.id:
            return (3 if head else 2), o
        if o.team == me.team:
            return (5 if head else 4), o
        return (7 if head else 6), o

    def bfs(self, start, me, vis_set, block_codes=(2, 3, 4, 5, 6, 7), limit=24):
        """BFS inside the visible window from start (absolute tile). Returns (area, pearl_dist).
        Kelp blocks; portal edges are not traversed (their far side is outside known geometry)."""
        g = self.g
        nbr, occ, pearls = g.board.nbr, g.occ, g.pearls
        if start is None:
            return 0, 99
        seen = {start: 0}
        q = collections.deque([start])
        pearl_d = 99
        while q:
            t = q.popleft()
            dist = seen[t]
            if pearl_d == 99 and t in pearls:
                pearl_d = dist
            for n, via, has_edge in nbr[t]:
                if has_edge or n in seen or n not in vis_set or n in occ:
                    continue
                seen[n] = dist + 1
                q.append(n)
        self._last_seen = seen
        return len(seen), pearl_d

    # --- observation ---------------------------------------------------
    def observe(self, d):
        g, b = self.g, self.g.board
        m = self.mem.get(d.id)
        if m is None:
            m = self.mem[d.id] = Memory(g.round if d.born >= 0 else -1, d.born < 0)
        head = d.body[0]
        facing = d.facing
        L = len(d.body)
        row = dict(game=self.gid, round=g.round, dragon=d.id, facing_abs=facing,
                   x=head[0], y=head[1], xn=head[0] / b.W, yn=head[1] / b.H, W=b.W, H=b.H,
                   length=L, units=g.unit_count(d.team), unit_limit=b.unit_limit)
        row['units_frac'] = row['units'] / b.unit_limit
        # messages / echoes (protocol-dependent readability recorded, not assumed)
        msgs = d.inbox
        row['n_msgs_all'] = len(msgs)
        row['n_msgs_u32'] = sum(1 for v in msgs if v[0] <= 0xFFFFFFFF)
        for i, k in enumerate(recon.ECHO_ORDER):
            row['echo_' + k] = d.echo[i]
        cells = self.window(d)
        vis = set(cells.values())
        counts = collections.Counter()
        grid = {}
        nearest = {'pearl': 99, 'enemy_head': 99, 'ally_head': 99, 'enemy_body': 99, 'bed_ready': 99}
        min_cd = 999
        seen_ids_enemy, seen_ids_ally = set(), set()
        bodies_off = []
        for (dx, dy), t in cells.items():
            f, r = ego_offset(facing, dx, dy)
            code, o = self.occupant(t, d)
            if code >= 4:
                bodies_off.append(((dx, dy), code))
            pearl = t in g.pearls
            cd = g.countdown.get(t, -1) if t in b.gaps else -1
            dist = abs(dx) + abs(dy)
            if (dx, dy) != (0, 0):
                counts['code%d' % code] += 1
                if code in (6, 7):
                    seen_ids_enemy.add(o.id)
                    nearest['enemy_body'] = min(nearest['enemy_body'], dist)
                if code in (4, 5):
                    seen_ids_ally.add(o.id)
                if code == 7:
                    nearest['enemy_head'] = min(nearest['enemy_head'], dist)
                if code == 5:
                    nearest['ally_head'] = min(nearest['ally_head'], dist)
            if pearl:
                counts['pearl'] += 1
                if (dx, dy) != (0, 0):
                    nearest['pearl'] = min(nearest['pearl'], dist)
                # quadrant of pearls in ego frame
                counts['pearl_front' if f > 0 else ('pearl_back' if f < 0 else 'pearl_side')] += 1
                counts['pearl_right' if r > 0 else ('pearl_left' if r < 0 else 'pearl_mid')] += 1
            if cd >= 0:
                counts['bed'] += 1
                min_cd = min(min_cd, cd)
                if cd <= 3 and not pearl:
                    nearest['bed_ready'] = min(nearest['bed_ready'], dist)
            if code in (6, 7):
                counts['enemy_front' if f > 0 else ('enemy_back' if f < 0 else 'enemy_side')] += 1
            if abs(f) <= 2 and abs(r) <= 2:
                grid['g_%d_%d_occ' % (f, r)] = code
                grid['g_%d_%d_pearl' % (f, r)] = int(pearl)
                grid['g_%d_%d_cd' % (f, r)] = cd
        # edges in view
        n_kelp = n_portal = 0
        pid_count = collections.Counter()
        for (dx, dy), t in cells.items():
            for dd in ('north', 'west', 'south', 'east'):
                e = b.edge(t, dd)
                if e is not None and e[0] == 'p':
                    pid_count[e[1]] += 1
        for (dx, dy), t in cells.items():
            for dd in ('north', 'west'):
                e = b.edge(t, dd)
                if e is None:
                    continue
                if e[0] == 'k':
                    n_kelp += 1
                else:
                    n_portal += 1
                    m.seen_portals.add(e[1])
        row.update(vis_pearls=counts['pearl'], vis_beds=counts['bed'], vis_min_cd=min_cd if min_cd < 999 else -1,
                   vis_enemy_seg=counts['code6'] + counts['code7'], vis_enemy_heads=counts['code7'],
                   vis_ally_seg=counts['code4'] + counts['code5'], vis_ally_heads=counts['code5'],
                   vis_own_seg=counts['code2'], vis_enemy_ids=len(seen_ids_enemy), vis_ally_ids=len(seen_ids_ally),
                   vis_kelp=n_kelp, vis_portal=n_portal,
                   pearl_front=counts['pearl_front'], pearl_back=counts['pearl_back'],
                   pearl_left=counts['pearl_left'], pearl_right=counts['pearl_right'],
                   enemy_front=counts['enemy_front'], enemy_back=counts['enemy_back'])
        for k, v in nearest.items():
            row['near_' + k] = v
        # per-candidate first-step features
        free_dirs = 0
        for rel in ('F', 'R', 'L', 'B'):
            ad = abs_of(facing, rel)
            dest, via = b.step(head, ad)
            p = 'c' + rel + '_'
            if dest is None:
                code = 1  # kelp
                row[p + 'block'] = 1
                row[p + 'portal'] = 0
                row[p + 'pearl'] = 0
                row[p + 'area'] = 0
                row[p + 'pdist'] = 99
                row[p + 'eh_adj'] = 0
                row[p + 'cd'] = -1
                continue
            pe = b.edge(head, ad)
            if dest not in vis or (via and pid_count[pe[1]] < 3):
                # pid_count counts edge sightings from both adjacent tiles (an interior edge is seen twice);
                # a portal is only 'known' when another end with the same id is also in view.
                # portal exit outside the 7x7 window: contents are NOT in the round block
                row[p + 'block'] = -1
                row[p + 'portal'] = 1
                row[p + 'pearl'] = -1
                row[p + 'cd'] = -2
                row[p + 'eh_adj'] = -1
                row[p + 'area'] = -1
                row[p + 'pdist'] = 99
                free_dirs += 1
                continue
            code, o = self.occupant(dest, d)
            row[p + 'block'] = 0 if code == 0 else (code + 0)  # 2/3 own, 4/5 ally, 6/7 enemy
            row[p + 'portal'] = int(via)
            row[p + 'pearl'] = int(dest in g.pearls)
            row[p + 'cd'] = g.countdown.get(dest, -1) if dest in b.gaps else -1
            eh = 0
            if dest in vis:
                for d2 in DIRS:
                    n2, _ = b.step(dest, d2)
                    if n2 is None or n2 == head:
                        continue
                    c2, o2 = self.occupant(n2, d)
                    if c2 == 7:
                        eh += 1
            row[p + 'eh_adj'] = eh
            if code == 0:
                free_dirs += 1
                if via:
                    row[p + 'area'], row[p + 'pdist'] = -1, 99   # beyond known geometry
                else:
                    row[p + 'area'], row[p + 'pdist'] = self.bfs(dest, d, vis)
            else:
                row[p + 'area'], row[p + 'pdist'] = 0, 99
            # v3 richer candidate descriptors (legal: window contents + own memory only)
            if code == 0 and not via:
                seen = self._last_seen
                pm = pc3 = bs = unv = 0
                for t2, dd in seen.items():
                    if t2 in g.pearls:
                        pm += 1.0 / (1 + dd)
                        pc3 += dd <= 3
                    elif t2 in b.gaps:
                        cdv = g.countdown.get(t2, 99)
                        if cdv <= dd + 1:
                            bs += 1
                    if dd <= 3 and t2 not in m.visited:
                        unv += 1
                row[p + 'pmass'], row[p + 'pc3'], row[p + 'bedsoon'], row[p + 'unvisited'] = pm, pc3, bs, unv
            else:
                row[p + 'pmass'] = row[p + 'pc3'] = row[p + 'bedsoon'] = row[p + 'unvisited'] = -1
            ah = eseg = 0
            if code == 0 and dest in vis:
                ddx, ddy = recon.DXY[ad]
                for (bx, by), kind in bodies_off:
                    md = abs(bx - ddx) + abs(by - ddy)
                    if md <= 2:
                        if kind == 5:
                            ah += 1
                        elif kind in (6, 7):
                            eseg += 1
            row[p + 'allyh2'], row[p + 'eseg2'] = ah, eseg
            run = 0
            at = head
            for _ in range(3):
                nx, vv = b.step(at, ad)
                if nx is None or vv or nx not in vis or nx in g.occ:
                    break
                run += 1
                at = nx
            row[p + 'run'] = run
        row['free_dirs'] = free_dirs
        # memory (causal, own process)
        m.visited[head] += 1
        if m.start_xy is None:
            m.start_xy = head
        grew = (m.last_len is not None and L > m.last_len)
        if grew:
            m.last_eat_turn = m.turns
        row.update(mem_age=m.turns, mem_initial=int(m.initial), mem_birth_round=m.birth_round,
                   mem_last_family=m.last_family, mem_last_rel=m.last_rel,
                   mem_len_delta=(L - m.last_len) if m.last_len is not None else 0,
                   mem_since_split=(m.turns - m.last_split_turn) if m.last_split_turn is not None else 999,
                   mem_n_splits=m.n_splits,
                   mem_since_eat=(m.turns - m.last_eat_turn) if m.last_eat_turn is not None else 999,
                   mem_visited=len(m.visited), mem_revisit=m.visited[head] - 1,
                   mem_msgs_total=m.msgs_total, mem_portals_seen=len(m.seen_portals),
                   mem_enemy_heads_prev=m.last_enemy_heads, mem_pearls_prev=m.last_pearls_vis,
                   mem_disp=abs(head[0] - m.start_xy[0]) + abs(head[1] - m.start_xy[1]),
                   mem_max_len=max(m.max_len, L))
        row.update(grid)
        # analyst-only (full state) — separate namespace
        mine = [x for x in g.dragons.values() if x.alive and x.team == d.team]
        theirs = [x for x in g.dragons.values() if x.alive and x.team != d.team]
        row.update(priv_team_total=sum(len(x.body) for x in mine), priv_enemy_total=sum(len(x.body) for x in theirs),
                   priv_enemy_units=len(theirs), priv_is_longest=int(L == max(len(x.body) for x in mine)),
                   priv_rank_len=sum(1 for x in mine if len(x.body) > L), priv_pearls_board=len(g.pearls),
                   priv_msgs_gt32=len(msgs) - row['n_msgs_u32'])
        m.msgs_total += len(msgs)
        m.last_enemy_heads = row['vis_enemy_heads']
        m.last_pearls_vis = row['vis_pearls']
        m.max_len = max(m.max_len, L)
        m.last_len = L
        m.turns += 1
        return row, m

    def cb(self, kind, **k):
        if kind == 'round':
            self.round = k['round']
        elif kind == 'turn':
            d = k['dragon']
            if d.team == self.side:
                self.pending = self.observe(d)
            else:
                self.pending = None
        elif kind == 'action' and self.pending is not None:
            row, m = self.pending
            d, a = k['dragon'], k['action']
            fam = a[0]
            row['y_family'] = fam
            if fam == 'move':
                rels = [rel_of(d.facing, a[1][0])]
                cur = a[1][0]
                for s in a[1][1:]:
                    rels.append(rel_of(cur, s))
                    cur = s
                row['y_first'] = rels[0]
                row['y_nsteps'] = len(rels)
                row['y_seq'] = ''.join(rels)
                row['y_split'] = 0
                m.last_family = 'move' if len(rels) == 1 else 'sprint'
                m.last_rel = rels[0]
            elif fam == 'split':
                row['y_first'] = 'split'
                row['y_nsteps'] = 0
                row['y_seq'] = 'S%d' % a[1]
                row['y_split'] = a[1]
                row['y_split_frac'] = a[1] / row['length']
                m.last_family = 'split'
                m.n_splits += 1
                m.last_split_turn = m.turns - 1
            else:
                row['y_first'] = fam
                row['y_nsteps'] = 0
                row['y_seq'] = fam
                row['y_split'] = 0
                m.last_family = fam
            row['y_tle'] = int(k['tle'])
            self.rows.append(row)
            self.pending = None
        elif kind == 'death' and self.rows and self.rows[-1]['dragon'] == k['dragon'].id \
                and self.rows[-1]['round'] == self.round:
            self.rows[-1]['post_died'] = 1   # outcome annotation (diagnostic only)


def extract(path, side, gid):
    g = recon.Game(path)
    ex = Extractor(g, side, gid)
    g.run(ex.cb)
    return ex.rows, g


if __name__ == '__main__':
    import pandas as pd
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    sides = json.loads(Path(sys.argv[2]).read_text())
    for p in sys.argv[3:]:
        gid = Path(p).stem
        side = sides.get(gid)
        o = outdir / (gid + '.parquet')
        if side is None or o.exists():
            continue
        try:
            rows, g = extract(p, side, int(gid))
            df = pd.DataFrame(rows)
            df['map'] = g.board.name
            tmp = outdir / (gid + '.part')
            df.to_parquet(tmp)
            tmp.replace(o)
            print(gid, len(df), dict(g.checks), flush=True)
        except Exception as e:
            (outdir / (gid + '.error')).write_text(f'{type(e).__name__}: {e}')
            print(gid, 'ERROR', e, flush=True)

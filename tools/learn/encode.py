"""Phase 3 observation encoder (Data lane, kageyama). ENC_VERSION 1.

Contract
- Input: one dragon process's spawn block and the sequence of protocol blocks it received, in order, plus (optionally)
  the actions that same process sent. Nothing else: no replay state, no map file, no future. Legal by construction.
- Output per turn: a flat vector of int32 (no floats, so the C++ twin `learn_encode.hpp` matches bit for bit).
  Layout: 49 cells x N_CH channels (egocentric, rotated so the dragon's facing is up), then N_SC scalars.
  `names()` gives every column name; `SPEC` documents each.
- Map identity is never emitted: no absolute x/y, no W/H, no absolute facing. Memory keeps absolute coordinates
  internally and emits only relative offsets / ages.

Rotation: forward = facing. Window row 0 is 3 cells ahead, column 0 is 3 cells to the left.
Edge channels are relative to the dragon: F (ahead side of the cell), R, B, L.

Usage
    enc = Encoder(spawn)                    # block.Spawn
    x = enc.observe(block)                  # block.Block -> list[int]
    enc.act(kind, rel_steps=None, child=0)  # optional: this process's own action this turn (legal own memory)
"""
from block import VISION, R

ENC_VERSION = 1
DIRS = 'NESW'
DXY = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
RELS = 'FRBL'
UNSEEN = -1          # value of an age / distance feature with no information
BIG = 999

CH = ['kelp_F', 'kelp_R', 'kelp_B', 'kelp_L', 'portal_F', 'portal_R', 'portal_B', 'portal_L',
      'pearl', 'bed', 'pearl_in',
      'own_seg', 'ally_body', 'ally_head', 'enemy_body', 'enemy_head', 'ally_queen', 'enemy_queen',
      'head_fac_F', 'head_fac_R', 'head_fac_B', 'head_fac_L', 'seg_toward_me']
N_CH = len(CH)

SC = ['round', 'rounds_left', 'phase', 'length', 'unit_count', 'unit_limit', 'headroom', 'split_elig',
      'turn_index', 'is_child', 'rounds_since_birth', 'rounds_since_split', 'last_kind', 'last_first_rel', 'last_nsteps',
      'n_msgs', 'n_msgs_nonzero', 'n_msgs_gt32', 'echo_present', 'echo_kelp', 'echo_ally', 'echo_ally_head',
      'echo_enemy', 'echo_enemy_head', 'echo_total',
      'exit_ord', 'exit_portal', 'exit_F', 'exit_R', 'exit_L',
      'n_enemy_heads', 'n_ally_heads', 'n_enemy_parts', 'n_ally_parts', 'n_pearls', 'n_beds',
      'enemy_head_d1', 'enemy_head_min_d', 'ally_head_min_d', 'pearl_min_d', 'enemy_vis_len_max',
      'is_queen', 'ownq_visible', 'ownq_age', 'ownq_f', 'ownq_r', 'ownq_d',
      'enemyq_visible', 'enemyq_age', 'enemyq_f', 'enemyq_r', 'enemyq_d', 'enemyq_vis_parts',
      'home_known', 'home_f', 'home_r', 'home_d', 'mirror_xy_f', 'mirror_xy_r', 'mirror_xy_d',
      'mirror_y_f', 'mirror_y_r', 'mirror_y_d', 'len_delta', 'units_delta']
N_SC = len(SC)

SPEC = {
    'pearl_in': 'bed countdown clipped to [0,255]; 0 off-bed (see bed); -1 never emitted',
    'own_seg': 'own body: segment index from the head +1 (head = 1), 0 elsewhere',
    'seg_toward_me': 'for any visible non-head part: 1 if its facing points at a cell adjacent to my head (a body the '
                     'next step of which comes my way), else 0',
    'phase': 'round bucket: 0 <25, 1 <100, 2 <250, 3 <400, 4 >=400',
    'last_kind': 'own previous action: 0 none/unknown, 1 move, 2 split, 3 invalid/suicide',
    'last_first_rel': '0..3 = F,R,B,L of the previous move relative to the facing then; -1 otherwise',
    'ownq_*/enemyq_*': 'queen = id 0 (team A) / 1 (team B). age = rounds since its head (or any part) was last seen '
                       'by this process, -1 never; f/r = last-seen head offset in the current rotated frame (torus-'
                       'minimal), d = |f|+|r|; 999 when unknown',
    'home_*': 'own spawn cell (only for a process present at round 0; children 0/999)',
    'mirror_xy_* / mirror_y_*': 'the enemy home under point symmetry / reflection in y, from own spawn (round-0 '
                                'processes only). The bot cannot read the map symmetry, so both are emitted',
    'len_delta / units_delta': 'change since this process\'s previous block (eat / loss signal)',
}


def _tor(d, n):
    d %= n
    return d - n if d > n // 2 else d


class Encoder:
    def __init__(self, spawn):
        self.id, self.team, self.W, self.H, self.limit = spawn.id, spawn.team, spawn.W, spawn.H, spawn.unit_limit
        self.my_queen = 0 if self.team == 'A' else 1
        self.their_queen = 1 - self.my_queen
        self.turn = 0
        self.first_round = None
        self.home = None
        self.last = dict(kind=0, first=-1, nsteps=0)
        self.last_split_round = None
        self.prev_len = None
        self.prev_units = None
        self.q_seen = {0: None, 1: None}     # queen id -> (round, abs x, abs y)

    # own actions (legal: the process knows what it sent)
    def act(self, kind, rel_steps=None, child=0, rnd=None):
        k = {'move': 1, 'split': 2, 'suicide': 3, 'invalid': 3}.get(kind, 0)
        self.last = dict(kind=k, first=RELS.index(rel_steps[0]) if (k == 1 and rel_steps) else -1,
                         nsteps=len(rel_steps) if (k == 1 and rel_steps) else 0)
        if k == 2:
            self.last_split_round = rnd if rnd is not None else self.cur_round

    def _rot(self, dx, dy, fac):
        fx, fy = DXY[fac]
        rx, ry = -fy, fx
        return dx * fx + dy * fy, dx * rx + dy * ry      # (forward, right)

    def _rel_dir(self, absd, fac):
        return (DIRS.index(absd) - DIRS.index(fac)) % 4  # 0 F 1 R 2 B 3 L

    def observe(self, b):
        fac = b.dir
        self.cur_round = b.round
        hx, hy = b.tiles[24][0], b.tiles[24][1]
        if self.first_round is None:
            self.first_round = b.round
            if b.round == 0:
                self.home = (hx, hy)
        grid = [[0] * N_CH for _ in range(49)]

        def idx(dx, dy):                                 # absolute offset -> rotated cell index
            f, r = self._rot(dx, dy, fac)
            return (3 - f) * 7 + (3 + r)

        # tiles
        n_pearls = n_beds = 0
        pearl_min = BIG
        for k, (x, y, hp, pin) in enumerate(b.tiles):
            dx, dy = k % 7 - 3, k // 7 - 3
            g = grid[idx(dx, dy)]
            if hp:
                g[8] = 1; n_pearls += 1
                pearl_min = min(pearl_min, abs(dx) + abs(dy))
            if pin >= 0:
                g[9] = 1; n_beds += 1
                g[10] = min(pin, 255)
        # edges: hedges[r][c] is the north edge of window cell (c, r); vedges[r][c] the west edge of (c, r)
        def put_edge(c, r, absd, tok):
            if not (0 <= c < 7 and 0 <= r < 7) or tok == '.':
                return
            rd = self._rel_dir(absd, fac)
            grid[idx(c - 3, r - 3)][(0 if tok == 'w' else 4) + rd] = 1
        for r in range(8):
            for c in range(7):
                t = b.hedges[r][c]
                put_edge(c, r, 'N', t); put_edge(c, r - 1, 'S', t)
        for r in range(7):
            for c in range(8):
                t = b.vedges[r][c]
                put_edge(c, r, 'W', t); put_edge(c - 1, r, 'E', t)
        # parts
        pos = {(x, y): k for k, (x, y, _, _) in enumerate(b.tiles)}
        own_k = 0
        n_eh = n_ah = n_ep = n_ap = 0
        eh_min = ah_min = BIG
        eh_d1 = 0
        vis_len, enemy_of = {}, {}
        q_vis = {0: False, 1: False}
        q_parts = {0: 0, 1: 0}
        q_pos = {}
        adj_me = {((hx + ex) % self.W, (hy + ey) % self.H) for ex, ey in DXY.values()}
        for t, i, x, y, f, h in b.parts:
            k = pos[(x, y)]
            dx, dy = k % 7 - 3, k // 7 - 3
            g = grid[idx(dx, dy)]
            d = abs(dx) + abs(dy)
            if i == self.id:
                own_k += 1
                g[11] = own_k
                continue
            ally = t == self.team
            vis_len[i] = vis_len.get(i, 0) + 1
            enemy_of[i] = not ally
            if i in (0, 1):
                g[16 if (i == self.my_queen) else 17] = 1
                q_parts[i] += 1
                if h:
                    q_pos[i] = (x, y)
                elif i not in q_pos:
                    q_pos[i] = (x, y)
                q_vis[i] = True
            if h:
                g[13 if ally else 15] = 1
                g[18 + self._rel_dir(f, fac)] = 1
                if ally:
                    n_ah += 1; ah_min = min(ah_min, d)
                else:
                    n_eh += 1; eh_min = min(eh_min, d)
                    if d == 1:
                        eh_d1 += 1
            else:
                g[12 if ally else 14] = 1
                if ally:
                    n_ap += 1
                else:
                    n_ep += 1
                ddx, ddy = DXY[f]
                if ((x + ddx) % self.W, (y + ddy) % self.H) in adj_me:
                    g[22] = 1
        for qi, (x, y) in q_pos.items():
            self.q_seen[qi] = (b.round, x, y)
        if self.id in (0, 1):
            self.q_seen[self.id] = (b.round, hx, hy)
            q_vis[self.id] = True
        # exits from the head
        he = {'N': b.hedges[3][3], 'S': b.hedges[4][3], 'W': b.vedges[3][3], 'E': b.vedges[3][4]}
        occ = {(x, y) for _, _, x, y, _, _ in b.parts}
        ex_ord = ex_por = 0
        ex_rel = {}
        for a in DIRS:
            rd = self._rel_dir(a, fac)
            tok = he[a]
            ok = 0
            if tok == '.':
                ddx, ddy = DXY[a]
                if ((hx + ddx) % self.W, (hy + ddy) % self.H) not in occ:
                    ok = 1; ex_ord += 1
            elif tok != 'w':
                ok = 1; ex_por += 1
            ex_rel[rd] = ok

        def qfeat(qid):
            s = self.q_seen[qid]
            if s is None:
                return [UNSEEN, BIG, BIG, BIG]
            f, r = self._rot(_tor(s[1] - hx, self.W), _tor(s[2] - hy, self.H), fac)
            return [b.round - s[0], f, r, abs(f) + abs(r)]

        def cell_feat(c):
            if c is None:
                return [BIG, BIG, BIG]
            f, r = self._rot(_tor(c[0] - hx, self.W), _tor(c[1] - hy, self.H), fac)
            return [f, r, abs(f) + abs(r)]

        home = self.home
        mxy = (self.W - 1 - home[0], self.H - 1 - home[1]) if home else None
        my_ = (home[0], self.H - 1 - home[1]) if home else None
        e = b.echoes
        rnd = b.round
        phase = 0 if rnd < 25 else 1 if rnd < 100 else 2 if rnd < 250 else 3 if rnd < 400 else 4
        sc = [rnd, 500 - rnd, phase, b.length, b.unit_count, self.limit, self.limit - b.unit_count,
              int(b.length >= 4 and b.unit_count < self.limit),
              self.turn, int(self.first_round > 0), rnd - self.first_round,
              (rnd - self.last_split_round) if self.last_split_round is not None else UNSEEN,
              self.last['kind'], self.last['first'], self.last['nsteps'],
              len(b.msgs), sum(1 for v in b.msgs if v), sum(1 for v in b.msgs if v > 0xFFFFFFFF),
              int(e is not None)] + (list(e) if e else [0] * 5) + [sum(e) if e else 0,
              ex_ord, ex_por, ex_rel[0], ex_rel[1], ex_rel[3],
              n_eh, n_ah, n_ep, n_ap, n_pearls, n_beds,
              eh_d1, eh_min, ah_min, pearl_min, max([v for i, v in vis_len.items() if enemy_of[i]] or [0]),
              int(self.id == self.my_queen), int(q_vis[self.my_queen])] + qfeat(self.my_queen) + \
             [int(q_vis[self.their_queen])] + qfeat(self.their_queen) + [q_parts[self.their_queen]] + \
             [int(home is not None)] + cell_feat(home) + cell_feat(mxy) + cell_feat(my_) + \
             [b.length - self.prev_len if self.prev_len is not None else 0,
              b.unit_count - self.prev_units if self.prev_units is not None else 0]
        assert len(sc) == N_SC, (len(sc), N_SC)
        self.prev_len, self.prev_units = b.length, b.unit_count
        self.turn += 1
        out = [v for g in grid for v in g]
        out += sc
        return out


def names():
    # cell k of the rotated window: forward = 3 - k // 7 (ahead > 0), right = k % 7 - 3
    return [f'f{3 - k // 7}r{k % 7 - 3}_{c}'.replace('-', 'm') for k in range(49) for c in CH] + SC

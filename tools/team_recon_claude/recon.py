"""Event-exact state reconstruction for UNSW Battlecode v1/v2 replays.

Replays the recorded event stream (not a re-simulation) and keeps the full
board: bodies, pearls, bed countdowns, sonar inboxes/echoes.  Movement is
also *predicted* from the recorded command with engine semantics
(portals/kelp/wrap) and checked against the recorded dragonUpdate events,
so every replay carries its own reconstruction-validation counters.

Semantics source: upstream unswcpmsoc/battlecode eb54612 (copied under
experiment_data/team_recon_306_20260927/semantics, read-only) and local
unswbc/engine/src/{actions,helpers,config}.cc.
"""
from __future__ import annotations

import collections
import gzip
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIRS = ('north', 'east', 'south', 'west')
DXY = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}
OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
LETTER = {'north': 'N', 'east': 'E', 'south': 'S', 'west': 'W'}
ECHO_ORDER = ('kelp', 'ally', 'allyHead', 'enemy', 'enemyHead')
VISION_R = 3

_schema = None


def schema():
    global _schema
    if _schema is None:
        import capnp
        capnp.remove_import_hook()
        _schema = capnp.load(str(HERE / 'replay_v2.capnp'))
    return _schema


def load_replay(path):
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    if raw[:1] in (b'<',) or raw[:15].lower().startswith(b'<!doctype'):
        raise ValueError('HTML body, not a replay')
    return schema().Replay.from_bytes_packed(raw, traversal_limit_in_words=2 ** 62)


class Board:
    """Static map: size, beds, kelp/portal edges, spawns, unit limit."""

    def __init__(self, text):
        self.W = self.H = 0
        self.unit_limit = 64  # engine DEFAULT_UNIT_LIMIT unless the map overrides
        self.symmetry = None
        self.name = None
        self.gaps = {}           # bed -> (min,max)
        self.hedge = {}          # (x,y) north side of tile -> ('k',) or ('p', id)
        self.vedge = {}          # (x,y) west side of tile
        ends = collections.defaultdict(list)
        self.spawns = []
        for line in text.splitlines():
            p = line.split()
            if not p:
                continue
            k = p[0]
            if k == 'MAP':
                self.W, self.H = int(p[1]), int(p[2])
            elif k == 'UNIT_LIMIT':
                self.unit_limit = int(p[1])
            elif k == 'SYMMETRY':
                self.symmetry = p[1]
            elif k == 'MAP_NAME':
                self.name = ' '.join(p[1:])
            elif k == 'TILE':
                x, y, mn, mx = map(int, p[1:5])
                if mx > 0:
                    self.gaps[(x, y)] = (mn, mx)
            elif k == 'EDGE':
                idx, kind, pid = int(p[1]), int(p[2]), int(p[3])
                e = self._edge_of_index(idx)
                if e is None:
                    continue
                table, key = e
                if kind == 0:
                    table.pop(key, None)
                elif kind == 1:
                    table[key] = ('k',)
                elif kind == 2:
                    old = table.get(key)
                    newid = min(old[1], pid) if old and old[0] == 'p' else pid
                    table[key] = ('p', newid)
                    ends[pid].append((table is self.hedge, key))
            elif k == 'DRAGON':
                n = int(p[2])
                self.spawns.append(('AB'[int(p[1])], [(int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)]))
        self.partner = {}
        for pid, es in ends.items():
            if len(es) == 2:
                a, b = es
                self.partner[a] = b
                self.partner[b] = a
                tid = min(self._table(a)[a[1]][1], self._table(b)[b[1]][1])
                self._table(a)[a[1]] = ('p', tid)
                self._table(b)[b[1]] = ('p', tid)
        # neighbour table: tile -> ((dest|None, via_portal, has_edge) for N,E,S,W)
        self.nbr = {}
        for y in range(self.H):
            for x in range(self.W):
                row = []
                for d in DIRS:
                    t, via = self.step((x, y), d)
                    row.append((t, via, self.edge((x, y), d) is not None))
                self.nbr[(x, y)] = tuple(row)
        self.portal_edges = sum(1 for t in (self.hedge, self.vedge) for v in t.values() if v[0] == 'p')

    def _table(self, e):
        return self.hedge if e[0] else self.vedge

    def _edge_of_index(self, idx):
        stride = self.W + 1
        col, row = idx % stride, idx // stride
        if row % 2 == 0:
            if col == self.W or row == 2 * self.H:
                return None
            return self.hedge, (col, row // 2)
        if col == self.W:
            return None
        return self.vedge, (col, (row - 1) // 2)

    def wrap(self, x, y):
        return x % self.W, y % self.H

    def edge_key(self, tile, d):
        """(is_horizontal, key) of the edge on side d of tile."""
        x, y = tile
        if d == 'north':
            return True, (x, y)
        if d == 'south':
            return True, (x, (y + 1) % self.H)
        if d == 'west':
            return False, (x, y)
        return False, ((x + 1) % self.W, y)

    def edge(self, tile, d):
        h, key = self.edge_key(tile, d)
        return (self.hedge if h else self.vedge).get(key)

    def step(self, tile, d):
        """Tile after stepping; None into kelp.  Returns (tile, via_portal)."""
        h, key = self.edge_key(tile, d)
        e = (self.hedge if h else self.vedge).get(key)
        if e is None:
            dx, dy = DXY[d]
            return self.wrap(tile[0] + dx, tile[1] + dy), False
        if e[0] == 'k':
            return None, False
        ph, pkey = self.partner[(h, key)]
        x, y = pkey
        if ph:
            t = (x, y) if d == 'south' else (x, y - 1)
        else:
            t = (x, y) if d == 'east' else (x - 1, y)
        return self.wrap(*t), True

    def dir_between(self, a, b):
        for d in DIRS:
            t, _ = self.step(a, d)
            if t == b:
                return d
        return None

    def mirror(self, p):
        x, y = p
        s = self.symmetry
        if s == 'x':
            return (x, self.H - 1 - y)
        if s == 'y':
            return (self.W - 1 - x, y)
        if s == 'xy':
            return (self.W - 1 - x, self.H - 1 - y)
        return p


class Dragon:
    __slots__ = ('id', 'team', 'body', 'facing', 'alive', 'born', 'parent', 'last_turn_round',
                 'inbox', 'echo', 'pending_echo', 'turns')

    def __init__(self, ident, team, body, facing, born, parent=None):
        self.id, self.team, self.body, self.facing = ident, team, collections.deque(body), facing
        self.alive, self.born, self.parent = True, born, parent
        self.last_turn_round = None
        self.inbox = []          # (value64, value32, sender) since last turn
        self.echo = [0] * 5      # counts from own sonars last turn
        self.pending_echo = [0] * 5
        self.turns = 0


class Game:
    """Full-state replay walker.  Call run(callback) — callback(kind, **info)."""

    def __init__(self, path):
        self.path = str(path)
        self.rep = load_replay(path)
        self.version = self.rep.formatVersion
        self.board = Board(self.rep.map)
        self.round = -1
        self.dragons = {}
        self.occ = {}
        self.pearls = {}             # tile -> provenance ('bed'|'corpse'|'init')
        self.countdown = {}
        self.checks = collections.Counter()
        b = self.board
        for i, (team, cells) in enumerate(b.spawns):
            facing = b.dir_between(cells[1], cells[0])
            d = Dragon(i, team, cells, facing, -1)
            self.dragons[i] = d
            for c in cells:
                self.occ[c] = i
        self.next_id = len(b.spawns)

    # -- queries -------------------------------------------------------
    def in_vision(self, head, tile):
        W, H = self.board.W, self.board.H
        ox = (tile[0] - head[0]) % W
        oy = (tile[1] - head[1]) % H
        return (ox <= VISION_R or ox >= W - VISION_R) and (oy <= VISION_R or oy >= H - VISION_R)

    def seg_facing(self, d, i):
        if i == 0:
            return d.facing
        return self.board.dir_between(d.body[i], d.body[i - 1])

    def unit_count(self, team):
        return sum(1 for d in self.dragons.values() if d.alive and d.team == team)

    # -- walker --------------------------------------------------------
    def _kill(self, d):
        d.alive = False
        for c in d.body:
            if self.occ.get(c) == d.id:
                del self.occ[c]

    def run(self, cb=None):
        cb = cb or (lambda *a, **k: None)
        b = self.board
        turn = None           # dragon id currently acting
        phase = 'pre'         # pre | tick | turn
        pred = None           # predicted step list for validation
        for ev in self.rep.events:
            w = ev.which()
            if w == 'sonarPing':
                s = ev.sonarPing
                v64 = s.value64 if self.version >= 2 else s.value
                hk = str(s.hitKind) if self.version >= 2 else 'unknown'
                sender = self.dragons.get(s.senderId)
                hit = s.hitId if s.which() == 'hitId' else None
                if hit is not None and hit in self.dragons:
                    self.dragons[hit].inbox.append((v64, s.value, s.senderId))
                if sender is not None and hk in ECHO_ORDER:
                    sender.pending_echo[ECHO_ORDER.index(hk)] += 1
                cb('sonar', sender=s.senderId, direction=str(s.direction), value64=v64, hit=hit, hitkind=hk,
                   origin=(s.origin.x, s.origin.y), end=(s.end.x, s.end.y))
            elif w == 'turnStart':
                ident = ev.turnStart.id
                turn = ident
                phase = 'turn'
                d = self.dragons[ident]
                d.echo = d.pending_echo       # echoes of the sonars cast at the end of its previous turn
                d.pending_echo = [0] * 5
                cb('turn', dragon=d)          # observation point: state == round block
                d.inbox = []
                d.last_turn_round = self.round
                d.turns += 1
            elif w == 'dragonAction':
                a = ev.dragonAction
                d = self.dragons[a.id]
                act = None
                if a.tle or not a._has('action'):
                    act = ('tle',)
                else:
                    try:
                        which = a.action.which()
                    except Exception:
                        which = None
                    if which == 'move':
                        act = ('move', [str(x) for x in a.action.move])
                    elif which == 'split':
                        act = ('split', a.action.split)
                    elif which == 'suicide':
                        act = ('suicide',)
                    else:
                        act = ('none',)
                pts = None
                try:
                    if a._has('instructions'):
                        pts = a.instructions.count
                except Exception:
                    pts = None
                pred = None
                if act[0] == 'move':
                    pred = self._predict(d, act[1])
                cb('action', dragon=d, action=act, tle=bool(a.tle), points=pts)
            elif w == 'dragonUpdate':
                u = ev.dragonUpdate
                d = self.dragons.get(u.id)
                h, t = (u.head.x, u.head.y), (u.tail.x, u.tail.y)
                if phase == 'pre' or d is None:
                    if d is not None:
                        d.facing = str(u.facing)
                        if d.body[0] != h:
                            self.checks['init_head_mismatch'] += 1
                    continue
                if pred:
                    exp = pred.pop(0)
                    self.checks['step_ok' if exp[0] == h else 'step_bad'] += 1
                    via = exp[1]
                else:
                    via = False
                ate = False
                if d.body[0] != h:
                    d.body.appendleft(h)
                    self.occ[h] = d.id
                old_len = len(d.body)
                while len(d.body) > 1 and d.body[-1] != t:
                    c = d.body.pop()
                    if self.occ.get(c) == d.id:
                        del self.occ[c]
                d.facing = str(u.facing)
                cb('step', dragon=d, head=h, via_portal=via, length_after=len(d.body), popped=old_len - len(d.body))
            elif w == 'tileChange':
                tc = ev.tileChange
                p = (tc.tile.x, tc.tile.y)
                if tc.hasPearl:
                    prov = 'bed' if phase == 'tick' else ('corpse' if phase == 'turn' else 'init')
                    self.pearls[p] = prov
                    cb('pearl_add', tile=p, prov=prov)
                else:
                    prov = self.pearls.pop(p, None)
                    cb('pearl_eat', tile=p, prov=prov, dragon=self.dragons.get(turn))
            elif w == 'pearlCountdown':
                pc = ev.pearlCountdown
                self.countdown[(pc.tile.x, pc.tile.y)] = pc.countdown
            elif w == 'roundStart':
                self.round = ev.roundStart.round
                phase = 'tick'
                for k in self.countdown:
                    self.countdown[k] -= 1
                cb('round', round=self.round)
            elif w == 'dragonSplit':
                s = ev.dragonSplit
                par = self.dragons[s.parentId]
                pb = [(p.x, p.y) for p in s.parentBody]
                chb = [(p.x, p.y) for p in s.childBody]
                par.body = collections.deque(pb)
                team = 'A' if str(s.team) == 'a' else 'B'
                ch = Dragon(s.childId, team, chb, str(s.childFacing), self.round, s.parentId)
                self.dragons[s.childId] = ch
                for c in chb:
                    self.occ[c] = ch.id
                for c in pb:
                    self.occ[c] = par.id
                cb('split', parent=par, child=ch)
            elif w == 'dragonDeath':
                dd = ev.dragonDeath
                d = self.dragons[dd.id]
                length = len(d.body)
                self._kill(d)
                cb('death', dragon=d, reason=str(dd.reason), length=length, actor=turn)
                pred = None if dd.id == turn else pred
        res = self.rep.result
        self.result = dict(
            terminated=res.terminated, reason=str(res.endReason),
            winner=(str(res.winner).upper() if res.which() == 'winner' else None),
            A=dict(units=res.teamA.dragonCount, longest=res.teamA.longestDragon, total=res.teamA.totalLength),
            B=dict(units=res.teamB.dragonCount, longest=res.teamB.longestDragon, total=res.teamB.totalLength),
            rounds=self.round + 1)
        for t in 'AB':
            alive = [d for d in self.dragons.values() if d.alive and d.team == t]
            ok = (len(alive) == self.result[t]['units'] and
                  sum(len(d.body) for d in alive) == self.result[t]['total'] and
                  max([len(d.body) for d in alive] or [0]) == self.result[t]['longest'])
            self.checks['standings_ok' if ok else 'standings_bad'] += 1
        cb('end', result=self.result)
        return self.result

    def _predict(self, d, steps):
        out = []
        at = d.body[0]
        for s in steps:
            t, via = self.board.step(at, s)
            if t is None:
                break
            out.append((t, via))
            at = t
        return out

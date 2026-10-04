"""Rebuild, from a replay alone, the exact protocol block every dragon received on every turn.

Why: the encoder (encode.py) takes only blocks, so a dataset built from a replay is legal-observation by construction.
This module is the one place that touches replay (global) state; everything downstream sees blocks only.
Validated against the engine's real blocks by test_rebuild.py (engine runs with logged replies).

Unknowable from a replay (documented, flagged per row): whether a process negotiated protocol 3. We assume it did
from its second turn on (the ECHOES line appears from turn 2 for a p3 process); `proto3=False` drops the ECHOES line
and >32-bit messages, as the engine does for an old-protocol process.
"""
import collections, gzip, struct, sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for p in (_HERE.parents[1] / 'hub' / 'vendor' / 'leviathan', Path.cwd() / 'tools' / 'hub' / 'vendor' / 'leviathan'):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))
from replay import Reader, unpack  # noqa: E402

DIRS = 'NESW'
DXY = ((0, -1), (1, 0), (0, 1), (-1, 0))
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
HIT = ('unknown', 'empty', 'kelp', 'ally', 'ally_head', 'enemy', 'enemy_head')


def reader(data):
    if data[:2] == b'\x1f\x8b':
        data = gzip.decompress(data)
    r = Reader.__new__(Reader)
    r.raw = unpack(data)
    count = struct.unpack_from('<I', r.raw)[0] + 1
    sizes = struct.unpack_from('<' + 'I' * count, r.raw, 4)
    off = ((count + 2) // 2) * 8
    r.segments = []
    for s in sizes:
        r.segments.append(memoryview(r.raw)[off:off + s * 8]); off += s * 8
    return r


class Map:
    def __init__(self, text):
        self.text = text
        self.W = self.H = 0
        self.tiles = {}
        self.hedge = {}   # (x, y) -> token of the north edge of cell (x, y)
        self.vedge = {}   # (x, y) -> token of the west edge of cell (x, y)
        self.dragons = []
        self.unit_limit = 64
        self.name = 'unknown'
        self.symmetry = ''
        for ln in text.splitlines():
            p = ln.split()
            if not p:
                continue
            k = p[0]
            if k == 'MAP':
                self.W, self.H = int(p[1]), int(p[2])
            elif k == 'MAP_NAME':
                self.name = ln[9:]
            elif k == 'SYMMETRY':
                self.symmetry = p[1]
            elif k == 'UNIT_LIMIT':
                self.unit_limit = int(p[1])
            elif k == 'TILE':
                self.tiles[(int(p[1]), int(p[2]))] = (int(p[3]), int(p[4]))
            elif k == 'EDGE':
                idx, kind, pid = int(p[1]), int(p[2]), int(p[3])
                col, row = idx % (self.W + 1), idx // (self.W + 1)
                if col >= self.W or row >= 2 * self.H:
                    continue
                tok = '.' if kind == 0 else 'w' if kind == 1 else str(pid)
                (self.hedge if row % 2 == 0 else self.vedge)[(col, row // 2)] = tok
            elif k == 'DRAGON':
                n = int(p[2])
                self.dragons.append(('AB'[int(p[1])], [(int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)]))
        self.beds = {c for c, v in self.tiles.items() if v[1] > 0}

    def h(self, x, y):
        return self.hedge.get((x % self.W, y % self.H), '.')

    def v(self, x, y):
        return self.vedge.get((x % self.W, y % self.H), '.')


class Dragon:
    __slots__ = ('id', 'team', 'body', 'fac', 'facing', 'alive', 'inbox', 'echo', 'turns', 'born', 'parent')

    def __init__(self, i, team, body, fac, facing, born, parent=None):
        self.id, self.team, self.body, self.fac, self.facing = i, team, collections.deque(body), collections.deque(fac), facing
        self.alive, self.inbox, self.echo, self.turns, self.born, self.parent = True, [], None, 0, born, parent


def _step(m, a, b):
    for d, (dx, dy) in zip(DIRS, DXY):
        if ((a[0] + dx) % m.W, (a[1] + dy) % m.H) == b:
            return d
    return None


def _initial_facing(m, body):
    # map spawns carry no facing; the engine points the head away from its neck (neck -> head)
    if len(body) < 2:
        return 'N'
    (hx, hy), (nx, ny) = body[0], body[1]
    for d, (dx, dy) in zip(DIRS, DXY):
        if ((nx + dx) % m.W, (ny + dy) % m.H) == (hx, hy):
            return d
    return 'N'


def walk(data, emit, proto3=True):
    """Stream a replay; call emit(dragon_id, spawn_dict, block_text, ctx) once per dragon turn, in engine order, when
    the turn has finished. ctx carries replay-side facts for LABELS only (never encoder input): round, facing and
    head at turn start, the action (('move', 'NNE') | ('split', k) | ('suicide', None) | None), tle, the sonar pings
    cast (requested-or-physical dir, origin, value, hit kind), death cause during the turn, and split child."""
    r = reader(data)
    root = r.object(0, 0)
    m = Map(root.text(0))
    D = {}
    for i, (t, b) in enumerate(m.dragons):
        f = _initial_facing(m, b)
        fac = [f] + [_step(m, b[k], b[k - 1]) or f for k in range(1, len(b))]
        D[i] = Dragon(i, t, b, fac, f, 0)
    pearls, cd = set(), {}
    rnd = -1
    cur = {}

    def flush():
        if cur.get('id') is not None:
            d = D[cur['id']]
            cur['ctx']['facing_after'] = d.facing
            cur['ctx']['head_after'] = d.body[0]
            emit(cur['id'], dict(id=cur['id'], team=d.team, W=m.W, H=m.H, unit_limit=m.unit_limit), cur['txt'], cur['ctx'])
        cur.clear()

    def point(o):
        return (o.num(), o.num(4))

    def _cd(c):
        if c not in m.beds or c not in cd:
            return -1
        v, r0 = cd[c]
        return v - (rnd - r0)

    def block(d):
        hx, hy = d.body[0]
        cells = [((hx + c - 3) % m.W, (hy + rr - 3) % m.H) for rr in range(7) for c in range(7)]
        cset = set(cells)
        p3 = proto3 and (d.turns > 0 or d.parent is not None)
        msgs = [v for v in d.inbox if p3 or v <= 0xFFFFFFFF]
        out = [f'ROUND {rnd}', f'DIR {d.facing}', f'LENGTH {len(d.body)}',
               f'UNIT_COUNT {sum(1 for o in D.values() if o.alive and o.team == d.team)}', f'NUM_MSGS {len(msgs)}']
        out += [str(v) for v in msgs]
        if p3:
            out.append('ECHOES ' + ' '.join(map(str, d.echo or (0, 0, 0, 0, 0))))
        for c in cells:
            out.append(f'{c[0]} {c[1]} {1 if c in pearls else 0} {_cd(c)}')
        parts = []
        for o in sorted(D.values(), key=lambda z: z.id):
            if not o.alive:
                continue
            for k, c in enumerate(o.body):
                if c in cset:
                    parts.append(f'{o.team} {o.id} {c[0]} {c[1]} {o.fac[k]} {1 if k == 0 else 0}')
        out.append(f'DRAGON_BODIES {len(parts)}')
        out += parts
        x0, y0 = hx - 3, hy - 3
        for rr in range(8):
            out.append(' '.join(m.h(x0 + c, y0 + rr) for c in range(7)))
        for rr in range(7):
            out.append(' '.join(m.v(x0 + c, y0 + rr) for c in range(8)))
        return '\n'.join(out) + '\n'

    for e in root.items(3):
        kind = e.num(0, 'H')
        o = e.child(0)
        if kind == 0:
            flush()
            rnd = o.num()
        elif kind == 1:
            flush()
            i = o.num()
            d = D[i]
            txt = block(d)
            cur.update(id=i, txt=txt, ctx=dict(round=rnd, born=d.born, parent=d.parent, turn=d.turns, facing=d.facing,
                                                head=d.body[0], length=len(d.body), action=None, tle=False, sonar=[],
                                                death=None, split_child=None))
            d.inbox = []
            d.echo = [0, 0, 0, 0, 0]
            d.turns += 1
        elif kind == 4:
            if cur.get('id') == o.num():
                c = cur['ctx']
                c['tle'] = bool(o.num(4, 'B') & 1)
                if o.has(0):
                    a = o.child(0)
                    ak = a.num(0, 'H')
                    if ak == 0:
                        s_, at, word = r.pointer(a.s, a.a + a.dw)
                        cnt = word >> 35
                        steps = struct.unpack_from('<' + 'H' * cnt, r.segments[s_], at * 8) if cnt else ()
                        c['action'] = ('move', ''.join(DIRS[v] for v in steps))
                    elif ak == 1:
                        c['action'] = ('split', a.num(4))
                    elif ak == 2:
                        c['action'] = ('suicide', None)
                    else:
                        c['action'] = (f'kind{ak}', None)
        elif kind == 2:
            cd[point(o.child(0))] = (o.num(0), rnd)
        elif kind == 3:
            c = point(o.child(0))
            if o.num(0, 'B') & 1:
                pearls.add(c)
            else:
                pearls.discard(c)
        elif kind == 9:
            i = o.num()
            d = D[i]
            fac = DIRS[o.num(4, 'H')]
            head, tail = point(o.child(0)), point(o.child(1))
            if d.body[0] != head:
                # the head stepped: the cell it left keeps the direction of that step
                d.fac[0] = fac
                d.body.appendleft(head); d.fac.appendleft(fac)
            d.facing = fac
            d.fac[0] = fac
            while len(d.body) > 1 and d.body[-1] != tail:
                d.body.pop(); d.fac.pop()
        elif kind == 10:
            pid, cid = o.num(), o.num(4)
            cf = DIRS[o.num(10, 'H')]
            p = D[pid]
            pb = [point(q) for q in o.items(0)]
            cb = [point(q) for q in o.items(1)]
            old = dict(zip(p.body, p.fac))
            p.body = collections.deque(pb); p.fac = collections.deque(old.get(c, p.facing) for c in pb)
            # a reversed segment faces its new predecessor (toward the child's head): the old facing of the cell
            # behind it, reversed (equal to the geometric step except across a portal)
            cfac = [cf] + [OPP[old.get(cb[k - 1], 'N')] for k in range(1, len(cb))]
            D[cid] = Dragon(cid, p.team, cb, cfac, cf, rnd, pid)
            if cur.get('id') == pid:
                cur['ctx']['split_child'] = (cid, len(cb))
        elif kind == 11:
            did = o.num()
            D[did].alive = False
            if cur.get('id') == did:
                cur['ctx']['death'] = ('wall', 'self', 'body', 'h2h', 'invalid')[o.num(4, 'H')] if o.num(4, 'H') < 5 else 'other'
        elif kind == 12:
            sid = o.num()
            which = o.num(6, 'H')
            hk = HIT[o.num(24, 'H')] if o.num(24, 'H') < 7 else 'unknown'
            v64 = o.num(16, 'Q')
            if which == 1:
                hid = o.num(12)
                if hid in D:
                    D[hid].inbox.append(v64)
            if cur.get('id') == sid:
                cur['ctx']['sonar'].append(dict(dir=DIRS[o.num(4, 'H')], origin=point(o.child(0)), value=v64, hit=hk))
            s = D.get(sid)
            if s is not None:
                if s.echo is None:
                    s.echo = [0, 0, 0, 0, 0]
                j = ('kelp', 'ally', 'ally_head', 'enemy', 'enemy_head')
                if hk in j:
                    s.echo[j.index(hk)] += 1
    flush()
    return m

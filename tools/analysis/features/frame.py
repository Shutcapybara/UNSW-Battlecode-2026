"""Decode a replay once into a compact per-game frame (F1 feature lab).

Input contract: a replay path (local or field corpus). Output: a plain dict (picklable) with
  meta      bots, map, map_hash, W, H, winner, reason, last round, replay version
  terrain   nbr[cell] -> 4 destinations (N,E,S,W; None = kelp wall), beds {cell: (minGap, maxGap)}
  rounds    per round r (start-of-round snapshot): {id: (team, body tuple head-first)}
  pearls    per round r: frozenset of cells holding a pearl at round start
  events    eats, spawns, splits, deaths, sonar, actions, countdowns (lists of dicts)
Event layout follows the viewer's capnp schema (engine event variant order 0..12):
RoundStart TurnStart PearlCountdown TileChange DragonAction EngineLog DragonLog DragonIndicator DebugDraw
DragonUpdate DragonSplit DragonDeath SonarPing.
"""
import collections, gzip, hashlib, os, pickle, sys
from pathlib import Path

_V = Path(__file__).resolve().parents[2] / 'hub' / 'vendor'
for p in (_V / 'leviathan', _V / 'ouroboros'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from replay import Reader  # noqa: E402
from mapview import load_map  # noqa: E402

FRAME_VERSION = 7
# unswbc >= 1.2.3 ranks a game that reaches the round limit by (queen length, longest dragon, total length); the queen
# is the team's starting dragon (id 0 or 1; a split child takes a new id, the parent keeps its own) and a dead queen
# counts 0. FRAME_RULES=pre123 restores the old (longest, total) ranking for replays played under unswbc <= 1.2.2.
RULES = os.environ.get('FRAME_RULES', '123')
DIRS = 'NESW'
DEATH_CAUSES = ('wall', 'self', 'body', 'h2h', 'invalid')
HIT_KINDS = ('unknown', 'empty', 'kelp', 'ally', 'ally_head', 'enemy', 'enemy_head')


def terrain(maptext):
    m = load_map(maptext)
    W, H = m['W'], m['H']
    edges, ports = {}, collections.defaultdict(list)
    for line in maptext.splitlines():
        p = line.split()
        if p and p[0] == 'EDGE':
            idx, k, pid = map(int, p[1:])
            col, row = idx % (W + 1), idx // (W + 1)
            if col >= W or row >= 2 * H:
                continue
            key = (row % 2, col, row // 2)
            edges[key] = (k, pid)
            if k == 2:
                ports[pid].append(key)

    def dest(c, d):
        x, y = c
        key = ((0, x, y), (1, (x + 1) % W, y), (0, x, (y + 1) % H), (1, x, y))[d]
        k, pid = edges.get(key, (0, -1))
        if k == 1:
            return None
        if k == 2:
            other = next(e for e in ports[pid] if e != key)
            ori, x2, y2 = other
            return ((x2 if ori == 0 or d == 1 else x2 - 1) % W, (y2 if ori == 1 or d == 2 else y2 - 1) % H)
        return ((x + (0, 1, 0, -1)[d]) % W, (y + (-1, 0, 1, 0)[d]) % H)

    nbr = {(x, y): tuple(dest((x, y), d) for d in range(4)) for x in range(W) for y in range(H)}
    beds = {c: v for c, v in m['tiles'].items() if v[1] > 0}
    portal_cells = set()
    for pid, keys in ports.items():
        for ori, x, y in keys:
            portal_cells.add((x % W, y % H))
            portal_cells.add(((x - 1) % W, y % H) if ori == 1 else (x % W, (y - 1) % H))
    return m, W, H, nbr, beds, portal_cells


def _reader(path):
    """Reader over raw or gzip-served replay bytes (the public corpus stores what the server sent)"""
    import struct
    from replay import unpack
    data = Path(path).read_bytes()
    if data[:2] == b'\x1f\x8b':
        data = gzip.decompress(data)
    r = Reader.__new__(Reader)
    r.raw = unpack(data)
    count = struct.unpack_from('<I', r.raw)[0] + 1
    sizes = struct.unpack_from('<' + 'I' * count, r.raw, 4)
    offset = ((count + 2) // 2) * 8
    r.segments = []
    for size in sizes:
        r.segments.append(memoryview(r.raw)[offset:offset + size * 8])
        offset += size * 8
    return r


def decode(path):
    r = _reader(path)
    root = r.object(0, 0)
    version = root.num(0, 'I')
    if version not in (0, 1, 2):
        raise ValueError(f'unsupported replay version {version}')
    maptext = root.text(0)
    m, W, H, nbr, beds, portal_cells = terrain(maptext)
    name = next((l[9:] for l in maptext.splitlines() if l.startswith('MAP_NAME ')), 'unknown')
    teams = {i: t for i, (t, b) in enumerate(m['dragons'])}
    body = {i: collections.deque(b) for i, (t, b) in enumerate(m['dragons'])}
    live = set(body)
    born = {i: 0 for i in live}
    pearls, pearl_origin = set(), {}
    rounds, pearl_rounds = [], []
    ev = dict(eats=[], spawns=[], splits=[], deaths=[], sonar=[], actions=[], countdowns=[])
    rnd, actor, steps, upd, drop, h2h_victim = -1, None, [], 0, None, None

    def point(o):
        return (o.num(), o.num(4))

    cur = dict(rec=None, before=0, eats=0, death_len=None)

    def finalize():
        a = cur['rec']
        if a is not None and a['kind'] == 'move':
            after = cur['death_len'] if cur['death_len'] is not None else len(body[a['id']])
            a['paid'] = cur['before'] + cur['eats'] - after     # segments paid for sprinting (0 for a walk)
        cur.update(rec=None, eats=0, death_len=None)

    def snap():
        rounds.append({i: (teams[i], tuple(body[i])) for i in live})
        pearl_rounds.append(frozenset(pearls))

    for e in root.items(3):
        kind = e.num(0, 'H')
        o = e.child(0)
        i = o.num()
        if kind not in (3, 11):
            drop = None
        if kind in (0, 1):
            finalize()
        if kind == 0:
            rnd = i
            while len(rounds) <= rnd:
                snap()
        elif kind == 1:
            actor, steps, upd, h2h_victim = i, [], 0, None
            cur['before'] = len(body[i]) if i in body else 0
        elif kind == 2:
            ev['countdowns'].append(dict(round=rnd, cell=point(o.child(0)), countdown=o.num(0)))
        elif kind == 3:
            c = point(o.child(0))
            if o.num(0, 'B') & 1:
                origin = drop if drop else ('bed', None)
                pearls.add(c)
                pearl_origin[c] = (origin, rnd)
                ev['spawns'].append(dict(round=rnd, cell=c, origin=origin[0], donor=origin[1]))
            else:
                pearls.discard(c)
                (origin, donor), born_r = pearl_origin.pop(c, (('unknown', None), rnd))
                if actor in live:
                    t = teams[actor]
                    label = origin if origin in ('bed', 'unknown') else ('ally_corpse' if origin == t else 'enemy_corpse')
                    cur['eats'] += 1
                    ev['eats'].append(dict(round=rnd, id=actor, team=t, cell=c, origin=label, age=rnd - born_r, donor=donor))
        elif kind == 4:
            t = teams[i]
            rec = dict(round=rnd, id=i, team=t, kind=None, steps=0, tle=bool(o.num(4, 'B') & 1), cpu=None)
            if o.has(1):
                rec['cpu'] = o.child(1).num(0, 'Q')
            if o.has(0):
                a = o.child(0)
                ak = a.num(0, 'H')
                rec['kind'] = ('move', 'split', 'suicide')[ak] if ak < 3 else str(ak)
                if ak == 0:
                    import struct
                    s, at, word = r.pointer(a.s, a.a + a.dw)
                    count = word >> 35
                    steps = list(struct.unpack_from('<' + 'H' * count, r.segments[s], at * 8)) if count else []
                    rec['steps'] = count
                    rec['dirs'] = tuple(steps)
            ev['actions'].append(rec)
            cur['rec'] = rec
        elif kind == 9:
            b = body[i]
            head, tail = point(o.child(0)), point(o.child(1))
            if b[0] != head:
                b.appendleft(head)
                if i == actor:
                    upd += 1
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif kind == 10:
            child = o.num(4)
            t = teams[i]
            teams[child] = t
            born[child] = rnd
            live.add(child)
            before = len(body[i])
            body[i] = collections.deque(point(p) for p in o.items(0))
            body[child] = collections.deque(point(p) for p in o.items(1))
            ev['splits'].append(dict(round=rnd, team=t, parent=i, child=child, before=before,
                                     parent_len=len(body[i]), child_len=len(body[child])))
        elif kind == 11:
            t = teams[i]
            cause = DEATH_CAUSES[o.num(4, 'H')] if o.num(4, 'H') < 5 else 'other'
            rec = dict(round=rnd, id=i, team=t, cause=cause, length=len(body[i]), actor=actor, age=rnd - born[i],
                       head=body[i][0], initial=born[i] == 0 and i < len(m['dragons']), killer=None, killer_team=None)
            if i != actor and actor in teams:
                rec['killer'], rec['killer_team'] = actor, teams[actor]  # h2h victim: the mover's head hit ours
                h2h_victim = i
            elif i == actor and cause == 'h2h' and h2h_victim is not None:
                rec['killer'], rec['killer_team'], rec['mutual'] = h2h_victim, teams[h2h_victim], True
            elif i == actor and cause in ('body', 'h2h') and upd < len(steps):
                nxt = nbr[body[i][0]][steps[upd]]
                occ = {c: j for j in live if j != i for c in body[j]}
                if nxt in occ:
                    rec['killer'], rec['killer_team'] = occ[nxt], teams[occ[nxt]]
                elif nxt is not None and nxt in body[i]:
                    rec['killer'], rec['killer_team'] = i, t
            ev['deaths'].append(rec)
            if i == actor:
                cur['death_len'] = len(body[i])
            live.discard(i)
            drop = (t, i)
        elif kind == 12:
            which = o.num(6, 'H')
            hk = o.num(24, 'H')
            org = point(o.child(0))
            # a ray aimed into the sender's own neck exits through the tail (total internal refraction): dir is then the
            # physical direction of travel, not the one requested
            refr = i in body and len(body[i]) > 0 and org != body[i][0]
            ev['sonar'].append(dict(round=rnd, id=i, team=teams.get(i), dir=o.num(4, 'H'), origin=org, refracted=refr,
                                    end=point(o.child(1)), hit=o.num(12) if which == 1 else None,
                                    hit_kind=HIT_KINDS[hk] if hk < 7 else str(hk)))
    finalize()
    snap()  # final state after the last round
    res = root.child(4)
    # TeamStanding: dragonCount, longestDragon, totalLength and, from unswbc 1.2.3, a fourth int32: the queen's length (the
    # team's original lowest-id dragon; 0 once it has died, no succession; always 0 in replays written before 1.2.3)
    final = {t: dict(units=res.child(n).num(), longest=res.child(n).num(4), total=res.child(n).num(8), queen=res.child(n).num(12))
             for n, t in enumerate('AB')}
    for i in (0, 1):  # the queens inferred from the body track (ids 0 and 1): for analysis of pre-1.2.3 replays, whose header has no queen field
        if i in teams:
            final[teams[i]]['queen_body'] = len(body[i]) if i in live else 0
    fa, fb = final['A'], final['B']
    keys = ('longest', 'total') if RULES == 'pre123' else ('queen', 'longest', 'total')
    if res.num(0, 'B') & 1:
        # the engine's own verdict (GameResult: endReason u16 @2, union tag u16 @4 = 1 for a winner, winner u16 @6, 0 = A).
        # Authoritative under every rule set (Antioch, validated 300/300 against server winners, 1 Oct)
        winner = ('A', 'B')[res.num(6, 'H')] if res.num(4, 'H') == 1 else 'draw'
        if res.num(2, 'H') == 0:
            reason = 'elimination'
        else:
            reason = next((k for k in keys if fa.get(k, 0) != fb.get(k, 0)), 'tie')
    else:   # unterminated record: infer (FRAME_RULES=pre123 restores the old ranking for replays played under <= 1.2.2)
        alive_a, alive_b = fa['units'] > 0, fb['units'] > 0
        if alive_a != alive_b:
            winner, reason = ('A' if alive_a else 'B'), 'elimination'
        else:
            ka, kb = tuple(fa.get(k, 0) for k in keys), tuple(fb.get(k, 0) for k in keys)
            winner = 'A' if ka > kb else 'B' if kb > ka else 'draw'
            reason = next((k for k in keys if fa.get(k, 0) != fb.get(k, 0)), 'tie')
    return dict(
        frame_version=FRAME_VERSION, file=str(path), id=Path(path).stem, version=version,
        botA=root.text(1), botB=root.text(2), map=name, map_hash=hashlib.sha256(maptext.encode()).hexdigest()[:12],
        W=W, H=H, nbr=nbr, beds=beds, portal_cells=portal_cells, n_initial=len(m['dragons']),
        winner=winner, reason=reason, final=final, last_round=len(rounds) - 2,
        rounds=rounds, pearls=pearl_rounds, events=ev)


def load(path, cache_dir=None):
    """Decode with an on-disk cache keyed by path + size + mtime."""
    path = Path(path)
    if cache_dir is None:
        return decode(path)
    st = path.stat()
    key = hashlib.sha1(f'{path.resolve()}|{st.st_size}|{st.st_mtime_ns}|{FRAME_VERSION}|{RULES}'.encode()).hexdigest()[:16]
    cp = Path(cache_dir) / f'{path.stem}.{key}.pkl.gz'
    if cp.exists():
        with gzip.open(cp, 'rb') as f:
            return pickle.load(f)
    g = decode(path)
    cp.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(cp, 'wb', compresslevel=3) as f:
        pickle.dump(g, f, protocol=pickle.HIGHEST_PROTOCOL)
    return g

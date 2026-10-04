"""Parse the engine's per-turn protocol block (the exact text a dragon receives) into a plain structure.

This is the only input the Phase 3 encoder accepts: everything a policy sees must be derivable from the sequence of
blocks one dragon process has received (its legal observation), plus its spawn block. No replay state, no map file.

Block grammar (unswbc 1.2.9, protocol 3; see the C++ helper's update()):
    ROUND r | DIR d | LENGTH n | UNIT_COUNT u | NUM_MSGS k + k lines of uint64 | [ECHOES kelp ally allyHead enemy enemyHead]
    49 tiles "x y hasPearl pearlIn" row-major from the top-left | DRAGON_BODIES m + m lines "team id x y facing isHead"
    8 rows x 7 horizontal edges | 7 rows x 8 vertical edges        (edge tokens: '.' empty, 'w' kelp, int = portal id)
"""
from dataclasses import dataclass, field

VISION = 7
R = 3


@dataclass
class Spawn:
    id: int
    team: str
    W: int
    H: int
    unit_limit: int


@dataclass
class Block:
    round: int
    dir: str
    length: int
    unit_count: int
    msgs: list
    echoes: tuple | None            # (kelp, ally, ally_head, enemy, enemy_head) or None when the line is absent
    tiles: list                     # 49 x (x, y, has_pearl, pearl_in), row-major from the top-left of the window
    parts: list                     # (team, id, x, y, facing, is_head) in block order
    hedges: list                    # 8 rows x 7 tokens: row r is the north edge of window row r (row 7 = south of row 6)
    vedges: list                    # 7 rows x 8 tokens: col c is the west edge of window col c (col 7 = east of col 6)
    ended: bool = False


def parse_spawn(text):
    kv = {}
    for ln in text.strip().splitlines():
        p = ln.split()
        if p:
            kv[p[0]] = p[1:]
    return Spawn(int(kv['ID'][0]), kv['TEAM'][0], int(kv['MAP'][0]), int(kv['MAP'][1]), int(kv['UNIT_LIMIT'][0]))


def _lines(text):
    for ln in text.splitlines():
        if '#' in ln:
            ln = ln[:ln.index('#')]
        p = ln.split()
        if p:
            yield p


def parse_block(text):
    it = _lines(text if isinstance(text, str) else text.decode())
    first = next(it)
    if first[0] == 'ENDGAME':
        return Block(-1, '', 0, 0, [], None, [], [], [], [], ended=True)
    rnd = int(first[1])
    d = next(it)[1]
    length = int(next(it)[1])
    units = int(next(it)[1])
    k = int(next(it)[1])
    msgs = [int(next(it)[0]) for _ in range(k)]
    p = next(it)
    echoes = None
    if p[0] == 'ECHOES':
        echoes = tuple(int(v) for v in p[1:6])
        p = next(it)
    tiles = []
    for i in range(VISION * VISION):
        if i:
            p = next(it)
        tiles.append((int(p[0]), int(p[1]), int(p[2]), int(p[3])))
    m = int(next(it)[1])
    parts = []
    for _ in range(m):
        q = next(it)
        parts.append((q[0], int(q[1]), int(q[2]), int(q[3]), q[4], int(q[5])))
    hedges = [next(it) for _ in range(VISION + 1)]
    vedges = [next(it) for _ in range(VISION)]
    return Block(rnd, d, length, units, msgs, echoes, tiles, parts, hedges, vedges)


def format_block(b):
    """Inverse of parse_block (canonical whitespace) - used by the rebuild parity test."""
    out = [f'ROUND {b.round}', f'DIR {b.dir}', f'LENGTH {b.length}', f'UNIT_COUNT {b.unit_count}', f'NUM_MSGS {len(b.msgs)}']
    out += [str(m) for m in b.msgs]
    if b.echoes is not None:
        out.append('ECHOES ' + ' '.join(map(str, b.echoes)))
    out += [f'{x} {y} {p} {c}' for x, y, p, c in b.tiles]
    out.append(f'DRAGON_BODIES {len(b.parts)}')
    out += [f'{t} {i} {x} {y} {f} {h}' for t, i, x, y, f, h in b.parts]
    out += [' '.join(r) for r in b.hedges]
    out += [' '.join(r) for r in b.vedges]
    return '\n'.join(out) + '\n'


def canon(text):
    """Canonical text of a raw block (comment-stripped, single-spaced, no blank lines)."""
    return '\n'.join(' '.join(p) for p in _lines(text if isinstance(text, str) else text.decode())) + '\n'

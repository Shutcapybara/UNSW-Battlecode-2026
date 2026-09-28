"""Rebuild the exact engine round block a dragon received, from replay state.

Mirrors upstream protocol.cc BuildRoundBlock (eb54612).  `proto3` controls
64-bit message readability and the ECHOES line (negotiated per process, not
recorded in replays)."""
import recon

LET = {'north': 'N', 'east': 'E', 'south': 'S', 'west': 'W'}


def edge_char(e):
    if e is None:
        return '.'
    return 'w' if e[0] == 'k' else str(e[1])


def build_block(g, d, proto3):
    b = g.board
    hx, hy = d.body[0]
    out = []
    msgs = [m[0] for m in d.inbox if proto3 or m[0] <= 0xFFFFFFFF]
    out.append(f'ROUND {g.round}')
    out.append(f'DIR {LET[d.facing]}')
    out.append(f'LENGTH {len(d.body)}')
    out.append(f'UNIT_COUNT {g.unit_count(d.team)}')
    out.append(f'NUM_MSGS {len(msgs)}')
    out += [str(m) for m in msgs]
    if proto3:
        out.append('ECHOES ' + ' '.join(str(x) for x in d.echo))
    tiles = [[b.wrap(hx + c - 3, hy + r - 3) for c in range(7)] for r in range(7)]
    for r in range(7):
        for c in range(7):
            t = tiles[r][c]
            cd = g.countdown.get(t, 0) if t in getattr(g, 'beds', b.gaps) else -1
            out.append(f'{t[0]} {t[1]} {1 if t in g.pearls else 0} {cd}')
    bodies = []
    for o in sorted(g.dragons.values(), key=lambda x: x.id):
        if not o.alive:
            continue
        for i, t in enumerate(o.body):
            if g.in_vision((hx, hy), t):
                bodies.append(f'{o.team} {o.id} {t[0]} {t[1]} {LET[g.seg_facing(o, i)]} {1 if i == 0 else 0}')
    out.append(f'DRAGON_BODIES {len(bodies)}')
    out += bodies
    for r in range(8):
        row = []
        for c in range(7):
            t = tiles[r][c] if r < 7 else tiles[6][c]
            row.append(edge_char(b.edge(t, 'north' if r < 7 else 'south')))
        out.append(' '.join(row))
    for r in range(7):
        row = []
        for c in range(8):
            t = tiles[r][c] if c < 7 else tiles[r][6]
            row.append(edge_char(b.edge(t, 'west' if c < 7 else 'east')))
        out.append(' '.join(row))
    return out

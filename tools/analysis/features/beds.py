"""Recover bed timings for server replays.

Server replays blank the bed timings (every TILE line reads `x y 0 0`) and may be dealt in another orientation. The
public maps in REPO/maps carry the real `minGap maxGap`. We find the flip that maps the local map's kelp layout onto the
replay's (cell by cell, blocked directions must match exactly) and carry the beds across. No match = no beds (NaN features).
"""
import functools
from pathlib import Path

from .frame import terrain

MAPS = Path(__file__).resolve().parents[3] / 'maps'
# direction index N E S W; a flip in x swaps E/W, a flip in y swaps N/S
FLIPS = {'id': (False, False), 'fx': (True, False), 'fy': (False, True), 'fxy': (True, True)}


@functools.lru_cache(maxsize=None)
def _local(name, W, H):
    out = []
    for p in sorted(MAPS.glob('*.map')):
        text = p.read_text()
        if f'MAP_NAME {name}' not in text.splitlines():
            continue
        m, w, h, nbr, beds, _ = terrain(text)
        if (w, h) == (W, H):
            out.append((p.name, nbr, beds))
    return out


def _blocked(nbr):
    return {c: tuple(n is None for n in v) for c, v in nbr.items()}


def resolve(g):
    """returns (beds dict, source string); beds keyed by the replay's own cells"""
    if g['beds']:
        return g['beds'], 'replay'
    W, H = g['W'], g['H']
    target = _blocked(g['nbr'])
    for fname, nbr, beds in _local(g['map'], W, H):
        src = _blocked(nbr)
        for tag, (fx, fy) in FLIPS.items():
            ok = True
            for (x, y), bl in src.items():
                c = ((W - 1 - x) if fx else x, (H - 1 - y) if fy else y)
                n, e, s, w = bl
                if fx:
                    e, w = w, e
                if fy:
                    n, s = s, n
                if target.get(c) != (n, e, s, w):
                    ok = False
                    break
            if ok:
                return {((W - 1 - x) if fx else x, (H - 1 - y) if fy else y): v for (x, y), v in beds.items()}, f'{fname}:{tag}'
    return {}, 'unresolved'

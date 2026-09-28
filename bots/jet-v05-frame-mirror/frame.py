"""Jet c23 frame wrapper: play the game in a transformed frame (identity, x-mirror, y-mirror or 180-degree rotation).

The engine sees true coordinates and directions; the policy sees the transformed world. Any of the four frames is a
valid game world; which one a biased policy plays best in is an empirical, per-map question. All dragons of a team
must use the same frame (sonar payloads carry coordinates), so the choice depends only on (W, H, team).
FRAMES maps (W, H, team) -> frame; DEFAULT applies otherwise. team is "A" or "B" as sent by the engine.
"""
FRAMES = {}
DEFAULT = {"A": "id", "B": "id"}
try:
    from frame_config import FRAMES as _F, DEFAULT as _D
    FRAMES.update(_F); DEFAULT.update(_D)
except ImportError:
    pass

MODE = ["id"]
LOGGED = [False]
W = H = 0
_DM = {"id": {}, "fx": {"E": "W", "W": "E"}, "fy": {"N": "S", "S": "N"}, "r": {"N": "S", "S": "N", "E": "W", "W": "E"}}


def choose(w, h, team):
    global W, H
    W, H = w, h
    MODE[0] = FRAMES.get((w, h, team), DEFAULT.get(team, "id"))


def xy(x, y):
    m = MODE[0]
    if m == "id":
        return x, y
    if m == "fx":
        return W - 1 - x, y
    if m == "fy":
        return x, H - 1 - y
    return W - 1 - x, H - 1 - y


def dirs(s):
    d = _DM[MODE[0]]
    return "".join(d.get(ch, ch) for ch in s)


def tile(t):
    x, y = xy(t[0], t[1])
    return (x, y) + tuple(t[2:])


def body(b):
    b = list(b)
    b[2], b[3] = (str(v) for v in xy(int(b[2]), int(b[3])))
    b[4] = dirs(b[4])
    return b


def hedges(rows):
    m = MODE[0]
    if m in ("fy", "r"):
        rows = rows[::-1]
    if m in ("fx", "r"):
        rows = [r[::-1] for r in rows]
    return rows


def vedges(rows):
    return hedges(rows)  # 7x8: row flip for fy/r, column flip for fx/r (same index algebra)


def tiles(ts):
    """Transform the 7x7 view and restore the engine's row-major order in the new frame (index 24 = head)."""
    m = MODE[0]
    out = [tile(t) for t in ts]
    if m in ("fy", "r"):
        out = [out[7 * (6 - r) + c] for r in range(7) for c in range(7)]
    if m in ("fx", "r"):
        out = [out[7 * r + (6 - c)] for r in range(7) for c in range(7)]
    return out

"""Jet frame wrapper (Jet lineage, Claude): run any text-protocol bot in host/ inside a transformed frame.

The host sees the game through one of four frames: id, fx (x -> W-1-x, E<->W), fy (y -> H-1-y, N<->S) or r (both).
Transformed turn by turn at the text level: the facing line, tile lines (coordinates and 7x7 row-major order),
body lines (coordinates and direction letters) and edge rows. On the way out, MOVE and SONAR directions are mapped
back. The frame depends only on (W, H, team) from the init block, so all dragons of a team agree and sonar payloads
stay consistent. Table: frame_config.py (FRAMES[(W, H, team)] -> frame; DEFAULT[team]).
Built by tools/jet/make_frame.py; see bots/jet-v05-frame-mirror for the in-protocol version and the evidence.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from frame_config import FRAMES, DEFAULT  # noqa: E402

_in, _out = sys.stdin, sys.stdout
DM = {"id": {}, "fx": {"E": "W", "W": "E"}, "fy": {"N": "S", "S": "N"}, "r": {"N": "S", "S": "N", "E": "W", "W": "E"}}
ST = {"mode": "id", "W": 0, "H": 0, "logged": False}


def _d(s):
    m = DM[ST["mode"]]
    return "".join(m.get(c, c) for c in s)


def _xy(x, y):
    m, W, H = ST["mode"], ST["W"], ST["H"]
    if m in ("fx", "r"):
        x = W - 1 - x
    if m in ("fy", "r"):
        y = H - 1 - y
    return x, y


def _flip(rows):
    m = ST["mode"]
    if m in ("fy", "r"):
        rows = rows[::-1]
    if m in ("fx", "r"):
        rows = [r[::-1] for r in rows]
    return rows


def _toks():
    while True:
        line = _in.readline()
        if not line:
            return None
        t = line.split("#", 1)[0].split()
        if t:
            return t


def _line(t):
    return " ".join(t) + "\n"


class FrameIn:
    def __init__(self):
        self.q = []
        self.init = False

    def _block(self):
        if not self.init:
            a = _toks(); b = _toks(); c = _toks(); d = _toks()
            if a is None or d is None:
                return [_line(t) for t in (a, b, c, d) if t]
            ST["W"], ST["H"] = int(c[1]), int(c[2])
            ST["mode"] = FRAMES.get((ST["W"], ST["H"], b[1]), DEFAULT.get(b[1], "id"))
            self.init = True
            return [_line(a), _line(b), _line(c), _line(d)]
        h = _toks()
        if h is None:
            return []
        if h[0] == "ENDGAME" or ST["mode"] == "id":
            out = [_line(h)]
            if h[0] == "ENDGAME" or ST["mode"] == "id":
                return out
        out = [_line(h)]
        dr = _toks(); dr[1] = _d(dr[1]); out.append(_line(dr))
        out.append(_line(_toks())); out.append(_line(_toks()))  # length, units
        mc = _toks(); out.append(_line(mc))
        for _ in range(int(mc[1])):
            out.append(_line(_toks()))
        f = _toks()
        if f[0] == "ECHOES":
            out.append(_line(f)); f = _toks()
        tiles = [f] + [_toks() for _ in range(48)]
        tt = []
        for t in tiles:
            x, y = _xy(int(t[0]), int(t[1])); tt.append([str(x), str(y)] + t[2:])
        m = ST["mode"]
        if m in ("fy", "r"):
            tt = [tt[7 * (6 - r) + c] for r in range(7) for c in range(7)]
        if m in ("fx", "r"):
            tt = [tt[7 * r + (6 - c)] for r in range(7) for c in range(7)]
        out += [_line(t) for t in tt]
        bc = _toks(); out.append(_line(bc))
        for _ in range(int(bc[1])):
            b = _toks(); x, y = _xy(int(b[2]), int(b[3])); b[2], b[3] = str(x), str(y); b[4] = _d(b[4]); out.append(_line(b))
        out += [_line(t) for t in _flip([_toks() for _ in range(8)])]
        out += [_line(t) for t in _flip([_toks() for _ in range(7)])]
        return out

    def readline(self):
        if not self.q:
            if self.init and ST["mode"] == "id":
                return _in.readline()
            self.q = self._block()
            if not self.q:
                return ""
        return self.q.pop(0)

    def __getattr__(self, k):
        return getattr(_in, k)


class FrameOut:
    def __init__(self):
        self.buf = ""

    def write(self, s):
        if ST["mode"] == "id":
            return _out.write(s)
        self.buf += s
        while "\n" in self.buf:
            line, self.buf = self.buf.split("\n", 1)
            t = line.split(" ")
            if t[0] == "MOVE" and len(t) > 1:
                t[1] = _d(t[1])
                if not ST["logged"]:
                    _out.write("LOG ACT:frame:%s\n" % ST["mode"]); ST["logged"] = True
            elif t[0] == "SONAR" and len(t) > 2:
                t[1] = _d(t[1])
            _out.write(" ".join(t) + "\n")
        return len(s)

    def flush(self):
        _out.flush()

    def __getattr__(self, k):
        return getattr(_out, k)


def run():
    sys.stdin = FrameIn()
    sys.stdout = FrameOut()
    sub = os.path.join(HERE, "host")
    sys.path.insert(0, sub)
    os.chdir(sub)
    import main as bot  # noqa: E402  the host's own main.py
    bot.main()


if __name__ == "__main__":
    run()

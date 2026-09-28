"""Jet v01c: income-density doctrine dispatcher (Jet lineage, Claude).

One process per dragon.  Before playing, read the init block and the first
turn, and pick a doctrine from observable facts only:
  * rich view  = >= 20 visible fertile tiles, >= 8 of them empty, and >= 75%
                 of the empty ones respawn within 20 rounds (fast renewal), and
  (v01a counted pearl-carrying tiles as fast; newborns on a slow 30-70 board
   then switched doctrine mid-game. Fixed here.)
  * small board = WIDTH*HEIGHT <= 400 (a first draft used 625; newborns near
    isolated fast beds on devil/commons then switched, mixing doctrines).
Rule 'a': ladder iff rich view and small board (all processes alike).
Rule 'b': as 'a', but a round-0 root also needs team units == 1.
Doctrines: host/ = gavroche-v32-supported-divecap (verbatim);
ladder/ = ouroboros-v13-ladder (verbatim; its churn ladder runs on <= 625 tiles).
The consumed lines are replayed to the chosen bot, which then runs unchanged.
"""
import os, sys

RULE = 'a'
HERE = os.path.dirname(os.path.abspath(__file__))
_real = sys.stdin
buf = []


def tokens():
    while True:
        line = _real.readline()
        if not line:
            return None
        buf.append(line)
        t = line.split('#', 1)[0].split()
        if t:
            return t


class Replay:
    def __init__(self, lines):
        self.lines = lines

    def readline(self):
        if self.lines:
            return self.lines.pop(0)
        return _real.readline()

    def __getattr__(self, k):
        return getattr(_real, k)


def choose():
    t = tokens()
    if t is None:
        return 'host'
    tokens()  # team
    size = tokens(); tokens()  # size, unit limit
    area = int(size[1]) * int(size[2])
    r = tokens()
    if r is None or r[0] == 'ENDGAME':
        return 'host'
    rnd = int(r[1]); tokens(); tokens(); units = int(tokens()[1])
    for _ in range(int(tokens()[1])):
        tokens()
    f = tokens()
    if f[0] == 'ECHOES':
        f = tokens()
    tiles = [f] + [tokens() for _ in range(48)]
    fert = [x for x in tiles if int(x[3]) >= 0]
    empty = [x for x in fert if x[2] != '1']  # only empty beds show a renewal countdown
    fast = sum(1 for x in empty if int(x[3]) <= 20)
    rich = len(fert) >= 20 and len(empty) >= 8 and fast >= 0.75 * len(empty)
    ok = rich and area <= 400
    if RULE == 'b' and rnd == 0 and units != 1:
        ok = False
    return 'ladder' if ok else 'host'


def run():
    doctrine = choose()
    sys.stdin = Replay(buf)
    sys.stdout.write('LOG JET doctrine=%s\n' % doctrine)
    sub = os.path.join(HERE, doctrine)
    sys.path.insert(0, sub)
    os.chdir(sub)
    import main as bot  # the chosen doctrine's own main.py
    bot.main()


if __name__ == '__main__':
    run()

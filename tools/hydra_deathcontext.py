#!/usr/bin/env python3
"""Death context: why did a dragon die, and what did it believe?

Reads a packed .replay, counts deaths by cause per team, and prints the
actions/indicator leading into every hitSelf / hitOtherBody / hitWall
death of a chosen team. Same capnp reader as hydra_replay.py.

Usage: python3 tools/hydra_deathcontext.py FILE.replay [--team A] [--all]
       [--probe] prints raw payload words for layout checking
"""
import struct
import sys
from collections import deque, defaultdict

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hydra_replay import Rep, Obj  # noqa: E402

REASONS = ['hitWall', 'hitSelf', 'hitOtherBody', 'hitHeadToHead', 'noValidAction']
DIRLET = 'NESW'


def u16list(o, index):
    """A List(UInt16)-shaped pointer (capnp enum lists) at pointer slot."""
    got = o.r.ptr(o.s, o.a + o.dw + index)
    if got is None:
        return []
    s, a, tag = got
    if tag & 3 != 1:
        return []
    esize = (tag >> 32) & 7
    if esize == 7:  # composite struct list: elements are 1-word structs
        etag = o.r.word(s, a)
        count = (etag >> 2) & 0x3FFFFFFF
        edw, enp = (etag >> 32) & 0xFFFF, (etag >> 48) & 0xFFFF
        return [Obj(o.r, s, a + 1 + i * (edw + enp), edw, enp).num(0, 'H')
                for i in range(count)]
    if esize == 3:  # two-byte elements
        count = tag >> 35
        return [struct.unpack_from('<H', o.r.segments[s], a * 8 + i * 2)[0]
                for i in range(count)]
    return []


def action_text(act):
    which = act.num(0, 'H')
    if which == 0:
        return 'MOVE ' + ''.join(DIRLET[d] for d in u16list(act, 0))
    if which == 1:
        return 'SPLIT %d' % act.num(4, 'i')
    return 'NONE'


def main():
    path = sys.argv[1]
    team_filter = None
    if '--team' in sys.argv:
        team_filter = sys.argv[sys.argv.index('--team') + 1]
    show_all = '--all' in sys.argv
    probe = '--probe' in sys.argv

    rep = Rep(path)
    root = rep.obj(0, 0)
    team_of = {}
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            team_of[len(team_of)] = 'AB'[int(p[1])]

    rnd = -1
    hist = defaultdict(lambda: deque(maxlen=8))
    causes = defaultdict(int)

    for event in root.struct_list(3):
        kind = event.num(0, 'H')
        obj = event.child(0)
        if obj is None:
            continue
        if kind == 0:
            rnd = obj.num()
        elif kind == 1:
            pass
        elif kind == 4:
            ident = obj.num()
            trail = action_text(obj.child(0))
            hist[ident].append((rnd, trail))
        elif kind == 7:
            ident = obj.num()
            try:
                txt = obj.text(0)
            except Exception:
                txt = '?'
            if hist[ident]:
                r, a = hist[ident][-1]
                hist[ident][-1] = (r, a + ' [' + txt + ']')
        elif kind == 10:
            child = obj.num(4)
            team_of[child] = team_of[obj.num()]
        elif kind == 11:
            ident = obj.num()
            reason = obj.num(4, 'H')
            team = team_of.get(ident, '?')
            causes[(team, REASONS[reason] if reason < 5 else str(reason))] += 1
            interesting = reason in (0, 1, 2)
            if interesting or show_all:
                if team_filter is None or team == team_filter:
                    trail = ' | '.join('%d:%s' % (r, a) for r, a in hist[ident])
                    print('r%3d team %s id %2d %-13s %s' % (
                        rnd, team, ident,
                        REASONS[reason] if reason < 5 else str(reason), trail))
            hist.pop(ident, None)

    print('\ndeaths by cause:')
    for (team, reason), n in sorted(causes.items()):
        print('  team %s %-14s %d' % (team, reason, n))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Hydra replay stats: per-round pearls/population/positions from a packed replay.

Self-contained capnp packed-stream reader (spec-c far/double-far pointers).
Emits, per team and per round: population, cumulative pearls eaten, splits,
and head positions per live dragon.

Usage: python3 tools/hydra_replay.py FILE.replay [--every N] [--json] [--heads]
"""
import struct
import sys
from pathlib import Path


def unpack(data):
    """Capnp packed stream -> raw word stream."""
    out, i = bytearray(), 0
    n = len(data)
    while i < n:
        tag = data[i]
        i += 1
        word = bytearray(8)
        for bit in range(8):
            if tag & (1 << bit):
                word[bit] = data[i]
                i += 1
        out.extend(word)
        if tag == 0:
            out.extend(bytes(8 * data[i]))
            i += 1
        elif tag == 0xFF:
            count = 8 * data[i]
            i += 1
            out.extend(data[i:i + count])
            i += count
    return bytes(out)


class Rep:
    def __init__(self, path):
        raw = unpack(Path(path).read_bytes())
        count = struct.unpack_from('<I', raw, 0)[0] + 1
        sizes = struct.unpack_from('<' + 'I' * count, raw, 4)
        offset = ((count + 2) // 2) * 8
        self.segments = []
        for size in sizes:
            self.segments.append(raw[offset:offset + size * 8])
            offset += size * 8

    def word(self, s, w):
        return struct.unpack_from('<Q', self.segments[s], w * 8)[0]

    def ptr(self, s, w):
        """Resolve the pointer at (segment, word) -> (segment, word, tag).

        Returns the location of the struct/list CONTENT plus its pointer tag
        (for structs: the tag that describes data/pointer sections).
        """
        word = self.word(s, w)
        if word == 0:
            return None
        if word & 3 == 2:  # far pointer
            landing = (word >> 3) & 0x1FFFFFFF
            tseg = word >> 32
            if word & 4:  # double far
                w1 = self.word(tseg, landing)
                tag = self.word(tseg, landing + 1)
                dseg, doff = w1 >> 32, (w1 >> 3) & 0x1FFFFFFF
                return dseg, doff, tag
            return self.ptr(tseg, landing)
        return s, w + 1 + ((word >> 2) & 0x3FFFFFFF) - ((word >> 2) & 0x20000000) * 2, word

    def obj(self, s, w):
        got = self.ptr(s, w)
        if got is None:
            return None
        s, a, tag = got
        if tag & 3 != 0:
            raise ValueError('expected struct, got list')
        return Obj(self, s, a, (tag >> 32) & 0xFFFF, (tag >> 48) & 0xFFFF)


class Obj:
    def __init__(self, r, s, a, dw, np):
        self.r, self.s, self.a, self.dw, self.np = r, s, a, dw, np

    def num(self, offset=0, fmt='i'):
        if offset + struct.calcsize(fmt) > self.dw * 8:
            return 0
        return struct.unpack_from('<' + fmt, self.r.segments[self.s], self.a * 8 + offset)[0]

    def child(self, index):
        if index >= self.np or self.r.word(self.s, self.a + self.dw + index) == 0:
            return None
        return self.r.obj(self.s, self.a + self.dw + index)

    def text(self, index):
        got = self.r.ptr(self.s, self.a + self.dw + index)
        if got is None:
            return None
        s, a, tag = got
        if tag & 3 != 1 or (tag >> 32) & 7 != 2:
            raise ValueError('expected a byte list (Text)')
        count = tag >> 35
        raw = self.r.segments[s][a * 8:a * 8 + count]
        return raw[:-1].decode('utf-8', 'replace') if raw.endswith(b'\x00') else raw.decode('utf-8', 'replace')

    def struct_list(self, index):
        """List of same-layout structs -> list of Obj."""
        w = self.r.word(self.s, self.a + self.dw + index)
        if w == 0:
            return []
        got = self.r.ptr(self.s, self.a + self.dw + index)
        s, a, tag = got
        if tag & 3 != 1:
            raise ValueError('expected list')
        if (tag >> 32) & 7 != 7:
            raise ValueError('not a composite list')
        etag = self.r.word(s, a)
        count = (etag >> 2) & 0x3FFFFFFF
        edw, enp = (etag >> 32) & 0xFFFF, (etag >> 48) & 0xFFFF
        start = a + 1
        return [Obj(self.r, s, start + i * (edw + enp), edw, enp)
                for i in range(count)]


def analyse(path, every=5):
    rep = Rep(path)
    root = rep.obj(0, 0)
    version = root.num(0, 'I')
    if version not in (0, 1, 2):
        raise ValueError('unsupported replay version %d' % version)
    team_of, live = {}, set()
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            ident = len(team_of)
            team_of[ident] = 'AB'[int(p[1])]
            live.add(ident)

    series, split_lengths = [], []
    pearls = {'A': 0, 'B': 0}
    splits = {'A': 0, 'B': 0}
    deaths = {'A': 0, 'B': 0}
    turn_id = None
    round_num = -1
    updates = {}

    def snapshot():
        heads = [(team_of[i], updates[i]) for i in sorted(live) if i in updates]
        series.append(dict(
            round=round_num,
            pop={t: sum(team_of[i] == t for i in live) for t in 'AB'},
            pearls=dict(pearls), splits=dict(splits), deaths=dict(deaths),
            heads=heads))

    for event in root.struct_list(3):
        kind, obj = event.num(0, 'H'), event.child(0)
        ident = obj.num()
        if kind == 0:
            if round_num >= 0 and round_num % every == 0:
                snapshot()
            round_num = ident
        elif kind == 1:
            turn_id = ident
        elif kind == 3 and not obj.num(0, 'B'):
            pearls[team_of[turn_id]] += 1
        elif kind == 9:
            head, tail = obj.child(0), obj.child(1)
            updates[ident] = (head.num(), head.num(4), tail.num(), tail.num(4))
        elif kind == 10:
            team = team_of[ident]
            splits[team] += 1
            child = obj.num(4)
            team_of[child] = team
            live.add(child)
            try:
                pl = len(obj.struct_list(0))
                cl = len(obj.struct_list(1))
            except ValueError:
                pl = cl = 0
            split_lengths.append((round_num, team, pl, cl))
        elif kind == 11:
            deaths[team_of[ident]] += 1
            live.discard(ident)
    if round_num >= 0:
        snapshot()
    return dict(version=version, rounds=round_num + 1, series=series,
                split_lengths=split_lengths)


if __name__ == '__main__':
    argv = sys.argv[1:]
    every = int(argv[argv.index('--every') + 1]) if '--every' in argv else 5
    out = analyse(argv[0], every)
    if '--json' in argv:
        import json
        print(json.dumps(out))
    else:
        for snap in out['series']:
            print(f"r{snap['round']:4d} pop={snap['pop']['A']:3d}v{snap['pop']['B']:<3d} "
                  f"pearls={snap['pearls']['A']:4d}v{snap['pearls']['B']:<4d} "
                  f"splits={snap['splits']['A']:3d}v{snap['splits']['B']:<3d}")
        if out['split_lengths']:
            print('split lengths (round, team, parent, child) first 10:')
            for row in out['split_lengths'][:10]:
                print('   ', row)

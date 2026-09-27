"""Dependency-free reader for engine/replay.capnp v1/v2 packed match replays.

Reads only the fields needed for diagnostics. Supports near, far and double-far
pointers; rejects unknown replay versions instead of silently inventing metrics.
"""
import collections
import json
import struct
from pathlib import Path


def unpack(data):
    out, i = bytearray(), 0
    while i < len(data):
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
        elif tag == 255:
            count = 8 * data[i]
            i += 1
            out.extend(data[i:i + count])
            i += count
    return out


class Reader:
    def __init__(self, path):
        self.raw = unpack(Path(path).read_bytes())
        count = struct.unpack_from('<I', self.raw)[0] + 1
        sizes = struct.unpack_from('<' + 'I' * count, self.raw, 4)
        offset = ((count + 2) // 2) * 8
        self.segments = []
        for size in sizes:
            self.segments.append(memoryview(self.raw)[offset:offset + size * 8])
            offset += size * 8

    def word(self, segment, at):
        return struct.unpack_from('<Q', self.segments[segment], at * 8)[0]

    def pointer(self, segment, at):
        word = self.word(segment, at)
        if word & 3 == 2:
            landing, target_segment = (word >> 3) & 0x1fffffff, word >> 32
            if word & 4:
                far = self.word(target_segment, landing)
                tag = self.word(target_segment, landing + 1)
                return far >> 32, (far >> 3) & 0x1fffffff, tag
            return self.pointer(target_segment, landing)
        offset = (word >> 2) & 0x3fffffff
        if offset & 0x20000000:
            offset -= 0x40000000
        return segment, at + 1 + offset, word

    def object(self, segment, at):
        s, a, word = self.pointer(segment, at)
        return Obj(self, s, a, (word >> 32) & 65535, word >> 48)


class Obj:
    def __init__(self, reader, segment, at, data_words, pointers):
        self.r, self.s, self.a, self.dw, self.np = reader, segment, at, data_words, pointers

    def num(self, offset=0, fmt='i'):
        if offset + struct.calcsize(fmt) > self.dw * 8:
            return 0
        return struct.unpack_from('<' + fmt, self.r.segments[self.s], self.a * 8 + offset)[0]

    def child(self, index):
        return self.r.object(self.s, self.a + self.dw + index)

    def has(self, index):
        return index < self.np and self.r.word(self.s, self.a + self.dw + index) != 0

    def text(self, index):
        s, a, word = self.r.pointer(self.s, self.a + self.dw + index)
        return bytes(self.r.segments[s][a * 8:a * 8 + (word >> 35) - 1]).decode()

    def items(self, index):
        s, a, word = self.r.pointer(self.s, self.a + self.dw + index)
        if not word:
            return
        if (word >> 32) & 7 != 7:
            raise ValueError('Expected composite list')
        tag = self.r.word(s, a)
        dw, np = (tag >> 32) & 65535, tag >> 48
        count = (tag & 0xffffffff) >> 2
        for i in range(count):
            yield Obj(self.r, s, a + 1 + i * (dw + np), dw, np)


def analyse(path):
    reader = Reader(path)
    root = reader.object(0, 0)
    if root.num(0, 'I') not in (0, 1, 2):
        raise ValueError('Unsupported replay version')
    teams, live, indicators, decision_rounds = {}, set(), {}, {}
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            ident = len(teams)
            teams[ident] = 'AB'[int(p[1])]
            live.add(ident)
    stats = {t: dict(deaths=collections.Counter(), splits=0, pearls=0,
                     turns=0, max_points=0, timeouts=0, initiated_trades=0) for t in 'AB'}
    curve, deaths = [], []
    round_num, turn_id = -1, None
    for event in root.items(3):
        kind, obj = event.num(0, 'H'), event.child(0)
        ident = obj.num()
        if kind == 0:
            round_num = ident
            if round_num % 50 == 0:
                curve.append(dict(round=round_num, **{t: sum(teams[i] == t for i in live) for t in 'AB'}))
        elif kind == 1:
            turn_id = ident
        elif kind == 3 and not obj.num(0, 'B') and turn_id in live:
            # Empty tile during a move = one eaten pearl, before dragonUpdate.
            stats[teams[turn_id]]['pearls'] += 1
        elif kind == 4:
            st = stats[teams[ident]]
            st['turns'] += 1
            exceeded = bool(obj.num(4, 'B') & 1)
            if obj.has(1):
                usage = obj.child(1)
                st['max_points'] = max(st['max_points'], usage.num(0, 'Q'))
                exceeded |= bool(usage.num(8, 'B') & 1)
            st['timeouts'] += exceeded
        elif kind == 7:
            indicators[ident] = obj.text(0)
            decision_rounds[ident] = round_num
        elif kind == 10:
            child = obj.num(4)
            teams[child] = teams[ident]
            live.add(child)
            stats[teams[ident]]['splits'] += 1
        elif kind == 11:
            reason = ['wall', 'self', 'body', 'head-to-head', 'invalid'][obj.num(4, 'H')]
            stats[teams[ident]]['deaths'][reason] += 1
            if reason == 'head-to-head' and turn_id == ident:
                stats[teams[ident]]['initiated_trades'] += 1
            deaths.append(dict(round=round_num, id=ident, team=teams[ident], cause=reason,
                               actor=turn_id, decision_round=decision_rounds.get(ident),
                               indicator=indicators.get(ident)))
            live.discard(ident)
    # Use official final lengths rather than estimating sprint costs.
    result = root.child(4)
    for index, team in enumerate('AB'):
        standing = result.child(index)
        stats[team]['final'] = dict(units=standing.num(), longest=standing.num(4), total=standing.num(8))
        if standing.num() != sum(teams[i] == team for i in live):
            raise ValueError('Replay event population disagrees with official standings')
    return dict(rounds=round_num + 1, outcome=('AB'[result.num(6, 'H')] if result.num(4, 'H') == 1 else 'draw'),
                reason=['elimination', 'length'][result.num(2, 'H')], teams=stats,
                population=curve,
                death_events=deaths)


if __name__ == '__main__':
    import sys
    print(json.dumps(analyse(sys.argv[1]), indent=2))

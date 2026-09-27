"""Compare movement, split and sonar streams on matched frozen fixtures."""
import json
from pathlib import Path
import sys
from replay import Reader


def actions(path):
    r = Reader(path)
    root = r.object(0, 0)
    turn = -1
    for event in root.items(3):
        kind, obj = event.num(0, 'H'), event.child(0)
        if kind == 0:
            turn = obj.num()
        if kind == 4:
            if not obj.has(0):
                yield (turn, obj.num(), 'missing', None)
                continue
            a = obj.child(0)
            action_kind = a.num(0, 'H')
            if action_kind == 0:
                s, pos, word = r.pointer(a.s, a.a + a.dw)
                payload = bytes(r.segments[s][pos * 8:pos * 8 + (word >> 35) * 2]).hex()
            else:
                payload = a.num(4)
            yield (turn, obj.num(), action_kind, payload)
        elif kind == 12:
            # Compare data and pointed-to coordinates, not pointer offsets.
            # This handles both old UInt32 and current UInt64 sonar layouts.
            def data(o):
                return bytes(r.segments[o.s][o.a * 8:(o.a + o.dw) * 8]).hex()
            yield (turn, obj.num(), 'sonar', (data(obj), tuple(
                data(obj.child(i)) if obj.has(i) else None for i in range(obj.np))))


def indexed(folder):
    manifest = json.loads((folder / 'manifest.json').read_text())
    focus = manifest['focus']
    index = {}
    for row in json.loads((folder / 'results.json').read_text()):
        if row['outcome'] == 'error' or row.get('analysis_error') or not row.get('replay'):
            raise ValueError('Unhealthy fixture: ' + str(folder))
        side = 'A' if row['team_a'] == focus else 'B'
        opponent = row['team_b'] if side == 'A' else row['team_a']
        index[(row['map'], opponent, side)] = folder / row['replay']
    return index


def main():
    folders = [Path(p) for p in sys.argv[1:3]]
    manifests = [json.loads((p / 'manifest.json').read_text()) for p in folders]
    if manifests[0]['sandbox'] != manifests[1]['sandbox']:
        raise ValueError('Cannot compare native and sandbox streams')
    first, second = (indexed(p) for p in folders)
    common = sorted(first.keys() & second.keys())
    for board, opponent, side in common:
        for source in (board + '.map', opponent):
            if manifests[0]['hashes'][source] != manifests[1]['hashes'][source]:
                raise ValueError('Changed fixture: ' + source)
    failures = []
    for key in common:
        a, b = list(actions(first[key])), list(actions(second[key]))
        if a != b:
            diff = next(((x, y) for x, y in zip(a, b) if x != y), ('length', (len(a), len(b))))
            failures.append(dict(case=key, first_difference=diff))
    print(json.dumps(dict(cases=len(common), identical=len(common) - len(failures), differences=failures), indent=2))
    return bool(failures) or not common


if __name__ == '__main__':
    sys.exit(main())

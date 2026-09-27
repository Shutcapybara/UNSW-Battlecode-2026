"""Run with: PYTHONPYCACHEPREFIX=/tmp/leviathan-pycache python3 -m unittest discover -s tools/leviathan -p 'test_*.py' -v"""
import importlib.util
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BOT = ROOT / 'bots/leviathan-v07-local-cache'
sys.path.insert(0, str(BOT))
spec = importlib.util.spec_from_file_location('leviathan', BOT / 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
from replay import unpack, Reader
from lab import attach_metrics


def board():
    b = mod.Bot(0, 'A', 11, 11, 64)
    b.edges = {c: '.' for c in range(b.n * 2)}
    b.head, b.body, b.length = 60, [60, 59, 58], 3
    b.own, b.other = set(b.body), set()
    b.enemies, b.allies, b.counts = {}, {}, {}
    b.visible = set(range(b.n))
    b.seen = {c: 0 for c in range(b.n)}
    b.round = 10
    return b


class Geometry(unittest.TestCase):
    def test_torus(self):
        b = board()
        self.assertEqual(b.destinations(0), (110, 1, 11, 10))

    def test_portal_pair_and_cache_invalidation(self):
        b = board()
        b.learn(b.key(60, 1), '7')
        self.assertEqual(b.destinations(60)[1], -1)
        b.learn(b.key(20, 3), '7')
        self.assertEqual(b.destinations(60)[1], 20)
        self.assertEqual(b.destinations(20)[3], 60)
        b.learn(b.key(60, 0), '8')
        b.learn(b.key(90, 2), '8')
        self.assertEqual(b.destinations(60)[0], 90)
        self.assertEqual(b.destinations(90)[2], 60)

    def test_local_cache_matches_full_recomputation(self):
        b = board()
        # Warm every cache entry, then learn walls and both portal endpoints.
        for key, token in [(60, 'w'), (181, '7'), (141, '7'), (33, '8'), (90, '8')]:
            before = [b.destinations(c) for c in range(b.n)]
            b.learn(key, token)
            cached = [b.destinations(c) for c in range(b.n)]
            b.graph.clear()
            self.assertEqual(cached, [b.destinations(c) for c in range(b.n)])

    def test_tail_is_not_vacant_before_collision(self):
        b = board()
        b.body = [60, 61, 72, 71]
        b.length, b.own = 4, set(b.body)
        b.units = 64
        action, _ = b.decide()
        self.assertTrue(action.startswith('MOVE '))
        self.assertNotIn(action.split()[1][0], 'ES')

    def test_no_sprint_overspending(self):
        b = board()
        b.body, b.length, b.own = [60, 59], 2, {60, 59}
        action, _ = b.decide()
        self.assertEqual(len(action.split()[1]), 1)

    def test_stale_pearl_cannot_pay_for_extra_step(self):
        b = board()
        b.body, b.length, b.own = [60, 59], 2, {60, 59}
        b.pearls[61] = b.round - 1
        old = mod.P['sprint']
        try:
            mod.P['sprint'] = 1000  # force a sprint if the legality gate allows it
            action, _ = b.decide()
            self.assertEqual(len(action.split()[1]), 1)
        finally:
            mod.P['sprint'] = old

    def test_material_charged_for_sprint(self):
        b = board()
        b.role = 'hunter'
        _, features = b.evaluate((1, 1, 1), [63, 62, 61], {61, 62, 63}, {}, [0] * 4)
        self.assertEqual(features['pearl'], 1)

    def test_enemies_of_both_id_orders_threaten_next_turn(self):
        b = board()
        b.id = 10
        b.enemies, b.other = {64: 2}, {64}
        low = b.threats()
        b.enemies = {64: 20}
        self.assertEqual(low, b.threats())
        self.assertGreater(low[63], 0)

    def test_no_deliberate_trade_with_last_dragon(self):
        b = board()
        b.enemies, b.other, b.counts = {61: 1}, {61}, {1: 100}
        b.units = 1
        action, _ = b.decide()
        self.assertNotEqual(action, 'MOVE E')


class PackedReplay(unittest.TestCase):
    def test_single_far_pointer(self):
        r = Reader.__new__(Reader)
        # Segment 0 points to a landing pad in segment 1; one data word.
        r.segments = [memoryview(struct.pack('<Q', 2 | (1 << 32))),
                      memoryview(struct.pack('<QQ', 1 << 32, 42))]
        self.assertEqual(r.object(0, 0).num(), 42)

    def test_double_far_pointer(self):
        r = Reader.__new__(Reader)
        r.segments = [memoryview(struct.pack('<Q', 6 | (1 << 32))),
                      memoryview(struct.pack('<QQ', 2 | (2 << 32), 1 << 32)),
                      memoryview(struct.pack('<Q', 77))]
        self.assertEqual(r.object(0, 0).num(), 77)

    def test_negative_near_offset(self):
        r = Reader.__new__(Reader)
        r.segments = [memoryview(struct.pack('<QQ', 91, (1 << 32) | (0x3ffffffe << 2)))]
        self.assertEqual(r.object(0, 1).num(), 91)

    def test_absent_metrics_are_not_zero_usage(self):
        detail = {'teams': {'A': {}, 'B': {}}}
        attach_metrics(detail, 'team A points per turn: p50 20.1M  max 88.8M (10 turns)')
        self.assertEqual(detail['teams']['A']['max_points_estimate'], 88_800_000)
        self.assertIsNone(detail['teams']['B']['max_points_estimate'])

    def test_zero_run(self):
        self.assertEqual(unpack(bytes([0, 3])), bytes(32))

    def test_literal_run(self):
        data = bytes([255]) + b'abcdefgh' + bytes([1]) + b'ijklmnop'
        self.assertEqual(unpack(data), b'abcdefghijklmnop')

    def test_sparse_word(self):
        self.assertEqual(unpack(bytes([0b10000001, 3, 9])), bytes([3, 0, 0, 0, 0, 0, 0, 9]))


if __name__ == '__main__':
    unittest.main()

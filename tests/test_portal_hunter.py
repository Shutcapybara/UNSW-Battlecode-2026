"""Portal trip tests with a persistent bot and a small deterministic board."""
import subprocess
import sys
import unittest

BOT = sys.argv.pop(1)
_original_argv = sys.argv
sys.argv = ['test_bot.py', BOT]
from test_bot import turn
sys.argv = _original_argv


class Board:
    def __init__(self, pearls=(), spawns=None):
        self.head = (5, 5)
        self.body = [(5, 5), (5, 6)]
        self.pearls = set(pearls)
        self.spawns = dict(spawns or {})
        self.edges = {('v', 6, 5): '1', ('v', 8, 5): '1'}
        self.enemies = []
        self.round = 1
        self.facing = 'N'
        self.collected = 0
        self.crossings = 0
        self.history = ''

    def block(self):
        x, y = self.head
        rows = [f'ROUND {self.round}', f'DIR {self.facing}',
                f'LENGTH {len(self.body)}', 'UNIT_COUNT 1', 'NUM_MSGS 0']
        visible = {((x+dx) % 11, (y+dy) % 11)
                   for dy in range(-3, 4) for dx in range(-3, 4)}
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                p = ((x+dx) % 11, (y+dy) % 11)
                countdown = max(0, self.spawns[p]-self.round) if p in self.spawns else -1
                rows.append(f'{p[0]} {p[1]} {int(p in self.pearls)} {countdown}')
        parts = [f'A 0 {a} {b} {self.facing} {int(i == 0)}'
                 for i, (a, b) in enumerate(self.body) if (a, b) in visible]
        parts += [f'B {i+1} {a} {b} N 1' for i, (a, b) in enumerate(self.enemies)
                  if (a, b) in visible]
        rows.append(f'DRAGON_BODIES {len(parts)}')
        rows.extend(parts)
        for r in range(8):
            rows.append(' '.join(self.edges.get(('h', (x+c-3) % 11, (y+r-3) % 11), '.')
                                 for c in range(7)))
        for r in range(7):
            rows.append(' '.join(self.edges.get(('v', (x+c-3) % 11, (y+r-3) % 11), '.')
                                 for c in range(8)))
        return '\n'.join(rows) + '\n'

    def action(self):
        self.history += self.block()
        result = subprocess.run([BOT], input='ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n'+self.history,
                                text=True, capture_output=True, check=True, timeout=3)
        return result.stdout.splitlines()[-3]

    def move(self, action):
        assert action.startswith('MOVE ') and len(action) == 6, action
        d = action[-1]
        x, y = self.head
        dx, dy = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}[d]
        edge = ('h' if d in 'NS' else 'v', (x+(d == 'E')) % 11, (y+(d == 'S')) % 11)
        symbol = self.edges.get(edge, '.')
        assert symbol != 'w', 'hit wall'
        p = ((x+dx) % 11, (y+dy) % 11)
        if symbol != '.':
            other = next(e for e, s in self.edges.items() if s == symbol and e != edge)
            p = ((other[1]-(d == 'W')) % 11, (other[2]-(d == 'N')) % 11)
            self.crossings += 1
        assert p not in self.body, ('body collision', p, self.body)
        assert p not in self.enemies, 'enemy collision'
        self.body.insert(0, p)
        if p in self.pearls:
            self.pearls.remove(p)
            self.spawns.pop(p, None)
            self.collected += 1
        else:
            self.body.pop()
        self.head, self.facing = p, d
        self.round += 1
        for p, at in self.spawns.items():
            if at <= self.round:
                self.pearls.add(p)


class PortalHunter(unittest.TestCase):
    def late_action(self, round_number, **kwargs):
        block = turn(**kwargs).replace('ROUND 1\n', f'ROUND {round_number}\n', 1)
        result = subprocess.run([BOT], input='ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n'+block,
                                text=True, capture_output=True, check=True, timeout=3)
        return result.stdout.splitlines()[0]

    def test_growth_starts_exactly_at_round_400(self):
        self.assertEqual(self.late_action(399, length=6, pearls=[(6, 5)]), 'SPLIT 2')
        for round_number in (400, 401, 499):
            self.assertEqual(self.late_action(round_number, length=6, pearls=[(6, 5)]), 'MOVE E')

    def test_growth_avoids_hunting_enemy_heads(self):
        options = dict(length=6, units=3, other_heads=[('B', 6, 5)], pearls=[(4, 5)])
        self.assertEqual(self.late_action(399, **options), 'MOVE E')
        self.assertEqual(self.late_action(400, **options), 'MOVE W')

    def test_growth_avoids_contested_pearl(self):
        self.assertEqual(self.late_action(400, length=6, units=3,
                         other_heads=[('B', 7, 5)], pearls=[(6, 5), (4, 5)]), 'MOVE W')

    def test_growth_keeps_emergency_split_when_trapped(self):
        self.assertEqual(self.late_action(400, length=6, walls='NESW'), 'SPLIT 2')

    def finish_trip(self, board):
        for _ in range(18):
            board.move(board.action())
            if board.crossings == 2:
                # The reserved continuation must also avoid walls and bodies.
                board.move(board.action())
                board.move(board.action())
                return
        self.fail('did not return through the portal')

    def test_collects_multiple_pearls_and_returns_without_splitting(self):
        board = Board(pearls=[(8, 5), (8, 4), (7, 4)])
        self.assertEqual(board.action(), 'MOVE E')
        board.history = ''
        self.finish_trip(board)
        self.assertEqual(board.collected, 3)
        self.assertEqual(board.crossings, 2)

    def test_plans_for_pearls_not_yet_spawned(self):
        board = Board(spawns={(8, 4): 3, (7, 4): 4})
        self.finish_trip(board)
        self.assertEqual(board.collected, 2)

    def test_does_not_enter_for_spawns_beyond_horizon(self):
        board = Board(spawns={(8, 5): 100})
        self.assertNotEqual(board.action(), 'MOVE E')

    def test_no_entry_without_known_other_end(self):
        board = Board(pearls=[(8, 5)])
        del board.edges[('v', 8, 5)]
        self.assertNotEqual(board.action(), 'MOVE E')

    def test_no_entry_into_trapped_destination(self):
        board = Board(pearls=[(8, 5)])
        board.edges.update({('h', 8, 5): 'w', ('h', 8, 6): 'w', ('v', 9, 5): 'w'})
        self.assertNotEqual(board.action(), 'MOVE E')

    def test_no_entry_near_enemy(self):
        board = Board(pearls=[(8, 5)])
        board.enemies = [(8, 4)]
        self.assertNotEqual(board.action(), 'MOVE E')

    def test_rechecks_route_after_new_obstacle(self):
        board = Board(pearls=[(8, 5), (8, 4), (7, 4)])
        board.move(board.action())
        self.assertEqual(board.crossings, 1)
        # A newly observed wall blocks the old northward collection route.
        board.edges[('h', 8, 5)] = 'w'
        self.assertNotEqual(board.action(), 'MOVE N')
        board.history = board.history[:board.history.rfind('ROUND ')]
        self.finish_trip(board)


if __name__ == '__main__':
    unittest.main()

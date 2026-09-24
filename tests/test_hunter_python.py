"""Protocol and conservative combat regressions for Python Hunter snapshots."""
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = sorted(ROOT.glob('bots/hunter-v*/main.py'))
# The older fixture module consumes a command-line binary argument at import.
argv = sys.argv[:]
sys.argv = ['test_bot.py', 'unused']
from test_bot import turn
sys.argv = ['test_portal_hunter.py', 'unused']
from test_portal_hunter import Board
sys.argv = argv


def load(path):
    spec = importlib.util.spec_from_file_location('hunter', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def block_with_enemy(size, length=3, units=3, **kwargs):
    block = turn(length=length, units=units, other_heads=[('B', 7, 5)], **kwargs)
    extra = ''.join(f'B 1 7 {5 - index} W 0\n' for index in range(1, size))
    return block.replace('DRAGON_BODIES 2\n', f'DRAGON_BODIES {size + 1}\n').replace(
        'B 1 7 5 W 1\n', 'B 1 7 5 W 1\n' + extra)


def bot_for(module, *blocks):
    bot = module.Bot(io.StringIO('ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n' + ''.join(blocks)))
    bot.update()
    return bot


class PythonHunter(unittest.TestCase):
    def each(self):
        for path in VERSIONS:
            yield path, load(path)

    def test_larger_target_uses_multi_step_attack(self):
        for path, module in self.each():
            with self.subTest(version=path.parent.name):
                bot = bot_for(module, block_with_enemy(4))
                self.assertEqual(bot.attack_path(), 'EE')
                self.assertEqual(bot.body(False), 'MOVE EE')

    def test_equal_and_smaller_targets_remain_blocked_even_with_unit_lead(self):
        for path, module in self.each():
            for size in (2, 3):
                for units in (3, 10, 64):
                    with self.subTest(version=path.parent.name, size=size, units=units):
                        self.assertEqual(bot_for(module, block_with_enemy(size, units=units)).attack_path(), '')

    def test_distant_enemy_does_not_trigger_partial_attack(self):
        for path, module in self.each():
            with self.subTest(version=path.parent.name):
                self.assertEqual(bot_for(module, block_with_enemy(4, length=2)).attack_path(), '')

    def test_adjacent_larger_enemy(self):
        for path, module in self.each():
            block = block_with_enemy(4).replace('B 1 7 ', 'B 1 6 ')
            self.assertEqual(bot_for(module, block).attack_path(), 'E')

    def test_stale_enemy_size_cannot_authorize_attack(self):
        for path, module in self.each():
            bot = bot_for(module, block_with_enemy(4), block_with_enemy(2).replace('ROUND 1', 'ROUND 2'))
            bot.update()
            self.assertEqual(bot.attack_path(), '')

    def test_body_and_walls_block_attack(self):
        for path, module in self.each():
            bot = bot_for(module, block_with_enemy(4, walls='E'))
            self.assertEqual(bot.attack_path(), '')
            bot.set_edge(bot.head, 1, '.')
            bot.occupied.add(bot.pos(6, 5))
            self.assertEqual(bot.attack_path(), '')

    def test_unsuitable_head_is_not_a_route_to_larger_enemy(self):
        for path, module in self.each():
            bot = bot_for(module, block_with_enemy(4))
            q = bot.pos(6, 5)
            bot.heads[q] = 2
            bot.sizes[2] = 2
            bot.occupied.add(q)
            self.assertEqual(bot.attack_path(), '')

    def test_preserve_minimum_force(self):
        for path, module in self.each():
            bot = bot_for(module, block_with_enemy(4, units=2))
            self.assertNotEqual(bot.body(False), 'MOVE EE')

    def test_echoes_and_64_bit_status(self):
        for path, module in self.each():
            bot = bot_for(module, turn().replace('NUM_MSGS 0', 'NUM_MSGS 0\nECHOES 1 2 3 4 5'))
            self.assertEqual(bot.echoes, (1, 2, 3, 4, 5))
            status = (0xA7 << 56) | (6 << 38) | (5 << 32) | (5 << 26) | (1 << 10)
            if hasattr(module, 'pack_status'):
                status = module.pack_status(0, 6, 5, 5, 1)
            self.assertEqual(bot.action().splitlines()[1:5], [f'SONAR {d} {status}' for d in 'NESW'])

    def test_move_aside_preserves_other_status_channels(self):
        for path, module in self.each():
            bot = bot_for(module, turn(other_heads=[('A', 7, 5)]).replace('DIR N', 'DIR E'))
            lines = bot.action().splitlines()
            self.assertEqual(lines[2], 'SONAR E 1146242894')
            self.assertEqual(len(lines), 6)
            self.assertEqual(int(lines[1].split()[2]) >> 56, module.TAG >> 56)

    def test_late_growth_seeks_safe_pearl(self):
        for path, module in self.each():
            bot = bot_for(module, turn(pearls=[(6, 5)], units=64).replace('ROUND 1', 'ROUND 450'))
            self.assertEqual(bot.body(False), 'MOVE E')

    def test_protocol_multiple_turns_and_clean_eof(self):
        for path, module in self.each():
            result = subprocess.run([sys.executable, str(path)], input='ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n' + turn() * 2,
                                    capture_output=True, text=True, check=True, timeout=5)
            self.assertEqual(result.stdout.count('ENDTURN'), 2)
            self.assertEqual(result.stderr, '')

    def test_portal_round_trip_reserves_body(self):
        for path, module in self.each():
            bot = bot_for(module, turn(portals=[('v', 3, 4, '1'), ('v', 3, 6, '1')]))
            self.assertEqual(bot.destination(bot.head, 1), -1)
            q = bot.destination(bot.head, 1, False, True)
            self.assertEqual(q, bot.pos(8, 5))
            bot.occupied.add(q)
            self.assertIsNone(bot.advance(bot.initial_trip(), 1, set()))


class PortalTrips(unittest.TestCase):
    def test_collect_and_return_with_two_safe_exit_steps(self):
        for path in VERSIONS:
            with self.subTest(version=path.parent.name):
                module = load(path)
                board = Board(pearls=[(8, 5), (8, 4), (7, 4)])
                bot = bot_for(module, board.block())
                returned = False
                for step in range(18):
                    if step:
                        bot.stream = io.StringIO(board.block())
                        bot.update()
                    board.move(bot.action().splitlines()[0])
                    if board.crossings == 2:
                        returned = True
                        for _ in range(2):
                            bot.stream = io.StringIO(board.block())
                            bot.update()
                            board.move(bot.action().splitlines()[0])
                        break
                self.assertTrue(returned)
                self.assertEqual(board.collected, 3)

    def test_unknown_endpoint_and_threat_block_entry(self):
        for path in VERSIONS:
            module = load(path)
            board = Board(pearls=[(8, 5)])
            board.enemies = [(8, 4)]
            self.assertNotEqual(bot_for(module, board.block()).body(False), 'MOVE E')
            board.enemies = []
            del board.edges[('v', 8, 5)]
            self.assertNotEqual(bot_for(module, board.block()).body(False), 'MOVE E')


class PearlRouting(unittest.TestCase):
    def setUp(self):
        self.module = load(ROOT / 'bots/hunter-v06-pearl-routing/main.py')

    def test_teammate_behind_kelp_does_not_claim_pearl(self):
        bot = bot_for(self.module, turn(length=2, other_heads=[('A', 7, 4)], pearls=[(7, 5)]))
        self.assertFalse(bot.owns_pearl(bot.pos(7, 5), 2))
        bot.edges[bot.pos(7, 4)] = ['w'] * 4
        bot.friend_routes = None
        self.assertTrue(bot.owns_pearl(bot.pos(7, 5), 2))

    def test_reachable_closer_teammate_still_owns_pearl(self):
        bot = bot_for(self.module, turn(length=2, other_heads=[('A', 7, 4)], pearls=[(7, 5)]))
        self.assertFalse(bot.owns_pearl(bot.pos(7, 5), 2))

    def test_nearby_pearl_beats_distant_isolated_pearl(self):
        bot = bot_for(self.module, turn(length=2, pearls=[(6, 5), (2, 5)], other_heads=[('A', 5, 4)]))
        self.assertEqual(bot.forage(), 'MOVE E')

    def test_equal_route_tie_uses_id(self):
        bot = bot_for(self.module, turn(length=2, other_heads=[('A', 7, 4)]))
        self.assertTrue(bot.owns_pearl(bot.pos(6, 4), 1))
        bot.id = 5
        self.assertFalse(bot.owns_pearl(bot.pos(6, 4), 1))


class WideTeamState(unittest.TestCase):
    def setUp(self):
        self.module = load(ROOT / 'bots/hunter-v07-wide-team-state/main.py')
        self.combined = load(ROOT / 'bots/hunter-v08-pearl-wide-sonar/main.py')

    def test_lifetime_ids_do_not_alias(self):
        for module in (self.module, self.combined):
            for ident in (0, 63, 64, 128, 3449, 64000):
                message = module.pack_status(ident, 19, 5, 6, 499)
                self.assertLess(message, 1 << 64)
                self.assertEqual(module.unpack_status(message, 500, 11, 11),
                                 (ident, 19, 71, 499))

    def test_stale_future_and_invalid_messages_are_ignored(self):
        for module in (self.module, self.combined):
            pack, unpack = module.pack_status, module.unpack_status
            self.assertIsNone(unpack(pack(64, 6, 5, 5, 1), 22, 11, 11))
            self.assertIsNone(unpack(pack(64, 6, 5, 5, 30), 22, 11, 11))
            self.assertIsNone(unpack(pack(64, 6, 12, 5, 20), 22, 11, 11))
            self.assertIsNone(unpack(pack(64, 1, 5, 5, 20), 22, 11, 11))
            self.assertIsNone(unpack(1146242894, 22, 11, 11))

    def test_same_low_id_teammate_is_not_discarded_as_self(self):
        for module in (self.module, self.combined):
            self._check_same_low_id(module)

    def _check_same_low_id(self, module):
        message = module.pack_status(64, 10, 6, 5, 450)
        block = turn(length=6, units=3).replace('ROUND 1', 'ROUND 450').replace('NUM_MSGS 0', f'NUM_MSGS 1\n{message}')
        bot = bot_for(module, block)
        self.assertIn(64, bot.teammates)
        self.assertFalse(bot.growth())

    def test_out_of_order_message_does_not_overwrite_newer_length(self):
        for module in (self.module, self.combined):
            newer = module.pack_status(64, 4, 5, 5, 450)
            older = module.pack_status(64, 10, 5, 5, 449)
            block = turn().replace('ROUND 1', 'ROUND 450').replace('NUM_MSGS 0', f'NUM_MSGS 2\n{newer}\n{older}')
            bot = bot_for(module, block)
            self.assertEqual(bot.teammates[64][0], 4)


class TeamConfidence(unittest.TestCase):
    def setUp(self):
        self.module = load(ROOT / 'bots/hunter-v09-confidence-team-state/main.py')

    def teammate_block(self, round_number, body_segments=0, message=None):
        options = {'other_heads': [('A', 7, 5)]} if body_segments else {}
        block = turn(length=2, units=64, **options).replace('ROUND 1', f'ROUND {round_number}')
        if body_segments:
            block = block.replace('DRAGON_BODIES 2\n',
                                  f'DRAGON_BODIES {2 + body_segments}\n', 1)
            marker = 'A 1 7 5 W 1\n'
            tail = ''.join(f'A 1 7 {6 + offset} W 0\n'
                           for offset in range(body_segments))
            block = block.replace(marker, marker + tail, 1)
        if message is not None:
            block = block.replace('NUM_MSGS 0', f'NUM_MSGS 1\n{message}', 1)
        return block

    def test_visible_partial_body_does_not_refresh_expired_sonar_length(self):
        blocks = [self.teammate_block(400,
                  message=self.module.pack_status(1, 10, 7, 5, 400))]
        blocks.extend(self.teammate_block(round_number, body_segments=2)
                      for round_number in range(401, 422))
        bot = self.module.Bot(io.StringIO('ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n'))
        for block in blocks:
            bot.stream = io.StringIO(block)
            bot.update()
        self.assertEqual(bot.teammates[1][0], 10)  # historical report retained
        self.assertEqual(bot.teammate_estimate(1), (3, 'visible_lower_bound', 421))
        self.assertEqual(bot.active_team(), [(1, 3)])

    def test_unseen_teammate_expires_and_fresh_sonar_replaces_old_length(self):
        initial = self.teammate_block(400,
                  message=self.module.pack_status(1, 10, 7, 5, 400))
        bot = bot_for(self.module, initial)
        fresh = self.teammate_block(401,
                  message=self.module.pack_status(1, 4, 7, 5, 401))
        bot.stream = io.StringIO(fresh)
        bot.update()
        self.assertEqual(bot.teammate_estimate(1), (4, 'recent_sonar', 401))
        unseen = self.teammate_block(422)
        bot.stream = io.StringIO(unseen)
        bot.update()
        self.assertIsNone(bot.teammate_estimate(1))
        self.assertEqual(bot.active_team(), [])

    def test_current_visible_size_can_raise_a_recent_lower_bound(self):
        block = self.teammate_block(450, body_segments=4,
            message=self.module.pack_status(1, 3, 7, 5, 450))
        bot = bot_for(self.module, block)
        self.assertEqual(bot.teammate_estimate(1), (5, 'visible_lower_bound', 450))


class EnemyConfidence(unittest.TestCase):
    def setUp(self):
        self.module = load(ROOT / 'bots/hunter-v10-confidence-enemy-state/main.py')

    def test_enemy_size_is_labeled_as_visible_lower_bound(self):
        bot = bot_for(self.module, block_with_enemy(4))
        ident = next(iter(bot.enemies))
        self.assertEqual(bot.enemy_estimate(ident), (4, 'visible_lower_bound', 1))
        self.assertEqual(bot.enemy_pressure(), 4)
        bot.stream = io.StringIO(turn().replace('ROUND 1', 'ROUND 22'))
        bot.update()
        self.assertIsNone(bot.enemy_estimate(ident))
        self.assertEqual(bot.enemy_pressure(), 0)

    def test_enemy_size_decays_and_expires_after_lost_contact(self):
        bot = bot_for(self.module, block_with_enemy(4))
        ident = next(iter(bot.enemies))
        bot.stream = io.StringIO(turn().replace('ROUND 1', 'ROUND 5'))
        bot.update()
        self.assertEqual(bot.enemy_estimate(ident), (0, 'decayed_observation', 1))
        self.assertEqual(bot.enemy_pressure(), 0)


class LargeMapWork(unittest.TestCase):
    def test_bot_caches_only_local_edges_on_large_maps(self):
        module = load(ROOT / 'bots/hunter-v09-confidence-team-state/main.py')
        block = turn().replace('MAP 11 11', 'MAP 64 64')
        bot = bot_for(module, block)
        self.assertLess(len(bot.edges), 100)
        self.assertLess(len(bot.visits), 2)
        self.assertTrue(bot.action().startswith(('MOVE ', 'SPLIT ')))

    def test_portal_endpoints_survive_when_they_leave_current_vision(self):
        module = load(ROOT / 'bots/hunter-v09-confidence-team-state/main.py')
        board = Board(pearls=[(8, 5)])
        bot = bot_for(module, board.block())
        self.assertEqual(len(bot.portals['1']), 2)
        board.head, board.body = (0, 0), [(0, 0), (0, 1)]
        board.round += 1
        bot.stream = io.StringIO(board.block())
        bot.update()
        self.assertEqual(len(bot.portals['1']), 2)


class RouteAwareExploration(unittest.TestCase):
    def test_known_detour_replaces_manhattan_for_exploration_spacing(self):
        module = load(ROOT / 'bots/hunter-v11-route-distance-exploration/main.py')
        bot = bot_for(module, turn(length=2, other_heads=[('A', 7, 5)]))
        target, friend = bot.pos(6, 5), bot.pos(7, 5)
        self.assertEqual(bot.nearest_friend(target), 1)
        bot.set_edge(target, 1, 'w')
        bot.set_edge(friend, 3, 'w')
        bot.friend_dist.clear()
        bot.friend_routes = None
        self.assertEqual(bot.nearest_friend(target), 3)

    def test_v12_spacing_ignores_temporary_body_obstacles(self):
        module = load(ROOT / 'bots/hunter-v12-static-map-spacing/main.py')
        bot = bot_for(module, turn(length=2, other_heads=[('A', 7, 5)]))
        target, friend = bot.pos(6, 5), bot.pos(7, 5)
        bot.set_edge(target, 1, 'w')
        bot.set_edge(friend, 3, 'w')
        bot.occupied.update((bot.pos(6, 4), bot.pos(6, 6)))
        self.assertEqual(bot.nearest_friend(target), 3)

    def test_v13_uses_live_route_when_available(self):
        module = load(ROOT / 'bots/hunter-v13-hybrid-route-spacing/main.py')
        bot = bot_for(module, turn(length=2, other_heads=[('A', 7, 5)]))
        target = bot.pos(6, 5)
        self.assertEqual(bot.nearest_friend(target), 1)

    def test_v13_falls_back_to_static_route_around_temporary_bodies(self):
        module = load(ROOT / 'bots/hunter-v13-hybrid-route-spacing/main.py')
        bot = bot_for(module, turn(length=2, other_heads=[('A', 7, 5)]))
        target, friend = bot.pos(6, 5), bot.pos(7, 5)
        bot.set_edge(target, 1, 'w')
        bot.set_edge(friend, 3, 'w')
        bot.occupied.update((bot.pos(6, 4), bot.pos(6, 6)))
        self.assertEqual(bot.nearest_friend(target), 3)

if __name__ == '__main__':
    unittest.main()

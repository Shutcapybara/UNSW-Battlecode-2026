"""Mechanistic tests for Estuary's uncertainty, safety and donor constraints."""
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
BOT = ROOT / 'bots/leviathan-x03-estuary-roles'


@contextmanager
def colony(overrides=None):
    names = ('config', 'params', 'pearl_model', 'estuary', 'estuary_params', 'continuation', 'estuary_test_core')
    saved = {n: sys.modules.pop(n) for n in names if n in sys.modules}
    oldpath = sys.path[:]
    sys.path.insert(0, str(BOT))
    params = types.ModuleType('params')
    params.PARAMS = {'pearl.prepos': 1, 'pearl.confirmed_only': 1, 'estuary.enabled': 1, **(overrides or {})}
    sys.modules['params'] = params
    try:
        spec = importlib.util.spec_from_file_location('estuary_test_core', BOT / 'main.py')
        core = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = core
        spec.loader.exec_module(core)
        core.W = core.H = 11
        core.setup()
        core.ek = bytearray([1]) * (2 * core.NC)
        core.unk = bytearray(core.NC)
        core.RND, core.MY_ID, core.HEAD, core.LEN, core.UNITS = 400, 1, 60, 3, 8
        core.ROLE = core.GATHER
        core.trail = [58, 59, 60]
        core.POLICY = core.Colony(core)
        core.POLICY.budget[0] = 120
        yield core, core.POLICY
    finally:
        sys.path[:] = oldpath
        for n in names:
            sys.modules.pop(n, None)
        sys.modules.update(saved)


class Continuation(unittest.TestCase):
    def test_tail_collision_is_checked_before_release(self):
        with colony() as (c, p):
            from continuation import survives
            self.assertIs(survives([0, 1], lambda x: [0], set(), set(), 1, [20]), False)

    def test_growth_can_turn_a_cycle_into_a_trap(self):
        with colony():
            from continuation import survives
            neighbors = lambda x: [(x + 1) % 3]
            self.assertIs(survives([0, 1], neighbors, set(), set(), 5, [20]), True)
            self.assertIs(survives([0, 1], neighbors, set(), {2}, 5, [20]), False)

    def test_a_pearl_is_consumed_once_over_a_loop(self):
        with colony():
            from continuation import survives
            self.assertIs(survives([0, 1], lambda x: [(x + 1) % 4], set(), {2}, 12, [30]), True)

    def test_budget_or_unknown_is_not_a_proven_trap(self):
        with colony():
            from continuation import survives
            self.assertIsNone(survives([0, 1], lambda x: [2], set(), set(), 3, [0]))
            self.assertIsNone(survives([0, 1], lambda x: [-2, -1], set(), set(), 3, [30]))
            self.assertIs(survives([0, 1], lambda x: [-1], set(), set(), 3, [30]), False)

    def test_partial_newborn_body_is_not_treated_as_complete(self):
        with colony() as (c, p):
            c.LEN = 30
            c.ROLE = c.CROWN
            self.assertIsNone(p.move_survives([1], [59, 60, 61]))
            self.assertIsNone(p.child_survives(28))

    def test_split_child_checks_reversed_body_and_parent_obstruction(self):
        with colony() as (c, p):
            c.LEN = 4; c.trail = [57, 58, 59, 60]
            # Tail 57 is completely surrounded by the child neck, walls and
            # another body. A parent head escape does not rescue this child.
            c.occ = {46: (9, True, False), 68: (9, True, False), 56: (9, True, False)}
            self.assertIs(p.child_survives(2), False)


class RunnerBootstrap(unittest.TestCase):
    def test_exec_namespace_is_not_the_host_main_module(self):
        import io
        from unittest.mock import patch
        with colony():
            namespace = {'__name__': '__main__', '__file__': str(BOT / 'main.py')}
            with patch('sys.stdin', io.StringIO('ID 0\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n')):
                exec(compile((BOT / 'main.py').read_text(), str(BOT / 'main.py'), 'exec'), namespace)
            self.assertIs(namespace['POLICY'].c.P, namespace['P'])
            namespace['RND'] = 77
            self.assertEqual(namespace['POLICY'].c.RND, 77)


class Doctrine(unittest.TestCase):
    def test_region_counts_do_not_double_count_repeated_views(self):
        with colony() as (c, p):
            p.observed(60, True, True)
            p.observed(60, False, True)
            self.assertEqual(sum(p.known), 1)
            self.assertEqual(sum(p.beds), 1)

    def test_scout_retires_after_coverage_or_time(self):
        with colony() as (c, p):
            c.NC = 1024; c.RND = 100; p.coverage = 0.1
            self.assertGreater(p.mix()[2], 0)
            p.coverage = 0.9
            self.assertEqual(p.mix()[2], 0)
            p.coverage = 0.1; c.RND = 400
            self.assertEqual(p.mix()[2], 0)

    def test_banking_reduces_production_but_keeps_hunter_replacements(self):
        with colony() as (c, p):
            c.RND = 100; p.bank = p.progress(); early = p.population_target()
            c.RND = 410; p.bank = p.progress()
            self.assertLess(p.population_target(), early)
            self.assertFalse(p.split_allowed())
            c.ROLE = c.HUNT; c.UNITS = 3
            self.assertTrue(p.split_allowed())

    def test_due_bed_occupancy_has_cost_without_inventing_food(self):
        with colony() as (c, p):
            c.spawn_at = {61: 401}
            self.assertGreater(p.bed_cost([60, 61]), 0)
            self.assertEqual(c.simulate([1], c.trail)[2], 3)

    def test_largest_fresh_candidate_wins_tie_by_full_id(self):
        with colony() as (c, p):
            c.LEN = 8; c.MY_ID = 50000
            c.allies[49000] = (65, 8, c.GATHER, c.RND)
            p.bank = 0.5; p.elect()
            self.assertNotEqual(c.ROLE, c.CROWN)
            c.allies.clear(); p.elect()
            self.assertEqual(c.ROLE, c.CROWN)


class Communication(unittest.TestCase):
    def test_self_packet_preserves_lifetime_id(self):
        with colony() as (c, p):
            c.MY_ID = 50000; c.LEN = 300; c.ROLE = c.SCOUT
            packet = p.self_packet(); c.MY_ID = 1; c.hear(packet)
            self.assertEqual(c.allies[50000][:3], (60, 300, c.SCOUT))
            self.assertNotIn(50000 & 4095, c.allies)

    def test_crown_relay_keeps_original_timestamp(self):
        with colony() as (c, p):
            c.MY_ID = 50000; c.RND = 300; c.LEN = 30
            packet = p.crown_packet(3)
            c.MY_ID = 1; c.RND = 310; c.hear(packet)
            self.assertEqual(p.crowns[50000], (60, 30, 300))
            c.RND = 314; c.hear(packet)
            self.assertEqual(p.crowns[50000][2], 300)
            c.LEN = 8; c.ROLE = c.GATHER; p.elect()
            self.assertEqual(c.ROLE, c.CROWN)  # stale beacon cannot block election

    def test_old_enemy_report_is_not_refreshed_by_relay(self):
        with colony() as (c, p):
            c.RND = 300; packet = p.enemy_packet(65, 10, 60000, 3)
            c.RND = 310; c.hear(packet)
            self.assertNotIn(60000, c.enemies)

    def test_regional_packet_has_named_target_consumer(self):
        with colony() as (c, p):
            c.ROLE = c.GATHER; z = c.zone_of(60)
            before = p.region_reward(60)
            packet = c.pack(8, (2 << 50) | (z << 42) | (60 << 35) | (30 << 28) | c.RND)
            c.hear(packet)
            self.assertGreater(p.region_reward(60), before)

    def test_portal_ids_are_not_truncated_to_eight_bits(self):
        with colony() as (c, p):
            c.pends[500] = [10, 20]
            packet = c.portal_packet(500); c.pends.clear(); c.ek = bytearray(2*c.NC)
            c.hear(packet)
            self.assertEqual(c.epid[10], 500)
            self.assertEqual(c.pends[500], [10, 20])


class Donation(unittest.TestCase):
    @staticmethod
    def recipient(c, p):
        c.P['estuary.feed_period'] = 1
        p.crowns[9] = (62, 15, c.RND)
        c.occ[62] = (9, True, True, 0)

    def test_feed_requires_visible_recipient_and_recent_evidence(self):
        with colony() as (c, p):
            self.recipient(c, p)
            self.assertTrue(p.feed())
            c.occ.clear()
            self.assertFalse(p.feed())
            c.occ[62] = (9, True, True, 0); c.RND += 4
            self.assertFalse(p.feed())

    def test_minimum_force_cannot_be_sacrificed(self):
        with colony() as (c, p):
            self.recipient(c, p)
            c.UNITS = c.P['estuary.feed_reserve']
            self.assertFalse(p.feed())

    def test_enemy_near_crown_blocks_donation(self):
        with colony() as (c, p):
            self.recipient(c, p)
            c.enemies[20] = (64, c.RND, 2)
            self.assertFalse(p.feed())

    def test_distance_through_wall_is_not_delivery_access(self):
        with colony() as (c, p):
            self.recipient(c, p)
            c.ek[c.ekey(62, 3)] = 2
            self.assertFalse(p.feed())

    def test_hunters_keep_their_defensive_job(self):
        with colony() as (c, p):
            self.recipient(c, p)
            c.ROLE = c.HUNT
            self.assertFalse(p.feed())


if __name__ == '__main__':
    unittest.main()

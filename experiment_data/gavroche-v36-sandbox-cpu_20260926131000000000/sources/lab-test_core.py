"""Convergence gates: extraction, arrival timing, confirmed growth, ledger."""
import ast
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def bot(name, overrides=None):
    folder = ROOT / 'bots' / name
    names = ('config', 'params', 'pearl_model')
    saved = {k: sys.modules.pop(k) for k in names if k in sys.modules}
    if overrides is not None:
        params = types.ModuleType('params')
        params.PARAMS = overrides
        sys.modules['params'] = params
    old_path = sys.path[:]
    sys.path.insert(0, str(folder))
    try:
        spec = importlib.util.spec_from_file_location('isolated_bot', folder / 'main.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.path[:] = old_path
        for k in names:
            sys.modules.pop(k, None)
        sys.modules.update(saved)


def board(m):
    m.W = m.H = 11
    m.setup()
    m.RND, m.LEN, m.HEAD = 100, 3, 60
    m.ek = bytearray([1]) * (2 * m.NC)
    m.occ = {}
    m.trail = [58, 59, 60]


class Core(unittest.TestCase):
    def test_reference_functions_unchanged(self):
        def functions(name):
            tree = ast.parse((ROOT / 'bots' / name / 'main.py').read_text())
            return {n.name: ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name != 'load_params'}
        self.assertEqual(functions('ouroboros-v10-beacon'), functions('leviathan-v08-core'))

    def test_reference_parameters_unchanged(self):
        with bot('ouroboros-v10-beacon') as reference:
            p, rp = reference.P, reference.RP
        with bot('leviathan-v08-core') as core:
            self.assertEqual(core.P, p)
            self.assertEqual(core.RP, rp)

    def test_neutral_candidate_parameters(self):
        with bot('leviathan-v08-core') as base:
            p, rp = base.P, base.RP
        with bot('leviathan-v09-arrival', {}) as candidate:
            self.assertEqual({k: candidate.P[k] for k in p}, p)
            self.assertEqual(candidate.RP, rp)
            self.assertEqual(candidate.P['pearl.prepos'], 0)
            self.assertEqual(candidate.P['pearl.confirmed_only'], 0)

    def test_arrival_uses_current_turn_as_first_step(self):
        with bot('leviathan-v09-arrival', {}) as m:
            # Adjacent: countdown 1 is too early to step onto it now.
            self.assertEqual(m.arrival_value(100, 1, 101, 10, 4), 0)
            self.assertEqual(m.arrival_value(100, 2, 101, 10, 4), 10)
            self.assertEqual(m.arrival_value(100, 4, 104, 10, 4), 0)
            self.assertEqual(m.arrival_value(100, 4, 103, 10, 4), 10)

    def test_overdue_prediction_expires(self):
        with bot('leviathan-v09-arrival', {}) as m:
            self.assertGreater(m.arrival_value(100, 2, 99, 10, 4), 0)
            self.assertEqual(m.arrival_value(100, 2, 95, 10, 4), 0)

    def test_target_consumer_prefers_ready_on_arrival_bed(self):
        with bot('leviathan-v09-arrival', {}) as m:
            board(m)
            m.unk = bytearray(m.NC)
            m.spawn_at = {61: 110, 64: 101}
            self.assertEqual(m.choose_target({})[0], 61)
            m.P['pearl.prepos'] = 1
            self.assertEqual(m.choose_target({})[0], 64)

    def test_compact_option_leaves_open_map_target_unchanged(self):
        with bot('leviathan-v09-arrival', {}) as m:
            board(m)
            m.W = m.H = 32
            m.setup()
            m.ek = bytearray([1]) * (2 * m.NC)
            m.unk = bytearray(m.NC)
            m.spawn_at = {61: 110, 64: 101}
            before = m.choose_target({})
            m.P['pearl.prepos'] = 1
            self.assertEqual(m.choose_target({}), before)

    def test_predictions_never_grow_simulated_body(self):
        with bot('leviathan-v09-arrival', {}) as m:
            board(m)
            m.P['pearl.prepos'] = 1
            m.P['pearl.confirmed_only'] = 1
            m.spawn_at[61] = 100
            self.assertEqual(m.simulate([1, 1], m.trail)[2:4], (2, 0))

    def test_stale_pearl_growth_is_separate_ablation(self):
        with bot('leviathan-v09-arrival', {}) as m:
            board(m)
            m.pearls[61] = 90
            self.assertEqual(m.simulate([1, 1], m.trail)[2:4], (3, 1))
            m.P['pearl.confirmed_only'] = 1
            self.assertEqual(m.simulate([1, 1], m.trail)[2:4], (2, 0))
            m.seen[61] = 101
            m.pearls[61] = 100
            self.assertEqual(m.simulate([1, 1], m.trail)[2:4], (3, 1))

    def test_confirmed_sprint_does_not_enter_own_tail(self):
        with bot('leviathan-v09-arrival', {}) as m:
            board(m)
            m.P['pearl.confirmed_only'] = 1
            self.assertFalse(m.simulate([3], m.trail)[0])

    def test_cpu_percentiles_are_nullable(self):
        from lab import attach_metrics
        detail = {'teams': {'A': {}, 'B': {}}}
        attach_metrics(detail, 'team A points per turn: p50 29.2M  p99 48.1M  mean 30M  max 69.0M')
        self.assertEqual(detail['teams']['A']['p99_points_estimate'], 48_100_000)
        self.assertIsNone(detail['teams']['B']['p99_points_estimate'])


    def test_map_class_includes_625_tiles(self):
        from lab import map_class
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'board.map'
            path.write_text('MAP 25 25\nEND\n')
            self.assertEqual(map_class(path), 'compact')
            path.write_text('MAP 25 26\nEND\n')
            self.assertEqual(map_class(path), 'open')

    def test_error_ledger_does_not_count_as_loss(self):
        from lab import ledger_row
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'board.map'
            path.write_text('MAP 11 11\nEND\n')
            row = dict(map='arena', team_a='ours', team_b='opponent',
                       outcome='error', winner=None, rounds=None)
            entry = ledger_row(row, 'ours', 'base', '1', path)
            self.assertEqual(entry['result'], 'E')
            self.assertIsNone(entry['cpu_p99'])
            self.assertIsNone(entry['our_longest'])


if __name__ == '__main__':
    unittest.main()

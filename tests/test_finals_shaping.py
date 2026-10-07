"""Contract tests for bounded Heartbreaker potential shaping and team-round returns."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('finals_collect_shaping', ROOT / 'tools/finals/collect.py')
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)


class PotentialShaping(unittest.TestCase):
    def test_balanced_state_is_zero_and_seat_swap_negates_potential(self):
        a = dict(queen=8, longest=20, total=50, queen_alive=True, visited=80)
        b = dict(a)
        self.assertEqual(collect.heartbreaker_potential(a, b, 123, 48 * 24), 0.0)
        advantaged = dict(queen=12, longest=30, total=75, queen_alive=True, visited=100)
        behind = dict(queen=5, longest=18, total=46, queen_alive=True, visited=70)
        p_ab = collect.heartbreaker_potential(advantaged, behind, 220, 48 * 24)
        p_ba = collect.heartbreaker_potential(behind, advantaged, 220, 48 * 24)
        self.assertAlmostEqual(p_ab, -p_ba, places=12)
        self.assertGreater(p_ab, 0)

    def test_potential_stays_bounded_and_round_limit_uses_queen_tiebreak(self):
        a = dict(queen=40, longest=80, total=200, queen_alive=True, visited=400)
        b = dict(queen=0, longest=120, total=250, queen_alive=False, visited=700)
        self.assertLessEqual(abs(collect.heartbreaker_potential(a, b, 499, 48 * 24)), 1.0)
        self.assertGreater(collect.heartbreaker_potential(a, b, 499, 48 * 24), 0.0)
        self.assertGreater(collect.heartbreaker_potential(a, b, 0, 48 * 24), 0.0)

    def test_replay_snapshots_track_initial_queen_and_cumulative_unique_heads(self):
        frame = dict(W=8, H=8, last_round=2, rounds=[
            {0: ('A', ((0, 0), (0, 1))), 2: ('A', ((1, 0),)),
             1: ('B', ((7, 7), (7, 6))), 3: ('B', ((6, 7),))},
            {0: ('A', ((0, 1), (0, 2))), 2: ('A', ((2, 0),)),
             1: ('B', ((7, 6), (7, 5))), 3: ('B', ((5, 7),))},
            {0: ('A', ((0, 2), (0, 3))), 2: ('A', ((3, 0),)),
             1: ('B', ((7, 5), (7, 4))), 3: ('B', ((4, 7),))},
            {},
        ])
        a = collect.potentials_from_frame(frame, 'A', 2)
        b = collect.potentials_from_frame(frame, 'B', 2)
        self.assertEqual(a.shape, (3,))
        np.testing.assert_allclose(a, -b, atol=1e-12)

    def test_discounted_potential_difference_telescopes_to_start_constant(self):
        rounds = [0, 0, 1, 2, 2]
        potentials = [0.1, 0.25, -0.2]
        terminal, weights = collect.credit(rounds, 2, 1, 0.9)
        shaped, shaped_weights = collect.credit(rounds, 2, 1, 0.9,
                                                potentials=potentials, alpha=0.2)
        expected = np.asarray([1 * 0.9 ** (2 - r) - 0.2 * potentials[r] for r in rounds])
        np.testing.assert_allclose(shaped, expected, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(shaped_weights, weights)
        self.assertLessEqual(abs(shaped[0] - terminal[0]), 0.2)
        np.testing.assert_allclose(collect.credit(rounds, 2, 1, 0.9,
                                                  potentials=potentials, alpha=0.0)[0], terminal)

    def test_bad_potential_timeline_is_rejected(self):
        with self.assertRaises(ValueError):
            collect.credit([0, 1], 1, 1, 0.9, potentials=[0.2])
        with self.assertRaises(ValueError):
            collect.credit([0], 0, 1, 0.9, potentials=[np.nan])
        with self.assertRaises(ValueError):
            collect.credit([0], 0, 1, 0.9, potentials=[1.01])


if __name__ == '__main__':
    unittest.main()

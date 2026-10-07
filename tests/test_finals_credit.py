"""Terminal team credit across interleaved dragons, births and donor deaths."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('finals_collect', ROOT / 'tools/finals/collect.py')
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)


class Credit(unittest.TestCase):
    def test_interleaved_dragon_death_keeps_delayed_team_reward(self):
        # Donor 1 last acts in round 2, while another dragon and a newborn continue.
        rounds = [0, 0, 1, 1, 2, 2, 3, 3, 4]
        returns, weights = collect.credit(rounds, 4, 1, 0.5)
        np.testing.assert_allclose(returns, [.0625, .0625, .125, .125, .25, .25, .5, .5, 1])
        self.assertEqual(returns[4], .25)  # donor's credit survives its private trajectory ending
        for rnd in set(rounds):
            self.assertEqual(sum(weights[i] for i, r in enumerate(rounds) if r == rnd), 1)

    def test_elimination_round_limit_draw_and_round_gaps(self):
        for end in (8, 499):
            wins, _ = collect.credit([0, 3, 7], end, 1, .997)
            losses, _ = collect.credit([0, 3, 7], end, -1, .997)
            draws, _ = collect.credit([0, 3, 7], end, 0, .997)
            np.testing.assert_allclose(losses, -wins)
            np.testing.assert_array_equal(draws, [0, 0, 0])
            self.assertAlmostEqual(wins[1] / wins[0], .997 ** -3, places=5)
        with self.assertRaises(ValueError):
            collect.credit([10], 9, 1, .997)

    def test_inclusive_engine_round_limit_last_decision_gets_full_reward(self):
        returns, weights = collect.credit([498, 499], 499, 1, .997)
        np.testing.assert_allclose(returns, [.997, 1])


if __name__ == '__main__':
    unittest.main()

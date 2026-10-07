"""Swarm-independent team loss weights and one joint sonar decision per dragon turn."""
from pathlib import Path
import sys
import unittest
import numpy as np
import torch
from torch.distributions import Categorical

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/finals'))
from ppo import team_round_weights, log_prob_entropy
from model import Scorer


class PPO(unittest.TestCase):
    def test_loss_is_invariant_to_swarm_size_and_excludes_override_rows(self):
        ids = [0, 0, 0, 0, 1, 1, 1]
        rounds = [2, 2, 3, 3, 7, 7, 8]
        valid = [True, True, False, True, True, True, True]
        w = team_round_weights(ids, rounds, valid)
        self.assertEqual(w[2], 0)
        self.assertAlmostEqual(sum(w[:4]), 1)
        self.assertAlmostEqual(sum(w[4:]), 1)
        self.assertAlmostEqual(w[0] + w[1], w[3])
        # Ten identical dragons in the same round do not increase its weighted objective.
        small = team_round_weights([0, 0], [0, 1], [True, True])
        large = team_round_weights([0] * 11, [0] * 10 + [1], [True] * 11)
        self.assertAlmostEqual(float(np.dot(small, [2, 4])), float(np.dot(large, [2] * 10 + [4])), places=6)

    def test_four_rays_are_one_joint_probability_and_reward_weight(self):
        logits = torch.tensor([[[1., 2.], [2., 1.], [0., 0.], [3., -1.]]])
        dist = Categorical(logits=logits)
        selected = torch.tensor([[0, 1, 0, 0]])
        logp, entropy = log_prob_entropy(dist, selected, 'sonar')
        self.assertEqual(logp.shape, (1,))
        torch.testing.assert_close(logp, dist.log_prob(selected).sum(dim=1))
        torch.testing.assert_close(entropy, dist.entropy().sum(dim=1))
        model = Scorer()
        self.assertEqual(model(torch.zeros(2, 1193), torch.zeros(2, 4, 5, 32)).shape, (2, 4, 5))

    def test_joint_sampler_respects_masks_and_fixed_rays(self):
        model = Scorer()
        counts = [1, 2, 3, 1]
        rays = [np.zeros((n, 32), dtype=np.float32) for n in counts]
        selected = model.sample_rays(np.zeros(1193, dtype=np.int16), rays, np.random.default_rng(1))
        for n, (choice, logp) in zip(counts, selected):
            self.assertTrue(0 <= choice < n)
            self.assertAlmostEqual(logp, -np.log(n), places=6)


if __name__ == '__main__':
    unittest.main()

"""Shape, conditioning, and joint-update contracts for the spatial finals trainer."""
from pathlib import Path
import sys
import tempfile
import unittest
from itertools import islice

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/finals'))
from spatial_model import SpatialPolicy
from train_spatial import plateau_status, train_batch, update_sequence, warmstart, write_metrics


def synthetic_episode(n=32):
    x = np.zeros((n, 1193), dtype=np.int16)
    action_features = np.zeros((n, 12, 32), dtype=np.float32)
    action_features[..., 0] = 1
    action_features[:, 1, 0] = 0
    action_features[:, 1, 1] = 1
    action_features[:, 1, 6] = 1.0
    action_mask = np.zeros((n, 12), dtype=bool)
    action_mask[:, :2] = True
    sonar_features = np.zeros((n, 4, 5, 32), dtype=np.float32)
    sonar_features[..., 0] = 1
    sonar_features[:, :, 1, 0] = 0
    sonar_features[:, :, 1, 1] = 1
    sonar_features[:, :, 1, 3] = 1.0
    sonar_mask = np.zeros((n, 4, 5), dtype=bool)
    sonar_mask[:, :, :2] = True
    chosen_action = action_features[:, 0].copy()
    return dict(
        x=x,
        action_features=action_features,
        chosen_action_features=chosen_action,
        action_mask=action_mask,
        action=np.zeros(n, dtype=np.int64),
        action_logp=np.full(n, -np.log(2), dtype=np.float32),
        sonar_features=sonar_features,
        sonar_mask=sonar_mask,
        sonar=np.zeros((n, 4), dtype=np.int64),
        sonar_logp=np.full((n, 4), -np.log(2), dtype=np.float32),
        actor_valid=np.ones(n, dtype=bool),
        round=np.arange(n, dtype=np.int32),
        returns=np.tile([1.0, -1.0], n // 2).astype(np.float32),
    )


class SpatialModel(unittest.TestCase):
    def test_shared_encoder_and_candidate_head_shapes(self):
        policy = SpatialPolicy()
        x = torch.zeros(2, 1193, dtype=torch.int16)
        actions = torch.zeros(2, 5, 32)
        actions[..., 0] = 1
        rays = torch.zeros(2, 4, 5, 32)
        rays[..., 0] = 1
        action_context = torch.zeros(2, 32)
        action_context[:, 0] = 1
        context = policy.encode(x)
        self.assertEqual(tuple(context.shape), (2, 128))
        self.assertEqual(tuple(policy.action_head(context, actions).shape), (2, 5))
        self.assertEqual(tuple(policy.sonar_head(context, rays, action_context).shape), (2, 4, 5))
        self.assertEqual(tuple(policy.value(x).shape), (2,))

    def test_sampling_conditions_sonar_on_the_selected_action(self):
        policy = SpatialPolicy()
        x = np.zeros(1193, dtype=np.int16)
        actions = np.zeros((2, 32), dtype=np.float32)
        actions[:, 0] = 1
        actions[1, 0] = 0
        actions[1, 1] = 1
        chosen, action_logp = policy.action_view.sample(x, actions, np.random.default_rng(4))
        self.assertIn(chosen, (0, 1))
        self.assertTrue(np.isfinite(action_logp))
        rays = []
        for count in (1, 2, 3, 1):
            values = np.zeros((count, 32), dtype=np.float32)
            values[:, 0] = 1
            rays.append(values)
        selected = policy.sonar_view.sample_rays_conditioned(
            x, rays, actions[chosen], np.random.default_rng(5))
        self.assertEqual(selected[0][0], 0)
        self.assertEqual(selected[3][0], 0)
        for ray, (choice, logp) in zip(rays, selected):
            self.assertTrue(0 <= choice < len(ray))
            self.assertTrue(np.isfinite(logp))

    def test_warmstart_and_joint_ppo_update_both_heads(self):
        data = synthetic_episode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'episode.npz'
            np.savez_compressed(path, **data)
            policy = SpatialPolicy()
            clone = warmstart(policy, 'joint', [path], epochs=1, batch_size=8, seed=1)
            self.assertEqual(clone['mode'], 'joint')
            self.assertTrue(np.isfinite(clone['head_diagnostics']['action']['validation_loss']))
            self.assertTrue(np.isfinite(clone['head_diagnostics']['sonar']['validation_loss']))

        policy = SpatialPolicy()
        before_encoder = policy.encoder.fusion[0].weight.detach().clone()
        before_action = policy.action_head.scorer[-1].weight.detach().clone()
        before_sonar = policy.sonar_head.scorer[-1].weight.detach().clone()
        optimizer = torch.optim.Adam(policy.parameters(), lr=3e-4)
        report = train_batch(policy, optimizer, [(data, {}), (data, {})], 'joint',
                             np.random.default_rng(2), epochs=1, batch_size=8)
        self.assertEqual(report['active_action_decisions'], 64)
        self.assertEqual(report['active_sonar_rays'], 256)
        self.assertIn('actor_loss', report['ppo_epochs'][0])
        self.assertFalse(torch.equal(before_encoder, policy.encoder.fusion[0].weight))
        self.assertFalse(torch.equal(before_action, policy.action_head.scorer[-1].weight))
        self.assertFalse(torch.equal(before_sonar, policy.sonar_head.scorer[-1].weight))

    def test_monitor_needs_three_checkpoints_before_plateau_label(self):
        self.assertEqual(plateau_status([{'eval': {'paired_score_delta': 0.1}}])['monitor_trend'],
                         'insufficient_checkpoints')
        status = plateau_status([{'eval': {'paired_score_delta': 0.10}},
                                 {'eval': {'paired_score_delta': 0.11}},
                                 {'eval': {'paired_score_delta': 0.105}}])
        self.assertEqual(status['monitor_trend'], 'flat_on_fixed_monitor_plateau_candidate')

    def test_continuous_update_sequence_has_no_target_cap(self):
        self.assertEqual(list(islice(update_sequence(4, 10, True), 5)), [4, 5, 6, 7, 8])
        self.assertEqual(list(update_sequence(4, 6, False)), [4, 5])

    def test_progress_csv_reports_per_update_and_cumulative_terminal_reward(self):
        import csv
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            first = {'update': 1, 'training': {'wins': 1, 'draws': 0, 'losses': 0,
                                               'sampled_games': 1, 'terminal_reward_sum': 1.0,
                                               'mean_policy_return': 0.2, 'mean_terminal_return': 0.15,
                                               'mean_shaping_return': 0.05}}
            second = {'update': 2, 'training': {'wins': 0, 'draws': 1, 'losses': 0,
                                                'sampled_games': 1, 'terminal_reward_sum': 0.0}}
            write_metrics(output, first)
            write_metrics(output, second)
            with (output / 'progress.csv').open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(float(rows[1]['train_reward_sum']), 0.0)
            self.assertEqual(float(rows[1]['cumulative_train_reward']), 1.0)
            self.assertEqual(float(rows[1]['cumulative_train_score']), 0.75)
            self.assertEqual(float(rows[0]['mean_policy_return']), 0.2)
            self.assertEqual(float(rows[0]['mean_shaping_return']), 0.05)


if __name__ == '__main__':
    unittest.main()

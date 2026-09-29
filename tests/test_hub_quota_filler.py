"""Tests for the automatic top-10/dev quota planner."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools.hub import db, executor, quota_filler
from tools.hub.config import REPO_ROOT, load_config, set_quota_filler_enabled, write_default_config


class QuotaFillerTest(unittest.TestCase):
    def setUp(self):
        self.cfg = {
            'team': {'dev_opponents': [545, 752]},
            'budget': {'hourly_games': {'field': 60, 'dev': 60}},
            'quota_filler': {'top_n': 10, 'batch_games': 3, 'cycle_games': 10, 'include_ladder_devs': True},
        }
        self.ladder = [
            {'id': 7, 'rank': 4},
            {'id': 10, 'rank': 1}, {'id': 11, 'rank': 2}, {'id': 12, 'rank': 3},
            {'id': 13, 'rank': 5}, {'id': 14, 'rank': 6}, {'id': 15, 'rank': 7},
            {'id': 16, 'rank': 8}, {'id': 17, 'rank': 9}, {'id': 18, 'rank': 10},
            {'id': 19, 'rank': 11}, {'id': 545, 'rank': 15, 'dev': True},
        ]

    def test_targets_exclude_us_and_keep_dev_allowance_separate(self):
        field, dev = quota_filler.target_pools(self.cfg, self.ladder, 7)
        self.assertEqual(field, [10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
        self.assertEqual(dev, [545, 752])

    def test_batches_rotate_targets_and_maps(self):
        batches, state = quota_filler.plan_batches('field', [10, 11], [1, 2, 3, 4], 8, 3)
        self.assertEqual([(b['opponent'], b['map_ids']) for b in batches], [
            (10, [1, 2, 3]), (11, [4, 1, 2]), (10, [3, 4]),
        ])
        self.assertEqual(state['field_target'], 1)
        self.assertEqual(state['field_map'], 0)
        next_batches, _ = quota_filler.plan_batches('field', [10, 11], [1, 2, 3, 4], 3, 3, state)
        self.assertEqual(next_batches[0]['opponent'], 11)
        self.assertEqual(next_batches[0]['map_ids'], [1, 2, 3])

    def test_remaining_uses_full_hourly_cap_after_executor_work(self):
        quota = {'field': {'used': 45}, 'dev': {'used': 50}}
        self.assertEqual(quota_filler.hourly_remaining(self.cfg, quota, 'field', 5), 10)
        self.assertEqual(quota_filler.hourly_remaining(self.cfg, quota, 'dev', 0), 10)
        self.assertEqual(quota_filler.hourly_remaining(self.cfg, {'field': {'unknown': True}}, 'field'), 0)

    def test_toggle_persists_and_is_easy_to_reverse(self):
        root = Path(tempfile.mkdtemp())
        try:
            write_default_config(root)
            set_quota_filler_enabled(root, True)
            self.assertTrue(load_config(root)['quota_filler']['enabled'])
            set_quota_filler_enabled(root, False)
            self.assertFalse(load_config(root)['quota_filler']['enabled'])
        finally:
            shutil.rmtree(root)

    @unittest.skipIf(sys.platform == 'darwin', 'Mac deployment intentionally keeps its configured paths')
    def test_non_mac_defaults_follow_this_checkout(self):
        root = Path(tempfile.mkdtemp())
        try:
            cfg = load_config(root)
            self.assertEqual(cfg['paths']['repo'], str(REPO_ROOT))
            self.assertEqual(cfg['paths']['python'], sys.executable)
            self.assertEqual(cfg['paths']['key_file'], str(REPO_ROOT / '.battlecode-api-key'))
        finally:
            shutil.rmtree(root)

    def test_shadow_dispatch_paces_each_pool_to_one_cycle_slice_without_api_calls(self):
        root = Path(tempfile.mkdtemp())
        conn = db.connect(root)
        try:
            cfg = dict(self.cfg, quota_filler=dict(self.cfg['quota_filler'], enabled=True))
            snap = SimpleNamespace(team_id=7, active=9001, ladder=self.ladder,
                                   map_ids=list(range(1, 21)), history=[], now=0)
            db.kv_set(conn, 'control', 9001)
            summary = dict(mode='shadow', stop=None, dispatched=[], plan=[], deferred=[], attention=[])
            executor.dispatch_quota_fill(conn, root, cfg, snap, object(), 'test',
                                          {'field': {'used': 0, 'unknown': False, 'blocked_until': 0},
                                           'dev': {'used': 0, 'unknown': False, 'blocked_until': 0}}, summary)
            self.assertEqual(summary['quota_filler']['planned_games'], 20)
            self.assertEqual(summary['quota_filler']['dispatched_games'], 20)
            self.assertEqual(len(summary['plan']), 8)
            self.assertTrue(db.kv_get(conn, 'quota_filler_cursor'))
        finally:
            conn.close()
            shutil.rmtree(root)


if __name__ == '__main__':
    unittest.main()

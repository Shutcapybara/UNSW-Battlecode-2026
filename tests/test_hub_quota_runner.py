import tempfile
import time
import unittest
from pathlib import Path

from tests.test_hub_executor import FakeServer
from tools.hub import db, executor, quota_runner
from tools.hub.config import load_config


class QuotaRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.conn = db.connect(self.root)
        self.addCleanup(self.conn.close)
        self.cfg = load_config(self.root)
        self.cfg['quota_filler'].update(enabled=True, reserve_games={'field': 20, 'dev': 20})
        self.now = time.time()
        self.server = FakeServer(self.now)

    def run_cycle(self, **kwargs):
        return quota_runner.run_cycle(self.conn, self.root, self.cfg,
                                      self.server, now=self.now, **kwargs)

    def test_disabled_makes_no_api_calls(self):
        self.cfg['quota_filler']['enabled'] = False
        self.run_cycle(live=True)
        self.assertEqual(self.server.calls, [])

    def test_shadow_does_not_report_or_send_real_games(self):
        result = self.run_cycle()
        self.assertEqual(result['quota_filler']['planned_games'], 20)
        self.assertEqual(result['quota_filler']['dispatched_games'], 0)
        self.assertFalse(any(method == 'POST' for method, _ in self.server.calls))

    def test_repeated_cycles_preserve_reserve_and_never_activate(self):
        for _ in range(6):
            result = self.run_cycle(live=True)
            self.assertIsNone(result['stop'])
        counts = dict(self.conn.execute("SELECT pool,sum(count) FROM requests WHERE status='accepted' GROUP BY pool"))
        self.assertEqual(counts, {'dev': 40, 'field': 40})
        self.assertTrue(all(path == '/api/v1/battles' for method, path in self.server.calls if method == 'POST'))

    def test_lost_acknowledgement_is_reconciled_before_more_dispatch(self):
        self.server.fail_posts = 1
        first = self.run_cycle(live=True)
        self.assertIn('uncertain mutation', first['stop'])
        self.assertEqual(len(executor.open_intents(self.conn)), 1)
        second = self.run_cycle(live=True)
        self.assertIsNone(second['stop'])
        self.assertEqual(len(second['reconciled']), 1)
        self.assertEqual(executor.open_intents(self.conn), [])

    def test_fresh_lease_blocks_second_connection(self):
        token = quota_runner.acquire(self.conn)
        other = db.connect(self.root)
        try:
            self.assertIsNotNone(token)
            self.assertIsNone(quota_runner.acquire(other))
            self.conn.execute('UPDATE executor_lease SET expires_at=0')
            self.assertIsNotNone(quota_runner.acquire(other))
        finally:
            other.close()

    def test_mutation_boundary_rejects_activation_and_ranked(self):
        client = quota_runner.BattlesOnly(self.server)
        for path, body in [('/api/v1/submissions/1/activate', {}),
                           ('/api/v1/battles', {'ranked': True})]:
            with self.assertRaises(executor.Stop):
                client.post(path, body)
        self.assertEqual(self.server.calls, [])


if __name__ == '__main__':
    unittest.main()

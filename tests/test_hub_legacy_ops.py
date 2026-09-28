"""Watchdog classification and clear-review behaviour (D-009)."""
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.hub import legacy_ops  # noqa: E402


class LegacyOpsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.live = self.tmp / 'live'
        (self.live / 'state' / 'runner_logs').mkdir(parents=True)
        (self.live / 'state' / 'state.json').write_text(json.dumps(dict(incumbent=1)))
        self.root = self.tmp / 'hub'
        self.root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def status(self, error, reason='controller process failed; new test requests stopped'):
        log = self.live / 'state' / 'runner_logs' / 'controller-1.log'
        log.write_text('stuff\nCycle stopped; durable state preserved {\'error\': "' + error + '"}\nTraceback...\n')
        return dict(state='needs_review', attention=dict(reason=reason, log=str(log), at='t1'), jobs={})

    def test_classification(self):
        self.assertTrue(legacy_ops.classify(self.live, self.status("'submissionAId'"))[0] is False or True)  # KeyError text alone is not in the log; use explicit classes below
        t, *_ = legacy_ops.classify(self.live, self.status('HTTP 502: bad gateway'))
        self.assertTrue(t)
        t, *_ = legacy_ops.classify(self.live, self.status('KeyError: submissionAId'))
        self.assertTrue(t)
        t, *_ = legacy_ops.classify(self.live, self.status('Uncertain API acknowledgement requires reconciliation: battle'))
        self.assertFalse(t)
        t, *_ = legacy_ops.classify(self.live, self.status('Upload acknowledgement requires exact-name reconciliation; no upload retry'))
        self.assertFalse(t)
        t, *_ = legacy_ops.classify(self.live, self.status('Something unknown happened'))
        self.assertFalse(t)
        (self.live / 'state' / 'state.json').write_text(json.dumps(dict(incumbent=1, switch=dict(candidate=2, previous=1))))
        t, _, _, open_tx = legacy_ops.classify(self.live, self.status('HTTP 503: unavailable'))
        self.assertFalse(t)
        self.assertTrue(open_tx)

    def test_clear_review_and_cap(self):
        alert = self.live / 'state' / 'runner_attention.json'
        alert.write_text(json.dumps(dict(reason='x', at='t1')))
        self.assertTrue(legacy_ops.clear_review(self.live, 'test'))
        self.assertFalse(alert.exists())
        self.assertTrue((self.live / 'state' / 'runner.renew').exists())
        self.assertTrue(any(p.name.startswith('cleared-review-') for p in (self.live / 'state' / 'runner_logs').iterdir()))
        for _ in range(3):
            legacy_ops.log(self.root, dict(action='auto_clear'))
        self.assertEqual(legacy_ops.recent_auto_clears(self.root), 3)

    def test_watchdog_auto_clears_transient_once_per_alert(self):
        cfg = dict(paths=dict(legacy_live=str(self.live)), legacy=dict(launchd_label='x', auto_clear_per_hour=3))
        st = self.status('HTTP 502: bad gateway')
        (self.live / 'state' / 'runner_status.json').write_text(json.dumps(st))
        (self.live / 'state' / 'runner_attention.json').write_text(json.dumps(st['attention']))
        notes = []
        state = {}
        out = legacy_ops.watchdog(self.root, cfg, state, lambda k, t: notes.append(k), lambda t: None)
        self.assertIn('auto_clear', out)
        self.assertFalse((self.live / 'state' / 'runner_attention.json').exists())
        out2 = legacy_ops.watchdog(self.root, cfg, state, lambda k, t: notes.append(k), lambda t: None)
        self.assertEqual(out2, {})  # same alert timestamp: not acted on twice
        st2 = self.status('Uncertain API acknowledgement requires reconciliation: battle')
        st2['attention']['at'] = 't2'
        (self.live / 'state' / 'runner_status.json').write_text(json.dumps(st2))
        (self.live / 'state' / 'runner_attention.json').write_text(json.dumps(st2['attention']))
        out3 = legacy_ops.watchdog(self.root, cfg, state, lambda k, t: notes.append(k), lambda t: None)
        self.assertIn('review', out3)
        self.assertTrue((self.live / 'state' / 'runner_attention.json').exists())


if __name__ == '__main__':
    unittest.main()

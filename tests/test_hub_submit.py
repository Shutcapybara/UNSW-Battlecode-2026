"""submit_check (D-056 §B): an upload without activation leaves the prior active submission active."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'tests'))
from tools.hub import actuator, db, executor  # noqa: E402
from tools.hub.config import load_config  # noqa: E402
from test_hub_executor import FakeServer  # noqa: E402

INC = 9508


class SubmitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'
        self.root.mkdir()
        self.mirror = self.tmp / 'hub-state'
        (self.root / 'hub.toml').write_text(f'[paths]\nrepo = "{self.tmp}"\nlegacy_live = "{self.tmp}/live"\nmirror = "{self.mirror}"\n[notify]\nosascript = false\n[team]\nid = 7\n')
        self.cfg = load_config(self.root)
        self.now = 1_790_600_000 + 25 * 60   # outside the even-hour blackout
        self.server = FakeServer(self.now)
        self.server.auto_activate_upload = True
        self.conn = db.connect(self.root)
        executor.ensure_columns(self.conn)
        archive = self.tmp / 'newbot.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            z.writestr('main.py', 'print(1)\n')
        files = {'main.py': hashlib.sha256(b'print(1)\n').hexdigest()}
        db.upsert(self.conn, 'candidates', dict(name='newbot', fingerprint='b' * 64, code_fingerprint='c', lineage='x', status='runtime_ok', priority=100,
                                                language='python', archive_path=str(archive), source_files=json.dumps(files)), 'name')
        self.conn.close()
        self.p = patch.object(actuator.time, 'time', lambda: self.now); self.p.start()

    def tearDown(self):
        self.p.stop()
        shutil.rmtree(self.tmp)

    def submit(self, **kw):
        ctl = self.mirror / 'control'
        ctl.mkdir(parents=True, exist_ok=True)
        (ctl / 'submit.json').write_text(json.dumps(dict(candidate='newbot', by='test/daichi', **kw)))
        actuator.submit_check(self.root, self.cfg, {}, self.server, lambda *a: None)
        self.assertFalse((ctl / 'submit.json').exists())
        return json.loads((ctl / 'submit.done.json').read_text())

    def test_auto_activation_is_undone(self):
        out = self.submit(activate=False)
        self.assertEqual(out.get('upload'), 'uploaded', out)
        self.assertEqual(out['active_before'], INC)
        self.assertEqual(out['restore']['action'], 'restored')
        self.assertEqual(self.server.active, INC)

    def test_no_auto_activation_needs_nothing(self):
        self.server.auto_activate_upload = False
        out = self.submit(activate=False)
        self.assertEqual(out['restore']['action'], 'none')
        self.assertEqual(self.server.active, INC)

    def test_activation_requested_keeps_upload(self):
        out = self.submit(activate=True)
        self.assertTrue(out.get('activated'))
        self.assertEqual(self.server.active, out['submission'])

    def test_restore_after_failed_post(self):
        self.server.fail_posts = 1   # the upload lands (auto-activated) but the POST answers 502
        out = self.submit(activate=False)
        self.assertIn('error', out)
        self.assertEqual(out['restore']['action'], 'restored')
        self.assertEqual(self.server.active, INC)

    def test_blackout_refuses_upload(self):
        self.now = 1_790_600_000 + 61 * 60 + 40   # 13:55:00Z, five minutes before an even hour
        n = len(self.server.subs)
        out = self.submit(activate=False)
        self.assertIn('blackout', out.get('error', ''))
        self.assertEqual(len(self.server.subs), n)
        self.assertEqual(self.server.active, INC)


if __name__ == '__main__':
    unittest.main()

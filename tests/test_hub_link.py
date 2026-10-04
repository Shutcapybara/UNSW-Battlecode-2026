"""register.json link items (D-048 §6): link a server submission to a registered candidate, no API call.
Run: python -m unittest tests.test_hub_link
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.hub import actuator, db  # noqa: E402
from tools.hub.config import load_config  # noqa: E402

FP = 'ebeba55fdd89' + '0' * 52


class LinkTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'
        self.root.mkdir()
        self.repo = self.tmp / 'repo'
        (self.repo / 'hub-state' / 'control').mkdir(parents=True)
        (self.root / 'hub.toml').write_text(f'[paths]\nrepo = "{self.repo}"\nlegacy_live = "{self.tmp}/live"\nmirror = "{self.repo}/hub-state"\npython = "{sys.executable}"\n[notify]\nosascript = false\n[team]\nid = 7\ndev_opponents = [545, 752]\n')
        self.cfg = load_config(self.root)
        self.conn = db.connect(self.root)
        db.upsert(self.conn, 'candidates', dict(name='carthage-05-free-sprint', fingerprint=FP, code_fingerprint='c' * 64, status='runtime_ok'), 'name')
        db.upsert(self.conn, 'candidates', dict(name='other', fingerprint='f' * 64, code_fingerprint='d' * 64, status='runtime_ok'), 'name')
        db.upsert(self.conn, 'submissions', dict(id=14585, name='LV-carthage-05-free-sprint-ebeba55f-ai'), 'id')
        db.upsert(self.conn, 'submissions', dict(id=99, name='Someone Else'), 'id')
        self.ctl = self.repo / 'hub-state' / 'control'

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.tmp)

    def run_items(self, items, **body):
        self.ctl.joinpath('register.json').write_text(json.dumps(dict(body, candidates=items)))
        actuator.register_check(self.root, self.cfg, {}, lambda m: None)
        self.assertFalse((self.ctl / 'register.json').exists())
        return json.loads((self.ctl / 'register.done.json').read_text())['results']

    def linked(self, name):
        r = self.conn.execute('SELECT submission_id, upload_name, status FROM candidates WHERE name=?', (name,)).fetchone()
        return tuple(r)

    def test_guards(self):
        item = dict(name='carthage-05-free-sprint', submission=14585, fingerprint8='ebeba55f', decision='D-048')
        cases = [
            (dict(item, decision=None), 'decision'),
            (dict(item, fingerprint8='ebeba5'), 'fingerprint8'),
            (dict(item, fingerprint8='deadbeef'), 'does not start'),
            (dict(item, name='nope'), 'unknown candidate'),
            (dict(item, submission=12345), 'not in the mirrored'),
            (dict(item, submission=99), 'expected'),
            (dict(item, submission='x'), 'integer'),
        ]
        for it, frag in cases:
            res = self.run_items([it])
            self.assertIn(frag, res[0].get('error', ''), (it, res))
        self.assertEqual(self.linked('carthage-05-free-sprint'), (None, None, 'runtime_ok'))

    def test_link_applies_once_and_keeps_status(self):
        item = dict(name='carthage-05-free-sprint', submission=14585, fingerprint8='ebeba55f')
        res = self.run_items([item], decision='D-048 §6', by='daichi')
        self.assertTrue(res[0]['linked'], res)
        self.assertEqual(self.linked('carthage-05-free-sprint'), (14585, 'LV-carthage-05-free-sprint-ebeba55f-ai', 'runtime_ok'))
        ev = self.conn.execute("SELECT actor, payload FROM events WHERE kind='candidate_linked'").fetchall()
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]['actor'], 'daichi')
        self.assertIn('D-048', ev[0]['payload'])
        # idempotent re-link is fine; another candidate cannot take the submission
        self.assertTrue(self.run_items([item], decision='D-048')[0]['linked'])
        db.upsert(self.conn, 'submissions', dict(id=14585, name='LV-other-ffffffff-ai'), 'id')
        res = self.run_items([dict(name='other', submission=14585, fingerprint8='ffffffff', decision='D-048')])
        self.assertIn('already linked', res[0]['error'])

    def test_priority_items_unchanged(self):
        res = self.run_items([dict(name='other', priority=300, reason='t')])
        self.assertEqual(res[0]['priority'], 300)


if __name__ == '__main__':
    unittest.main()

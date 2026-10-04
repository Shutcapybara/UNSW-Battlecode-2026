"""Targeted requested battles (tools/hub/battles.py) against the executor tests' fake server."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'tests'))
from tools.hub import battles, db, executor  # noqa: E402
from tools.hub.config import load_config  # noqa: E402
from test_hub_executor import FakeServer, fake_analyse, MAPS  # noqa: E402

INC, CAND = 9508, 9980


class BattlesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'
        self.root.mkdir()
        self.mirror = self.tmp / 'hub-state'
        (self.root / 'hub.toml').write_text(f'[paths]\nrepo = "{self.tmp}"\nlegacy_live = "{self.tmp}/live"\nmirror = "{self.mirror}"\n[notify]\nosascript = false\n[team]\nid = 7\ndev_opponents = [545, 752]\n')
        self.cfg = load_config(self.root)
        self.now = 1_790_600_000 + 25 * 60   # outside the even-hour blackout
        self.server = FakeServer(self.now)
        self.conn = db.connect(self.root)
        executor.ensure_columns(self.conn)
        db.kv_set(self.conn, 'control', INC)
        db.upsert(self.conn, 'candidates', dict(name='cand', fingerprint='a' * 64, code_fingerprint='c', lineage='x', status='uploaded', submission_id=CAND, priority=100, language='python'), 'name')
        self.p1 = patch.object(executor, 'analyse_replay', fake_analyse(self.server)); self.p1.start()
        self.p2 = patch.object(executor, 'runtime_exceptions', lambda p, s: []); self.p2.start()

    def tearDown(self):
        self.p1.stop(); self.p2.stop()
        self.conn.close()
        shutil.rmtree(self.tmp)

    def snap(self, now=None):
        return executor.Snapshot(self.server, self.conn, self.cfg, now or self.now)

    def request(self, body):
        ctl = self.mirror / 'control'
        ctl.mkdir(parents=True, exist_ok=True)
        (ctl / 'battles.json').write_text(json.dumps(body))
        battles.handle_request(self.conn, self.root, self.cfg, self.mirror, self.snap, log=lambda *a: None)
        self.assertFalse((ctl / 'battles.json').exists())
        return json.loads((ctl / 'battles.done.json').read_text())

    def base(self, **kw):
        body = dict(label='screen', by='test/daichi', decision='D-999', arms=[{'submission': INC}, {'candidate': 'cand'}],
                    opponents=[45, 62], seats='both', games_per_pair=2)
        body.update(kw)
        return body

    def tick(self, now=None):
        executor.CLOCK['now'] = None
        return battles.tick(self.conn, self.root, self.cfg, self.server, now=now or self.now)

    def posts(self):
        return [c for c in self.server.calls if c[0] == 'POST']

    def test_request_needs_a_decision(self):
        out = self.request(self.base(decision=''))
        self.assertIn('decision is required', out['error'])
        self.assertFalse(battles.open_jobs(self.conn))

    def test_unknown_candidate_and_bad_seats_are_refused(self):
        self.assertIn('not registered', self.request(self.base(arms=[{'candidate': 'nope'}]))['error'])
        self.assertIn('even', self.request(self.base(games_per_pair=3))['error'])
        self.assertIn('unknown or inactive maps', self.request(self.base(maps=['nowhere']))['error'])

    def test_no_dispatch_until_enabled(self):
        out = self.request(self.base())
        self.assertTrue(out['accepted'])
        self.assertEqual(out['planned_games'], 2 * 2 * len(MAPS) * 2)   # opponents × arms × maps × seats
        self.assertFalse(out['dispatch_enabled'])
        s = self.tick()
        self.assertIn('dispatch_disabled', [d['reason'] for d in s['deferred']])
        self.assertFalse(self.posts())

    def test_enable_needs_a_decision(self):
        self.assertIn('error', self.request(dict(action='enable', by='x')))
        self.assertTrue(self.request(dict(action='enable', by='x', decision='D-999'))['enabled'])

    def test_dispatch_pairs_both_arms_both_parities_and_restores(self):
        self.request(self.base())
        self.request(dict(action='enable', by='chair', decision='D-999'))
        s = self.tick()
        self.assertEqual(self.server.active, INC)                    # candidate was active only for its POSTs
        self.assertFalse(executor.open_txs(self.conn))
        self.assertFalse(executor.open_intents(self.conn))
        self.assertEqual(sum(d['games'] for d in s['dispatched']), 24)
        jid = battles.open_jobs(self.conn) or db.rows(self.conn, 'SELECT id FROM battle_jobs')
        jid = jid[0]['id']
        rows = db.rows(self.conn, 'SELECT submission, opponent_team, game_ids FROM requests WHERE block_id=?', (f'job:{jid}',))
        cover = {}
        for r in rows:
            for gid in json.loads(r['game_ids']):
                g = next(g for s_ in self.server.series.values() for g in s_['games'] if g['id'] == gid)
                cover.setdefault((r['submission'], r['opponent_team'], g['mapId']), set()).add(gid % 2)
        self.assertEqual(len(cover), 2 * 2 * len(MAPS))
        self.assertTrue(all(v == {0, 1} for v in cover.values()))   # every arm × opponent × map at both parities
        self.assertEqual(db.rows(self.conn, 'SELECT status FROM battle_jobs')[0]['status'], 'dispatched')

    def test_blackout_defers_a_foreign_arm(self):
        self.request(self.base())
        self.request(dict(action='enable', by='chair', decision='D-999'))
        blackout = 1_790_600_000 - (1_790_600_000 % 7200) + 7200 + 3 * 60   # 3 min after an even hour
        s = self.tick(now=blackout)
        self.assertIn('ranked_exposure_blackout', [d['reason'] for d in s['deferred']])
        self.assertFalse(self.posts())

    def test_incumbent_only_job_runs_in_blackout(self):
        self.request(self.base(arms=[{'submission': INC}], opponents=[45]))
        self.request(dict(action='enable', by='chair', decision='D-999'))
        blackout = 1_790_600_000 - (1_790_600_000 % 7200) + 7200 + 3 * 60
        s = self.tick(now=blackout)
        self.assertEqual(sum(d['games'] for d in s['dispatched']), 6)
        self.assertFalse([c for c in self.posts() if c[1].endswith('/activate')])

    def test_external_activation_pauses(self):
        self.request(self.base())
        self.request(dict(action='enable', by='chair', decision='D-999'))
        self.server.subs[INC]['status'] = 'idle'; self.server.subs[CAND]['status'] = 'active'   # a human activated something else
        s = self.tick()
        self.assertIn('battles_paused_external_activation', [a['kind'] for a in s['attention']])
        self.assertEqual(db.rows(self.conn, 'SELECT status FROM battle_jobs')[0]['status'], 'paused')
        # (the lost-switch path is not involved: no switch transaction is open)
        self.assertFalse(self.posts())

    def test_quota_defers_a_unit_that_does_not_fit(self):
        self.cfg['battles'] = dict(self.cfg['battles'], cycle_games=5)
        self.request(self.base())
        self.request(dict(action='enable', by='chair', decision='D-999'))
        s = self.tick()
        self.assertIn('quota', [d['reason'] for d in s['deferred']])
        self.assertFalse(self.posts())

    def test_lost_restore_is_repaired(self):
        tid = executor.open_tx(self.conn, 'switch', dict(previous=INC, candidate=CAND))
        self.server.subs[INC]['status'] = 'idle'; self.server.subs[CAND]['status'] = 'active'
        s = self.tick()
        self.assertEqual(self.server.active, INC)
        self.assertTrue(s['restored'])
        self.assertFalse(executor.open_txs(self.conn))
        self.assertTrue(tid)

    def test_cancel(self):
        jid = self.request(self.base())['job']
        self.assertTrue(self.request(dict(action='cancel', job=jid, by='chair'))['cancelled'])
        self.assertFalse(battles.open_jobs(self.conn))

    def test_harvest_and_paired_report(self):
        jid = self.request(self.base())['job']
        self.request(dict(action='enable', by='chair', decision='D-999'))
        self.tick()
        for r in db.rows(self.conn, 'SELECT submission, game_ids FROM requests WHERE block_id=?', (f'job:{jid}',)):
            for gid in json.loads(r['game_ids']):
                self.server.winner[gid] = 'a' if r['submission'] == CAND else 'b'   # the candidate wins everything
        executor.run_cycle(self.conn, self.root, self.cfg, self.server, mode='shadow', actor='test', now=self.now + 60)   # shadow harvest
        idx = battles.status(self.conn, self.mirror)
        job = idx['jobs'][0]
        self.assertEqual(job['verified'], job['requested'])
        p = job['paired']
        self.assertEqual((p['reference'], p['candidate']), (INC, CAND))
        self.assertEqual(p['pairs'], 2 * len(MAPS) * 2)
        self.assertEqual(p['delta'], 1.0)
        self.assertTrue((self.mirror / 'battles' / f'{jid}.json').exists())
        self.assertNotIn('rejected', job['requests'])
        self.assertEqual(job['rejected_opponents'], [])

    def test_rejected_requests_are_counted_in_the_index(self):
        jid = self.request(self.base())['job']
        db.upsert(self.conn, 'requests', dict(id='r-x', at=0, pool='field', opponent_team=752, submission=INC, map_ids='[]', count=5,
                                              status='rejected', game_ids='[]', block_id=f'job:{jid}', origin='test'), 'id')
        job = battles.status(self.conn, self.mirror)['jobs'][0]
        self.assertEqual(job['requests'].get('rejected'), 1)
        self.assertEqual(job['rejected_opponents'], [752])

    def test_paired_report_drops_missing_cells(self):
        games = [dict(verified=True, score=1.0, map_id=1, parity=0, opponent=5, arm=INC),
                 dict(verified=True, score=0.0, map_id=1, parity=0, opponent=5, arm=CAND),
                 dict(verified=False, score=None, map_id=2, parity=0, opponent=5, arm=CAND),
                 dict(verified=True, score=1.0, map_id=2, parity=0, opponent=5, arm=INC)]
        p = battles.paired_report(games, [INC, CAND])
        self.assertEqual(p['pairs'], 1)
        self.assertEqual(p['delta'], -1.0)

    def test_actuator_round_trip(self):
        from tools.hub import actuator
        ctl = self.mirror / 'control'
        ctl.mkdir(parents=True, exist_ok=True)
        (ctl / 'battles.json').write_text(json.dumps(self.base()))
        state = {}
        with patch.object(executor, 'Snapshot', lambda c, conn, cfg, now, progress=None: _RealSnapshot(c, conn, cfg, self.now)):
            actuator.battles_check(self.root, self.cfg, state, self.server, lambda *a: None)
        done = json.loads((ctl / 'battles.done.json').read_text())
        self.assertTrue(done['accepted'])
        self.assertTrue((self.mirror / 'battles' / 'index.json').exists())
        self.assertGreater(state['next_battles'], 0)
        self.assertFalse(self.posts())   # not enabled


_RealSnapshot = executor.Snapshot



if __name__ == '__main__':
    unittest.main()

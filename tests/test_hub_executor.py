"""Executor acceptance tests against a fake server that reproduces today's incidents (Part B §13, v2 form)."""
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.hub import stats, db, executor  # noqa: E402
from tools.hub.api import APIError  # noqa: E402
from tools.hub.config import load_config  # noqa: E402

TEAM = 7
MAPS = [9, 20, 21]
ISO = lambda t: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))


class FakeServer:
    """Enough of the Battlecode API for the executor: submissions, activation, battles, replays."""

    def __init__(self, now):
        self.now = now
        self.subs = {9508: dict(id=9508, name='Bifrost v18', status='active', language='python', sourceHash='h9508'),
                     9980: dict(id=9980, name='LV-cand-aaaaaaaa-ai', status='idle', language='python', sourceHash='h9980')}
        self.series = {}
        self.next_id = 1000
        self.fail_posts = 0            # next N POSTs raise 502 AFTER applying the effect (lost acknowledgement)
        self.reject_posts = None       # (status, message) for next POST
        self.partial_ids = set()       # game ids whose replay is not available yet (new shape: hasReplay false; old shape: no submission ids/replayKey)
        self.old_shape = False         # True: the pre-28-Sep payload (submission ids and replayKey in `match`); False: no ids, games[].hasReplay
        self.members = {'me'}
        self.calls = []
        self.layout_flip = set()       # (submission, map) that get the opposite layout (legacy fake; unused when parity_layouts)
        self.parity_layouts = True     # the real rule (A1-Q3): starting orientation = f(map, game id parity)
        self.max_maps = 20             # server limit per request (refusal path); the real server instead creates one game per distinct map
        self.dedupe_maps = True        # the real behaviour (D-022): a request listing a map twice yields one game for it
        self.gap = 0                   # foreign games created after each of our batches (shifts the next batch's id parity)
        self.gap_schedule = []         # per-POST gaps consumed first (then `gap`): odd values between an arm's two waves split its layouts
        self.auto_activate_upload = False
        self.winner = {}               # game id -> 'a'/'b'

    @property
    def active(self):
        return next(s['id'] for s in self.subs.values() if s['status'] == 'active')

    def get(self, path, attempts=3):
        self.calls.append(('GET', path))
        if path == '/api/v1/submissions':
            return [dict(s) for s in self.subs.values()]
        if path == '/api/v1/maps':
            return [dict(id=m, active=True, private=False, name=f'map{m}') for m in MAPS]
        if path == '/api/v1/team':
            return dict(team=dict(id=TEAM, members=[dict(id=m) for m in self.members]))
        if path == '/api/v1/ratings':
            return dict(ladder=[dict(id=545, dev=True, rank=13), dict(id=752, dev=True, rank=87), dict(id=62, rank=37), dict(id=45, rank=68), dict(id=470, rank=2), dict(id=TEAM, rank=76)])
        if path.startswith('/api/v1/battles?'):
            return [dict(id=sid, at=ISO(s['match']['_requested']), outcome='live') for sid, s in sorted(self.series.items(), reverse=True)][:200]
        if path.startswith('/api/v1/battles/'):
            gid = int(path.rsplit('/', 1)[1])
            for s in self.series.values():
                for g in s['games']:
                    if g['id'] == gid:
                        m = dict(s['match'])
                        m['id'] = gid
                        m['mapId'] = g['mapId']
                        m['seed'] = g['seed']
                        m['winner'] = self.winner.get(gid, 'a')
                        if self.old_shape:
                            if gid in self.partial_ids:
                                for k in ('submissionAId', 'submissionBId', 'replayKey', 'mapHash'):
                                    m.pop(k, None)
                            return dict(match={k: v for k, v in m.items() if not k.startswith('_')}, mapName=f"map{g['mapId']}", games=[dict(id=x['id'], status=m['status']) for x in s['games']])
                        for k in ('submissionAId', 'submissionBId', 'replayKey', 'mapHash'):
                            m.pop(k, None)
                        return dict(match={k: v for k, v in m.items() if not k.startswith('_')}, mapName=f"map{g['mapId']}", wait=None,
                                    games=[dict(id=x['id'], status=m['status'], hasReplay=x['id'] not in self.partial_ids, mapName=f"map{x['mapId']}") for x in s['games']])
            raise APIError(404, 'no such battle')
        raise APIError(404, path)

    def post(self, path, body, content_type='application/json'):
        self.calls.append(('POST', path))
        if self.reject_posts:
            status, message = self.reject_posts
            self.reject_posts = None
            raise APIError(status, message, 3000 if status == 429 else None)
        if path.endswith('/activate'):
            sid = int(path.split('/')[-2])
            for s in self.subs.values():
                s['status'] = 'active' if s['id'] == sid else 'idle'
            result = dict(ok=True)
        elif path == '/api/v1/battles':
            if len(body['mapIds']) > self.max_maps:
                raise APIError(400, f'{{"error":"at most {self.max_maps} maps per request"}}')
            ids = []
            sid = self.next_id
            for m in (dict.fromkeys(body['mapIds']) if self.dedupe_maps else body['mapIds']):
                gid = self.next_id
                self.next_id += 1
                ids.append(dict(id=gid, mapId=m, seed=f'seed{gid}'))
            a_sub = self.active
            self.series[sid] = dict(match=dict(id=sid, seriesId=f's{sid}', requestedBy='me', requestedAt=ISO(self.now), _requested=self.now, teamAId=TEAM, teamBId=body['teamId'],
                                               submissionAId=a_sub, submissionBId=1, ranked=False, status='completed', winner='a', replayKey='r', mapHash='x'), games=ids)
            result = dict(ids=[g['id'] for g in ids])
            self.next_id += self.gap_schedule.pop(0) if self.gap_schedule else self.gap
        elif path == '/api/v1/submissions':
            sid = 9990 + len(self.subs)
            self.subs[sid] = dict(id=sid, name='LV-newbot-bbbbbbbb-ai', status='active' if self.auto_activate_upload else 'idle', language='python', sourceHash='hnew')
            if self.auto_activate_upload:
                for s in self.subs.values():
                    if s['id'] != sid:
                        s['status'] = 'idle'
            result = dict(id=sid)
        else:
            raise APIError(404, path)
        if self.fail_posts:
            self.fail_posts -= 1
            raise APIError(502, 'error code: 502')
        return result

    def download_replay(self, game_id, destination):
        Path(destination).write_bytes(b'REPLAY' + str(game_id).encode())
        return destination


def fake_analyse(server):
    def analyse(path):
        gid = int(Path(path).stem)
        game = next(g for s in server.series.values() for g in s['games'] if g['id'] == gid)
        sub = next(s['match']['submissionAId'] for s in server.series.values() for g in s['games'] if g['id'] == gid)
        winner = server.winner.get(gid, 'a').upper()   # the real decoder reports 'A'/'B'/'draw'; the API reports 'a'/'b'
        layout = f"L{(gid + game['mapId']) % 2}" if server.parity_layouts else ('L2' if (sub, game['mapId']) in server.layout_flip else 'L1')
        curve = [dict(round=r, A=dict(units=5, total=20, longest=6), B=dict(units=5, total=20, longest=6)) for r in (100, 200, 250, 300, 320, 360, 380, 400, 450, 499)]
        return dict(winner=winner, stats={'A': dict(turns=100, tle=0, cpu_max=50_000_000, cpu_recorded=100), 'B': dict(turns=100, tle=0, cpu_max=50_000_000, cpu_recorded=100)},
                    final={'A': dict(units=3, longest=10, total=20), 'B': dict(units=3, longest=8, total=20)}, curve=curve, rounds=500, reason='roundLimit', map_hash=layout, deaths=[], first_length={})
    return analyse


class ExecutorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'
        self.root.mkdir()
        (self.root / 'hub.toml').write_text(f'[paths]\nrepo = "{self.tmp}"\nlegacy_live = "{self.tmp}/live"\nmirror = "{self.tmp}/hub-state"\n[notify]\nosascript = false\n[team]\nid = 7\ndev_opponents = [545, 752]\n')
        self.cfg = load_config(self.root)
        self.cfg['panels'] = {'screen': [62, 45, 470], 'confirmation': [853, 241, 481, 473, 133, 30, 193, 262, 130, 306, 213, 157]}
        self.now = 1_790_600_000 + 25 * 60   # 12:25 UTC-ish: outside the blackout around even hours
        self.server = FakeServer(self.now)
        self.conn = db.connect(self.root)
        executor.ensure_columns(self.conn)
        db.kv_set(self.conn, 'control', 9508)
        db.upsert(self.conn, 'candidates', dict(name='cand', fingerprint='aaaaaaaa' * 8, code_fingerprint='c', lineage='x', status='uploaded', submission_id=9980, priority=100, language='python'), 'name')
        self.patcher = patch.object(executor, 'analyse_replay', fake_analyse(self.server))
        self.patcher.start()
        self.patcher2 = patch.object(executor, 'runtime_exceptions', lambda p, s: [])
        self.patcher2.start()

    def tearDown(self):
        self.patcher.stop()
        self.patcher2.stop()
        self.conn.close()
        shutil.rmtree(self.tmp)

    def cycle(self, mode='live', now=None):
        return executor.run_cycle(self.conn, self.root, self.cfg, self.server, mode=mode, actor='test', now=now or self.now)

    def test_dev_coverage_and_screen_open_with_restore(self):
        s = self.cycle()
        self.assertEqual(s['control'], 9508)
        dev = [d for d in s['dispatched'] if d['pool'] == 'dev']
        self.assertTrue(dev)  # dev coverage for the control and the candidate
        self.assertEqual(self.server.active, 9508)  # restored after the candidate's batches
        self.assertFalse(executor.open_txs(self.conn))
        self.assertFalse(executor.open_intents(self.conn))

    def test_shadow_never_posts(self):
        s = self.cycle(mode='shadow')
        self.assertTrue(s['plan'])
        self.assertFalse([c for c in self.server.calls if c[0] == 'POST'])
        self.assertFalse(s['dispatched'])

    def test_shadow_writes_no_experiment_state(self):
        # a dev_ok candidate would open a screen when live; shadow only plans it
        self.conn.execute("UPDATE candidates SET status='dev_ok' WHERE name='cand'")
        s = self.cycle(mode='shadow')
        self.assertIn('open_experiment', [x['action'] for x in s['plan']])
        self.assertFalse(s['opened'])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0], 0)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0], 0)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0], 0)

    def test_legacy_v1_experiment_is_never_evaluated_or_frozen(self):
        # a running protocol-v1 row imported from LIVE/state (three empty screen blocks would be 'screening' under v2,
        # but the executor must not touch it, nor freeze it when the control changes)
        db.upsert(self.conn, 'experiments', dict(id='legacy1', candidate_name='yuna', candidate_submission=10013, control_submission=9508, protocol='v1', status='running', params=None, map_ids=[1, 2]), 'id')
        self.conn.execute("UPDATE candidates SET status='dev_ok' WHERE name='cand'")
        s = self.cycle(mode='shadow')
        self.assertEqual(self.conn.execute("SELECT status FROM experiments WHERE id='legacy1'").fetchone()[0], 'running')
        self.assertFalse(s['verdicts'])
        self.assertIn('open_experiment', [x['action'] for x in s['plan']])   # v1 rows do not count as the running experiment
        # a teammate activates another submission: the v1 row is still not the executor's to freeze
        self.server.subs[9990] = dict(id=9990, name='Heimdall v10', status='active', language='python', sourceHash='h')
        self.server.subs[9508]['status'] = 'idle'
        s2 = self.cycle(mode='shadow', now=self.now + 600)
        self.assertEqual(self.conn.execute("SELECT status FROM experiments WHERE id='legacy1'").fetchone()[0], 'running')
        self.assertFalse(s2['frozen'])
        self.assertTrue(s2['external_actions'])
        self.assertEqual(s2['control'], 9990)

    def test_lost_battle_acknowledgement_reconciles_without_repost(self):
        self.server.fail_posts = 1   # the first POST (a dev batch for the control) is applied server-side but answered 502
        s = self.cycle()
        self.assertTrue(s['stop'])
        opens = executor.open_intents(self.conn)
        self.assertEqual(len(opens), 1)
        posts_before = len([c for c in self.server.calls if c == ('POST', '/api/v1/battles')])
        s2 = self.cycle(now=self.now + 120)
        self.assertFalse(executor.open_intents(self.conn))
        req = self.conn.execute("SELECT status, game_ids FROM requests WHERE id=?", (opens[0]['payload']['request_id'],)).fetchone()
        self.assertEqual(req['status'], 'accepted')
        self.assertTrue(json.loads(req['game_ids']))
        posts_after = len([c for c in self.server.calls if c == ('POST', '/api/v1/battles')])
        self.assertGreaterEqual(posts_after, posts_before)  # new batches may follow, but the lost one was not re-posted for the same request
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM requests WHERE status='accepted'").fetchone()[0], len({tuple(json.loads(r['game_ids'])) for r in db.rows(self.conn, "SELECT game_ids FROM requests WHERE status='accepted'")}))

    def test_lost_acknowledgement_with_no_series_is_released_after_grace(self):
        self.server.fail_posts = 1
        s = self.cycle()
        intent = executor.open_intents(self.conn)[0]
        # simulate the server having dropped the request entirely
        self.server.series.clear()
        self.cycle(now=self.now + 100)
        self.assertEqual(len(executor.open_intents(self.conn)), 1)  # inside the grace period: still open
        self.cycle(now=self.now + 700)
        self.assertFalse(executor.open_intents(self.conn))
        self.assertEqual(self.conn.execute('SELECT status FROM requests WHERE id=?', (intent['payload']['request_id'],)).fetchone()[0], 'released')

    def test_partial_payload_is_unknown_not_a_loss(self):
        self.cycle()
        gid = next(g['id'] for s in self.server.series.values() for g in s['games'])
        self.server.partial_ids.add(gid)
        self.cycle(now=self.now + 60)
        row = self.conn.execute('SELECT verified, error, own_submission, score FROM games WHERE game_id=?', (gid,)).fetchone()
        self.assertEqual(row['verified'], 0)
        self.assertIn('not yet', row['error'])
        self.assertIsNotNone(row['own_submission'])
        self.assertIsNone(row['score'])
        self.server.partial_ids.discard(gid)
        self.cycle(now=self.now + 120)
        self.assertEqual(self.conn.execute('SELECT verified FROM games WHERE game_id=?', (gid,)).fetchone()[0], 1)

    def test_games_are_attributed_by_the_request_when_the_api_omits_submission_ids(self):
        self.cycle()
        self.cycle(now=self.now + 60)
        rows_ = db.rows(self.conn, "SELECT game_id, own_submission, verified, stats FROM games WHERE pool='dev'")
        self.assertTrue(rows_ and all(r['verified'] for r in rows_))
        self.assertEqual({r['own_submission'] for r in rows_}, {9508, 9980})
        self.assertTrue(all(json.loads(r['stats'])['attribution'] == 'request' for r in rows_))
        # the old shape still verifies through the API-reported ids, and a mismatch is excluded
        self.server.old_shape = True
        self.conn.execute('UPDATE games SET verified=0, harvest_attempts=0')
        self.cycle(now=self.now + 120)
        rows_ = db.rows(self.conn, "SELECT stats FROM games WHERE pool='dev' AND verified=1")
        self.assertTrue(rows_ and all(json.loads(r['stats'])['attribution'] == 'api' for r in rows_))
        for sid in self.server.series.values():
            sid['match']['submissionAId'] = 4242
        self.conn.execute('UPDATE games SET verified=0, harvest_attempts=0')
        self.cycle(now=self.now + 180)
        self.assertTrue(all('mismatch' in (r['error'] or '') for r in db.rows(self.conn, "SELECT error FROM games WHERE pool='dev'")))

    def test_incomplete_payloads_are_refetched_for_a_day_with_backoff(self):
        self.cycle()
        ids = [g['id'] for s in self.server.series.values() for g in s['games']]
        self.server.partial_ids.update(ids)   # the server's replay pipeline lags: every dev game comes back with hasReplay false
        for i in range(1, 7):
            self.cycle(now=self.now + 600 * i)
        gets = lambda: len([c for c in self.server.calls if c[0] == 'GET' and c[1].startswith(f'/api/v1/battles/{ids[0]}')])
        before = gets()
        self.assertEqual(self.conn.execute('SELECT harvest_attempts FROM games WHERE game_id=?', (ids[0],)).fetchone()[0], 6)
        self.cycle(now=self.now + 600 * 7)        # attempts ≥ 6 and the last try 10 min ago: backlog backoff, not re-fetched
        self.assertEqual(gets(), before)
        self.cycle(now=self.now + 600 * 9)        # 30 min after the last try it is re-fetched again (no attempt cap)
        self.assertEqual(gets(), before + 1)
        row = self.conn.execute('SELECT harvest_attempts, verified FROM games WHERE game_id=?', (ids[0],)).fetchone()
        self.assertEqual((row['harvest_attempts'], row['verified']), (7, 0))
        self.server.partial_ids.clear()
        self.cycle(now=self.now + 600 * 12)
        self.assertEqual(self.conn.execute('SELECT verified FROM games WHERE game_id=?', (ids[0],)).fetchone()[0], 1)
        self.server.partial_ids.update(ids)
        self.conn.execute('UPDATE games SET verified=0, harvest_attempts=0')
        n = len(self.server.calls)
        self.cycle(now=self.now + executor.HARVEST_HORIZON + 7200)   # beyond the horizon nothing is fetched for those requests
        self.assertFalse([c for c in self.server.calls[n:] if c[0] == 'GET' and c[1] in {f'/api/v1/battles/{i}' for i in ids}])

    def make_candidate_win(self):
        original_post = self.server.post

        def winning_post(path, body, content_type='application/json'):
            out = original_post(path, body, content_type)
            if path == '/api/v1/battles':
                a_sub = self.server.series[max(self.server.series)]['match']['submissionAId']
                for gid in out['ids']:
                    self.server.winner[gid] = 'a' if a_sub == 9980 else 'b'
            return out
        self.server.post = winning_post

    def test_external_activation_freezes_and_requeues(self):
        self.make_candidate_win()
        for i in range(6):
            self.cycle(now=self.now + 600 * i)
        self.assertTrue(db.rows(self.conn, "SELECT id FROM experiments WHERE status='running'"))
        self.server.subs[9990] = dict(id=9990, name='Heimdall v10', status='active', language='python', sourceHash='h')
        self.server.subs[9508]['status'] = 'idle'
        s = self.cycle(now=self.now + 600 * 7)
        self.assertEqual(s['control'], 9990)
        self.assertTrue(s['external_actions'])
        self.assertTrue(s['frozen'])
        running = db.rows(self.conn, "SELECT id, control_submission FROM experiments WHERE status='running'")
        self.assertTrue(all(r['control_submission'] == 9990 for r in running))   # re-compared against the new control, never against the old one
        self.assertTrue(db.rows(self.conn, "SELECT id FROM experiments WHERE status LIKE 'superseded%'"))
        self.assertEqual(self.server.active, 9990)  # never re-activated our own control
        cand = self.conn.execute("SELECT status FROM candidates WHERE name='cand'").fetchone()[0]
        self.assertIn(cand, ('uploaded', 'dev_ok'))  # not orphaned; will be re-compared against 9990

    def test_own_switch_is_restored_and_teammate_choice_preserved(self):
        tid = executor.open_tx(self.conn, 'switch', dict(previous=9508, candidate=9980))
        self.server.subs[9980]['status'] = 'active'
        self.server.subs[9508]['status'] = 'idle'
        s = self.cycle()
        self.assertEqual(self.server.active, 9508)
        self.assertFalse(executor.open_txs(self.conn))
        tid = executor.open_tx(self.conn, 'switch', dict(previous=9508, candidate=9980))
        self.server.subs[9990] = dict(id=9990, name='Heimdall v10', status='active', language='python', sourceHash='h')
        self.server.subs[9508]['status'] = 'idle'
        s = self.cycle(now=self.now + 60)
        self.assertEqual(self.server.active, 9990)
        self.assertEqual(self.conn.execute("SELECT outcome FROM transactions WHERE id=?", (tid,)).fetchone()[0], 'external_choice_preserved')

    def test_blackout_defers_candidate_batches(self):
        even_hour = (self.now // 7200) * 7200 - 120   # two minutes before an even UTC hour
        s = self.cycle(now=even_hour)
        self.assertTrue(any(d['reason'] == 'ranked_exposure_blackout' for d in s['deferred']))
        self.assertFalse(any(d['submission'] == 9980 for d in s['dispatched']))

    def test_quota_rejection_blocks_pool(self):
        self.server.reject_posts = (429, 'Your team has used its 60 games for the hour. More free up in 50 min.')
        s = self.cycle()
        self.assertTrue(any(a['kind'] == 'quota_rejection' for a in s['attention']))
        blocked = self.conn.execute("SELECT until FROM quota_blocks").fetchone()
        self.assertGreater(blocked['until'], self.now + 2000)

    def test_two_orientation_blocks_pair_completely_without_fills(self):
        for i in range(4):
            self.cycle(now=self.now + 600 * i)
        blocks = db.rows(self.conn, "SELECT id, request_maps, fill_attempts, requests FROM blocks WHERE phase='screen'")
        self.assertTrue(blocks)
        self.assertEqual(json.loads(blocks[0]['request_maps']), executor.rotation(MAPS))
        groups = json.loads(blocks[0]['requests'])
        self.assertEqual(len(groups), 4)                                   # two waves per arm (D-022)
        self.assertTrue(all(len(g) == len(MAPS) for g in groups))          # one game per distinct map per wave
        posted = [c for c in self.server.calls if c == ('POST', '/api/v1/battles')]
        self.assertGreaterEqual(len(posted), 4)
        shaped0, results0 = executor.legacy_shapes(self.conn)
        layouts = {}
        for b in shaped0:
            if b['phase'] != 'screen':
                continue
            for g in b['requests']:
                for i in g:
                    r = results0.get(str(i))
                    if r:
                        layouts.setdefault((r['submission'], r['map_id']), set()).add(r['map_hash'])
        self.assertTrue(all(len(v) == 2 for v in layouts.values()), layouts)   # every arm saw both starting layouts of every map
        for maps in ([9, 20, 21], list(range(10)), [1, 2]):
            r = executor.rotation(maps)
            for m in maps:
                pos = [i for i, x in enumerate(r) if x == m]
                self.assertEqual(len(pos), 2)
                self.assertNotEqual(pos[0] % 2, pos[1] % 2, (maps, m, pos))
        self.assertFalse(any((b['fill_attempts'] or 0) for b in blocks))
        shaped, results = executor.legacy_shapes(self.conn)
        paired = stats.paired_blocks_v2(shaped, results)
        done = [p for p in paired if p['complete']]
        self.assertTrue(done)
        self.assertEqual(len(done[0]['pairs']), 2 * len(MAPS))
        self.assertEqual(len({(x['map_id'], x['side']) for x in done[0]['pairs']}), len(MAPS))

    def test_interleaved_foreign_games_are_repaired_by_paired_fills(self):
        self.cycle()   # dev coverage (4 dev POSTs); the first screen block comes next
        self.server.gap_schedule = [1]   # one foreign game between the first arm's two waves: that arm repeats a layout instead of covering
        # both, and every later request lands on the parity the arm order dictates, so a single-arm fill could never re-pair (locked parity)
        for i in range(1, 8):
            s = self.cycle(now=self.now + 600 * i)
        blocks = db.rows(self.conn, "SELECT id, fill_attempts, requests, excluded_reason FROM blocks WHERE phase='screen' ORDER BY created_at")
        self.assertTrue(blocks)
        first = blocks[0]
        self.assertGreaterEqual(first['fill_attempts'], 1)
        self.assertIsNone(first['excluded_reason'])
        groups = json.loads(first['requests'])
        self.assertGreaterEqual(len(groups), 6)   # four waves plus paired fills (both arms each)
        shaped, results = executor.legacy_shapes(self.conn)
        p = next(x for x in stats.paired_blocks_v2(shaped, results) if x['block'] == first['id'])
        self.assertTrue(p['complete'], (len(p['pairs']), p['missing_maps']))
        self.assertGreaterEqual(len(p['pairs']), 2 * len(MAPS))

    def test_screen_blocks_against_dev_teams_draw_on_the_dev_allowance(self):
        self.cfg['panels']['screen'] = [545, 752, 45]   # D-026
        self.make_candidate_win()
        self.cycle()                                    # dev coverage (12 games on dev quota)
        s = self.cycle(now=self.now + 600)              # first screen block: vs 545, both arms
        field = [d for d in s['dispatched'] if d['pool'] == 'field']
        dev = [d for d in s['dispatched'] if d['pool'] == 'dev' and d['opponent'] == 545]
        self.assertFalse(field)
        self.assertEqual(len(dev), 4)                   # two waves per arm
        self.assertEqual(s['quota']['field']['available'], self.cfg['budget']['executor_cap']['field'])
        s2 = self.cycle(now=self.now + 1200)            # second block: vs 752, still on dev quota
        self.assertTrue(all(d['pool'] == 'dev' and d['opponent'] == 752 for d in s2['dispatched']) and s2['dispatched'])
        s3 = self.cycle(now=self.now + 1800)            # third block: the field calibration opponent
        self.assertTrue(all(d['pool'] == 'field' and d['opponent'] == 45 for d in s3['dispatched']) and s3['dispatched'], (s3['dispatched'], s3['deferred']))
        self.assertLess(s3['quota']['field']['available'], self.cfg['budget']['executor_cap']['field'])

    def test_waves_and_spread(self):
        self.assertEqual(executor.waves_of_distinct_maps(executor.rotation([9, 20, 21])), [[9, 20, 21], [9, 20, 21]])
        self.assertEqual(executor.waves_of_distinct_maps(executor.rotation(list(range(10)))), [list(range(10)), list(range(1, 10)) + [0]])
        self.assertEqual(executor.waves_of_distinct_maps([]), [])
        self.assertEqual(executor.spread([9, 9, 20, 21, 21]), [9, 20, 21, 9, 21])
        self.assertEqual(executor.waves_of_distinct_maps(executor.spread([9, 9, 20, 21, 21])), [[9, 20, 21], [9, 21]])
        self.assertEqual(executor.aligned([9, 21], 1, MAPS), [9, 21])            # even wave: same order aligns consecutive ids
        self.assertEqual(executor.aligned([9], 1, MAPS), [20, 9])               # odd wave: a spare map in front shifts the parity
        self.assertEqual(executor.aligned([9, 20, 21], 1, MAPS), [20, 21, 9])   # no spare left: rotate (the wrapped map waits for the next fill)
        self.assertEqual(executor.aligned([9, 20, 21], 0, MAPS), [9, 20, 21])

    def test_running_experiment_params_are_migrated(self):
        self.make_candidate_win()
        self.cycle(); self.cycle(now=self.now + 600)
        e = db.rows(self.conn, "SELECT id, params FROM experiments WHERE status='running'")[0]
        old = dict(json.loads(e['params']), max_fills=0, min_pairs=14)
        self.conn.execute('UPDATE experiments SET params=? WHERE id=?', (json.dumps(old), e['id']))
        s = self.cycle(now=self.now + 1200)
        self.assertEqual([m['experiment'] for m in s.get('migrated', [])], [e['id']])
        p = json.loads(db.rows(self.conn, "SELECT params FROM experiments WHERE id=?", (e['id'],))[0]['params'])
        self.assertEqual((p['max_fills'], p['min_pairs']), (3, 10))
        self.assertFalse(self.cycle(now=self.now + 1800).get('migrated'))
        # a block the old rule excluded before its games were verified is reinstated and then filled
        b = db.rows(self.conn, "SELECT id FROM blocks WHERE experiment_id=? ORDER BY created_at", (e['id'],))[0]
        self.conn.execute("UPDATE blocks SET excluded_reason=? WHERE id=?", ('0 pairs after 0 fills (min 14)', b['id']))
        s = self.cycle(now=self.now + 2400)
        self.assertTrue(any(m.get('block') == b['id'] for m in s.get('migrated', [])))
        self.assertIsNone(db.rows(self.conn, "SELECT excluded_reason FROM blocks WHERE id=?", (b['id'],))[0]['excluded_reason'])

    def test_single_orientation_shape_still_works_with_fills(self):
        db.kv_set(self.conn, 'request_shape', 'single')   # the legacy shape (kept for a server that refuses the waves)
        self.server.gap = 2   # with 3-map batches an odd id gap between the arms (3 + 2) flips the layout family: single-orientation blocks then need fills
        for i in range(16):
            self.cycle(now=self.now + 600 * i)
        self.assertEqual(self.server.active, 9508)
        blocks = db.rows(self.conn, "SELECT id, request_maps, fill_attempts, excluded_reason FROM blocks WHERE phase='screen'")
        live_blocks = [b for b in blocks if b['request_maps'] and len(json.loads(b['request_maps'])) == len(MAPS)]
        self.assertTrue(live_blocks)
        self.assertTrue(any((b['fill_attempts'] or 0) >= 1 for b in live_blocks))   # legacy fill path still works
        e = db.rows(self.conn, "SELECT status FROM experiments")[0]
        self.assertIn(e['status'], ('running', 'reject_screen', 'promote'))

    def test_upload_auto_activation_is_undone(self):
        self.server.auto_activate_upload = True
        (self.root / 'candidates').mkdir()
        import zipfile
        with zipfile.ZipFile(self.root / 'candidates' / 'newbot.zip', 'w') as z:
            z.writestr('main.py', 'print(1)\n')
        import hashlib
        db.upsert(self.conn, 'candidates', dict(name='newbot', fingerprint='bbbbbbbb' * 8, code_fingerprint='cc', lineage='y', status='runtime_ok', priority=200, language='python',
                                                archive_path=str(self.root / 'candidates' / 'newbot.zip'), source_files={'main.py': hashlib.sha256(b'print(1)\n').hexdigest()}), 'name')
        self.make_candidate_win()
        s = self.cycle()   # the upload of newbot happens here (auto-activated by the fake server) plus dev coverage
        self.assertTrue(any(u.get('pending') for u in s['uploads']))
        s1 = self.cycle(now=self.now + 600)   # upload reconciled and undone; 9980's screen opens against 9508
        self.assertEqual(self.server.active, 9508)
        self.assertTrue(db.rows(self.conn, "SELECT id FROM experiments WHERE status='running'"))
        new_sub = max(self.server.subs)
        self.server.subs[new_sub]['status'] = 'active'; self.server.subs[9508]['status'] = 'idle'   # the server activates the upload again when its build completes (28 Sep 14:26 incident)
        s2 = self.cycle(now=self.now + 1200)
        self.assertTrue(any(a['kind'] == 'upload_auto_activated' for a in s2['attention']), s2['attention'])
        self.assertFalse(s2['external_actions'], 'an auto-activated executor upload is never a teammate action')
        self.assertEqual(db.kv_get(self.conn, 'control'), 9508)
        self.assertEqual(self.server.active, 9508)   # auto-activation undone
        self.assertFalse(db.rows(self.conn, "SELECT id FROM experiments WHERE status LIKE 'superseded%'"), 'the running screen must not be frozen by our own upload')
        row = self.conn.execute("SELECT status, submission_id FROM candidates WHERE name='newbot'").fetchone()
        self.assertIn(row['status'], ('uploaded', 'dev_ok'))
        self.assertEqual(row['submission_id'], new_sub)
        self.assertFalse(executor.open_txs(self.conn))

    def test_poisoned_control_is_repaired_to_the_last_real_control(self):
        # the 28 Sep state: the executor's own upload (9980 in this fixture) was adopted as control by the old code
        self.cycle(); self.cycle(now=self.now + 600)   # 9980 uploaded/dev-covered; its name ends in -ai
        db.upsert(self.conn, 'external_actions', dict(id='x1', at=executor.now_iso(), kind='activation', submission=9980, previous=9508, requested_by=None, note='teammate_selected'), 'id')
        db.event(self.conn, self.root, 'test', 'upload_reconciled', dict(name='LV-cand-aaaaaaaa-ai', submission=9980))
        db.kv_set(self.conn, 'control', 9980); db.kv_set(self.conn, 'control_owner', 'teammate')
        for sub in self.server.subs.values():
            sub['status'] = 'active' if sub['id'] == 9980 else 'idle'
        s = self.cycle(now=self.now + 1200)
        self.assertTrue(any(a['kind'] == 'upload_auto_activated' for a in s['attention']), s['attention'])
        self.assertEqual(self.server.active, 9508)
        self.assertEqual(db.kv_get(self.conn, 'control'), 9508)
        self.assertFalse(s['external_actions'])

    def test_running_experiment_with_a_stale_control_is_frozen_and_replaced(self):
        self.make_candidate_win()
        self.cycle(); self.cycle(now=self.now + 600)
        e = db.rows(self.conn, "SELECT id, control_submission FROM experiments WHERE status='running'")
        self.assertTrue(e)
        # the control moves without the observer seeing an activation (director restore path): 9508 -> 9990
        self.server.subs[9990] = dict(id=9990, name='Heimdall v10', status='active', language='python', sourceHash='h')
        self.server.subs[9508]['status'] = 'idle'
        db.kv_set(self.conn, 'control', 9990); db.kv_set(self.conn, 'control_owner', 'director')
        s = self.cycle(now=self.now + 1200)
        self.assertEqual(self.conn.execute("SELECT status FROM experiments WHERE id=?", (e[0]['id'],)).fetchone()[0], 'superseded_by_external_activation')
        running = db.rows(self.conn, "SELECT control_submission FROM experiments WHERE status='running'")
        self.assertTrue(running and all(r['control_submission'] == 9990 for r in running))
        self.assertIn('ranked_recent', s)

    def test_slow_server_budgets_never_dispatch_on_unknown_quota(self):
        # snapshot budget exhausted before the history is read: harvest/evaluate proceed, requests do not
        self.cycle()   # first cycle creates history (dev batches)
        posts = len([c for c in self.server.calls if c == ('POST', '/api/v1/battles')])
        self.cfg['executor']['snapshot_seconds'] = 0
        s = self.cycle(now=self.now + 600)
        self.assertTrue(any(a['kind'] == 'quota_unknown' for a in s['attention']))
        self.assertTrue(s['quota']['field']['unknown'])
        self.assertFalse(s['dispatched'])
        self.assertEqual(len([c for c in self.server.calls if c == ('POST', '/api/v1/battles')]), posts)
        self.assertIsNotNone(s.get('seconds'))

    def test_harvest_budget_bounds_work_per_cycle_and_keeps_a_backlog(self):
        s = self.cycle()   # dev batches requested (12 games)
        self.assertTrue(s['dispatched'])
        self.cfg['executor']['harvest_seconds'] = 0   # a slow server: at least one game per cycle, the rest waits
        s2 = self.cycle(now=self.now + 600)
        self.assertEqual(s2['harvest']['attempted'], 1)
        self.assertGreater(s2['harvest']['backlog'], 0)
        phases = []
        s3 = executor.run_cycle(self.conn, self.root, self.cfg, self.server, mode='live', actor='test', now=self.now + 1200, progress=lambda ph, d=None: phases.append(ph))
        self.assertIn('harvest', phases)
        self.assertIn('plan', phases)

    def test_ranked_series_in_flight_defers_candidate_activation(self):
        self.cycle()   # dev coverage requested and harvested next cycle
        self.cycle(now=self.now + 600)
        # an autoscrim series involving us, still running, appears in the recent history
        sid = 777777
        self.server.series[sid] = dict(match=dict(id=sid, seriesId=f's{sid}', requestedBy='autoscrim', requestedAt=ISO(self.now + 1100), _requested=self.now + 1100, teamAId=TEAM, teamBId=999,
                                                  submissionAId=9508, submissionBId=1, ranked=True, status='running', winner=None, replayKey='r', mapHash='x'), games=[dict(id=sid, mapId=9, seed='x')])
        s = self.cycle(now=self.now + 1200)
        self.assertTrue(any(d['reason'] == 'ranked_series_in_flight' for d in s['deferred']), s['deferred'])
        self.assertFalse(any(d['submission'] == 9980 for d in s['dispatched']))
        self.assertEqual(self.server.active, 9508)
        self.server.series[sid]['match']['status'] = 'completed'
        s2 = self.cycle(now=self.now + 1800)
        self.assertFalse(any(d['reason'] == 'ranked_series_in_flight' for d in s2['deferred']))

    def test_dev_only_candidate_is_never_screened(self):
        self.conn.execute("UPDATE candidates SET dev_only=1 WHERE name='cand'")
        for i in range(4):
            s = self.cycle(now=self.now + 600 * i)
        self.assertEqual(self.conn.execute("SELECT status FROM candidates WHERE name='cand'").fetchone()[0], 'dev_done')
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0], 0)
        self.assertFalse([c for c in self.server.calls if c == ('POST', '/api/v1/battles')][12:])   # only the dev batches

    def test_stage_snapshots_include_r25_and_r50(self):
        self.cycle(); self.cycle(now=self.now + 600)
        g = self.conn.execute("SELECT stages, decoder_revision FROM games WHERE verified=1 LIMIT 1").fetchone()
        st = json.loads(g['stages'])
        self.assertIn('25', st); self.assertIn('50', st); self.assertIn('499', st)
        self.assertEqual(g['decoder_revision'], executor.DECODER_REVISION)

    def test_promotion_requires_six_blocks_with_pair_test_and_activates(self):
        self.make_candidate_win()
        for i in range(70):   # 9 blocks x 40 games at the 45/hour executor cap ≈ 8 hours
            self.cycle(now=self.now + 600 * i)
        e = db.rows(self.conn, "SELECT status, verdict, decision FROM experiments")
        self.assertTrue(e)
        self.assertEqual(e[0]['status'], 'promote', e[0])
        d = json.loads(e[0]['decision'])
        self.assertLessEqual(d['p'], 0.025)
        self.assertGreaterEqual(d['positive_blocks'], 4)
        self.assertEqual(self.server.active, 9980)
        self.assertEqual(db.kv_get(self.conn, 'control'), 9980)
        self.assertTrue(db.kv_get(self.conn, 'probation'))
        blocks = self.conn.execute("SELECT COUNT(*) FROM blocks WHERE phase='confirm'").fetchone()[0]
        self.assertEqual(blocks, 6)

    def test_pair_level_sign_test(self):
        self.assertEqual(stats.sign_test_one_sided(0, 0), 1.0)
        self.assertAlmostEqual(stats.sign_test_one_sided(71, 49), 0.0272, places=3)   # 71 of 120 discordant: just outside alpha
        self.assertLess(stats.sign_test_one_sided(72, 48), 0.025)
        self.assertEqual(stats.sign_test_one_sided(3, 0), 0.125)


if __name__ == '__main__':
    unittest.main()

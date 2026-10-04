"""Daemon-level behaviour that the executor tests do not cover: auto-cutover sequencing and self-redeploy gating.
Run: python -m unittest tests.test_hub_daemon
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.hub import actuator, db  # noqa: E402
from tools.hub.config import load_config, set_mode  # noqa: E402


def iso(ts):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


class DaemonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'
        self.root.mkdir()
        self.live = self.tmp / 'live'
        (self.live / 'state').mkdir(parents=True)
        self.repo = self.tmp / 'repo'
        (self.repo / 'hub-state' / 'control').mkdir(parents=True)
        (self.root / 'hub.toml').write_text(f'[paths]\nrepo = "{self.repo}"\nlegacy_live = "{self.live}"\nmirror = "{self.repo}/hub-state"\npython = "{sys.executable}"\n[notify]\nosascript = false\n[team]\nid = 7\ndev_opponents = [545, 752]\n')
        self.cfg = load_config(self.root)
        self.conn = db.connect(self.root)
        self.logs = []
        self.log = self.logs.append
        (self.live / 'state/state.json').write_text(json.dumps(dict(incumbent=9508, experiments=[], requests=[])))
        self.status(state='running', jobs={})

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.tmp)

    def status(self, state='running', jobs=None, age=0):
        (self.live / 'state/runner_status.json').write_text(json.dumps(dict(at=iso(time.time() - age), state=state, jobs=jobs or {}, incumbent=9508)))

    def test_auto_cutover_waits_for_drain_then_adopts_and_goes_live(self):
        state = {'mode': 'shadow', 'configured': 'auto', 'cutover_pending': True}
        db.upsert(self.conn, 'experiments', dict(id='legacy1', candidate_name='yuna', candidate_submission=10013, control_submission=9508, protocol='v1', status='running', map_ids=[1]), 'id')
        with patch.object(actuator, 'legacy_alive', return_value=True):
            self.assertEqual(actuator.auto_cutover(self.root, self.cfg, state, self.log), 'draining')
        self.assertTrue((self.live / 'state/runner.stop').exists())        # stop requested, nothing else yet
        self.assertEqual(state['mode'], 'shadow')
        self.status(state='stopping', jobs={'controller': {'pid': 1}})     # still draining a job
        with patch.object(actuator, 'legacy_alive', return_value=True):
            self.assertEqual(actuator.auto_cutover(self.root, self.cfg, state, self.log), 'draining')
        self.assertEqual(self.conn.execute("SELECT status FROM experiments WHERE id='legacy1'").fetchone()[0], 'running')
        self.status(state='stopping', jobs={})                             # drained
        with patch.object(actuator, 'legacy_alive', return_value=False):
            self.assertEqual(actuator.auto_cutover(self.root, self.cfg, state, self.log), 'live')
        self.assertEqual(state['mode'], 'live')
        self.assertEqual(self.conn.execute("SELECT status FROM experiments WHERE id='legacy1'").fetchone()[0], 'superseded_by_cutover')
        self.assertTrue(db.kv_get(self.conn, 'cutover'))
        self.assertTrue(db.kv_get(self.conn, 'legacy_adopted'))
        self.assertEqual(db.kv_get(self.conn, 'control'), 9508)

    def test_auto_cutover_never_forces_an_open_transaction(self):
        state = {'mode': 'shadow', 'configured': 'auto', 'cutover_pending': True, 'cutover_started': time.time() - 4000}
        (self.live / 'state/runner.stop').touch()
        (self.live / 'state/state.json').write_text(json.dumps(dict(incumbent=9508, switch=dict(candidate=1, previous=9508))))
        self.status(state='stopping', jobs={}, age=600)
        with patch.object(actuator, 'legacy_alive', return_value=False):
            self.assertEqual(actuator.auto_cutover(self.root, self.cfg, state, self.log), 'draining')
        self.assertTrue(state.get('cutover_paged'))
        self.assertEqual(state['mode'], 'shadow')

    def test_mode_request_sets_hub_toml_and_restarts(self):
        ctl = self.repo / 'hub-state' / 'control'
        ctl.joinpath('mode.json').write_text(json.dumps(dict(mode='shadow', by='director', note='teammates own uploads')))
        state = {'mode': 'live', 'configured': 'auto'}
        actuator.mode_check(self.root, self.cfg, state, self.log)
        done = json.loads((ctl / 'mode.done.json').read_text())
        self.assertEqual(done['mode'], 'shadow')
        self.assertEqual(state['restart'], 'set_mode shadow')
        self.assertFalse((ctl / 'mode.json').exists())
        self.assertEqual(load_config(self.root)['executor']['mode'], 'shadow')
        ctl.joinpath('mode.json').write_text(json.dumps(dict(mode='bogus')))
        state = {'mode': 'live', 'configured': 'shadow'}
        actuator.mode_check(self.root, self.cfg, state, self.log)
        self.assertIn('error', json.loads((ctl / 'mode.done.json').read_text()))
        self.assertFalse(state.get('restart'))
        self.assertEqual(load_config(self.root)['executor']['mode'], 'shadow')

    def test_redeploy_rejects_hash_mismatch_and_accepts_after_gate(self):
        ctl = self.repo / 'hub-state' / 'control'
        (self.repo / 'tools' / 'hub').mkdir(parents=True)
        (self.repo / 'tools' / 'hub' / 'x.py').write_text('a = 1\n')
        ctl.joinpath('redeploy.json').write_text(json.dumps(dict(note='t', expect={'tools/hub/x.py': 'deadbeef'})))
        state = {'mode': 'live'}
        actuator.redeploy_check(self.root, self.cfg, state, self.log)
        rej = json.loads((ctl / 'redeploy.rejected.json').read_text())
        self.assertIn('sha256', rej['reason'])
        self.assertFalse((ctl / 'redeploy.json').exists())
        self.assertFalse(state.get('restart'))
        # correct hash, gate passes (subprocess stubbed), deploy succeeds -> done + restart requested
        digest = actuator.sha256_file(self.repo / 'tools' / 'hub' / 'x.py')
        ctl.joinpath('redeploy.json').write_text(json.dumps(dict(note='t2', expect={'tools/hub/x.py': digest})))
        calls = []

        def fake_run(cmd, **kw):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout='abc1234\n' if 'rev-parse' in cmd else 'ok', stderr='')
        with patch.object(actuator.subprocess, 'run', fake_run):
            actuator.redeploy_check(self.root, self.cfg, state, self.log)
        done = json.loads((ctl / 'redeploy.done.json').read_text())
        self.assertTrue(done['sha'].startswith('abc1234-'))
        self.assertTrue(state.get('restart'))
        self.assertTrue(any('unittest' in c for c in calls) and any('deploy' in c for c in calls))

    def test_redeploy_rejects_failing_gate(self):
        ctl = self.repo / 'hub-state' / 'control'
        ctl.joinpath('redeploy.json').write_text(json.dumps(dict(note='bad', expect={})))
        state = {'mode': 'live'}

        def fake_run(cmd, **kw):
            return subprocess.CompletedProcess(cmd, 1 if 'unittest' in cmd else 0, stdout='', stderr='FAILED (errors=1)')
        with patch.object(actuator.subprocess, 'run', fake_run):
            actuator.redeploy_check(self.root, self.cfg, state, self.log)
        rej = json.loads((ctl / 'redeploy.rejected.json').read_text())
        self.assertEqual(rej['reason'], 'gate tests failed')
        self.assertFalse(state.get('restart'))

    def test_frozen_status_file_counts_as_drained(self):
        # the legacy worker died with a controller job still listed in its last status write (28 Sep 13:22 UTC)
        state = {'mode': 'shadow', 'configured': 'auto', 'cutover_pending': True, 'cutover_started': time.time() - 30}
        (self.live / 'state/runner.stop').touch()
        self.status(state='stopping', jobs={'controller': {'pid': 1}}, age=900)
        with patch.object(actuator, 'legacy_alive', return_value=False):
            self.assertEqual(actuator.auto_cutover(self.root, self.cfg, state, self.log), 'live')
        self.assertEqual(state['mode'], 'live')

    def test_register_request_freezes_and_reports(self):
        bot = self.repo / 'bots' / 'tst-s01'
        bot.mkdir(parents=True)
        (bot / 'bot.toml').write_text('[project]\nlanguage = "py"\ninclude = ["*.py"]\n')
        (bot / 'main.py').write_text('print("PROTOCOL 3")\n')
        (bot / 'CANDIDATE.toml').write_text('name = "tst-s01"\nlineage = "tst"\nauthor = "t/tst/1"\nlanguage = "python"\nhypothesis = "h"\nmechanism = "m"\nexpected_change = "e"\npriority = 300\n[activation_contract]\nkind = "trace_marker"\nmarkers = [["ACT:x", 0, 500, 1]]\n')
        ctl = self.repo / 'hub-state' / 'control'
        ctl.joinpath('register.json').write_text(json.dumps(dict(note='t', candidates=[dict(dir='bots/tst-s01', priority=120), dict(dir='bots/missing')])))
        actuator.register_check(self.root, self.cfg, {}, self.log)
        done = json.loads((ctl / 'register.done.json').read_text())
        self.assertEqual(done['results'][0]['name'], 'tst-s01')
        self.assertEqual(done['results'][0]['status'], 'needs_runtime')
        self.assertEqual(done['results'][0]['priority'], 120)
        self.assertIn('error', done['results'][1])
        self.assertFalse((ctl / 'register.json').exists())
        self.assertEqual(self.conn.execute("SELECT priority FROM candidates WHERE name='tst-s01'").fetchone()[0], 120)
        # re-prioritising an existing candidate by name
        ctl.joinpath('register.json').write_text(json.dumps(dict(candidates=[dict(name='tst-s01', priority=410, reason='t'), dict(name='nope', priority=1)])))
        actuator.register_check(self.root, self.cfg, {}, self.log)
        done = json.loads((ctl / 'register.done.json').read_text())
        self.assertEqual((done['results'][0]['priority'], done['results'][0]['was']), (410, 120))
        self.assertIn('unknown', done['results'][1]['error'])
        self.assertEqual(self.conn.execute("SELECT priority FROM candidates WHERE name='tst-s01'").fetchone()[0], 410)
        # a second request for the same directory is reported, not applied twice
        ctl.joinpath('register.json').write_text(json.dumps(dict(candidates=[dict(dir='bots/tst-s01')])))
        actuator.register_check(self.root, self.cfg, {}, self.log)
        done = json.loads((ctl / 'register.done.json').read_text())
        self.assertIn('already registered', done['results'][0]['error'])

    def test_director_restore_control(self):
        class Client:
            def __init__(self):
                self.subs = {9508: dict(id=9508, name='Bifrost v18', status='idle'), 9943: dict(id=9943, name='Heimdall v10', status='active'), 10376: dict(id=10376, name='LV-sakura-ed44cf2d-ai', status='idle')}
                self.posts = []

            def get(self, path):
                return list(self.subs.values())

            def post(self, path, body, content_type='application/json'):
                self.posts.append(path)
                sid = int(path.split('/')[-2])
                for s in self.subs.values():
                    s['status'] = 'active' if s['id'] == sid else 'idle'
                return dict(ok=True)
        client = Client()
        ctl = self.repo / 'hub-state' / 'control'
        # refused: the active submission is a teammate's bot and no force
        ctl.joinpath('restore.json').write_text(json.dumps(dict(previous=9508, candidate=9943, reason='t', by='director')))
        actuator.restore_check(self.root, self.cfg, {}, client, self.log)
        self.assertIn('refused', json.loads((ctl / 'restore.done.json').read_text())['result'])
        self.assertFalse(client.posts)
        # forced by the director: restored and control set
        ctl.joinpath('restore.json').write_text(json.dumps(dict(previous=9508, candidate=9943, reason='the executor restored to the wrong previous control', by='claude/director/x', force=True)))
        actuator.restore_check(self.root, self.cfg, {}, client, self.log)
        out = json.loads((ctl / 'restore.done.json').read_text())
        self.assertIn('restored 9508', out['result'])
        self.assertEqual(client.posts, ['/api/v1/submissions/9508/activate'])
        self.assertEqual(db.kv_get(self.conn, 'control'), 9508)
        # refused: the named candidate is no longer active
        ctl.joinpath('restore.json').write_text(json.dumps(dict(previous=9508, candidate=9943, force=True)))
        actuator.restore_check(self.root, self.cfg, {}, client, self.log)
        self.assertIn('refused', json.loads((ctl / 'restore.done.json').read_text())['result'])

    def test_git_request_runs_the_keeper_now_with_the_requested_quiet_period(self):
        ctl = self.repo / 'hub-state' / 'control'
        ctl.joinpath('git.json').write_text(json.dumps(dict(by='director', note='sync', quiet_minutes=0)))
        seen = {}

        def fake_sync(repo, root, policy, actor='x', dry_run=False, now=None):
            seen.update(policy=policy, actor=actor)
            return dict(committed=['a'], skipped=[], merged=True, pushed=True, errors=[], attention=[])
        with patch.object(actuator, 'git_sync', fake_sync):
            actuator.git_check(self.root, self.cfg, {}, self.log)
        out = json.loads((ctl / 'git.done.json').read_text())
        self.assertEqual(out['report']['committed'], ['a'])
        self.assertEqual(seen['policy']['quiet_minutes'], 0)
        self.assertEqual(seen['actor'], 'director')
        self.assertFalse((ctl / 'git.json').exists())

    def test_git_request_merges_named_local_branches_first(self):
        ctl = self.repo / 'hub-state' / 'control'
        r = subprocess.run
        env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
        os.environ.update({k: env[k] for k in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL')})   # the merge commit needs an identity on a bare VM too
        for cmd in (['git', 'init', '-q', '-b', 'main'], ['git', 'commit', '-q', '--allow-empty', '-m', 'root'], ['git', 'checkout', '-q', '-b', 'cx/f'],):
            r(cmd, cwd=self.repo, env=env, check=True)
        (self.repo / 'from_branch.md').write_text('x\n')
        r(['git', 'add', 'from_branch.md'], cwd=self.repo, env=env, check=True)
        r(['git', 'commit', '-q', '-m', 'branch work'], cwd=self.repo, env=env, check=True)
        r(['git', 'checkout', '-q', 'main'], cwd=self.repo, env=env, check=True)
        ctl.joinpath('git.json').write_text(json.dumps(dict(by='director', note='merge', quiet_minutes=0, merge=['cx/f', 'no/such'])))
        with patch.object(actuator, 'git_sync', lambda repo, root, policy, actor='x', dry_run=False, now=None: dict(committed=[], skipped=[], merged=None, pushed=None, errors=[], attention=[])):
            actuator.git_check(self.root, self.cfg, {}, self.log)
        out = json.loads((ctl / 'git.done.json').read_text())
        self.assertTrue((self.repo / 'from_branch.md').exists())
        self.assertEqual(out['merged_branches'][0], dict(branch='cx/f', merged=True))
        self.assertIn('error', out['merged_branches'][1])

    def test_git_request_pushes_named_branches_to_origin(self):
        ctl = self.repo / 'hub-state' / 'control'
        r = subprocess.run
        env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
        os.environ.update({k: env[k] for k in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL')})
        origin = self.tmp / 'origin.git'
        r(['git', 'init', '-q', '--bare', str(origin)], check=True)
        for cmd in (['git', 'init', '-q', '-b', 'main'], ['git', 'commit', '-q', '--allow-empty', '-m', 'root'], ['git', 'remote', 'add', 'origin', str(origin)],
                    ['git', 'checkout', '-q', '-b', 'r/ra'], ['git', 'commit', '-q', '--allow-empty', '-m', 'lane'], ['git', 'checkout', '-q', 'main']):
            r(cmd, cwd=self.repo, env=env, check=True)
        ctl.joinpath('git.json').write_text(json.dumps(dict(by='director', note='push', quiet_minutes=0, push_branches=['r/ra', 'no/such', 'bad name'])))
        with patch.object(actuator, 'git_sync', lambda repo, root, policy, actor='x', dry_run=False, now=None: dict(committed=[], skipped=[], merged=None, pushed=None, errors=[], attention=[])):
            actuator.git_check(self.root, self.cfg, {}, self.log)
        out = json.loads((ctl / 'git.done.json').read_text())
        self.assertEqual(out['pushed_branches'][0], dict(branch='r/ra', pushed=True))
        self.assertIn('error', out['pushed_branches'][1])
        self.assertEqual(out['pushed_branches'][2]['error'], 'bad branch name')
        self.assertIn('r/ra', r(['git', 'branch', '--list', 'r/ra'], cwd=origin, capture_output=True, text=True).stdout)

    def test_git_request_fetches_remote_branch_before_merging(self):
        ctl = self.repo / 'hub-state' / 'control'
        r = subprocess.run
        env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
        os.environ.update({k: env[k] for k in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL')})
        origin = self.tmp / 'origin.git'; other = self.tmp / 'other'
        r(['git', 'init', '-q', '--bare', '-b', 'main', str(origin)], check=True)
        for cmd in (['git', 'init', '-q', '-b', 'main'], ['git', 'commit', '-q', '--allow-empty', '-m', 'root'], ['git', 'remote', 'add', 'origin', str(origin)], ['git', 'push', '-q', '-u', 'origin', 'main']):
            r(cmd, cwd=self.repo, env=env, check=True)
        r(['git', 'clone', '-q', str(origin), str(other)], env=env, check=True)     # another host pushes a lane branch
        for cmd in (['git', 'checkout', '-q', '-b', 'r/hb1'], ['git', 'commit', '-q', '--allow-empty', '-m', 'lane'], ['git', 'push', '-q', '-u', 'origin', 'r/hb1']):
            r(cmd, cwd=other, env=env, check=True)
        ctl.joinpath('git.json').write_text(json.dumps(dict(by='director', note='merge', quiet_minutes=0, merge=['origin/r/hb1'])))
        with patch.object(actuator, 'git_sync', lambda repo, root, policy, actor='x', dry_run=False, now=None: dict(committed=[], skipped=[], merged=None, pushed=None, errors=[], attention=[])):
            actuator.git_check(self.root, self.cfg, {}, self.log)
        out = json.loads((ctl / 'git.done.json').read_text())
        self.assertEqual(out['merged_branches'][0], dict(branch='origin/r/hb1', merged=True))
        self.assertIn('lane', r(['git', 'log', '--oneline', '-3'], cwd=self.repo, capture_output=True, text=True).stdout)

    def test_set_mode_rewrites_or_appends_executor_section(self):
        set_mode(self.root, 'off')
        text = (self.root / 'hub.toml').read_text()
        self.assertIn('[executor]\nmode = "off"', text)
        set_mode(self.root, 'auto')
        text = (self.root / 'hub.toml').read_text()
        self.assertEqual(text.count('mode = '), 1)
        self.assertEqual(load_config(self.root)['executor']['mode'], 'auto')


if __name__ == '__main__':
    unittest.main()


class CorpusTest(unittest.TestCase):
    def setUp(self):
        from tools.hub import corpus
        self.corpus = corpus
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'; self.root.mkdir()
        self.repo = self.tmp / 'repo'; self.repo.mkdir()
        (self.root / 'hub.toml').write_text(f'[paths]\nrepo = "{self.repo}"\nlegacy_live = "{self.tmp}/live"\nmirror = "{self.repo}/hub-state"\n[team]\nid = 7\n[corpus]\nenabled = true\nper_team = 3\ntop_n = 2\nband = [50, 51]\n')
        self.cfg = load_config(self.root)
        self.cfg['corpus']['teams'] = [dict(id=306, games=4, why='top')]
        self.cfg['corpus']['include_own_team'] = False   # the fixtures below describe the field-only watch list
        self.calls = []
        test = self

        class Client:
            base = 'https://example'

            def get(self, path):
                test.calls.append(path)
                gid = int(path.rsplit('/', 1)[1])
                team = {1: 306, 2: 62, 3: 999, 4: 998}.get(gid // 100, 306)   # the fixture's game ids are numbered by team
                return dict(match=dict(id=gid, seriesId=f's{gid // 5}', teamAId=team if gid % 2 else 45, teamBId=45 if gid % 2 else team, submissionAId=None, submissionBId=None,
                                       ranked=True, requestedAt='2026-09-28T14:05:00Z', requestedBy='autoscrim', mapId=9, winner='a', status='completed', seed='x'), mapName='Schooltime')

            def download_replay(self, gid, dest):
                test.calls.append(f'replay {gid}')
                Path(dest).write_bytes(b'REPLAY' + str(gid).encode())
        self.client = Client()
        self.ladder = [dict(id=306, rank=1, rating=2147), dict(id=62, rank=40), dict(id=45, rank=59), dict(id=999, rank=50), dict(id=998, rank=51), dict(id=545, rank=15, dev=True), dict(id=7, rank=68)]

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_watch_list_merges_explicit_top_and_band_and_excludes_us(self):
        w = self.corpus.watch_list(self.cfg, self.ladder)
        self.assertEqual(w[306]['target'], 4)
        self.assertIn(62, w)          # top 2 (306, 62); 545 is dev and skipped
        self.assertIn(999, w); self.assertIn(998, w)   # band 50-51
        self.assertNotIn(7, w); self.assertNotIn(545, w)

    def test_own_team_is_watched_and_refreshed_first_when_opted_in(self):
        self.cfg['corpus'].update(include_own_team=True, own_team_games=5)
        w = self.corpus.watch_list(self.cfg, self.ladder)
        self.assertIn(7, w); self.assertEqual(w[7]['target'], 5); self.assertTrue(w[7].get('own'))
        order = []

        def discover(tid, n):
            order.append(tid)
            return {7: [701, 702], 306: [101]}.get(tid, [])
        self.corpus.fetch_pass(self.root, self.cfg, self.client, None, discover=discover, ladder=self.ladder)
        self.assertEqual(order[0], 7)
        index = (self.repo / 'public_replays/corpus/index.jsonl').read_text()
        self.assertIn('"game_id": 701', index)

    def test_fetch_pass_downloads_new_games_within_caps_and_indexes_them(self):
        discovered = {306: [101, 102, 103, 104, 105, 106], 62: [201, 202, 203], 999: [301], 998: []}
        with patch.object(self.corpus, 'header', lambda p: dict(bot_a='A', bot_b='B', map_hash='h', map_name='Schooltime', version=2)):
            r1 = self.corpus.fetch_pass(self.root, self.cfg, self.client, None, discover=lambda tid, n: discovered[tid], max_downloads=5, ladder=self.ladder)
        self.assertEqual(r1['fetched'], 5)
        index = self.corpus.load_index(self.repo / 'public_replays' / 'corpus')
        self.assertEqual(len(index), 5)
        row = index[101]
        self.assertEqual((row['team_a'], row['watch_team'], row['autoscrim_window'], row['bot_a']), (306, 306, True, 'A'))
        self.assertTrue((self.repo / 'public_replays' / 'corpus' / 'replays' / '101.replay').exists())
        self.assertTrue(list((self.repo / 'public_replays' / 'corpus' / 'ladder').glob('*.json')))
        # second pass: nothing re-downloaded, remaining targets served
        calls_before = len(self.calls)
        with patch.object(self.corpus, 'header', lambda p: dict(bot_a='A', bot_b='B', map_hash='h', map_name='Schooltime', version=2)):
            r2 = self.corpus.fetch_pass(self.root, self.cfg, self.client, None, discover=lambda tid, n: discovered[tid], max_downloads=40, ladder=self.ladder)
        self.assertFalse(any(c == 'replay 101' for c in self.calls[calls_before:]))
        self.assertGreater(r2['fetched'], 0)
        teams = json.loads((self.repo / 'public_replays' / 'corpus' / 'teams.json').read_text())['teams']
        self.assertIn('306', teams)
        self.assertTrue(teams['306']['checked_at'])

    def test_targets_are_floors_new_games_keep_arriving_after_backfill(self):
        discovered = {306: [101, 102, 103, 104], 62: [201, 202, 203], 999: [301, 302, 303], 998: [401, 402, 403]}
        hdr = lambda p: dict(bot_a='A', bot_b='B', map_hash='h', map_name='Schooltime', version=2)
        with patch.object(self.corpus, 'header', hdr):
            for _ in range(3):
                self.corpus.fetch_pass(self.root, self.cfg, self.client, None, discover=lambda tid, n: discovered[tid], max_downloads=40, ladder=self.ladder)
        teams = json.loads((self.repo / 'public_replays' / 'corpus' / 'teams.json').read_text())['teams']
        self.assertTrue(all(v['have'] >= v['target'] for v in teams.values()), teams)
        # every target met: a new game in 306's public history is still fetched (refresh), and the least recently checked team goes first
        discovered[306] = [107] + discovered[306]
        seen = []
        with patch.object(self.corpus, 'header', hdr):
            r = self.corpus.fetch_pass(self.root, self.cfg, self.client, None, discover=lambda tid, n: seen.append((tid, n)) or discovered[tid], max_downloads=40, ladder=self.ladder)
        self.assertEqual(r['refreshed'], 1)
        self.assertIn(107, self.corpus.load_index(self.repo / 'public_replays' / 'corpus'))
        self.assertTrue(all(n == 25 for _, n in seen))   # refresh discovery reads the newest page only
        self.assertNotEqual(r.get('note'), 'all targets met')


class ThroughputTest(unittest.TestCase):
    """D-025: the shared paced client, 429 handling, discovery caching and the corpus thread's yielding."""

    def test_client_pacing_is_shared_across_threads_and_a_429_pauses_everyone(self):
        import threading
        from tools.hub.api import Client, APIError
        c = Client(REPO, min_interval=0.05, key='k')
        stamps = []

        def worker():
            for _ in range(5):
                c.pace()
                stamps.append(time.monotonic())
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        stamps.sort()
        gaps = [b - a for a, b in zip(stamps, stamps[1:])]
        self.assertEqual(len(stamps), 15)
        self.assertGreaterEqual(min(gaps), 0.045)
        c.note_throttle(1)
        t0 = time.monotonic()
        c.pace()
        self.assertGreaterEqual(time.monotonic() - t0, 0.9)
        self.assertEqual(c.throttled, 1)
        # a 429 on a read is retried after the pause; the second answer succeeds
        answers = [APIError(429, 'slow down', 1), {'ok': True}]
        c.paused_until = 0

        def fake_request(path, body=None, content_type='application/json', timeout=60):
            a = answers.pop(0)
            if isinstance(a, Exception):
                c.note_throttle(0.2)
                raise a
            return a
        c._request = fake_request
        self.assertEqual(c.get('/api/v1/x'), {'ok': True})

    def test_corpus_discovery_is_cached_for_backfill_and_fresh_for_refresh(self):
        from tools.hub import corpus
        corpus.DISCOVERY.clear()
        calls = []
        discover = lambda tid, n: calls.append((tid, n)) or [1, 2, 3]
        have = {}
        self.assertEqual(corpus.cached_discover(discover, 306, 420, have, 'backfill'), [1, 2, 3])
        self.assertEqual(corpus.cached_discover(discover, 306, 420, have, 'backfill'), [1, 2, 3])
        self.assertEqual(len(calls), 1)                      # second backfill call within the TTL reuses the listing
        have = {1: 1, 2: 1, 3: 1}
        corpus.cached_discover(discover, 306, 420, have, 'backfill')
        self.assertEqual(len(calls), 2)                      # exhausted listing: re-read
        corpus.cached_discover(discover, 306, 25, have, 'refresh')
        self.assertEqual(len(calls), 3)                      # a refresh always reads the newest page
        corpus.DISCOVERY.clear()

    def test_corpus_thread_yields_to_the_executor_and_stops(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            stop = tmp / 'stop'
            state = {'executor_busy': True}
            passes = []

            def fake_pass(root, cfg, client, log, should_yield=None):
                passes.append(should_yield())
                return dict(fetched=1, throttled=0)
            with patch.object(actuator.hub_corpus, 'fetch_pass', fake_pass):
                import threading
                th = threading.Thread(target=actuator.corpus_thread, args=(tmp, {'corpus': {'interval_seconds': 0.05}}, state, object(), lambda m: None, stop), daemon=True)
                th.start()
                time.sleep(0.3)
                self.assertEqual(passes, [])                  # busy executor: no pass
                state['executor_busy'] = False
                time.sleep(1.5)
                self.assertGreater(len(passes), 1)            # continuous passes once the executor is idle
                self.assertTrue(all(p is False for p in passes))
                stop.write_text('')
                th.join(3)
                self.assertFalse(th.is_alive())
                self.assertEqual(state['corpus_last']['fetched'], 1)
        finally:
            shutil.rmtree(tmp)

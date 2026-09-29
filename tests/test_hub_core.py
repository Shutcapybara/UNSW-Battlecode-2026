"""Hub acceptance tests (Part B §13, day-one subset). Run: python -m unittest discover -s tests -p 'test_hub_*.py'.

Fixture-based tests read a snapshot of the legacy live-validation directory from $JKS_HUB_FIXTURE or
<repo>/build/hub-fixture (git-ignored); they are skipped when no snapshot is present.
"""
import json
import os
import shutil
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(REPO))
from tools.hub import db, stats, contracts, priority, candidates, records  # noqa: E402
from tools.hub.config import load_config  # noqa: E402
from tools.hub.legacy_import import import_legacy, lineage_of  # noqa: E402
from tools.hub.cycle import run_cycle  # noqa: E402
from tools.hub.toml_lite import _Parser  # noqa: E402

FIXTURE = Path(os.environ.get('JKS_HUB_FIXTURE') or REPO / 'build' / 'hub-fixture')


def block(bid, phase, control, candidate, opponent, maps, requests):
    return dict(id=bid, phase=phase, control=control, candidate=candidate, opponent=opponent, map_ids=maps, experiment='e', requests=requests)


def result(gid, sub, map_id, score, side='A', opp_sub=1, faults=0, verified=True):
    return dict(game_id=gid, submission=sub, map_id=map_id, side=side, opponent_submission=opp_sub, map_hash='h', score=score,
                longest_margin=0, faults=faults, caught_errors=0, verified=verified)


class TomlLiteTest(unittest.TestCase):
    def test_subset(self):
        text = '''# c
name = "a-b"
n = 1_000
f = 1.5
ok = true
arr = [["ACT:x", 0, 100, 5], ["ACT:y", 300, 500, 1]]
inline = {field = 60, dev = 60}
[table.sub]
k = "v"
'''
        got = _Parser(text).parse()
        self.assertEqual(got['name'], 'a-b')
        self.assertEqual(got['n'], 1000)
        self.assertEqual(got['arr'][1], ['ACT:y', 300, 500, 1])
        self.assertEqual(got['inline'], {'field': 60, 'dev': 60})
        self.assertEqual(got['table']['sub']['k'], 'v')


class StatsTest(unittest.TestCase):
    def test_quota_counts_games_not_series_and_reservations(self):
        now = time.time()
        iso = lambda t: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))
        series = [dict(match=dict(requestedBy='m1', requestedAt=iso(now - 100), seriesId='s1', teamAId=7, teamBId=62), games=[dict(id=1), dict(id=2)]),
                  dict(match=dict(requestedBy='m1', requestedAt=iso(now - 100), seriesId='s1', teamAId=7, teamBId=62), games=[dict(id=1), dict(id=2)]),
                  dict(match=dict(requestedBy='x', requestedAt=iso(now - 100), seriesId='s2', teamAId=7, teamBId=545), games=[dict(id=3)]),
                  dict(match=dict(requestedBy='m2', requestedAt=iso(now - 4000), seriesId='s3', teamAId=7, teamBId=545), games=[dict(id=4)])]
        reservations = [dict(at=now - 10, status='reserved', pool='field', count=10, ids=[]), dict(at=now - 10, status='accepted', pool='dev', ids=[3, 9], count=2)]
        used = stats.quota_used(series, reservations, {'m1', 'm2'}, {545, 752}, now)
        self.assertEqual(used, {'field': 12, 'dev': 1})

    def test_pairing_requires_same_layout_and_submission(self):
        b = block('b1', 'screen', 1, 2, 62, [9, 20], [[101, 102], [201, 202]])
        results = {'101': result(101, 1, 9, 0.0), '102': result(102, 1, 20, 1.0), '201': result(201, 2, 9, 1.0), '202': result(202, 2, 20, 1.0, opp_sub=2)}
        paired = stats.paired_blocks([b], results)[0]
        self.assertEqual([p['map_id'] for p in paired['pairs']], [9])
        self.assertFalse(paired['complete'])
        self.assertEqual(paired['missing_maps'], [20])

    def test_v1_screen_reject_and_v2_futility(self):
        results = {}
        blocks = []
        for i, opp in enumerate((62, 45, 470)):
            reqs = [[], []]
            for m in range(10):
                gid_c, gid_x = 1000 + i * 20 + m, 2000 + i * 20 + m
                results[str(gid_c)] = result(gid_c, 1, m, 1.0)
                results[str(gid_x)] = result(gid_x, 2, m, 0.0 if m < 7 else 1.0)
                reqs[0].append(gid_c)
                reqs[1].append(gid_x)
            blocks.append(block(f'b{i}', 'screen', 1, 2, opp, list(range(10)), reqs))
        self.assertEqual(stats.decision_v1(blocks, results, 0.01)['verdict'], 'reject_screen')
        one = stats.decision_v2(blocks[:1], results)
        self.assertEqual(one['verdict'], 'reject_screen')
        self.assertIn('futility', one['reason'])

    def test_v2_efficacy_once_at_twelve_blocks(self):
        results = {}
        blocks = []
        for i in range(12):
            reqs = [[], []]
            for m in range(10):
                gid_c, gid_x = 1000 + i * 20 + m, 2000 + i * 20 + m
                results[str(gid_c)] = result(gid_c, 1, m, 0.0 if m < 6 else 1.0)
                results[str(gid_x)] = result(gid_x, 2, m, 0.0 if (m == 8 and i < 2) else 1.0)  # map 8 mean delta -2/12 stays above -0.25
                reqs[0].append(gid_c)
                reqs[1].append(gid_x)
            blocks.append(block(f'c{i}', 'confirm', 1, 2, 100 + i, list(range(10)), reqs))
        screen = []
        for i in range(3):
            reqs = [[], []]
            for m in range(10):
                gid_c, gid_x = 5000 + i * 20 + m, 6000 + i * 20 + m
                results[str(gid_c)] = result(gid_c, 1, m, 0.0)
                results[str(gid_x)] = result(gid_x, 2, m, 1.0)
                reqs[0].append(gid_c)
                reqs[1].append(gid_x)
            screen.append(block(f's{i}', 'screen', 1, 2, 60 + i, list(range(10)), reqs))
        partial = stats.decision_v2(screen + blocks[:11], results)
        self.assertEqual(partial['verdict'], 'confirming')
        full = stats.decision_v2(screen + blocks, results)
        self.assertEqual(full['verdict'], 'promote')
        self.assertLessEqual(full['p'], 0.025)
        repeated = stats.decision_v2(screen + blocks[:6] + blocks[:6], results)  # a repeated opponent cannot count twice
        self.assertIn(repeated['verdict'], ('confirming', 'reject_confirmation'))

    def test_blackout(self):
        self.assertTrue(stats.in_blackout(9 * 60 + 55))
        self.assertTrue(stats.in_blackout(10 * 60 + 5))
        self.assertFalse(stats.in_blackout(10 * 60 + 13))
        self.assertFalse(stats.in_blackout(11 * 60))
        self.assertTrue(stats.in_blackout(23 * 60 + 55))


class ContractTest(unittest.TestCase):
    LOG = '\n'.join(['round 0: bot 0 (team A) stdout:', 'PROTOCOL 3', 'MOVE E', 'LOG ACT:prod', 'round 0: bot 0 (team A) points 100 memory 1',
                     'round 0: bot 1 (team B) stdout:', 'LOG ACT:prod', 'round 0: bot 1 (team B) points 100 memory 1',
                     'round 350: bot 0 (team A) stdout:', 'MOVE N', 'LOG ACT:diss ACT:esc', 'round 350: bot 0 (team A) points 100 memory 1'])

    def test_trace_marker(self):
        contract = dict(kind='trace_marker', markers=[['ACT:prod', 0, 100, 1], ['ACT:diss', 300, 500, 1]])
        got = contracts.evaluate(contract, [dict(label='9-A', side='A', log_text=self.LOG)])
        self.assertTrue(got['passed'])
        bad = contracts.evaluate(dict(kind='trace_marker', markers=[['ACT:diss', 0, 100, 1]]), [dict(label='9-A', side='A', log_text=self.LOG)])
        self.assertFalse(bad['passed'])
        other_side = contracts.evaluate(contract, [dict(label='9-B', side='B', log_text=self.LOG)])
        self.assertFalse(other_side['passed'])
        self.assertIsNone(contracts.evaluate(dict(kind='behavioural_signature', statistics=['x >= 1']), [])['passed'])

    def test_points_profile(self):
        got = contracts.points_profile(self.LOG, 'A')
        self.assertEqual(got['turns'], 2)
        self.assertEqual(got['max_points'], 100)


class PriorityTest(unittest.TestCase):
    def test_terms(self):
        now = time.time()
        cand = dict(name='x-s01', lineage='x', mechanism='M', hypothesis='see F-1', novelty='structural')
        ctx = dict(now=now, incumbent_lineage='y', lineage_last_live={}, lineage_live_games={}, lineage_rejected_mechanisms={'x': {'m'}}, probes={'x-s01': dict(max_points=60e6, p99_points=40e6)}, finding_ids={'F-1'})
        s, terms = priority.score(cand, ctx)
        self.assertEqual(terms['already_rejected_same_mechanism'], 1.0)
        self.assertEqual(terms['replay_link'], 1.0)
        self.assertEqual(terms['headroom'], 1.0)
        self.assertLess(s, 0)
        ctx['lineage_rejected_mechanisms'] = {}
        s2, _ = priority.score(cand, ctx)
        self.assertEqual(s2, 40 + 30 + 20 + 25 + 20)


class CandidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'
        self.conn = db.connect(self.root)
        self.bot = self.tmp / 'bots' / 'x-s01-test'
        self.bot.mkdir(parents=True)
        (self.bot / 'bot.toml').write_text('[project]\nlanguage = "py"\ninclude = ["*.py"]\n')
        (self.bot / 'main.py').write_text('print("PROTOCOL 3")\n')
        (self.bot / 'README.md').write_text('# x\n')
        (self.bot / 'CANDIDATE.toml').write_text('''name = "x-s01-test"
lineage = "x"
author = "test/x/1"
language = "python"
lineage_parent = ""
hypothesis = "h"
mechanism = "m"
expected_change = "e"
priority = 250
[activation_contract]
kind = "trace_marker"
markers = [["ACT:prod", 0, 100, 1]]
''')

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.tmp)

    def test_register_freezes_and_refuses_same_code(self):
        row = candidates.register_from_dir(self.conn, self.root, self.bot, 'test/x/1')
        self.assertEqual(row['status'], 'needs_runtime')
        self.assertTrue(Path(row['archive_path']).exists())
        self.assertNotEqual(row['fingerprint'], row['code_fingerprint'])
        (self.bot / 'README.md').write_text('# docs only\n')
        (self.bot / 'CANDIDATE.toml').write_text((self.bot / 'CANDIDATE.toml').read_text().replace('x-s01-test', 'x-s02-docs'))
        with self.assertRaises(ValueError):
            candidates.register_from_dir(self.conn, self.root, self.bot, 'test/x/1')
        (self.bot / 'main.py').write_text('print("PROTOCOL 3")\nprint("MOVE N")\n')
        row2 = candidates.register_from_dir(self.conn, self.root, self.bot, 'test/x/1')
        self.assertEqual(row2['name'], 'x-s02-docs')

    def test_cpp_manifest_registers_with_the_cli_spelling(self):
        (self.bot / 'bot.toml').write_text('[project]\nlanguage = "c++"\ninclude = ["*.cpp", "*.hpp"]\n')
        (self.bot / 'main.py').unlink()
        (self.bot / 'main.cpp').write_text('int main(){return 0;}\n')
        (self.bot / 'CANDIDATE.toml').write_text((self.bot / 'CANDIDATE.toml').read_text().replace('language = "python"', 'language = "c++"'))
        row = candidates.register_from_dir(self.conn, self.root, self.bot, 'test/x/1')
        self.assertEqual(row['language'], 'cpp')
        self.assertEqual(row['status'], 'needs_runtime')

    def test_manifest_validation(self):
        (self.bot / 'CANDIDATE.toml').write_text('name = "BAD NAME"\n')
        with self.assertRaises(ValueError):
            candidates.register_from_dir(self.conn, self.root, self.bot, 'test/x/1')

    def test_supersedes_required_after_live_rejection(self):
        db.upsert(self.conn, 'experiments', dict(id='e1', candidate_name='x-s00-parent', candidate_submission=1, control_submission=2, protocol='v1', status='reject_screen', verdict='reject_screen'), 'id')
        (self.bot / 'CANDIDATE.toml').write_text((self.bot / 'CANDIDATE.toml').read_text().replace('lineage_parent = ""', 'lineage_parent = "x-s00-parent"'))
        with self.assertRaises(ValueError):
            candidates.register_from_dir(self.conn, self.root, self.bot, 'test/x/1')

    def test_tasks_and_findings(self):
        tid = records.create_task(self.conn, self.root, 'test/x/1', 'research', 'T', dict(goal='g', deliverable='finding', done_when='d'), exclusive=True)
        records.claim_task(self.conn, self.root, 'a/1', tid)
        with self.assertRaises(ValueError):
            records.claim_task(self.conn, self.root, 'b/2', tid)
        fid = records.publish_finding(self.conn, self.root, 'a/1', 'hypothesis', 'H', 'body', evidence_refs=[dict(type='file', id='x')], task_id=tid)
        with self.assertRaises(ValueError):
            records.publish_finding(self.conn, self.root, 'a/1', 'correction', 'C', 'body')
        cid = records.publish_finding(self.conn, self.root, 'a/1', 'correction', 'C', 'body', supersedes=fid)
        self.assertEqual(self.conn.execute('SELECT status FROM findings WHERE id=?', (fid,)).fetchone()[0], 'superseded')
        self.assertTrue(cid)


@unittest.skipUnless((FIXTURE / 'state' / 'state.json').exists(), 'no legacy fixture snapshot')
class LegacyImportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'hub'
        (self.root).mkdir()
        (self.root / 'hub.toml').write_text(f'[paths]\nrepo = "{self.tmp}"\nlegacy_live = "{FIXTURE}"\nmirror = "{self.tmp}/hub-state"\n[notify]\nosascript = false\n')
        self.cfg = load_config(self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_import_matches_manifest_and_is_idempotent(self):
        conn = db.connect(self.root)
        m1 = import_legacy(conn, self.root, FIXTURE)
        state = json.loads((FIXTURE / 'state/state.json').read_text())
        self.assertEqual(sum(m1['counts']['results'].values()), len(state['results']))
        self.assertEqual(m1['hub_counts']['games'], len(state['results']))
        self.assertEqual(m1['counts']['blocks'], len(state['blocks']))
        self.assertTrue(m1['checks']['row_counts_cover_manifest'])
        self.assertEqual(db.kv_get(conn, 'incumbent'), state['incumbent'])
        m2 = import_legacy(conn, self.root, FIXTURE)
        self.assertEqual(m2['hub_counts'], m1['hub_counts'])
        for e in db.rows(conn, 'SELECT status, verdict, protocol FROM experiments'):
            self.assertEqual(e['protocol'], 'v1')
            legacy = next(x for x in state['experiments'] if x['status'] == e['status'])
            self.assertEqual(e['status'], legacy['status'])
        conn.close()

    def test_cycle_rederives_verdicts_and_writes_packet(self):
        tick = run_cycle(self.root, self.cfg, actor='test', force_packet=True)
        self.assertTrue(all(e['agree'] for e in tick['experiments']), tick['experiments'])
        packet = Path(tick['packet']).read_text()
        self.assertLessEqual(packet.count('\n'), 300)
        for section in ('## 0. Safety', '## 1. Changes', '## 2. Failures', '## 3. Contradictions', '## 4. Prioritized', '## 5. Queue', '## 6. Decisions'):
            self.assertIn(section, packet)
        self.assertTrue((Path(self.cfg['paths']['mirror']) / 'status.json').exists())
        self.assertTrue((Path(self.cfg['paths']['mirror']) / '.gitignore').exists())
        self.assertEqual(tick['restoration_matched'], json.loads((FIXTURE / 'state/restoration_check.json').read_text())['matched'])
        tick2 = run_cycle(self.root, self.cfg, actor='test')
        self.assertNotIn('packet', tick2)  # no second packet inside the same two-hour window


class LineageTest(unittest.TestCase):
    def test_names(self):
        self.assertEqual(lineage_of('LV-local-yuna-v02-eec84bfe-ai'), 'yuna')
        self.assertEqual(lineage_of('Heimdall v10'), 'heimdall')
        self.assertEqual(lineage_of('local-tidus-t02-spread-only'), 'tidus')


if __name__ == '__main__':
    unittest.main()

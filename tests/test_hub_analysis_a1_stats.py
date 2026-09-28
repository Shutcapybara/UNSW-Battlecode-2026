"""Handoff A1 statistics added 2026-09-28 by glm/analysis/a1: layout parity, first-trailing
stage, runtime table, sonar split, elo trajectory, opponent fingerprints, local-priority gate.
Run: python -m unittest discover -s tests -p 'test_hub_analysis_a1_stats.py'"""
import unittest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.hub import analysis, calibration  # noqa: E402


def _stages(win, units=17, total=74, longest=9, sonar=3900):
    snap = {}
    for r in (100, 200, 250, 300, 320, 360, 380, 400, 450, 499):
        snap[str(r)] = dict(units=units if win else 6, total=total if win else 4, longest=longest if win else 0,
                            deaths=10, death_wall=5, death_h2h=8, newborn_deaths_10=20, splits=30, sonar=sonar,
                            turns=1000, portal_steps=10, pearls=1, length_lost=1)
    return snap


def game(gid, sub=9508, opp=62, score=1.0, reason='roundLimit', map_id=9, map_name='Schooltime',
         verified=True, origin='controlled', pool='field', cpu=50_000_000, stages=None, opp_stages=None,
         map_hash=None, rounds=500):
    return dict(game_id=gid, own_submission=sub, opponent_team=opp, opponent_submission=9343, map_id=map_id,
                map_name=map_name, map_hash=map_hash, api_side='A', pool=pool, origin=origin, verified=verified,
                score=score, longest_margin=3, rounds=rounds, reason=reason, faults=0, cpu_max=cpu,
                stages=stages if stages is not None else _stages(score >= 0.5),
                opponent_stages=opp_stages if opp_stages is not None else _stages(score < 0.5))


class LayoutParityTest(unittest.TestCase):
    def test_two_layout_map_follows_id_parity(self):
        games = [game(10, map_id=9, map_hash='AAAA'), game(11, map_id=9, map_hash='BBBB'),
                 game(12, map_id=9, map_hash='AAAA'), game(13, map_id=9, map_hash='BBBB')]
        lp = analysis.layout_parity(games)
        self.assertEqual(lp[9]['match_rate'], 1.0)
        self.assertEqual(lp[9]['n'], 4)

    def test_one_exception_lowers_rate(self):
        games = [game(10, map_id=9, map_hash='AAAA'), game(11, map_id=9, map_hash='BBBB'),
                 game(12, map_id=9, map_hash='BBBB')]
        lp = analysis.layout_parity(games)
        self.assertEqual(lp[9]['match_rate'], round(2 / 3, 3))
        self.assertEqual(lp[9]['exceptions'], 1)

    def test_three_hash_map_flagged_not_applicable(self):
        games = [game(10, map_id=17, map_hash='A'), game(11, map_id=17, map_hash='B'),
                 game(12, map_id=17, map_hash='C')]
        lp = analysis.layout_parity(games)
        self.assertIsNone(lp[17]['match_rate'])


class TrailingTest(unittest.TestCase):
    def test_loser_behind_from_first_stage(self):
        row = game(1, score=0)
        self.assertEqual(analysis.first_trailing(row), 100)

    def test_never_behind_when_equal(self):
        row = game(1, score=1, stages=_stages(True), opp_stages=_stages(True))
        self.assertIsNone(analysis.first_trailing(row))

    def test_trailing_profile(self):
        rows = [game(1, score=0), game(2, score=1, map_name='Portals')]
        tp = analysis.trailing_profile(rows)
        self.assertEqual(tp['open']['at_or_before_250'], 1.0)
        self.assertEqual(tp['compact']['at_or_before_250'], 1.0)


class RuntimeSonarTest(unittest.TestCase):
    def test_runtime_counts_at_cap(self):
        games = [game(1, cpu=100_000_000), game(2, cpu=95_000_000), game(3, cpu=50_000_000, verified=False)]
        rt = analysis.runtime_table(games)
        row = [r for r in rt if r['submission'] == 9508][0]
        self.assertEqual(row['n'], 2)
        self.assertEqual(row['at_cap'], 1)
        self.assertEqual(row['over_near_cap'], 2)

    def test_sonar_split(self):
        games = []
        for i in range(6):
            games.append(game(i, score=i % 2, stages=_stages(True, sonar=2000 + (1000 if i % 2 else 0))))
        sn = analysis.sonar_table(games)
        row = [r for r in sn if r['submission'] == 9508][0]
        self.assertEqual(row['n'], 6)
        self.assertIn(row['rate_med'], (2.5, 3.0))


class EloTrajectoryTest(unittest.TestCase):
    def test_delta_over_snapshots(self):
        payloads = [
            dict(match=dict(id=100, teamAId=7, teamBId=62, ranked=False), teamAElo=1784, teamBElo=1800),
            dict(match=dict(id=200, teamBId=7, teamAId=45, ranked=True), teamAElo=1790, teamBElo=1750),
            dict(match=dict(id=300, teamAId=8, teamBId=9, ranked=False), teamAElo=1500, teamBElo=1500),
        ]
        t = analysis.elo_trajectory(payloads)
        self.assertEqual(t['first'], 1784)
        self.assertEqual(t['last'], 1750)
        self.assertEqual(t['delta'], -34)
        self.assertEqual(len(t['snapshots']), 2)

    def test_elo_lines_render(self):
        payloads = [dict(match=dict(id=100, teamAId=7, teamBId=62), teamAElo=1784, teamBElo=1800),
                    dict(match=dict(id=200, teamAId=7, teamBId=62), teamAElo=1750, teamBElo=1800)]
        lines = analysis.elo_lines(payloads)
        self.assertEqual(len(lines), 1)
        self.assertIn('-34', lines[0])


class OpponentFingerprintTest(unittest.TestCase):
    def test_fingerprint_fields(self):
        games = [game(1, opp=62, score=0, reason='elimination', rounds=120), game(2, opp=62, score=1)]
        fps = calibration.opponent_fingerprints(games)
        self.assertEqual(len(fps), 1)
        fp = fps[0]
        self.assertEqual(fp['opponent'], 62)
        self.assertEqual(fp['n'], 2)
        self.assertEqual(fp['our_share'], 0.5)
        self.assertEqual(fp['their_elim_round_med'], 120)
        self.assertEqual(fp['sonar_per_turn'], 3.9)


class LocalPriorityGateTest(unittest.TestCase):
    def test_gate_blocks_small_n(self):
        rows = [dict(local_value=0.2, live_value=0.1)] * 9
        g = calibration.local_priority_ok(rows)
        self.assertFalse(g['allowed'])

    def test_gate_passes_with_agreement(self):
        rows = [dict(local_value=0.2 * s, live_value=0.1 * s) for s in (1, 1, 1, 1, 1, 1, 1, 1, -1, -1, 1)]
        g = calibration.local_priority_ok(rows)
        self.assertEqual(g['n'], 11)
        self.assertEqual(g['agreement'], 1.0)
        self.assertTrue(g['allowed'])

    def test_gate_fails_on_disagreement(self):
        rows = [dict(local_value=0.2, live_value=-0.1)] * 10
        g = calibration.local_priority_ok(rows)
        self.assertEqual(g['agreement'], 0.0)
        self.assertFalse(g['allowed'])


class PacketLinesTest(unittest.TestCase):
    def test_a1_packet_lines_render(self):
        a = dict(layout_parity={9: dict(n_hashes=2, match_rate=1.0, exceptions=0, n=40)},
                 runtime=[dict(submission=9508, pool='field', n=10, med=92_000_000, p95=100_000_000,
                               mx=100_000_000, over_near_cap=9, at_cap=5)],
                 sonar=[dict(submission=9508, pool='field', n=10, rate_med=3.91, share_hi=0.4, share_lo=0.5)])
        lines = analysis.packet_lines_a1(a)
        self.assertTrue(any('parity' in l for l in lines))
        self.assertTrue(any('9508' in l and 'at-cap 5' in l for l in lines))


if __name__ == '__main__':
    unittest.main()

"""Tests for the A1 statistics in tools/hub/analysis_a1.py (merged into tools/hub/analysis.run) (loss anatomy, exact-pair contrasts, layout rule, runtime,
sonar). Synthetic game rows in the hub `games` shape; no fixture needed.
Run: python -m unittest tests.test_hub_analysis
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.hub import analysis, analysis_a1  # noqa: E402

MAPS = ['Schooltime', 'Portals', 'Slithery Fight', 'Queen Of Spades', 'Default', 'Trophy', 'Prisoners Dilemma', 'Autarky', 'Devil', 'Trauma']


def layout(map_name, parity):
    """Deterministic stand-in for the server's two starting orientations per map."""
    return f'{map_name[:4].lower().replace(" ", "_")}{parity}'.ljust(8, '0')


def stages(units, total, longest, turns=1000, sonar=None, deaths=0, h2h=0, wall=0, cpu=50_000_000, newborn=0, splits=0):
    """Stage dict with the same value at every stored stage (terminal state carried forward)."""
    return {str(r): dict(units=units, total=total, longest=longest, turns=turns, sonar=(sonar if sonar is not None else 4 * turns), deaths=deaths, death_h2h=h2h,
                         death_wall=wall, death_self=0, death_body=0, cpu_max=cpu, newborn_deaths_10=newborn, splits=splits) for r in analysis_a1.STAGES}


def game(gid, sub, map_name, score, opp_sub=100, side='A', block=None, exp=None, reason=None, cpu=50_000_000, faults=0, own=None, opp=None,
         origin='controlled', pool='field', verified=1, map_hash=None, rounds=500):
    own = own or stages(10, 40, 8, cpu=cpu)
    opp = opp or stages(12, 50, 9)
    return dict(game_id=gid, own_submission=sub, opponent_team=62, opponent_submission=opp_sub, map_id=MAPS.index(map_name), map_name=map_name,
                map_hash=(map_hash or layout(map_name, gid % 2)) + 'x' * 56, api_side=side, pool=pool, origin=origin, verified=verified, score=score,
                longest_margin=(5 if score else -5), rounds=rounds, reason=reason or ('roundLimit' if rounds == 500 else 'elimination'), faults=faults,
                cpu_max=cpu, cpu_recorded=1000, turns=1000, block_id=block, experiment_id=exp, phase='screen' if block else None, stages=own, opponent_stages=opp)


class SignTestTest(unittest.TestCase):
    def test_exact_binomial(self):
        self.assertIsNone(analysis_a1.sign_test_p(0, 0))
        self.assertEqual(analysis_a1.sign_test_p(5, 5), 1.0)
        self.assertAlmostEqual(analysis_a1.sign_test_p(4, 6), 0.754, places=3)
        self.assertAlmostEqual(analysis_a1.sign_test_p(10, 0), 2 / 1024, places=4)


class LossAnatomyTest(unittest.TestCase):
    def rows(self):
        out = []
        for i in range(24):
            compact = i % 2 == 0
            win = i % 3 == 0
            own = stages(15 if win else (0 if compact else 4), 60 if win else (0 if compact else 20), 10 if win else (0 if compact else 3), deaths=10, h2h=(2 if win else 8))
            opp = stages(12, 50, 9)
            out.append(game(1000 + i, 9508, 'Devil' if compact else 'Trauma', 1.0 if win else 0.0, own=own, opp=opp,
                            rounds=(500 if win or not compact else 150), reason=('roundLimit' if win or not compact else 'elimination')))
        return out

    def test_anatomy_counts_and_first_behind(self):
        a = analysis_a1.loss_anatomy(self.rows(), 9508, min_games=20)
        self.assertEqual(a['n'], 24)
        self.assertEqual(a['wins'], 8)
        self.assertEqual(a['losses'], 16)
        self.assertEqual(a['losses_elimination'], 8)          # compact losses are eliminations at r150
        self.assertEqual(a['losses_roundlimit'], 8)
        self.assertEqual(a['elimination_round']['median'], 150)
        self.assertEqual(a['loss_first_behind_total'], {'100': 16})
        self.assertEqual(a['win_first_behind_total'], {'never': 8})
        self.assertEqual(a['share_by_r100_lead']['compact_ahead_r100']['share'], 1.0)
        self.assertEqual(a['share_by_r100_lead']['compact_behind_r100']['share'], 0.0)
        self.assertEqual(a['by_class']['compact']['survival_own']['100'], round(4 / 12, 2))
        self.assertEqual(a['curves']['compact_loss']['deaths_per_1k']['death_h2h'], 8.0)
        self.assertIsNone(analysis_a1.loss_anatomy(self.rows(), 9508, min_games=25))
        self.assertIsNone(analysis_a1.loss_anatomy(self.rows(), 9999, min_games=1))

    def test_terminal_state_is_not_survivor_only(self):
        rows = self.rows()
        # an eliminated side keeps units 0 and total 0 at every later stage; the median over all games must include them
        a = analysis_a1.loss_anatomy(rows, 9508, min_games=20)
        self.assertEqual(a['curves']['compact_loss']['total_r250'], 0)
        self.assertEqual(a['curves']['compact_loss']['units_r100'], 0)
        self.assertEqual(a['curves']['open_loss']['units_r100'], 4)


class PairedContrastTest(unittest.TestCase):
    def rows(self):
        out = []
        # block b1: candidate 9639 vs control 9508, ten games each, ids interleaved so parity (layout) matches per map
        for k, m in enumerate(MAPS):
            gid = 2000 + k
            out.append(game(gid, 9508, m, 1.0 if k < 6 else 0.0, block='b1', exp='e1'))
            out.append(game(gid + 20, 9639, m, 1.0 if k < 4 else 0.0, block='b1', exp='e1'))   # +20 keeps the id parity, hence the layout
        # an unpaired candidate game with the opposite layout
        out.append(game(2109, 9639, 'Devil', 1.0, block='b1', exp='e1'))   # Devil sits at even id 2008; 2109 is the other layout
        # a game outside the experiment must not be paired
        out.append(game(3000, 9639, 'Devil', 1.0, block='b9', exp='e2'))
        return out

    def test_pairs_and_sign_test(self):
        p = analysis_a1.paired_contrast(self.rows(), 9639, 9508, 'e1')
        self.assertEqual(p['pairs'], 10)
        self.assertEqual(p['unpaired'], {9639: 1, 9508: 0})
        self.assertEqual((p['better'], p['same'], p['worse']), (0, 8, 2))
        self.assertAlmostEqual(p['delta'], -0.2)
        self.assertEqual(p['sign_test_p'], 0.5)
        self.assertEqual(p['by_class']['compact']['n'], 4)
        self.assertEqual(p['by_class']['open']['n'], 6)
        self.assertEqual(p['flips']['n'], 2)
        self.assertIsNone(analysis_a1.paired_contrast(self.rows(), 9639, 9508, 'e3'))

    def test_layout_mismatch_is_never_paired(self):
        rows = [game(4000, 9508, 'Devil', 1.0, block='b2', exp='e4'), game(4001, 9639, 'Devil', 0.0, block='b2', exp='e4')]
        self.assertIsNone(analysis_a1.paired_contrast(rows, 9639, 9508, 'e4'))
        rows.append(game(4003, 9639, 'Devil', 0.0, block='b2', exp='e4'))   # same parity as 4001, still not 4000
        self.assertIsNone(analysis_a1.paired_contrast(rows, 9639, 9508, 'e4'))
        rows.append(game(4002, 9639, 'Devil', 0.0, block='b2', exp='e4'))   # same parity as 4000 -> exact pair
        p = analysis_a1.paired_contrast(rows, 9639, 9508, 'e4')
        self.assertEqual(p['pairs'], 1)
        self.assertEqual(p['worse'], 1)


class LayoutRuleTest(unittest.TestCase):
    def test_parity_rule_holds(self):
        rows = [game(5000 + i, 9508, 'Devil' if i % 3 else 'Trauma', 1.0) for i in range(40)]
        r = analysis_a1.layout_rule(rows)
        self.assertEqual(r['violations'], 0)
        self.assertEqual(r['n'], 40)
        self.assertTrue(r['rule'].startswith('layout = f(map, game_id parity)'))
        self.assertEqual(r['maps']['Devil']['hashes'], 2)

    def test_violation_is_counted(self):
        rows = [game(5000 + i, 9508, 'Devil', 1.0) for i in range(10)]
        rows.append(game(5011, 9508, 'Devil', 1.0, map_hash=layout('Devil', 0)))   # odd id with the even layout
        r = analysis_a1.layout_rule(rows)
        self.assertEqual(r['violations'], 1)
        self.assertEqual(r['rule'], 'not parity-determined')

    def test_unverified_rows_ignored(self):
        self.assertEqual(analysis_a1.layout_rule([game(1, 9508, 'Devil', 1.0, verified=0)])['rule'], 'no data')


class RuntimeSonarTest(unittest.TestCase):
    def test_runtime_table(self):
        rows = [game(6000 + i, 9508, 'Devil', 1.0, cpu=(100_000_000 if i < 3 else 60_000_000), faults=(5 if i < 3 else 0)) for i in range(10)]
        rows.append(game(6100, 9663, 'Trauma', 0.0, cpu=95_000_000))
        t = analysis_a1.runtime_table(rows)
        self.assertEqual(t['9508']['at_cap_games'], 3)
        self.assertEqual(t['9508']['near_cap_games'], 3)
        self.assertEqual(t['9508']['faults'], 15)
        self.assertEqual(t['9508']['max_M'], 100.0)
        self.assertEqual(t['9508']['first_stage_at_cap'], {'100': 3})
        self.assertEqual(t['9663']['near_cap_games'], 1)
        self.assertEqual(t['9663']['at_cap_games'], 0)
        self.assertEqual(t['9663']['map_max_M'], {'Trauma': 95.0})

    def test_sonar_table(self):
        rows = [game(7000 + i, 9980, 'Devil', 1.0 if i % 2 else 0.0, own=stages(10, 40, 8, sonar=(1000 * (i + 1)))) for i in range(4)]
        t = analysis_a1.sonar_table(rows)
        self.assertEqual(t['9980']['n'], 4)
        self.assertEqual(t['9980']['rays_per_turn'], 2.5)
        self.assertTrue(t['9980']['identifiable'])
        self.assertEqual(t['9980']['by_outcome']['compact_win']['rays_per_turn_r100'], 3.0)
        self.assertEqual(t['9980']['opponent_rays_per_turn'], 4.0)


class PacketTest(unittest.TestCase):
    def test_packet_lines_include_a1_sections(self):
        rows = [game(8000 + i, 9508, 'Devil' if i % 2 else 'Trauma', 1.0 if i % 3 else 0.0) for i in range(24)]
        res = dict(profiles=analysis.submission_profiles(rows), opponents=analysis.opponent_table(rows), contrasts={}, pairs={},
                   anatomy=analysis_a1.loss_anatomies(rows), layout=analysis_a1.layout_rule(rows), runtime=analysis_a1.runtime_table(rows), sonar=analysis_a1.sonar_table(rows))
        lines = analysis.packet_lines(res, 9508)
        self.assertTrue(any(l.startswith('- Loss anatomy 9508') for l in lines))
        self.assertTrue(any(l.startswith('- Layout rule: layout = f(map, game_id parity)') for l in lines))
        self.assertTrue(any(l.startswith('- Runtime') for l in lines))
        self.assertLessEqual(len(lines), 60)


if __name__ == '__main__':
    unittest.main()

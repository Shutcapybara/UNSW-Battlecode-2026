#!/usr/bin/env python3
"""No-game checks for campaign recovery and evidence validation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import campaign as c


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bot = c.QUEUE[0]
        self.key = ('autarky', 'A', 1, 'opponent')
        self.dest = self.root / 'run'
        self.dest.mkdir()
        self.patches = [patch.object(c, 'run_dir', return_value=self.dest),
                        patch.object(c, 'source_id', side_effect=lambda b: b + '-hash'),
                        patch.object(c.panel, 'expected', return_value={self.key})]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.rep = self.dest / 'replays' / (c.fixture_tag(self.bot, self.key) + '.replay')
        self.rep.parent.mkdir()
        self.rep.write_bytes(b'completed replay')
        self.row = dict(map='autarky', side='A', seed=1, opp='opponent',
            cand='bots/' + self.bot, errors=[], result='win',
            candidate_fingerprint=self.bot + '-hash', opponent_fingerprint='opponent-hash',
            replay=str(self.rep.relative_to(self.dest)), replay_sha256=c.sha(self.rep))

    def pending(self):
        p = self.dest / (c.fixture_tag(self.bot, self.key) + '.pending.json')
        p.write_text(json.dumps(self.row))
        return p

    def test_recover_before_replay_publication(self):
        self.pending()
        self.rep.rename(self.rep.with_suffix('.replay.tmp'))
        c.recover(self.bot, 'z1')
        self.assertEqual(c.read_rows(self.bot, 'z1'), {self.key: self.row})

    def test_recover_after_replay_publication(self):
        self.pending()
        c.recover(self.bot, 'z1')
        c.recover(self.bot, 'z1')
        self.assertEqual(len(c.read_rows(self.bot, 'z1')), 1)

    def test_recover_after_index_publication(self):
        self.pending()
        c.append_row(self.dest, self.row)
        c.recover(self.bot, 'z1')
        self.assertEqual(len(c.read_rows(self.bot, 'z1')), 1)

    def test_invalid_evidence_rejected(self):
        for field, value in [('result', 'oops'), ('errors', ['error']),
                             ('opponent_fingerprint', 'changed'), ('candidate_fingerprint', 'changed'),
                             ('replay', '../unrelated.replay'), ('seed', 7)]:
            with self.subTest(field=field):
                row = copy.deepcopy(self.row)
                row[field] = value
                with self.assertRaises(ValueError):
                    c.validate_row(row, self.bot, 'z1', self.dest)
        self.rep.write_bytes(b'corrupt replay')
        with self.assertRaises(ValueError):
            c.validate_row(self.row, self.bot, 'z1', self.dest)

    def test_duplicates_rejected(self):
        c.append_row(self.dest, self.row)
        c.append_row(self.dest, self.row)
        with self.assertRaises(ValueError):
            c.read_rows(self.bot, 'z1')

    def test_interrupted_index_write_not_published(self):
        c.append_row(self.dest, self.row)
        (self.dest / 'rows.jsonl.tmp').write_text('{partial')
        self.assertEqual(c.read_rows(self.bot, 'z1'), {self.key: self.row})

    def test_unjournaled_replay_refuses_new_game(self):
        self.rep.rename(self.rep.with_suffix('.replay.tmp'))
        with patch.object(c, 'freeze', return_value=self.dest), patch.object(c.arena_lune, 'run_game') as game:
            with self.assertRaises(ValueError):
                c.play(self.bot, 'z1', self.key)
            game.assert_not_called()


class FocusedScreenTests(unittest.TestCase):
    def test_production_uses_fresh_seeds_and_separate_panel(self):
        fixtures = list(c.fixture_order('food-hold-v1'))
        self.assertEqual(len(fixtures), 80)
        self.assertEqual(len(set(fixtures)), 80)
        self.assertEqual({pn for pn, _ in fixtures}, {'production-v1'})
        self.assertEqual({k[2] for _, k in fixtures}, {3, 4})
        self.assertEqual({k[0] for _, k in fixtures}, set(c.panel.runner.LIVE))
        self.assertEqual({k[3] for _, k in fixtures}, set(c.CHALLENGE_OPPONENTS))
        self.assertEqual(c.expected('production-v1', [1, 2]), set())
        self.assertEqual(c.panel_seeds('frontier-v1'), [1, 2])
        with patch.object(c, 'read_rows', return_value={}):
            jobs = list(c.jobs('expedition-11-foodhold', 'food-hold-v1'))
        self.assertEqual(len(jobs), 160)
        self.assertTrue(all(pn == 'production-v1' for _, pn, _ in jobs))

    def test_frontier_is_distinct_and_complete(self):
        fixtures = list(c.fixture_order('explore-frontier-v1'))
        self.assertEqual(len(fixtures), 80)
        self.assertEqual(len(set(fixtures)), 80)
        self.assertEqual({pn for pn, _ in fixtures}, {c.CHALLENGE_PANEL})
        self.assertEqual({k[0] for _, k in fixtures}, set(c.panel.runner.LIVE))
        self.assertEqual({k[3] for _, k in fixtures}, set(c.CHALLENGE_OPPONENTS))
        self.assertEqual(c.expected(c.CHALLENGE_PANEL, [3]), set())
        with self.assertRaises(ValueError):
            c.expected('typo', [1])
        for pn in ('z1', 'gen'):
            self.assertEqual(c.expected(pn, [1, 2, 3]), c.panel.expected(pn, [1, 2, 3]))

    def test_frontier_does_not_reuse_old_panel_rows(self):
        def rows(bot, pn):
            self.assertEqual(pn, c.CHALLENGE_PANEL)
            return {}
        with patch.object(c, 'read_rows', side_effect=rows):
            jobs = list(c.jobs('expedition-05-explore3', 'explore-frontier-v1'))
        self.assertEqual(len(jobs), 160)
        for parent, child in zip(jobs[::2], jobs[1::2]):
            self.assertEqual(parent[0], c.panel.PARENT)
            self.assertEqual(child[0], 'expedition-05-explore3')
            self.assertEqual(parent[1:], child[1:])

    def test_selected_panel_cannot_emit_original_gate(self):
        import report
        with patch.object(c, 'read_rows', return_value={}), \
                patch.object(c, 'expected', return_value=set()), \
                patch.object(c, 'run_dir', return_value=Path('/not-an-expedition-run')), \
                patch.object(c.panel.gate, 'gate') as gate:
            result = report.build_report('expedition-05-explore3', [c.CHALLENGE_PANEL])
        gate.assert_not_called()
        self.assertEqual(result['status'], 'COMPLETE SELECTED COVERAGE; NO STRENGTH VERDICT')

    def test_exact_focused_coverage(self):
        fixtures = list(c.fixture_order('mouth-contest-v1'))
        self.assertEqual(len(fixtures), 112)
        self.assertEqual(len(set(fixtures)), 112)
        self.assertEqual(fixtures[0][1][0], 'queen_of_spades')
        self.assertEqual({key[2] for _, key in fixtures[:56]}, {1})
        self.assertEqual({key[2] for _, key in fixtures[56:]}, {2})
        for pn, key in fixtures:
            self.assertIn(key, c.panel.expected(pn, [1, 2, 3]))
        self.assertEqual(len(list(c.fixture_order())), 1176)

    def test_reuses_parent_and_resumes_candidate(self):
        fixtures = list(c.fixture_order('mouth-contest-v1'))
        completed = fixtures[:3]
        def rows(bot, pn):
            return {key: {} for p, key in (fixtures if bot == c.panel.PARENT else completed) if p == pn}
        with patch.object(c, 'read_rows', side_effect=rows):
            jobs = list(c.jobs(c.FOCUSED_CANDIDATE, 'mouth-contest-v1'))
        self.assertEqual(len(jobs), 109)
        self.assertEqual([(pn, key) for _, pn, key in jobs], fixtures[3:])
        self.assertTrue(all(bot == c.FOCUSED_CANDIDATE for bot, _, _ in jobs))

    def test_frozen_screen_rejects_declaration_change(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(c, 'STORE', Path(tmp)), \
                patch.object(c, 'source_id', return_value='runtime'), \
                patch.object(c, 'sha', return_value='declaration') as digest:
            c.freeze_screen(c.FOCUSED_CANDIDATE, 'mouth-contest-v1')
            c.freeze_screen(c.FOCUSED_CANDIDATE, 'mouth-contest-v1')
            digest.return_value = 'changed'
            with self.assertRaises(ValueError):
                c.freeze_screen(c.FOCUSED_CANDIDATE, 'mouth-contest-v1')


class PhaseExposureTests(unittest.TestCase):
    def test_unequal_exposure_uses_counts(self):
        from phase_report import summarize
        def row(transits, deaths):
            return dict(won=1, totals=dict(c_transits=transits, c_transit_died3=deaths,
                c_death_h2h_ally=0, c_own_goals=0, c_dragon_turns=100,
                c_splits=0, c_deaths_newborn=0, total=20))
        result = summarize([row(10, 2), row(1, 1)])
        self.assertAlmostEqual(result['transit_died3'], 3 / 11)
        self.assertIsNone(result['newborn_death_per_split'])
        self.assertEqual(result['totals']['c_transits'], 11)

    def test_no_transits_is_unmeasured_not_safe(self):
        from phase_report import summarize
        row = dict(won=0, totals=dict(c_transits=0, c_transit_died3=0,
            c_death_h2h_ally=0, c_own_goals=0, c_dragon_turns=100,
            c_splits=0, c_deaths_newborn=0, total=0))
        self.assertIsNone(summarize([row])['transit_died3'])


class FieldPercentileTests(unittest.TestCase):
    def test_zero_inflated_ties_count_half(self):
        from report import percentile
        self.assertEqual(percentile(0, [0, 0, 0, 0, 10]), 0.4)
        self.assertEqual(percentile(5, [0, 0, 0, 0, 10]), 0.8)
        self.assertEqual(percentile(10, [0, 0, 0, 0, 10]), 0.9)

    def test_missing_reference_is_not_zero(self):
        from report import percentile
        self.assertIsNone(percentile(10, []))


class EconomyEstimandTests(unittest.TestCase):
    def test_mean_and_median_can_reverse_sign(self):
        from report import economy_estimands
        result = economy_estimands([[0] * 4, [1] * 4, [100] * 4], [[2] * 4] * 3)
        self.assertAlmostEqual(result['mean_delta'], 95 / 3)
        self.assertEqual(result['mean_checkpoint_median_delta'], -1)

    def test_difference_of_medians_is_not_median_paired_difference(self):
        from report import economy_estimands
        result = economy_estimands([[0] * 4, [100] * 4, [101] * 4],
                                   [[0] * 4, [1] * 4, [100] * 4])
        self.assertEqual(result['mean_checkpoint_median_delta'], 99)
        # Paired differences are 0, 99, 1, whose median would be 1.

    def test_checkpoint_medians_precede_checkpoint_averaging(self):
        from report import economy_estimands
        result = economy_estimands([[0, 0, 100, 100], [0, 100, 0, 100], [100, 0, 0, 100]],
                                   [[0] * 4] * 3)
        self.assertEqual(result['mean_checkpoint_median_delta'], 25)
        self.assertEqual(result['mean_delta'], 50)

    def test_incomplete_or_nonfinite_rows_rejected(self):
        from report import economy_estimands
        for child, parent in [([], []), ([[1] * 4], []), ([[1] * 3], [[1] * 4]),
                              ([[float('nan')] * 4], [[1] * 4])]:
            with self.subTest(child=child, parent=parent), self.assertRaises(ValueError):
                economy_estimands(child, parent)


class MapDiagnosticTests(unittest.TestCase):
    def test_map_cancellation_and_missing_coverage_remain_visible(self):
        from report import map_diagnostics
        wanted = {(m, seat, seed, 'opp') for m in ('gain', 'loss', 'missing')
                  for seat in ('A', 'B') for seed in (1, 2, 3)}
        keys = {k for k in wanted if k[0] != 'missing' and k[2] == 1}
        child = {k: {'result': 'win' if k[0] == 'gain' else 'loss'} for k in keys}
        parent = {k: {'result': 'loss' if k[0] == 'gain' else 'win'} for k in keys}
        features = {k: dict.fromkeys(('pearls@25', 'pearls@50', 'pearls@100',
                                     'units@100', 'total@100', 'total@250'), 0) for k in keys}
        result = map_diagnostics(wanted, child, parent, features, features)
        self.assertEqual(result['collective']['win_delta'], 0)
        self.assertEqual(result['maps']['gain']['win_delta'], 1)
        self.assertEqual(result['maps']['loss']['win_delta'], -1)
        self.assertEqual(result['leave_one_map_out']['gain']['win_delta'], -1)
        self.assertEqual(result['maps']['gain']['complete_seeds'], [1])
        self.assertFalse(result['maps']['gain']['complete'])
        self.assertEqual(result['maps']['missing']['missing_pairs'], 6)
        self.assertIsNone(result['maps']['missing']['win_delta'])
        self.assertIsNone(result['maps']['gain']['by_seed']['2']['raw_mean_deltas'])
        self.assertEqual(result['maps']['gain']['by_opponent']['opp']['paired'], 2)

    def test_draw_points_and_unpaired_games(self):
        from report import map_diagnostics
        a, b = ('map', 'A', 1, 'opp'), ('map', 'B', 1, 'opp')
        fields = ('pearls@25', 'pearls@50', 'pearls@100', 'units@100', 'total@100', 'total@250')
        features = {a: dict.fromkeys(fields, 0)}
        result = map_diagnostics({a, b}, {a: {'result': 'draw'}, b: {'result': 'win'}},
                                 {a: {'result': 'loss'}}, features, features)
        self.assertEqual(result['collective']['paired'], 1)
        self.assertEqual(result['collective']['win_delta'], .5)
        self.assertFalse(result['maps']['map']['by_seed']['1']['complete'])


class OpeningAuditTests(unittest.TestCase):
    def test_missing_event_is_not_zero_and_both_sides_share_pairs(self):
        from opening_audit import paired_measure
        result = paired_measure([0, None, 8], [4, 2, None])
        self.assertEqual(result, dict(paired=1, missing_pairs=2, parent=0, candidate=4, delta=4))
        self.assertIsNone(paired_measure([], [])['delta'])

    def test_misaligned_event_arrays_rejected(self):
        from opening_audit import paired_measure
        with self.assertRaises(ValueError):
            paired_measure([1, 2], [1])


class ParentPhaseTests(unittest.TestCase):
    def test_early_candidate_win_stays_in_parent_late_cohort(self):
        from screen_report import parent_phase_cohort
        row = dict(parent=dict(rounds=500, result='loss'), child=dict(rounds=100, result='win'),
                   parent_features={'total_share@250': .4, 'longest_margin_end': -2},
                   candidate_features={'total_share@250': 1., 'longest_margin_end': 5})
        excluded = dict(row, parent=dict(rounds=200, result='loss'), child=dict(rounds=500, result='loss'))
        result = parent_phase_cohort([row, excluded], 400)
        self.assertEqual(result['pairs'], 1)
        self.assertEqual(result['expected_score_delta'], 1)
        self.assertEqual(result['longest_margin_end_delta'], 7)
        self.assertIsNone(parent_phase_cohort([excluded], 400)['expected_score_delta'])


class MapClusterUncertaintyTests(unittest.TestCase):
    def fixture(self, map_name, seed, parent, child, tempo=0):
        return dict(panel='frontier-v1', key=(map_name, 'A', seed, 'opp'),
                    parent=dict(result=parent), child=dict(result=child), tempo=tempo)

    def test_repeating_seeds_does_not_invent_independent_maps(self):
        from screen_report import map_cluster_uncertainty as audit
        rows = [self.fixture('gain', 1, 'loss', 'win', -4),
                self.fixture('loss', 1, 'win', 'loss', 4)]
        repeated = [dict(x, key=(x['key'][0], 'A', seed, 'opp'))
                    for x in rows for seed in range(1, 11)]
        base = audit(rows, repeats=1000)
        replicated = audit(repeated, repeats=1000)
        self.assertEqual(base['metrics'], replicated['metrics'])
        self.assertEqual(replicated['clusters'], 2)
        self.assertEqual(base['metrics']['expected_score']['interval95'], [-1, 1])
        self.assertEqual(base, audit(list(reversed(rows)), repeats=1000))

    def test_draws_and_unequal_map_sizes(self):
        from screen_report import map_cluster_uncertainty as audit
        rows = [self.fixture('a', s, 'loss', 'draw') for s in (1, 2, 3)]
        rows.append(self.fixture('b', 1, 'win', 'loss'))
        self.assertEqual(audit(rows, repeats=100)['metrics']['expected_score']['mean_delta'], .125)
        single = audit(rows[:3], repeats=100)
        self.assertEqual(single['metrics']['expected_score']['mean_delta'], .5)
        self.assertIsNone(single['metrics']['expected_score']['interval95'])

    def test_missing_duplicate_and_nonfinite_pairs_rejected(self):
        from screen_report import map_cluster_uncertainty as audit
        row = self.fixture('a', 1, 'loss', 'win')
        for rows in ([], [row, row], [dict(row, tempo=float('nan'))]):
            with self.assertRaises(ValueError):
                audit(rows, repeats=100)
        with self.assertRaises(KeyError):
            audit([dict(panel='frontier-v1', key=('a', 'A', 1, 'opp'),
                        parent=dict(result='win'), tempo=0)], repeats=100)


if __name__ == '__main__':
    unittest.main()

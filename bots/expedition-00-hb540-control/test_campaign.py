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


if __name__ == '__main__':
    unittest.main()

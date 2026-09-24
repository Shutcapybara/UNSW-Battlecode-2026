import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('summary', Path(__file__).resolve().parents[1] / 'bots/summarize_hunter.py')
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class SummaryTests(unittest.TestCase):
    def test_cpu_failure_is_not_counted_as_tactical_win(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'manifest.json').write_text(json.dumps(dict(focus_bot='new', bots=['new', 'old'], maps=['small'])))
            (root / 'match.log').write_text('round 0: bot 0 exceeded CPU limit\nteam B wins after 1 rounds')
            (root / 'results.json').write_text(json.dumps([dict(map='small', team_a='old', team_b='new', outcome='B', winner='new', log='match.log')]))
            result, _, _ = summary.summarize(root)
            self.assertEqual(result['raw']['wins'], 1)
            self.assertEqual(result['clean']['wins'], 0)
            self.assertFalse(result['complete'])
            self.assertEqual(len(result['excluded']), 1)

    def test_error_is_not_a_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'manifest.json').write_text(json.dumps(dict(focus_bot='new', bots=['new', 'old'], maps=['small'])))
            (root / 'match.log').write_text('timed out')
            (root / 'results.json').write_text(json.dumps([dict(map='small', team_a='old', team_b='new', outcome='error', winner=None, log='match.log')]))
            result, _, _ = summary.summarize(root)
            self.assertEqual(result['raw']['errors'], 1)
            self.assertEqual(result['raw']['losses'], 0)

    def make_run(self, root, focus):
        root.mkdir()
        (root / 'manifest.json').write_text(json.dumps(dict(focus_bot=focus,
            bots=['new', 'old', 'third'], maps=['arena'], input_hash='same', script_hash='same', executable='unswbc', replays=False)))
        results = []
        for a in ('new', 'old', 'third'):
            for b in ('new', 'old', 'third'):
                if a == b or focus not in (a, b):
                    continue
                winner = 'new' if 'new' in (a, b) else 'third'
                results.append(dict(map='arena', team_a=a, team_b=b,
                    outcome='A' if winner == a else 'B', winner=winner, log='match.log'))
        (root / 'match.log').write_text('team A wins after 100 rounds')
        (root / 'results.json').write_text(json.dumps(results))

    def test_equal_coverage_is_required_for_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            new, old = Path(tmp) / 'new', Path(tmp) / 'old'
            self.make_run(new, 'new')
            self.make_run(old, 'old')
            result = summary.compare(new, old)
            self.assertTrue(result['valid'])
            self.assertEqual(result['pool_standings'][0]['bot'], 'new')
            self.assertEqual({row['played'] for row in result['pool_standings']}, {4})
            self.assertEqual(result['decision'], 'improved on this small sample')
            rows = json.loads((old / 'results.json').read_text())
            (old / 'results.json').write_text(json.dumps(rows[:-1]))
            self.assertFalse(summary.compare(new, old)['valid'])

    def test_disagreement_and_changed_sources_block_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            new, old = Path(tmp) / 'new', Path(tmp) / 'old'
            self.make_run(new, 'new')
            self.make_run(old, 'old')
            rows = json.loads((old / 'results.json').read_text())
            rows[0]['outcome'] = 'B'
            rows[0]['winner'] = 'old'
            (old / 'results.json').write_text(json.dumps(rows))
            result = summary.compare(new, old)
            self.assertFalse(result['valid'])
            self.assertEqual(len(result['duplicate_disagreements']), 1)
            manifest = json.loads((old / 'manifest.json').read_text())
            manifest['input_hash'] = 'changed'
            (old / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                summary.compare(new, old)


if __name__ == '__main__':
    unittest.main()

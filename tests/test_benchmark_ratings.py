"""The live estimate consumes shared stats and never replaces good data on failure."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import benchmark_ratings as ratings


class RatingTests(unittest.TestCase):
    def test_refresh_rebuilds_shared_union_before_fitting(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);events=[]
            def rebuild(rows):
                self.assertEqual(rows,[]);events.append('rebuild')
            def build(path):
                events.append('fit');self.assertTrue(path.is_dir())
                return {'fixtures':123}
            with patch.object(ratings,'publish_games',side_effect=rebuild), \
                 patch.object(ratings,'build_snapshot',side_effect=build), \
                 patch.object(ratings,'summary',return_value='ranking'):
                ratings.refresh(out)
            self.assertEqual(events,['rebuild','fit'])
            self.assertEqual(json.loads((out/'latest.json').read_text()),{'fixtures':123})
            self.assertEqual((out/'latest.md').read_text(),'ranking')

    def test_failed_fit_preserves_last_success_and_removes_working_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            (out/'latest.json').write_text('{"old":true}')
            (out/'latest.md').write_text('old ranking')
            with patch.object(ratings,'publish_games'), \
                 patch.object(ratings,'build_snapshot',side_effect=RuntimeError('no convergence')):
                with self.assertRaises(RuntimeError):ratings.refresh(out)
            self.assertEqual((out/'latest.json').read_text(),'{"old":true}')
            self.assertEqual((out/'latest.md').read_text(),'old ranking')
            self.assertEqual(sorted(p.name for p in out.iterdir()),['latest.json','latest.md'])

    def test_new_contribution_or_identity_metadata_triggers_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);campaign=root/'campaign';campaign.mkdir()
            (root/'experiment_data').mkdir()
            (root/'experiment_data/benchmark-current.json').write_text(json.dumps({'directory':str(campaign)}))
            for name in ('manifest.json','aliases.json'):(campaign/name).write_text('{}')
            for name in ('runs','sources'):(root/'game_stats'/name).mkdir(parents=True)
            before=ratings.inputs(root)
            (root/'game_stats/runs/new.parquet').write_bytes(b'new contribution')
            after=ratings.inputs(root)
            self.assertNotEqual(before,after)
            self.assertEqual(after,ratings.inputs(root))
            (root/'game_stats/sources/new.json').write_text('{}')
            self.assertNotEqual(after,ratings.inputs(root))


if __name__=='__main__':unittest.main()

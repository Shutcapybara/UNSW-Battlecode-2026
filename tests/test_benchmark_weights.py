"""Map distribution affects sampling/aggregation, never fixture identity."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benchmark_weights import configured_distribution, normalized_weights
from benchmark_data import sha, with_rating_context
from benchmark_priority import adaptive_batch


class WeightTests(unittest.TestCase):
    def test_suite_mass_is_independent_of_map_count_and_checks_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            maps = {name: root/(name+'.map') for name in ('old', 'sibling', 'single')}
            for name, path in maps.items(): path.write_text(name)
            suite = root/'suite.json'
            suite.write_text(json.dumps(dict(maps=[dict(name=n, sha256=sha(maps[n]),
                default_training_map_weight=w) for n, w in [('sibling', 1), ('single', 2)]])))
            config = dict(map_distribution=dict(manifest='suite.json', mass=.6))
            weights, policy = configured_distribution(config, maps, root/'benchmark.toml')
            self.assertAlmostEqual(weights['old'], .4)
            self.assertAlmostEqual(weights['sibling'], .2)
            self.assertAlmostEqual(weights['single'], .4)
            self.assertEqual(policy['suite_mass'], .6)
            maps['single'].write_text('changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                configured_distribution(config, maps, root/'benchmark.toml')

    def test_invalid_distributions_fail_instead_of_silently_ignoring_maps(self):
        for weights in ({'a': 1}, {'a': 0, 'b': 1}, {'a': -1, 'b': 2},
                        {'a': float('nan'), 'b': 1}, {'a': float('inf'), 'b': 1}):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                normalized_weights(dict(maps=['a', 'b'], map_weights=weights))

    def test_weighted_sampling_prioritizes_high_mass_but_eventually_covers_both(self):
        manifest = dict(bots=['a', 'b', 'c'], maps=['low', 'high'],
                        map_weights=dict(low=.1, high=.9))
        queue, trace = adaptive_batch(manifest, {}, size=2)
        self.assertEqual(queue, [('a', queue[0][1], 'high'), (queue[0][1], 'a', 'high')])
        self.assertAlmostEqual(trace['selections'][0]['map_weight'], .9)
        queue, _ = adaptive_batch(manifest, {}, size=100)
        self.assertEqual(len(queue), 12)
        self.assertEqual({x[2] for x in queue}, {'low', 'high'})

    def test_legacy_campaigns_keep_uniform_sampling(self):
        manifest = dict(bots=['a', 'b', 'c'], maps=['x', 'y'])
        old, _ = adaptive_batch(manifest, {}, size=8)
        explicit, _ = adaptive_batch(manifest | dict(map_weights=dict(x=.5, y=.5)), {}, size=8)
        self.assertEqual(old, explicit)

    def test_retired_opponents_inform_fit_but_are_never_scheduled(self):
        manifest = dict(bots=['a', 'b'], maps=['x', 'y'], effective_hashes=dict(a='new-a', b='b'),
                        rating_context=dict(effective_hashes=dict(a='old-a', retired='r')))
        expanded = with_rating_context(manifest)
        self.assertEqual(expanded['effective_hashes']['a'], 'new-a')
        self.assertIn('retired', expanded['bots'])
        self.assertEqual(manifest['bots'], ['a', 'b'])
        games = {('a', 'retired', 'x'): [dict(outcome='A')],
                 ('retired', 'b', 'y'): [dict(outcome='B')]}
        queue, trace = adaptive_batch(manifest, games, size=100)
        self.assertEqual(trace['observed_fixtures'], 2)
        self.assertEqual(trace['rating_context_bots'], 1)
        self.assertEqual(len(queue), 4)
        self.assertTrue(all(set(f[:2]) == {'a', 'b'} for f in queue))


if __name__ == '__main__': unittest.main()

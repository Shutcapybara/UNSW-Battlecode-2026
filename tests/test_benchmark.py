"""Coverage must mean identical inputs; scheduling must improve weak coverage first."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benchmark import observed, ordered_gaps, targets, record
from benchmark_data import effective_hash, register_source, aliases, preserve_published_fault_counts
from game_stats import digest
import benchmark


def manifest():
    names=['anchor','experienced','new-a','new-b']
    files={n:{'main.py':digest(n)} for n in names}
    return dict(bots=names,maps=['small','large'],references=['anchor'],pairing='panel',
        mode='native',runner_version='test',map_hashes={m:digest(m) for m in ['small','large']},
        effective_hashes={n:digest(f) for n,f in files.items()},
        hashes={'bots/'+n:f for n,f in files.items()},run_id='0'*32,created='2026-09-25T00:00:00+00:00')


def game(m,a='new-a',b='anchor',board='small'):
    return record(m,dict(team_a=a,team_b=b,map=board,outcome='A',rounds=100))


class BenchmarkTests(unittest.TestCase):
    def test_reimport_preserves_fault_evidence_but_other_conflicts_still_fail(self):
        from game_stats import union
        old=game(manifest()) | dict(runtime_faults=40)
        rows,audit=preserve_published_fault_counts([old | dict(runtime_faults=0)], [old])
        self.assertEqual(union([old]+rows),[old])
        self.assertEqual(audit[0]['published_runtime_faults'],40)
        changed=old | dict(rounds=101,runtime_faults=0)
        rows,audit=preserve_published_fault_counts([changed],[old])
        self.assertEqual(audit,[])
        with self.assertRaisesRegex(ValueError,'Conflicting copies'):
            union([old]+rows)

    def test_skip_seen_and_fill_low_coverage_with_both_sides(self):
        m=manifest()
        seen={f for f in targets(m) if 'experienced' in f}
        queue=ordered_gaps(m,seen)
        self.assertEqual(set(queue),targets(m)-seen)
        self.assertEqual(len(queue),len(set(queue)))
        self.assertEqual(queue[1],(queue[0][1],queue[0][0],queue[0][2]))
        owners=[next(n for n in f[:2] if n!='anchor') for f in queue[:4]]
        self.assertEqual(set(owners),{'new-a','new-b'})

    def test_partial_pair_gets_missing_side_only(self):
        m=manifest(); seen=targets(m)-{('anchor','new-a','small')}
        self.assertEqual(ordered_gaps(m,seen),[('anchor','new-a','small')])

    def test_versions_maps_runtime_and_seeds_do_not_cross(self):
        m=manifest(); good=game(m)
        self.assertEqual(len(observed(m,[good,good],{})),1)
        for changes in [dict(bot_a_sha256='f'*64),dict(map_sha256='f'*64),dict(mode='sandbox'),
                        dict(runner_version='another'),dict(seed='1')]:
            with self.subTest(changes=changes):
                self.assertFalse(observed(m,[good|changes],{}))
        self.assertTrue(observed(m,[good|dict(bot_a_sha256='f'*64)],{'f'*64:good['bot_a_sha256']}))

    def test_markdown_ignored_only_if_packaging_explicitly_excludes_it(self):
        files={'bot.toml':digest('config'),'main.py':digest('code'),'README.md':digest('a')}
        changed=files|{'README.md':digest('b')}
        config='[project]\ninclude=["*.py"]\n'
        self.assertEqual(effective_hash(files,config),effective_hash(changed,config))
        for includes in ['["*"]','[]']:
            self.assertNotEqual(effective_hash(files,'[project]\ninclude='+includes),
                                effective_hash(changed,'[project]\ninclude='+includes))
        self.assertNotEqual(effective_hash(files,config),effective_hash(files|{'main.py':digest('new')},config))

    def test_portable_alias_metadata_validates_configuration(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); bot=root/'bot'; bot.mkdir()
            content='[project]\ninclude=["*.py"]\n'; (bot/'bot.toml').write_text(content)
            files={'bot.toml':hashlib.sha256(content.encode()).hexdigest(),'README.md':digest('doc')}
            effective=register_source(files,bot,root)
            self.assertEqual(aliases(root),{digest(files):effective})
            path=next((root/'game_stats/sources').glob('*.json'))
            data=json.loads(path.read_text()); data['bot_toml']+='broken'
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): aliases(root)

    def test_round_robin_and_empty_gap(self):
        m=manifest()|dict(pairing='round_robin')
        self.assertEqual(len(targets(m)),24)
        self.assertEqual(ordered_gaps(m,targets(m)),[])
        self.assertEqual(set(ordered_gaps(m,set())),targets(m))

    def test_run_resume_publishes_once_and_errors_never_become_draws(self):
        from game_stats import read_parquet
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); out=root/'experiment'; out.mkdir()
            m=manifest() | dict(benchmark_version=1,runner='fake',
                settings=dict(jobs=1,timeout_seconds=10,sandbox=False))
            for name in m['bots']:
                folder=out/'sources/bots'/name; folder.mkdir(parents=True)
                (folder/'bot.toml').write_text('[project]\ninclude=["*.py"]\n')
                (folder/'main.py').write_text(name)
                files=benchmark.hashes(folder)
                m['hashes']['bots/'+name]=files; m['effective_hashes'][name]=digest(files)
            (out/'sources/maps').mkdir()
            for board in m['maps']:
                p=out/'sources/maps'/(board+'.map'); p.write_text(board)
                m['map_hashes'][board]=benchmark.sha(p)
            fixtures=[('new-a','anchor','small'),('anchor','new-a','small')]
            for file,value in [('manifest.json',m),('plan.json',fixtures),('aliases.json',{})]:
                (out/file).write_text(json.dumps(value))
            fail=[True]
            def fake_play(executable,board,a,b,directory,label,*args):
                (directory/(label+'.log')).write_text('')
                return dict(team_a=a.name,team_b=b.name,map=board.stem,
                    outcome='error' if fail[0] else 'A',rounds=100,log=label+'.log',error=None)
            with patch.object(benchmark,'ROOT',root), patch.object(benchmark,'aliases',return_value={}), \
                 patch.object(benchmark.subprocess,'check_output',return_value='test'), \
                 patch.object(benchmark,'play',side_effect=fake_play):
                benchmark.run(out,limit=1,replays=False)
                self.assertEqual(read_parquet(root/'game_stats.parquet'),[])
                self.assertEqual(set(json.loads((out/'blocked-bots.json').read_text())),{'new-a','anchor'})
                benchmark.run(out,replays=False)
                self.assertEqual(read_parquet(root/'game_stats.parquet'),[])
                fail[0]=False
                benchmark.run(out,limit=1,replays=False,retry_errors=True)
                self.assertEqual(len(read_parquet(root/'game_stats.parquet')),1)
                benchmark.run(out,replays=False)
                self.assertEqual(len(read_parquet(root/'game_stats.parquet')),2)
                # Adaptive mode must refill its queue from newly published evidence,
                # even though the original static plan is now exhausted.
                m['pairing']='adaptive'
                (out/'manifest.json').write_text(json.dumps(m))
                wanted=[('new-b','anchor','large'),('anchor','new-b','large')]
                def batch(manifest,games,**kwargs):
                    remaining=[f for f in wanted if f not in games]
                    return remaining[:1],dict(reason_counts={'coverage':1})
                with patch('benchmark_priority.adaptive_batch',side_effect=batch) as planner:
                    benchmark.run(out,limit=2,replays=False)
                    self.assertEqual(planner.call_count,2)
                    benchmark.run(out,replays=False)
                self.assertEqual(len(read_parquet(root/'game_stats.parquet')),4)

    def test_lab_import_verifies_overridden_sources_and_is_repeatable(self):
        from benchmark_data import lab_records,sha
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); folder=root/'build/old-run'; folder.mkdir(parents=True)
            fingerprints={}
            for name in ['a','b']:
                bot=folder/'sources'/name; bot.mkdir(parents=True)
                (bot/'main.py').write_text(name+' # parameter override already applied')
                fingerprints[name]={'main.py':sha(bot/'main.py')}
            board=folder/'sources/x.map'; board.write_text('MAP 10 10')
            fingerprints['x.map']=sha(board)
            m=dict(focus='a',opponents=['b'],maps=['x'],hashes=fingerprints,sandbox=False,
                runner_version='test',overrides={'speed':2})
            path=folder/'manifest.json'; path.write_text(json.dumps(m))
            games=[dict(team_a='a',team_b='b',map='x',outcome='A',winner='a',rounds=100)]
            first=lab_records(path,m,games,root)
            self.assertEqual(first,lab_records(path,m,games,root))
            (folder/'sources/a/main.py').write_text('changed')
            with self.assertRaisesRegex(ValueError,'Frozen source changed'):
                lab_records(path,m,games,root)


if __name__=='__main__':
    unittest.main()

"""Check mathematical identities and safe ingestion used by similarity analysis."""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import hashlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import numpy as np
from scipy.optimize import check_grad
from performance_model import objective,unpack,logits
from similarity_report import components
from import_field_stats import field_records
from bot_similarity import dataset
from game_stats import make_record


class SimilarityTests(unittest.TestCase):
    def test_gradient_and_strength_cycle_separation(self):
        n,m,q=5,3,2
        x=np.random.default_rng(2).normal(0,.2,n+n*m+m+2*n*q)
        data=(np.array([0,1,2,3,4,0]),np.array([1,2,3,4,0,2]),np.array([0,1,2,0,1,2]),np.array([1.,.5,0,1,0,1]))
        error=check_grad(lambda p:objective(p,data,n,m,q)[0],lambda p:objective(p,data,n,m,q)[1],x)
        self.assertLess(error,1e-6)
        model=dict(x=x,q=q,maps=True)
        s,t,b,c,_=components(model,n,m,np.arange(n))
        a,d,board,_=data
        z=s[a]-s[d]+t[a,board]-t[d,board]+b[board]+c[a,d]
        np.testing.assert_allclose(z,logits(x,data,n,m,q))
        np.testing.assert_allclose(c,-c.T)
        np.testing.assert_allclose(c.sum(axis=1),0,atol=1e-12)
        singular=np.linalg.svd(c,compute_uv=False)
        np.testing.assert_allclose(singular[:2*q:2],singular[1:2*q:2],atol=1e-12)

    def test_repeats_and_documentation_aliases_do_not_add_weight(self):
        values=dict(run_id='0'*32,game_key='one',source='bot_field_tournament',run_started_at='2026-09-25T00:00:00+00:00',
                    bot_a='alpha',bot_b='beta',bot_a_sha256='a'*64,bot_b_sha256='b'*64,map_name='arena',
                    map_sha256='c'*64,mode='native',runner_version='unswbc 1.0.0',outcome='draw')
        one=make_record(**values)
        two=make_record(**(values|dict(run_id='1'*32,bot_a_sha256='d'*64)))
        data,meta=dataset([one,two],{('alpha','a'*64):'e'*64,('alpha','d'*64):'e'*64,('beta','b'*64):'b'*64})
        self.assertEqual(len(data[3]),1)
        self.assertEqual(data[3][0],.5)
        self.assertEqual(meta['repeated_fixtures_removed'],1)
        self.assertEqual(meta['conflicting_fixture_count'],0)

    def test_field_import_is_repeatable_and_does_not_change_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'sources/maps').mkdir(parents=True)
            (root/'sources/maps/arena.map').write_text('MAP 4 4\n')
            sha=hashlib.sha256((root/'sources/maps/arena.map').read_bytes()).hexdigest()
            manifest=dict(prepared=True,mode='native',created='2026-09-25T00:00:00+00:00',bots=['a','b'],maps=['arena'],
                          hashes={'a':{'main.py':'a'*64},'b':{'main.py':'b'*64},'arena.map':sha},
                          runner_version='unswbc 1.0.0',games=2,seed=123)
            (root/'manifest.json').write_text(json.dumps(manifest))
            game=dict(map='arena',team_a='a',team_b='b',outcome='A',winner='a',rounds=10,runtime_faults=[])
            with sqlite3.connect(root/'games.sqlite3') as db:
                db.execute('CREATE TABLE games(map TEXT,a TEXT,b TEXT,outcome TEXT,data TEXT)')
                db.execute('INSERT INTO games VALUES(?,?,?,?,?)',('arena','a','b','A',json.dumps(game)))
            before={p.name:p.read_bytes() for p in (root/'manifest.json',root/'games.sqlite3')}
            first,info=field_records(root);second,_=field_records(root)
            self.assertEqual(first,second)
            self.assertIsNone(first[0]['seed'])  # Scheduling RNG is not the game seed.
            self.assertEqual(info['completed'],1)
            self.assertEqual(before,{p.name:p.read_bytes() for p in (root/'manifest.json',root/'games.sqlite3')})


if __name__=='__main__':
    unittest.main()

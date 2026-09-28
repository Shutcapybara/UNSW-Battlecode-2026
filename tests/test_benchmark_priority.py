"""Adaptive selection contracts: exploration, opponent information, and no repeats."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import numpy as np
from benchmark_priority import adaptive_batch


class PriorityTests(unittest.TestCase):
    def test_cold_bot_faces_informative_known_opponent_not_obvious_mismatch(self):
        names=['new','good','weak','other'];maps=['one','two','three']
        m=dict(bots=names,maps=maps)
        games={(a,b,board):[dict(outcome='A')] for a,b in
               [('good','weak'),('weak','good'),('good','other'),('other','good'),('weak','other'),('other','weak')]
               for board in maps}
        x=np.r_[np.array([2.,2.,-8.,-8.]),np.zeros(4*3+3)]
        with patch('benchmark_priority.fit',return_value=dict(x=x,success=True)):
            queue,info=adaptive_batch(m,games,size=2)
        self.assertEqual(set(queue[0][:2]),{'new','good'})
        self.assertEqual(queue[1],(queue[0][1],queue[0][0],queue[0][2]))
        self.assertEqual(info['selections'][0]['reason'],'coverage')

    def test_completed_excluded_and_blocked_fixtures_never_scheduled(self):
        m=dict(bots=['a','b','c','blocked'],maps=['x','y'])
        games={('a','b','x'):[dict(outcome='A')]}
        excluded={('b','a','y')}
        queue,detail=adaptive_batch(m,games,excluded=excluded,blocked={'blocked'},size=100)
        self.assertEqual(len(queue),len(set(queue)))
        self.assertTrue(set(queue).isdisjoint(set(games)|excluded))
        self.assertTrue(all('blocked' not in f[:2] for f in queue))
        expected={(a,b,board) for a in ['a','b','c'] for b in ['a','b','c'] if a!=b for board in ['x','y']}
        self.assertEqual(set(queue),expected-set(games)-excluded)
        self.assertIn(('b','a','x'),queue)

    def test_new_evidence_changes_next_batch_and_cold_start_is_finite(self):
        m=dict(bots=['a','b','c'],maps=['x','y'])
        first,_=adaptive_batch(m,{},size=4)
        games={f:[dict(outcome='A')] for f in first}
        second,info=adaptive_batch(m,games,size=4)
        self.assertTrue(set(first).isdisjoint(second))
        self.assertTrue(all(np.isfinite(r['priority']) for r in info['selections']))
        all_games={(a,b,board):[dict(outcome='draw')] for a in m['bots'] for b in m['bots'] if a!=b for board in m['maps']}
        self.assertEqual(adaptive_batch(m,all_games)[0],[])


if __name__=='__main__':unittest.main()

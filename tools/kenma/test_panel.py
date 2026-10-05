"""Regression check: resource-aborted fixtures must be recoverable without hiding old errors."""
import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import panel

class RecoveryTest(unittest.TestCase):
    def test_external_maps_and_path_escape(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(panel.map_path('live_var/hidden',t),Path(t).resolve()/'live_var/hidden.map')
            self.assertEqual(panel.map_path('live/default'),(panel.ROOT/'maps/live/default.map').resolve())
            with self.assertRaises(ValueError):panel.map_path('../escape',t)

    def test_external_opponent_never_relocates_candidate(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            paths=panel.source_paths('kenma-test',['bokuto-test'],root)
            self.assertEqual(paths['kenma-test'],panel.ROOT/'bots/kenma-test')
            self.assertEqual(paths['bokuto-test'],root.resolve()/'bokuto-test')
            self.assertEqual(panel.source_paths('kenma-test',['control'])['control'],panel.ROOT/'bots/control')
            with self.assertRaises(ValueError):
                panel.source_paths('same',['same'],root)

    def test_failed_attempt_preserved_then_replaced(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)
            fx=dict(map='live/default',seed=1,opp='opponent',seat='A')
            key='live+default__s1__A__opponent'
            prior=dict(fx,bot='kenma-test',rc=-15,winner=None,faults=['resource interruption'])
            (out/f'{key}.json').write_text(json.dumps(prior))
            (out/f'{key}.log').write_text('old interrupted log')
            args=argparse.Namespace(bot='kenma-test',retry_errors=False,keep_replays=False)
            with patch.object(panel,'check_space'):
                self.assertEqual(panel.run(fx,args,{},out),prior)
            class CompletedGame:
                pid=99999999
                returncode=0
                def __init__(self,cmd,stdout,**kwargs):
                    stdout.write('team A wins after 500 rounds (longer queen, 3 to 0)\n')
                def wait(self,**kwargs): return 0
            args.retry_errors=True
            with patch.object(panel,'check_space'), patch.object(panel.subprocess,'Popen',CompletedGame):
                row=panel.run(fx,args,{'kenma-test':'candidate','opponent':'control'},out)
            self.assertEqual(row['winner'],'A')
            self.assertEqual(row['rc'],0)
            self.assertEqual(row['faults'],[])
            self.assertEqual(len(list(out.glob('*.json'))),1)
            archived=list((out/'attempts').glob('*.json'))
            self.assertEqual(len(archived),1)
            self.assertEqual(json.loads(archived[0].read_text()),prior)
            self.assertEqual(next((out/'attempts').glob('*.log')).read_text(),'old interrupted log')
            self.assertFalse(panel.ACTIVE)

if __name__=='__main__':unittest.main()

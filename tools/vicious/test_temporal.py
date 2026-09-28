import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
bot='vicious-x01-surface'
if '--bot' in sys.argv:
    idx=sys.argv.index('--bot');bot=sys.argv[idx+1];del sys.argv[idx:idx+2]
sys.path.insert(0,str(ROOT/'bots'/bot))
import protocol as io
import world as w
import temporal as t
import roles
import tactics as tx
from params import P

class Checks(unittest.TestCase):
    def setUp(self):
        self.saved=P.copy()
        io.game.update(id=40,team='A',size=(12,12),unit_limit=64)
        w.init();w.ek[:]=bytes([2])*len(w.ek)
        w.RND=w.BORN=360;w.HEAD=40;w.LEN=4;w.UNITS=12
        w.body=[37,38,39,40];w.occ={};w.ally_heads=[];w.enemy_heads=[];w.crown=None;w.cut=set();w.alen={}
        w.pearls={};w.spawn={};io.observation['tiles']=[]
        t.STATE.update(intent=None,open=0,late=0,changed=0)
    def tearDown(self):P.clear();P.update(self.saved)
    def edge(self,c,d):
        k=w.ekey(c,d);w.ek[k]=1;w._touch(k)
    def test_boundaries_and_age(self):
        for r,phase in [(59,'opening'),(60,'middle'),(61,'middle'),(359,'middle'),(360,'endgame'),(361,'endgame')]:
            self.assertEqual(t.schedule(r)[0],phase)
        P['temporal_egress']=1;t.observe()
        self.assertEqual(t.STATE['phase'],'endgame');self.assertEqual(t.STATE['age'],0)
    def test_soft_bounds(self):
        for r in range(500):
            _,op,late=t.schedule(r,mode='soft')
            self.assertTrue(0<=op<=1 and 0<=late<=1)
        self.assertEqual(t.schedule(390,mode='soft')[2],.5)
    def test_addressed_birth_message(self):
        w.HEAD=37;w.LEN=2
        p=37|(35<<12)|(360<<24)|(2<<33)
        t.hear(p);self.assertEqual(t.STATE['intent'][0],35)
        for bad in [38|(35<<12)|(360<<24)|(2<<33),37|(35<<12)|(359<<24)|(2<<33),37|(35<<12)|(360<<24)|(3<<33)]:
            t.STATE['intent']=None;t.hear(bad);self.assertIsNone(t.STATE['intent'])
        w.BORN=359;t.hear(p);self.assertIsNone(t.STATE['intent'])
    def test_corridor_exit_and_dead_end(self):
        self.edge(37,3);self.assertIsNone(t.corridor_goal(37,set(w.body)))
        self.edge(36,3);self.edge(47,0);self.edge(47,2)
        self.assertEqual(t.corridor_goal(37,set(w.body)),47)
    def test_other_half_blocks_newborn(self):
        P['temporal_split_guard']=1
        # A one-tile side pocket is an exit but cannot sustain the newborn.
        self.edge(37,0)
        ranked=[(8,('split',2)),(1,('move',[1]))]
        result=t.adjust(ranked,{})
        self.assertEqual(max(result)[1],('move',[1]))
        self.edge(25,0)
        self.assertEqual(max(t.adjust(ranked,{}))[1],('split',2))
    def test_off_switch(self):
        for key in ('temporal_egress','temporal_split_guard','temporal_open_bonus',
                    'temporal_conversion','temporal_crown_state','temporal_body_guard','temporal_body_state'):
            P[key]=0
        ranked=[(8,('split',2)),(1,('move',[1]))]
        self.assertIs(t.adjust(ranked,{}),ranked)
        self.assertEqual(t.resource_value(40,10),10)
        self.assertTrue(t.donation_allowed(39))
    def test_donation_requires_reachable_receiver(self):
        P['temporal_conversion']=1;w.RND=410;w.LEN=4;w.crown=[20,41,12,410]
        self.assertFalse(t.donation_allowed(41))
        self.edge(40,1)
        self.assertTrue(t.donation_allowed(41))
        w.enemy_heads=[(28,21)];self.assertFalse(t.donation_allowed(41))
    def test_crown_loss_restores_production(self):
        P['temporal_conversion']=1;P['temporal_convert_from']=340
        w.ME=48;w.crown=[20,41,12,360];t.observe()
        self.assertEqual(P['split_stop'],360)
        w.crown=None;w.RND=361;t.observe()
        self.assertEqual(P['split_stop'],t.BASE['split_stop'])
    def test_direct_crown_length(self):
        if not hasattr(t,'before_roles'):self.skipTest('cycle 2 feature')
        P['temporal_crown_state']=1;P['temporal_refresh_crown']=1;w.crown=[20,41,30,359]
        w.ally_heads=[(41,20)];w.alen={20:3}
        t.before_roles();self.assertEqual(w.crown[2],3)
        w.cut={20};w.crown[2]=30
        t.before_roles();self.assertEqual(w.crown[2],30)
    def test_carrier_admission_and_endgame(self):
        if not hasattr(t,'before_roles'):self.skipTest('cycle 2 feature')
        P['temporal_crown_state']=1;P['temporal_carrier_min']=8
        roles.ROLE[0]='crown';w.LEN=4;w.RND=379;t.observe()
        self.assertEqual(roles.ROLE[0],'forager')
        roles.ROLE[0]='crown';w.RND=380;t.observe()
        self.assertEqual(roles.ROLE[0],'crown')
    def test_visible_crown_across_portal_is_lower_bound(self):
        if not hasattr(t,'before_roles'):self.skipTest('cycle 2 feature')
        P['temporal_crown_state']=1;P['temporal_refresh_crown']=1
        w.crown=[20,41,30,359];w.ally_heads=[(41,20)];w.alen={20:3}
        w.occ={41:(20,True,True)};w.ek[w.ekey(41,0)]=3
        t.before_roles();self.assertEqual(w.crown[2],30)
    def test_partial_body_matches_full_body_oracle(self):
        import inspect,itertools
        if 'actual_length' not in inspect.signature(tx.flood).parameters:self.skipTest('cycle 3 feature')
        w.ek[:]=bytes([1])*len(w.ek);w.DC=[None]*w.NC;w.OPT=[None]*w.NC
        w.LEN=8;w.HEAD=40;w.body=[4,16,28,40]
        full=[100,112,124,136,4,16,28,40]
        P['temporal_body_state']=0
        self.assertEqual(tx.sim([1,0,3],w.body)[0],'ok')  # inherited false survival
        P['temporal_body_state']=1
        self.assertEqual(tx.sim([1,0,3],w.body)[0],'dead')
        for food in ({},{41:w.RND,29:w.RND}):
            w.pearls=food
            for length in (1,2,3):
                for path in itertools.product(range(4),repeat=length):
                    partial=tx.sim(path,w.body);complete=tx.sim(path,full)
                    self.assertEqual(partial[0],complete[0],path)
                    self.assertEqual(partial[2],complete[2],path)
                    if partial[0]=='ok':
                        self.assertEqual(partial[1],complete[1][-len(partial[1]):])

if __name__=='__main__':unittest.main()

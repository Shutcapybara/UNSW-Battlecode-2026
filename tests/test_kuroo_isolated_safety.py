"""Isolated local donor election and length-preserving queen escape rules."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
FEED = r'''
#include "policy.hpp"
#include <cassert>
int main() {
 ares::World w; w.W=w.H=12;w.NC=144;w.me=20;w.rnd=436;w.len=8;w.head=90;w.face=0;
 w.body={78,79,80,81,82,83,91,90};w.own.assign(w.NC,0);
 for(int i=0;i<8;i++)w.own[w.body[i]]=i+1;
 w.occ.assign(w.NC,-1);w.dest_tab.assign(w.NC*4,ares::BLOCKED);
 w.parts={{77,1,true,true,0,3}};w.ally_heads={0};w.occ[77]=0;
 w.dest_tab[77*4+1]=78;w.dest_tab[78*4+1]=79;
 ares::Policy p;assert(p.local_obstruction_feed(w));
 // An existing queen exit removes the reason to sacrifice.
 w.dest_tab[77*4]=65;assert(!p.local_obstruction_feed(w));w.dest_tab[77*4]=ares::BLOCKED;
 // Unknown terrain, attackers, early game and an invisible queen fail closed.
 w.dest_tab[77*4]=ares::UNKNOWN;assert(!p.local_obstruction_feed(w));w.dest_tab[77*4]=ares::BLOCKED;
 w.parts.push_back({76,9,false,true,0,3});w.enemy_heads={1};assert(!p.local_obstruction_feed(w));w.enemy_heads.clear();
 w.rnd=399;assert(!p.local_obstruction_feed(w));w.rnd=436;
 w.ally_heads.clear();assert(!p.local_obstruction_feed(w));w.ally_heads={0};
 // Another local blocker with a lower ID wins the donor election.
 w.parts.push_back({65,10,true,false,0,3});w.occ[65]=2;w.dest_tab[77*4]=65;
 assert(!p.local_obstruction_feed(w));
}
'''
MOVE = r'''
#include "bokuto.hpp"
#include <cassert>
int main() {
 ares::World w;w.W=w.H=16;w.NC=256;w.me=0;w.rnd=438;w.len=31;w.units=20;w.limit=64;w.head=200;
 for(int c=226;c<256;c++)w.body.push_back(c);w.body.push_back(w.head);
 w.own.assign(w.NC,0);for(int i=0;i<31;i++)w.own[w.body[i]]=i+1;
 w.occ.assign(w.NC,-1);w.pearl_seen.assign(w.NC,-1);w.dest_tab.resize(w.NC*4);
 for(int c=0;c<w.NC;c++)for(int d=0;d<4;d++)w.dest_tab[c*4+d]=w.nbr(c,d);
 w.seen.assign(w.NC,w.rnd+1);
 bokuto::Guard g;g.queen_mode=true;g.no_dive=true;g.mark_heads(w);
 // Landing safety forces search beyond the old three-step ceiling.
 g.enemy_reach.assign(w.NC,1);g.enemy_reach[120]=0;
 auto path=g.free_queen_escape(w,6);assert(path.size()>=5 && path.size()<=8);
 ares::Policy p;auto sim=p.simulate(w,path);assert(sim.status==ares::Policy::SimStatus::OK);
 assert(sim.body.size()==31 && sim.body.back()==120);
 g.enemy_reach[120]=1;assert(g.free_queen_escape(w,6).empty());
 w.rnd=100;g.enemy_reach[120]=0;assert(g.free_queen_escape(w,6).empty());
 w.rnd=438;w.body.pop_back();assert(g.free_queen_escape(w,6).empty());
}
'''
class IsolatedSafetyTest(unittest.TestCase):
 def test_variants(self):
  with tempfile.TemporaryDirectory() as tmp:
   for name,code in [('kuroo-04-local-obstruction-feed',FEED),('kuroo-05-free-queen-escape',MOVE)]:
    src=Path(tmp)/'test.cpp';src.write_text(code);exe=Path(tmp)/name
    subprocess.run(['g++','-std=c++20','-O1','-I',str(ROOT/'bots'/name),str(src),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()

"""Queen-selected obstruction rescue is targeted, fresh and locally validated."""
from pathlib import Path
import subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
CPP=r'''
#include "policy.hpp"
#include <cassert>
ares::World world() {
 ares::World w;w.W=w.H=12;w.NC=144;w.me=1;w.team='A';w.rnd=435;
 w.len=8;w.head=78;w.body={84,85,86,87,88,89,90,78};
 w.own.assign(w.NC,0);for(int i=0;i<8;i++)w.own[w.body[i]]=i+1;
 w.occ.assign(w.NC,-1);w.dest_tab.assign(w.NC*4,ares::BLOCKED);
 w.parts={{77,573,true,false,0,3}};w.occ[77]=0;
 w.dest_tab[78*4+3]=77;
 for(int c=70;c<77;c++){w.dest_tab[c*4+1]=c+1;w.dest_tab[(c+1)*4+3]=c;}
 return w;
}
int main() {
 auto q=world();ares::Policy p;
 auto target=p.distress_target(q);assert(target.first==573 && target.second==77);
 // Existing roomy terrain, early/short/partial queen, or a nearby attacker do not request.
 q.dest_tab[78*4]=66;for(int c=60;c<70;c++)q.dest_tab[c*4+1]=c+1;
 q.dest_tab[66*4]=54;for(int c=40;c<60;c++)q.dest_tab[c*4+1]=c+1;
 assert(p.distress_target(q).first<0);
 q=world();q.rnd=399;assert(p.distress_target(q).first<0);
 q=world();q.body.pop_back();assert(p.distress_target(q).first<0);
 q=world();q.parts.push_back({80,9,false,true,0,3});q.enemy_heads={1};
 q.parts.push_back({76,573,true,true,0,3});q.ally_heads={2};assert(p.distress_target(q).first<0);
 q=world();auto packet=p.distress_packet(q,573,77);assert(packet);
 ares::World donor=world();donor.me=573;donor.head=120;donor.len=37;
 donor.body={77,119,120};donor.own.assign(donor.NC,0);
 for(int c:donor.body)donor.own[c]=1;
 donor.parts.clear();donor.ally_heads.clear();donor.enemy_heads.clear();
 ares::Policy receiver;receiver.queen_id=1;receiver.hear_distress(donor,packet);
 assert(receiver.distress_feed_ready(donor)); // queen head outside donor vision
 donor.own[77]=0;assert(receiver.distress_feed_ready(donor)); // current queen certificate, unknown tail
 donor.rnd=436;assert(!receiver.distress_feed_ready(donor)); // no stale unknown-tail certificate
 donor.rnd=435;donor.own[77]=1;
 donor.me=574;ares::Policy other;other.hear_distress(donor,packet);assert(!other.distress_feed_ready(donor));
 donor.me=573;donor.rnd=438;assert(!receiver.distress_feed_ready(donor));
 donor.rnd=434;assert(!receiver.distress_feed_ready(donor));
 donor.rnd=436;donor.own[77]=0;assert(!receiver.distress_feed_ready(donor));donor.own[77]=1;
 donor.parts={{76,9,false,true,0,3}};donor.enemy_heads={0};assert(!receiver.distress_feed_ready(donor));donor.enemy_heads.clear();
 donor.team='B';ares::Policy wrongteam;wrongteam.hear_distress(donor,packet);assert(!wrongteam.distress_feed_ready(donor));donor.team='A';
 ares::Policy corrupted;corrupted.hear_distress(donor,packet^(1ULL<<56));assert(!corrupted.distress_feed_ready(donor));
 receiver.queen_id=0;assert(!receiver.distress_feed_ready(donor));receiver.queen_id=1;
 // Older reports cannot rewind the latest request.
 q.rnd=436;receiver.hear_distress(donor,p.distress_packet(q,573,76));
 assert(receiver.distress_cell==76);receiver.hear_distress(donor,packet);assert(receiver.distress_cell==76);
}
'''
class DistressTest(unittest.TestCase):
 def test_protocol_and_request(self):
  with tempfile.TemporaryDirectory() as tmp:
   src=Path(tmp)/'test.cpp';src.write_text(CPP);exe=Path(tmp)/'test'
   subprocess.run(['g++','-std=c++20','-O1','-I',str(ROOT/'bots/kuroo-06-targeted-distress'),str(src),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()

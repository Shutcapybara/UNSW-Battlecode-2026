"""Diagonal visible queens must not invalidate a fresh opening request."""
from pathlib import Path
import subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
CPP=r'''
#include "policy.hpp"
#include <cassert>
int main(int argc,char**argv) {
 ares::World q;q.W=q.H=12;q.NC=144;q.me=1;q.team='A';q.rnd=435;q.len=31;
 ares::Policy sender;auto packet=sender.distress_packet(q,62,77);assert(packet);
 auto w=q;w.me=62;w.len=70;w.head=78;w.body={80,79,77,78};w.own.assign(w.NC,0);
 for(int c:w.body)w.own[c]=1;
 w.parts={{103,1,true,true,0,3}};w.ally_heads={0};
 ares::Policy receiver;receiver.queen_id=1;receiver.hear_distress(w,packet);
 assert(w.tdist(103,77)==4 && w.cheb(103,77)==2);
 assert(receiver.distress_feed_ready(w)==(argv[1][0]=='N'));
 w.parts[0].cell=125;assert(!receiver.distress_feed_ready(w)); // beyond visibility
 w.rnd=438;w.parts[0].cell=103;assert(!receiver.distress_feed_ready(w)); // expired
}
'''
class VisibilityTest(unittest.TestCase):
 def test_diagonal_request(self):
  with tempfile.TemporaryDirectory() as tmp:
   src=Path(tmp)/'test.cpp';src.write_text(CPP)
   for bot,mode in [('kuroo-06-targeted-distress','O'),('kuroo-07-distress-visibility','N')]:
    exe=Path(tmp)/bot
    subprocess.run(['g++','-std=c++20','-O1','-I',str(ROOT/'bots'/bot),str(src),'-o',str(exe)],check=True)
    subprocess.run([str(exe),mode],check=True)
if __name__=='__main__':unittest.main()

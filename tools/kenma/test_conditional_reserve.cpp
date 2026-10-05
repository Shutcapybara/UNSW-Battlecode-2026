#include <cassert>
#include <iostream>
#include "kenma_reserve.hpp"
ares::World world(){ares::World w;w.W=8;w.H=8;w.NC=64;w.me=2;w.team='A';w.head=18;w.ek.assign(128,ares::EK_KELP);return w;}
int main(){
 auto w=world();for(auto e:std::vector<std::pair<int,int>>{{18,1},{19,2},{27,3},{26,0}})w.ek[w.ekey(e.first,e.second)]=ares::EK_OPEN;
 assert(!kenma::queen_component_open(w,18));w.ek[w.ekey(18,0)]=ares::EK_UNK;assert(!kenma::queen_component_open(w,18));
 w.ek[w.ekey(18,0)]=ares::EK_PORTAL;assert(kenma::queen_component_open(w,18));
 w=world();std::fill(w.ek.begin(),w.ek.end(),ares::EK_OPEN);assert(kenma::queen_component_open(w,18));kenma::ReserveState state;state.observe(w);assert(!state.released); // Own open space says nothing about the queen.
 w.parts.push_back({18,0,true,true,0,3});w.ally_heads={0};state.observe(w);assert(state.released);
 w.ally_heads.clear();w.parts.clear();w.me=0;kenma::ReserveState queen;queen.observe(w);assert(queen.released);
 uint64_t rng=1234567;ares::Policy p;w.me=2;
 for(int type=1;type<=7;++type)for(int k=0;k<1000;++k){rng=rng*6364136223846793005ULL+1;uint64_t payload=rng&((1ULL<<44)-1);auto original=ares::Policy::pack(w,type,payload);p.sonar_out={original,0,original,0};state.tag(w,p);assert(p.sonar_out[1]==0&&p.sonar_out[3]==0);int kind=0;uint64_t actual=0;assert(ares::Policy::unpack(w,p.sonar_out[0],kind,actual));assert(kind==(type|8)&&actual==payload);w.msgs={p.sonar_out[0]};kenma::ReserveState receiver;receiver.observe(w);assert(receiver.released&&w.msgs[0]==original);p.sonar_out[0]=w.msgs[0];receiver.tag(w,p);assert(p.sonar_out[0]!=original);}
 auto packet=ares::Policy::pack(w,9,0);w.team='B';w.msgs={packet};kenma::ReserveState enemy;enemy.observe(w);assert(!enemy.released);w.team='A';w.msgs={packet^1};kenma::ReserveState bad;bad.observe(w);assert(!bad.released);
 std::cout<<"Reserve proof: closed/unknown/portal/open terrain, queen-only seed, 7000 full-payload packet roundtrips, relay and corrupt/opposing-tag guards passed\n";
}

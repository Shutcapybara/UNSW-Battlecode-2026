#include <cassert>
#include <iostream>
#include "kenma_pocket.hpp"
ares::World pocket(int length) {
    ares::World w;w.W=8;w.H=8;w.NC=64;w.me=0;w.rnd=10;w.len=length;w.units=64;w.limit=64;w.head=18;w.face=0;
    w.ek.assign(128,ares::EK_KELP);w.dest_tab.resize(256);
    for(auto e:std::vector<std::pair<int,int>>{{18,1},{19,2},{27,3},{26,0}})w.ek[w.ekey(e.first,e.second)]=ares::EK_OPEN;
    w.rebuild_dest();w.seen.assign(64,w.rnd+1);w.pearl_seen.assign(64,-1);w.bed.assign(64,-1);w.spawn_at.assign(64,-1);w.occ.assign(64,-1);
    w.body=length==3?std::vector<int>{27,26,18}:std::vector<int>{26,18};return w;
}
int main(int argc,char** argv){ares::Policy p;ares::Decision d;
 if(argc>1){int target=std::stoi(argv[1]);auto [ct,g]=unswbc::init();ares::World w;w.init(ct,g);bool checked=false;while(unswbc::update(ct,g)){w.sense(ct,g);if(w.rnd==target){assert(kenma::queen(w,p,d));assert(d.dirs.size()==2);auto s=p.simulate(w,d.dirs);assert(s.body.size()==2);checked=true;}}assert(checked);std::cout<<"Observed countdown triggers preventive sprint at round "<<target<<"\n";return 0;}
 auto w=pocket(3);assert(kenma::queen(w,p,d)&&d.dirs.size()==1);assert(p.simulate(w,d.dirs).body.size()==3);
 w.bed[19]=1;w.spawn_at[19]=w.rnd+2;assert(kenma::queen(w,p,d)&&d.dirs.size()==1);
 w.spawn_at[19]=w.rnd+1;assert(kenma::queen(w,p,d)&&d.dirs.size()==2);assert(p.simulate(w,d.dirs).body.size()==2);
 w=pocket(2);w.pearl_seen[19]=w.rnd;w.bed[19]=1;w.spawn_at[19]=w.rnd+30;assert(kenma::queen(w,p,d)&&d.dirs.size()==1);assert(p.simulate(w,d.dirs).body.size()==3);
 w.pearl_seen[27]=w.rnd;assert(kenma::growth_pressure(w,{1}));assert(kenma::queen(w,p,d));assert(p.simulate(w,d.dirs).status==ares::Policy::SimStatus::OK);
 w=pocket(3);w.seen[19]=w.rnd;assert(kenma::queen(w,p,d)&&d.dirs.size()==2);
 w=pocket(3);w.rnd=unswbc::Constants::MAX_ROUNDS-1;w.pearl_seen[19]=w.rnd;assert(kenma::queen(w,p,d)&&d.dirs.size()==1);assert(p.simulate(w,d.dirs).body.size()==4);
 std::cout<<"Countdown pocket: normal length3, observed next-round pressure, regrowth, remaining food, stale view and final-turn growth passed\n";
}

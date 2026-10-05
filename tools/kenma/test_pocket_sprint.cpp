#include <cassert>
#include <iostream>
#include "kenma_pocket.hpp"
// Four cells on a toroidal board, with all external edges proven closed.
ares::World pocket(int length) {
    ares::World w;w.W=8;w.H=8;w.NC=64;w.me=0;w.rnd=10;w.len=length;w.units=64;w.limit=64;w.head=18;w.face=0;
    w.ek.assign(128,ares::EK_KELP);w.dest_tab.resize(256);
    for(auto edge:std::vector<std::pair<int,int>>{{18,1},{19,2},{27,3},{26,0}})w.ek[w.ekey(edge.first,edge.second)]=ares::EK_OPEN;
    w.rebuild_dest();w.seen.assign(64,w.rnd+1);w.pearl_seen.assign(64,-1);w.occ.assign(64,-1);
    w.body=length==3?std::vector<int>{27,26,18}:std::vector<int>{26,18};return w;
}
int main(int argc,char** argv){
    ares::Policy p;
    if(argc>1){auto [ct,g]=unswbc::init();ares::World w;w.init(ct,g);int shrink=0,full=0;while(unswbc::update(ct,g)){w.sense(ct,g);ares::Decision d;if(kenma::queen(w,p,d)&&d.act==ares::Act::MOVE&&d.dirs.size()==2){auto s=p.simulate(w,d.dirs);assert(s.status==ares::Policy::SimStatus::OK);assert(s.body.size()==2);++shrink;}if(w.len==4&&w.units==w.limit)++full;}assert(shrink>0&&full==1);std::cout<<"Recorded failure has "<<shrink<<" legal preventive sprints; one full-pocket terminal turn\n";return 0;}
    auto w=pocket(3);assert(kenma::pocket_size(w)==4);ares::Decision d;
    assert(kenma::queen(w,p,d));assert(d.dirs==std::vector<int>({1,2}));auto s=p.simulate(w,d.dirs);assert(s.body.size()==2&&s.eaten==0);
    // Iterate actual movement state, forcing intermittent pearls while at population cap.
    for(int round=0;round<80;++round){assert(kenma::queen(w,p,d));assert(d.act==ares::Act::MOVE);s=p.simulate(w,d.dirs);assert(s.status==ares::Policy::SimStatus::OK&&s.body.size()==2);w.body=s.body;w.head=w.body.back();w.len=2;w.face=d.dirs.back();++w.rnd;std::fill(w.pearl_seen.begin(),w.pearl_seen.end(),-1);if(round%3==0){for(int dir=0;dir<4;++dir){int n=w.dest(w.head,dir);if(n>=0&&std::find(w.body.begin(),w.body.end(),n)==w.body.end()){w.pearl_seen[n]=w.rnd;break;}}}}
    w=pocket(3);w.pearl_seen[19]=w.rnd;assert(p.simulate(w,{1,2}).status!=ares::Policy::SimStatus::OK);assert(kenma::queen(w,p,d)&&d.dirs.size()==1); // Cannot shed after colliding with existing tail.
    w=pocket(2);w.pearl_seen[19]=w.rnd;assert(kenma::queen(w,p,d)&&d.dirs.size()==2);s=p.simulate(w,d.dirs);assert(s.body.size()==2&&s.eaten==1);
    w=pocket(3);w.me=2;assert(!kenma::queen(w,p,d));w.me=0;w.ek[w.ekey(18,3)]=ares::EK_UNK;assert(!kenma::queen(w,p,d));
    std::cout<<"Pocket sprint: 80 food/empty transitions at full population, growth-before-tax collision, nonqueen and unknown guards passed\n";
}

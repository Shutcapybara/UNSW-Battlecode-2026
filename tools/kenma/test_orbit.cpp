#include <cassert>
#include <iostream>
#include "kenma_orbit.hpp"
ares::World world(int head=27) {
    ares::World w;
    w.W=8;w.H=8;w.NC=64;w.me=0;w.rnd=10;w.len=3;w.units=3;w.head=head;w.face=1;
    w.ek.assign(128,ares::EK_OPEN);w.dest_tab.resize(256);w.rebuild_dest();
    w.seen.assign(64,w.rnd+1);w.bed.assign(64,-1);w.pearl_seen.assign(64,-1);w.occ.assign(64,-1);
    int tail=w.nbr(w.nbr(head,3),3);w.body={tail,w.nbr(head,3),head};
    return w;
}
int main() {
    ares::Policy pol;
    // Exercise the real protocol parser and memory update before synthetic rollouts.
    std::ostringstream protocol;
    protocol << "ID 0\nTEAM A\nMAP 8 8\nUNIT_LIMIT 64\nROUND 10\nDIR E\nLENGTH 3\nUNIT_COUNT 3\nNUM_MSGS 0\n";
    for(int y=0;y<7;++y)for(int x=0;x<7;++x)protocol<<x<<" "<<y<<" 0 -1\n";
    protocol<<"DRAGON_BODIES 3\nA 0 3 3 E 1\nA 0 2 3 E 0\nA 0 1 3 E 0\n";
    for(int y=0;y<8;++y)protocol<<". . . . . . .\n";
    for(int y=0;y<7;++y)protocol<<". . . . . . . .\n";
    protocol<<"ENDGAME\n";
    std::istringstream input(protocol.str());
    auto* original_input=std::cin.rdbuf(input.rdbuf());
    auto [ct,game]=unswbc::init();
    ares::World observed;observed.init(ct,game);
    assert(unswbc::update(ct,game));observed.sense(ct,game);
    assert(observed.seen[observed.head]==observed.rnd+1);
    assert(observed.bed[observed.head]==-1);
    assert(observed.body.size()==3);
    kenma::Orbit parsed_orbit;ares::Decision parsed_decision;
    assert(parsed_orbit.choose(observed,pol,parsed_decision));
    assert(parsed_decision.why=='o');
    assert(!unswbc::update(ct,game));
    std::cin.rdbuf(original_input);

    for(int head:{27,0}) {
        auto w=world(head);kenma::Orbit orbit;ares::Decision out;
        assert(orbit.choose(w,pol,out));auto ring=orbit.cells;
        for(int round=0;round<40;++round) {
            out=ares::Decision{};assert(orbit.choose(w,pol,out));assert(orbit.cells==ring);
            assert(out.dirs.size()==1);
            auto sim=pol.simulate(w,out.dirs);assert(sim.status==ares::Policy::SimStatus::OK);
            assert(sim.body.size()==3 && !sim.eaten);
            w.body=sim.body;w.head=w.body.back();w.face=out.dirs[0];++w.rnd;
            std::fill(w.seen.begin(),w.seen.end(),w.rnd+1);
        }
        w.parts.push_back({ring[1],8,true,false,0,3});
        assert(!kenma::Orbit::valid(w,ring));
    }
    for(int variant=0;variant<10;++variant) {
        auto w=world();kenma::Orbit orbit;ares::Decision out;
        if(variant==0)w.me=2;
        if(variant==1)w.units=2;
        if(variant==2)w.body.pop_back();
        if(variant==3)std::fill(w.bed.begin(),w.bed.end(),1);
        if(variant==4)std::fill(w.pearl_seen.begin(),w.pearl_seen.end(),w.rnd);
        if(variant==5){std::fill(w.ek.begin(),w.ek.end(),ares::EK_UNK);w.rebuild_dest();}
        if(variant==6){w.parts.push_back({w.nbr(w.head,0),9,false,true,0,3});w.enemy_heads={0};}
        if(variant==7){out.act=ares::Act::SPLIT;out.split=2;}
        if(variant==8)w.seen[w.head]=w.rnd; // World stores last-seen round + 1.
        if(variant==9)std::fill(w.bed.begin(),w.bed.end(),0); // Unknown is not confirmed empty.
        auto original=out;
        assert(!orbit.choose(w,pol,out));assert(out.act==original.act && out.split==original.split);
    }
    std::cout<<"Queen orbit: real protocol/sense activation plus 80 stable turns including torus entry; body/food/bed/threat/unknown/population/split guards passed\n";
}

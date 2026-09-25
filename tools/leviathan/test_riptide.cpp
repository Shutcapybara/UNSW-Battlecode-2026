#include <cassert>
#include <iostream>
#ifndef RIPTIDE_VIABILITY
#include "../../bots/leviathan-x01-riptide-horizon/planner.h"
#else
#include "../../bots/leviathan-x02-riptide-viability/planner.h"
#endif
World board() {
    World w;w.setup(11,11);std::fill(w.edges.begin(),w.edges.end(),-1);w.rebuild();
    w.round=10;w.head=60;w.id=1;w.length=3;w.units=1;w.body={60,59,58};w.history=w.body;
    return w;
}
int main() {
    {auto w=board();assert(w.next(0,0)==110&&w.next(0,3)==10);
     w.learn(w.key(60,1),"257");w.rebuild();assert(w.next(60,1)==-1);
     w.learn(w.key(20,3),"257");w.rebuild();assert(w.next(60,1)==20&&w.next(20,3)==60);
     w.learn(w.key(60,1),"1");w.rebuild();assert(w.next(60,1)==-1);
     assert(w.portals[257].size()==1);}
    {auto w=board();Planner p(w);Node n;n.body=w.body;
     assert(!p.step(n,3,0)); // neck is occupied before the tail moves
     n.body={60,61,72,71};assert(!p.step(n,2,0)); // own tail still occupies 71
    }
    {auto w=board();Planner p(w);Node n;n.body={60,59};
     assert(p.step(n,1,0));assert(!p.step(n,1,0,1));
     w.tiles[61].seen=9;w.tiles[61].pearl=9;
     n=Node{};n.body={60,59};assert(p.step(n,1,0));assert(n.body.size()==2);
     assert(!p.step(n,1,0,1)); // remembered pearl cannot buy an extra step
     w.tiles[61].seen=10;w.tiles[61].pearl=10;
     n=Node{};n.body={60,59};assert(p.step(n,1,0));assert(n.body.size()==3);
     assert(p.step(n,1,0,1));assert(n.body.size()==2);
    }
    {auto w=board();Planner p(w);Node n;n.body=w.body;
     w.tiles[61].bed=true;w.tiles[61].due=11;
     assert(p.step(n,1,0));assert(n.body.size()==3); // forecast does not grow this action
     n=Node{};n.body=w.body;assert(p.step(n,1,1));assert(n.body.size()==4);
    }
    {auto w=board();w.id=65537;auto a=w.packet(60,17);w.id=1;auto b=w.packet(60,17);
     assert(a!=b);w.id=2;w.hear(a);w.hear(b);assert(w.reports.size()==2);
     assert(w.reports[65537].length==17);w.reports.clear();w.hear(a^(1ULL<<23));assert(w.reports.empty());
     w.team='B';w.hear(a);assert(w.reports.empty());w.team='A';w.round=15;w.hear(a);assert(w.reports.empty());
    }
    {auto w=board();w.length=4;w.body={60,59,58,57};w.history=w.body;Planner p(w);p.model();
     assert(!p.fork()); // empty area does not fund a colony
     w.tiles[61].bed=true;w.tiles[61].due=10;
     assert(!p.fork()); // one shared food source is not two catchments
     w.tiles[56].bed=true;w.tiles[56].due=10;assert(p.fork());
     w.round=P::split_stop;assert(!p.fork());w.round=10;w.units=64;assert(!p.fork());
    }
    {auto w=board();Planner p(w);auto a=p.decide();assert(!a.path.empty());assert(a.depth==P::horizon);
     Node n;n.body=w.body;for(size_t i=0;i<a.path.size();i++)assert(p.step(n,std::string(DIRS).find(a.path[i]),0,i));}
#ifdef RIPTIDE_VIABILITY
    {auto w=board();Planner p(w);assert(p.capacity(w.body)>=20);
     std::fill(w.edges.begin(),w.edges.end(),-3);w.rebuild();assert(p.capacity(w.body)==1);
     w.learn(w.key(60,1),".");w.rebuild();assert(p.capacity(w.body)==2);
    }
#endif
    std::cout<<"Riptide geometry, simulation, forecast, identity, colony and planner checks passed\n";
}

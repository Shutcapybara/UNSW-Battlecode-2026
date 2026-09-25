#include <cassert>
#include <iostream>
#include "../../bots/leviathan-x04-charybdis-replies/planner.h"
World board() {
    World w;w.setup(11,11);std::fill(w.edges.begin(),w.edges.end(),-1);w.rebuild();
    w.round=10;w.head=60;w.id=1;w.length=3;w.units=2;w.body={60,59,58};w.history=w.body;
    for(auto&t:w.tiles)t.seen=w.round;
    for(int c:w.body)w.parts[c]={1,true,c==60,1};
    w.parts[62]={2,false,true,3};w.parts[63]={2,false,false,3};w.enemy_heads={62};
    return w;
}
Action move(std::string path){Action a;a.path=path;return a;}
int main(){
    {auto w=board();Planner p(w);auto s=p.model();assert(p.opponent==2);
     assert(p.apply(s,move("N")));assert(s.actor==1&&s.clock==0);
     assert(p.apply(s,move("N")));assert(s.actor==0&&s.clock==1);}
    {auto w=board();w.parts[62].id=w.parts[63].id=0;Planner p(w);auto s=p.model();
     assert(p.apply(s,move("N")));assert(s.actor==1&&s.clock==1);
     assert(p.apply(s,move("N")));assert(s.actor==0&&s.clock==1);}
    {auto w=board();Planner p(w);auto s=p.model();
     assert(!p.apply(s,move("W"))); // collision is checked before tail release
     s=p.model();assert(p.apply(s,move("EE")));assert(!s.snakes[0].alive&&!s.snakes[1].alive);
     assert(p.pearl(s,61)&&p.pearl(s,62)); // head clash leaves alternating carcass pearls
    }
    {auto w=board();w.body={60,59};w.length=2;w.tiles[61].pearl=9;
     Planner p(w);auto s=p.model();assert(!p.apply(s,move("EN")));
     w.tiles[61].pearl=10;Planner p2(w);s=p2.model();assert(p2.apply(s,move("EN")));assert(s.snakes[0].body.size()==2);}
    {auto w=board();w.length=4;w.body={60,59,58,57};w.parts[57]={1,true,false,1};
     Planner p(w);auto s=p.model();Action a;a.split=true;assert(p.apply(s,a));
     assert(s.snakes.size()==3&&s.snakes[2].body==vector<int>({57,58}));
     assert(s.actor==1&&s.clock==0);assert(p.apply(s,move("N")));
     assert(s.actor==2&&s.clock==0); // newborn acts this round after older IDs
     assert(p.apply(s,move("N")));assert(s.actor==0&&s.clock==1);
     w.units=w.limit;Planner full(w);s=full.model();assert(!full.apply(s,a));}
    {auto w=board();w.tiles[61].bed=true;w.tiles[61].due=11;Planner p(w);auto s=p.model();
     assert(!p.pearl(s,61));p.advance(s,100);assert(s.clock==1&&p.pearl(s,61));
     s=p.model();s.snakes[0].body[0]=61;p.advance(s,100);assert(!p.pearl(s,61));}
    {auto w=board();w.tiles[64].seen=-1000;Planner p(w);p.model();assert(p.opponent==-1);}
    {auto w=board();w.tiles[61].pearl=w.round;Planner p(w);auto s=p.model();
     auto east=s,north=s;assert(p.apply(east,move("E"))&&p.apply(north,move("N")));
     assert(p.evaluate(east)>p.evaluate(north));int a=600,b=600;
     assert(p.search(east,3,a,-1e30,1e30)<p.search(north,3,b,-1e30,1e30));}
    {auto w=board();Planner p(w);auto s=p.model();int budget=3;
     p.search(s,0,budget,-1e30,1e30);assert(budget==2); // leaf evaluation consumes the budget too
     auto action=p.decide();assert(p.nodes>0&&p.nodes<=P::node_budget+21);
     s=p.model();assert(p.apply(s,action));}
    std::cout<<"Charybdis turn order, newborn turns, clashes, food timing, uncertainty and adversarial replies passed\n";
}

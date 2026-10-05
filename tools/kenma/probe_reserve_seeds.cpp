// Fixed-observation diagnosis only. Does visible queen body seed proof earlier?
#include <iostream>
#include "policy.hpp"
#include "kenma_reserve.hpp"
int main(){
 auto [ct,g]=unswbc::init();ares::World w;w.init(ct,g);kenma::ReserveState old;
 bool broader=false;int first_old=-1,first_broader=-1,extra_turns=0;
 while(unswbc::update(ct,g)){
  w.sense(ct,g);old.observe(w);broader=broader||old.released;
  if(!broader)for(auto const& p:w.parts)
   if(p.ally && p.id<=1 && kenma::queen_component_open(w,p.cell)){broader=true;break;}
  if(old.released && first_old<0)first_old=w.rnd;
  if(broader && first_broader<0)first_broader=w.rnd;
  if(broader && !old.released)++extra_turns;
 }
 std::cout<<first_old<<" "<<first_broader<<" "<<extra_turns<<"\n";
}

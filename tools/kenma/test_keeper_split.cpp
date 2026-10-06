#include <cassert>
#include <cmath>
#include <iostream>
#include "policy.hpp"
#include "kenma_split_prior.hpp"
int main(){
 double p[7]={.1,.2,.05,.15,.25,.15,.1};assert(std::abs(kenma::split_log_odds(p))<1e-12);
 double q[7]={.1,.2,.05,.4,.15,.05,.05};assert(std::abs(kenma::split_log_odds(q)-std::log(1.0/3))<1e-12);
 for(double& v:q)v*=7;assert(std::abs(kenma::split_log_odds(q)-std::log(1.0/3))<1e-12);
 double move[7]={1,0,0,0,0,0,0},split[7]={0,0,0,0,1,0,0},zero[7]={};
 assert(std::abs(kenma::split_log_odds(move)-std::log(1e-4))<1e-12);
 assert(std::abs(kenma::split_log_odds(split)+std::log(1e-4))<1e-12);
 assert(kenma::split_log_odds(zero)==0);
 // Verify the actual opening score hook and explicit rescue exemption.
 ares::World w;w.W=8;w.H=8;w.NC=64;w.len=6;w.units=3;w.limit=64;w.rnd=ares::Params::opening_production_start;w.born=w.rnd;w.me=99;
 ares::Policy base,prior;prior.kenma_split_log_odds=-2.0;int ka=0,kb=0;double a=0,b=0;char wa=0,wb=0;
 assert(base.tyr_opening_split(w,ka,a,wa)&&prior.tyr_opening_split(w,kb,b,wb));assert(wa=='s'&&wb=='s'&&ka==kb&&std::abs(a-b-2)<1e-12);
 w.rnd=0;w.born=0;w.me=0;w.len=ares::Params::opening_rescue_min_len;
 assert(base.tyr_opening_split(w,ka,a,wa)&&prior.tyr_opening_split(w,kb,b,wb));assert(wa=='r'&&wb=='r'&&ka==kb&&a==b);
 std::cout<<"Keeper split prior: probability aggregation, scale invariance, floors, actual production-score hook and rescue exemption passed\n";
}

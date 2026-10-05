#include <cassert>
#include <cmath>
#include <iostream>
#include "kenma_blend.hpp"
int main(){
 std::vector<double> p{.5,.3,.2};auto a=kenma::blend_direction(p,{.5,.3,.2});
 for(int i=0;i<3;++i)assert(std::abs(a[i]-p[i])<1e-12);
 auto b=kenma::blend_direction(p,{.1,.8,.1});assert(b[1]>b[0] && b[0]>b[2]);
 assert(std::abs(b[0]/b[1]-std::sqrt(.05/.24))<1e-12);
 auto c=kenma::blend_direction({1,0,0},{0,1,0});assert(std::abs(c[0]-c[1])<1e-12);
 assert(c[2]>0 && std::abs(c[0]+c[1]+c[2]-1)<1e-12);
 std::cout<<"Teacher blend: identity, normalized geometric ratios, directional preference and zero-probability floors passed\n";
}

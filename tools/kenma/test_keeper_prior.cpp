#include <cassert>
#include <cmath>
#include <iostream>
#include "policy.hpp"
int main() {
    double p[7]={0.12,0.18,0.06,0.24,0.1,0.2,0.1};
    for(int face=0;face<4;++face) {
        double out[4];kenma::keeper_log_prior(face,p,1.0,out);
        for(int rel=0;rel<4;++rel)assert(std::abs(out[(face+rel)&3]-std::log(p[rel]/0.6))<1e-12);
    }
    double zero[7]={0,0,0,0,1,0,0},out[4];
    kenma::keeper_log_prior(0,zero,1.0,out);
    for(double x:out)assert(std::isfinite(x) && std::abs(x-std::log(1e-4))<1e-12);
    std::cout<<"Keeper prior: movement conditioning, four facing rotations, and zero-mass floor passed\n";
}

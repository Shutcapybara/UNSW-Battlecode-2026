#include <cassert>
#include <cmath>
#include <iostream>
#include "kenma_prior.hpp"
int main() {
    double p[4]={0.6,0.1,0.1,0.2};
    double z=std::pow(.6,1.61)+std::pow(.1,1.61)+std::pow(.2,1.61);
    for(int face=0;face<4;++face) {
        double a[4]={0,0,0,0};kenma::stacked_search_prior(face,p,1,a);
        double sum=0;
        for(int rel:{0,1,3}) {
            assert(std::abs(a[(face+rel)&3]-std::log(std::pow(p[rel],1.61)/z))<1e-12);
            sum+=std::exp(a[(face+rel)&3]);
        }
        assert(std::abs(sum-1)<1e-12);assert(a[(face+2)&3]==0);
    }
    double tiny[4]={1e-250,0,1,0},a[4]={};kenma::stacked_search_prior(0,tiny,1,a);
    for(double v:a)assert(std::isfinite(v));
    std::cout<<"Calibrated prior: normalization, all rotations, reverse preservation and tiny-mass stability pass\n";
}

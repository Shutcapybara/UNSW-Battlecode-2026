// Sharpen and renormalize F/R/L probabilities before the unchanged search weight.
#pragma once
#include <algorithm>
#include <cmath>
namespace kenma {
inline void stacked_search_prior(int face,double const* p,double weight,double* absolute_logp) {
    static constexpr int rels[3]={0,1,3};
    double q[3],z=0;
    for(int i=0;i<3;++i){q[i]=std::pow(std::max(p[rels[i]],1e-30),1.61);z+=q[i];}
    for(int i=0;i<3;++i)absolute_logp[(face+rels[i])&3]=weight*std::log(std::max(q[i]/z,1e-4));
}
}

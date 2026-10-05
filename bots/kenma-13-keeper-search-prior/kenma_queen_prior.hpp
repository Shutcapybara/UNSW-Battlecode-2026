// Keeper probabilities guide the parent search for original queens only.
#pragma once
#include <algorithm>
#include <cmath>
#include "gbt_compact.hpp"
#include "kenma_queen_model.hpp"
namespace kenma {
inline void keeper_log_prior(int face,double const* probabilities,double weight,double* absolute_logp) {
    double total=0;
    for(int rel=0;rel<4;++rel)total+=probabilities[rel];
    for(int rel=0;rel<4;++rel)
        absolute_logp[(face+rel)&3]=weight*std::log(std::max(probabilities[rel]/std::max(total,1e-30),1e-4));
}
inline void queen_prior(int face,hb1::Row const& row,double weight,double* absolute_logp) {
    static hb1::Bound const bound{hb1::dirc_bind};
    auto x=bound.vec(row);
    double probabilities[7];
    GBT_PROBA(kenma_queen,x.data(),probabilities);
    keeper_log_prior(face,probabilities,weight,absolute_logp);
}
}

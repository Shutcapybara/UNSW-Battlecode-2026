// Split-vs-move likelihood only; parent movement ranking remains unchanged.
#pragma once
#include <algorithm>
#include <cmath>
#include "gbt_compact.hpp"
#include "kenma_queen_model.hpp"
namespace kenma {
inline double split_log_odds(double const* p){
    double move=p[0]+p[1]+p[2]+p[3],split=p[4]+p[5]+p[6];
    double z=std::max(move+split,1e-30);
    return std::log(std::max(split/z,1e-4))-std::log(std::max(move/z,1e-4));
}
inline double keeper_split_prior(hb1::Row const& row){
    static hb1::Bound const bound{hb1::dirc_bind};
    auto x=bound.vec(row);double p[7];GBT_PROBA(kenma_queen,x.data(),p);
    return split_log_odds(p);
}
}

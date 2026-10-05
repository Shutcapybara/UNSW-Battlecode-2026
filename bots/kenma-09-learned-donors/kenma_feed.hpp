// Donor classifier: only current legal HB-1 features; original queens excluded.
#pragma once
#include "policy.hpp"
#include "gbt_compact.hpp"
#include "kenma_feed_model.hpp"
namespace kenma {
inline double donor_probability(float const* x) {
    double margin[1];
    gbt::margins(kenma_feed::K,kenma_feed::N_TREES,kenma_feed::CMP,kenma_feed::BASE,
        kenma_feed::TREE_NODE,kenma_feed::TREE_LEAF,kenma_feed::THR,kenma_feed::F,
        kenma_feed::T,kenma_feed::R,kenma_feed::LEAF,x,margin);
    return 1.0/(1.0+std::exp(-margin[0])); // Binary margin; multiclass softmax would be wrong here.
}
inline bool learned_donor(ares::World const& w,hb1::Row const& row) {
    if (w.me<=1 || w.len>8 || w.units<2 || w.ally_heads.empty()) return false;
    static hb1::Bound const bound{hb1::dirc_bind};
    auto x=bound.vec(row);
    return donor_probability(x.data())>=0.9;
}
}

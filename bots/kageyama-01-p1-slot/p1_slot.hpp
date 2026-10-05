// The learned direction prior for the slot (D-065 §D): encoder v1 (learn_encode.hpp, bit-exact twin of
// tools/learn/encode.py) on this process's own blocks -> p1_model.hpp (export_gbt.py) -> P(F, R, B, L).
#pragma once
#include <array>
#include <cmath>
#include "learn_helper.hpp"
#include "gbt_compact.hpp"
#include "p1_model.hpp"

namespace p1slot {
static_assert(p1::N_FEAT == learn::N_X, "p1 model inputs must be encoder v1 columns in names() order");
static_assert(p1::K == 4, "p1 model classes must be F, R, B, L");

struct Slot {
    learn::Encoder enc;
    std::array<double, 4> p{};   // F, R, B, L
    bool ok = false;
    Slot(unswbc::Controller const& ct, unswbc::Game const& game) : enc(learn::spawn_from(ct, game)) {}

    // every turn, before the decision
    void observe(unswbc::Controller const& ct, unswbc::Game const& game) {
        ok = false;
        auto const& x = enc.observe(learn::block_from(ct, game));
        static std::array<float, learn::N_X> xf;
        for (int i = 0; i < learn::N_X; i++) xf[i] = float(x[i]);
        GBT_PROBA(p1, xf.data(), p.data());
        ok = true;
    }
    // every turn, the process's own action (kind 1 move, 2 split, 3 invalid), as the training rows recorded it
    void act(int kind, int first_rel, int nsteps, int round) { enc.act(kind, first_rel, nsteps, round); }
};
}  // namespace p1slot

// The learned direction prior for the slot (D-065 §D, D-066 §E): P(F, R, B, L) from p1_model.hpp (export_gbt.py),
// evaluated by gbt_compact.hpp on one of two inputs, fixed by the model header (p1::INPUT):
//   0  encoder v1 (learn_encode.hpp, bit-exact twin of tools/learn/encode.py) on this process's own blocks;
//   1  HB-1's feature vector: carthage-05's own extractor (hb1::Proc::features), the columns named in p1::FEAT_NAMES.
// KAGEYAMA_P1_MIRROR_AVG (p1_switch.hpp) = 1: arm A8b, the mean of P on the row and on its left-right mirror image
// (p1::MIRROR_* tables, the map of tools/hinata/r2_mirror.py) mapped back (R <-> L). Two model evaluations a turn.
#pragma once
#include <array>
#include <cmath>
#include <vector>
#include "learn_helper.hpp"
#include "gbt_compact.hpp"
#include "hb1_features.hpp"
#include "p1_model.hpp"

namespace p1slot {
static_assert(p1::K == 4, "p1 model classes must be F, R, B, L");
static_assert(p1::INPUT == 1 || p1::N_FEAT == learn::N_X, "an encoder-input model must take encoder v1's columns");

struct Slot {
    learn::Encoder enc;
    std::array<double, 4> p{};   // F, R, B, L
    std::array<float, p1::N_FEAT> x{}, xm{};
    Slot(unswbc::Controller const& ct, unswbc::Game const& game) : enc(learn::spawn_from(ct, game)) {}

    // input 0: every turn, before the decision
    void observe(unswbc::Controller const& ct, unswbc::Game const& game) {
        auto const& e = enc.observe(learn::block_from(ct, game));
        for (int i = 0; i < p1::N_FEAT; i++) x[i] = float(e[i]);
        predict();
    }
    // input 1: every turn, with this turn's HB-1 row (as Bound::vec builds the parent's model input)
    void observe_row(hb1::Row const& r) {
        for (int i = 0; i < p1::N_FEAT; i++) x[i] = float(r.get(p1::FEAT_NAMES[i]));
        predict();
    }
    void predict() {
        GBT_PROBA(p1, x.data(), p.data());
#if KAGEYAMA_P1_MIRROR_AVG
        for (int i = 0; i < p1::N_FEAT; i++) xm[i] = x[p1::MIRROR_SRC[i]];
        for (int j = 0; j < p1::N_MIRROR_NEG; j++) { float& v = xm[p1::MIRROR_NEG[j]]; if (v != 999.0f) v = -v; }
        {
            std::array<float, p1::N_FEAT> const orig = xm;
            for (int j = 0; j < p1::N_MIRROR_CODE; j++)
                if (orig[p1::MIRROR_CODE_IDX[j]] == float(p1::MIRROR_CODE_FROM[j])) xm[p1::MIRROR_CODE_IDX[j]] = float(p1::MIRROR_CODE_TO[j]);
        }
        std::array<double, 4> q;
        GBT_PROBA(p1, xm.data(), q.data());
        double const back[4] = {q[0], q[3], q[2], q[1]};   // mirror frame -> this frame: R <-> L
        for (int k = 0; k < 4; k++) p[k] = 0.5 * (p[k] + back[k]);
#endif
    }
    // input 0: every turn, the process's own action (kind 1 move, 2 split, 3 invalid), as the training rows recorded it
    void act(int kind, int first_rel, int nsteps, int round) { enc.act(kind, first_rel, nsteps, round); }
};
}  // namespace p1slot

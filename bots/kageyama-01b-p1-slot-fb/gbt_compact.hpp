// Generic evaluator for headers written by tools/learn/export_gbt.py (Data lane, kageyama; D-065 §D).
// Usage: #include "<model>.hpp" then gbt::proba<NS>(x, p) via the macro GBT_MODEL(NS), or call gbt::margins with the
// arrays directly. x: float features in the model's column order; NaN takes each node's default side.
#pragma once
#include <cmath>
#include <cstdint>

namespace gbt {

template <class Leaf>
inline void margins(int K, int n_trees, int cmp, double const* base, std::uint32_t const* tree_node,
                    std::uint32_t const* tree_leaf, double const* thr, std::uint16_t const* F, std::uint16_t const* T,
                    std::uint16_t const* R, Leaf const* leaf, float const* x, double* s) {
    for (int k = 0; k < K; k++) s[k] = base[k];
    for (int t = 0; t < n_trees; t++) {
        std::uint32_t i = tree_node[t];
        for (;;) {
            std::uint16_t f = F[i];
            if (f == 0x7FFF) { s[t % K] += double(leaf[tree_leaf[t] + T[i]]); break; }
            float v = x[f & 0x7FFF];
            bool left;
            if (std::isnan(v)) left = (f & 0x8000) != 0;
            else left = cmp == 0 ? double(v) <= thr[T[i]] : double(v) < thr[T[i]];
            i += left ? 1u : std::uint32_t(R[i]);
        }
    }
}

inline void softmax(int K, double const* s, double* p) {
    double mx = s[0];
    for (int k = 1; k < K; k++) mx = s[k] > mx ? s[k] : mx;
    double z = 0;
    for (int k = 0; k < K; k++) { p[k] = std::exp(s[k] - mx); z += p[k]; }
    for (int k = 0; k < K; k++) p[k] /= z;
}

}  // namespace gbt

// p[NS::K] = class probabilities of model namespace NS for features x
#define GBT_PROBA(NS, x, p)                                                                                     \
    do {                                                                                                        \
        double _s[NS::K];                                                                                       \
        gbt::margins(NS::K, NS::N_TREES, NS::CMP, NS::BASE, NS::TREE_NODE, NS::TREE_LEAF, NS::THR, NS::F, NS::T, \
                     NS::R, NS::LEAF, (x), _s);                                                                 \
        gbt::softmax(NS::K, _s, (p));                                                                           \
    } while (0)

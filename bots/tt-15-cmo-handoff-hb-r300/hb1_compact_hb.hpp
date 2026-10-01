// HB-1 hb1-04: evaluator for the 8-byte preorder direction model in hb1_direction_compact.hpp.
#pragma once
#include <cmath>
#include <cstdint>
#include <cstring>
#include <vector>
#include "hb1_models.hpp"
#include "hb1_direction_compact_hb.hpp"

namespace hb1 {

// Binding shell: the feature list and classes of the compact direction model, for Bound / class lookup.
inline Model const dirhb_bind{"direction_hb", dirhb_n_feat, dirhb_feats, dirhb_K, dirhb_K, dirhb_classes, dirhb_base, 0, nullptr, nullptr};

inline float dirhb_f32(unsigned long long w) {
    std::uint32_t u = std::uint32_t(w);
    float f;
    std::memcpy(&f, &u, 4);
    return f;
}

inline std::vector<double> dirhb_proba(std::vector<float> const& x) {
    double s[3] = {dirhb_base[0], dirhb_base[1], dirhb_base[2]};
    for (int t = 0; t < dirhb_n_trees; t++) {
        unsigned long long const* nd = dirhb_nodes + dirhb_tree_start[t];
        int j = 0;
        for (;;) {
            unsigned long long w = nd[j];
            unsigned f = unsigned(w >> 32) & 0x7FFFu;
            if (f == 0x7FFFu) { s[t % 3] += dirhb_f32(w); break; }
            float v = x[f];
            bool left = std::isnan(v) ? ((w >> 47) & 1u) : (v < dirhb_f32(w));
            j += left ? 1 : int(w >> 48);
        }
    }
    double mx = std::max(s[0], std::max(s[1], s[2])), z = 0;
    std::vector<double> p(3);
    for (int k = 0; k < 3; k++) { p[k] = std::exp(s[k] - mx); z += p[k]; }
    for (double& v : p) v /= z;
    return p;
}

}  // namespace hb1

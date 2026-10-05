// Kenma 08: exact 4-byte preorder nodes; branch thresholds are shared without rounding.
#pragma once
#include <cmath>
#include <cstdint>
#include <cstring>
#include <vector>
#include "hb1_models.hpp"
#include "hb1_direction_compact.hpp"

namespace hb1 {

// Binding shell: the feature list and classes of the compact direction model, for Bound / class lookup.
inline Model const dirc_bind{"direction_v04", dirc_n_feat, dirc_feats, dirc_K, dirc_K, dirc_classes, dirc_base, 0, nullptr, nullptr};

inline float dirc_f32(unsigned long long w) {
    std::uint32_t u = std::uint32_t(w);
    float f;
    std::memcpy(&f, &u, 4);
    return f;
}

inline std::vector<double> dirc_proba(std::vector<float> const& x) {
    double s[3] = {dirc_base[0], dirc_base[1], dirc_base[2]};
    for (int t = 0; t < dirc_n_trees; t++) {
        unsigned int const* nd = dirc_nodes + dirc_tree_start[t];
        int j = 0;
        for (;;) {
            unsigned int w = nd[j];
            unsigned f = w & 511u;
            if (!(w & (1u << 30))) { s[t % 3] += dirc_f32(w); break; }
            float v = x[f];
            bool left = std::isnan(v) ? ((w >> 31) & 1u) : (v < dirc_f32(dirc_thresholds[(w >> 18) & 4095u]));
            j += left ? 1 : int((w >> 9) & 511u);
        }
    }
    double mx = std::max(s[0], std::max(s[1], s[2])), z = 0;
    std::vector<double> p(3);
    for (int k = 0; k < 3; k++) { p[k] = std::exp(s[k] - mx); z += p[k]; }
    for (double& v : p) v /= z;
    return p;
}

}  // namespace hb1

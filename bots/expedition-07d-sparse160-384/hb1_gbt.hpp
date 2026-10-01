// HB-1: evaluator for the exported XGBoost models in hb1_models.hpp.
#pragma once
#include <cmath>
#include <string>
#include <vector>
#include "hb1_features.hpp"
#include "hb1_models.hpp"

namespace hb1 {

// Feature vector in a model's column order, filled from a Row by name (bound once).
struct Bound {
    Model const* m;
    std::vector<std::string> names;
    explicit Bound(Model const& model) : m(&model) {
        for (int i = 0; i < model.n_feat; i++) names.emplace_back(model.feats[i]);
    }
    std::vector<float> vec(Row const& r) const {
        std::vector<float> x(names.size());
        for (size_t i = 0; i < names.size(); i++) x[i] = float(r.get(names[i]));
        return x;
    }
};

// Raw margins, one per output (K = 1 for binary).
inline std::vector<double> margins(Model const& m, std::vector<float> const& x) {
    std::vector<double> s(m.base, m.base + m.K);
    for (int t = 0; t < m.n_trees; t++) {
        Node const* nd = m.nodes + m.tree_start[t];
        int n = 0;
        while (nd[n].f >= 0) {
            float v = x[nd[n].f];
            n = std::isnan(v) ? nd[n].miss : (v < nd[n].t ? nd[n].yes : nd[n].no);
        }
        s[t % m.K] += nd[n].leaf;
    }
    return s;
}

// Class probabilities in m.classes order.
inline std::vector<double> proba(Model const& m, std::vector<float> const& x) {
    auto s = margins(m, x);
    if (m.K == 1) {
        double p = 1.0 / (1.0 + std::exp(-s[0]));
        return {1.0 - p, p};
    }
    double mx = s[0];
    for (double v : s) mx = std::max(mx, v);
    double z = 0;
    for (double& v : s) { v = std::exp(v - mx); z += v; }
    for (double& v : s) v /= z;
    return s;
}

}  // namespace hb1

#pragma once
#include <cmath>
#include <vector>
#include "world.hpp"
namespace ares {
// Exact ally-grid subset of maelle-02 State; one consumer, no training state.
struct ExpeditionAllyState {
    std::vector<float> ally;
    int last_rnd = -1;
    void update(const World& w) {
        if (static_cast<int>(ally.size()) != w.NC) ally.assign(w.NC, 0.f);
        if (last_rnd >= 0 && w.rnd > last_rnd) {
            const float f = static_cast<float>(std::pow(0.90, w.rnd - last_rnd));
            for (float& v : ally) v *= f;
        }
        last_rnd = w.rnd;
        for (const Part& q : w.parts) if (q.ally) ally[q.cell] += 1.f;
    }
    double feature(const World& w, int c) const {
        double sum = 0.0;
        const int cx = c % w.W, cy = c / w.W;
        for (int dy = -2; dy <= 2; dy++) {
            const int y = ((cy + dy) % w.H + w.H) % w.H;
            for (int dx = -2; dx <= 2; dx++)
                sum += ally[y * w.W + ((cx + dx) % w.W + w.W) % w.W];
        }
        const double b = sum / 25;
        return b > 0.0 ? b / (b + 0.30) : 0.0;
    }
};
}

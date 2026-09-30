// Maelle (SF-1) — per-dragon decayed state grids, scalars and the feature
// interface read by the policy. Every dragon is its own process, so every grid
// is that dragon's own memory from its own 7x7 view (plus the pearls its
// allies gossip over sonar, which World already folds into pearl_seen).
//
// Grids (one float per cell, x lambda per round, +1 per event):
//   food    a pearl instance becomes known on the cell (first sighting)
//   ally    a visible ally part on the cell, per round
//   enemy   a visible enemy part on the cell, per round
//   threat  the cell is within Chebyshev threat_k of a visible enemy head
//   death   a dragon died here: its id vanished while its last head cell is
//           still in view and one of its last visible cells now holds a pearl
//   seen_age is read from World::seen, not stored.
// Features are read at query time through a (2 * blur + 1)^2 box mean and a
// saturation B / (B + s), so every feature lies in [0, 1].
#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include <fcntl.h>
#include <unistd.h>

#include "params.hpp"
#include "world.hpp"

namespace ares {

struct State {
    int W = 0, H = 0, NC = 0;
    int last_rnd = -1;
    std::vector<float> food, ally, enemy, threat, death;
    std::vector<uint8_t> pearl_known;
    struct Prev { int cell, id; bool head; };
    std::vector<Prev> prev_parts;
    // scalars
    double sparsity = 1.0;  // 1 / (1 + pearls known inside the last search horizon / 2)
    int view_units = 0;     // other dragons' distinct ids in view
    int deaths_seen = 0;

    void init(const World& w) {
        W = w.W; H = w.H; NC = w.NC;
        food.assign(NC, 0.f); ally.assign(NC, 0.f); enemy.assign(NC, 0.f);
        threat.assign(NC, 0.f); death.assign(NC, 0.f);
        pearl_known.assign(NC, 0);
    }

    static void decay(std::vector<float>& g, double lam, int dt) {
        float f = static_cast<float>(std::pow(lam, dt));
        for (float& v : g) v *= f;
    }

    void update(const World& w) {
        if (NC != w.NC) init(w);
        if (last_rnd >= 0 && w.rnd > last_rnd) {
            int dt = w.rnd - last_rnd;
            decay(food, Tun::lam_food, dt); decay(ally, Tun::lam_ally, dt);
            decay(enemy, Tun::lam_enemy, dt); decay(threat, Tun::lam_threat, dt);
            decay(death, Tun::lam_death, dt);
        }
        last_rnd = w.rnd;
        for (int c = 0; c < NC; c++) {
            uint8_t k = w.pearl_seen[c] >= 0 ? 1 : 0;
            if (k && !pearl_known[c]) food[c] += 1.f;
            pearl_known[c] = k;
        }
        // deaths: an id seen last round, gone now, its head cell still in view
        // and a pearl on one of its previously visible cells (the corpse)
        for (size_t i = 0; i < prev_parts.size(); i++) {
            const Prev& p = prev_parts[i];
            if (!p.head || w.cheb(p.cell, w.head) > unswbc::Constants::VISION_RADIUS) continue;
            bool alive = false;
            for (const Part& q : w.parts) if (q.id == p.id) { alive = true; break; }
            if (alive) continue;
            bool corpse = false;
            for (const Prev& r : prev_parts)
                if (r.id == p.id && w.pearl_seen[r.cell] == w.rnd) { corpse = true; break; }
            if (corpse) { death[p.cell] += 1.f; deaths_seen++; }
        }
        prev_parts.clear();
        int ids = 0;
        for (const Part& q : w.parts) {
            (q.ally ? ally : enemy)[q.cell] += 1.f;
            prev_parts.push_back({q.cell, q.id, q.head});
            if (q.head) ids++;
            if (q.head && !q.ally) {
                const int k = Tun::threat_k, hx = q.cell % W, hy = q.cell / W;
                for (int dy = -k; dy <= k; dy++)
                    for (int dx = -k; dx <= k; dx++) {
                        int x = ((hx + dx) % W + W) % W, y = ((hy + dy) % H + H) % H;
                        threat[y * W + x] += 1.f;
                    }
            }
        }
        view_units = ids;
    }

    double box(const std::vector<float>& g, int c) const {
        const int r = Tun::blur, cx = c % W, cy = c / W;
        double s = 0.0;
        for (int dy = -r; dy <= r; dy++) {
            int y = ((cy + dy) % H + H) % H;
            const float* row = g.data() + y * W;
            for (int dx = -r; dx <= r; dx++) s += row[((cx + dx) % W + W) % W];
        }
        return s / ((2 * r + 1) * (2 * r + 1));
    }
    static double sat(double b, double s) { return b > 0.0 ? b / (b + s) : 0.0; }

    double age_f(const World& w, int c) const {
        if (!w.seen[c]) return 1.0;
        return std::min(1.0, (w.rnd - (w.seen[c] - 1)) / 100.0);
    }

    // f(cell) for a target candidate. `unseen_like`: the value comes from a
    // never-seen cell or a bed (not a known pearl).
    void target_features(const World& w, int c, bool unseen_like, double* f) const {
        const double clock = w.rnd / 500.0;
        const double fo = sat(box(food, c), Tun::s_food);
        const double al = sat(box(ally, c), Tun::s_ally);
        const double en = sat(box(enemy, c), Tun::s_enemy);
        f[feat::T_FOOD] = fo;
        f[feat::T_FOOD_UNSEEN] = unseen_like ? fo : 0.0;
        f[feat::T_ALLY] = al;
        f[feat::T_ENEMY] = en;
        f[feat::T_THREAT] = sat(box(threat, c), Tun::s_threat);
        f[feat::T_DEATH] = sat(box(death, c), Tun::s_death);
        f[feat::T_AGE] = age_f(w, c);
        f[feat::T_FOOD_SAT] = fo * al;
        f[feat::T_FOOD_CLOCK] = fo * clock;
        f[feat::T_ALLY_CLOCK] = al * clock;
        f[feat::T_ENEMY_CLOCK] = en * clock;
        f[feat::T_SPARSE] = (!w.seen[c]) ? sparsity : 0.0;
        f[feat::T_FOOD_FREE] = unseen_like ? fo * (1.0 - al) : 0.0;
    }
    double target_factor(const World& w, int c, bool unseen_like) const {
        double f[feat::NT];
        target_features(w, c, unseen_like, f);
        double s = 0.0;
        for (int i = 0; i < feat::NT; i++) s += Tun::wt[i] * f[i];
        return std::exp(s);
    }

    void move_features(const World& w, int c, double* g) const {
        g[feat::M_FOOD] = sat(box(food, c), Tun::s_food);
        g[feat::M_ALLY] = sat(box(ally, c), Tun::s_ally);
        g[feat::M_ENEMY] = sat(box(enemy, c), Tun::s_enemy);
        g[feat::M_THREAT] = sat(box(threat, c), Tun::s_threat);
        g[feat::M_DEATH] = sat(box(death, c), Tun::s_death);
        g[feat::M_AGE] = age_f(w, c);
    }
    double move_term(const World& w, int c) const {
        double g[feat::NM];
        move_features(w, c, g);
        double s = 0.0;
        for (int j = 0; j < feat::NM; j++) s += Tun::wm[j] * g[j];
        return s;
    }
};

// Decision dump (local training data; inert unless MAELLE_DUMP names a file).
// One write() per turn with O_APPEND, so every dragon process of a game can
// share one file. Record: int32 header[12] = {magic 'MLD1', rnd, me, team,
// kind (0 target, 1 move), n rows, chosen row (-1 none), columns, len, units,
// why, target cell}, then n * columns float32.
struct Dump {
    static constexpr int32_t MAGIC = 0x31444c4d;
    int fd = -2;
    std::vector<char> buf;

    bool on() {
        if (fd == -2) {
            const char* p = std::getenv("MAELLE_DUMP");
            fd = p ? ::open(p, O_WRONLY | O_CREAT | O_APPEND, 0644) : -1;
        }
        return fd >= 0;
    }
    void record(const World& w, int kind, int n, int chosen, int cols, char why, int target,
                const std::vector<float>& rows) {
        int32_t h[12] = {MAGIC, w.rnd, w.me, w.team, kind, n, chosen, cols, w.len, w.units, why, target};
        const char* hp = reinterpret_cast<const char*>(h);
        buf.insert(buf.end(), hp, hp + sizeof h);
        const char* rp = reinterpret_cast<const char*>(rows.data());
        buf.insert(buf.end(), rp, rp + rows.size() * sizeof(float));
    }
    void flush() {
        if (fd >= 0 && !buf.empty()) {
            ssize_t r = ::write(fd, buf.data(), buf.size());
            (void)r;
        }
        buf.clear();
    }
};

}  // namespace ares

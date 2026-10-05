// Team-trajectory block, C++ twin of tools/learn/traj.py (TRAJ_VERSION 1). Header-only, C++20; uses learn::Block
// from learn_encode.hpp. Must match the Python bit for bit (tools/learn/test_traj_parity.py + traj_parity_main.cpp).
//   learn::Traj t(spawn);  auto const& v = t.observe(block);   // std::array<int32_t, learn::N_T>, once per own turn
#pragma once
#include <array>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include "learn_encode.hpp"

namespace learn {

constexpr int TRAJ_VERSION = 1;
constexpr int N_T = 7;

class Traj {
public:
    explicit Traj(Spawn const& s) : id_(s.id), team_(s.team), W_(s.W), H_(s.H) {}

    std::array<int32_t, N_T> const& observe(Block const& b) {
        int const rnd = b.round;
        int const hx = b.tiles[24].x, hy = b.tiles[24].y;
        int ev = 0, ec = 0;
        for (auto const& p : b.parts) {
            if (p.id == id_ || p.team == team_) continue;
            ev = 1;
            if (p.head && std::abs(tor(p.x - hx, W_)) + std::abs(tor(p.y - hy, H_)) <= 2) ec = 1;
        }
        if (ev) { has_enemy_ = true; last_enemy_ = rnd; }
        H const* h20 = back(rnd, 20);
        H const* h100 = back(rnd, 100);
        int c20 = ev, k20 = ec, n20 = 1;
        for (auto const& h : hist_) if (h.r > rnd - 20) { c20 += h.ev; k20 += h.ec; n20++; }
        v_[0] = h20 ? b.unit_count - h20->u : BIG;
        v_[1] = h100 ? b.unit_count - h100->u : BIG;
        v_[2] = h20 ? b.length - h20->l : BIG;
        v_[3] = has_enemy_ ? rnd - last_enemy_ : UNSEEN;
        v_[4] = c20; v_[5] = k20; v_[6] = n20;
        hist_.push_back(H{rnd, b.unit_count, b.length, ev, ec});
        while (hist_.size() > 1 && hist_[1].r <= rnd - 100) hist_.pop_front();
        return v_;
    }

private:
    struct H { int r, u, l, ev, ec; };
    static int tor(int d, int n) { d %= n; if (d < 0) d += n; return d > n / 2 ? d - n : d; }
    H const* back(int rnd, int k) const {
        H const* best = nullptr;
        for (auto const& h : hist_) { if (h.r <= rnd - k) best = &h; else break; }
        return best;
    }
    int id_; char team_; int W_, H_;
    std::deque<H> hist_;
    bool has_enemy_ = false; int last_enemy_ = 0;
    std::array<int32_t, N_T> v_{};
};

}  // namespace learn

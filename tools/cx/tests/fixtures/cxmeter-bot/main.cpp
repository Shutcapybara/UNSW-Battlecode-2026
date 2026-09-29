// cxmeter-bot: the unswbc C++ template bot with the CX_METER instrumentation
// protocol that tools/cx/meter.py --mode cxx consumes. Built plainly it plays
// exactly like the template; built with CX_METER defined it additionally
// prints one line per turn to stderr:
//
//     CX_METER parse=<us> sense=<us> policy=<us> bfs=<us>
//
// (integer microseconds). The runner never forwards stderr to the engine or
// the replay, so the timing build is behaviourally the plain build.
#include "helper.hpp"

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <random>
#include <vector>

static long long phase_us(std::chrono::steady_clock::time_point t0,
                          std::chrono::steady_clock::time_point t1) {
    return std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count();
}

// a small fixed BFS over an 64x64 grid: the "BFS" phase placeholder
static long long bfs_cost_us() {
    using clock = std::chrono::steady_clock;
    auto t0 = clock::now();
    std::vector<int> dist(64 * 64, -1);
    std::vector<int> q;
    q.push_back(0);
    dist[0] = 0;
    for (std::size_t head = 0; head < q.size(); ++head) {
        int c = q[head];
        int x = c % 64, y = c / 64;
        for (int d = 0; d < 4; ++d) {
            int nx = x + (d == 0) - (d == 1), ny = y + (d == 2) - (d == 3);
            if (nx < 0 || ny < 0 || nx >= 64 || ny >= 64) continue;
            int n = ny * 64 + nx;
            if (dist[n] < 0) { dist[n] = dist[c] + 1; q.push_back(n); }
        }
    }
    return phase_us(t0, clock::now());
}

int main() {
    auto [ct, game] = unswbc::init();

    std::mt19937 shuffler(0);

    while (unswbc::update(ct, game)) {
        using clock = std::chrono::steady_clock;
#ifdef CX_METER
        auto t_parse = clock::now();      // update() above read and parsed the block
        auto t_sense = t_parse;           // the template senses inside the policy loop
        long long bfs_us = bfs_cost_us();
        auto t_policy = clock::now();
#endif

        auto const here = ct.get_position();
        auto const* hereTile = ct.get_tile(here);
        bool moved = false;

        auto directions = unswbc::Direction::get_direction_list();
        std::shuffle(directions.begin(), directions.end(), shuffler);

        for (auto const direction : directions) {
            if (hereTile && !hereTile->get_edge(direction).is_passable()) {
                continue;
            }
            auto const* ahead = ct.get_tile(here.add_dir(direction));
            if (ahead && ahead->get_dragon()) {
                continue;
            }
            ct.make_move(direction);
            moved = true;
            break;
        }
        if (!moved) {
            ct.make_move(unswbc::Direction::NORTH);
        }

#ifdef CX_METER
        auto t_end = clock::now();
        std::fprintf(stderr, "CX_METER parse=%lld sense=%lld policy=%lld bfs=%lld\n",
                     phase_us(t_parse, t_sense), phase_us(t_sense, t_policy),
                     phase_us(t_policy, t_end), bfs_us);
#endif
        unswbc::end_turn();
    }
}

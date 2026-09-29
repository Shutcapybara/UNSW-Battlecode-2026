// anna-a01-chassis — protocol-3 C++ chassis for the C1 phase.
//
// Turn loop: helper parse -> World::sense (memory) -> Policy::decide -> reply.
// The official helper.hpp is untouched; everything else lives in world.hpp,
// nav.hpp, policy.hpp and params.hpp.
#include <cstdio>
#include <iostream>

#include "helper.hpp"
#include "nav.hpp"
#include "params.hpp"
#include "policy.hpp"
#include "world.hpp"

// Metering hooks (tools/cx/meter.sh builds copies with these set):
// 1 = helper parse only, 2 = parse + World::sense, 3 = full turn + 10 extra
// whole-map BFS (flood-fill cost = (3 - 0) / 10).
#ifndef ANNA_MEASURE
#define ANNA_MEASURE 0
#endif

int main() {
    auto [ct, game] = unswbc::init();
    anna::World w;
    anna::Policy pol;
    w.init(ct, game);

    while (unswbc::update(ct, game)) {
        anna::Decision dec;
        bool ok = true;
        if (ANNA_MEASURE == 1) {
            std::cout << "MOVE " << ct.get_dir().value << "\n";
            unswbc::end_turn();
            continue;
        }
        try {
            w.sense(ct, game);
            if (ANNA_MEASURE == 2) {
                std::cout << "MOVE " << ct.get_dir().value << "\n";
                unswbc::end_turn();
                continue;
            }
            dec = pol.decide(w);
            if (ANNA_MEASURE == 3) {
                static anna::Grid g;
                static std::vector<uint16_t> m;
                anna::build_block_mask(w, m);
                for (int i = 0; i < 10; i++) anna::dist(w, w.head, m, g);
            }
        } catch (...) {
            ok = false;
        }
        if (!ok) {
            // Fallback: first step that is not kelp or an occupied tile.
            auto const here = ct.get_position();
            auto const* tile = ct.get_tile(here);
            unswbc::Direction pick = ct.get_dir();
            for (auto d : unswbc::Direction::get_direction_list()) {
                if (tile && !tile->get_edge(d).is_passable()) continue;
                auto const* ahead = ct.get_tile(here.add_dir(d));
                if (ahead && ahead->get_dragon()) continue;
                pick = d;
                break;
            }
            std::cout << "MOVE " << pick.value << "\nLOG anna_fallback\n";
            unswbc::end_turn();
            continue;
        }
        if (dec.act == anna::Act::SPLIT) {
            ct.do_split(dec.split);
            // activation markers (one short LOG line, ~0.05 M points)
            std::cout << (dec.why == 't' ? "LOG ACT:tsplit\n" : "LOG ACT:split\n");
        } else {
            std::cout << "MOVE ";
            for (int d : dec.dirs) std::cout << anna::dir_char(d);
            std::cout << "\n";
            w.commit_move(dec.dirs);
        }
#ifdef ANNA_DEBUG
        fprintf(stderr, "C r%d act=%c tier=%d why=%c tgt=%d head=%d len=%d atlas=%d off=%d inf=%d\n", w.rnd,
                dec.act == anna::Act::SPLIT ? 'S' : anna::dir_char(dec.dirs.empty() ? 0 : dec.dirs[0]),
                dec.tier, dec.why, dec.target, w.head, w.len, w.atlas, w.body_offset, w.inferred);
#endif
        if (anna::Params::indicator) {
            std::cout << "INDICATOR " << dec.why << dec.tier << " t" << dec.target << "\n";
        }
        unswbc::end_turn();
    }
    return 0;
}

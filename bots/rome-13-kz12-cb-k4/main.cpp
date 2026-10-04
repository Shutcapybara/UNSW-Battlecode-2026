// Ares V06 — C++ implementation on Anna A02 protocol-3 runtime scaffold.
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
#ifndef ARES_MEASURE
#define ARES_MEASURE 0
#endif

int main() {
    auto [ct, game] = unswbc::init();
    ares::World w;
    ares::Policy pol;
    w.init(ct, game);
    // HB-1 Q5: this dragon's v5 feature process (Heartbreaker's view of the turn), fed to the policy.
    hb1::Proc hproc(ct.get_id(), ct.get_team().value, game.width, game.height, game.unit_limit);

    while (unswbc::update(ct, game)) {
        ares::Decision dec;
        char const hb_facing = ct.get_dir().value;
        hb1::Row hb_row;
        pol.hb_row = nullptr;
        try {
            hb_row = hproc.features(hb1::block_from(ct, game));
            pol.hb_row = &hb_row;
        } catch (...) {
        }
        bool ok = true;
        if (ARES_MEASURE == 1) {
            std::cout << "MOVE " << ct.get_dir().value << "\n";
            unswbc::end_turn();
            continue;
        }
        try {
            w.sense(ct, game);
            if (ARES_MEASURE == 2) {
                std::cout << "MOVE " << ct.get_dir().value << "\n";
                unswbc::end_turn();
                continue;
            }
            dec = pol.decide(w);
            pol.prepare_radio_for_decision(w, dec);
            if (ARES_MEASURE == 3) {
                static ares::Grid g;
                static std::vector<uint16_t> m;
                ares::build_block_mask(w, m);
                for (int i = 0; i < 10; i++) ares::dist(w, w.head, m, g);
            }
        } catch (...) {
            ok = false;
        }
        if (!ok) {
            // Match Tyr main.fallback(): first direction whose exact one-step
            // simulation is OK, otherwise keep the current facing.
            int fallback_dir = ares::dir_index(ct.get_dir());
            for (int d = 0; d < 4; d++) {
                if (pol.simulate(w, {d}).status == ares::Policy::SimStatus::OK) {
                    fallback_dir = d;
                    break;
                }
            }
            std::cout << "MOVE " << ares::dir_char(fallback_dir) << "\nLOG ares_fallback\n";
            unswbc::end_turn();
            continue;
        }
        if (dec.act == ares::Act::SPLIT) {
            hproc.record_split(dec.split);
        } else if (!dec.dirs.empty()) {
            std::string rels;
            char f = hb_facing;
            for (int d : dec.dirs) { char a = ares::dir_char(d); rels += hb1::abs_to_rel(f, a); f = a; }
            hproc.record_move(rels);
        }
        if (dec.act == ares::Act::SPLIT) {
            ct.do_split(dec.split);
            // activation markers (one short LOG line, ~0.05 M points)
            std::cout << (dec.why == 't' ? "LOG ACT:tsplit\n" : "LOG ACT:split\n");
        } else {
            std::cout << "MOVE ";
            for (int d : dec.dirs) std::cout << ares::dir_char(d);
            std::cout << "\n";
            w.commit_move(dec.dirs);
        }
        if (dec.kz12_checked)
            std::cout << "LOG KZ12 r=" << w.rnd << " k=" << dec.kz12_dose << " veto=" << dec.kz12_vetoed
                      << " fallback=" << (dec.kz12_fallback ? 1 : 0)
                      << " cap=" << dec.kz12_capacity << "\n";
#ifdef ARES_DEBUG
        fprintf(stderr, "C r%d act=%c why=%c tgt=%d head=%d len=%d off=%d inf=%d\n", w.rnd,
                dec.act == ares::Act::SPLIT ? 'S' : ares::dir_char(dec.dirs.empty() ? 0 : dec.dirs[0]),
                dec.why, dec.target, w.head, w.len);
#endif
        std::cout << "PROTOCOL " << unswbc::Constants::PROTOCOL_MAJOR << "\n";
        if (ares::Params::indicator) {
            std::cout << "INDICATOR " << dec.why << " t" << dec.target << "\n";
        }
        pol.send_radio(ct);
        std::cout << "ENDTURN\n" << std::flush;
    }
    return 0;
}

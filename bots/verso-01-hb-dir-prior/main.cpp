// Verso (X-1) on the Maelle (SF-1) platform on Ares V06 — C++ implementation on the Anna A02 protocol-3
// runtime scaffold.
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

namespace hb1 {
inline std::string edge_token(unswbc::Edge const& e) {
    if (e.get_edge_type() == unswbc::EdgeType::KELP) return "w";
    if (e.get_edge_type() == unswbc::EdgeType::PORTAL) return std::to_string(e.get_portal_id());
    return ".";
}
// The round block exactly as features_view.parse_block sees it (as hb1-12-direction-prior).
inline Block block_from(unswbc::Controller const& ct, unswbc::Game const& game) {
    Block b;
    b.round = game.get_round_num(); b.dir = ct.get_dir().value; b.length = ct.get_length();
    b.units = ct.get_unit_count(); b.n_msgs = int(ct.sonar_messages.size());
    auto const e = ct.get_sonar_echoes();
    b.has_echoes = true;
    b.echoes = {e.kelp, e.ally, e.ally_head, e.enemy, e.enemy_head};
    auto const& tiles = ct.get_tiles();
    for (int k = 0; k < 49; k++) {
        auto const& t = tiles[k];
        b.tiles[k] = {t.position.x, t.position.y, t.has_pearl() ? 1 : 0, t.get_pearl_time()};
        if (auto const* p = t.get_dragon())
            b.bodies.push_back({p->team.value, p->dragon_id, t.position.x, t.position.y, p->dir.value, p->is_head()});
    }
    for (int r = 0; r < 7; r++)
        for (int c = 0; c < 7; c++) {
            b.Hm[r][c] = edge_token(tiles[r * 7 + c].edges[0]);
            b.Vm[r][c] = edge_token(tiles[r * 7 + c].edges[3]);
        }
    for (int c = 0; c < 7; c++) b.Hm[7][c] = edge_token(tiles[6 * 7 + c].edges[2]);
    for (int r = 0; r < 7; r++) b.Vm[r][7] = edge_token(tiles[r * 7 + 6].edges[1]);
    return b;
}
}  // namespace hb1

int main() {
    if (std::getenv("VERSO_SCHEMA")) {  // print the feature schema and exit (tools/verso)
        const verso::Schema& S = verso::Schema::get();
        std::printf("%u\n", S.hash);
        for (auto const& n : S.names) std::printf("%s\n", n.c_str());
        return 0;
    }
    ares::Tun::load_env();
    auto [ct, game] = unswbc::init();
    ares::World w;
    ares::Policy pol;
    w.init(ct, game);
    verso::Cfg::load_env(static_cast<char>(ct.get_team().value));
    pol.vmodel.load();
    // This dragon's v5 feature process (HB-1's actor-local row), only when a head or the dump reads it.
    const bool vx_on = pol.verso_need_x();
    hb1::Proc hproc(ct.get_id(), ct.get_team().value, game.width, game.height, game.unit_limit);

    while (unswbc::update(ct, game)) {
        ares::Decision dec;
        bool ok = true;
        char const hb_facing = ct.get_dir().value;
        hb1::Row hb_row;
        pol.hb_row = nullptr;
        if (vx_on) {
            try {
                hb_row = hproc.features(hb1::block_from(ct, game));
                pol.hb_row = &hb_row;
            } catch (...) {
            }
        }
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
        if (vx_on) {
            if (dec.act == ares::Act::SPLIT) {
                hproc.record_split(dec.split);
            } else if (!dec.dirs.empty()) {
                std::string rels;
                char f = hb_facing;
                for (int d : dec.dirs) { char a = ares::dir_char(d); rels += hb1::abs_to_rel(f, a); f = a; }
                hproc.record_move(rels);
            }
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

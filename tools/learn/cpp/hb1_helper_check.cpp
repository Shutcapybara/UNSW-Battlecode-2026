// Check: hb1_scores' text parser == the bot's helper path (unswbc::update -> hb1::block_from) on one process.
// argv: spawn file, blocks file (blank-line separated), acts file (one "ACT ..." line per turn)
#include <fstream>
#include <iostream>
#include <sstream>
#include <memory>
#include "helper.hpp"
#include "hb1_features.hpp"
#include "hb1_gbt.hpp"
#include "hb1_compact.hpp"
namespace hb1 {
inline std::string edge_token(unswbc::Edge const& e) {
    if (e.get_edge_type() == unswbc::EdgeType::KELP) return "w";
    if (e.get_edge_type() == unswbc::EdgeType::PORTAL) return std::to_string(e.get_portal_id());
    return ".";
}
inline Block block_from(unswbc::Controller const& ct, unswbc::Game const& game) {   // verbatim from carthage-05 policy.hpp
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
}
int main(int argc, char** argv) {
    std::ifstream sp(argv[1]), bl(argv[2]), ac(argv[3]);
    std::stringstream input; input << sp.rdbuf() << bl.rdbuf() << "ENDGAME\n";
    std::cin.rdbuf(input.rdbuf());
    auto [ct, game] = unswbc::init();
    hb1::Proc proc(ct.get_id(), ct.get_team().value, game.width, game.height, game.unit_limit);
    static hb1::Bound const bound{hb1::dirc_bind};
    std::string line;
    while (unswbc::update(ct, game)) {
        auto p = hb1::dirc_proba(bound.vec(proc.features(hb1::block_from(ct, game))));
        std::printf("%.6f %.6f %.6f\n", p[0], p[1], p[2]);
        if (std::getline(ac, line)) { std::istringstream a(line.substr(4)); std::string k, v; a >> k >> v;
            if (k == "m" && !v.empty()) proc.record_move(v); else if (k == "s") proc.record_split(std::stoi(v)); }
    }
}

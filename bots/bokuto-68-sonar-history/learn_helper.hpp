// Adapter: the official C++ helper's parsed turn (unswbc::Controller / Game) -> learn::Block, so a bot can run the
// Phase 3 encoder on exactly what it was sent. Validated by helper_parity_main.cpp (helper path == text path).
#pragma once
#include "helper.hpp"
#include "learn_encode.hpp"

namespace learn {
inline char edge_of(unswbc::Edge const& e) {
    auto t = e.get_edge_type();
    return t == unswbc::EdgeType::KELP ? 'w' : t == unswbc::EdgeType::PORTAL ? 'p' : '.';
}
inline Spawn spawn_from(unswbc::Controller const& ct, unswbc::Game const& game) {
    return Spawn{ct.get_id(), ct.get_team().value, game.width, game.height, game.unit_limit};
}
inline Block block_from(unswbc::Controller const& ct, unswbc::Game const& game) {
    Block b;
    b.round = game.get_round_num(); b.dir = ct.get_dir().value; b.length = ct.get_length();
    b.unit_count = ct.get_unit_count();
    b.msgs.assign(ct.sonar_messages.begin(), ct.sonar_messages.end());
    auto const e = ct.get_sonar_echoes();
    b.has_echoes = true;   // absent line == five zeros for the encoder (echo_present is computed from turn/birth)
    b.echoes = {e.kelp, e.ally, e.ally_head, e.enemy, e.enemy_head};
    auto const& tiles = ct.get_tiles();
    for (int k = 0; k < 49; k++) {
        auto const& t = tiles[k];
        b.tiles[k] = {t.position.x, t.position.y, t.has_pearl() ? 1 : 0, t.get_pearl_time()};
        if (auto const* p = t.get_dragon())
            b.parts.push_back({p->team.value, p->dragon_id, t.position.x, t.position.y, p->dir.value, p->is_head() ? 1 : 0});
    }
    for (int r = 0; r < 7; r++)
        for (int c = 0; c < 7; c++) { b.hedge[r][c] = edge_of(tiles[r * 7 + c].edges[0]); b.vedge[r][c] = edge_of(tiles[r * 7 + c].edges[3]); }
    for (int c = 0; c < 7; c++) b.hedge[7][c] = edge_of(tiles[6 * 7 + c].edges[2]);
    for (int r = 0; r < 7; r++) b.vedge[r][7] = edge_of(tiles[r * 7 + 6].edges[1]);
    return b;
}
}  // namespace learn

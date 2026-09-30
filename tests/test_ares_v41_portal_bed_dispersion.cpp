#include <cassert>

#include "../bots/ares-v41-portal-bed-dispersion/policy.hpp"

namespace {

void add_ally(ares::World& w, int id, int cell) {
    const int index = static_cast<int>(w.parts.size());
    w.parts.push_back({cell, id, true, true, 0, 99});
    w.ally_heads.push_back(index);
    w.occ[cell] = index;
}

ares::World make_world(bool ally_covering_bed, bool recent_portal_exit = false) {
    ares::World w;
    w.W = 32;
    w.H = 16;
    w.NC = w.W * w.H;
    w.me = 25;
    w.team = 'A';
    w.limit = 64;
    w.rnd = 15;
    w.len = 3;
    w.units = 8;
    w.face = 0;
    w.head = 4 * w.W + 14;
    w.born = 10;
    w.last_exit_round = recent_portal_exit ? 14 : -1;

    w.ek.assign(2 * w.NC, ares::EK_OPEN);
    w.epid.assign(2 * w.NC, -1);
    const int bed = 15 * w.W + 5;
    const int exit_edge = w.head;
    const int pair_edge = 5;  // north edge at (5, 0) lands on (5, 15)
    w.ek[exit_edge] = w.ek[pair_edge] = ares::EK_PORTAL;
    w.epid[exit_edge] = w.epid[pair_edge] = 1;
    w.pends[1] = {exit_edge, pair_edge};
    if (recent_portal_exit) {
        w.last_exit_portal = pair_edge;
        w.last_exit_cell = w.head + 1;
    }
    w.dest_tab.assign(4 * w.NC, ares::UNKNOWN);
    w.dest_dirty = true;
    w.rebuild_dest();

    w.seen.assign(w.NC, 1);
    w.bed.assign(w.NC, -1);
    w.spawn_at.assign(w.NC, -1);
    w.pearl_seen.assign(w.NC, -1);
    w.body_seen.assign(w.NC, -1000);
    w.seen_count = w.NC;
    w.sectors_w = 4;
    w.sectors_h = 2;
    w.sector_unseen.assign(8, 0);
    const int explore = 4 * w.W + 13;
    w.seen[explore] = 0;
    w.seen_count--;
    w.sector_unseen[1] = 1;

    w.occ.assign(w.NC, -1);
    w.own.assign(w.NC, 0);
    w.body = {2 * w.W + 14, 3 * w.W + 14, w.head};
    w.trail = w.body;
    for (int i = 0; i < static_cast<int>(w.body.size()); i++) {
        w.own[w.body[i]] = static_cast<uint8_t>(i + 1);
        w.own_cells.push_back(w.body[i]);
    }

    w.bed[bed] = 1;
    w.spawn_at[bed] = w.rnd + 1;
    if (ally_covering_bed)
        add_ally(w, 26, bed + 1);
    return w;
}

int choose_target(bool ally_covering_bed, char& why, bool recent_portal_exit = false,
                  int* first_dir = nullptr) {
    auto w = make_world(ally_covering_bed, recent_portal_exit);
    ares::Policy policy;
    const auto action = policy.decide(w);
    assert(action.act == ares::Act::MOVE);
    if (first_dir && !action.dirs.empty()) *first_dir = action.dirs.front();
    why = action.why;
    return action.target;
}

}  // namespace

int main() {
    char why = '-';

    // Without another dragon nearby, the ripe bed beats the unseen cell.
    const int uncovered_target = choose_target(false, why);
    assert(uncovered_target == 15 * 32 + 5);
    assert(why == 'b');

    // The bed is two Manhattan tiles away but one portal step away. Its
    // covering ally is one Manhattan step away and has a higher ID. V40's
    // strict distance/tie test would not yield here; V41 should explore.
    assert(choose_target(true, why) == 4 * 32 + 13);
    assert(why == 'x');

    // Even without a nearby ally, a dragon that has just exited this portal
    // pair should explore instead of doubling back through it for a bed.
    auto recent_exit = make_world(false, true);
    ares::Policy policy;
    assert(policy.recent_portal_return(recent_exit, 0));
    assert(!policy.recent_portal_return(recent_exit, 1));
    int first_dir = -1;
    assert(choose_target(false, why, true, &first_dir) == 4 * 32 + 13);
    assert(why == 'x');
    assert(first_dir != 0);
}

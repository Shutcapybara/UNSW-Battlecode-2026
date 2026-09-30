#include <cassert>
#include <vector>

#include "../bots/ares-v40-length-priced-sprints/policy.hpp"

namespace {

enum class Goal { explore, pearl, bed };

void add_enemy(ares::World& w, int id, int x, int y, int length) {
    const int cell = y * w.W + x;
    const int index = static_cast<int>(w.parts.size());
    w.parts.push_back({cell, id, false, true, 0, 99});
    w.enemy_heads.push_back(index);
    w.occ[cell] = index;
    ares::DragonMem memory;
    memory.id = id;
    memory.ally = false;
    memory.cell = cell;
    memory.last_round = w.rnd;
    memory.first_round = 0;
    memory.vis_len = length;
    w.mem[id] = memory;
}

ares::World make_world(Goal goal, bool dense_threats = false, bool add_nearby_enemies = true) {
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
    w.born = 15;

    w.ek.assign(2 * w.NC, ares::EK_OPEN);
    w.epid.assign(2 * w.NC, -1);
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
    if (goal == Goal::explore) {
        const int target = 4 * w.W + 18;
        w.seen[target] = 0;
        w.seen_count--;
        w.sector_unseen[2] = 1;
    }

    w.occ.assign(w.NC, -1);
    w.own.assign(w.NC, 0);
    w.body = {2 * w.W + 14, 3 * w.W + 14, 4 * w.W + 14};
    w.trail = w.body;
    for (int i = 0; i < static_cast<int>(w.body.size()); i++) {
        w.own[w.body[i]] = static_cast<uint8_t>(i + 1);
        w.own_cells.push_back(w.body[i]);
    }

    if (add_nearby_enemies) {
        // The three enemy heads visible near the short dragon in match 686866.
        add_enemy(w, 7, 13, 2, 2);
        add_enemy(w, 9, 17, 4, 3);
        add_enemy(w, 23, 16, 2, 2);
        if (dense_threats) {
            add_enemy(w, 11, 17, 5, 2);
            add_enemy(w, 21, 18, 6, 2);
        }
    }

    const int dash_end = 3 * w.W + 15;
    if (goal == Goal::pearl) w.pearl_seen[dash_end] = w.rnd;
    if (goal == Goal::bed) {
        w.bed[dash_end] = 1;
        w.spawn_at[dash_end] = w.rnd;
    }
    return w;
}

std::vector<int> decide(Goal goal, int& target, char& why, bool dense_threats = false,
                        bool add_nearby_enemies = true) {
    auto w = make_world(goal, dense_threats, add_nearby_enemies);
    ares::Policy policy;
    const auto action = policy.decide(w);
    assert(action.act == ares::Act::MOVE);
    target = action.target;
    why = action.why;
    return action.dirs;
}

}  // namespace

int main() {
    int target = -1;
    char why = '-';

    // Nearby enemies alone should not cause a sprint when there is no pearl
    // or selected objective at the second-step endpoint.
    auto explore = decide(Goal::explore, target, why);
    assert((explore == std::vector<int>{2}));
    assert(target == 4 * 32 + 18);
    assert(why == 'x');

    // Taking a pearl on a dash does not increase current length. If nobody is
    // close enough to contest it, the future-growth opportunity cost keeps us
    // from consuming it early.
    auto unopposed_pearl = decide(Goal::pearl, target, why, false, false);
    assert((unopposed_pearl == std::vector<int>{1}));
    assert(target == 3 * 32 + 15);
    assert(why == 'p');

    // When a nearby enemy could reach that pearl, the dash earns denial value.
    auto contested_pearl = decide(Goal::pearl, target, why);
    assert((contested_pearl == std::vector<int>{1, 0}));
    assert(target == 3 * 32 + 15);
    assert(why == 'p');
}

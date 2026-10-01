// HB-1 structured mimic of Heartbreaker (team 62): the Q2 wrapper as rules around the exported models.
//   W0  a split needs length >= 4, units < limit and child in [2, length-2]
//   W1  no ordinary exit, no portal, split-eligible  -> split
//   W2  no ordinary exit, no portal, not eligible     -> ally head F>R>L, else forward
//   W3  portal only, not eligible                     -> a portal step
//   W4  otherwise moves only onto free / portal / enemy-head cells
// Policy parts: split admission (gate GBT), child size (alloc GBT), direction (direction GBT, masked by the wrapper),
// sonar ray pattern (sonar GBT; rays N,E,S,W with payload 0, a dropped slot redrawn from the other three).
#pragma once
#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>
#include "helper.hpp"
#include "hb1_features.hpp"
#include "hb1_gbt.hpp"

namespace hb1 {

inline std::string edge_token(unswbc::Edge const& e) {
    if (e.get_edge_type() == unswbc::EdgeType::KELP) return "w";
    if (e.get_edge_type() == unswbc::EdgeType::PORTAL) return std::to_string(e.get_portal_id());
    return ".";
}

// The round block exactly as features_view.parse_block sees it, rebuilt from the helper's parse.
inline Block block_from(unswbc::Controller const& ct, unswbc::Game const& game) {
    Block b;
    b.round = game.get_round_num();
    b.dir = ct.get_dir().value;
    b.length = ct.get_length();
    b.units = ct.get_unit_count();
    b.n_msgs = int(ct.sonar_messages.size());
    auto const e = ct.get_sonar_echoes();
    b.has_echoes = true;                     // absent ECHOES parse as zeros, as in the Python (echoes or [0]*5)
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

struct Choice {
    bool split = false;
    int child = 0;
    char rel = 'F';      // relative first step when moving
    char why = '?';      // w1 / w2 / w3 / g(ate) / d(irection)
};

class Mimic {
  public:
    Proc proc;
    Bound gate{gate_model}, alloc{alloc_model}, dir{direction_model}, sonar{sonar_model};
    std::uint64_t seed;
    bool sample_direction = false;

    Mimic(unswbc::Controller const& ct, unswbc::Game const& game)
        : proc(ct.get_id(), ct.get_team().value, game.width, game.height, game.unit_limit),
          seed(0x9E3779B97F4A7C15ull ^ std::uint64_t(ct.get_id()) * 0xBF58476D1CE4E5B9ull) {}

    static bool move_ok(Row const& r, char rel) {
        std::string P = std::string("c") + rel + "_";
        double blk = r.get(P + "block");
        return blk == 0 || (blk == -1 && r.get(P + "portal") == 1) || blk == 7;
    }

    // Most probable child-size class that is legal (W0: child <= length - 2); class 8 stands for ">= 8".
    int child_size(Row const& r, int L) {
        auto p = proba(alloc_model, alloc.vec(r));
        int best = 2;
        double bp = -1;
        for (int i = 0; i < alloc_model.n_class; i++) {
            int k = alloc_model.classes[i];
            if (k <= L - 2 && p[i] > bp) { bp = p[i]; best = k; }
        }
        return best;
    }

    Choice decide(Row const& r) {
        Choice c;
        int const L = int(r.get("length"));
        bool const elig = r.get("split_elig") == 1;
        bool const exitless = r.get("n_exit_ord") == 0 && r.get("n_exit_portal") == 0;
        if (exitless && elig) {                                           // W1
            c.split = true; c.child = child_size(r, L); c.why = '1';
            return c;
        }
        if (exitless) {                                                   // W2
            c.rel = 'F'; c.why = '2';
            for (char rel : {'L', 'R', 'F'})
                if (r.get(std::string("c") + rel + "_block") == 5) c.rel = rel;
            return c;
        }
        if (elig) {                                                       // policy: split admission
            auto p = proba(gate_model, gate.vec(r));
            if (p[1] >= 0.5) { c.split = true; c.child = child_size(r, L); c.why = 'g'; return c; }
        }
        auto p = proba(direction_model, dir.vec(r));                      // policy: direction, masked by W3/W4
        static constexpr char RELS[3] = {'F', 'R', 'L'};
        double bp = -1;
        c.rel = 'F';
        if (sample_direction) {
            // hb1-02: sample the direction from the model's probabilities over the wrapper-allowed moves
            double z = 0;
            for (int i = 0; i < 3; i++) z += move_ok(r, RELS[direction_model.classes[i]]) ? p[i] : 0;
            if (z > 0) {
                seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17;
                double u = double(seed >> 11) * 0x1.0p-53 * z;
                for (int i = 0; i < 3; i++) {
                    char rel = RELS[direction_model.classes[i]];
                    if (!move_ok(r, rel)) continue;
                    c.rel = rel;
                    if ((u -= p[i]) < 0) break;
                }
                c.why = r.get("n_exit_ord") == 0 ? '3' : 'd';
                return c;
            }
        }
        for (int i = 0; i < 3; i++) {
            char rel = RELS[direction_model.classes[i]];
            if (move_ok(r, rel) && p[i] > bp) { bp = p[i]; c.rel = rel; }
        }
        c.why = r.get("n_exit_ord") == 0 ? '3' : 'd';
        return c;
    }

    // Four rays N,E,S,W (payload 0); the sonar model's mask (relative to the pre-move facing) says which
    // direction is dropped, and that slot is redrawn from the other three.
    std::vector<char> sonar_dirs(Row const& r, Choice const& c, char facing) {
        Row s = r;
        s.set("act_F", !c.split && c.rel == 'F'); s.set("act_R", !c.split && c.rel == 'R');
        s.set("act_L", !c.split && c.rel == 'L'); s.set("act_split", c.split);
        auto p = proba(sonar_model, sonar.vec(s));
        int best = 0;
        for (int i = 1; i < sonar_model.n_class; i++) if (p[i] > p[best]) best = i;
        int mask = sonar_model.classes[best];
        std::vector<char> rays = {'N', 'E', 'S', 'W'};
        static constexpr char RB[4] = {'F', 'R', 'B', 'L'};
        for (int bit = 0; bit < 4; bit++) {
            if (mask & (1 << bit)) continue;
            char drop = rel_to_abs(facing, RB[bit]);
            seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17;
            std::vector<char> other;
            for (char d : rays) if (d != drop && std::find(other.begin(), other.end(), d) == other.end()) other.push_back(d);
            for (char& d : rays) if (d == drop) { d = other[seed % other.size()]; break; }
        }
        return rays;
    }
};

}  // namespace hb1

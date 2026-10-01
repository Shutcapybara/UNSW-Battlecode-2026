// anna chassis — WORLD MODEL.
//
// Persistent memory for one dragon (each dragon is its own process), refreshed
// from the helper's Controller every turn in O(visible tiles) plus O(changed
// cells). Cells are ints c = y * W + x. Directions 0..3 = N E S W.
//
// Edge keys: k = c is the north edge of cell c; k = NC + c is the west edge.
// Edge kinds: 0 unknown, 1 open, 2 kelp, 3 portal. A portal edge carries an id
// shared with exactly one other edge; crossing one side comes out of the other
// with the same heading (formula shared with yuna/ouroboros world.py).
//
// dest(c, d) is the engine's step: >= 0 the landing cell, BLOCKED (kelp),
// UNKNOWN (edge never seen), UNPAIRED (portal whose partner we have not seen).
#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <unordered_map>
#include <vector>

#include "atlas.hpp"
#include "helper.hpp"
#include "params.hpp"

namespace ares {

constexpr int BLOCKED = -1;
constexpr int UNKNOWN = -2;
constexpr int UNPAIRED = -3;

enum : uint8_t { EK_UNK = 0, EK_OPEN = 1, EK_KELP = 2, EK_PORTAL = 3 };

inline int dir_index(unswbc::Direction d) {
    switch (d.value) {
    case unswbc::Direction::NORTH: return 0;
    case unswbc::Direction::EAST: return 1;
    case unswbc::Direction::SOUTH: return 2;
    default: return 3;
    }
}
inline char dir_char(int d) { return "NESW"[d & 3]; }
inline int opposite(int d) { return (d + 2) & 3; }

// What we remember about another dragon across turns.
struct DragonMem {
    int id = -1;
    bool ally = false;
    int cell = -1;        // last head cell seen (-1 if only body seen)
    int facing = 0;       // last head facing
    int last_round = -1;  // last round any part was seen
    int first_round = -1; // first round any part was seen
    int vis_len = 0;      // segments visible the last time it was seen
    bool cut = false;      // visible chain runs off the vision rim
};

// A dragon part seen this turn (other dragons only).
struct Part {
    int cell;
    int id;
    bool ally;
    bool head;
    int dir;
    int vac = Params::other_block_t;  // free for arrival depth >= vac
};

struct World {
    // ---- constants of the game
    int W = 0, H = 0, NC = 0;
    int me = -1;
    char team = 'A';
    int limit = 64;

    // ---- this turn
    int rnd = 0, len = 3, units = 1, face = 0, head = -1;
    int born = -1;  // first round this process played
    bool is_queen = false;  // H-Q1: team's original lowest-id dragon (A=0, B=1; no succession)
    unswbc::SonarEchoes echoes{};
    std::vector<uint64_t> msgs;

    // ---- terrain memory
    std::vector<uint8_t> ek;       // 2*NC edge kinds
    std::vector<int> epid;         // 2*NC portal id (-1)
    std::unordered_map<int, std::array<int, 2>> pends;  // portal id -> edge keys (-1 empty)
    std::vector<int> portal_order; // preserve Python dict insertion order
    std::vector<int> dest_tab;     // 4*NC cached dest
    bool dest_dirty = true;
    std::vector<int> seen;         // per cell: last round seen + 1 (0 never)
    int seen_count = 0;            // cells ever seen
    static constexpr int sector_size = 8;
    int sectors_w = 0, sectors_h = 0;
    std::vector<int> sector_unseen;
    std::vector<int> visible_cells; // this turn in Python observation order
    std::vector<int> body_seen;     // latest round each other body cell was visible
    std::vector<int8_t> bed;       // 0 unknown, 1 bed, -1 not a bed
    std::vector<int> spawn_at;     // bed: round the next pearl appears (last countdown seen)
    std::vector<int> pearl_seen;   // round a pearl was last seen there, -1 none
    std::vector<int> pearl_order;  // Python dict insertion order for far_target ties

    // ---- dragons this turn
    std::vector<Part> parts;       // other dragons' visible parts
    std::vector<int> occ;          // per cell: index into parts, -1 free
    std::vector<int> occ_cells;    // cells set in occ (for O(changed) reset)
    std::vector<int> enemy_heads;  // indices into parts
    std::vector<int> ally_heads;
    std::unordered_map<int, DragonMem> mem;  // per other dragon id

    // ---- own body
    std::vector<int> trail;        // own head cells, oldest first
    std::vector<int> body;         // tail .. head
    std::vector<uint8_t> own;      // per cell: 1 + index in body (0 = not ours)
    std::vector<int> own_cells;
    int last_exit_portal = -1;     // edge key of the last portal we crossed
    int last_exit_round = -1;
    int last_move = -1;            // direction we moved last turn (-1 none)
    // Tyr keeps partial visible body history when its trail becomes inconsistent.

    // ---- atlas (terrain of the public maps, matched on the first view)
    int atlas = -1;                // index into atlas::maps, -1 none
    std::vector<uint8_t> atlas_bed;  // per cell: 0 none, else bed class (log2 mean gap + 1)

    // ------------------------------------------------------------ geometry
    int nbr(int c, int d) const {
        int x = c % W;
        switch (d) {
        case 0: return c >= W ? c - W : c - W + NC;
        case 1: return x + 1 < W ? c + 1 : c + 1 - W;
        case 2: return c < NC - W ? c + W : c + W - NC;
        default: return x ? c - 1 : c - 1 + W;
        }
    }
    int ekey(int c, int d) const {
        switch (d) {
        case 0: return c;
        case 1: return NC + nbr(c, 1);
        case 2: return nbr(c, 2);
        default: return NC + c;
        }
    }
    int dest_raw(int c, int d) const {
        int k = ekey(c, d);
        switch (ek[k]) {
        case EK_OPEN: return nbr(c, d);
        case EK_UNK: return UNKNOWN;
        case EK_KELP: return BLOCKED;
        default: break;
        }
        auto it = pends.find(epid[k]);
        if (it == pends.end() || it->second[1] < 0) return UNPAIRED;
        int pk = it->second[0] == k ? it->second[1] : it->second[0];
        if (pk >= NC) {
            int pc = pk - NC;
            return d == 1 ? pc : nbr(pc, 3);
        }
        return d == 2 ? pk : nbr(pk, 0);
    }
    void rebuild_dest() {
        int* out = dest_tab.data();
        for (int y = 0, c = 0; y < H; y++)
            for (int x = 0; x < W; x++, c++, out += 4) {
                const int nb[4] = {y ? c - W : c - W + NC, x + 1 < W ? c + 1 : c + 1 - W,
                                   y + 1 < H ? c + W : c + W - NC, x ? c - 1 : c - 1 + W};
                const int keys[4] = {c, NC + nb[1], nb[2], NC + c};
                for (int d = 0; d < 4; d++) {
                    switch (ek[keys[d]]) {
                    case EK_OPEN: out[d] = nb[d]; break;
                    case EK_UNK: out[d] = UNKNOWN; break;
                    case EK_KELP: out[d] = BLOCKED; break;
                    default: out[d] = dest_raw(c, d); break;
                    }
                }
            }
        dest_dirty = false;
    }
    // Engine step (see header). Valid after sense().
    int dest(int c, int d) const { return dest_tab[c * 4 + d]; }
    // Planning step: unknown edges optimistic (torus neighbour).
    int step_opt(int c, int d) const {
        int n = dest_tab[c * 4 + d];
        return n == UNKNOWN ? nbr(c, d) : n;
    }
    int tdist(int a, int b) const {
        int dx = std::abs(a % W - b % W), dy = std::abs(a / W - b / W);
        if (dx * 2 > W) dx = W - dx;
        if (dy * 2 > H) dy = H - dy;
        return dx + dy;
    }
    int cheb(int a, int b) const {
        int dx = std::abs(a % W - b % W), dy = std::abs(a / W - b / W);
        if (dx * 2 > W) dx = W - dx;
        if (dy * 2 > H) dy = H - dy;
        return dx > dy ? dx : dy;
    }
    bool in_vision(int c) const { return cheb(c, head) <= unswbc::Constants::VISION_RADIUS; }
    bool is_portal_edge(int c, int d) const { return ek[ekey(c, d)] == EK_PORTAL; }
    void learn_pair(int k1, int k2, int pid) {
        if (k1 < 0 || k2 < 0 || k1 >= 2 * NC || k2 >= 2 * NC || k1 == k2) return;
        for (int k : {k1, k2}) {
            if (ek[k] != EK_PORTAL) {
                ek[k] = EK_PORTAL;
                epid[k] = pid;
                dest_dirty = true;
            }
        }
        auto it = pends.find(pid);
        if (it == pends.end()) {
            pends.emplace(pid, std::array<int, 2>{k1, k2});
            portal_order.push_back(pid);
            dest_dirty = true;
        } else if (it->second[1] < 0) {
            it->second = {k1, k2};
            dest_dirty = true;
        }
    }
    int own_index(int c) const { return own[c] ? own[c] - 1 : -1; }  // 0 = tail
    const Part* part_at(int c) const { return occ[c] >= 0 ? &parts[occ[c]] : nullptr; }
    bool pearl_known(int c, int ttl) const { return pearl_seen[c] >= 0 && rnd - pearl_seen[c] <= ttl; }

    // ------------------------------------------------------------- lifecycle
    void init(const unswbc::Controller& ct, const unswbc::Game& g) {
        W = g.width;
        H = g.height;
        NC = W * H;
        me = ct.get_id();
        team = static_cast<char>(ct.get_team().value);
        // engine ids interleave by team parity from r0 (verified on 1.2.3 replays):
        // the team's lowest id -- the tiebreak queen -- is 0 for A, 1 for B.
        is_queen = (me == (team == 'A' ? 0 : 1));
        limit = g.unit_limit;
        ek.assign(2 * NC, EK_UNK);
        epid.assign(2 * NC, -1);
        dest_tab.assign(4 * NC, UNKNOWN);
        seen.assign(NC, 0);
        bed.assign(NC, 0);
        spawn_at.assign(NC, -1);
        pearl_seen.assign(NC, -1);
        body_seen.assign(NC, -1000);
        sectors_w = (W + sector_size - 1) / sector_size;
        sectors_h = (H + sector_size - 1) / sector_size;
        sector_unseen.assign(sectors_w * sectors_h, 0);
        for (int sy = 0; sy < sectors_h; sy++) for (int sx = 0; sx < sectors_w; sx++)
            sector_unseen[sy * sectors_w + sx] =
                std::min(sector_size, H - sy * sector_size) * std::min(sector_size, W - sx * sector_size);
        occ.assign(NC, -1);
        own.assign(NC, 0);
        trail.reserve(1024);
    }

    void learn_edge(int k, const unswbc::Edge& e) {
        uint8_t kind = e.is_portal() ? EK_PORTAL : (e.is_passable() ? EK_OPEN : EK_KELP);
        if (kind == EK_PORTAL) {
            int pid = e.get_portal_id();
            if (ek[k] != EK_PORTAL || epid[k] != pid) {
                ek[k] = EK_PORTAL;
                epid[k] = pid;
                dest_dirty = true;
            }
            auto it = pends.find(pid);
            if (it == pends.end()) {
                pends.emplace(pid, std::array<int, 2>{k, -1});
                portal_order.push_back(pid);
                dest_dirty = true;
            } else if (it->second[0] != k && it->second[1] < 0) {
                it->second[1] = k;
                dest_dirty = true;
            }
            return;
        }
        if (ek[k] != kind) {
            ek[k] = kind;
            dest_dirty = true;
        }
    }

    static uint8_t atlas_kind(char ch) { return ch == 'w' ? EK_KELP : ch == 'p' ? EK_PORTAL : EK_OPEN; }

    // Load the public map whose terrain agrees with every edge of this view
    // (unique match only). Edge kinds and portal ids must both agree.
    void atlas_try(const unswbc::Controller& ct) {
        int hit = -1;
        for (int m = 0; m < atlas::n_maps; m++) {
            const atlas::Map& A = atlas::maps[m];
            if (A.W != W || A.H != H) continue;
            bool ok = true;
            for (auto const& t : ct.get_tiles()) {
                int c = t.position.y * W + t.position.x;
                const int keys[4] = {c, NC + nbr(c, 1), nbr(c, 2), NC + c};
                for (int d = 0; d < 4 && ok; d++) {
                    auto const& e = t.get_edge(unswbc::Direction::get_direction_list()[d]);
                    uint8_t want = e.is_portal() ? EK_PORTAL : (e.is_passable() ? EK_OPEN : EK_KELP);
                    if (atlas_kind(A.edges[keys[d]]) != want) ok = false;
                    else if (want == EK_PORTAL) {
                        int pid = -2;
                        for (int i = 0; i < A.n_portals; i++)
                            if (A.portals[2 * i] == keys[d]) pid = A.portals[2 * i + 1];
                        if (pid != e.get_portal_id()) ok = false;
                    }
                }
                if (!ok) break;
            }
            if (ok) {
                if (hit >= 0) return;  // ambiguous
                hit = m;
            }
        }
        if (hit < 0) return;
        const atlas::Map& A = atlas::maps[hit];
        atlas = hit;
        for (int k = 0; k < 2 * NC; k++) ek[k] = atlas_kind(A.edges[k]);
        for (int i = 0; i < A.n_portals; i++) {
            int k = A.portals[2 * i], pid = A.portals[2 * i + 1];
            epid[k] = pid;
            auto it = pends.find(pid);
            if (it == pends.end()) pends.emplace(pid, std::array<int, 2>{k, -1});
            else if (it->second[0] != k && it->second[1] < 0) it->second[1] = k;
        }
        atlas_bed.assign(NC, 0);
        for (int c = 0; c < NC; c++) {
            atlas_bed[c] = static_cast<uint8_t>(A.beds[c] - '0');
            bed[c] = atlas_bed[c] ? 1 : -1;
        }
        dest_dirty = true;
    }

    // Observation -> memory. Call once per turn before anything else.
    void sense(const unswbc::Controller& ct, const unswbc::Game& g) {
        rnd = g.round_num;
        len = ct.get_length();
        units = ct.get_unit_count();
        face = dir_index(ct.get_dir());
        echoes = ct.sonar_echoes;
        msgs = ct.sonar_messages;
        auto hp = ct.get_position();
        head = hp.y * W + hp.x;
        if (born < 0) {
            born = rnd;  // Match Tyr: use only terrain actually observed or shared by sonar.
        }

        // tiles: pearls, beds, edge-independent observations
        visible_cells.clear();
        for (auto const& t : ct.get_tiles()) {
            int c = t.position.y * W + t.position.x;
            visible_cells.push_back(c);
            if (!seen[c]) {
                seen_count++;
                int sx = (c % W) / sector_size, sy = (c / W) / sector_size;
                sector_unseen[sy * sectors_w + sx]--;
            }
            seen[c] = rnd + 1;
            if (t.has_pearl()) {
                if (pearl_seen[c] < 0) pearl_order.push_back(c);
                pearl_seen[c] = rnd;
            } else {
                if (pearl_seen[c] >= 0) {
                    auto it = std::find(pearl_order.begin(), pearl_order.end(), c);
                    if (it != pearl_order.end()) pearl_order.erase(it);
                }
                pearl_seen[c] = -1;
            }
            int cd = t.get_pearl_time();
            if (cd >= 0) {
                bed[c] = 1;
                spawn_at[c] = rnd + cd;
            } else {
                bed[c] = -1;
            }
        }
        // Tyr world.py consumes the complete horizontal edge grid, then the
        // complete vertical grid. Preserve that ordering for portal memory.
        auto wrap = [](int v, int n) { return (v % n + n) % n; };
        const int hx = head % W, hy = head / W;
        for (int r = 0; r < 8; r++) {
            int edge_y = wrap(hy - 3 + r, H);
            int tile_y = wrap(hy - 3 + std::min(r, 6), H);
            for (int col = 0; col < 7; col++) {
                int x = wrap(hx - 3 + col, W);
                auto const* tile = ct.get_tile(unswbc::Position(x, tile_y));
                if (tile) learn_edge(edge_y * W + x, tile->get_edge(
                    r < 7 ? unswbc::Direction::NORTH : unswbc::Direction::SOUTH));
            }
        }
        for (int r = 0; r < 7; r++) {
            int y = wrap(hy - 3 + r, H);
            for (int col = 0; col < 8; col++) {
                int edge_x = wrap(hx - 3 + col, W);
                int tile_x = wrap(hx - 3 + std::min(col, 6), W);
                auto const* tile = ct.get_tile(unswbc::Position(tile_x, y));
                if (tile) learn_edge(NC + y * W + edge_x, tile->get_edge(
                    col < 7 ? unswbc::Direction::WEST : unswbc::Direction::EAST));
            }
        }
        if (dest_dirty) rebuild_dest();

        // dragons
        for (int c : occ_cells) occ[c] = -1;
        occ_cells.clear();
        parts.clear();
        enemy_heads.clear();
        ally_heads.clear();
        own_seen_.clear();
        for (auto const& t : ct.get_tiles()) {
            auto const* dp = t.get_dragon();
            if (!dp) continue;
            int c = t.position.y * W + t.position.x;
            int did = dp->get_id();
            if (did == me) {
                if (!dp->is_head()) own_seen_.push_back({c, dir_index(dp->get_dir())});
                continue;
            }
            bool ally = dp->get_team() == ct.get_team();
            body_seen[c] = rnd;
            Part p{c, did, ally, dp->is_head(), dir_index(dp->get_dir())};
            occ[c] = static_cast<int>(parts.size());
            occ_cells.push_back(c);
            if (p.head) (ally ? ally_heads : enemy_heads).push_back(static_cast<int>(parts.size()));
            parts.push_back(p);
            DragonMem& m = mem[did];
            if (m.id < 0) {
                m.id = did;
                m.first_round = rnd;
            }
            m.ally = ally;
            if (m.last_round != rnd) { m.vis_len = 0; m.cut = false; }
            m.last_round = rnd;
            m.vis_len++;
            if (p.head) {
                m.cell = c;
                m.facing = p.dir;
            }
        }
        vacancy();
        track_body();
        if (rnd % 8 == 0) {
            for (int c = 0; c < NC; c++) {
                if (pearl_seen[c] >= 0 && rnd - pearl_seen[c] > 400) {
                    pearl_seen[c] = -1;
                    auto it = std::find(pearl_order.begin(), pearl_order.end(), c);
                    if (it != pearl_order.end()) pearl_order.erase(it);
                }
                if (rnd - body_seen[c] > Params::blind_fresh) body_seen[c] = -1000;
            }
        }
    }

    // Record the move we are about to make (keeps the trail exact through sprints).
    void commit_move(const std::vector<int>& dirs) {
        if (dirs.empty()) return;
        int c = head;
        for (size_t i = 0; i < dirs.size(); i++) {
            int d = dirs[i];
            if (is_portal_edge(c, d)) {
                last_exit_portal = ekey(c, d);
                last_exit_round = rnd;
            }
            int n = dest(c, d);
            if (n < 0) break;
            if (i + 1 < dirs.size()) trail.push_back(n);  // intermediate cells
            c = n;
        }
        last_move = dirs.back();
    }

  private:
    std::vector<int> pointed_;       // per cell: part index pointing at it (-1)
    std::vector<int> pointed_cells_;
    std::vector<int> chain_;
    std::vector<int> next_part_;

    // Other bodies: walk each visible chain from its rear, as Tyr world.py
    // does. Rear fragments at the vision rim get the hidden-tail allowance.
    void vacancy() {
        if (static_cast<int>(pointed_.size()) != NC) pointed_.assign(NC, -1);
        for (int c : pointed_cells_) pointed_[c] = -1;
        pointed_cells_.clear();
        if (next_part_.size() != parts.size()) next_part_.assign(parts.size(), -1);
        else std::fill(next_part_.begin(), next_part_.end(), -1);
        for (size_t i = 0; i < parts.size(); i++) {
            const Part& p = parts[i];
            if (p.head) continue;
            int to = dest(p.cell, p.dir);
            if (to < 0) to = nbr(p.cell, p.dir);
            if (occ[to] >= 0 && parts[occ[to]].id == p.id) {
                next_part_[i] = occ[to];
                pointed_[to] = static_cast<int>(i);
                pointed_cells_.push_back(to);
            }
        }
        // Match Tyr's rear-first walk for every visible chain, including
        // disconnected fragments without a visible head.
        std::vector<uint8_t> assigned(parts.size(), 0);
        for (size_t rear = 0; rear < parts.size(); rear++) {
            int cell = parts[rear].cell;
            if (pointed_[cell] >= 0) continue;
            int hidden = cheb(cell, head) >= 3 ? Params::hidden_tail : 0;
            if (hidden) {
                auto it = mem.find(parts[rear].id);
                if (it != mem.end()) it->second.cut = true;
            }
            int arrival = hidden + 2;
            int cur = static_cast<int>(rear);
            for (int guard = 0; cur >= 0 && guard < 400 && !assigned[cur]; guard++) {
                assigned[cur] = 1;
                parts[cur].vac = arrival++;
                cur = next_part_[cur];
            }
        }
    }

    struct OwnSeen {
        int cell;
        int dir;
    };
    std::vector<OwnSeen> own_seen_;

    // Body = last `len` trail cells if consistent with what we see, else the
    // visible chain walked back from the head.
    void track_body() {
        if (trail.empty() || trail.back() != head) trail.push_back(head);
        if (trail.size() > 700) trail.erase(trail.begin(), trail.end() - 600);
        for (int c : own_cells) own[c] = 0;
        own_cells.clear();

        bool ok = static_cast<int>(trail.size()) >= len;
        if (ok) {
            for (int i = 0; i < len && ok; i++) {
                int c = trail[trail.size() - len + i];
                if (own[c]) ok = false;
                own[c] = 1;
                own_cells.push_back(c);
            }
            for (auto const& segment : own_seen_)
                if (ok && !own[segment.cell]) ok = false;
            for (int c : own_cells) own[c] = 0;
            own_cells.clear();
        }
        if (!ok) {
            std::vector<int> chain{head};
            std::vector<uint8_t> used(own_seen_.size(), 0);
            for (;;) {
                int cur = chain.back(), found = -1;
                for (size_t i = 0; i < own_seen_.size(); i++) {
                    if (used[i]) continue;
                    int c = own_seen_[i].cell, d = own_seen_[i].dir;
                    int n = dest(c, d);
                    if (n == cur || nbr(c, d) == cur) { found = static_cast<int>(i); break; }
                }
                if (found < 0) break;
                used[found] = 1;
                chain.push_back(own_seen_[found].cell);
            }
            trail.assign(chain.rbegin(), chain.rend());
        }
        int n = std::min<int>(len, static_cast<int>(trail.size()));
        body.assign(trail.end() - n, trail.end());
        for (int i = 0; i < n; i++) {
            own[body[i]] = static_cast<uint8_t>(i + 1);
            own_cells.push_back(body[i]);
        }
    }
};

}  // namespace ares

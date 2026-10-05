// HB-1: C++ mirror of tools/team_recon_claude/features_view.py (v4 actor-local row) plus the v5 legality columns
// of features_v5.py. Kept line-for-line parallel with the Python so parity can be checked on replay blocks
// (tools/hb1/cpp/feat_parity.cpp). Everything here is computed from the dragon's own protocol input and its own
// process memory; nothing is shared between dragons. mem_initial is not reproduced (the init block carries no
// parent information), so the exported models are fitted without it.
#pragma once
#include <array>
#include <cmath>
#include <cstdint>
#include <deque>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace hb1 {

// ---- the round block, as features_view.parse_block returns it -------------------------------------------
struct BlockTile { int x, y, p, cd; };
struct BlockBody { char team; int id, x, y; char facing; bool head; };
struct Block {
    int round = 0;
    char dir = 'N';
    int length = 0, units = 0, n_msgs = 0;
    bool has_echoes = false;
    std::array<int, 5> echoes{};                 // kelp ally allyHead enemy enemyHead
    std::array<BlockTile, 49> tiles{};           // row-major, row r = dy+3, col c = dx+3
    std::vector<BlockBody> bodies;
    std::array<std::array<std::string, 7>, 8> Hm; // horizontal edge rows (N of row r; row 7 = S of row 6)
    std::array<std::array<std::string, 8>, 7> Vm; // vertical edge rows (W of col c; col 7 = E of col 6)
};

static constexpr char DIRS[4] = {'N', 'E', 'S', 'W'};
static constexpr char REL[4] = {'F', 'R', 'B', 'L'};
inline int dir_index(char d) { return d == 'N' ? 0 : d == 'E' ? 1 : d == 'S' ? 2 : 3; }
inline std::pair<int, int> DXY(char d) {
    switch (d) {
    case 'N': return {0, -1};
    case 'E': return {1, 0};
    case 'S': return {0, 1};
    default:  return {-1, 0};
    }
}
inline char rel_to_abs(char facing, char rel) {
    int r = rel == 'F' ? 0 : rel == 'R' ? 1 : rel == 'B' ? 2 : 3;
    return DIRS[(dir_index(facing) + r) % 4];
}
inline char abs_to_rel(char facing, char d) { return REL[((dir_index(d) - dir_index(facing)) % 4 + 4) % 4]; }
inline std::pair<int, int> ego(char facing, int dx, int dy) {
    if (facing == 'N') return {-dy, dx};
    if (facing == 'S') return {dy, -dx};
    if (facing == 'E') return {dx, dy};
    return {-dx, -dy};
}

// ---- a feature row: name -> value, in first-set order -----------------------------------------------------
struct Row {
    std::vector<std::string> names;
    std::vector<double> vals;
    std::unordered_map<std::string, size_t> idx;
    void set(std::string const& k, double v) {
        auto it = idx.find(k);
        if (it == idx.end()) {
            idx.emplace(k, names.size());
            names.push_back(k);
            vals.push_back(v);
        } else {
            vals[it->second] = v;
        }
    }
    double get(std::string const& k) const {
        auto it = idx.find(k);
        return it == idx.end() ? NAN : vals[it->second];
    }
};

using XY = std::pair<int, int>;
using RC = std::pair<int, int>;

class Proc {
  public:
    int id;
    char team;
    int W, Hh, unit_limit;
    int turns = 0;
    std::string last_family = "none", last_rel = "none";
    int last_len = -1;                            // -1 = None
    int last_split_turn = -1, n_splits = 0, last_eat_turn = -1;
    std::map<XY, int> visited;
    long msgs_total = 0;
    std::set<std::string> seen_portals;
    int last_enemy_heads = 0, last_pearls_vis = 0;
    bool has_start = false;
    XY start{0, 0};
    int max_len = 0;
    std::map<XY, int> bed_next, bed_seen, pearl_seen;

    Proc(int my_id, char tm, int w, int h, int ul) : id(my_id), team(tm), W(w), Hh(h), unit_limit(ul) {}

    Row features(Block const& blk) {
        int const R = blk.round;
        char const facing = blk.dir;
        int const L = blk.length;
        std::map<RC, XY> cell;
        std::map<XY, std::pair<int, int>> info;
        for (int k = 0; k < 49; k++) {
            auto const& t = blk.tiles[k];
            cell[{k / 7, k % 7}] = {t.x, t.y};
            info[{t.x, t.y}] = {t.p, t.cd};
        }
        XY const head = cell[{3, 3}];
        std::map<XY, int> occ;
        for (auto const& b : blk.bodies) {
            int code;
            if (b.id == id) code = b.head ? 3 : 2;
            else if (b.team == team) code = b.head ? 5 : 4;
            else code = b.head ? 7 : 6;
            occ[{b.x, b.y}] = code;
        }
        auto occ_get = [&](XY t) { auto it = occ.find(t); return it == occ.end() ? 0 : it->second; };
        auto edge = [&](int r, int c, char d) -> std::string const& {
            if (d == 'N') return blk.Hm[r][c];
            if (d == 'S') return blk.Hm[r + 1][c];
            if (d == 'W') return blk.Vm[r][c];
            return blk.Vm[r][c + 1];
        };
        // -> kind 0=out 1=kelp 2=portal 3=in
        enum { OUT = 0, KELP = 1, PORTAL = 2, IN = 3 };
        auto step = [&](int r, int c, char d, RC& out) -> int {
            std::string const& e = edge(r, c, d);
            if (e == "w") return KELP;
            if (e != ".") return PORTAL;
            auto [dx, dy] = DXY(d);
            int r2 = r + dy, c2 = c + dx;
            if (0 <= r2 && r2 < 7 && 0 <= c2 && c2 < 7) { out = {r2, c2}; return IN; }
            return OUT;
        };

        // memory update from what is visible now
        for (auto const& [xy, pc] : info) {
            auto [p, cd] = pc;
            if (cd >= 0) { bed_next[xy] = R + cd; bed_seen[xy] = R; }
            if (p) pearl_seen[xy] = R;
            else pearl_seen.erase(xy);
        }
        Row row;
        row.set("round", R); row.set("length", L); row.set("units", blk.units); row.set("unit_limit", unit_limit);
        row.set("units_frac", double(blk.units) / unit_limit);
        row.set("W", W); row.set("H", Hh); row.set("x", head.first); row.set("y", head.second);
        row.set("xn", double(head.first) / W); row.set("yn", double(head.second) / Hh);
        row.set("facing_abs", dir_index(facing));
        row.set("n_msgs", blk.n_msgs);
        static char const* ECH[5] = {"kelp", "ally", "allyHead", "enemy", "enemyHead"};
        for (int k = 0; k < 5; k++) row.set(std::string("echo_") + ECH[k], blk.has_echoes ? blk.echoes[k] : 0);

        // window scan
        std::map<std::string, int> cnt;
        std::map<std::string, int> near = {{"pearl", 99}, {"enemy_head", 99}, {"ally_head", 99}, {"enemy_body", 99},
                                           {"bed_ready", 99}};
        int min_cd = 999;
        std::vector<std::pair<XY, int>> bodies_off;
        for (auto const& [rc, t] : cell) {
            int dy = rc.first - 3, dx = rc.second - 3;
            auto [f, rr] = ego(facing, dx, dy);
            int code = occ_get(t);
            auto [p, cd] = info[t];
            int dist = std::abs(dx) + std::abs(dy);
            std::string g = "g_" + std::to_string(f) + "_" + std::to_string(rr);
            row.set(g + "_occ", code); row.set(g + "_pearl", p); row.set(g + "_cd", cd);
            if (dist) {
                cnt["code" + std::to_string(code)] += 1;
                if (code >= 4) bodies_off.push_back({{dx, dy}, code});
                if (code == 6 || code == 7) near["enemy_body"] = std::min(near["enemy_body"], dist);
                if (code == 7) near["enemy_head"] = std::min(near["enemy_head"], dist);
                if (code == 5) near["ally_head"] = std::min(near["ally_head"], dist);
            }
            if (p) {
                cnt["pearl"] += 1;
                if (dist) near["pearl"] = std::min(near["pearl"], dist);
                cnt[f > 0 ? "pearl_front" : (f < 0 ? "pearl_back" : "pearl_side")] += 1;
                cnt[rr > 0 ? "pearl_right" : (rr < 0 ? "pearl_left" : "pearl_mid")] += 1;
            }
            if (cd >= 0) {
                cnt["bed"] += 1;
                min_cd = std::min(min_cd, cd);
                if (cd <= 3 && !p) near["bed_ready"] = std::min(near["bed_ready"], dist);
            }
            if (code == 6 || code == 7) cnt[f > 0 ? "enemy_front" : (f < 0 ? "enemy_back" : "enemy_side")] += 1;
            if (code == 4 || code == 5) cnt[f > 0 ? "ally_front" : (f < 0 ? "ally_back" : "ally_side")] += 1;
        }
        int kelp = 0, portals = 0;
        auto scan_edge = [&](std::string const& e) {
            if (e == "w") kelp++;
            else if (e != ".") { portals++; seen_portals.insert(e); }
        };
        for (auto const& r : blk.Hm) for (auto const& e : r) scan_edge(e);
        for (auto const& r : blk.Vm) for (auto const& e : r) scan_edge(e);
        row.set("vis_pearls", cnt["pearl"]); row.set("vis_beds", cnt["bed"]);
        row.set("vis_min_cd", min_cd < 999 ? min_cd : -1);
        row.set("vis_enemy_seg", cnt["code6"] + cnt["code7"]); row.set("vis_enemy_heads", cnt["code7"]);
        row.set("vis_ally_seg", cnt["code4"] + cnt["code5"]); row.set("vis_ally_heads", cnt["code5"]);
        row.set("vis_own_seg", cnt["code2"]); row.set("vis_kelp", kelp); row.set("vis_portal", portals);
        for (char const* k : {"pearl_front", "pearl_back", "pearl_left", "pearl_right", "enemy_front", "enemy_back",
                              "ally_front", "ally_back"})
            row.set(k, cnt[k]);
        for (char const* k : {"pearl", "enemy_head", "ally_head", "enemy_body", "bed_ready"})
            row.set(std::string("near_") + k, near[k]);

        // BFS inside the window from a cell (portals not traversed)
        auto bfs = [&](RC s) {
            std::map<RC, int> seen{{s, 0}};
            std::deque<RC> q{s};
            while (!q.empty()) {
                RC a = q.front(); q.pop_front();
                for (char d : DIRS) {
                    RC b;
                    if (step(a.first, a.second, d, b) != IN || seen.count(b) || occ.count(cell[b])) continue;
                    seen[b] = seen[a] + 1;
                    q.push_back(b);
                }
            }
            return seen;
        };

        int free = 0;
        for (char rel : {'F', 'R', 'L', 'B'}) {
            char ad = rel_to_abs(facing, rel);
            RC dst;
            int kind = step(3, 3, ad, dst);
            std::string P = std::string("c") + rel + "_";
            double block = 0, portal = 0, pearl = 0, cd = -1, eh_adj = 0, area = 0, pdist = 99, pmass = 0, pc3 = 0,
                   bedsoon = 0, unvisited = 0, allyh2 = 0, eseg2 = 0, run = 0, mem_bed = 99, mem_bed_n = 0,
                   mem_pearl = 99;
            if (kind == KELP) {
                block = 1;
            } else if (kind == PORTAL || kind == OUT) {
                block = -1; portal = kind == PORTAL; pearl = -1; cd = -2; eh_adj = -1; area = -1;
                pmass = -1; pc3 = -1; bedsoon = -1; unvisited = -1;
                if (kind == PORTAL) free += 1;
            } else {
                XY t = cell[dst];
                int code = occ_get(t);
                block = code;
                pearl = info[t].first; cd = info[t].second;
                int eh = 0;
                for (char d2 : DIRS) {
                    RC n2;
                    if (step(dst.first, dst.second, d2, n2) == IN && n2 != RC{3, 3} && occ_get(cell[n2]) == 7) eh++;
                }
                eh_adj = eh;
                if (code == 0) {
                    free += 1;
                    auto seen = bfs(dst);
                    area = seen.size();
                    double pm = 0; int pcc = 0, bs = 0, unv = 0, pd = 99;
                    for (auto const& [b, dd] : seen) {
                        XY tb = cell[b];
                        auto [pb, cdb] = info[tb];
                        if (pb) { pd = std::min(pd, dd); pm += 1.0 / (1 + dd); pcc += dd <= 3; }
                        else if (cdb >= 0 && cdb <= dd + 1) bs += 1;
                        if (dd <= 3 && !visited.count(tb)) unv += 1;
                    }
                    pdist = pd; pmass = pm; pc3 = pcc; bedsoon = bs; unvisited = unv;
                    auto [ddx, ddy] = DXY(ad);
                    int ah = 0, es = 0;
                    for (auto const& [bxy, kd] : bodies_off) {
                        if (std::abs(bxy.first - ddx) + std::abs(bxy.second - ddy) <= 2) {
                            if (kd == 5) ah++;
                            else if (kd >= 6) es++;
                        }
                    }
                    allyh2 = ah; eseg2 = es;
                    int rn = 0; RC a{3, 3};
                    for (int i = 0; i < 3; i++) {
                        RC n3;
                        if (step(a.first, a.second, ad, n3) != IN || occ.count(cell[n3])) break;
                        rn++; a = n3;
                    }
                    run = rn;
                }
            }
            // memory-based long-range pull (wrapped Manhattan, ignores kelp): remembered beds/pearls out of view
            if (block == 0 || block == -1) {
                auto [dx0, dy0] = DXY(ad);
                int sx = ((head.first + dx0) % W + W) % W, sy = ((head.second + dy0) % Hh + Hh) % Hh;
                int best_b = 99, nb = 0, best_p = 99;
                auto wd = [&](int bx, int by) {
                    return std::min(((bx - sx) % W + W) % W, ((sx - bx) % W + W) % W) +
                           std::min(((by - sy) % Hh + Hh) % Hh, ((sy - by) % Hh + Hh) % Hh);
                };
                for (auto const& [bxy, nxt] : bed_next) {
                    if (info.count(bxy)) continue;
                    int dd = wd(bxy.first, bxy.second);
                    if (dd <= 20 && nxt <= R + dd + 1) { nb++; best_b = std::min(best_b, dd); }
                }
                for (auto const& [pxy, sr] : pearl_seen) {
                    if (info.count(pxy) || R - sr > 30) continue;
                    best_p = std::min(best_p, wd(pxy.first, pxy.second));
                }
                mem_bed = best_b; mem_bed_n = nb; mem_pearl = best_p;
            }
            row.set(P + "block", block); row.set(P + "portal", portal); row.set(P + "pearl", pearl);
            row.set(P + "cd", cd); row.set(P + "eh_adj", eh_adj); row.set(P + "area", area);
            row.set(P + "pdist", pdist); row.set(P + "pmass", pmass); row.set(P + "pc3", pc3);
            row.set(P + "bedsoon", bedsoon); row.set(P + "unvisited", unvisited); row.set(P + "allyh2", allyh2);
            row.set(P + "eseg2", eseg2); row.set(P + "run", run); row.set(P + "mem_bed", mem_bed);
            row.set(P + "mem_bed_n", mem_bed_n); row.set(P + "mem_pearl", mem_pearl);
        }
        row.set("free_dirs", free);
        // own-process memory
        if (!has_start) { start = head; has_start = true; }
        if (last_len >= 0 && L > last_len) last_eat_turn = turns;
        auto wrapd = [](int a, int b, int n) { return std::min(((a - b) % n + n) % n, ((b - a) % n + n) % n); };
        row.set("mem_age", turns);
        row.set("mem_len_delta", last_len >= 0 ? L - last_len : 0);
        row.set("mem_since_split", last_split_turn >= 0 ? turns - last_split_turn : 999);
        row.set("mem_n_splits", n_splits);
        row.set("mem_since_eat", last_eat_turn >= 0 ? turns - last_eat_turn : 999);
        row.set("mem_visited", visited.size());
        row.set("mem_revisit", visited.count(head) ? visited[head] : 0);
        row.set("mem_msgs_total", msgs_total);
        row.set("mem_portals_seen", seen_portals.size());
        row.set("mem_enemy_heads_prev", last_enemy_heads);
        row.set("mem_pearls_prev", last_pearls_vis);
        row.set("mem_disp", wrapd(head.first, start.first, W) + wrapd(head.second, start.second, Hh));
        row.set("mem_max_len", std::max(max_len, L));
        row.set("mem_beds_known", bed_next.size());
        static std::map<std::string, int> const FAM = {{"none", 0}, {"move", 1}, {"sprint", 2}, {"split", 3}, {"suicide", 4}};
        static std::map<std::string, int> const RL = {{"none", 0}, {"F", 1}, {"R", 2}, {"L", 3}, {"B", 4}};
        row.set("mem_last_family", FAM.count(last_family) ? FAM.at(last_family) : 0);
        row.set("mem_last_rel", RL.count(last_rel) ? RL.at(last_rel) : 0);
        visited[head] += 1;
        msgs_total += blk.n_msgs;
        last_enemy_heads = int(row.get("vis_enemy_heads"));
        last_pearls_vis = int(row.get("vis_pearls"));
        max_len = std::max(max_len, L);
        last_len = L;
        turns += 1;
        // v5 legality columns (features_v5.extract)
        row.set("split_elig", (L >= 4 && blk.units < unit_limit) ? 1 : 0);
        int n_ord = 0, n_por = 0;
        for (char r : {'F', 'R', 'L'}) {
            n_ord += row.get(std::string("c") + r + "_block") == 0;
            n_por += row.get(std::string("c") + r + "_portal") == 1;
        }
        row.set("n_exit_ord", n_ord); row.set("n_exit_portal", n_por); row.set("n_exit_any", n_ord + n_por);
        return row;
    }

    // kind: 'm' move (rels = relative steps), 's' split (child size)
    void record_move(std::string const& rels) {
        last_family = rels.size() == 1 ? "move" : "sprint";
        last_rel = std::string(1, rels[0]);
    }
    void record_split(int child) {
        if (child == 1) { last_family = "suicide"; return; }
        last_family = "split";
        n_splits += 1;
        last_split_turn = turns - 1;
    }
};

}  // namespace hb1

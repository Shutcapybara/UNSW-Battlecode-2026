// Actor-local H-Q8 v1; mirrored in hq8_features.py. See hq8_schema.md.
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <vector>

namespace hq8 {
using XY = std::pair<int, int>;
struct Tile { int x, y, pearl, countdown; };
struct Body { char team; int id, x, y; char facing; bool head; };
struct Block {
    int round, length;
    std::array<Tile, 49> tiles;
    std::vector<Body> bodies;
    std::array<std::array<std::string, 7>, 8> H;
    std::array<std::array<std::string, 8>, 7> V;
};
inline std::vector<std::string> const names = {
    "round", "rounds_remaining", "is_queen", "mode", "rl_likely", "pocket_map",
    "own_alive", "own_seen_age", "own_x", "own_y", "own_distance",
    "enemy_alive", "enemy_seen_age", "enemy_x", "enemy_y", "enemy_distance",
    "own_length", "enemy_length", "length_margin", "own_visible_length_lb",
    "enemy_visible_length_lb", "own_visible_rank", "own_rank_exact",
    "own_split_age", "own_enemy_heads_3", "own_enemy_reach_lb", "own_reach_exact",
    "own_ally_heads_2", "own_ally_heads_3", "own_free_cells_5",
    "own_free_cells_censored", "own_kelp_edges", "own_nearest_bed",
    "own_nearest_pearl", "own_pearl_origin_known", "sonar_decoded"
};
class Encoder {
    int id, width, height, queen, round = 0, split_round = -1;
    std::array<int, 2> seen_round{{-1, -1}};
    std::array<XY, 2> last;
    int distance(XY a, XY b) const {
        int dx = std::abs(a.first - b.first), dy = std::abs(a.second - b.second);
        return std::min(dx, width - dx) + std::min(dy, height - dy);
    }
  public:
    Encoder(int my_id, char team, int w, int h, int) : id(my_id), width(w), height(h), queen(team == 'A' ? 0 : 1) {}
    void record_split() { if (id == queen) split_round = round; }
    std::vector<int32_t> features(Block const& b) {
        round = b.round;
        XY head{b.tiles[24].x, b.tiles[24].y};
        std::map<int, int> visible;
        std::map<int, XY> heads;
        std::map<XY, XY> xy_to_rc;
        std::set<XY> occupied;
        for (auto const& body : b.bodies) {
            visible[body.id]++;
            if (body.head) heads[body.id] = {body.x, body.y};
            occupied.insert({body.x, body.y});
        }
        for (int k = 0; k < 49; k++) xy_to_rc[{b.tiles[k].x, b.tiles[k].y}] = {k / 7, k % 7};
        std::map<std::string, int> row;
        for (auto const& name : names) row[name] = -1;
        row["round"] = round; row["rounds_remaining"] = std::max(0, 500 - round);
        row["is_queen"] = id == queen; row["sonar_decoded"] = 0;
        row["own_pearl_origin_known"] = 0; row["own_rank_exact"] = 0; row["own_reach_exact"] = 0;
        for (int side = 0; side < 2; side++) {
            int qid = side == 0 ? queen : 1 - queen;
            std::string p = side == 0 ? "own" : "enemy";
            if (heads.count(qid)) {
                last[side] = heads[qid]; seen_round[side] = round;
                row[p + "_alive"] = 1;
            }
            if (seen_round[side] >= 0) {
                row[p + "_seen_age"] = round - seen_round[side];
                row[p + "_x"] = last[side].first; row[p + "_y"] = last[side].second;
                row[p + "_distance"] = distance(head, last[side]);
            }
            row[p + "_visible_length_lb"] = visible[qid];
            if (id == qid) row[p + "_length"] = b.length;
        }
        if (row["own_alive"] == 1 && row["enemy_alive"] == 1) row["mode"] = 3;
        if (id == queen) row["own_split_age"] = split_round < 0 ? round : round - split_round;
        if (heads.count(queen)) {
            XY qxy = heads[queen];
            int enemy3 = 0, enemy_reach = 0, ally2 = 0, ally3 = 0;
            for (auto const& [did, xy] : heads) {
                if (did == queen) continue;
                int dist = distance(qxy, xy);
                if (did % 2 == queen) { ally2 += dist <= 2; ally3 += dist <= 3; }
                else { enemy3 += dist <= 3; enemy_reach += dist <= 1 + (visible[did] + 3) / 4; }
            }
            row["own_enemy_heads_3"] = enemy3; row["own_enemy_reach_lb"] = enemy_reach;
            row["own_ally_heads_2"] = ally2; row["own_ally_heads_3"] = ally3;
            if (id == queen) {
                int rank = 1;
                for (auto const& [did, length] : visible) if (did != queen && did % 2 == queen && length > b.length) rank++;
                row["own_visible_rank"] = rank;
            }
            int bed = -1, pearl = -1;
            for (auto const& tile : b.tiles) {
                int dist = distance(qxy, {tile.x, tile.y});
                if (tile.countdown >= 0) bed = bed < 0 ? dist : std::min(bed, dist);
                if (tile.pearl > 0) pearl = pearl < 0 ? dist : std::min(pearl, dist);
            }
            row["own_nearest_bed"] = bed; row["own_nearest_pearl"] = pearl;
            XY start = xy_to_rc.at(qxy);
            auto edge = [&](XY rc, int d) -> std::string const& {
                int r = rc.first, c = rc.second;
                if (d == 0) return b.H[r][c];
                if (d == 1) return b.V[r][c + 1];
                if (d == 2) return b.H[r + 1][c];
                return b.V[r][c];
            };
            int kelp = 0;
            for (int d = 0; d < 4; d++) kelp += edge(start, d) == "w";
            row["own_kelp_edges"] = kelp;
            std::set<XY> seen{start};
            std::queue<std::pair<XY, int>> queue;
            queue.push({start, 0});
            constexpr int dy[4] = {-1, 0, 1, 0}, dx[4] = {0, 1, 0, -1};
            int free = 0, censored = 0;
            while (!queue.empty()) {
                auto [rc, depth] = queue.front(); queue.pop();
                if (depth == 5) continue;
                for (int d = 0; d < 4; d++) {
                    std::string const& e = edge(rc, d);
                    if (e == "w") continue;
                    XY next{rc.first + dy[d], rc.second + dx[d]};
                    if (e != "." || next.first < 0 || next.first >= 7 || next.second < 0 || next.second >= 7) {
                        censored = 1; continue;
                    }
                    auto const& tile = b.tiles[next.first * 7 + next.second];
                    if (seen.count(next) || occupied.count({tile.x, tile.y})) continue;
                    seen.insert(next); free++; queue.push({next, depth + 1});
                }
            }
            row["own_free_cells_5"] = free; row["own_free_cells_censored"] = censored;
        }
        std::vector<int32_t> result;
        for (auto const& name : names) result.push_back(row.at(name));
        return result;
    }
};
}  // namespace hq8

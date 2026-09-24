#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <sstream>
#include <string>
#include <vector>

constexpr int DX[] = {0, 1, 0, -1};
constexpr int DY[] = {-1, 0, 1, 0};
constexpr char DIR[] = "NESW";
constexpr std::uint64_t MOVE_ASIDE = 1146242894u; // ASCII "DRGN"
constexpr std::uint64_t TEAM_STATUS_TAG = UINT64_C(0xA8) << 56;

struct Tile {
    bool visible = false, pearl = false, occupied = false;
    bool own_body = false;
    int countdown = -1;
    bool friendly_head = false, enemy_head = false;
    int dragon_id = -1, facing = -1;
    std::array<std::string, 4> edges = {".", ".", ".", "."};
};

struct Edge {
    int x, y;
    bool horizontal;
    bool operator==(const Edge& other) const {
        return x == other.x && y == other.y && horizontal == other.horizontal;
    }
};

struct EnemyMemory {
    int position = -1;
    int visible_size = 0;
    int facing = -1;
    int last_seen = -1;
};

struct PearlMemory {
    bool present = false;
    int countdown = -1;
    int last_seen = -1;
};

struct FriendlyMemory {
    int length = 0;
    int position = -1;
    int last_seen = -1;
};

class Bot {
    int width = 0, height = 0, id = 0, limit = 64;
    int round = 0, length = 0, units = 0, head = 0, facing = 0;
    bool asked_to_move = false;
    std::string my_team;
    std::vector<Tile> tiles;
    std::vector<int> visits;
    std::vector<std::array<std::string, 4>> known_edges;
    std::vector<bool> known_edge;
    std::vector<PearlMemory> known_pearls;
    std::map<int, EnemyMemory> enemies;
    std::map<int, FriendlyMemory> teammates;
    std::map<int, int> visible_friendly_sizes;
    std::map<std::string, std::vector<Edge>> portals;
    mutable bool friend_routes_ready = false;
    mutable std::map<int, std::vector<int>> live_friend_routes;
    mutable std::map<int, std::vector<int>> static_friend_routes;
    mutable std::vector<std::pair<int, int>> nearest_pearl_routes;
    std::string route, trip_portal;
    Edge trip_entry{0, 0, false};
    bool inside = false;
    int expected_head = -1, expected_round = -1;

    static bool line(std::string& value) {
        while (std::getline(std::cin, value)) {
            value = value.substr(0, value.find('#'));
            if (value.find_first_not_of(" \t\r") != std::string::npos) return true;
        }
        return false;
    }
    template<class T> static bool field(const std::string& expected, T& value) {
        std::string text, key;
        if (!line(text)) return false;
        std::istringstream input(text);
        return bool(input >> key >> value) && key == expected;
    }
    static int direction(char value) {
        for (int d = 0; d < 4; ++d) if (DIR[d] == value) return d;
        return 0;
    }
    static std::uint64_t team_status_message(int id, int length, int x, int y, int round) {
        return TEAM_STATUS_TAG |
               (static_cast<std::uint64_t>(id & 0xFFFFF) << 36) |
               (static_cast<std::uint64_t>(length & 4095) << 24) |
               (static_cast<std::uint64_t>(x) << 18) |
               (static_cast<std::uint64_t>(y) << 12) |
               (static_cast<std::uint64_t>(round & 1023) << 2);
    }
    int teammate_estimate(int teammate_id) const {
        int estimate = 0;
        auto report = teammates.find(teammate_id);
        if (report != teammates.end() && report->second.last_seen >= 0 &&
            round - report->second.last_seen <= 20)
            estimate = report->second.length;
        auto visible = visible_friendly_sizes.find(teammate_id);
        if (visible != visible_friendly_sizes.end())
            estimate = std::max(estimate, visible->second);
        return estimate;
    }
    bool teammate_active(int teammate_id) const {
        return teammate_estimate(teammate_id) > 0;
    }
    bool is_largest_known() const {
        for (const auto& item : teammates) {
            int estimate = teammate_estimate(item.first);
            if (estimate > length || (estimate == length && estimate > 0 && item.first < id))
                return false;
        }
        for (const auto& item : visible_friendly_sizes)
            if (!teammates.count(item.first) &&
                (item.second > length || (item.second == length && item.first < id)))
                return false;
        return true;
    }
    bool has_larger_known_teammate() const {
        for (const auto& item : teammates)
            if (teammate_estimate(item.first) > length) return true;
        for (const auto& item : visible_friendly_sizes)
            if (item.second > length) return true;
        return false;
    }
    bool should_explore_portals() const {
        constexpr int MIN_ALIVE_TO_EXPLORE = 4;
        return units >= MIN_ALIVE_TO_EXPLORE && has_larger_known_teammate();
    }
    int largest_known_team_length() const {
        int largest = length;
        for (const auto& item : teammates)
            largest = std::max(largest, teammate_estimate(item.first));
        for (const auto& item : visible_friendly_sizes)
            largest = std::max(largest, item.second);
        return largest;
    }
    int largest_known_enemy_length() const {
        int largest = 0;
        for (const auto& item : enemies)
            largest = std::max(largest, item.second.visible_size);
        return largest;
    }
    bool should_focus_growth() const {
        if (!is_largest_known()) return false;
        constexpr int SIZE_BUFFER = 2;
         constexpr int DEFICIT_ROUND = 400;
         constexpr int FORCED_GROWTH_ROUND = 450;
         return round >= FORCED_GROWTH_ROUND ||
             (round >= DEFICIT_ROUND &&
            largest_known_enemy_length() + SIZE_BUFFER >= largest_known_team_length());
    }
    bool visible_threat() const {
        for (const auto& tile : tiles)
            if (tile.enemy_head) return true;
        return false;
    }
    int pos(int x, int y) const {
        return ((y % height + height) % height) * width +
               (x % width + width) % width;
    }
    Edge edge_at(int p, int d) const {
        int anchor = pos(p % width + (d == 1), p / width + (d == 2));
        return {anchor % width, anchor / width, d % 2 == 0};
    }
    void set_edge(int p, int d, const std::string& symbol) {
        tiles[p].edges[d] = symbol;
        known_edges[p][d] = symbol;
        known_edge[p] = true;
        if (symbol == "." || symbol == "w") return;
        Edge edge = edge_at(p, d);
        auto& ends = portals[symbol];
        for (const auto& end : ends) if (end == edge) return;
        ends.push_back(edge);
    }
    int destination(int p, int d, bool check_body = true, bool allow_portal = false) const {
        const std::string& symbol = tiles[p].edges[d];
        if (symbol == "w") return -1;
        int next = pos(p % width + DX[d], p / width + DY[d]);
        if (symbol != ".") {
            // Every portal crossing must belong to a checked round trip.
            if (!allow_portal) return -1;
            auto found = portals.find(symbol);
            if (found == portals.end() || found->second.size() != 2) return -2;
            Edge entry = edge_at(p, d);
            Edge exit = found->second[0] == entry ? found->second[1] : found->second[0];
            if (entry.horizontal != exit.horizontal) return -2;
            next = pos(exit.x - (d == 3), exit.y - (d == 0));
        }
        if (!tiles[next].visible) return -2;
        return check_body && tiles[next].occupied ? -1 : next;
    }

    void rebuild_known_portals() {
        portals.clear();
        for (int p = 0; p < static_cast<int>(known_edges.size()); ++p) {
            for (int d = 0; d < 4; ++d) {
                const std::string& symbol = known_edges[p][d];
                if (!known_edge[p] || symbol == "." || symbol == "w") continue;
                Edge edge = edge_at(p, d);
                auto& ends = portals[symbol];
                if (std::find(ends.begin(), ends.end(), edge) == ends.end())
                    ends.push_back(edge);
            }
        }
    }

    static constexpr int HORIZON = 18;
    static constexpr int BEAM = 256;
    struct Trip {
        std::string moves, portal;
        Edge entry{0, 0, false};
        std::vector<int> trail, collected;
        int stage = 0, after_exit = 0; // approach, inside, returned
        int reward = 0;
    };

    std::vector<bool> threats() const {
        std::vector<bool> danger(tiles.size(), false);
        // Reserve the two-step reach of visible enemy heads. Future enemy
        // choices remain unknown; the whole route is checked again next turn.
        for (int p = 0; p < static_cast<int>(tiles.size()); ++p) {
            if (!tiles[p].enemy_head) continue;
            danger[p] = true;
            for (int d = 0; d < 4; ++d) {
                int q = destination(p, d, false, true);
                if (q < 0) continue;
                danger[q] = true;
                for (int e = 0; e < 4; ++e) {
                    int r = destination(q, e, false, true);
                    if (r >= 0) danger[r] = true;
                }
            }
        }
        return danger;
    }

    Trip initial_trip() const {
        Trip state;
        state.trail.push_back(head);
        if (inside) {
            state.stage = 1;
            state.portal = trip_portal;
            state.entry = trip_entry;
        }
        return state;
    }

    bool advance(Trip& state, int d, const std::vector<bool>& danger) const {
        int p = state.trail.back();
        int next = destination(p, d, false, true);
        if (next < 0 || danger[next]) return false;
        const int step = static_cast<int>(state.moves.size()) + 1;
        // Other dragons stay blocked. Since the protocol does not order our
        // segments, conservatively reserve each for a full grown body length.
        bool collected = std::find(state.collected.begin(), state.collected.end(), next)
                         != state.collected.end();
        // First move occurs this round, before a positive countdown expires.
        bool pearl = !collected && (tiles[next].pearl ||
            (tiles[next].countdown >= 0 && tiles[next].countdown < step));
        int grown_length = length + static_cast<int>(state.collected.size()) + int(pearl);
        if (tiles[next].occupied && (!tiles[next].own_body || step <= grown_length))
            return false;
        for (int i = 0; i < static_cast<int>(state.trail.size()); ++i)
            if (state.trail[i] == next && step - i <= grown_length) return false;

        const std::string& symbol = tiles[p].edges[d];
        if (symbol != ".") {
            if (state.stage == 0) {
                state.portal = symbol;
                state.entry = edge_at(p, d);
                state.stage = 1;
            } else if (state.stage == 1 && symbol == state.portal &&
                       !(edge_at(p, d) == state.entry)) {
                state.stage = 2;
            } else return false;
        } else if (state.stage == 2) {
            ++state.after_exit;
        }
        if (pearl) {
            state.collected.push_back(next);
            // Score the excursion and its escape, including a pearl on exit.
            if (state.stage != 0) ++state.reward;
        }
        state.moves += DIR[d];
        state.trail.push_back(next);
        return true;
    }

    std::string plan_trip(const std::vector<bool>& danger) const {
        bool has_pair = false;
        for (const auto& item : portals) has_pair |= item.second.size() == 2;
        if (!has_pair) return {};
        std::vector<Trip> beam{initial_trip()};
        Trip best;
        int best_reward = -1;
        for (int depth = 0; depth < HORIZON && !beam.empty(); ++depth) {
            std::vector<Trip> next_beam;
            for (const auto& state : beam) {
                for (int offset = 0; offset < 4; ++offset) {
                    int d = (offset + id + round / 8) % 4;
                    Trip next = state;
                    if (!advance(next, d, danger)) continue;
                    if (next.stage == 2 && next.after_exit >= 2) {
                        // When a committed trip is disrupted, get out promptly.
                        if (inside) return next.moves;
                        if ((inside || next.reward > 0 || should_explore_portals()) &&
                            next.reward > best_reward) {
                            best = next;
                            best_reward = next.reward;
                        }
                        continue;
                    }
                    next_beam.push_back(std::move(next));
                }
            }
            // Keep diverse locations and trip stages, so a rich cul-de-sac
            // does not evict every candidate with an actual return route.
            std::stable_sort(next_beam.begin(), next_beam.end(), [](const Trip& a, const Trip& b) {
                return a.reward > b.reward;
            });
            std::map<std::pair<int, int>, int> retained;
            beam.clear();
            for (auto& next : next_beam) {
                if (retained[{next.trail.back(), next.stage}]++ >= 4) continue;
                beam.push_back(std::move(next));
                if (static_cast<int>(beam.size()) == BEAM) break;
            }
        }
        return best.moves;
    }

    std::string plan_unmatched_portal(const std::vector<bool>& danger) const {
        std::vector<std::string> path(tiles.size());
        std::vector<bool> seen(tiles.size(), false);
        std::queue<int> pending;
        seen[head] = true;
        pending.push(head);
        while (!pending.empty()) {
            int p = pending.front();
            pending.pop();
            for (int offset = 0; offset < 4; ++offset) {
                int d = (offset + id + round / 8) % 4;
                const std::string& symbol = tiles[p].edges[d];
                auto portal = portals.find(symbol);
                if (symbol != "." && symbol != "w" && portal != portals.end() &&
                    portal->second.size() == 1)
                    return path[p] + DIR[d];
                int next = destination(p, d);
                if (next < 0 || seen[next] || danger[next]) continue;
                seen[next] = true;
                path[next] = path[p] + DIR[d];
                pending.push(next);
            }
        }
        return {};
    }

    int survival_move() const {
        auto danger = threats();
        int best = -1, best_score = std::numeric_limits<int>::min();
        for (int d = 0; d < 4; ++d) {
            if (tiles[head].edges[d] != ".") continue;
            Trip next = initial_trip();
            if (!advance(next, d, danger)) continue;
            int exits = 0;
            for (int e = 0; e < 4; ++e) {
                if (tiles[next.trail.back()].edges[e] != ".") continue;
                Trip onward = next;
                if (advance(onward, e, danger)) ++exits;
            }
            int score = exits * 1000 + nearest_friend(next.trail.back()) - visits[next.trail.back()];
            if (score > best_score) { best = d; best_score = score; }
        }
        return best;
    }

    std::string portal_action() {
        auto danger = threats();
        if (head != expected_head || round != expected_round) route.clear();
        if (!route.empty()) {
            Trip check = initial_trip();
            for (char move : route) {
                if (!advance(check, direction(move), danger)) { route.clear(); break; }
            }
        }
        if (route.empty()) route = plan_trip(danger);
        if (route.empty() && should_explore_portals())
            route = plan_unmatched_portal(danger);
        if (route.empty()) return {};
        int d = direction(route.front());
        const std::string& symbol = tiles[head].edges[d];
        if (symbol != ".") {
            if (!inside) { trip_portal = symbol; trip_entry = edge_at(head, d); inside = true; }
            else inside = false;
        }
        expected_head = destination(head, d, false, true);
        expected_round = round + 1;
        route.erase(0, 1);
        return std::string("MOVE ") + DIR[d];
    }
    void build_friend_routes() const {
        if (friend_routes_ready) return;
        friend_routes_ready = true;
        const int n = static_cast<int>(tiles.size());
        live_friend_routes.clear();
        static_friend_routes.clear();
        nearest_pearl_routes.assign(n, {9999, 9999});
        for (int source = 0; source < n; ++source) {
            if (!tiles[source].friendly_head || source == head) continue;
            int teammate_id = tiles[source].dragon_id;
            std::vector<int> live(n, -1), terrain(n, -1);
            std::queue<int> q;
            live[source] = 0;
            q.push(source);
            while (!q.empty()) {
                int p = q.front(); q.pop();
                for (int d = 0; d < 4; ++d) {
                    int next = destination(p, d);
                    if (next < 0 || live[next] >= 0) continue;
                    live[next] = live[p] + 1;
                    q.push(next);
                }
            }
            terrain[source] = 0;
            q.push(source);
            while (!q.empty()) {
                int p = q.front(); q.pop();
                for (int d = 0; d < 4; ++d) {
                    int next = destination(p, d, false);
                    if (next < 0 || terrain[next] >= 0) continue;
                    terrain[next] = terrain[p] + 1;
                    q.push(next);
                }
            }
            for (int p = 0; p < n; ++p) {
                if (live[p] >= 0 &&
                    std::pair<int, int>{live[p], teammate_id} < nearest_pearl_routes[p])
                    nearest_pearl_routes[p] = {live[p], teammate_id};
            }
            live_friend_routes[teammate_id] = std::move(live);
            static_friend_routes[teammate_id] = std::move(terrain);
        }
    }
    int nearest_friend(int start) const {
        build_friend_routes();
        int best = 99;
        int sx = start % width, sy = start / width;
        for (const auto& route : live_friend_routes) {
            int distance = route.second[start];
            if (distance < 0) {
                const auto& terrain = static_friend_routes.at(route.first);
                distance = terrain[start];
            }
            if (distance < 0) {
                for (int p = 0; p < static_cast<int>(tiles.size()); ++p) {
                    if (!tiles[p].friendly_head || p == head || tiles[p].dragon_id != route.first) continue;
                    int dx = std::abs(sx - p % width), dy = std::abs(sy - p / width);
                    distance = std::min(distance < 0 ? 99 : distance,
                        std::min(dx, width - dx) + std::min(dy, height - dy));
                }
            }
            if (distance >= 0) best = std::min(best, distance);
        }
        return best;
    }
    bool owns_pearl(int pearl, int route_distance) const {
        build_friend_routes();
        return nearest_pearl_routes[pearl] >= std::pair<int, int>{route_distance, id};
    }
    std::string attack_path() const {
        std::vector<std::string> path(tiles.size());
        std::vector<bool> seen(tiles.size(), false);
        std::queue<int> pending;
        seen[head] = true;
        pending.push(head);
        while (!pending.empty()) {
            int p = pending.front(); pending.pop();
            if (static_cast<int>(path[p].size()) >= length - 1) continue;
            for (int offset = 0; offset < 4; ++offset) {
                int d = (offset + id + round) % 4;
                int next = destination(p, d, false);
                if (next < 0 || seen[next]) continue;
                seen[next] = true;
                path[next] = path[p] + DIR[d];
                if (tiles[next].enemy_head) {
                    auto enemy = enemies.find(tiles[next].dragon_id);
                    if (enemy != enemies.end() && enemy->second.visible_size > length)
                        return path[next];
                    continue;
                }
                if (tiles[next].occupied) continue;
                pending.push(next);
            }
        }
        return {};
    }
    bool should_signal() const {
        // A one-tile gap is the closest range where moving forward does not
        // collide before sonar is cast. Prefer the lower-ID dragon as sender.
        int p = head;
        for (int distance = 1; distance <= 3; ++distance) {
            p = destination(p, facing, false);
            if (p < 0) return false;
            if (!tiles[p].occupied) continue;
            return distance >= 2 && tiles[p].friendly_head &&
                   tiles[p].facing == (facing + 2) % 4 && id < tiles[p].dragon_id;
        }
        return false;
    }
    int best_spread_move(bool urgent) const {
        int best = -1, best_score = std::numeric_limits<int>::min();
        for (int offset = 0; offset < 4; ++offset) {
            int d = (offset + id + round / 8) % 4;
            int next = destination(head, d);
            if (next < 0) continue;
            int exits = 0;
            for (int turn = 0; turn < 4; ++turn)
                if (destination(next, turn) >= 0) ++exits;
            int score = nearest_friend(next) * (urgent ? 1000 : 100) + exits * 8 - visits[next] * 3;
            if (d == (facing + 2) % 4) score -= 20; // usually points into our neck
            if (score > best_score) { best_score = score; best = d; }
        }
        return best;
    }

public:
    bool init() {
        std::string text, key;
        if (!field("ID", id) || !field("TEAM", my_team) || !line(text)) return false;
        std::istringstream input(text);
        if (!(input >> key >> width >> height) || key != "MAP" ||
            width < 1 || width > 64 || height < 1 || height > 64) return false;
        if (!field("UNIT_LIMIT", limit)) return false;
        visits.assign(width * height, 0);
        known_edges.assign(width * height, std::array<std::string, 4>{".", ".", ".", "."});
        known_edge.assign(width * height, false);
        known_pearls.assign(width * height, PearlMemory{});
        return true;
    }
    bool update() {
        std::string facing_text, text, team, body_facing;
        int count;
        std::map<int, int> observed_enemy_sizes;
        std::map<int, int> observed_friendly_sizes;
        if (!field("ROUND", round) || !field("DIR", facing_text) ||
            !field("LENGTH", length) || !field("UNIT_COUNT", units) ||
            !field("NUM_MSGS", count)) return false;
        facing = direction(facing_text[0]);
        asked_to_move = false;
        for (int i = 0; i < count; ++i) {
            std::uint64_t message;
            if (!line(text)) return false;
            std::istringstream input(text);
            if (!(input >> message)) return false;
            asked_to_move = asked_to_move || message == MOVE_ASIDE;
            if ((message & (UINT64_C(0xFF) << 56)) == TEAM_STATUS_TAG) {
                int teammate_id = static_cast<int>((message >> 36) & 0xFFFFF);
                int teammate_length = static_cast<int>((message >> 24) & 4095);
                int teammate_x = static_cast<int>((message >> 18) & 63);
                int teammate_y = static_cast<int>((message >> 12) & 63);
                int teammate_round = static_cast<int>((message >> 2) & 1023);
                int message_age = (round - teammate_round + 1024) % 1024;
                if (teammate_id != id && teammate_length >= 2 && message_age <= 20 &&
                    teammate_x < width && teammate_y < height) {
                    int observed_round = round - message_age;
                    auto previous = teammates.find(teammate_id);
                    if (previous == teammates.end() || observed_round >= previous->second.last_seen)
                        teammates[teammate_id] = {teammate_length,
                                                  teammate_y * width + teammate_x,
                                                  observed_round};
                }
            }
        }
        tiles.assign(width * height, Tile{});
        visible_friendly_sizes.clear();
        friend_routes_ready = false;
        live_friend_routes.clear();
        static_friend_routes.clear();
        nearest_pearl_routes.clear();
        for (int p = 0; p < static_cast<int>(tiles.size()); ++p)
            if (known_edge[p]) tiles[p].edges = known_edges[p];
        rebuild_known_portals();
        std::array<int, 49> window{};
        if (!line(text)) return false;
        if (text.rfind("ECHOES ", 0) == 0) {
            std::istringstream echoes(text);
            std::string key;
            int ignored[5];
            if (!(echoes >> key >> ignored[0] >> ignored[1] >> ignored[2] >> ignored[3] >> ignored[4]))
                return false;
            if (!line(text)) return false;
        }
        for (int i = 0; i < 49; ++i) {
            int x, y, pearl, countdown;
            if (i > 0 && !line(text)) return false;
            std::istringstream input(text);
            if (!(input >> x >> y >> pearl >> countdown)) return false;
            int p = window[i] = pos(x, y);
            tiles[p].visible = true;
            tiles[p].pearl = pearl != 0;
            tiles[p].countdown = countdown;
            known_pearls[p] = {tiles[p].pearl, countdown, round};
        }
        head = window[24];
        ++visits[head];
        if (!field("DRAGON_BODIES", count)) return false;
        for (int i = 0; i < count; ++i) {
            int dragon, x, y, is_head;
            if (!line(text)) return false;
            std::istringstream input(text);
            if (!(input >> team >> dragon >> x >> y >> body_facing >> is_head)) return false;
            int p = pos(x, y);
            tiles[p].occupied = true;
            tiles[p].own_body = team == my_team && dragon == id;
            tiles[p].pearl = false;
            tiles[p].dragon_id = dragon;
            if (team != my_team) {
                auto& memory = enemies[dragon];
                ++observed_enemy_sizes[dragon];
                memory.position = p;
                memory.last_seen = round;
            } else if (dragon != id) {
                ++observed_friendly_sizes[dragon];
            }
            if (is_head) {
                tiles[p].facing = direction(body_facing[0]);
                tiles[p].friendly_head = team == my_team;
                tiles[p].enemy_head = team != my_team;
                if (team != my_team) enemies[dragon].facing = tiles[p].facing;
            }
        }
        for (const auto& observed : observed_enemy_sizes) {
            auto& memory = enemies[observed.first];
            memory.visible_size = std::max(observed.second, memory.visible_size - 1);
        }
        for (auto& enemy : enemies) {
            if (observed_enemy_sizes.count(enemy.first) == 0)
                enemy.second.visible_size = std::max(0, enemy.second.visible_size - 1);
        }
        visible_friendly_sizes = observed_friendly_sizes;
        for (int row = 0; row < 8; ++row) {
            if (!line(text)) return false;
            std::istringstream input(text);
            for (int col = 0; col < 7; ++col) {
                std::string symbol;
                if (!(input >> symbol)) return false;
                if (row < 7) set_edge(window[row * 7 + col], 0, symbol);
                if (row > 0) set_edge(window[(row - 1) * 7 + col], 2, symbol);
            }
        }
        for (int row = 0; row < 7; ++row) {
            if (!line(text)) return false;
            std::istringstream input(text);
            for (int col = 0; col < 8; ++col) {
                std::string symbol;
                if (!(input >> symbol)) return false;
                if (col < 7) set_edge(window[row * 7 + col], 3, symbol);
                if (col > 0) set_edge(window[row * 7 + col - 1], 1, symbol);
            }
        }
        return true;
    }
private:
    std::string growth_action() {
        auto danger = threats();
        std::vector<int> distance(tiles.size(), -1), first(tiles.size(), -1);
        std::queue<int> pending;
        distance[head] = 0;
        pending.push(head);
        int target = -1, best_score = std::numeric_limits<int>::min();
        while (!pending.empty()) {
            int p = pending.front(); pending.pop();
            if (p != head && (tiles[p].pearl ||
                (tiles[p].countdown >= 0 && tiles[p].countdown < distance[p]))) {
                int score = -distance[p] * 100 + std::min(nearest_friend(p), 10) - visits[p] + 20;
                if (score > best_score) { best_score = score; target = p; }
            }
            for (int d = 0; d < 4; ++d) {
                int next = destination(p, d);
                if (next < 0 || danger[next] || distance[next] >= 0) continue;
                // Do not grow into a pocket with no clear onward move.
                bool onward = false;
                for (int e = 0; e < 4; ++e) {
                    int exit = destination(next, e);
                    if (exit >= 0 && exit != p && !danger[exit]) onward = true;
                }
                if (!onward) continue;
                distance[next] = distance[p] + 1;
                first[next] = p == head ? d : first[p];
                pending.push(next);
            }
        }
        if (target >= 0) {
            return std::string("MOVE ") + DIR[first[target]];
        }
        int move = survival_move();
        if (move < 0) move = best_spread_move(true);
        if (move >= 0) return std::string("MOVE ") + DIR[move];
        // Keep emergency splitting as a last resort when physically trapped.
        if (length >= 4 && units < limit) return "SPLIT 2";
        return "MOVE N";
    }

    std::string body(bool signal) {
        std::string portal_move = portal_action();
        if (!portal_move.empty()) return portal_move;
        if (inside) {
            // A changed view can invalidate the return plan. Stay in survival
            // mode and retry planning next turn instead of splitting/attacking.
            int move = survival_move();
            if (move < 0) move = best_spread_move(true);
            if (move >= 0) return std::string("MOVE ") + DIR[move];
            if (length >= 4 && units < limit) return "SPLIT 2";
            return "MOVE N";
        }
        if (should_focus_growth()) return growth_action();
        // Preserve a minimum force before trading dragons head-to-head. If the
        // team drops below three survivors, every remaining dragon rebuilds
        // the swarm instead of pursuing an enemy head.
        if (units >= 3) {
            std::string attack = attack_path();
            if (!attack.empty()) {
                int steps = std::min<int>(static_cast<int>(attack.size()), length - 1);
                if (steps > 0) return "MOVE " + attack.substr(0, steps);
            }
        }

        if (asked_to_move) {
            int move = best_spread_move(true);
            if (move >= 0) return std::string("MOVE ") + DIR[move];
        }
        if (length >= 4 && units < limit) {
            return "SPLIT 2";
        }
        if (signal && destination(head, facing) >= 0)
            return std::string("MOVE ") + DIR[facing];

        // Pearls are considered only after attacks, sonar reactions, splitting,
        // and the strong friendly-separation term in the route score.
        std::vector<int> distance(tiles.size(), -1), first(tiles.size(), -1);
        std::queue<int> pending;
        distance[head] = 0;
        pending.push(head);
        int pearl = -1, explore = -1, pearl_score = std::numeric_limits<int>::min();
        int explore_score = std::numeric_limits<int>::min();
        while (!pending.empty()) {
            int p = pending.front(); pending.pop();
            if (p != head) {
                int friend_distance = nearest_friend(p);
                int score = friend_distance * 100 - distance[p] * 8 - visits[p] * 3;
                int food_score = -distance[p] * 100 + std::min(friend_distance, 10) - visits[p];
                if (tiles[p].pearl && owns_pearl(p, distance[p]) && food_score > pearl_score) {
                    pearl_score = food_score;
                    pearl = p;
                }
                if (score > explore_score) { explore_score = score; explore = p; }
            }
            for (int offset = 0; offset < 4; ++offset) {
                int d = (offset + id + round / 8) % 4;
                int next = destination(p, d);
                if (next < 0 || distance[next] >= 0) continue;
                distance[next] = distance[p] + 1;
                first[next] = p == head ? d : first[p];
                pending.push(next);
            }
        }
        int target = pearl >= 0 ? pearl : explore;
        if (target >= 0) return std::string("MOVE ") + DIR[first[target]];
        if (length >= 4 && units < limit) return "SPLIT " + std::to_string(length - 2);
        for (int d = 0; d < 4; ++d)
            if (destination(head, d) == -2) return std::string("MOVE ") + DIR[d];
        return "MOVE N";
    }

public:
    std::string action() {
        bool signal = should_signal();
        std::string move = body(signal);
        std::uint64_t status = team_status_message(id, length, head % width, head / width, round);
        std::string output = move;
        for (int d = 0; d < 4; ++d) {
            std::uint64_t message = signal && d == facing ? MOVE_ASIDE : status;
            output += "\nSONAR " + std::string(1, DIR[d]) + " " + std::to_string(message);
        }
        return output;
    }
};

int main() {
    Bot bot;
    if (!bot.init()) return 0;
    while (bot.update()) std::cout << bot.action() << "\nENDTURN\n" << std::flush;
}

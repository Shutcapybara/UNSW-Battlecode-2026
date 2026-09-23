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
constexpr std::uint32_t MOVE_ASIDE = 1146242894u; // ASCII "DRGN"
constexpr std::uint32_t FILLER_SONAR = 8008135u;

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

class Bot {
    int width = 0, height = 0, id = 0, limit = 64;
    int round = 0, length = 0, units = 0, head = 0, facing = 0;
    bool asked_to_move = false;
    std::string my_team;
    std::vector<Tile> tiles;
    std::vector<int> visits;
    std::map<std::string, std::vector<Edge>> portals;
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
                        if ((inside || next.reward > 0) && next.reward > best_reward) {
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
    int nearest_friend(int start) const {
        int best = 99;
        int sx = start % width, sy = start / width;
        for (int p = 0; p < static_cast<int>(tiles.size()); ++p) {
            if (!tiles[p].friendly_head || p == head) continue;
            int dx = std::abs(sx - p % width), dy = std::abs(sy - p / width);
            best = std::min(best, std::min(dx, width - dx) + std::min(dy, height - dy));
        }
        return best;
    }
    std::string attack_path() const {
        std::vector<std::string> path(tiles.size());
        std::vector<bool> seen(tiles.size(), false);
        std::queue<int> pending;
        seen[head] = true;
        pending.push(head);
        while (!pending.empty()) {
            int p = pending.front(); pending.pop();
            for (int offset = 0; offset < 4; ++offset) {
                int d = (offset + id + round) % 4;
                int next = destination(p, d, false);
                if (next < 0 || seen[next] ||
                    (tiles[next].occupied && !tiles[next].enemy_head)) continue;
                seen[next] = true;
                path[next] = path[p] + DIR[d];
                if (tiles[next].enemy_head) return path[next];
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
            width < 10 || width > 64 || height < 10 || height > 64) return false;
        if (!field("UNIT_LIMIT", limit)) return false;
        visits.assign(width * height, 0);
        return true;
    }
    bool update() {
        std::string facing_text, text, team, body_facing;
        int count;
        if (!field("ROUND", round) || !field("DIR", facing_text) ||
            !field("LENGTH", length) || !field("UNIT_COUNT", units) ||
            !field("NUM_MSGS", count)) return false;
        facing = direction(facing_text[0]);
        asked_to_move = false;
        for (int i = 0; i < count; ++i) {
            std::uint32_t message;
            if (!line(text)) return false;
            std::istringstream input(text);
            if (!(input >> message)) return false;
            asked_to_move = asked_to_move || message == MOVE_ASIDE;
        }
        tiles.assign(width * height, Tile{});
        portals.clear();
        std::array<int, 49> window{};
        for (int i = 0; i < 49; ++i) {
            int x, y, pearl, countdown;
            if (!line(text)) return false;
            std::istringstream input(text);
            if (!(input >> x >> y >> pearl >> countdown)) return false;
            int p = window[i] = pos(x, y);
            tiles[p].visible = true;
            tiles[p].pearl = pearl != 0;
            tiles[p].countdown = countdown;
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
            if (is_head) {
                tiles[p].dragon_id = dragon;
                tiles[p].facing = direction(body_facing[0]);
                tiles[p].friendly_head = team == my_team;
                tiles[p].enemy_head = team != my_team;
            }
        }
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
        // Preserve a minimum force before trading dragons head-to-head. If the
        // team drops below three survivors, every remaining dragon rebuilds
        // the swarm instead of pursuing an enemy head.
        if (units >= 3) {
            std::string attack = attack_path();
            if (!attack.empty()) {
                int steps = std::min<int>({2, static_cast<int>(attack.size()), length - 1});
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
                int spread = nearest_friend(p) * 100;
                int score = spread - distance[p] * 8 - visits[p] * 3;
                if (tiles[p].pearl && score > pearl_score) { pearl_score = score; pearl = p; }
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
        return body(signal) + "\nSONAR " + std::to_string(signal ? MOVE_ASIDE : FILLER_SONAR);
    }
};

int main() {
    Bot bot;
    if (!bot.init()) return 0;
    while (bot.update()) std::cout << bot.action() << "\nENDTURN\n" << std::flush;
}

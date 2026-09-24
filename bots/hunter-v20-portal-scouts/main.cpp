#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <sstream>
#include <string>
#include <vector>

constexpr int DX[] = {0, 1, 0, -1};
constexpr int DY[] = {-1, 0, 1, 0};
constexpr char DIR[] = "NESW";
constexpr std::uint64_t MOVE_ASIDE = 1146242894u; // ASCII "DRGN"
constexpr std::uint64_t SUMMARY_TAG = UINT64_C(0xA9) << 56;
constexpr std::uint64_t HOTSPOT_TAG = UINT64_C(0xAA) << 56;
constexpr std::uint64_t PORTAL_TAG = UINT64_C(0xAB) << 56;
constexpr std::uint64_t COVERAGE_TAG = UINT64_C(0xAC) << 56;
constexpr std::uint64_t SCOUT_TAG = UINT64_C(0xAD) << 56;
constexpr int HOTSPOT_TTL = 8;
constexpr int SCOUT_CLAIM_TTL = 8;
constexpr int MAX_PORTAL_APPROACH = 8;

struct Tile {
    bool visible = false, pearl = false, occupied = false;
    bool own_body = false;
    int countdown = -1;
    bool friendly_head = false, enemy_head = false;
    int dragon_id = -1, facing = -1, body_direction = -1;
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

struct SharedSummary {
    int team_max = 0, enemy_max = 0, enemy_count = 0, unit_count = 0;
    int observed_round = -1;
};

struct PortalFact {
    int tile = -1, direction = 0, observed_round = -1;
    char symbol = 0;
    bool safe = false;
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
    std::vector<int> hotspot_strength, hotspot_round;
    std::vector<bool> scouted_sectors;
    int sector_columns = 0, sector_rows = 0;
    SharedSummary shared_summary;
    std::map<std::pair<int, int>, PortalFact> portal_facts;
    std::set<std::string> safe_portals;
    std::map<std::string, int> portal_last_visit;
    std::map<int, EnemyMemory> enemies;
    std::map<int, int> visible_friendly_sizes;
    std::map<std::string, std::vector<Edge>> portals;
    int portal_scout_id = -1, portal_scout_round = -1;
    int portal_policy_round = -1;
    bool portal_policy_decision = false;
    mutable bool friend_routes_ready = false;
    mutable std::map<int, std::vector<int>> live_friend_routes;
    mutable std::map<int, std::vector<int>> static_friend_routes;
    mutable std::vector<std::pair<int, int>> nearest_pearl_routes;
    std::string route, trip_portal;
    Edge trip_entry{0, 0, false};
    bool inside = false;
    int expected_head = -1, expected_round = -1;

    int age(int timestamp) const {
        return timestamp < 0 ? 1000000 : (round - timestamp + 1024) % 1024;
    }
    std::uint64_t scout_message() const {
        if (portal_scout_id < 0 || age(portal_scout_round) > SCOUT_CLAIM_TTL)
            return summary_message();
        return SCOUT_TAG | (std::uint64_t(portal_scout_round & 1023) << 46) |
            (std::uint64_t(portal_scout_id & 65535) << 30);
    }
    void update_scout_claim(int sent, int scout_id) {
        int incoming_age = age(sent);
        if (incoming_age > SCOUT_CLAIM_TTL || scout_id < 0 || scout_id > 65535) return;
        int current_age = age(portal_scout_round);
        if (portal_scout_id < 0 || current_age > SCOUT_CLAIM_TTL ||
            incoming_age < current_age ||
            (incoming_age == current_age && scout_id < portal_scout_id)) {
            portal_scout_id = scout_id;
            portal_scout_round = sent;
        }
    }
    std::uint64_t summary_message() const {
        int team_max = length, enemy_max = 0;
        for (const auto& friend_size : visible_friendly_sizes)
            team_max = std::max(team_max, friend_size.second);
        int enemy_count = 0;
        for (const auto& enemy : enemies) {
            enemy_max = std::max(enemy_max, enemy.second.visible_size);
            if (enemy.second.visible_size > 0) ++enemy_count;
        }
        int observed = round;
        if (age(shared_summary.observed_round) <= 20) {
            if (shared_summary.team_max > team_max || shared_summary.enemy_max > enemy_max ||
                shared_summary.enemy_count > enemy_count)
                observed = shared_summary.observed_round;
            team_max = std::max(team_max, shared_summary.team_max);
            enemy_max = std::max(enemy_max, shared_summary.enemy_max);
            enemy_count = std::max(enemy_count, shared_summary.enemy_count);
        }
        return SUMMARY_TAG | (std::uint64_t(observed & 1023) << 46) |
            (std::uint64_t(std::min(team_max, 1023)) << 36) |
            (std::uint64_t(std::min(enemy_max, 1023)) << 26) |
            (std::uint64_t(std::min(units, 255)) << 18) |
            (std::uint64_t(std::min(enemy_count, 255)) << 10);
    }
    std::uint64_t hotspot_message() const {
        std::vector<int> sites;
        for (int p = 0; p < static_cast<int>(hotspot_strength.size()); ++p)
            if (hotspot_strength[p] > 0 && age(hotspot_round[p]) <= HOTSPOT_TTL)
                sites.push_back(p);
        if (sites.empty()) return summary_message();
        auto rank = [&](int a, int b) {
            if (hotspot_strength[a] != hotspot_strength[b])
                return hotspot_strength[a] > hotspot_strength[b];
            return a < b;
        };
        std::size_t count = std::min<std::size_t>(sites.size(), 8);
        std::partial_sort(sites.begin(), sites.begin() + count, sites.end(), rank);
        int p = sites[(round / 4 + id) % count];
        return HOTSPOT_TAG | (std::uint64_t(hotspot_round[p] & 1023) << 46) |
            (std::uint64_t(p % width) << 40) | (std::uint64_t(p / width) << 34) |
            (std::uint64_t(hotspot_strength[p] & 255) << 26);
    }
    std::uint64_t portal_message() const {
        if (portal_facts.empty()) return coverage_message();
        auto it = portal_facts.begin();
        std::advance(it, (round / 4 + id) % portal_facts.size());
        const auto& fact = it->second;
        return PORTAL_TAG | (std::uint64_t(round & 1023) << 46) |
            (std::uint64_t(fact.tile % width) << 40) |
            (std::uint64_t(fact.tile / width) << 34) |
            (std::uint64_t(fact.direction) << 32) |
            (std::uint64_t(static_cast<unsigned char>(fact.symbol)) << 24) |
            (std::uint64_t(fact.safe || safe_portals.count(std::string(1, fact.symbol)) != 0) << 23);
    }
    std::uint64_t coverage_message() const {
        std::vector<int> seen;
        for (int i = 0; i < static_cast<int>(scouted_sectors.size()); ++i)
            if (scouted_sectors[i]) seen.push_back(i);
        if (seen.empty()) return hotspot_message();
        int sector = seen[(round / 4 + id) % seen.size()];
        int x = (sector % sector_columns) * 4;
        int y = (sector / sector_columns) * 4;
        return COVERAGE_TAG | (std::uint64_t(round & 1023) << 46) |
            (std::uint64_t(x) << 40) | (std::uint64_t(y) << 34);
    }

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
    bool is_largest_known() const {
        for (const auto& item : visible_friendly_sizes)
            if (item.second > length) return false;
        return age(shared_summary.observed_round) > 20 || shared_summary.team_max <= length;
    }
    bool has_larger_known_teammate() const {
        for (const auto& item : visible_friendly_sizes)
            if (item.second > length) return true;
        return age(shared_summary.observed_round) <= 20 && shared_summary.team_max > length;
    }
    int local_pearl_opportunity_count() const {
        constexpr int LOCAL_FOOD_RADIUS = 5;
        std::vector<bool> danger = threats();
        std::vector<int> distance(tiles.size(), -1);
        std::queue<int> pending;
        int opportunities = 0;
        distance[head] = 0;
        pending.push(head);
        while (!pending.empty()) {
            int p = pending.front();
            pending.pop();
            int steps = distance[p];
            if (steps > 0 && steps <= LOCAL_FOOD_RADIUS && !tiles[p].occupied &&
                !danger[p] &&
                (tiles[p].pearl ||
                 (tiles[p].countdown >= 0 && tiles[p].countdown < steps)) &&
                owns_pearl(p, steps))
                ++opportunities;
            if (steps == LOCAL_FOOD_RADIUS) continue;
            for (int d = 0; d < 4; ++d) {
                int next = destination(p, d);
                if (next < 0 || danger[next] || distance[next] >= 0) continue;
                distance[next] = steps + 1;
                pending.push(next);
            }
        }
        return opportunities;
    }
    bool has_local_pearl_supply() const {
        // One nearby pearl can feed one dragon, but it should not stall
        // portal scouting for a whole team when the starting area is sparse.
        int required_opportunities = std::max(2, std::min(4, (units + 7) / 8));
        return local_pearl_opportunity_count() >= required_opportunities;
    }
    bool should_explore_portals() {
        if (portal_policy_round == round) return portal_policy_decision;
        portal_policy_round = round;
        portal_policy_decision = false;
        auto decide = [&](bool value) {
            portal_policy_decision = value;
            return value;
        };
        constexpr int MIN_ALIVE_TO_EXPLORE = 4;
        constexpr int MIN_PORTAL_SCOUT_LENGTH = 3;
        // Compact boards put portal exits in immediate contention; portal
        // probes depleted V20 there without adding enough growth to pay back.
        if (width * height <= 625) return decide(false);
        if (units < MIN_ALIVE_TO_EXPLORE) return decide(false);
        if (has_local_pearl_supply()) return decide(false);

        if (portal_scout_id >= 0 && age(portal_scout_round) <= SCOUT_CLAIM_TTL) {
            if (portal_scout_id != id) return decide(false);
            if (age(portal_scout_round) >= SCOUT_CLAIM_TTL / 2)
                portal_scout_round = round;
            return decide(true);
        }

        constexpr int MAX_EXPENDABLE_SCOUT_LENGTH = 6;
        // Keep one mature dragon scouting once the initial force is active;
        // waiting for limit/8 survivors delays access on sparse starting boxes.
        int expendable_team_threshold = std::max(4, limit / 16);
        bool expendable_scout = units >= expendable_team_threshold &&
                                length >= MIN_PORTAL_SCOUT_LENGTH &&
                                length <= MAX_EXPENDABLE_SCOUT_LENGTH;
        if (!expendable_scout) return decide(false);

        // One sonar claim coordinates portal probing. Simultaneous claims are
        // resolved by the lower dragon ID when the claims reach teammates.
        portal_scout_id = id;
        portal_scout_round = round;
        return decide(true);
    }
    int largest_known_team_length() const {
        int largest = length;
        for (const auto& item : visible_friendly_sizes)
            largest = std::max(largest, item.second);
        if (age(shared_summary.observed_round) <= 20)
            largest = std::max(largest, shared_summary.team_max);
        return largest;
    }
    int largest_known_enemy_length() const {
        int largest = 0;
        for (const auto& item : enemies)
            largest = std::max(largest, item.second.visible_size);
        if (age(shared_summary.observed_round) <= 20)
            largest = std::max(largest, shared_summary.enemy_max);
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
        auto& fact = portal_facts[{p, d}];
        fact = {p, d, round, symbol[0],
                safe_portals.count(symbol) != 0 || fact.safe};
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
    // Keep growth routes out of short pockets enclosed by the dragon's own body.
    static constexpr int SURVIVAL_LOOKAHEAD = 6;
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

    struct ContinuationStats {
        int depth = 0;
        std::uint64_t paths = 1;
    };

    ContinuationStats safe_continuations(const Trip& state, int remaining,
                                         const std::vector<bool>& danger) const {
        if (remaining == 0) return {};
        ContinuationStats best;
        bool found = false;
        for (int d = 0; d < 4; ++d) {
            Trip next = state;
            if (!advance(next, d, danger)) continue;
            ContinuationStats tail = safe_continuations(next, remaining - 1, danger);
            int depth = 1 + tail.depth;
            if (!found || depth > best.depth) {
                best = {depth, tail.paths};
                found = true;
            } else if (depth == best.depth) {
                best.paths += tail.paths;
            }
        }
        return best;
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

    std::string plan_trip(const std::vector<bool>& danger) {
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
                        auto previous = portal_last_visit.find(next.portal);
                        bool fresh_route = previous == portal_last_visit.end() ||
                                           round - previous->second > 20;
                        if ((inside || (should_explore_portals() &&
                             (next.reward > 0 || fresh_route))) &&
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
                    (portal->second.size() == 1 ||
                     destination(p, d, false, true) == -2) &&
                    static_cast<int>(path[p].size()) < MAX_PORTAL_APPROACH)
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
        int best = -1;
        int best_depth = -1, best_exits = -1, best_preference = std::numeric_limits<int>::min();
        std::uint64_t best_paths = 0;
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
            ContinuationStats stats = safe_continuations(
                next, SURVIVAL_LOOKAHEAD - 1, danger);
            int preference = nearest_friend(next.trail.back()) - visits[next.trail.back()];
            bool better = best < 0 || stats.depth > best_depth ||
                (stats.depth == best_depth && stats.paths > best_paths) ||
                (stats.depth == best_depth && stats.paths == best_paths && exits > best_exits) ||
                (stats.depth == best_depth && stats.paths == best_paths &&
                 exits == best_exits && preference > best_preference);
            if (better) {
                best = d;
                best_depth = stats.depth;
                best_paths = stats.paths;
                best_exits = exits;
                best_preference = preference;
            }
        }
        return best;
    }

    std::string portal_action() {
        // A portal trip can take longer than the scout lease. Keep the claim
        // alive while its owner is committed to the paired return route.
        if (inside && portal_scout_id == id) portal_scout_round = round;
        auto danger = threats();
        if (head != expected_head || round != expected_round) route.clear();
        if (!route.empty()) {
            Trip check = initial_trip();
            for (char move : route) {
                if (!advance(check, direction(move), danger)) { route.clear(); break; }
            }
        }
        if (route.empty()) route = plan_trip(danger);
        if (route.empty() && !inside && should_explore_portals())
            route = plan_unmatched_portal(danger);
        if (route.empty()) return {};
        int d = direction(route.front());
        const std::string& symbol = tiles[head].edges[d];
        if (symbol != ".") {
            if (!inside) { trip_portal = symbol; trip_entry = edge_at(head, d); inside = true; }
            else { inside = false; safe_portals.insert(symbol); portal_last_visit[symbol] = round; }
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
    bool exact_enemy_length(int enemy_head, int enemy_id, int& size) const {
        int head_direction = tiles[enemy_head].facing;
        if (head_direction < 0) return false;
        int p = enemy_head;
        size = 1;
        std::vector<bool> seen(tiles.size(), false);
        seen[p] = true;
        int next = destination(p, (head_direction + 2) % 4, false, true);
        if (next < 0) return false;
        for (int step = 0; step < width * height; ++step) {
            if (next == -1) return true;
            if (next < 0 || !tiles[next].visible || seen[next]) return false;
            if (tiles[next].dragon_id != enemy_id) return true;
            if (tiles[next].body_direction < 0) return false;
            p = next;
            seen[p] = true;
            ++size;
            next = destination(p, (tiles[p].body_direction + 2) % 4, false, true);
        }
        return false;
    }
    bool close_to_other_enemy(int p, int ignored_id) const {
        for (int q = 0; q < static_cast<int>(tiles.size()); ++q) {
            if (!tiles[q].enemy_head || tiles[q].dragon_id == ignored_id) continue;
            int dx = std::abs(p % width - q % width);
            int dy = std::abs(p / width - q / width);
            if (std::min(dx, width - dx) + std::min(dy, height - dy) <= 1)
                return true;
        }
        return false;
    }
    std::string boost_surround_action() const {
        constexpr int MIN_SIZE_ADVANTAGE_AFTER_BOOST = 4;
        if (length < 8) return {};
        int best_score = std::numeric_limits<int>::min();
        std::string best;
        for (int enemy = 0; enemy < static_cast<int>(tiles.size()); ++enemy) {
            if (!tiles[enemy].enemy_head) continue;
            int enemy_id = tiles[enemy].dragon_id;
            if (enemy_id <= id) continue;
            int enemy_size = 0;
            if (!exact_enemy_length(enemy, enemy_id, enemy_size) ||
                length - 1 - enemy_size < MIN_SIZE_ADVANTAGE_AFTER_BOOST)
                continue;

            std::vector<int> sides;
            bool fully_visible = true;
            for (int d = 0; d < 4; ++d) {
                int q = destination(enemy, d, false, true);
                if (q == -2) { fully_visible = false; break; }
                if (q >= 0 && !tiles[q].occupied &&
                    std::find(sides.begin(), sides.end(), q) == sides.end())
                    sides.push_back(q);
            }
            if (!fully_visible || sides.size() < 3) continue;

            // Three sides can be occupied in a compact six-step loop. Longer
            // loops spend more body segments and often abandon useful routes.
            const int max_steps = std::min(length - 1, 6);
            std::vector<bool> visited(tiles.size(), false);
            std::vector<int> route, route_positions;
            visited[head] = true;
            std::string candidate;
            std::function<void(int, int, int)> search = [&](int p, int previous,
                                                            int depth) {
                if (depth >= 6) {
                    int post_size = length - depth + 1;
                    int first_retained_index = std::max(0, depth - post_size);
                    int occupied_sides = 0;
                    for (int i = first_retained_index; i < static_cast<int>(route_positions.size()); ++i)
                        if (std::find(sides.begin(), sides.end(), route_positions[i]) != sides.end())
                            ++occupied_sides;
                    const int dx = std::abs(p % width - enemy % width);
                    const int dy = std::abs(p / width - enemy / width);
                    const int distance = std::min(dx, width - dx) + std::min(dy, height - dy);
                    if (occupied_sides >= 3 && distance > 1 && post_size >= 6 &&
                        post_size - enemy_size >= MIN_SIZE_ADVANTAGE_AFTER_BOOST) {
                        int safe_exits = 0;
                        for (int d = 0; d < 4; ++d) {
                            if (tiles[p].edges[d] != ".") continue;
                            int q = destination(p, d, false, false);
                            if (q < 0 || q == head || visited[q] || tiles[q].occupied ||
                                close_to_other_enemy(q, enemy_id)) continue;
                            ++safe_exits;
                        }
                        if (safe_exits >= 2) {
                            int score = enemy_size * 100 + safe_exits * 10 - depth;
                            if (score > best_score) {
                                best_score = score;
                                candidate.clear();
                                for (int d : route) candidate += DIR[d];
                                best = candidate;
                            }
                        }
                    }
                }
                if (depth >= max_steps || length - depth - enemy_size < 1) return;
                for (int d = 0; d < 4; ++d) {
                    if (depth > 0 && d == (previous + 2) % 4) continue;
                    if (tiles[p].edges[d] != ".") continue;
                    int q = destination(p, d, false, false);
                    if (q < 0 || visited[q] || tiles[q].occupied || !tiles[q].visible || q == enemy)
                        continue;
                    visited[q] = true;
                    route.push_back(d);
                    route_positions.push_back(q);
                    search(q, d, depth + 1);
                    route_positions.pop_back();
                    route.pop_back();
                    visited[q] = false;
                }
            };
            search(head, -1, 0);
        }
        return best;
    }
    std::string boost_trap_action() const {
        constexpr int MIN_SIZE_ADVANTAGE_AFTER_BOOST = 3;
        if (length < 4) return {};
        int best_score = std::numeric_limits<int>::min();
        std::string best;
        for (int enemy = 0; enemy < static_cast<int>(tiles.size()); ++enemy) {
            if (!tiles[enemy].enemy_head) continue;
            int enemy_id = tiles[enemy].dragon_id;
            // Only heads that have not acted this round can be constrained now.
            if (enemy_id <= id) continue;
            int enemy_size = 0;
            if (!exact_enemy_length(enemy, enemy_id, enemy_size) ||
                length - 1 - enemy_size < MIN_SIZE_ADVANTAGE_AFTER_BOOST)
                continue;

            std::vector<int> escapes;
            bool fully_visible = true;
            for (int d = 0; d < 4; ++d) {
                int q = destination(enemy, d, false, true);
                if (q == -2) { fully_visible = false; break; }
                if (q >= 0 && !tiles[q].occupied) escapes.push_back(q);
            }
            if (!fully_visible || escapes.size() < 2) continue;

            for (int first = 0; first < 4; ++first) {
                if (tiles[head].edges[first] != ".") continue;
                int middle = destination(head, first);
                if (middle < 0) continue;
                for (int second = 0; second < 4; ++second) {
                    if (second == (first + 2) % 4 || tiles[middle].edges[second] != ".") continue;
                    int finish = destination(middle, second);
                    if (finish < 0 || finish == head || finish == middle) continue;

                    // The first landing becomes a new body segment. A useful
                    // boost must close an escape and leave room for our next move.
                    if (std::find(escapes.begin(), escapes.end(), middle) == escapes.end()) continue;
                    bool enemy_can_hit_head = false;
                    for (int d = 0; d < 4; ++d)
                        enemy_can_hit_head |= destination(enemy, d, false, true) == finish;
                    if (enemy_can_hit_head || static_cast<int>(escapes.size()) - 1 > 1) continue;

                    int safe_exits = 0;
                    for (int d = 0; d < 4; ++d) {
                        if (tiles[finish].edges[d] != ".") continue;
                        int q = destination(finish, d, false, false);
                        if (q < 0 || q == head || q == middle || q == finish || tiles[q].occupied)
                            continue;
                        if (close_to_other_enemy(q, enemy_id)) continue;
                        ++safe_exits;
                    }
                    if (safe_exits < 2) continue;

                    int score = enemy_size * 100 + safe_exits * 10 - static_cast<int>(escapes.size());
                    if (score > best_score) {
                        best_score = score;
                        best = std::string(1, DIR[first]) + DIR[second];
                    }
                }
            }
        }
        return best;
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
        hotspot_strength.assign(width * height, 0);
        hotspot_round.assign(width * height, -1);
        sector_columns = (width + 3) / 4;
        sector_rows = (height + 3) / 4;
        scouted_sectors.assign(sector_columns * sector_rows, false);
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
        for (int p = 0; p < static_cast<int>(hotspot_strength.size()); ++p) {
            if (age(hotspot_round[p]) > HOTSPOT_TTL) {
                hotspot_strength[p] = 0;
                hotspot_round[p] = -1;
            }
        }
        for (int i = 0; i < count; ++i) {
            std::uint64_t message;
            if (!line(text)) return false;
            std::istringstream input(text);
            if (!(input >> message)) return false;
            asked_to_move = asked_to_move || message == MOVE_ASIDE;
            std::uint64_t tag = message & (UINT64_C(0xFF) << 56);
            if (tag == SUMMARY_TAG) {
                int sent = static_cast<int>((message >> 46) & 1023);
                int delay = (round - sent + 1024) % 1024;
                if (delay <= 20) {
                    SharedSummary incoming{
                        static_cast<int>((message >> 36) & 1023),
                        static_cast<int>((message >> 26) & 1023),
                        static_cast<int>((message >> 10) & 255),
                        static_cast<int>((message >> 18) & 255), round - delay};
                    if (incoming.observed_round > shared_summary.observed_round)
                        shared_summary = incoming;
                    else if (incoming.observed_round == shared_summary.observed_round) {
                        shared_summary.team_max = std::max(shared_summary.team_max, incoming.team_max);
                        shared_summary.enemy_max = std::max(shared_summary.enemy_max, incoming.enemy_max);
                        shared_summary.enemy_count = std::max(shared_summary.enemy_count, incoming.enemy_count);
                    }
                }
            } else if (tag == HOTSPOT_TAG) {
                int sent = static_cast<int>((message >> 46) & 1023);
                int x = static_cast<int>((message >> 40) & 63);
                int y = static_cast<int>((message >> 34) & 63);
                if (age(sent) <= HOTSPOT_TTL && x < width && y < height) {
                    int p = pos(x, y);
                    int strength = static_cast<int>((message >> 26) & 255);
                    if (age(sent) < age(hotspot_round[p])) {
                        hotspot_strength[p] = strength;
                        hotspot_round[p] = sent;
                    } else if (sent == hotspot_round[p]) {
                        hotspot_strength[p] = std::max(hotspot_strength[p], strength);
                    }
                }
            } else if (tag == SCOUT_TAG) {
                int sent = static_cast<int>((message >> 46) & 1023);
                int scout_id = static_cast<int>((message >> 30) & 65535);
                update_scout_claim(sent, scout_id);
            } else if (tag == PORTAL_TAG) {
                int sent = static_cast<int>((message >> 46) & 1023);
                int x = static_cast<int>((message >> 40) & 63);
                int y = static_cast<int>((message >> 34) & 63);
                int d = static_cast<int>((message >> 32) & 3);
                char symbol = static_cast<char>((message >> 24) & 255);
                bool safe = ((message >> 23) & 1) != 0;
                if ((round - sent + 1024) % 1024 <= 80 && x < width && y < height &&
                    symbol != '.' && symbol != 'w' && symbol >= '!' && symbol <= '~') {
                    int p = pos(x, y);
                    std::string name(1, symbol);
                    if (known_edges[p][d] != "." && known_edges[p][d] != name) continue;
                    known_edges[p][d] = name;
                    known_edge[p] = true;
                    auto& fact = portal_facts[{p, d}];
                    fact = {p, d, round, symbol, safe || fact.safe};
                    if (safe) safe_portals.insert(name);
                }
            } else if (tag == COVERAGE_TAG) {
                int sent = static_cast<int>((message >> 46) & 1023);
                int x = static_cast<int>((message >> 40) & 63);
                int y = static_cast<int>((message >> 34) & 63);
                if ((round - sent + 1024) % 1024 <= 80 && x < width && y < height)
                    scouted_sectors[(y / 4) * sector_columns + x / 4] = true;
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
            scouted_sectors[(y / 4) * sector_columns + x / 4] = true;
            tiles[p].pearl = pearl != 0;
            tiles[p].countdown = countdown;
            known_pearls[p] = {tiles[p].pearl, countdown, round};
            int strength = 0;
            if (tiles[p].pearl) {
                strength = 12;
            } else if (countdown >= 0 && countdown <= 8) {
                strength = std::max(1, 6 - countdown / 2);
            }
            if (strength > 0) {
                hotspot_strength[p] = strength;
                hotspot_round[p] = round;
            } else {
                hotspot_strength[p] = 0;
                hotspot_round[p] = -1;
            }
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
            tiles[p].body_direction = direction(body_facing[0]);
            tiles[p].own_body = team == my_team && dragon == id;
            if (tiles[p].pearl) {
                hotspot_strength[p] = 0;
                hotspot_round[p] = -1;
            }
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
        int best_move = -1;
        int best_target_score = std::numeric_limits<int>::min();
        std::uint64_t best_paths = 0;
        for (int d = 0; d < 4; ++d) {
            if (tiles[head].edges[d] != ".") continue;
            Trip candidate = initial_trip();
            if (!advance(candidate, d, danger)) continue;
            ContinuationStats stats = safe_continuations(
                candidate, SURVIVAL_LOOKAHEAD - 1, danger);
            if (stats.depth != SURVIVAL_LOOKAHEAD - 1) continue;

            // Search independently from each safe first move. A blocked or
            // unsafe route to one pearl must not hide another viable route.
            std::vector<int> distance(tiles.size(), -1);
            std::queue<int> pending;
            int start = candidate.trail.back();
            distance[start] = 1;
            pending.push(start);
            while (!pending.empty()) {
                int p = pending.front(); pending.pop();
                if (tiles[p].pearl ||
                    (tiles[p].countdown >= 0 && tiles[p].countdown < distance[p])) {
                    int score = -distance[p] * 100 + std::min(nearest_friend(p), 10) -
                                visits[p] + 20;
                    if (score > best_target_score ||
                        (score == best_target_score && stats.paths > best_paths)) {
                        best_target_score = score;
                        best_paths = stats.paths;
                        best_move = d;
                    }
                }
                for (int e = 0; e < 4; ++e) {
                    int next = destination(p, e);
                    if (next < 0 || danger[next] || distance[next] >= 0) continue;
                    // Do not grow into a pocket with no clear onward move.
                    bool onward = false;
                    for (int f = 0; f < 4; ++f) {
                        int exit = destination(next, f);
                        if (exit >= 0 && exit != p && !danger[exit]) onward = true;
                    }
                    if (!onward) continue;
                    distance[next] = distance[p] + 1;
                    pending.push(next);
                }
            }
        }
        if (best_move >= 0) return std::string("MOVE ") + DIR[best_move];
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
        if (!inside && !should_focus_growth() && units >= 3) {
            std::string surround = boost_surround_action();
            if (!surround.empty()) return "MOVE " + surround;
            std::string trap = boost_trap_action();
            if (!trap.empty()) return "MOVE " + trap;
        }
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
        std::vector<int> hotspot_distance(tiles.size(), 99);
        std::queue<int> hotspot_queue;
        for (int p = 0; p < static_cast<int>(hotspot_strength.size()); ++p) {
            if (hotspot_strength[p] == 0 || age(hotspot_round[p]) > HOTSPOT_TTL) continue;
            hotspot_distance[p] = std::max(0, 12 - hotspot_strength[p]) / 2;
            hotspot_queue.push(p);
        }
        while (!hotspot_queue.empty()) {
            int p = hotspot_queue.front(); hotspot_queue.pop();
            for (int d = 0; d < 4; ++d) {
                int q = pos(p % width + DX[d], p / width + DY[d]);
                if (hotspot_distance[q] <= hotspot_distance[p] + 1) continue;
                hotspot_distance[q] = hotspot_distance[p] + 1;
                hotspot_queue.push(q);
            }
        }
        std::vector<int> unknown_distance(tiles.size(), 99);
        std::queue<int> unknown_queue;
        for (int sector = 0; sector < static_cast<int>(scouted_sectors.size()); ++sector) {
            if (scouted_sectors[sector]) continue;
            int x = std::min(width - 1, (sector % sector_columns) * 4 + 2);
            int y = std::min(height - 1, (sector / sector_columns) * 4 + 2);
            int p = pos(x, y);
            unknown_distance[p] = 0;
            unknown_queue.push(p);
        }
        while (!unknown_queue.empty()) {
            int p = unknown_queue.front(); unknown_queue.pop();
            for (int d = 0; d < 4; ++d) {
                int q = pos(p % width + DX[d], p / width + DY[d]);
                if (unknown_distance[q] <= unknown_distance[p] + 1) continue;
                unknown_distance[q] = unknown_distance[p] + 1;
                unknown_queue.push(q);
            }
        }
        std::queue<int> pending;
        distance[head] = 0;
        pending.push(head);
        int pearl = -1, explore = -1, pearl_score = std::numeric_limits<int>::min();
        int explore_score = std::numeric_limits<int>::min();
        while (!pending.empty()) {
            int p = pending.front(); pending.pop();
            if (p != head) {
                int friend_distance = nearest_friend(p);
                int frontier = 0;
                for (int d = 0; d < 4; ++d) {
                    int q = pos(p % width + DX[d], p / width + DY[d]);
                    if (!tiles[q].visible && known_edges[p][d] != "w") ++frontier;
                }
                int hotspot_pull = std::max(0, 10 - hotspot_distance[p]) * 35;
                int scout_pull = std::max(0, 12 - unknown_distance[p]) * 25;
                int score = friend_distance * 60 + frontier * 80 + hotspot_pull + scout_pull -
                            distance[p] * 8 - visits[p] * 3;
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
        std::uint64_t status = summary_message();
        std::string output = move;
        for (int d = 0; d < 4; ++d) {
            int slot = (round + d) % 4;
            std::uint64_t message = slot == 0 ? status :
                slot == 1 ? scout_message() :
                slot == 2 ? hotspot_message() :
                round % 2 == 0 ? portal_message() : coverage_message();
            if (signal && d == facing) message = MOVE_ASIDE;
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

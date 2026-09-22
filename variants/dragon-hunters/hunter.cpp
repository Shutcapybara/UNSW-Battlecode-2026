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

struct Tile {
    bool visible = false, pearl = false, occupied = false;
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
    int destination(int p, int d, bool check_body = true) const {
        const std::string& symbol = tiles[p].edges[d];
        if (symbol == "w") return -1;
        int next = pos(p % width + DX[d], p / width + DY[d]);
        if (symbol != ".") {
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
    std::string action() const {
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

        bool signal = should_signal();
        if (asked_to_move) {
            int move = best_spread_move(true);
            if (move >= 0) return std::string("MOVE ") + DIR[move];
        }
        if (length >= 4 && units < limit) {
            std::string result = "SPLIT 2";
            if (signal) result += "\nSONAR " + std::to_string(MOVE_ASIDE);
            return result;
        }
        if (signal && destination(head, facing) >= 0)
            return std::string("MOVE ") + DIR[facing] + "\nSONAR " + std::to_string(MOVE_ASIDE);

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
};

int main() {
    Bot bot;
    if (!bot.init()) return 0;
    while (bot.update()) std::cout << bot.action() << "\nENDTURN\n" << std::flush;
}

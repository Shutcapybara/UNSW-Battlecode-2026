#include <array>
#include <iostream>
#include <map>
#include <queue>
#include <sstream>
#include <string>
#include <vector>

// Battlecode wire protocol 2.1.0. Directions are clockwise from north.
constexpr int DX[] = {0, 1, 0, -1};
constexpr int DY[] = {-1, 0, 1, 0};
constexpr char DIR[] = "NESW";
struct Tile {
    bool visible = false, pearl = false, occupied = false;
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
    int round = 0, length = 0, units = 0, head = 0;
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
    int pos(int x, int y) const {
        return ((y % height + height) % height) * width + (x % width + width) % width;
    }
    Edge edge_at(int p, int d) const {
        int x = p % width, y = p / width;
        int anchor = pos(x + (d == 1), y + (d == 2));
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
    // -1 is blocked; -2 is a portal whose exit cannot be verified this turn.
    int destination(int p, int d) const {
        const auto& symbol = tiles[p].edges[d];
        if (symbol == "w") return -1;
        int next = pos(p % width + DX[d], p / width + DY[d]);
        if (symbol != ".") {
            auto found = portals.find(symbol);
            if (found == portals.end() || found->second.size() != 2) return -2;
            Edge entry = edge_at(p, d);
            Edge exit = found->second[0] == entry ? found->second[1] : found->second[0];
            if (exit.horizontal != entry.horizontal) return -2;
            next = pos(exit.x - (d == 3), exit.y - (d == 0));
        }
        if (!tiles[next].visible) return -2;
        return tiles[next].occupied ? -1 : next;
    }

public:
    bool init() {
        std::string team, text, key;
        if (!field("ID", id) || !field("TEAM", team) || !line(text)) return false;
        std::istringstream input(text);
        if (!(input >> key >> width >> height) || key != "MAP" ||
            width < 10 || width > 64 || height < 10 || height > 64) return false;
        if (!field("UNIT_LIMIT", limit)) return false;
        visits.assign(width * height, 0);
        return true;
    }
    bool update() {
        std::string facing, text, team;
        int count;
        if (!field("ROUND", round) || !field("DIR", facing) ||
            !field("LENGTH", length) || !field("UNIT_COUNT", units) ||
            !field("NUM_MSGS", count)) return false;
        for (int i = 0; i < count; ++i) if (!line(text)) return false;
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
            if (!(input >> team >> dragon >> x >> y >> facing >> is_head)) return false;
            tiles[pos(x, y)].occupied = true;
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
        // BFS finds the closest reachable visible pearl, respecting wrapping,
        // kelp, all bodies (including our tail), and verifiable portal exits.
        std::vector<int> distance(tiles.size(), -1), first(tiles.size(), -1);
        std::queue<int> queue;
        distance[head] = 0;
        queue.push(head);
        int target = -1, explore = -1, best_score = -1000000000;
        while (!queue.empty()) {
            int p = queue.front(); queue.pop();
            if (p != head) {
                if (tiles[p].pearl && target < 0) target = p;
                int exits = 0;
                for (int d = 0; d < 4; ++d) if (destination(p, d) >= 0) ++exits;
                int score = -visits[p] * 100 + distance[p] * 3 + exits * 2;
                if (score > best_score) { best_score = score; explore = p; }
            }
            // Rotate tie breaking across dragons and rounds to avoid fixed bias.
            for (int offset = 0; offset < 4; ++offset) {
                int d = (offset + id + round / 12) % 4;
                int next = destination(p, d);
                if (next < 0 || distance[next] >= 0) continue;
                distance[next] = distance[p] + 1;
                first[next] = p == head ? d : first[p];
                queue.push(next);
            }
        }
        if (target >= 0) return std::string("MOVE ") + DIR[first[target]];
        if (explore >= 0) return std::string("MOVE ") + DIR[first[explore]];
        // No known safe move: preserve all but two segments in the child.
        if (length >= 4 && units < limit) return "SPLIT " + std::to_string(length - 2);
        // If splitting is illegal, an unseen portal exit is our last chance.
        for (int d = 0; d < 4; ++d)
            if (destination(head, d) == -2) return std::string("MOVE ") + DIR[d];
        // A fully trapped, unsplittable dragon cannot survive any legal action.
        return "MOVE N";
    }
};

int main() {
    Bot bot;
    if (!bot.init()) return 0;
    while (bot.update()) std::cout << bot.action() << "\nENDTURN\n" << std::flush;
}

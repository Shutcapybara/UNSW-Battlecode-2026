#include <array>
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <sstream>
#include <string>
#include <vector>

// Battlecode wire protocol 2.1.0: the engine sends text through stdin and
// receives one action through stdout each turn. Each dragon runs its own bot.
// Direction indexes are 0 = north, 1 = east, 2 = south, 3 = west.
// Map y coordinates increase downward, so north subtracts one from y.
constexpr int DX[] = {0, 1, 0, -1};
constexpr int DY[] = {-1, 0, 1, 0};
constexpr char DIR[] = "NESW";
struct Tile {
    // Only current-turn vision is trusted for pearls and collision checks.
    bool visible = false, pearl = false, occupied = false;
    bool dragon_head = false;
    bool enemy_head = false;
    // Edges use the same NESW order: "." = open, "w" = kelp,
    // otherwise the string is a portal ID shared by two map edges.
    std::array<std::string, 4> edges = {".", ".", ".", "."};
};
struct Edge {
    // Canonical edge position: north side of (x,y) for horizontal edges,
    // west side for vertical edges. This identifies an edge from either side.
    int x, y;
    bool horizontal;
    bool operator==(const Edge& other) const {
        return x == other.x && y == other.y && horizontal == other.horizontal;
    }
};

class Bot {
    // Setup information stays constant throughout this dragon's lifetime.
    int width = 0, height = 0, id = 0, limit = 64;
    int round = 0, length = 0, units = 0, head = 0;
    int children_created = 0;
    std::string my_team;
    // Positions such as head are flattened indexes: y * width + x.
    std::vector<Tile> tiles;
    // Visits persist between turns, but are not shared with split children.
    std::vector<int> visits;
    // Portal ID -> distinct physical edges visible this turn.
    std::map<std::string, std::vector<Edge>> portals;

    // Ignore blank lines and protocol comments. EOF means the bot should stop.
    static bool line(std::string& value) {
        while (std::getline(std::cin, value)) {
            value = value.substr(0, value.find('#'));
            if (value.find_first_not_of(" \t\r") != std::string::npos) return true;
        }
        return false;
    }
    // Read a labelled value (for example "LENGTH 6") and verify the label.
    template<class T> static bool field(const std::string& expected, T& value) {
        std::string text, key;
        if (!line(text)) return false;
        std::istringstream input(text);
        return bool(input >> key >> value) && key == expected;
    }
    int pos(int x, int y) const {
        // Both map axes wrap. The extra addition handles negative coordinates
        // because C++'s remainder can be negative when moving north or west.
        return ((y % height + height) % height) * width + (x % width + width) % width;
    }
    Edge edge_at(int p, int d) const {
        int x = p % width, y = p / width;
        // East is the next tile's west edge; south is its north edge.
        int anchor = pos(x + (d == 1), y + (d == 2));
        return {anchor % width, anchor / width, d % 2 == 0};
    }
    void set_edge(int p, int d, const std::string& symbol) {
        tiles[p].edges[d] = symbol;
        if (symbol == "." || symbol == "w") return;
        Edge edge = edge_at(p, d);
        auto& ends = portals[symbol];
        // Two neighbouring tiles report the same edge: count it only once.
        for (const auto& end : ends) if (end == edge) return;
        ends.push_back(edge);
    }
    // Return a safe destination index, -1 for a known collision, or -2 for
    // an unknown destination (outside vision or an unverified portal exit).
    int destination(int p, int d, bool check_body = true) const {
        const auto& symbol = tiles[p].edges[d];
        if (symbol == "w") return -1;
        int next = pos(p % width + DX[d], p / width + DY[d]);
        if (symbol != ".") {
            auto found = portals.find(symbol);
            if (found == portals.end() || found->second.size() != 2) return -2;
            Edge entry = edge_at(p, d);
            Edge exit = found->second[0] == entry ? found->second[1] : found->second[0];
            if (exit.horizontal != entry.horizontal) return -2;
            // Keep the travel direction through a portal. Going west/north
            // exits on the tile just before the partner edge's anchor.
            next = pos(exit.x - (d == 3), exit.y - (d == 0));
        }
        if (!tiles[next].visible) return -2;
        // Even our own tail is blocked: collisions happen before it moves.
        return check_body && tiles[next].occupied ? -1 : next;
    }
    std::vector<int> threats() const {
        std::vector<int> danger(tiles.size(), 0);
        // Predict turns and short sprints from every other visible head.
        // These scores influence movement only, never whether we split.
        for (int origin = 0; origin < static_cast<int>(tiles.size()); ++origin) {
            if (!tiles[origin].dragon_head || origin == head) continue;
            for (int d = 0; d < 4; ++d) {
                int next = destination(origin, d, false);
                if (next < 0 || (tiles[next].occupied && next != head)) continue;
                danger[next] += 100;
                if (next == head) continue;
                for (int turn = 0; turn < 4; ++turn) {
                    int second = destination(next, turn, false);
                    if (second < 0 || (tiles[second].occupied && second != head)) continue;
                    danger[second] += 20;
                }
            }
        }
        return danger;
    }
    std::vector<int> enemy_distance() const {
        // Multi-source search measures approach distance through actual open
        // edges, rather than straight-line distance through kelp or bodies.
        std::vector<int> distance(tiles.size(), 1000);
        std::queue<int> pending;
        for (int p = 0; p < static_cast<int>(tiles.size()); ++p) {
            if (tiles[p].enemy_head) { distance[p] = 0; pending.push(p); }
        }
        while (!pending.empty()) {
            int p = pending.front(); pending.pop();
            for (int d = 0; d < 4; ++d) {
                int next = destination(p, d);
                if (next < 0 || distance[next] <= distance[p] + 1) continue;
                distance[next] = distance[p] + 1;
                pending.push(next);
            }
        }
        return distance;
    }
    int buffer_penalty(int distance) const {
        // Beyond four steps there is no reward for fleeing further from food.
        return std::max(0, 4 - distance) * 5;
    }
    bool sprint_has_room(int first, int finish, const std::vector<int>& danger) const {
        // Keep the first step occupied as the new neck. Conservatively retain
        // every current body tile, so neither step relies on a vacating tail.
        std::vector<bool> seen(tiles.size(), false);
        std::queue<int> pending;
        seen[finish] = true;
        pending.push(finish);
        int room = 1;
        bool safe_exit = false;
        for (int d = 0; d < 4; ++d) {
            int next = destination(finish, d);
            if (next >= 0 && next != first && next != finish && danger[next] == 0)
                safe_exit = true;
        }
        if (!safe_exit) return false;
        const int required = std::min(length, 6);
        while (!pending.empty() && room < required) {
            int p = pending.front(); pending.pop();
            for (int d = 0; d < 4; ++d) {
                int next = destination(p, d);
                if (next < 0 || next == first || seen[next]) continue;
                seen[next] = true;
                ++room;
                pending.push(next);
            }
        }
        return room >= required;
    }

public:
    bool init() {
        // Read the one-time setup block, including the team's split limit.
        std::string team, text, key;
        if (!field("ID", id) || !field("TEAM", team) || !line(text)) return false;
        my_team = team;
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
        // We do not use sonar, but must consume its lines to keep input aligned.
        for (int i = 0; i < count; ++i) if (!line(text)) return false;
        // Discard old observations: dragons and pearls may have moved/changed.
        tiles.assign(width * height, Tile{});
        portals.clear();
        std::array<int, 49> window{};
        // The engine sends a 7x7 square in row order, with wrapped coordinates.
        // window maps each local view position to its absolute board index.
        for (int i = 0; i < 49; ++i) {
            int x, y, pearl, countdown;
            if (!line(text)) return false;
            std::istringstream input(text);
            if (!(input >> x >> y >> pearl >> countdown)) return false;
            // Spawn countdowns are read but this strategy targets existing pearls.
            int p = window[i] = pos(x, y);
            tiles[p].visible = true;
            tiles[p].pearl = pearl != 0;
        }
        head = window[24]; // Centre of the view: row 3, column 3 (3 * 7 + 3).
        ++visits[head];
        if (!field("DRAGON_BODIES", count)) return false;
        // All visible body segments are obstacles, regardless of team or ID.
        for (int i = 0; i < count; ++i) {
            int dragon, x, y, is_head;
            if (!line(text)) return false;
            std::istringstream input(text);
            if (!(input >> team >> dragon >> x >> y >> facing >> is_head)) return false;
            tiles[pos(x, y)].occupied = true;
            tiles[pos(x, y)].dragon_head = is_head != 0;
            tiles[pos(x, y)].enemy_head = is_head != 0 && team != my_team;
            // A spawn location under a body is not collectible. Exclude it
            // explicitly, including our own head and tail. Fresh vision next
            // turn can make this tile a target again once it is clear.
            tiles[pos(x, y)].pearl = false;
        }
        // Horizontal boundaries form 8 rows of 7 edges. Interior boundaries
        // are both the northern tile's south edge and southern tile's north edge.
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
        // Vertical boundaries form 7 rows of 8 edges; likewise record both sides.
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
    std::string action() {
        // Each new process (including a split child) starts with zero children.
        // Preserve the current fry-v06-one-child policy. The engine allows one action
        // per turn, so a reproduction turn cannot also contain an escape move.
        if (children_created < 1 && length >= 4 && units < limit) {
            ++children_created;
            return "SPLIT 2";
        }
        const auto danger = threats();
        const auto distance_to_enemy = enemy_distance();
        std::array<int, 4> risk{};
        int lowest_risk = 1000000;
        bool has_escape = false;
        int lowest_threat = 1000000;
        for (int d = 0; d < 4; ++d) {
            risk[d] = 1000000;
            int next = destination(head, d);
            if (next < 0) continue;
            bool escape = false;
            for (int turn = 0; turn < 4; ++turn) {
                int onward = destination(next, turn);
                // Only actual obstacles count toward the split decision.
                // A predicted enemy move must not turn an open exit into a trap.
                if (onward >= 0 ||
                    (onward == -2 && tiles[next].edges[turn] == ".")) escape = true;
            }
            has_escape = has_escape || escape;
            lowest_threat = std::min(lowest_threat, danger[next]);
            risk[d] = danger[next] + buffer_penalty(distance_to_enemy[next]) + (escape ? 0 : 40);
            if (risk[d] < lowest_risk) lowest_risk = risk[d];
        }
        // Spend one segment only when every ordinary move is threatened and a
        // two-step route ends beyond those threats. Other dragons do not act
        // between these steps, but walls/bodies must be checked on both steps.
        std::string sprint;
        int sprint_score = 1000000;
        if (lowest_threat > 0 && lowest_threat < 1000000) {
            for (int d = 0; d < 4; ++d) {
                int first = destination(head, d);
                if (first < 0 || length + int(tiles[first].pearl) < 3) continue;
                for (int second_dir = 0; second_dir < 4; ++second_dir) {
                    int finish = destination(first, second_dir);
                    if (finish < 0 || finish == first || danger[finish] != 0) continue;
                    if (!sprint_has_room(first, finish, danger)) continue;
                    int score = buffer_penalty(distance_to_enemy[finish]);
                    if (score < sprint_score) {
                        sprint_score = score;
                        sprint = std::string("MOVE ") + DIR[d] + DIR[second_dir];
                    }
                }
            }
        }
        if (!sprint.empty()) return sprint;
        // Preserve early splitting for physical dead ends, independently of
        // nearby heads. If all exits are merely threatened, keep moving.
        if (!has_escape && length >= 4 && units < limit)
            return "SPLIT " + std::to_string(length - 2);

        // BFS finds the closest reachable visible pearl, respecting wrapping,
        // kelp, all bodies (including our tail), and verifiable portal exits.
        // Breadth-first search expands positions in increasing step count.
        // distance == -1 means unvisited; first stores the initial direction
        // along each route so we can act without reconstructing the whole path.
        std::vector<int> distance(tiles.size(), -1), first(tiles.size(), -1);
        std::queue<int> queue;
        distance[head] = 0;
        queue.push(head);
        int target = -1, explore = -1, best_score = -1000000000;
        while (!queue.empty()) {
            int p = queue.front(); queue.pop();
            if (p != head) {
                // The first pearl removed from the queue has a shortest route.
                if (tiles[p].pearl && target < 0) target = p;
                int exits = 0;
                for (int d = 0; d < 4; ++d) if (destination(p, d) >= 0) ++exits;
                // Exploration favours less-visited destinations, with bonuses
                // for distance and open exits. This is a heuristic, not proof
                // that a route will remain safe after other dragons act.
                int score = -visits[p] * 100 + distance[p] * 3 + exits * 2;
                if (score > best_score) { best_score = score; explore = p; }
            }
            // Rotate tie breaking across dragons and rounds to avoid fixed bias.
            for (int offset = 0; offset < 4; ++offset) {
                int d = (offset + id + round / 12) % 4;
                // Prefer the least threatened legal direction over a pearl.
                if (p == head && risk[d] != lowest_risk) continue;
                int next = destination(p, d);
                if (next < 0 || distance[next] >= 0) continue;
                distance[next] = distance[p] + 1;
                // Inherit the first step of the path as the search moves outward.
                first[next] = p == head ? d : first[p];
                queue.push(next);
            }
        }
        // Commit only one step, then reconsider with fresh vision next turn.
        // Bodies are treated as stationary during the search; no future moves
        // or tail movement are simulated. Pearls take priority over exploration.
        if (target >= 0) return std::string("MOVE ") + DIR[first[target]];
        if (explore >= 0) return std::string("MOVE ") + DIR[first[explore]];
        // No known safe move: preserve all but two segments in the child.
        // Both parent and child must have at least two segments, and the team
        // must be below its unit limit. Splitting uses the parent's entire turn;
        // the old tail becomes the child's head and acts later this round.
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
    // ENDTURN completes the reply. Flush so the engine can receive the action
    // before we block waiting for the next turn. Stop when input ends.
    while (bot.update()) std::cout << bot.action() << "\nENDTURN\n" << std::flush;
}

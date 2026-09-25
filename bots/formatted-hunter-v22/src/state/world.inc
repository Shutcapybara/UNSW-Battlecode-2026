    // Wire helpers, strategic team estimates, and remembered map geometry.
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
    std::pair<int, int> largest_known_team() const {
        int largest = length, largest_id = id;
        for (const auto& item : visible_friendly_sizes) {
            if (item.second > largest ||
                (item.second == largest && item.first < largest_id)) {
                largest = item.second;
                largest_id = item.first;
            }
        }
        if (age(shared_summary.observed_round) <= 20 &&
            (shared_summary.team_max > largest ||
             (shared_summary.team_max == largest && shared_summary.team_max_id >= 0 &&
              shared_summary.team_max_id < largest_id))) {
            largest = shared_summary.team_max;
            largest_id = shared_summary.team_max_id;
        }
        return {largest_id, largest};
    }
    bool is_largest_known() const {
        return largest_known_team().first == id;
    }
    bool has_larger_known_teammate() const {
        auto team = largest_known_team();
        return team.second > length || (team.second == length && team.first != id);
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
        // Reserve local pearl collection while it can support a meaningful
        // part of the force, then send some dragons to find richer territory.
        int required_opportunities = std::max(4, (units + 3) / 4);
        return local_pearl_opportunity_count() >= required_opportunities;
    }
    bool is_portal_scout_candidate() const {
        // Keep a small, deterministic scout group instead of allowing one
        // radio claim to suppress every other dragon on a large board.
        int desired_scouts = std::min(4, std::max(1, (units + 5) / 6));
        int eligible_dragons = std::max(1, (units + 1) / 2);
        int bucket_count = std::min(16,
            (desired_scouts * 16 + eligible_dragons - 1) / eligible_dragons);
        std::uint32_t mixed_id = static_cast<std::uint32_t>(id + 1) * UINT32_C(2654435761);
        return static_cast<int>(mixed_id >> 28) < bucket_count;
    }
    bool should_explore_portals() {
        if (portal_policy_round == round) return portal_policy_decision;
        portal_policy_round = round;
        portal_policy_decision = false;
        auto decide = [&](bool value) {
            portal_policy_decision = value;
            return value;
        };
        if (round >= CROWN_START && length >= 4 && largest_known_team().first == id)
            return decide(false);
        constexpr int MIN_ALIVE_TO_EXPLORE = 4;
        constexpr int MIN_PORTAL_SCOUT_LENGTH = 3;
        // Compact boards put portal exits in immediate contention; portal
        // probes depleted V20 there without adding enough growth to pay back.
        if (width * height <= 625) return decide(false);
        if (units < MIN_ALIVE_TO_EXPLORE) return decide(false);
        if (has_local_pearl_supply()) return decide(false);

        bool own_claim = portal_scout_id == id &&
                         age(portal_scout_round) <= SCOUT_CLAIM_TTL;
        if (!own_claim && !is_portal_scout_candidate()) return decide(false);
        if (own_claim) {
            if (age(portal_scout_round) >= SCOUT_CLAIM_TTL / 2)
                portal_scout_round = round;
            return decide(true);
        }

        constexpr int MAX_EXPENDABLE_SCOUT_LENGTH = 6;
        // Scouts should be large enough to survive a trip, while leaving the
        // rest of the force available to collect pearls and grow.
        int expendable_team_threshold = std::max(4, limit / 16);
        bool expendable_scout = units >= expendable_team_threshold &&
                                length >= MIN_PORTAL_SCOUT_LENGTH &&
                                length <= MAX_EXPENDABLE_SCOUT_LENGTH;
        if (!expendable_scout) return decide(false);

        // Claims still suppress non-scouts and extend an active trip. Other
        // deterministic scout candidates may probe different portal routes.
        portal_scout_id = id;
        portal_scout_round = round;
        return decide(true);
    }
    int largest_known_team_length() const {
        return largest_known_team().second;
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
        if (round >= CROWN_START && length >= 4 && largest_known_team().first == id)
            return true;
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

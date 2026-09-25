    // High-level growth, combat, split, food, and exploration ordering.
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

    // Policy chooses between named execution scripts.  Each script remains
    // independently replaceable; this function only owns their ordering.
    Decision choose_decision(bool signal) {
        current_signal = signal;
        PortalTripDecision portal;
        TacticalCombatDecision tactics;
        PortalRecoveryDecision recovery;
        GrowthDecision growth;
        AttackDecision attack;
        MoveAsideDecision move_aside;
        SplitDecision split;
        SignalAdvanceDecision advance;
        const DecisionRule* priorities[] = {
            &portal, &tactics, &recovery, &growth,
            &attack, &move_aside, &split, &advance,
        };
        for (const DecisionRule* rule : priorities)
            if (auto decision = rule->evaluate(*this)) return *decision;

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
                int hotspot_pull = std::max(0, 10 - hotspot_distance[p]) * 6;
                int scout_pull = std::max(0, 12 - unknown_distance[p]) * 20;
                // Reach an edge of the known map first. Teammate separation
                // and stale pearl memories are tie-breakers; they must not
                // outweigh making new tiles visible or revisiting old paths.
                int score = frontier * 10000 + scout_pull + hotspot_pull +
                            std::min(friend_distance, 12) * 4 -
                            distance[p] * 20 - std::min(visits[p], 24) * 25;
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
        if (target >= 0) {
            Execution execution = pearl >= 0 ? Execution::FORAGE : Execution::EXPLORE;
            return {execution, std::string("MOVE ") + DIR[first[target]]};
        }
        if (length >= 4 && units < limit)
            return {Execution::SPLIT, "SPLIT " + std::to_string(length - 2)};
        for (int d = 0; d < 4; ++d)
            if (destination(head, d) == -2)
                return {Execution::EXPLORE, std::string("MOVE ") + DIR[d]};
        return {Execution::FALLBACK, "MOVE N"};
    }

public:
    std::string action() {
        bool signal = should_signal();
        last_decision = choose_decision(signal);
        std::uint64_t status = summary_message();
        std::string output = last_decision.command;
        for (int d = 0; d < 4; ++d) {
            int slot = (round + d) % 4;
            std::uint64_t message = slot == 0 ? status :
                slot == 1 ? ((round & 1) ? scout_message() : crown_message()) :
                slot == 2 ? hotspot_message() :
                round % 2 == 0 ? portal_message() : coverage_message();
            if (signal && d == facing) message = MOVE_ASIDE;
            output += "\nSONAR " + std::string(1, DIR[d]) + " " + std::to_string(message);
        }
        return output;
    }

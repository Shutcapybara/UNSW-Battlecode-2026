    // Survival search and safe, paired portal excursions.
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
        // Scout eligibility must not strand a dragon beside an unpaired
        // portal when every ordinary exit is blocked. A hidden portal exit
        // is acceptable here only as the last available move; visible exits
        // still need to be unoccupied and outside the predicted danger zone.
        if (route.empty() && !inside) {
            bool ordinary_exit = false;
            for (int d = 0; d < 4; ++d) {
                if (tiles[head].edges[d] != ".") continue;
                int next = destination(head, d);
                if (next == -2 || (next >= 0 && !danger[next])) {
                    ordinary_exit = true;
                    break;
                }
            }
            if (!ordinary_exit) {
                int safe_visible_portal = -1;
                int hidden_portal = -1;
                for (int offset = 0; offset < 4; ++offset) {
                    int d = (offset + id + round / 8) % 4;
                    const std::string& symbol = tiles[head].edges[d];
                    if (symbol == "." || symbol == "w") continue;
                    int next = destination(head, d, false, true);
                    if (next == -2) {
                        if (hidden_portal < 0) hidden_portal = d;
                    } else if (next >= 0 && !tiles[next].occupied && !danger[next]) {
                        safe_visible_portal = d;
                        break;
                    }
                }
                int d = safe_visible_portal >= 0 ? safe_visible_portal : hidden_portal;
                if (d >= 0) {
                    const std::string& symbol = tiles[head].edges[d];
                    trip_portal = symbol;
                    trip_entry = edge_at(head, d);
                    inside = true;
                    expected_head = destination(head, d, false, true);
                    expected_round = round + 1;
                    return std::string("MOVE ") + DIR[d];
                }
            }
        }
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

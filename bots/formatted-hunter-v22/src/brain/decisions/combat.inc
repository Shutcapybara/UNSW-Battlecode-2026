    // Conservative hunts, boost tactics, signalling, and emergency spreading.
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
                    if (enemy != enemies.end()) {
                        int enemy_size = enemy->second.visible_size;
                        bool ordinary_hunt = enemy_size > length;
                        bool crown_kill = round >= 380 &&
                            enemy_size >= largest_known_team_length() && length >= enemy_size;
                        if (ordinary_hunt || crown_kill) return path[next];
                    }
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
            if (params::use_local_safety_tiebreak) score += local_safety_score(d);
            if (d == (facing + 2) % 4) score -= 20; // usually points into our neck
            if (score > best_score) { best_score = score; best = d; }
        }
        return best;
    }

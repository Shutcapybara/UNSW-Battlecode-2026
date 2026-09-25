    // Live/static teammate routes and deterministic pearl ownership.
    void build_friend_routes() const {
        if (friend_routes_ready) return;
        friend_routes_ready = true;
        const int n = static_cast<int>(tiles.size());
        live_friend_routes.clear();
        static_friend_routes.clear();
        nearest_pearl_routes.assign(n, {9999, 9999});
        auto add_friend_route = [&](int source, int teammate_id) {
            if (source < 0 || source >= n || source == head ||
                live_friend_routes.count(teammate_id)) return;
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
        };
        for (int source = 0; source < n; ++source) {
            if (tiles[source].friendly_head && source != head)
                add_friend_route(source, tiles[source].dragon_id);
        }
        auto leader = largest_known_team();
        if (age(crown_report.observed_round) <= CROWN_REPORT_TTL &&
            crown_report.dragon_id == leader.first && crown_report.dragon_id != id)
            add_friend_route(crown_report.position, crown_report.dragon_id);
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

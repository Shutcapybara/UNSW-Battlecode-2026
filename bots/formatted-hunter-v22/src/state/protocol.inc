    // Engine initialization and observation/report ingestion.
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
                        static_cast<int>((message >> 20) & 65535),
                        static_cast<int>((message >> 10) & 1023), round - delay};
                    if (incoming.observed_round > shared_summary.observed_round)
                        shared_summary = incoming;
                    else if (incoming.observed_round == shared_summary.observed_round) {
                        if (incoming.team_max > shared_summary.team_max ||
                            (incoming.team_max == shared_summary.team_max &&
                             incoming.team_max_id >= 0 &&
                             (shared_summary.team_max_id < 0 ||
                              incoming.team_max_id < shared_summary.team_max_id))) {
                            shared_summary.team_max = incoming.team_max;
                            shared_summary.team_max_id = incoming.team_max_id;
                        }
                        shared_summary.enemy_max = std::max(shared_summary.enemy_max, incoming.enemy_max);
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
            } else if (tag == CROWN_TAG) {
                int sent = static_cast<int>((message >> 46) & 1023);
                int crown_id = static_cast<int>((message >> 30) & 65535);
                int crown_length = static_cast<int>((message >> 20) & 1023);
                int x = static_cast<int>((message >> 14) & 63);
                int y = static_cast<int>((message >> 8) & 63);
                update_crown_report(sent, crown_id, crown_length, x, y);
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
        update_macro_features(observed_friendly_sizes, observed_enemy_sizes);
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

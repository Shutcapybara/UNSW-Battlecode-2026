    // Team knowledge and sonar packet construction.
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
        int team_max = length, team_max_id = id, enemy_max = 0;
        for (const auto& friend_size : visible_friendly_sizes) {
            if (friend_size.second > team_max ||
                (friend_size.second == team_max && friend_size.first < team_max_id)) {
                team_max = friend_size.second;
                team_max_id = friend_size.first;
            }
        }
        for (const auto& enemy : enemies)
            enemy_max = std::max(enemy_max, enemy.second.visible_size);
        int observed = round;
        if (age(shared_summary.observed_round) <= 20) {
            bool shared_team_leads = shared_summary.team_max > team_max ||
                (shared_summary.team_max == team_max && shared_summary.team_max_id >= 0 &&
                 shared_summary.team_max_id < team_max_id);
            if (shared_team_leads || shared_summary.enemy_max > enemy_max)
                observed = shared_summary.observed_round;
            if (shared_team_leads) {
                team_max = shared_summary.team_max;
                team_max_id = shared_summary.team_max_id;
            }
            enemy_max = std::max(enemy_max, shared_summary.enemy_max);
        }
        return SUMMARY_TAG | (std::uint64_t(observed & 1023) << 46) |
            (std::uint64_t(std::min(team_max, 1023)) << 36) |
            (std::uint64_t(team_max_id & 65535) << 20) |
            (std::uint64_t(std::min(enemy_max, 1023)) << 10);
    }
    std::uint64_t crown_message() const {
        int team_max = length, team_max_id = id;
        for (const auto& friend_size : visible_friendly_sizes) {
            if (friend_size.second > team_max ||
                (friend_size.second == team_max && friend_size.first < team_max_id)) {
                team_max = friend_size.second;
                team_max_id = friend_size.first;
            }
        }
        if (age(shared_summary.observed_round) <= 20 &&
            (shared_summary.team_max > team_max ||
             (shared_summary.team_max == team_max && shared_summary.team_max_id >= 0 &&
              shared_summary.team_max_id < team_max_id))) {
            team_max = shared_summary.team_max;
            team_max_id = shared_summary.team_max_id;
        }
        if (round >= CROWN_START && team_max_id == id && length == team_max && length >= 4) {
            return CROWN_TAG | (std::uint64_t(round & 1023) << 46) |
                (std::uint64_t(id & 65535) << 30) |
                (std::uint64_t(std::min(length, 1023)) << 20) |
                (std::uint64_t((head % width) & 63) << 14) |
                (std::uint64_t((head / width) & 63) << 8);
        }
        if (age(crown_report.observed_round) <= CROWN_REPORT_TTL &&
            crown_report.dragon_id == team_max_id && crown_report.position >= 0) {
            return CROWN_TAG | (std::uint64_t(crown_report.observed_round & 1023) << 46) |
                (std::uint64_t(crown_report.dragon_id & 65535) << 30) |
                (std::uint64_t(std::min(crown_report.length, 1023)) << 20) |
                (std::uint64_t((crown_report.position % width) & 63) << 14) |
                (std::uint64_t((crown_report.position / width) & 63) << 8);
        }
        return summary_message();
    }
    void update_crown_report(int sent, int dragon_id, int crown_length, int x, int y) {
        if (age(sent) > CROWN_REPORT_TTL || dragon_id < 0 || dragon_id > 65535 ||
            crown_length < 4 || x >= width || y >= height) return;
        int current_age = age(crown_report.observed_round);
        if (crown_report.dragon_id < 0 || current_age > CROWN_REPORT_TTL ||
            age(sent) < current_age ||
            (age(sent) == current_age && dragon_id < crown_report.dragon_id)) {
            crown_report = {dragon_id, crown_length, pos(x, y), sent};
        }
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

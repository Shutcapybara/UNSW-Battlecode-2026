    // Behaviour-neutral features and small graph analyses for policy experiments.
private:
    void update_macro_features(const std::map<int, int>& observed_friends,
                               const std::map<int, int>& observed_enemies) {
        const double alpha = static_cast<double>(params::density_alpha_numerator) /
                             params::density_alpha_denominator;
        const double friendly_now = static_cast<double>(observed_friends.size() + 1);
        const double enemy_now = static_cast<double>(observed_enemies.size());
        if (macro_features.round == 0) {
            macro_features.friendly_density_ewma = friendly_now;
            macro_features.enemy_density_ewma = enemy_now;
        } else {
            macro_features.friendly_density_ewma +=
                alpha * (friendly_now - macro_features.friendly_density_ewma);
            macro_features.enemy_density_ewma +=
                alpha * (enemy_now - macro_features.enemy_density_ewma);
        }
        macro_features.round = round;
        macro_features.own_length = length;
        macro_features.team_units = units;
        macro_features.visible_friendly_dragons = static_cast<int>(observed_friends.size()) + 1;
        macro_features.visible_enemy_dragons = static_cast<int>(observed_enemies.size());
    }

    LocalSafety local_safety_after_move(int direction) const {
        LocalSafety result;
        int start = destination(head, direction);
        if (start < 0) return result;

        std::vector<bool> enemy_reach(tiles.size(), false);
        for (int p = 0; p < static_cast<int>(tiles.size()); ++p) {
            if (!tiles[p].enemy_head) continue;
            for (int d = 0; d < 4; ++d) {
                int q = destination(p, d, false, true);
                if (q >= 0) enemy_reach[q] = true;
            }
        }

        std::vector<bool> seen(tiles.size(), false);
        std::queue<int> pending;
        seen[start] = true;
        pending.push(start);
        while (!pending.empty() && result.reachable_tiles < params::local_safety_cap) {
            int p = pending.front();
            pending.pop();
            ++result.reachable_tiles;
            if (enemy_reach[p]) ++result.enemy_reachable_tiles;
            for (int d = 0; d < 4; ++d) {
                int q = destination(p, d);
                if (q < 0 || q == head || seen[q]) continue;
                seen[q] = true;
                pending.push(q);
            }
        }
        for (int d = 0; d < 4; ++d) {
            int q = destination(start, d);
            if (q >= 0 && q != head) ++result.immediate_exits;
        }
        result.dead_end = result.immediate_exits == 0;
        return result;
    }

    int local_safety_score(int direction) const {
        LocalSafety safety = local_safety_after_move(direction);
        return safety.reachable_tiles * params::local_safety_reachable_weight +
               safety.immediate_exits * params::local_safety_exit_weight -
               safety.enemy_reachable_tiles * params::local_safety_enemy_weight -
               (safety.dead_end ? params::local_safety_dead_end_penalty : 0);
    }

public:
    const MacroFeatures& features() const { return macro_features; }
    const Decision& decision() const { return last_decision; }

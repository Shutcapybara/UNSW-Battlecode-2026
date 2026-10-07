#pragma once

#include "bokuto.hpp"
#include "learn_helper.hpp"
#include <memory>

namespace finals {

enum class Option { BASELINE, FORAGE, DISPERSE, ESCAPE, BED, PRODUCE };
constexpr int N_FEATURES = 32;
constexpr int MAX_CANDIDATES = 12;

inline bool same_command(const ares::Decision& a, const ares::Decision& b) {
    return a.act == b.act && (a.act == ares::Act::SPLIT ? a.split == b.split : a.dirs == b.dirs);
}

struct Candidate {
    Option option = Option::BASELINE;
    ares::Decision decision;
    std::array<float, N_FEATURES> features{};
    bool available = true;
};

// Staging runs the incumbent exactly once on copies, including its lawful inbox updates.
// Proposal generation reads that prepared state; persistent state changes only in commit().
struct Turn {
    ares::World world;
    ares::Policy policy;
    bokuto::Guard incoming_guard, baseline_guard;
    std::array<double, 4> incoming_momentum;
    ares::Decision raw, baseline;
    char baseline_tag = 0;
    std::vector<Candidate> candidates;
    bool committed = false;
    bool unexpected_override = false;

    Turn(const ares::World& w, const ares::Policy& p, const bokuto::Guard& g)
        : world(w), policy(p), incoming_guard(g), baseline_guard(g), incoming_momentum(p.momentum) {
        const int real_limit = world.limit;
        if (world.me > 1) world.limit = std::max(1, real_limit - 1);
        raw = policy.decide(world);
        world.limit = real_limit;
        baseline = raw;
        ares::Decision replacement;
        if (baseline_guard.apply(world, raw, replacement, baseline_tag)) baseline = replacement;
        add(Option::BASELINE, baseline, false);
    }

    int crowd(int target) const {
        int n = 0;
        if (target >= 0) for (int pi : world.ally_heads)
            n += world.tdist(world.parts[pi].cell, target) <= 3;
        return n;
    }

    std::array<float, N_FEATURES> features(Option option, const ares::Decision& d) const {
        std::array<float, N_FEATURES> x{};
        x[static_cast<int>(option)] = 1.0f;
        x[6] = world.len / 64.0f;
        x[7] = world.units / float(std::max(1, world.limit));
        x[8] = (world.limit - world.units) / float(std::max(1, world.limit));
        x[9] = world.rnd / 500.0f;
        x[10] = ares::is_queen(world);
        x[11] = policy.role_crown;
        x[12] = policy.role_feeder;
        x[13] = d.act == ares::Act::SPLIT;
        x[14] = d.split / 64.0f;
        x[15] = d.dirs.size() / 4.0f;
        x[16] = policy.sprint_paid(world, d.dirs.size()) / 4.0f;
        x[17] = policy.escape_active;
        int landing = world.head;
        if (d.act == ares::Act::MOVE) {
            auto sim = policy.simulate(world, d.dirs);
            if (!sim.body.empty()) landing = sim.body.back();
            x[18] = sim.eaten / 4.0f;
            x[19] = sim.status == ares::Policy::SimStatus::OK;
        }
        x[20] = std::min(32.0, policy.threat_cost(world, landing, world.len)) / 32.0f;
        x[21] = std::min(8, crowd(landing)) / 8.0f;
        x[22] = landing < int(policy.visits.size()) ? std::min(16, int(policy.visits[landing])) / 16.0f : 0;
        int exits = 0;
        for (int direction = 0; direction < 4; direction++) {
            int n = world.dest(landing, direction);
            exits += n >= 0 && world.occ[n] < 0 && !world.own[n];
        }
        x[23] = exits / 4.0f;
        if (d.target >= 0 && d.target < world.NC) {
            int target = d.target;
            int dx = target % world.W - world.head % world.W;
            int dy = target / world.W - world.head / world.W;
            if (dx > world.W / 2) dx -= world.W;
            if (dx < -world.W / 2) dx += world.W;
            if (dy > world.H / 2) dy -= world.H;
            if (dy < -world.H / 2) dy += world.H;
            const int fx[4] = {0, 1, 0, -1}, fy[4] = {-1, 0, 1, 0};
            x[24] = (dx * fx[world.face] + dy * fy[world.face]) / 32.0f;
            x[25] = (-dx * fy[world.face] + dy * fx[world.face]) / 32.0f;
            x[26] = std::min(32, world.tdist(world.head, target)) / 32.0f;
            x[27] = std::min(8, crowd(target)) / 8.0f;
            x[28] = world.pearl_seen[target] < 0 ? -1.0f :
                std::min(64, world.rnd - world.pearl_seen[target]) / 64.0f;
            x[29] = world.spawn_at[target] < 0 ? -1.0f :
                std::clamp(world.spawn_at[target] - world.rnd, -64, 64) / 64.0f;
            x[30] = (world.tdist(world.head, target) - world.tdist(landing, target)) / 4.0f;
            x[31] = world.pearl_known(target, ares::Params::memory_ttl);
        }
        return x;
    }

    void add(Option option, const ares::Decision& d, bool filter = true) {
        if (int(candidates.size()) >= MAX_CANDIDATES) return;
        for (const auto& old : candidates) if (same_command(old.decision, d)) return;
        if (filter) {
            if (d.act == ares::Act::MOVE && policy.simulate(world, d.dirs).status != ares::Policy::SimStatus::OK) return;
            if (d.act == ares::Act::SPLIT && (d.split < 2 || world.len - d.split < 2 ||
                world.units >= world.limit - 1 || int(world.body.size()) != world.len)) return;
            auto guard = incoming_guard;
            ares::Decision replacement;
            char tag = 0;
            if (guard.apply(world, d, replacement, tag) && !same_command(d, replacement)) return;
        }
        candidates.push_back({option, d, features(option, d), true});
    }

    void toward(Option option, int target, char why) {
        if (target < 0 || target == world.head || policy.fwd.d[target] < 1) return;
        auto route = ares::path(world, policy.fwd, target);
        if (route.empty()) return;
        // Small bounded menu; the chassis retains its full search as BASELINE.
        route.resize(std::min(int(route.size()), std::min(2, (world.len + 3) / 4)));
        ares::Decision d;
        d.dirs = route; d.target = target; d.why = why;
        add(option, d);
    }

    void propose() {
        // These roles/emergencies retain the exact guarded incumbent command.
        if (ares::is_queen(world) || policy.role_crown || policy.role_feeder || baseline_tag ||
            baseline.why == 't' || int(world.body.size()) != world.len) return;
        std::vector<std::pair<double, int>> food, beds, explore;
        for (int c : policy.fwd.order) {
            const int steps = policy.fwd.d[c];
            if (steps < 1 || steps > 16 || !bokuto::branch_allowed(world, c)) continue;
            if (world.pearl_known(c, ares::Params::memory_ttl) && policy.cell_value(world, c, steps) > 0)
                food.push_back({-policy.cell_value(world, c, steps) * std::pow(ares::Params::target_gamma, steps), c});
            if (world.bed[c] == 1 && world.spawn_at[c] >= world.rnd)
                beds.push_back({double(std::abs(world.spawn_at[c] - world.rnd - steps) + steps), c});
            if (!policy.escape_active) {
                double score = steps * 0.2 + crowd(c) * 3.0 + policy.visits[c] + (world.seen[c] ? 2.0 : 0.0);
                explore.push_back({score, c});
            }
        }
        auto bounded_targets = [&](auto& targets, Option option, char why, int count) {
            std::sort(targets.begin(), targets.end());
            for (int i = 0; i < std::min(count, int(targets.size())); i++) toward(option, targets[i].second, why);
        };
        if (!policy.escape_active) {
            bounded_targets(food, Option::FORAGE, 'p', 2);
            bounded_targets(explore, Option::DISPERSE, 'x', 2);
            bounded_targets(beds, Option::BED, 'b', 1);
        }
        if (policy.escape_active && policy.escape_plan_target >= 0)
            toward(Option::ESCAPE, policy.escape_plan_target, 'e');
        int escape = policy.tyr_escape_split(world);
        if (escape > 0 && policy.escape_active) {
            ares::Decision d; d.act = ares::Act::SPLIT; d.split = escape; d.why = 't';
            add(Option::ESCAPE, d);
        }
        // Split feasibility uses local scratch policy state (flood buffers), never live state.
        auto scratch = policy;
        auto view = world;
        view.limit = std::max(1, world.limit - 1);
        double score = 0;
        if (!policy.escape_active && scratch.tyr_split_option(view, score)) {
            ares::Decision d; d.act = ares::Act::SPLIT;
            d.split = ares::Params::split_child; d.why = 's';
            add(Option::PRODUCE, d);
        }
    }

    ares::Decision commit(ares::World& w, ares::Policy& p, bokuto::Guard& g, int selected, char& tag) {
        if (committed || selected < 0 || selected >= int(candidates.size()) || !candidates[selected].available)
            throw std::runtime_error("Invalid or repeated option commit");
        committed = true;
        auto actual = candidates[selected].decision;
        if (selected == 0) {
            g = std::move(baseline_guard);
            tag = baseline_tag;
        } else {
            g = incoming_guard;
            tag = 0;
            ares::Decision replacement;
            if (g.apply(world, actual, replacement, tag) && !same_command(actual, replacement)) {
                actual = replacement;
                unexpected_override = true;
            }
            policy.momentum = incoming_momentum;
            if (actual.act == ares::Act::MOVE) {
                for (double& m : policy.momentum) m *= ares::Params::momentum_decay;
                if (!actual.dirs.empty()) policy.momentum[actual.dirs.front()] += 1.0 - ares::Params::momentum_decay;
            }
            policy.previous_target = actual.target;
        }
        // Radio preparation and movement/history commit remain in the ordinary turn loop.
        w = std::move(world);
        p = std::move(policy);
        return actual;
    }
};

inline void emit_choices(const char* prefix, const std::array<int32_t, learn::N_X>& observation,
                         const Turn& turn) {
    std::cout.precision(std::numeric_limits<float>::max_digits10);
    std::cout << prefix << " {\"id\":" << turn.world.me << ",\"round\":" << turn.world.rnd << ",\"x\":[";
    for (int i = 0; i < learn::N_X; i++) { if (i) std::cout << ','; std::cout << observation[i]; }
    std::cout << "],\"candidates\":[";
    for (size_t i = 0; i < turn.candidates.size(); i++) {
        const auto& c = turn.candidates[i];
        if (i) std::cout << ',';
        std::cout << "{\"option\":" << int(c.option) << ",\"features\":[";
        for (int j = 0; j < N_FEATURES; j++) { if (j) std::cout << ','; std::cout << c.features[j]; }
        std::cout << "],\"act\":" << int(c.decision.act) << ",\"split\":" << c.decision.split << ",\"dirs\":[";
        for (size_t j = 0; j < c.decision.dirs.size(); j++) { if (j) std::cout << ','; std::cout << c.decision.dirs[j]; }
        std::cout << "]}";
    }
    std::cout << "]}" << std::endl;
}

enum class PacketOption { BASELINE, NO_SEND, TEMPLATE };
struct PacketCandidate {
    PacketOption option;
    int ray;
    uint64_t value;
    int type;
    bool protected_packet;
};

// Deterministic incumbent-compatible templates. Required handoff/beacon slots are fixed.
inline std::array<std::vector<PacketCandidate>, 4> packet_candidates(const ares::World& w, const ares::Policy& p) {
    std::array<std::vector<PacketCandidate>, 4> rays;
    for (int ray = 0; ray < 4; ray++) {
        int type = 0; uint64_t payload = 0;
        if (p.sonar_out[ray]) ares::Policy::unpack(w, p.sonar_out[ray], type, payload);
        bool protected_packet = type == 1 || type == 3 || type == 7;
        rays[ray].push_back({PacketOption::BASELINE, ray, p.sonar_out[ray], type, protected_packet});
        if (protected_packet) continue;
        if (p.sonar_out[ray]) rays[ray].push_back({PacketOption::NO_SEND, ray, 0, 0, false});
        for (int from : p.sonar_order) {
            uint64_t value = p.sonar_out[from];
            int family = 0; uint64_t bits = 0;
            if (!value || !ares::Policy::unpack(w, value, family, bits) || family == 1 || family == 3 || family == 7) continue;
            bool duplicate = false;
            for (auto const& old : rays[ray]) duplicate = duplicate || old.value == value;
            if (!duplicate) rays[ray].push_back({PacketOption::TEMPLATE, ray, value, family, false});
        }
    }
    return rays;
}

inline void commit_packets(ares::Policy& p, const std::array<std::vector<PacketCandidate>, 4>& rays,
                           const std::array<int, 4>& selected) {
    // Baseline preserves both packet values and original send ordering byte for byte.
    bool baseline = true;
    for (int ray = 0; ray < 4; ray++) {
        if (selected[ray] < 0 || selected[ray] >= int(rays[ray].size())) throw std::runtime_error("Invalid packet index");
        baseline = baseline && selected[ray] == 0;
    }
    if (baseline) return;
    for (int ray = 0; ray < 4; ray++) p.sonar_out[ray] = rays[ray][selected[ray]].value;
    p.sonar_order.clear();
    for (int ray = 0; ray < 4; ray++) if (p.sonar_out[ray]) p.sonar_order.push_back(ray);
}

}  // namespace finals

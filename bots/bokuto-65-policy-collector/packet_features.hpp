#pragma once
#include "options.hpp"

namespace finals {

inline std::array<float, N_FEATURES> packet_features(const ares::World& w, const ares::Policy& p,
                                                    const ares::Decision& action, const PacketCandidate& packet) {
    std::array<float, N_FEATURES> x{};
    x[int(packet.option)] = 1.0f;
    if (packet.type >= 1 && packet.type <= 7) x[2 + packet.type] = 1.0f;
    x[10] = packet.protected_packet;
    x[11 + (packet.ray - w.face + 4) % 4] = 1.0f;
    x[15] = w.rnd / 500.0f;
    int landing = w.head;
    std::vector<int> own = w.body;
    bool dying = false;
    if (action.act == ares::Act::MOVE) {
        auto sim = p.simulate(w, action.dirs);
        if (!sim.body.empty()) { own = sim.body; landing = own.back(); }
        dying = sim.status == ares::Policy::SimStatus::DEAD;
    } else if (int(own.size()) > action.split) {
        own.erase(own.begin(), own.begin() + action.split);
    }
    int dx = landing % w.W - w.head % w.W, dy = landing / w.W - w.head / w.W;
    if (dx > w.W / 2) dx -= w.W; if (dx < -w.W / 2) dx += w.W;
    if (dy > w.H / 2) dy -= w.H; if (dy < -w.H / 2) dy += w.H;
    const int fx[4] = {0,1,0,-1}, fy[4] = {-1,0,1,0};
    x[16] = (dx * fx[w.face] + dy * fy[w.face]) / 32.0f;
    x[17] = (-dx * fy[w.face] + dy * fx[w.face]) / 32.0f;
    int next = w.dest(landing, packet.ray);
    x[18] = next == ares::BLOCKED;
    x[19] = next == ares::UNKNOWN || next == ares::UNPAIRED;
    x[20] = next >= 0 && std::find(own.begin(), own.end(), next) != own.end();
    if (next >= 0 && w.occ[next] >= 0) {
        const auto& hit = w.parts[w.occ[next]];
        x[21] = hit.ally; x[22] = !hit.ally;
    }
    // Visible recipient geometry relative to the predicted landing, not pre-move head.
    int nearest = 32;
    for (int pi : w.ally_heads) nearest = std::min(nearest, w.tdist(landing, w.parts[pi].cell));
    x[23] = nearest / 32.0f;
    int type = 0; uint64_t payload = 0;
    if (packet.value && ares::Policy::unpack(w, packet.value, type, payload)) {
        int stamp = -1;
        if (type == 1 || type == 4) stamp = (payload >> 22) & 511;
        if (type == 6) stamp = (payload >> 12) & 511;
        if (type == 7) stamp = (payload >> 26) & 511;
        if (type == 2) stamp = (payload >> 12) & 511;
        x[24] = stamp < 0 ? -1.0f : std::clamp(w.rnd - stamp, -64, 64) / 64.0f;
    }
    x[25] = w.msgs.size() / 16.0f;
    x[26] = dying;
    x[27] = action.act == ares::Act::SPLIT;
    x[28] = action.split / 64.0f;
    x[29] = action.dirs.size() / 4.0f;
    x[30] = p.sprint_paid(w, action.dirs.size()) / 4.0f;
    x[31] = w.len / 64.0f;
    return x;
}

inline void emit_packets(const std::array<std::vector<PacketCandidate>, 4>& rays,
                         const ares::World& w, const ares::Policy& p, const ares::Decision& action) {
    std::cout.precision(std::numeric_limits<float>::max_digits10);
    std::cout << "PACKETS {\"rays\":[";
    for (int ray = 0; ray < 4; ray++) {
        if (ray) std::cout << ',';
        std::cout << '[';
        for (size_t i = 0; i < rays[ray].size(); i++) {
            if (i) std::cout << ',';
            auto x = packet_features(w, p, action, rays[ray][i]);
            std::cout << "{\"features\":[";
            for (int j = 0; j < N_FEATURES; j++) { if (j) std::cout << ','; std::cout << x[j]; }
            // uint64 payloads are strings to avoid any downstream float precision loss.
            std::cout << "],\"value\":\"" << rays[ray][i].value << "\"}";
        }
        std::cout << ']';
    }
    std::cout << "]}" << std::endl;
}

}  // namespace finals

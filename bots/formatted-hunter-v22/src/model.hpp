#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <queue>
#include <set>
#include <sstream>
#include <string>
#include <vector>

constexpr int DX[] = {0, 1, 0, -1};
constexpr int DY[] = {-1, 0, 1, 0};
constexpr char DIR[] = "NESW";
constexpr std::uint64_t MOVE_ASIDE = 1146242894u; // ASCII "DRGN"
constexpr std::uint64_t SUMMARY_TAG = UINT64_C(0xA9) << 56;
constexpr std::uint64_t HOTSPOT_TAG = UINT64_C(0xAA) << 56;
constexpr std::uint64_t PORTAL_TAG = UINT64_C(0xAB) << 56;
constexpr std::uint64_t COVERAGE_TAG = UINT64_C(0xAC) << 56;
constexpr std::uint64_t SCOUT_TAG = UINT64_C(0xAD) << 56;
constexpr std::uint64_t CROWN_TAG = UINT64_C(0xAE) << 56;
constexpr int HOTSPOT_TTL = 8;
constexpr int SCOUT_CLAIM_TTL = 8;
constexpr int CROWN_REPORT_TTL = 8;
constexpr int CROWN_START = 220;
constexpr int MAX_PORTAL_APPROACH = 8;

// Policy vocabulary used by the staged driver below.  The original V22
// helpers still return compact wire commands internally so their behaviour is
// preserved byte-for-byte while the outer lifecycle follows the new format.
enum class Execution {
    NONE,
    PORTAL_TRIP,
    SURROUND,
    TRAP,
    SURVIVE,
    GROW,
    ATTACK,
    YIELD,
    SPLIT,
    ADVANCE,
    FORAGE,
    EXPLORE,
    FALLBACK
};

struct Decision {
    Execution execution = Execution::NONE;
    std::string command;

    explicit operator bool() const { return !command.empty(); }
};

// A deliberately small, behaviour-neutral feature snapshot.  New policies can
// consume this without reaching into protocol parsing or persistent memory.
struct MacroFeatures {
    int round = 0;
    int own_length = 0;
    int team_units = 0;
    int visible_friendly_dragons = 0;
    int visible_enemy_dragons = 0;
    double friendly_density_ewma = 0.0;
    double enemy_density_ewma = 0.0;
};

struct LocalSafety {
    int reachable_tiles = 0;
    int immediate_exits = 0;
    int enemy_reachable_tiles = 0;
    bool dead_end = true;
};

struct Tile {
    bool visible = false, pearl = false, occupied = false;
    bool own_body = false;
    int countdown = -1;
    bool friendly_head = false, enemy_head = false;
    int dragon_id = -1, facing = -1, body_direction = -1;
    std::array<std::string, 4> edges = {".", ".", ".", "."};
};

struct Edge {
    int x, y;
    bool horizontal;
    bool operator==(const Edge& other) const {
        return x == other.x && y == other.y && horizontal == other.horizontal;
    }
};

struct EnemyMemory {
    int position = -1;
    int visible_size = 0;
    int facing = -1;
    int last_seen = -1;
};

struct PearlMemory {
    bool present = false;
    int countdown = -1;
    int last_seen = -1;
};

struct SharedSummary {
    int team_max = 0, team_max_id = -1, enemy_max = 0;
    int observed_round = -1;
};

struct CrownReport {
    int dragon_id = -1, length = 0, position = -1, observed_round = -1;
};

struct PortalFact {
    int tile = -1, direction = 0, observed_round = -1;
    char symbol = 0;
    bool safe = false;
};

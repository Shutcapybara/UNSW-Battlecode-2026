#pragma once

#include "model.hpp"
#include "params.hpp"

class Bot {
    int width = 0, height = 0, id = 0, limit = 64;
    int round = 0, length = 0, units = 0, head = 0, facing = 0;
    bool asked_to_move = false;
    std::string my_team;
    std::vector<Tile> tiles;
    std::vector<int> visits;
    std::vector<std::array<std::string, 4>> known_edges;
    std::vector<bool> known_edge;
    std::vector<PearlMemory> known_pearls;
    std::vector<int> hotspot_strength, hotspot_round;
    std::vector<bool> scouted_sectors;
    int sector_columns = 0, sector_rows = 0;
    SharedSummary shared_summary;
    CrownReport crown_report;
    std::map<std::pair<int, int>, PortalFact> portal_facts;
    std::set<std::string> safe_portals;
    std::map<std::string, int> portal_last_visit;
    std::map<int, EnemyMemory> enemies;
    std::map<int, int> visible_friendly_sizes;
    std::map<std::string, std::vector<Edge>> portals;
    int portal_scout_id = -1, portal_scout_round = -1;
    int portal_policy_round = -1;
    bool portal_policy_decision = false;
    mutable bool friend_routes_ready = false;
    mutable std::map<int, std::vector<int>> live_friend_routes;
    mutable std::map<int, std::vector<int>> static_friend_routes;
    mutable std::vector<std::pair<int, int>> nearest_pearl_routes;
    std::string route, trip_portal;
    Edge trip_entry{0, 0, false};
    bool inside = false;
    int expected_head = -1, expected_round = -1;
    MacroFeatures macro_features;
    Decision last_decision;
    bool current_signal = false;

#include "communications/sonar.inc"
#include "state/world.inc"
#include "state/features.inc"
#include "navigation/portals.inc"
#include "navigation/team_routes.inc"
#include "brain/decisions/combat.inc"
#include "state/protocol.inc"
#include "brain/decision.inc"
#include "brain/decisions/scripts.inc"
#include "brain/policy.inc"
};

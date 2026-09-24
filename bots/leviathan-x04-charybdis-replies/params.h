#pragma once
namespace P {
constexpr auto reply_plies = 3;       // 0..4; adversarial half-turns after our root action
constexpr auto reply_width = 6;       // 2..20; ordered replies retained at interior nodes
constexpr auto node_budget = 450;     // 100..5000; leaf/expansion budget across root actions
constexpr auto duel_range = 5;        // 1..8; choose nearest complete visible enemy within this distance
constexpr auto sprint_max = 2;        // 1..3; root and reply action generator
constexpr auto life_value = 7.0;      // 0..20; early economic value per surviving producer
constexpr auto material_value = 3.0;  // 1..10; value per segment
constexpr auto kill_weight = 1.0;     // 0..2; enemy losses relative to our losses
constexpr auto mobility_value = 1.2;  // 0..5; available immediate exits
constexpr auto target_value = 0.75;   // 0..3; food/frontier potential per move
constexpr auto visit_cost = 0.12;     // 0..1; repetition penalty
constexpr auto outside_risk = 8.0;    // 0..30; reach from enemies outside the selected duel
constexpr auto split_stop = 390;     // 0..500; last reproduction round
constexpr auto anchor_start = 90;    // 0..400; designated growers stop splitting
constexpr auto anchor_stride = 7;    // 1..64; approximately one in this many IDs is a grower
constexpr auto anchor_length = 6;    // 4..20; grower maturity threshold
constexpr auto bank_value = 0.03;     // 0..0.2; late quadratic length value
constexpr auto memory_ttl = 12;       // 1..40; routing memory only, never immediate sprint funding
}

#pragma once
// Riptide's entire experimental parameter table. Lab overrides this private copy.
namespace P {
constexpr auto horizon = 6;            // 1..10 simulated turns; plan_route
constexpr auto beam = 8;               // 1..24 states per first action per turn
constexpr auto sprint_max = 2;         // 1..3; actual candidate generator
constexpr auto pearl_value = 10.0;     // 0..30; route reward per net segment
constexpr auto step_cost = 0.75;       // 0.1..3; target distance attenuation
constexpr auto frontier_value = 3.0;   // 0..10; unexplored edges in target field
constexpr auto risk_cost = 10.0;       // 0..50; future head reach penalty
constexpr auto visit_cost = 0.12;      // 0..2; route repetition cost
constexpr auto future_discount = 0.86; // 0..1; forecast reward confidence
constexpr auto memory_ttl = 16;        // 1..40; remembered pearls as destinations
constexpr auto claim_discount = 0.35;  // 0..1; closer ally owns target
constexpr auto radio = true;          // ablation: self reports -> target ownership
constexpr auto split_min = 4;          // 4..12; minimum parent length
constexpr auto split_stop = 350;       // 0..500; distributed length banking begins
constexpr auto reserve_len = 12;      // 4..100; length >= this never voluntarily splits
constexpr auto fork_food = true;      // ablation: require separate resource catchments
constexpr auto fork_radius = 7;        // 1..12; parent/child resource BFS radius
constexpr auto fork_window = 25;       // 0..50; forecast food horizon for reproduction
constexpr auto population_max = 64;    // 1..64; population ceiling
}

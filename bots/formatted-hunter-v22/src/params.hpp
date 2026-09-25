#pragma once

// Experimental knobs live here so a small hypothesis does not require editing
// navigation, combat, protocol, and policy code at once.  Defaults reproduce
// the original formatted V22 policy.
namespace params {
constexpr bool use_local_safety_tiebreak = false;
constexpr int local_safety_cap = 24;
constexpr int local_safety_reachable_weight = 1;
constexpr int local_safety_exit_weight = 8;
constexpr int local_safety_enemy_weight = 12;
constexpr int local_safety_dead_end_penalty = 20;

// alpha = numerator / denominator.  This only updates observable features and
// does not alter the default policy.
constexpr int density_alpha_numerator = 1;
constexpr int density_alpha_denominator = 4;
}

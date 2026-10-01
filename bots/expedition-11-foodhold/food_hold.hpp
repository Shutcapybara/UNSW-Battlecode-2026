#pragma once
namespace ares {
// Hold ordinary production only for an immediately available, roomy meal.
// The policy supplies its already-selected move, never a newly forced route.
inline bool hold_split_for_food(int round, bool complete_body, bool safe,
                                int steps, int eaten, int blind_cell,
                                int room, int need) {
    return round < 150 && complete_body && safe && steps == 1 && eaten > 0 &&
           blind_cell < 0 && room >= need;
}
}  // namespace ares

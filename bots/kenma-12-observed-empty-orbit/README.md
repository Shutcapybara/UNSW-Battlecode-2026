# Kenma 12 — observed-empty queen orbit

Parent: kenma-11-current-view-orbit. Corrects the no-bed requirement to World.bed == -1, as produced by World::sense from an observed tile with no pearl bed. Unknown cells (0) are rejected. The round+1 freshness check and activation logging from 11 remain. All strategy and geometric guards are unchanged.

The earlier hand-built fixtures repeated incorrect memory conventions: 10 used round instead of round+1; 11 still used bed=0 instead of -1. Their runtime snapshots remain frozen. The new test first feeds a protocol observation through unswbc::init/update and World::sense and requires an orbit activation, then tests 80 persistent synthetic turns and hazard guards. An actual game activation check is required before a full screen.

Status: rejected versus03 after the full Carthage comparison. Reserved seeds 11–13 and new maps untouched.

Real-game activation smoke: **3–1/4**, zero errors, Weakhold/Australia both seats seed 1. All four replays activated the orbit (168,140 Weakhold;144,239 Australia log entries); replay diagnostics saved. This is integration evidence only. Full Carthage102 now running with unchanged runtime ab99829d2d7b5073fdac35682d1fba07d5ba6dea4e52b55db3f2bfcd2a7add68. Outputs main build/kenma/k12-orbit-smoke/ and k12-smoke-diagnostics.json.

## Full Carthage result

**54–48/102**, zero errors; 17 ranked maps × both seats × seeds1–3. Below03 at58–44. Weakhold and Trauma each6–0, offset by losses elsewhere. All12 retained Schooltime/Weakhold replays analyzed in main build/kenma/k12-final-diagnostics.json; six Schooltime queens and three Weakhold A queens survive, three Weakhold B queens eventually die after leaving their loops. Output k12-v-carthage-s123/score.json. No deployment/pool expansion or reserved validation for this rejected version.

| Map | W | L |
|---|---:|---:|
| schooltime | 6 | 0 |
| portals | 3 | 3 |
| slithery_fight | 2 | 4 |
| queen_of_spades | 2 | 4 |
| default | 3 | 3 |
| trophy | 3 | 3 |
| dilemma | 5 | 1 |
| autarky | 3 | 3 |
| devil | 1 | 5 |
| trauma | 6 | 0 |
| australia | 3 | 3 |
| islands | 0 | 6 |
| unsw | 4 | 2 |
| maze | 4 | 2 |
| weakhold | 6 | 0 |
| stripes | 2 | 4 |
| tower_defense | 1 | 5 |

# Kenma 12 — observed-empty queen orbit

Parent: kenma-11-current-view-orbit. Corrects the no-bed requirement to World.bed == -1, as produced by World::sense from an observed tile with no pearl bed. Unknown cells (0) are rejected. The round+1 freshness check and activation logging from 11 remain. All strategy and geometric guards are unchanged.

The earlier hand-built fixtures repeated incorrect memory conventions: 10 used round instead of round+1; 11 still used bed=0 instead of -1. Their runtime snapshots remain frozen. The new test first feeds a protocol observation through unswbc::init/update and World::sense and requires an orbit activation, then tests 80 persistent synthetic turns and hazard guards. An actual game activation check is required before a full screen.

Status: prepared; no strength result. Reserved seeds 11–13 and new maps untouched.

Real-game activation smoke: **3–1/4**, zero errors, Weakhold/Australia both seats seed 1. All four replays activated the orbit (168,140 Weakhold;144,239 Australia log entries); replay diagnostics saved. This is integration evidence only. Full Carthage102 now running with unchanged runtime ab99829d2d7b5073fdac35682d1fba07d5ba6dea4e52b55db3f2bfcd2a7add68. Outputs main build/kenma/k12-orbit-smoke/ and k12-smoke-diagnostics.json.

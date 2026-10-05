# Kenma 12 — observed-empty queen orbit

Parent: kenma-11-current-view-orbit. Corrects the no-bed requirement to World.bed == -1, as produced by World::sense from an observed tile with no pearl bed. Unknown cells (0) are rejected. The round+1 freshness check and activation logging from 11 remain. All strategy and geometric guards are unchanged.

The earlier hand-built fixtures repeated incorrect memory conventions: 10 used round instead of round+1; 11 still used bed=0 instead of -1. Their runtime snapshots remain frozen. The new test first feeds a protocol observation through unswbc::init/update and World::sense and requires an orbit activation, then tests 80 persistent synthetic turns and hazard guards. An actual game activation check is required before a full screen.

Status: prepared; no strength result. Reserved seeds 11–13 and new maps untouched.

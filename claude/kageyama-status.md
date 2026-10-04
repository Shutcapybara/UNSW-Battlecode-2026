# kageyama — Phase 3 Data lane (Claude Opus 5.5)

Branch `r/kageyama` (private tree in the Cowork VM: shared object store of the main checkout, private index, plumbing
commits only — never touches main's index or HEAD). Tools `tools/learn/`. Heavy compute: the Cowork cloud container
(official engine 1.2.9 in-process, no Mac CPU) for engine truth runs; Mac-native only for corpus-scale builds.

## State (2026-10-04 11:30 UTC)

- Lane started. Read: macro, prompts, D-042..D-045, live-maps brief, BOARD tail, chongqing wrap-up, HB-1 finding.
- **Block rebuild (replay -> exact protocol block per dragon-turn): 401,434 / 401,434 identical** to the blocks the
  engine really sent (22 maps random walkers x3 seeds + carthage-05 self-play on 17 LIVE_MAPS_M2 maps).
- Encoder v1 (`tools/learn/encode.py`): blocks only -> int32 vector (49 cells x 23 channels, egocentric rotated, + 66
  scalars incl. queen block). Invariant tests pass. C++ twin not yet written.

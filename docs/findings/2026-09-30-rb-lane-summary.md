# rb lane (Aline lineage) — closing summary

30 September 2026 · Claude Opus 5.5 (desktop, Claude Code) · branch `r/rb` · lineage **Aline** (the prompt's
"Basquiat", renamed by the user). R-2b open exploration lane, blind: no programme conclusions were read (log in
`claude/rb-status.md`). Detailed reports: `2026-09-30-rb-lane.md` (versions 01–06) and `2026-09-30-rb-lane-2.md`
(07–23). The lane is closed at the user's request after version 23.

## Outcome

One accepted version: **`aline-17-sym-seal`**, on top of the lane parent `aline-01-nodevil`.

| vs aline-01 (D-032, seeds 1–3, both seats, 90 %) | pool, n = 480 | generalisation, n = 696 |
|---|---|---|
| economy (mean of p@50/100/150/250) | +0.025 [+0.005, +0.045] | +0.012 [−0.003, +0.027] |
| dragons@100 | +0.052 [+0.022, +0.083] | +0.076 [+0.045, +0.108] |
| length@100 | +0.048 [+0.023, +0.076] | +0.071 [+0.040, +0.104] |
| win rate | +0.061 [+0.025, +0.096] | +0.029 [−0.001, +0.058] |
| worst tier-2 change | h2h +7 % | wall +8.7 % |

- **Where it acts:** the gain is at p@50 and p@100; p@250 is flat.
- **Robustness:** under a fixture-cluster bootstrap the pool economy lower bound is −0.000. The dragon, length and
  win gains are the robust part.
- **Cost:** CPU max 9.08 M points per turn (budget 30 M), with no errors.

It combines two mechanisms, each measured alone first:

1. **Symmetry inference (13).** Each dragon works out whether the map is x-mirror, y-mirror or 180°-rotation
   symmetric, from terrain and bed countdowns it has seen, or adopts a teammate's decision received by sonar.
   It then fills in mirrored terrain, mirrored bed timings (the rules share a tile's countdown with its mirror) and
   mirrored portal pairs. This uses measured structure, not map identity.
2. **Ally right-of-way convention (07, the user's idea).** In a contested narrow space, the longer dragon keeps the
   cell; at equal length, the greater x (then y) keeps it. Every dragon runs the same program, so both sides agree
   without radio.

## What the lane learned

- **The parent's weakness is the opening on gated maps.** p@50 is 0.97 of the field median; trauma is at 0.17 and
  portals at 0.68, because the food sits behind portals whose landings are unknown.
- **Death churn dominates the pearl flow.** About 257 own deaths per game, mostly at length 2–3. The pocket farm
  (enter a dead end for its pearls, split the tail out, the head dies) is net positive: making it cheaper or dearer
  in either direction lost (03, 16, 18).
- **Information paid; pressure did not.** Symmetry, which supplies knowledge a dragon could not otherwise get, is
  the only mechanism accepted. Every raise in exploration or farming pressure either lost economy or bought pearls
  with dragons, length and wins:
  - bed waiting (02);
  - global dive value, three times (04, 12, 19);
  - dive value conditioned on starvation (23): fixed trauma (+0.333) but pool win −0.087;
  - spreading (20).
- **Conventions work in view and fail out of view.** The seal convention cut self and body deaths. Both portal
  right-of-way rules (05, 06) never fired, because a crossing's landing is invisible to both dragons. Every one of
  766 ally head-on collisions happened on a blind portal crossing.
- **Pearls eaten is not strength on its own.** 04 was +0.169 on economy and still lost dragons, length and wins;
  part of its gain was corpse recycling. The guards did the real work.
- **Ablations located the channels inside symmetry.** Bed timings carry the economy (15); terrain carries most of
  the wins (22). Terrain also causes the one known weakness: on dilemma, known kelp makes the planner avoid the
  1-wide fountain corridors (fountain eats before round 150: 50.9 → 32.6 per game).

## Versions at a glance

- **Tried:** 23 versions. **Accepted:** 17.
- **Rejected at screen or gate:** 02, 03, 04, 12, 15, 16, 18, 19, 20, 21, 22, 23.
- **Rejected as null on a direct replay check:** 05, 06.
- **Measured and used only as stack parts:** 07 and 13.
- **Never measured (superseded, dropped or withdrawn):** 08, 09, 10, 11, 14.

## Open threads for whoever picks this up

1. **A corridor-aware room check.** Value 1-wide pass-through corridors by both exits, or value fast-respawning
   beds by their rate. This would recover dilemma (about +0.013 on the pool mean) without losing symmetry's terrain
   gain.
2. **The end game.** Wins are decided by the longest dragon, and consolidation loses about half of the length it
   gathers. This gate cannot credit changes after round 250, so such a change can at best be a hold.
3. **A sonar probe before portal crossings (the user's idea).** It would address the 35 % of ally portal collisions
   where the victim was already standing on the exit. It is worth trying only as part of a crossing overhaul.

## Reproducing

- **Tools:** in `tools/rb/`. `gate.py run|score` runs and scores the panels; `queue.sh` runs a queue of candidates;
  `look.py`, `doom.py`, `show.py`, `allyh2h.py` and `postland.py` read replays.
- **Run data:** panel rows are under `build/rb/runs/` on the desktop host (not in git, per the artifact policy).
- **Re-score the accepted version:**
  `python tools/rb/gate.py score aline-17-sym-seal --parent aline-01-nodevil --seeds 1,2,3`.
- **Registration:** nothing has been registered. `aline-17-sym-seal/CANDIDATE.toml` carries its gate record.

# bokuto-61-mouth vs bokuto-46-regions: diff read (Sugawara, 5 Oct 2026 22:30Z)

Asked by the Chair in D-090 ("if time allows before upload; does not hold the trial"). Source: `../wt-bokuto/bots/{bokuto-46-regions,bokuto-57-queenblind46,bokuto-58-reachable,bokuto-61-mouth}` (worktree files, read 22:20Z). Read only; no runs.

## The diff (two files, three hunks)

| hunk | file:line (61) | what | who it affects |
|---|---|---|---|
| 57 queen-blind | bokuto.hpp:205 `if (no_dive && is_portal_edge && !in_vision(n)) return fail;` | survival test fails any path that crosses a *paired* portal into a cell the dragon cannot see | dragons with id&4095 ≤ 1 (queens), **all rounds** (`no_dive = is_q`, l.392) |
| 57 queen-blind | policy.hpp:1747 `if (sim.blind_cell >= 0 && queen_careful(w)) score -= dive_penalty` | soft policy penalty on the same move | careful queen |
| 58 reachable | policy.hpp:911–947, 1553 | region_target keeps a per-process `unreachable_sector_` mask; a sector whose target has no `long_route` is excluded; a standing migration is dropped when its route is gone | non-queen, non-crown, non-feeder (l.1550) |
| 61 mouth | policy.hpp:937–943 | migration target = junction of the dead-end corridor holding the sector's best bed | same as 58 |

Legality: all inputs are turn-start observation (`in_vision`, known terrain, occupancy) or per-process memory. No map identity beyond the atlas already ruled (D-080 §D). OK.

## Finding 1 (main): the queen can no longer escape through a known portal even when nothing else survives

`no_dive` is set once from `is_q` (l.392) and **never relaxed**. The fallback at l.469–478 relaxes `queen_mode` ("the strict rule finds nothing: relax it") but `after_path` still returns `fail` (turns 0) on every path through a paired portal to an unseen landing. The field comment (l.41) says "a blind portal dive fails the survival test (the queen, unless nothing else survives)" — the "unless" is not implemented for either the old UNPAIRED rule (l.203) or the new 57 rule (l.205). In 46 only unpaired dives were blocked; 57 extends the block to every paired portal whose far side is out of sight.

Consequence: a queen in a dead-end corridor whose only exit is a portal with an unseen landing scores every move as 0 turns and takes the 'g' fallback (best of zeros) — she stays and dies at a wall. That is the class Bokuto describes (21:18Z: fed queen cornered in a dead-end corridor, UNSW r354), and it fits both observed costs: qk2 queen wall deaths 10 (61) vs 3 (46), and the pool twin miss localised to Australia/Slithery through queen deaths (my 21:31Z line). 46 − 41 (no 57 rule) is −0.74; 61 − 41 is −3.68. 58/61 hunks do not touch the queen (region_target is skipped for `is_queen`), so 57 is the only direct queen change in the stack.

Status: **mechanism hypothesis from code, not replicated** (no time for the replay join before the look). Cheap test from frozen inputs: in 61's qk2 + pool replays, for each queen wall death, was a portal edge adjacent to her head in the previous 1–3 turns with its far cell outside her vision? Prediction: ≥ 5 of the 10 qk2 queen wall deaths, vs ≤ 1 of 46's 3. P(≥ 5/10) = 0.55.

Fix (one change, for Bokuto/Asahi as a post-trial build, not for this upload): in the fallback block (l.469), also set `no_dive = false` and re-run the single-step search when `best_mv.turns < K` — i.e. implement the comment's "unless nothing else survives". Expected effect: recovers most of the 61−41 pool gap on Aus/Slithery (P(61-fix − 41 pool > −1.5) = 0.45) while keeping 57's Maze-r120 gain (the blind landing stays last resort).

## Finding 2 (minor): 58's unreachable mask is permanent and partly spurious

- `long_route` BFS blocks cells by current occupancy (bodies with `vac` > distance) and stops at 2,500 queued cells. A sector marked unreachable while a body blocks a corridor, or beyond the BFS cap, stays excluded for the life of the process. With `migrate_max_dist` 60 and torus-Manhattan `tdist`, an open-map target beyond ≈ 35 steps can exceed the cap (diamond area ≈ 2d²) and be marked unreachable.
- l.940: a sector whose junction is within 4 of the head is also marked unreachable permanently (the dragon arrived, then can never migrate back).
- Effect is likely small (fewer long migrations; γ^40 ≈ 0.55 already discounts them) and may even help. Suggest a TTL on the mask (e.g. clear after 40 rounds) if 58's migration is kept. Not a trial issue.

## Finding 3: the mouth hunk does what it says

Junction substitution is guarded (`g_br`, bounds, `junction >= 0`). It changes where migrants stop, not the queen. No objection.

## Verdict

**Agree** with trial 5 going up as named (the Chair's call; this does not hold it). **Amend for the look and the next build:** read 61's Aus/Slithery queen deaths with the Finding-1 test (portal adjacent, landing unseen); if it holds, the next 61 build should relax `no_dive` in the fallback. Precedent: hard action masks vs. soft penalties with last-resort fallback (Lux/Halite rule bots; AlphaZero legal-move masks never remove the only legal move) — a safety rule that can empty the action set needs an explicit fallback.

Forecasts (log): Finding-1 test ≥ 5/10 qk2 queen wall deaths portal-adjacent 0.55; 61-fix − 41 pool > −1.5 0.45.

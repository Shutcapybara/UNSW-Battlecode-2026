# Phase 3 summary — UNSW Battlecode 2026, team 7 "Just Keep Swimming"

Written by the Chair (Ushijima), 6 Oct 2026 01:00Z, when the lead stopped all efforts. The binding record is
`docs/findings/2026-09-28-director-decisions.md`, D-046 (4 Oct, the Phase 3 charter) to D-094 (this stop).
Every statistic below is score minus Elo expectation per ranked game at anchor rating 1725, whole-series bootstrap
(1,000 draws, seed 7), 5th and 95th percentiles, unless it says otherwise.

## 1. Where things stand

- **Incumbent of record: `bokuto-18-queenfeed`, submission 17791** (D-088). Over its 60-game trial window it scored
  **+0.174 [+0.079, +0.282]** (32–28, 11 of its 12 series against teams rated 1725 or above), a performance rating
  near 1859. It is the only bot of the phase whose ladder interval excluded zero by a clear margin, and the only
  trialled bot that stores no copy of the ladder maps. The team rating stood at about 1840, rank 59, on the evening
  of 5 Oct (1725 a day earlier).
- **Active on the server at the stop: `bokuto-61-mouth`, submission 18078**, trial 5, activated 5 Oct 22:55:18Z. Its
  60-game look (about 02:30Z–03:00Z on 6 Oct) will not be read by anyone now. It stores all 17 ladder maps.
- **The Qualifiers and the Grand Final use new maps** (the lead, D-093). Stored maps help only on the ladder.
  **Recommendation for the final activation: 17791** (`bokuto-18-queenfeed`, folder `bots/bokuto-18-queenfeed`),
  because it carries no stored maps and its ladder result was earned without them. The one reason to keep 18078
  active longer is the seed, which is set by the rating at the seeding cutoff; that trade is the lead's.
- Restoring 17791 is one hub control (`hub-state/control/restore.json` with `previous` = 17791, `candidate` =
  18078) or one click on the contest website. Nobody has done it.

## 2. Every bot that held the live slot (D-089 §B, D-091, at anchor 1725)

| Submission | Bot | Stored maps | First 60 ranked at a series boundary | All ranked games |
|---|---|---|---|---|
| 14585 | `carthage-05-free-sprint` | 10 | −0.048 [−0.141, +0.039] | −0.022 over 1,095 |
| 16979 | `asahi-05-kz12-k16` | 10 | −0.305 [−0.418, −0.191] (44 games) | rolled back |
| 17388 | `kenma-03-pocket-queen` | 10 | +0.074 [−0.048, +0.197] | +0.060 [−0.010, +0.132] over 130 |
| 17530 | `bokuto-13-cull` | 10 | −0.041 [−0.132, +0.062] | −0.002 over 120 |
| **17791** | **`bokuto-18-queenfeed`** | **none** | **+0.174 [+0.079, +0.282]** | +0.170 over 65 |
| 17940 | `asahi-27-b13-reserve` | 10 | +0.093 [+0.004, +0.185] | +0.107 over 80 |
| 18078 | `bokuto-61-mouth` | 17 | running at the stop | |

What the trials say when read together (D-091, D-092): Kenma's reserve lines (one unit slot kept free) were worth
about +0.13 over `bokuto-13-cull`, and Bokuto's queen changes (queen fed from round 290, terrain safety from round
0, a dodge) about +0.08 more. Against stronger teams, in games that reached round 300, the queen survived to round
300 in 0.72 of games with the queen changes and 0.33 without. Neither step has a resolved interval on its own.

## 3. What we learned about the game and the field

- **Three targets** from 1,171 ladder games of the top ten (D-082, corrected by D-083): total length near 78 at round
  100 and 154 at round 300; queen alive at round 300 near 0.58; at least 70 % of round-300 leads converted. A
  round-limit game is decided by the longer live queen, then the longest dragon, then total length.
- **17791 against those targets** (checked by two lanes, D-089): queen alive at round 300 0.72 and 14 of 20 live
  leads converted, both at target; the economy is not. It totals 65 at round 100 against the top ten's winners'
  78, and grows 38 cells a game between rounds 100 and 300 against their 68 (all top-ten sides about 52). **The
  remaining gap is mid-game economy.**
- **Compute:** the limit is 100 M points per dragon per turn, not 30 M as our documents said for two days (D-087;
  checked on our own server games, where turns up to 99.5 M survived). Our bots use about 13 M, 3 M of it the
  output write. The search knobs of the current lineage do not spend more; a different search would be needed.
- **Seats:** drawn once per series; no measurable advantage once rating is held (D-087 §B).
- **Local panels do not rank bots the way the ladder does.** The 8-bot pool ordered our candidates wrongly at
  least four times. The two panels against opponents of our level (`qk2`, the two queen keepers, and the
  head-to-head against kenma-03) were closer. Any panel on the 17 ladder maps overstates bots that store those
  maps; for the tournament the panel that matters is one on maps nobody tuned on (`gen`, 29 maps, and the
  `gen-h2h` panel ordered in D-093, not yet run).
- **Learned components:** a direction prior cloned from Heartbreaker helped (Phase 2). Every later clone prior,
  including the ten-team clone with the best move accuracy (0.738), lost 6 to 14 points in play (D-068 to D-080);
  the line was paused. A value model failed out of sample (R1, D-057). No learned component was promoted in
  Phase 3. The rung ladder of the charter stopped at R2.
- **Stored maps (atlas):** two twins lost about 4.4 points to a 17-map atlas on the pool, because dragons that know
  the whole map route through the same portals and collide (D-087 §C). Bokuto later loaded terrain and beds without
  portal pairs; that is what 61 carries.

## 4. Where the material is

- **Bots** (`bots/` on main): `bokuto-18-queenfeed` (incumbent), `bokuto-61-mouth` (trial 5), `bokuto-41-atlas0`,
  `bokuto-46-regions`, `bokuto-13-cull`, `asahi-27-b13-reserve`, `kenma-03-pocket-queen`, `kenma-28-harvest-reserve`,
  `carthage-05-free-sprint` (rollback reference), and the component twins carded on 5 Oct. Bokuto's later material
  (`bokuto-48` to `bokuto-62`, including the queen fixes 57 and 58 that 61 contains) lives in its own clone
  `../wt-bokuto`; the main repository's `r/bokuto` stops at 8dbbd3ed (5 Oct 04:59Z) — see §6.
- **Decisions and registers:** the decision log (D-046 to D-094), `docs/learning/registry.md` (REG-000 to REG-017),
  `docs/learning/ladder.md`, `docs/learning/calibration.md` (forecasts and Brier scores), `docs/learning/proposals/`,
  `docs/learning/reviews/` (Sugawara's checks), `docs/learning/trials-1725.md` (Daichi's table), `docs/hub/BOARD.md`.
- **Tools:** `tools/hinata/look.py` (frozen curve block for a trial look), `tools/hinata/curves.py`,
  `tools/hinata/r100col.py`; Asahi's job runner `tools/asahi/jobd.py`, panels and cards (`tools/asahi/`), the probe
  with the 60 M gate; Daichi's `tools/daichi/live_monitor.py` and trial tables; Kageyama's bed emulator and oracle
  (`tools/learn/`), the encoder with its C++ twin, the teacher rows manifest.
- **Data:** the replay corpus (`public_replays/corpus/`, about 166,000 replays, not in git), teacher rows
  (`build/learn/kageyama/teachers_v1/`, not in git).
- **Hub:** the daemon on the Mac (pid 40226) stopped at 01:00:15Z on 6 Oct with a keyboard interrupt (stopped by
  hand). Its last keeper pass (00:58:09Z, commit 721836cc8) pushed main up to D-093. The final commit of this
  summary and the merge of the lane branches did not run; see §6.

## 5. What we would do next if work resumes

1. Activate 17791 for the tournament (or after the seeding cutoff).
2. Run `gen-h2h` (candidate against 17791 on 29 unseen maps, 174 games) for any challenger; the tournament plays
   unseen maps.
3. Attack mid-game economy without stored maps: the measured classes are length-3 dragons dying at corridor ends,
   the unit cap, and openers that wander (D-086, D-091).
4. Spend the compute budget: an enemy-response lookahead or rollouts at 25–50 M points a turn, behind a hard cap.
5. The RL route assessed for the lead (D-086 §F): a per-team clone fine-tuned against clone opponents, with a JAX
   port of the engine as an optional accelerator; no training was approved.

## 6. Loose ends at the stop

- **The final commit and merge are not done.** The Chair wrote this summary, D-094, the stop line on the BOARD and
  the final status into the main working tree, and left a keeper request in `hub-state/control/git.json` (commit
  with a 1-minute quiet time, fetch, merge `r/kageyama`, `r/asahi`, `r/daichi`, `r/bokuto`, `r/kenma`, `r/tanaka`,
  `r/nishinoya`, `r/shenzhen`, `r/ushijima`, push). The hub was stopped before it ran. Restarting the hub once
  carries it out; otherwise the commands are in the Chair's final message to the lead.

- **Unmerged work:** Bokuto's clone `../wt-bokuto` holds commits up to at least fecd1af7a that the main repository
  does not have. The keeper can merge only what is in this repository; someone must push `r/bokuto` from that
  clone into this repository or to GitHub.
- **Uncommitted analyst work:** Shenzhen's units 36–39 (D-074 §C), if anyone still wants them.
- The Chair's device shell failed with a permission error all of 5 Oct; the Chair worked by file copy. The old
  disk image `~/Desktop/sessiondata.img.bak` can be deleted.
- Scheduled tasks disabled at the stop (not deleted, so their history is kept): Chair unit 43, Asahi's 01:15 check,
  Hinata (hourly), Daichi (hourly), Sugawara (hourly). The older Chair hourly unit and the git-coherence task were
  already disabled.

## 7. How the programme worked, and what to keep

- The second-lane check (D-083 §A) caught at least six errors before they became decisions: side-swapped queen
  columns, a survivorship reading, a wrong anchor for 17388's statistic, an overstated exit-split finding, a
  threshold read as a pass on one bootstrap draw, and a growth reading that was a lower start catching up.
- Trials back to back on the ladder cost nothing in rating (each submission keeps its own) and were the only test
  that decided anything. One 60-game window has an interval of about ±0.10 a game, so only large differences show.
- The Chair's own probability forecasts carried little information: five too optimistic, then two too pessimistic
  (`calibration.md`).

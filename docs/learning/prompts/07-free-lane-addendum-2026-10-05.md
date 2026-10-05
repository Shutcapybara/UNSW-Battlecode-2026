# Free lane addendum, 5 Oct 2026: what a new builder needs to know today

Read `07-free-lane.md` first; its goal and rules stand. This page replaces its "Facts that will save you time"
where the two differ. Written by the Chair (Ushijima) at 14:25Z; the decision log (D-075 to D-084) is the source.

## Where we stand

- Four bots have held the live slot today. On the ladder none is separable from the others: the old incumbent
  14585 (`carthage-05-free-sprint`) −0.043 a game against Elo expectation, `bokuto-13-cull` −0.054 over 120 games,
  `kenma-03-pocket-queen` (incumbent of record, 17388) +0.005 over 129. `bokuto-18-queenfeed` (17791) is on trial.
  We are near Elo 1780, rank about 70. The top ten are more than 400 points above.
- Each submission has its own rating, so a ladder trial costs the incumbent nothing. A trial is 60 ranked games,
  about three hours. Qualification: a passing deploy probe and a same-host pool not below `carthage-05-free-sprint`
  (paired 5th percentile above −5 points). Live ops (Daichi) uploads; you never touch the server.

## What the top ten do that we do not (1,171 ladder games, checked by a second lane)

| | Total length, round 100 / 300 | Queen alive at round 300 |
|---|---|---|
| Top ten, winner | 78 / 154 | 58 % |
| Top ten, loser | 61 / 111 | 37 % |
| 14585 | 63 / 128 | 6 % |
| `kenma-03-pocket-queen` | 60 / 116 | 12 % |
| `bokuto-13-cull` | 55 / 103 | 50 % |

- **Three targets for a candidate:** total length near 78 and 154 at rounds 100 and 300; the queen (the team's
  original dragon) alive at round 300 in about 58 % of games; at least 70 % of the games led at round 300 won.
  No bot of ours has both the economy and the queen. A candidate that buys one with the other has not gained.
- A round-limit game goes to the side whose queen is alive and longer, then to the longest dragon, then to total
  length. The top teams hide the queen at length 2–3 until about round 250–300, then feed her (allies die beside
  her) to 30–60. Our queen's extra deaths are at walls (portal dives, single-exit cells), not in fights.
- Between rounds 100 and 300 the top ten's winners add 75 cells; we add 48 to 65. That mid-game growth is the
  largest gap and nobody has attacked it yet.

## What measures what

- **The pool (8 old bots × 17 maps × 2 seats) cannot see the ladder's game.** Its opponents hold 41 and 81 cells at
  rounds 100 and 300 and almost never keep a queen, so every bot leads and converts about 90 %. Pool gains of +2.6
  and +5.5 points have gone to nothing or worse on the ladder, and a bot 2 points below on the pool did no worse.
  Treat the pool as a safety floor only.
- Read candidates on `qk2` (against `bokuto-13-cull` and `kenma-28-harvest-reserve`, the two local bots whose
  queens survive) and on a 102-game head-to-head against the incumbent, with the queen and economy columns
  (queen alive at rounds 100, 200, 300 and the end; queen length at the end; total length at rounds 100 and 300;
  round-300 leads converted; queen deaths by cause). Even these have disagreed with the ladder once.
- **The ladder trial is the test.** Ask for one early.
- Mac jobs: one line on `docs/hub/BOARD.md` to Asahi: `JOB <bot folder under your worktree> : <pool | probe | gen |
  h2h vs <bot>>`, up to two an hour. Every card comes with the columns above.

## What exists to build on (copy, never edit)

- `bokuto-13-cull`: queen caution, hiding and feeding late; allies yield to the queen; corridor harvesting; a spare
  length-2 dragon culls itself at the unit cap. Best queen, smallest economy.
- `asahi-27-b13-reserve`: the same plus two lines that keep one unit slot free for non-queens; on the pool this
  restores 11 cells of total length at round 300. Trial 4.
- `bokuto-18-queenfeed`: queen fed from round 290, queen terrain safety from round 0, the reserve lines. Trial 3.
- `kenma-03-pocket-queen`: a sealed-pocket rule that keeps the Schooltime queen alive; otherwise carthage-05.
- A terrain atlas of all 17 live maps cost 4.4 points on the maps where it was exact (`bokuto-17-atlas`); do not
  repeat it without finding why.
- Five hidden bed layouts (14.5 % of ranked games) are rebuilt in `maps/live_var/`; Asahi's cards include them.
- Tools: Hinata's curve table and matched comparison (`tools/hinata/curves.py`, `p06_column.py`), Sugawara's
  feeding census (`docs/learning/reviews/D-080-queen-feeding-sugawara.md`), Bokuto's status file for mechanisms.

## Pitfalls that cost us hours today

- In replays the queen is the team's lowest initial dragon id from the map's DRAGON lines, not id 0 or 1 by side.
- Keep replays, results and virtual environments under `build/<name>/` on the mounted folder, never in the VM's
  own home or `/tmp`: the session disk is 9.8 GB and shared.
- Append to `docs/hub/BOARD.md` from the shell with `>>` only, with the time from `date -u`. Never write it
  through file staging.
- Commit early to `r/<name>`; ask the Chair on the BOARD for a push.
- A cloned direction prior (six variants) and the isolated one-switch queen builds on carthage-05 all failed.
  Mechanisms have worked only inside a bot built around them.

## Correction, 5 Oct 18:18Z (D-087): the compute limit is 100 M points a turn, not 30 M

- Checked on our own server games (turns up to 99.5 M survived; cuts at exactly 100,000,000) and in the local
  sandbox. A turn that exhausts its points kills the dragon. **Working ceiling: the probe's highest turn, first
  turn included, at or below 60 M.** A bot that scales its search with the budget needs a hard internal cap.
- Our bots spend about 9.8 M on compute and 3.0 M on the output write each turn. So about five times the search,
  or a model of tens of millions of points a turn, now fits. Nobody here has measured a bot at that size.
- Local games slow down with the points spent. Asahi screens such bots on `qk2` and the head-to-head first.
- Atlas bots: two twins (`bokuto-17-atlas`, `bokuto-35-knownbeds`) lost about 4.4 points to the atlas, and on 35
  the cause is collisions between our own dragons (ally head-on deaths +86 %). An atlas bot goes to trial only if
  it is not below its own atlas-off twin on the pool.

# Nara status — glm/nara, P2-A analyst

Worktree `../wt-nara`, branch `r/nara`, tools `tools/nara/`. Host: the Mac. I am **not** the replay lead: I read the
corpus/store, I never pull. Findings: `docs/findings/2026-10-01-nara-era-and-queen.md` (unit 1).

## Unit 1 (1 Oct, ~13:50 UTC) — era + queen, done

1. **Era boundary established**: the live server switched to 1.2.3 rules in the 1 Oct **05:54–09:23 UTC maintenance
   window** (no games in between; last old game 05:53:35, first new game 09:23:44 = g800028). Sprint formula
   verified exact on 44,825 moves: `paid = steps − min(steps, ⌈L/4⌉)`, 0 violations. Proposed store tag:
   `post iff started_at ≥ 2026-10-01T09:00Z`.
2. **Queen rule pinned down and verified** (201 rl games, 0 violations): queen = the team's **original lowest-id
   initial robot**; dead → length 0; **no inheritance** (5 discriminating games reject sibling inheritance; 3
   reject living-lowest-id). A living queen of length 8 has beaten an opponent's longest of 39.
3. **Queen anatomy** (842 post-era side-games): nobody protects it — survival to r490 is 2–13 % by cohort, median
   queen never exceeds length 4, dies <r150 in ~90 % of sides. **Cutlery (rank 1) already protects + feeds** (5/12
   games, all ≥8). 10 % of post-era rl games were queen-decided; 5.5 % flipped vs longest.
4. **Opening pre/post**: field flat at r50 (−1 %), total@100 **+12 %** (retention; long dragons move free).
   Post-era references NOT stable yet (58–116 field sides/map vs 1,500 pre); rebuild after the store catches up +
   ~300/map. Schooltime pearls@100 +79 % is the outlier to watch.
5. **Operational bug found**: `frame.py` decode winner is pre-change (longest→total); store `won`/`decoded_winner`
   and every local-panel W-L-D under 1.2.3 is wrong in queen-decided games (~5.5 % of rl games). Patch text in the
   findings §5 — for the replay lead / tools owner to apply.

## Live hypothesis list (mine; weights proposed to the director)

- **N1 queen protection, 0.7** — keep own original queen alive to r490; ~7–10 pp on rl maps at current field death
  rates. Falsifier: elimination-map wins drop on a 160-game regime-split panel. Suits any tester; smallest
  mechanism with the largest era-specific payoff. Stack with hb1-21's regime selector (round-limit detector).
- **N2 queen hunting, 0.4** — kill the enemy's original queen (spawn geometry + L38 symmetry). Identification from
  partial views is the crux.
- **N3 opening-era continuity, 0.6** — pre-era opening targets stand; sprint pays mid-game. Falsifier: post-era
  field pearls@50 moves >10 % on ≥4 maps after the rebuild.

## Next unit (queue)

1. Read the board + other statuses; answer anything addressed to me.
2. When the replay lead rebuilds the store with post games: re-derive per-map field medians (say if stable),
   Q3-style top10-vs-field component table for the post era, transits@50 (early portal use — not yet measured
   post-era).
3. Queen feeding anatomy v2: do protectors feed the queen (eats by q0 late) or just park it; queen survival vs
  opponent awareness (are queens hunted once visible?); pre-era baseline for queen survival (is top10's 13 % new?).
4. Opponent anatomy on demand (HB_TEAM method).

## Notes to self

- The corpus decoder stack needs `sys.path = [tools/leviathan, tools/analysis/features]` then `from frame import
  decode`; team values in events/rounds are **'A'/'B' strings** (not 0/1 — cost me two bugs).
- `paid` (sprint cost) is only trustworthy for moves whose actor survived the round.
- Sample caps: probes cap 12 games/team (post) / 6 (pre) with seed-fixed shuffle; era probes bucket by 2 h.
- Team 7 has no post-era corpus games; "us post" comes from the testers' panels until the executor leaves shadow.

# D-085 §B check — Bokuto's exit-split finding and bokuto-27's diff (Sugawara, 5 Oct 2026 15:35Z)

**Verdict: amend.** The code-path finding is right and the diff is clean, but the count attributed to it is not.
The order fix can reach at most ~7 of the 81 cells a game we lose to walls in excess of opponents; the larger
shares are length-3 walkers (no split exists at any order) and walkers at the unit cap (blocked in 17530 by the cap,
and in 18/27 one unit earlier by the reserve). 27 is a fine trial candidate; it is not "the mechanism for the growth gap".

## Inputs

- 17530 (bokuto-13-cull) ranked games requested 08:15–12:40Z, 120 games (all post-m2 era; single map_era).
  `frame.decode` deaths r100–300, cause `wall`; split events of the dying id in rounds r, r−1 (child_len ≤ 2 =
  production split). Code `build/sugawara/exitsplit/{census.py,summ.py,save.py}`; rows `rows.jsonl` sha256 fe124cca6d56.
- Diff `wt-bokuto/bots/bokuto-18-queenfeed` → `bokuto-27-exitsplit`: policy.hpp l.1707–1730 only (+ README, build).

## Replication

- Wall length r100–300 per game: **us 132.1, opponents 51.3** (Bokuto: 131 / 51) ✔.
- Our wall deaths of length 3–5: 2,482 events, 69.8 cells/game = 53 % of our wall length (Bokuto: 41 %; definition differs).
  Classified:

| class (us, len 3–5 wall deaths, r100–300) | events | share | order fix helps? |
|---|---|---|---|
| length 3, no split before death (no split exists for L3: `tyr_escape_split` needs len ≥ 4) | 1,139 | 46 % | no |
| head part after a production split (child 2) within 1 round | 671 | 27 % | yes, saves len − 2 cells |
| whole, team at ≥ 63 units | 508 | 20 % | no (cap; in 18/27 also the reserve) |
| whole, below cap | 164 | 7 % | no (no exit for the child / guard) |

- Opponents: 648 such events, 552 of them L3-whole; 7 after a production split.
- **Upper bound of the order fix:** sum over production-split head parts of (len − 2) = **7.3 cells/game [5.5, 9.1]**
  (game bootstrap, 1,000 × seed 7, 5–95 %), 5.7 events/game. Head parts after a production split are length 2 in 867
  cases (L = 4: both orders give a 2-child — no difference) and length 3 in 657 (saves 1 cell). This is an upper bound:
  it assumes every one of these was a dead end and that the L−2 child walks out.
- Whole deaths at the cap with len ≥ 4: 25.8 cells/game beyond the 2 an escape would lose — 3.5 × the order fix.
- By map (cells/game): order-fix bound Slithery Fight 36.7, Autarky 29.9, Maze 16.7, weakhold 11.8 (11 games, 2 wins;
  wall 50/g), Around UNSW 10.0; elsewhere ≤ 7. **Portals: 219 cells/game of L3-whole wall deaths** (73 events/game) — the
  single largest block, untouched by 27.

## Code path (read)

- 18: `decide()` scores production (`tyr_split_option`, split_value) and opening splits first; the escape split is only
  tried if best_score is still < −900 afterwards. So when the production split is legal it always wins at a dead end. ✔
- 27: if all moves < −900 and `tyr_escape_split` > 0 → escape (child = len − 2) and skip both other splits. One hunk ✔.
- Note A: "< −900" is not only "no move survives": the queen's threat_mult/danger terms and −950 head-adjacent moves also
  land there. For non-queens the guard (`bokuto.hpp apply_impl`) replaces the split with a step that survives K turns,
  so threat-only cases become a step or a cell-neutral split. Acceptable.
- Note B (queen): the parent keeps the id, so a stuck queen that escape-splits dies at length 2 (18: at len − 2).
  Same outcome (dead queen); from r290 `queen_dodge` forced mode replaces her splits anyway. No new queen risk.
- **Note C (reserve):** in 18/27 the guard sets `reserve_block` for any non-queen split at units ≥ limit − 1 and forces a
  move — so at 63 units the walker still dies whole. The 17530 census (no reserve) understates the cap class for this
  lineage. A one-line follow-up would exempt `why == 't'` from the reserve block (an escape split adds no unit net when
  the head part dies the same turn, though it does need the free slot for one round).
- Inputs legal (own body, terrain, occupancy; no map identity).

## P(pass) and effect

- 27 meets the D-085 §C conditions (probe pass + paired pool 5th pct > −5 pp vs c05): **0.85**.
- Paired vs 18 on local panels, total length r300 ≥ +5 cells: **0.30** (upper bound 7.3 is ladder-weighted; carthage-05
  shares the bug, Bokuto notes, so qk2 can't show it either).
- Beats the incumbent of record by > 0.03 if trialled: **0.25** (same as the base rate of today's trials).

## Dissent / recommendation

1. Record the finding as "the order bug costs ≤ 7 cells/game (≈ 9 % of the 81-cell wall excess)", not as the mechanism
   for the growth gap. D-085 §B's "41 % … because decide() prefers the production split" conflates Bokuto's 14:36Z
   (at the cap) and 14:46Z (order) descriptions.
2. Bigger targets by the same census: **L3 walkers dying whole** (Portals 73/game, Slithery, Maze) — why are corridor
   walkers length 3 where opponents' are length 2 (opp L2 wall deaths 1,976, L3 612; ours 1,730 / 1,860)? And the
   cap/reserve class (Note C).
3. Wall length is gross, not net: corpses are food (`eats.origin == ally_corpse`). Before ranking wall classes, report
   the share of our wall-dead cells re-eaten by our own dragons within 20 rounds, both sides.

Precedent: Halite III ships at the cap / dropoff saturation — fix the binding constraint (cap) before the ordering.

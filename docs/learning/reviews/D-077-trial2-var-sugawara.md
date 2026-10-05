# D-077 trial 2 (`bokuto-13-cull`): pool replication, out-of-sample read on the variant block, and an atlas note — Sugawara (unit 21, 5 Oct 2026 07:27–07:45Z)

Verdict on D-077 §A: **agree.** No change to the trial order. Two additions for the reader of trial 2 and of the leave-one-out.

## 1. Pool replication (frozen inputs: Asahi's index files, seed 1)

Source: `wt-asahi/build/asahi/runs/<bot>/<fp>/pool/index.jsonl`, paired on (map, opp, seat), seed == 1 only, map × opp cluster bootstrap 1,000 × seed 7, percentile 5–95.

| bot | n | wins | vs carthage-05 (226) |
|---|---|---|---|
| bokuto-13-cull | 272 | 241 | **+5.51 [+1.84, +8.82]** (Asahi +5.51 [+2.19, +9.19]; interval method differs) |
| asahi-05-kz12-k16 | 272 | 233 | +2.57 [+0.37, +4.78] |
| bokuto-04-queen | 272 | 226 | 0.00 [−5.51, +5.15] |
| kenma-03-pocket-queen | 272 | 220 | −2.21 [−4.41, 0.00] |

Replicated.

## 2. Out-of-sample read: the live_var block is already on disk

Asahi's D-075 §F variant block (`…/var/index.jsonl`, 5 hidden layouts × 8 opponents × 2 seats, seed 1; files written 07:22–07:27Z) exists for c05, k16, 13-cull, and partly kenma-03 (32 of 80). These maps were merged at 06:43Z; `wt-bokuto` has no `maps/live_var` and 13-cull's tree was copied at 06:46Z, so **Bokuto never developed against them**. This answers part of D-077 §A's caution ("some of the gain may be fitted to the pool").

| bot | n | wins | vs carthage-05 (63/80) |
|---|---|---|---|
| bokuto-13-cull | 80 | 72 | **+11.25 [+1.25, +21.25]** |
| asahi-05-kz12-k16 | 80 | 62 | −1.25 [−5.00, +2.50] |
| kenma-03 (partial) | 32 | 30 | 0.00 |

13-cull by layout (13-cull / c05, of 16): devil_b 16/14, dilemma_10 10/12, queen_of_spades_b 16/16, schooltime_open4 **15/7**, slithery_fight_b 15/14.

Reading:
- The gain survives on unseen layouts, but **+8 of the +9 is one map, schooltime_open4** (the queen cage on a Schooltime layout: consistent with the 16/16 queen-alive on Schooltime in the pool). Excluding it: 57/64 vs 56/64, +1.6 pp. The non-Schooltime part of the gain is not confirmed out of sample at n = 64; it is not refuted either (the pool's non-queen gains — Slithery, Weakhold, Trauma — mostly do not have variants here).
- k16 is +2.57 on the pool and −1.25 on the variants; k16 failed live. One case, not evidence of a rule; worth tracking whether the var block predicts live better than the pool once trial 2 lands.
- These are pool-card-convention numbers read post hoc by me; Asahi's own var card is the record.

P(trial 2 primary statistic exceeds 14585's reference by > 0.03) — owner forecasts are closed (D-072 §B); for the record only, I'd put it at 0.65 (Chair 0.75): the Schooltime-family cage fix is about 12.5 % of ranked draws plus ~3 % schooltime_open4, and that part looks real; the rest is pool-fitted until shown otherwise.

## 3. Mechanism note: the atlas and the hidden layouts (inherited, not new to 13-cull)

- `world.hpp::atlas_try` (byte-identical in carthage-05, bokuto-04, bokuto-13-cull) matches the first view's **terrain** against 10 public maps and then sets, for every cell, `bed[c] = template bed ? 1 : −1` and `atlas_bed[c]` = template bed class. Observation overwrites a cell when seen (`sense`, l.357–362).
- On the hidden layouts the terrain is the template's: EDGE lines identical for devil_b, queen_of_spades_b, slithery_fight_b, dilemma_10 (schooltime_open4 differs on 4 edges, so the match probably fails there), while TILE (bed) lines differ on 102 / 138 / 365 / 32 rows. So on about **11.4 % of ranked games** (Kageyama's shares for those four) every unseen cell carries the template's bed belief: real beds marked "not a bed" until seen, template beds that are not beds marked "bed".
- New in the Bokuto layers: `bokuto_branch.hpp:122` counts "never observed but known fast bed from the atlas" toward the branch gate, so 13-cull uses the template prior in one more decision than c05.
- Legality: the atlas is terrain-matched structure, compiled from public maps; it predates the "no map identity" rule and is not re-litigated here. The point is **train/deploy skew**: the pool contains only template layouts, so the pool cannot see this cost; the var block can. On the var block 13-cull is level-to-ahead on the four atlas-matched layouts (57/64 vs 56/64), so no measured harm. No action now.
- If a later card wants to test it: one change, "atlas sets terrain only; bed beliefs from observation" (or: drop `bed[c] = −1` for non-template cells), read on the var block with both totals. Precedent: Halite/Lux bots that hard-code map priors lose on rotated seeds; the standard fix is to keep geometry priors and learn resource priors online.

## Dissent / limits

- n = 80 on the var block, one seed, eight opponents; the interval is wide and almost all mass is one layout.
- I did not decode replays; reasons by layout not checked this unit.

# Q-sugawara-01 — The queen: diagnosis, mechanisms and build order (owner: Sugawara, D-072 §C)

Written 5 Oct 2026 04:36Z. Owner's plan, not a card (D-072 §C: no card or review is needed for a screen).
Inputs are frozen and re-runnable: `public_replays/corpus/index.jsonl` as of 04:27Z, `tools/analysis/features/frame.decode`,
team 7 games started ≥ 2026-10-05T02:13Z (16979, 47 decoded), and the last 70 decoded games of teams 213 and 507 since
2026-10-04T12:00Z. Outputs: `build/sugawara/q16979.json`, `build/sugawara/qtop.json` (one row per game, queen death round,
cause, length, final queen lengths). Post-m2 era, live maps; numbers are counts, no intervals (descriptive).

## 1. Diagnosis (16979, 47 ranked games, W–L 18–29)

- **Queen-decided: 0 W, 19 L. 19 of 29 losses are queen-rule losses** (Schooltime 5, Trauma 3, Maze 2, Around UNSW 2,
  Australia 2, one each Portals, Slithery, Default, Dilemma, Autarky). Our queen is alive at the end in 4 of 47 (all
  elimination wins).
- **Our queen dies small.** Length at death 2–4 in 43 of 43. Causes: enemy head-on 22, wall 11, self 9 (5 of them the
  Schooltime cage at r0), ally 1. Death round: r0 6, r25–99 16, r100–199 8, r200+ 13.
- **Opponents' surviving queens in our queen losses:** lengths 2, 3×6, 6, 8, 9, 9, 10, 10, 11, 13, 22, 24, 30, 30.
  So a queen of length ≥ 4 that merely survives wins 7 of 19 (incl. the 5 cage games); the other 12 need a queen that also
  grows to 6–30.
- **What the keepers do.** Team 213 (31 games, 25 W; queen-decided 11–1): queen alive in 12 of 20 round-limit games, and the
  surviving queen **is the team's longest dragon in 10 of 12** (queen 23–80). It also splits its queen to length 2 at r13,
  then regrows it. Team 507 (39 games; queen-decided 5–1): 6 of 8; two queens are the longest (52, 67), four are hidden
  length-2–3 queens. Two archetypes: the **crown queen** (213) and the **hidden queen** (507, Kenma's pocket).
- **Queen identity is legal and structural.** On all 16 live maps the initial dragons alternate team (ABAB… / BABA…), so the
  two queens are ids 0 and 1. `w.me <= 1` (as in kz12, Kenma and Bokuto) is correct on today's pool; it is a map-structure
  assumption, not map identity. Guard for later maps: a dragon with id ≤ 1 that sees an ally head with a lower id at r0
  drops the role.

## 2. Read of the material (D-071 §C.1, D-072 §C)

- **`kenma-03-pocket-queen`** (`../wt-kenma`, parent carthage-05, 47-line `kenma_pocket.hpp` + 9 lines in main):
  three mechanisms, not one switch. (a) *Pocket proof:* a flood from the head over known non-portal terrain; a pocket is a
  sealed component of ≤ 8 cells (unknown or portal edge → not a pocket). Only the Schooltime cage meets it on today's pool.
  (b) *In-pocket queen:* the queen splits to length 2 when length ≥ 4 and a unit slot is free, otherwise takes the
  legal single step that eats least. (c) *Donor cull:* a non-queen dragon whose own sealed pocket contains the queen's head
  plays `SPLIT 1` (dies) so the queen has room. (d) *Global reserve:* every non-queen dragon plans with `limit − 1` on all
  maps, all game. (a)–(c) are one switch (structural, acts only in a proven pocket). **(d) is a second switch, acts on every
  map, and is the likely cause of its pool deficit (220–52 vs 226–46; Kenma's own same-host diagnostic: UNSW 9 vs 14,
  Australia 11 vs 14).** No map identity.
- **`bokuto-04-queen`** (`../wt-bokuto`, parent carthage-05): a survival guard (`bokuto.hpp`, exact K-turn search over the
  own body; K = 4 for the queen, which also keeps off cells adjacent to other heads; cage split; a 1-slot reserve when
  splitting), dead-end branch gating (`bokuto_branch.hpp`), and a **queen block in `policy.hpp`**: the queen stops
  splitting after r60, never attacks or hunts, pays 3× the enemy-head threat cost plus 6 for ending on a cell an enemy head
  reaches next turn, 40 for a blind portal dive, and **from r250 a live queen is the crown** (allies feed it; nobody else
  claims). This is the 213 archetype. Reported 58–44 vs carthage-05, queen-decided 9–1 (lane harness, unverified; no pool
  panel).
- **`asahi-01-cage-cd-e0`** (C+D only): pool +2.21 [−0.37, +5.15], q_dec 5–4 vs parent 0–5, tier-2 `death_invalid` 0 → 8.1/1k
  (flagged), Portals −12.5. Shenzhen 03:50Z: C+D gets the cage queen past r0 6/6 and wins 5/6.

## 3. Mechanisms, one switch each, on `asahi-05-kz12-k16`

| id | switch | acts on | expected prize (ladder, from §1) |
|---|---|---|---|
| Q1 | **Cage**: Kenma (a)+(b)+(c) — pocket-proof, in-pocket queen split/step, donor cull. No global reserve. | proven sealed pockets ≤ 8 cells (Schooltime today) | 5 of 19 queen losses; ≈ 1 ranked game in 8 is Schooltime |
| Q2 | **Crown queen**: Bokuto-04's `policy.hpp` queen block only (split stop after r60, no attack/hunt, threat ×3 + danger 6, dive 40, queen is crown from r250, feeders accept it). No guard, no branch gate. | every map, the queen only (plus feeders after r250) | the other 14; needs survival *and* growth |
| Q3 | **Queen survival guard**: Bokuto's `Guard` restricted to the queen (K = 4, keep off cells adjacent to heads), non-queens untouched, no reserve | every map, the queen only | wall (11) and self (4 non-cage) deaths |

Why Q1 rather than C+D: C+D raised `death_invalid` to 8/1k and cost Portals 12.5; Kenma's (a)–(c) is gated by a proof and
cannot act off-pocket by construction. Why not (d): it is the measured cost and is not needed when the donors cull.

## 4. Order and gates

1. **Asahi builds Q1 = `sugawara-q1-cage` on asahi-05-kz12-k16** (copy `kenma_pocket.hpp`; in `main.cpp` add the donor
   check and the `kenma::queen` override after `pol.decide`; omit the `w.limit − 1` lines). Golden parity off-pocket: the
   build must equal the incumbent on every pool fixture except Schooltime (a parity run is the cheapest correctness test:
   any non-Schooltime difference is a bug). Then the seed-1 pool with queen columns.
   Pass: Schooltime queen-decided W > L vs parent, pool Δwin point ≥ 0 (D-055 §A).
2. **Q2 on top of Q1** (`sugawara-q2-crown`), seed-1 pool with queen columns. Pass: pool queen-decided W > L vs Q1 and pool
   Δwin not below Q1's lower bound. **The pool is weak here:** its opponents rarely keep a queen (parent's pool q_dec is 0–5
   in 272), so the pool tests the cost, not the prize. Add a **queen-keeper panel**: Q2 vs `bokuto-04-queen` and
   `kenma-03-pocket-queen`, 17 maps × both seats, seed 1 (68 games each), read queen-alive-at-limit and queen-decided W–L.
3. **Q3 on top of Q2**, same two readings.
4. A build that passes goes to a live screen on a one-line request (D-072 §C). Ladder reading: queen-decided W–L and queen
   alive at the limit, against 16979's 0–19 and 4/47.

## 5. Risks

- Q2 may cost economy: the queen stops producing after r60 and the crown moves to a dragon that hunts nothing. Watch econ~
  and units@100.
- Feeders dying into a cautious queen that keeps away from heads may starve it; if Q2's queen is alive but short at the
  limit (≤ 6 median), the next lever is feed range, not safety.
- `w.me <= 1` breaks on a map whose dragon list is not alternating; add the r0 guard in §1.
- 16979 may be rolled back at the D-052 §B look (Daichi). The switches port unchanged to carthage-05 (both are carthage-05
  descendants; kz12 touches only the queen's one-step veto, which Q2 leaves in place).

## 6. Addendum after reading BOARD to 1202 (04:36Z)

- **Shenzhen 04:27Z (live lean table, 7,702 side-games, not audited) agrees with §1 on a wider base:** our queen peaks at mean
  length 5.8 (top ten 10.8; surviving top-ten queens 23.6), is about length 1 by r100 and dies at median r74; on kelp-dense
  maps the length-2–3 queen dies at a wall (weakhold 7/7, Trauma 6/6, Maze 5/6, Portals 4/5). Team split rates are normal:
  **it is the queen that splits itself down.** H-SZ77: no queen split below length ≈ 12 (cage split exempt).
- **So Q2 is split into its simplest part first.** Q2a = `sugawara-q2a-grow`: the queen never splits if the parent part
  would be shorter than 12 (cage/pocket split exempt). One constant, one condition in the two split generators (the lines
  Bokuto-04 gates at policy.hpp ≈ 1129 and 1176). Q2b (Bokuto's caution and crown block) only if Q2a's queens survive but
  stay short, or die to heads. Readings as §4.2.
- **D-074 §B: `kenma-03-pocket-queen` gets a 60-game ladder trial now.** It contains Q1 plus the global reserve (d). Its ladder
  table (Schooltime queen W–L vs the rest) separates the two: if Schooltime is won and the non-Schooltime rate is not below
  16979's window, (d) is harmless on the ladder despite the pool. I will read that table; Q1 stays queued as the
  reserve-free variant regardless, since it is the one that can sit on the incumbent.
- Shenzhen is stopped (D-074 §C), so the analyst work in §1 is mine; the tool is the inline scan recorded at the top.
- **Build spec for Q2a (for Asahi).** The incumbent has several split generators (`tyr_split_option`, opening production,
  the escape split, conversion), so gate at the action, not in each generator. In `main.cpp`, after `dec = pol.decide(w)`:
  if `w.me <= 1` and `dec.act == SPLIT` and `w.len - dec.split < 12` and Q1's pocket proof does not hold, set
  `w.limit = w.units` (every generator checks `units >= limit`; Kenma's reserve uses the same lever), call `pol.decide(w)`
  again, restore `w.limit`. Log `LOG q2a` when it fires. Cost: one extra decide on the queen's split turns only.
  Parity check: identical to the parent on every turn where the queen did not choose such a split.

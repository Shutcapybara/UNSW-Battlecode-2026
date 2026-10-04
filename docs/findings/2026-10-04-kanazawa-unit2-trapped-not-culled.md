# Kanazawa unit 2: our wall deaths are trapped dragons, not culls. H-C5 has no code to act on (4 Oct 2026, ~04:10Z)

Lane: kanazawa (Claude Opus 5.5, analyst: cross-lane synthesis). Data: post-m2 (`started_at ≥ 2026-10-02T03:49`), team-7
games in `public_replays/corpus`. Spread sample of 60 out of 286 eligible; 57 decoded, 3,620 wall deaths. Tool:
`tools/kanazawa/q_trap.py` (output in `build/kanazawa/trap/deaths.csv`). Map set: live post-m2 maps, per `map_name`
(table below). Parent of the code reading: `bots/carthage-05-free-sprint` (submission 14585).

## 1. Question
Chongqing C3-01 reads our north-into-kelp wall deaths as the lineage's deliberate cull: "we kill our own queen the first
time it looks like a small dragon". From that it proposes H-C5 (0.85): exempt ids 0/1 from the cull. Shenzhen endorsed
H-C5 as tester arm 2. The test here: if these deaths are culls, the dying dragon should usually have had a free cell.
If they are traps, it should have had none.

## 2. Result (replays)
For each wall death I took the state at the start of round r (`rounds[r]`, head first). Free neighbours are cells that
are not kelp (`nbr`) and not occupied by any body. The lenient count also treats any dragon's tail tip as free, except
our own neck.

| subset | n | north share | no free neighbour (strict) | no free neighbour (lenient) |
|---|---|---|---|---|
| all wall deaths | 3,620 | 0.93 | **0.87** | 0.74 |
| north moves | 3,352 | 1.00 | 0.91 | 0.77 |
| non-north moves | 268 | 0 | 0.41 | 0.37 |
| strictly trapped | 3,154 | **0.97** | 1.00 | 0.85 |
| had a free cell | 466 | 0.66 | 0 | 0 |
| queen (id 0/1) | 17 | 1.00 | **1.00** | 0.53 |
| queen, split ≤ 5 rounds before | 13 | 1.00 | 1.00 | 0.46 |

By map (n / north / trapped): Portals 899/0.92/0.87, Slithery 557/0.97/0.93, Around UNSW 525/0.95/0.87, Trauma
355/0.92/0.83, Maze 290/0.91/0.85, Islands 270/0.98/0.91, Schooltime 240/0.94/0.85, weakhold 123/1.00/1.00, Tower
Defense 112/0.89/0.85. Devil 82/0.37/0.57 is the only exception. Queen deaths came at lengths 2–3, at r29–r141.

## 3. Mechanism (code: carthage-05 `policy.hpp`)
- **There is no early cull.** The only deliberate fatal move is the feeder branch (`role_feeder`, about line 1349). It
  needs a crown. Crown election starts at r250, and feeding starts at `feed_from = 500 − 40 − 0.6·(W+H)` (≈ 412 on a 40×40
  map). Every queen death in the sample came at r29–r141.
- **The direction is north because of a tie-break.** The candidate list starts with `{0},{1},{2},{3}`. A DEAD path scores
  `−1000 − steps`, and the strict `>` comparison against `best_score = −1e30` keeps the first of the tied paths. When every
  path is fatal, path `{0}` = NORTH wins. Any OK path scores far above −1000 (the trap penalty peaks at about 60 × value
  scale). So a north wall death means the dragon's own model found no legal move. It was not choosing to die.
- **How the queen ends up boxed.** `tyr_opening_split` (opening production and rescue splits) checks no exit for the
  parent at all. `tyr_split_option` checks the child's exits, but only takes a soft penalty (≤ 30) for the parent's room,
  against `split_value = 8`. The queen keeps the head end (replay 858818: length 5 → split r28 → length-3 parent with
  child 15 behind it, all of its free cells kelp → `move dir 0` r29). Rescue splits leave a parent of length 2, and a
  length-2 or length-3 dragon cannot use `tyr_escape_split` (needs length ≥ 4).

## 4. Readings
- **C3-01 (Chongqing):** the measurements stand: north 90 %+, the queen dies within 5 rounds of its split, weakhold is
  deterministic. The cause does not. These are trapped dragons in the tie-break, not culls. H-C5 as worded ("exempt ids
  0/1 from the cull") has no code to act on before r250. A tester implementing it literally gets a no-op, or a rule that
  can't fire because every move is fatal.
- **Replacement (H-KZ6, below):** one mechanism, a parent-exit guard on queen splits. carthage-02 (queen never splits,
  old maps, hb1-era parent) moved queen alive@490 from 1 % to 13 % pool, but cost econ −0.036 pool and −0.317 gen and was
  rejected. H-KZ6 blocks only the splits that box the parent, so its economy cost should be much smaller.
- **H-C6 (Chongqing, corpse placement)** still holds as a separate question: when trapped, which fatal move we pick
  decides who eats the corpse. Today it is always north.
- **466 deaths (13 %) had a free cell at the start of the round.** Some of those cells were taken earlier in the same
  round (by lower ids). Any remainder is an error in the bot's model (H-KZ7).

## 5. Hypotheses
| id | claim | weight | falsifier | size if true | cost | suits |
|---|---|---|---|---|---|---|
| H-KZ6 | Queen splits (ids 0/1, `tyr_split_option` + `tyr_opening_split`) are allowed only if the parent keeps ≥ 1 free exit after the split (excluding child cells) and flood ≥ min(len−2+3, 5); otherwise no split. This raises queen alive@RL-end on Trauma, Portals, Maze and weakhold. | 0.6 | alive@RL-end < 0.15 on those 4 maps, or the D-042 units guard fails (Δlog units@100 LB < −0.10) | queen 0 → 0.2–0.4 on the queen-race maps; weakhold r29/r44 deaths gone | one switch on carthage-05, `LIVE_MAPS_M2` + gen, seeds 1–3, both seats | Claude tester (Rome/Seoul) |
| H-KZ7 | Some of the 466 free-cell wall deaths are model errors (unknown portal pairings, stale body) rather than cells taken in-round. | 0.3 | an in-round re-simulation (id order) finds every one of those cells occupied before the dragon's turn | ≤ 13 % of wall deaths, about 8 per game | corpus pass with the id-ordered state | Kanazawa |
| H-KZ8 (blue-sky) | When trapped, choosing the fatal direction (toward an ally head or our pearl zone, away from enemy heads) raises corpse recovery. 3,154 trapped deaths ≈ 55 per game are pearls placed by tie-break today. | 0.3 | Δcorpse_recovered_share < +0.03 (pairs with H-C6) | +0.05–0.1 corpse share | one switch: break DEAD ties by ally-head distance | tester |

Freeze for H-KZ6 (stated before any run): the primary is queen alive at RL end on {Trauma, Portals, Maze, weakhold}, per
map_hash, paired against carthage-05. Expected sign: positive. Guards: D-042 win-led rule and units guard.

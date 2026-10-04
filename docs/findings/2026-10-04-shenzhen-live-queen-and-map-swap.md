---
id: shenzhen-live-queen-and-map-swap
author: Shenzhen (P2-A analyst, Opus 5.5, replay lead)
kind: measurement + hypotheses
title: Unit 1 — a second era boundary (the 2 Oct map swap), the Schooltime cage our live bot dies in, the field's queen adoption, and live top-10 − us
evidence: build/shenzhen/lean/ (lean decode, 5,650 post-change games = 11,300 side-rows; team 7 complete, 742 games); build/s1/corpus/games.parquet (rebuilt 3 Oct 22:26Z ladder, 114,008 games)
queries: tools/shenzhen/{lean,q_queen,q_opening,q_us,q_qsplit}.py (repo root; SZ_M2=1 = post-swap only)
---

# 0. Data, and what it is not

- **Lean table, not the S-1 store.** The full S-1 decode costs ~9 CPU-s/game on the Mac's Cowork VM (4 cores): the 20,475
  undecoded post-change in-scope games would take ~13 h. `tools/shenzhen/lean.py` decodes with `frame.decode` only
  (~1.7 CPU-s/game) and keeps per-side opening, endgame and queen columns at r10/25/50/100/150/250/400/490 and the end.
  No territory, no bed capture. Engine verdicts (FRAME_VERSION 7) agree with the index's official winners on 11,300/11,300
  side-rows.
- **Coverage:** 5,650 of 22,867 post-change in-scope games (top-50 of the 3 Oct ladder, or us), decoded newest-first and
  balanced round-robin over (rank tier, map). Team 7 is complete (742 games). **5,164 of the 5,650 are after the map swap
  below.** The pre-swap field is barely in the table (486 games, mostly ours); pre-swap field numbers come from Antioch's
  and Nara's units.
- **Cohorts** are by the 3 Oct ladder (snapshots 22:26Z and 23:18Z hold the same ten teams; top ten = Vibing++ (ex-Cutlery, 306), forgot to mention, SSS, Sponge,
  Cache me outside, horse, WeHaveQuizzes, 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿, free trip to sydney pls, tungtung67). The ladder moves between
  snapshots, so teams 9–12 trade places run to run.
- **Us live:** submission 14265 (`hb1-14-prior-r540`) from 1 Oct 17:00Z to 2 Oct ~04Z (501 games); 14585
  (`LV-carthage-05-free-sprint`) from 2 Oct ~04Z (241 games). Team 7 games stop at 2 Oct 14Z apart from 12 on 3 Oct.
  Unranked games are mostly against the top ten (carthage-05: 65 % of unranked opponents are top-ten teams).

# 1. A second boundary: the server swapped six maps at 2 Oct 03:49Z

Every map in the store has two `map_hash` values per period (the two seat orientations). On **2 Oct between 03:45:52Z
and 03:49:02Z** six maps changed hash and the old hashes never reappear: Autarky, Default, Prisoners Dilemma, Schooltime,
Slithery Fight, Trophy. Devil, Portals, Queen Of Spades and Trauma are unchanged. What changed, from the map text inside
the replays (old vs new, same seat):

| map | change |
|---|---|
| Autarky | the dragon list is re-ordered: ids 0/1 (the queens) were the 14-long column in the side pocket; now they are 3-long open dragons |
| Slithery Fight | re-ordered: the queens were the 7-long dragons; now they are the 25-long coils |
| Prisoners Dilemma | re-ordered (queens were the 11-long; now 3-long) and two dragons removed |
| Trophy | the queen spawns moved (y 2 → 9) and four edges changed |
| Schooltime | 20 edge changes: **each queen now spawns inside a closed 2×2 cage** (below) |
| Default | four edge changes |

Consequences:

1. **The "pocket maps" are gone.** Antioch's H-Q3 (no queen survives Slithery, Autarky, PD) and every pocket-map
   exemption in TARGETS (Antioch, Nara, L49's falsifier "excluding pocket maps") describe maps the server stopped playing
   on 2 Oct 03:49Z. Since the swap the top ten lose the queen by r10 in 0 % (Autarky, n = 120), 1 % (Slithery, 124) and 0–4 % (PD and PD 10, 58/69) of games.
2. **The repo's `maps/*.map` are the old versions** for all six maps (`maps/autarky.map` ids 0/1 = the 14-long dragons;
   `maps/schooltime.map` has no cage). Every local panel since then has tested the queen on maps the server no longer
   uses. The live versions, extracted from replays, are in `tools/shenzhen/maps_live/<map>__<hash>.map` (both seats; the
   format is the replay's map text, loadable by `mapview.load_map`; a tester should confirm `unswbc` runs them before
   use).
3. **The package already carries the live maps.** PyPI shows `unswbc` 1.2.4–1.2.9 after 1.2.3 (1.2.6 uploaded 2 Oct
   04:05:56Z, 17 minutes after the swap; 1.2.9 on 3 Oct 06:59Z). Unpacked: `unswbc_engine.wasm` and every module except
   `__init__.py` are byte-identical from 1.2.3 to 1.2.9 — **the rules did not change again**. 1.2.6 replaces exactly the
   six maps above (plus Colosseum and default_small) in `unswbc/templates/maps/`; 1.2.9 adds the seven non-ladder maps the
   server also plays (australia, islands, maze, stripes, tower_defense, unsw, weakhold). Its `autarky.map` and
   `slithery_fight.map` dragon lists match the replays. So the fix for every panel is: `pip install unswbc==1.2.9` and
   take maps from its `templates/maps/` (my `maps_live/` extraction is a cross-check, not a replacement).
4. **Era tag.** I propose `map_era = 'm2'` ⇔ started ≥ 2026-10-02T03:49:00Z for every map (the four unchanged maps carry
   it too, so the tag is a single cut). All my numbers below are m2 unless marked.

# 2. The Schooltime cage: our live bot kills its own queen in round 0, every game

On live Schooltime each queen spawns 4-long, coiled in a 2×2 box whose four outward edges are walls: from the head
(3,2) the moves are N → (3,1) (its own neck), W → (2,2) (its tail), E and S blocked. `carthage-05` (live as 14585) moves
**N into its own neck at round 0 and dies (cause self) in 21 of 21 Schooltime games** since the swap, both seats, all four
hashes. It wins 2 of 21 (9.5 %). The top ten never lose the queen there (0/123 by r10): 30/30 sampled top-ten queens
split at r0 (keeping a 2-long head in the cage) and then circle the box, eating the occasional pearl that spawns
inside; the queen is alive at the end of 93.5 % of their round-limit Schooltime games, at length 3. A caged queen is a
queen that cannot be killed, so Schooltime is now a queen-tiebreak map that our bot forfeits at r0.

The local panel cannot see this: `maps/schooltime.map` is the old, open spawn.

# 3. The field adopted the queen in 48 hours

| m2, side-games | n | RL share | queen alive at end of RL games | median queen length if alive | RL win | queen-decided W–L | RL losses with a total lead | longest at end (RL, median) | total at end (RL, median) |
|---|---|---|---|---|---|---|---|---|---|
| top ten | 2,083 | 0.59 | **0.42** | 16.5 | 0.69 | 383–186 | 0.41 | 47 | 137 |
| ranks 11–30 | 2,465 | 0.61 | 0.34 | 3 | 0.55 | 340–314 | 0.40 | 36 | 110 |
| ranks 31–50 | 2,688 | 0.66 | 0.25 | 4 | 0.46 | 279–364 | 0.32 | 28 | 84 |
| below 50 (vs top 50) | 2,836 | 0.63 | 0.25 | 4 | 0.39 | 279–371 | 0.30 | 24 | 75 |
| **us (carthage-05)** | 256 | 0.62 | **0.00** (0/159) | — | **0.27** | **0–46** | 0.19 | 33 | 71 |

- On 1 Oct the top ten kept the queen in 0.7 % of RL games (Antioch). Since the swap they keep it in 42 %, and **40 % of
  all RL games are decided by the queen** (1,281 of 3,220). The 12-hour clock: top-ten queen survival (RL, all maps)
  0.19 (1 Oct pm, n = 27) → 0.36 → 0.43 → 0.50 (3 Oct pm), excluding Slithery/Autarky/PD; this series is not cut at the swap.
- Two shapes, both in the top ten. **Fed crown:** Vibing++ (queen length 39 when alive, alive in 49 % of RL games),
  Sponge (27.5, 54 %), horse (30, 42 %): the queen moves 85–95 % of rounds, eats 8–11 pearls, splits 1–3 times. **Small
  runner:** free trip to sydney pls (length 5, alive 67 %, moves every round, eats 1, never splits), tungtung67 (6, 45 %).
  forgot to mention (#2) and WeHaveQuizzes do **not** keep a queen (14–15 %) and still win 63–70 % of RL games — they win
  on longest with a dead queen against opponents whose queen also died, and lose the queen tiebreak 8–36 and 7–23.
- Length is not what matters at the tiebreak; being alive is. Static counterfactual on our 109 RL losses since the swap
  (opponent unchanged): a queen alive at length 1 flips 65 (60 %), length 5 flips 85 (78 %), length 15 flips 91 (83 %).
  This is an upper bound — keeping the queen alive costs material (carthage-02/03) — but the first unit of queen length
  is worth more than every later one combined.
- Queen killers (m2, excluding the three ex-pocket maps): top ten h2h 61 %, invalid 15 %, self 10 %, wall 8 %, body 6 % (n = 1,086); ours h2h 48 %, wall 34 %, self 14 % (n = 203). Our wall share is four times theirs.

# 4. Opening, live: top-10 − us is twice what the panel said

Field-normalised z per map (field = every side in the lean table on that map, m2), averaged; 90 % bootstrap over sides;
"us" = carthage-05 live, 256 side-games; top ten 2,083.

| component | r25 | r50 | r100 | r150 | r50 medians top-10 / us |
|---|---|---|---|---|---|
| transits (cum.) | **0.62** [0.54, 0.69] | **0.65** [0.58, 0.72] | 0.64 | 0.61 | 4 / 2 |
| total length | 0.54 | 0.47 [0.37, 0.57] | 0.62 | 0.69 | 26 / 25 |
| units | 0.34 | 0.40 [0.30, 0.49] | 0.50 | 0.48 | 11 / 10 |
| splits (cum.) | 0.43 | 0.38 [0.28, 0.48] | 0.47 | 0.57 | 14 / 11.5 |
| bed pearls (cum.) | 0.25 | 0.33 [0.23, 0.43] | 0.45 | 0.55 | 23 / 20 |
| longest | 0.46 | 0.34 [0.28, 0.40] | 0.41 | 0.55 | 4 / 3 |

Against the same opponents (both sides playing a top-ten team; top ten n = 566, us 129) the r50 gaps are the same within
0.1: transits 0.57, total 0.50, units 0.41, splits 0.35, bed 0.32. Antioch's panel-based r50 gap for total length (0.18)
understated the live gap (0.47): the panel opponents are weaker than the live field. The order of the components is
unchanged — **portal use first**, then material, production and bed pearls — and the gap widens to r150 rather than
closing.

# 5. Hypotheses (proposed ledger rows; weights for the director)

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| **H-SZ1 cage** | On live Schooltime the queen must not move into its own neck at r0. The fix: when a dragon has no move except into its own body, split (the head keeps 2) or step into the tail cell; never into the neck. Expected: Schooltime round-0 self-deaths 21/21 → 0, Schooltime win share up from 0.10. | queen alive at r10 on live Schooltime < 0.95 over 40 games, or any non-Schooltime fixture changes (the rule only fires when no legal non-self move exists) | 40 Schooltime games on `maps_live/schooltime__*.map`, both seats; plus a parity check on the old panel (expected 0 divergent turns) | any tester; **first in the queue — a live bug, one rule, no economy cost expected** |
| **H-SZ2 maps** | The local panel's six old maps measure a game the server stopped playing; queen arms judged on them are biased toward "pocket deaths". | carthage-08's pool queen alive@490 changes by < 5 pp between old and live maps | carthage-08 and carthage-00, pool seeds 1–3 on the live map set | tester with the desktop |
| **H-SZ3 first unit** | Under the m2 field, a queen alive at any length flips ≥ 60 % of our RL losses; the cheapest survival form (the small runner: length 3–6, moves every round, never splits, never feeds) is worth more than the fed crown per unit of economy. | runner arm vs fed-crown arm on the live map set: RL win LB of runner ≤ fed crown's, or econ LB < −0.03 | pool + gen seeds 1–3, live maps | Claude tester |
| **H-SZ4 transits** | The largest live opening gap is portal use (0.65 SD at r50, n = 256 live). Unchanged from the panel and from Antioch's H-S1. Restated with live numbers; not new. | — | — | — |

# 6. Readings

- **L49 (queen preservation) and every queen arm since 1 Oct** were judged with pocket-map exemptions on the old maps.
  Under m2 the exemption has no basis. The falsifier should read "alive@490 ≥ 0.5 on the live map set, all maps".
- **N6 (fed crown) vs H-SZ3 (runner):** both shapes are in the top ten. Nara's "crown from birth" is Vibing++'s shape;
  free trip to sydney pls shows the cheap shape works too. The tester should run both, not assume the crown.
- **Nara unit 4 (team 7 live: 0/326 RL queen survival, loss maps = RL maps):** agree, and the map swap explains part of
  the per-map pattern: on Schooltime the loss is a round-0 bug, not strategy.

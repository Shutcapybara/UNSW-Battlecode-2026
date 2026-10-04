# Chongqing unit 3 — per-map queen hazard on the new maps, and why our queen dies: we cull it

Claude analyst (Opus 5.5), S-1 store / replay lead. 4 Oct 2026, 03:25 UTC. Store 45,230 games (post-m2 ≈ 1,300; VM decode
slowed to 2.5 s/game this unit, so the bulk is still pending). Era `post-m2` (new maps) unless stated; cohorts = ladder
2026-10-04T00:53Z; `qs/qd` views as in unit 1 § A. Field = all non-team-7 sides in the store (≈ 60 % of them are our
opponents in post-m2, so field rows lean toward the teams that play us).

## 1. The queen on each new map (post-m2, field sides vs carthage-05 live, vs top ten ranked)

RL = share of games reaching the round limit; alive = queen alive at the end of RL games; death causes are shares of
queen deaths (h2h-e = enemy head-on; own = self / ally body / ally head-on; cull = invalid / suicide).

| map (new) | field n | RL | field alive | top-10 alive (n) | **us alive** | field death cause | **our death cause** | our median death | RL games queen-decided (field) |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|
| Schooltime | 113 | 1.00 | **0.965** | 1.000 (22) | **0.000** | — (cage) | own 1.00 at r0 (cage) | r0 | 0.25 |
| Trauma | 106 | 0.93 | **0.798** | 0.957 (26) | **0.000** | own 0.42, h2h-e 0.33, wall 0.17 | **wall 0.61**, own 0.22 | r116 | **0.89** |
| Portals | 120 | 1.00 | 0.375 | 0.586 (29) | 0.000 | own 0.61, wall 0.20, cull 0.19, h2h-e **0.00** | **wall 0.88** | r68 | 0.61 |
| Maze | 119 | 0.93 | 0.315 | 0.406 (34) | 0.000 | h2h-e 0.41, own 0.35 | **wall 0.67** | r144 | 0.56 |
| Slithery Fight | 104 | 1.00 | 0.317 | 0.276 (29) | 0.000 | h2h-e 0.59, own 0.25 | own 0.56, h2h-e 0.31 | r259 | 0.52 |
| weakhold | 104 | 0.59 | 0.279 | 0.350 (32) | 0.000 | h2h-e 0.41, wall 0.33 | **wall 1.00 at r29 / r44** | r36 | 0.48 |
| Around UNSW | 132 | 1.00 | 0.182 | 0.242 (33) | 0.000 | h2h-e 0.73 | h2h-e 0.67, wall 0.33 | r116 | 0.29 |
| Australia | 127 | 0.97 | 0.187 | 0.286 (29) | 0.000 | h2h-e 0.83 | h2h-e 1.00 | r107 | 0.35 |
| Islands | 118 | 0.84 | 0.141 | 0.370 (28) | 0.000 | h2h-e 0.68 | h2h-e 0.89 | r107 | 0.24 |
| Autarky | 118 | 0.31 | 0.297 | 0.300 (31) | 0.000 | h2h-e 0.73 | h2h-e 0.57, wall 0.29 | r72 | 0.57 |
| Default | 120 | 0.47 | 0.089 | 0.067 (35) | 0.000 | h2h-e 0.90 | h2h-e 0.82 | r84 | 0.18 |
| Tower Defense | 103 | 0.38 | 0.308 | — | 0.077 | h2h-e 0.75 | h2h-e 0.58, wall 0.33 | r130 | 0.56 |
| Prisoners Dilemma (4+10) | 105 | 0.28 | 0.50 | 0.833 (23) | 0.05 | h2h-e 0.70 | h2h-e 0.80 | r33 | 0.66 |
| Queen Of Spades | 98 | 0.16 | 0.188 | 0.500 (33) | 0.000 | h2h-e 0.86 | h2h-e 0.44 | r84 | 0.38 |
| Devil / Trophy / Stripes | 109 / 107 / 99 | ≤ 0.02 | n/a | n/a | n/a | h2h-e 0.7–0.9 | h2h-e 0.6–0.8 | r50–93 | elimination maps |

Three map classes for the queen on the live pool: (a) **cage**: Schooltime — the field keeps 96 %, we keep 0 (H-H3 / H-SZ1);
(b) **queen-race maps** (RL ≥ 0.6, half or more of RL games queen-decided): Trauma, Portals, Maze, Slithery, weakhold, Around
UNSW, Australia, Islands — the field keeps 14–80 %, we keep 0; (c) **elimination maps**: Devil, Trophy, Stripes (RL ≤ 0.02),
and mostly QoS/Autarky/PD/Default/Tower Defense (RL 0.16–0.47). The queen column matters on (a) and (b): 9 of 17 maps.

## 2. Why our queen dies: the cull does not exempt it

- On the corridor and portal maps our queen's deaths are **wall** (Trauma 0.61, Portals 0.88, Maze 0.67, weakhold 1.00) where
  the top ten's are 0.00–0.17. On weakhold it is deterministic: **r29 on seat-hash 665a…, r44 on 9c3a…, 15/16 games.**
- The queen is at length 5 at r28 on weakhold, **splits** (production), and the length-3 remnant walks **north into kelp** at
  r29 (replay 858818: id 0, action `move steps 1 dir 0`; 888879 likewise at r44). **74 % of our 87 post-m2 queen wall deaths
  fall within 5 rounds after a queen split** (splits table, parent ∈ {0, 1}).
- This is the lineage's cull. Our wall deaths overall: median length 2, age 14, 42 % newborn — the same profile as the top
  ten's deliberate culls, which they execute as `invalid` / `self` / `suicide` (185k such deaths in the post-m2 store;
  median length 2, age 14). We execute ours as a **north move into kelp**: in every game checked, ≥ 90 % of our wall deaths
  are single-step north moves (e.g. Portals 852907: 187 N / 15 E / 1 S / 4 W, while our ordinary moves are 2990 / 2468 /
  2740 / 2485 by direction; Trauma 999612: 109 N / 11 E / 1 S; Maze 1003123: 122 N / 13 E), and it is **chronic**: live
  13010 (pre-change) 92–106 N per game, 14265 155–164 N, 14585 the same. Total death rate is normal (us 23.3/1k dragon-turns,
  top ten 25.0), so this is the channel, not extra churn. The top ten's queen is 0.0015 of their wall deaths and 0.0007
  of their self deaths; ours is 0.0048 and 0.0033.
- Reading: **we kill our own queen the first time it looks like a small dragon — right after its own production split.**
  This is the mirror of Cutlery's 13:00Z flip ("stop culling the queen", Nara unit 3), which took team 306 to rank 1.

## 3. Hypotheses

- **H-C5 (0.85) — exempt the queen (original ids 0/1) from the cull, no other change.** Expected on the new maps: queen alive
  at RL end 0 → ≥ 0.3 on Trauma / Portals / Maze / weakhold (where wall is 61–100 % of its deaths), queen-decided losses on
  those maps −50 % or more, economy flat (one dragon fewer culled per game). Falsifier: queen alive@RL-end on those four maps
  < 0.15 after the exemption, or econ lb < −0.03. Size: four maps × seeds 1–3 both seats (~100 pairs) on **live maps** (unswbc
  ≥ 1.2.6). Does not touch Schooltime (cage; H-H3/H-SZ1 is separate) nor the contact maps (Australia/Islands/Around UNSW:
  h2h-enemy 0.67–1.00 — that is H-Q5 distance work). Suits the Claude tester / Carthage lineage (its cull routine).
- **H-C6 (0.6) — the north-into-kelp cull is itself a leak**: a cull should die where an ally eats the corpse (the top ten
  recover 0.777 of corpses, we 0.682; our ally-corpse share of pearls equals theirs at 0.35). Falsifier: switching the cull
  to an in-place `invalid`/`self` death beside an ally does not raise corpse_recovered_share ≥ +0.05. Size: pool + gen s1–3.
- **H-C7 (watch)** — after H-C5 the next queen killer is head-on on contact maps (Australia 1.00, Islands 0.89, Default
  0.82): the field's own survival there is only 0.14–0.19, so parity, not supremacy, is the target.

## 4. Readings

- Rome 03 (REJECT) and 04 (pool −1.35 pp, gen 0; fails): agree with Himeji H15-01/H17-01 and Nara — both arms fired with the
  queen already dead (95/96 Portals triggers). § 2 says why: the queen is culled within 5 rounds of its first split, so no
  r250 trigger ever sees it alive. H-C5 is the prerequisite for every L39/L49 arm.
- Shenzhen's probe (14-line cage rule, 11/12 wins vs carthage-05 on live Schooltime): consistent with § 1 — the field keeps
  96.5 % of Schooltime queens, so the cage rule only buys parity; the tiebreak then goes to length (max 3 in the cage, H-SZ20).

## 5. Store

+65 games this unit only (VM at 2.5 s/game; host busy). `games.map_era` live; `qq.py` carries `map_era`, `map_hash`.
Per-new-map field counts 100–130 sides (50–75 games) — new-map norms need ≥ 300 games/map: not before the bulk lands.

Ledger: L49 → 0.7 stands; propose **H-C5 as a row at 0.85** (mechanism measured, intervention one line), H-C6 at 0.6;
L29 (churn) unchanged in weight but re-described: the base's culls are north-into-kelp walks, not accidents.

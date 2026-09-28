---
id: 2026-09-29-yeji-s01-swarm-dissolve
author: claude/yeji/01SVqD5S
kind: observation
title: "S1 swarm-dissolve 2x2: production is mildly positive, adjacent dissolution is negative; a public-map prior fixes the compact-map opening but hurts open maps"
task: next-gen-prompt-S1-swarm-dissolve
supersedes: ""
evidence:
  - docs/findings/yeji-s1-runs/ (results.jsonl per arm; one row per game with ystats contract statistics)
  - bots/yeji-s01-swarm-dissolve/README.md
  - bots/yeji-s01p-production/README.md
  - bots/yeji-s02-mapfield/README.md
  - tools/yeji/ (yrun.py harness, ystats.py, meter.py, crowns.py, build_prior.py)
---

# S1 swarm-dissolve: what the 2×2 says

**Setup.** unswbc **1.2.2** (scratch venv), `--seed 1`, the ten live maps × both sides × 8 lineage-diverse references
(yuna-v02-core, gavroche-v32-supported-divecap, sinbad-v07-divecap, hunter-v20-portal-scouts, kraken-v04-eval,
ouroboros-m01-vibing-mimic, witten-x03-confirmed-fastbed, fry-v14-stateful-size-aware-3) = **160 paired fixtures
per arm**, paired by (map, side, seed, opponent). ouroboros-v10-beacon is the control and so is not in the pool
(fry-v14 replaces it). One seed only: every Δ below is selection evidence, not proof, and none is a rating.

| Arm | Score | Δ vs control | better / worse | sign p |
|---|---|---|---|---|
| control `ouroboros-v10-beacon` | 0.494 | — | — | — |
| P: production only (`yeji-s01p-production`) | 0.531 | +0.037 | 19 / 13 | 0.38 |
| D: dissolve only | 0.419 | **−0.075** | 10 / 22 | **0.05** |
| PD: `yeji-s01-swarm-dissolve` | 0.444 | −0.050 | 15 / 23 | 0.26 |
| `yeji-s02-mapfield` (P + map prior + bed field) | 0.519 | +0.025 | 22 / 18 | 0.64 |
| `yeji-s02-mapfield@dissolve_on=1` | 0.469 | −0.025 | 19 / 23 | 0.64 |

## Falsifiers

- **H-prod fired.** Median units at r100 is 14 over the panel (control 14; open maps 17 vs 14); wall/self deaths 3.5 per
  1k turns. Raising the split value does not raise production on compact maps: the pearl intake is the bottleneck.
  On Trophy vs sinbad (an s01-family build, seed 2), sinbad ate 23 pearls in r20–40 against our 3: its dragons reach the fast beds in the cup by r17;
  ours forage slow-bed spawns near home (traced).
- **H-dissolve fired.** Longest at r400 11 (base 11); at r499 17 (base 24). The funnel works mechanically —
  83 % of corpse pearls are eaten by an ally within 2 rounds and 74 % by a crown (676 dissolves, 995 pearls, 160 games)
  — but it moves ≈ 4.6 pearls per game, while the S1 crown rules (r250 election with stagger, longest-known rule,
  min length 6, crown risk ×3) cost length: `crowns.py` shows ~64 crown assumptions per game on Schooltime and crowns
  dying to forced corridor moves and enemy head-ons. The host's cruder feeding (L ≤ 20 within 2 tiles from r400,
  4,027 corpse pearls, 22 % reaching an ally) yields a longer longest (26).
- **H-cert untested.** Delivery measured: the backward ray reaches the child in **37 %** of births; adding any straight
  ray that stops on the child raises it to **57 %** (s02). Newborn deaths within 10 rounds stay ≈ 40 per 100 births in
  every arm, including the control (whose handoff uses the same ray), so no effect is visible.

## What else was learned

1. **Forced corridor deaths dominate our own-move deaths.** `deaths.py` on Schooltime: 100 body + 59 self deaths were
   forced (1-wide kelp corridors blocked by allies), 37 "chosen" body deaths were almost all blind portal landings.
2. **A public-map prior is the largest lever found.** Recognising the map from the first view and loading its terrain and
   fast beds (s02) gives compact maps units r100 **26 vs 13** and longest r499 **32 vs 19**, Devil +0.44 vs the P arm.
   A compact 32-fixture screen: s02 vs s01 **+0.28 (10 better / 1 worse, p = 0.012)**; without the prior −0.22.
3. **The same bed field hurts open maps** (Default −0.50 vs P): every dragon climbs the same gradient, the enemy is
   there too, and the open-map economy stalls (units r250 16 vs 32).
4. **Loading must be C-level.** The s02 loader (Python loop over 2·W·H edges) exceeded 100M points on Schooltime's first
   turn in the sandbox. s03 stores edge kinds, portal ids, bed rates and the field as constants and loads them with
   slice copies: turn 0 is 57–62M on Schooltime (34–36M without the prior; the import itself costs ≈ 6M).
5. **Remote agents in this environment share the container**; they did not add compute.

## What s02/s03 change, and what s04 should try

- s02 dropped the S1 crown/dissolve layer (evidence above) and added the map prior, the bed field, portal-exit memory and
  direct certificate rays. s03 keeps the field on compact maps only (≤ 625 tiles) and fixes the loader's CPU.
- Next: a crowding- and enemy-aware field (subtract ally/enemy presence per zone), bed pre-positioning by predicted
  countdown for beds seen once (symmetric maps share countdowns between mirror tiles), and a budget-aware degradation
  mode (none exists; the host has none).

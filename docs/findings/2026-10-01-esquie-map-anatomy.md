---
id: esquie-map-anatomy
author: glm/esquie
kind: map anatomy (M-1 Parts 1-3)
title: M-1 — map anatomy on the nodevil base: the brick list, signature clusters, and the local-fix/global-test loop
task: M-1
evidence: game_stats/runs/esquie-01-nodevil-*.json/.md/.tsv, game_stats/runs/esquie-01-z1-ledger.json,
game_stats/runs/esquie-01-z1-portal.json, build/esquie/signatures.json,
build/zoo/{z1,gen}-esquie-01-nodevil-aa4f6042/, golden transcripts build/cx/golden/{devil,portals,schooltime,trauma,dilemma}-*-1/
---

# M-1 map anatomy — Esquie lane, Part 1 (the brick list) and Part 2 (anatomies)

Branch `r/esquie`, worktree `../wt-esquie`. Base **`esquie-01-nodevil`** = `lune-r1-07-latecap8x-only`
(Ares V06 + `search_cap_late` 48→384, sparse 64→512) with the three `W==32 && H==16` terms off behind
`Params::shape_terms=false` (D-033; renoir-23 ablation form). Golden parity at launch: the
`shape_terms=true` variant is **0 divergent / 27,957 turns** against fresh lune-r1-07 recordings
(devil-A 5,731 / portals-A 8,648 / schooltime-B 13,578); the shipped nodevil bot is 0-divergent on
schooltime and diverges only on the three 32×16 pool maps (devil 335, portals 638 turns) — note
**Portals is 32×16 too**, so the V06 shape terms were live there, not only on Devil/Dilemma.

Panels: z1 = 10 live maps × 8 zoo opponents × both seats, seeds 1+2 (320 side-games);
gen = 29 unseen maps (maps/new 20 + maps/var *_tr 9), seed 1 (464 side-games).
Pooled base: z1 W–L–D 227–93 (70.9 %), economy mean 1.1276 (r50 1.005 / r100 1.104 / r150 1.155 /
r250 1.247), dragons@100 1.115, length@100 1.043, wall 6.99 / own 4.32 / ally-body 2.82 / h2h-ally
1.08 per 1k. Gen: 294–170 (63.4 %). Atlas is dead code in this lineage; every number is atlas-off
by construction. Fixed references: `docs/analysis/benchmarks/`.

## Part 1 — the brick list

### Pool, three-number form (seeds 1+2, 32 side-games per map)

`econ_pct` = mean field percentile of the four economy checkpoints (share of field sides beaten).
Full table: `game_stats/runs/esquie-01-nodevil-bricklist-z1,gen.tsv`; raw TSV reproduced in
`build/esquie/bricklist-full.txt`.

| map | win | econ_pct | economy\|map | p@50\|map | trapped | newborn | portal | crowd23 | worst tier-2 pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **Trauma** | 0.750 | **0.375** | 0.682 | **0.111** | 14.0 | 4.3 | 0.0 | 3.5 | wall 0.353 |
| **Prisoners Dilemma** | 0.812 | **0.413** | 0.784 | 0.778 | 45.6 | 25.6 | 4.6 | 24.9 | h2h 0.143 |
| **Portals** | 0.844 | **0.506** | 1.003 | 0.714 | **81.9** | 37.0 | **74.6** | 35.2 | h2h **0.056** |
| Default | 0.750 | 0.518 | 1.042 | 0.750 | 3.9 | 5.5 | 11.8 | 8.5 | ally-body 0.116 |
| Trophy | 0.719 | 0.594 | 1.166 | 1.143 | 11.3 | 8.3 | 13.2 | 9.5 | wall 0.177 |
| Queen Of Spades | 0.688 | 0.609 | 1.186 | 1.143 | 35.4 | 19.9 | 29.4 | 18.9 | self 0.263 |
| Slithery Fight | 0.594 | 0.640 | 1.174 | 1.081 | **101.3** | **73.6** | 4.5 | 32.6 | h2h 0.226 |
| Autarky | 0.750 | 0.657 | 1.178 | 1.152 | 38.2 | 21.7 | 3.0 | 2.4 | wall 0.239 |
| Devil | **0.500** | 0.680 | 1.763 | 1.275 | 68.8 | 37.7 | 0.0 | 34.6 | self 0.190 |
| Schooltime | 0.688 | **0.790** | 3.011 | 2.375 | 34.5 | 21.9 | 3.9 | 11.8 | ally-body 0.146 |

Ledger rows: length lost / 1k dragon-turns, rounds 0–99, top-10 reference trapped 18.5 / newborn
24.0 / portal 3.5 / crowd23 2.7. The r3/V06 per-map peaks all reproduce on this base (Slithery
trapped 101.3 vs V06's 101.5; Portals 81.9; portal Portals 74.6 — higher than V06's 57.7;
newborn Slithery 73.6).

**The prior expectation inverted.** Schooltime — expected to be a large/dense brick — is our best
economy map (pct 0.790; the local fixture even under-represents the live bed field by ~118 cells,
C1-E note 13, so the true live number is if anything understated). The economy bricks are
**Trauma, Prisoners Dilemma, Portals** — and they are three *different kinds* of brick (Part 2).
Devil's 0.500 win share is the known identity cost of D-033 (the terms were worth 1.00→0.31 on
Devil alone, Renoir), classified with the transposed pair below, not fixable here.

### Gen (29 unseen maps, seed 1; raw, no field reference)

Win share and death composition per map (16 side-games each; deaths per 1k dragon-turns,
`enemy` = enemy body + h2h enemy):

| worst gen maps | win | deaths/1k | enemy share | pattern |
|---|---:|---:|---:|---|
| Trophy tr | 0.25 | 23.4 | 88 % | identity loss (nodevil cost) |
| mc26_pinwheel | 0.31 | 20.8 | 100 % | fight loss; also supply8 = 0 beds in 8 steps of spawn |
| mc26_seam_market | 0.38 | 32.6 | **100 %** | fight loss at the seam; units@100 collapses to 3, pearls frozen at 67 from r100 |
| Devil tr | 0.44 | 37.8 | 49 % | identity loss + fight |
| commons shared/spread | 0.50 | 40.8 / 29.6 | 89 % / 63 % | fight loss over the central field |
| Portals tr | 0.62 | 54.3 | 0 % | pure self-inflicted leak (the pool Portals mechanism, transposed) |
| … best | 0.88–0.94 | ≤ 15 | — | promenade_ring, default_tr, nursery_bays, spring_wells |

### Signature clusters (`tools/esquie/signature.py`, 21 features, average linkage, k=8)

Every `*_tr` map clusters with its original — the signature is orientation-free, as it must be.
The load-bearing clusters:

| cluster | members (pool in bold) | brick annotation |
|---|---|---|
| corridor/kelp | **Devil, Trauma**, devil_tr, trauma_tr, Slithery (at k=10) | Trauma starved-opening; Devil identity cost; Slithery trapped leak |
| portal-heavy | **Portals**, portals_tr | transit + same-pair collision leak |
| QoS | **Queen Of Spades**, QoS_tr | starved opening (supply50 0.20) + big detour (4.12) + territory game |
| default/trophy | **Default, Trophy**, default_tr, trophy_tr | 100 %-bed slow-renewal; trophy_tr identity loss |
| mega-cluster (open gen) | 23 maps incl. pinwheel, seam_market, commons, dilemma* | fight-loss bricks live here; structure does not separate them |
| singles | Schooltime, equatorial_belt | our best maps |

**The gen suite does not cover the pool's brick motifs.** The corridor/kelp cluster contains no
maps/new member (all 20 new maps: kelp ≤ 0.09, deg≤2 share ≤ 0.02); the portal cluster's only gen
neighbours are mild (portal_quartet/relay_depots at 4 pairs vs Portals' 20). So a fix keyed on
those motifs can only be transfer-tested on the `_tr` twins — that is a real limitation on the
transfer verdict, stated up front.

## Part 2 — anatomy of the three worst

### Trauma — starved opening (economy brick, pct 0.375, r50 = 0.111)

- **Curve:** field median eats 9 pearls by r50; we eat **1** (seat A: exactly 1 in every seed-1
  game, all eight opponents — opponent-independent behaviour). Recovery later: r250 = 1.15 of
  median. Deaths are *low* (trapped 14.0, newborn 4.3, wall pct 0.35): this is not a leak map.
- **Signature:** supply8 = **3.0 beds within 8 BFS steps of spawn** (pool low), supply50 = 0.75
  expected-ripe; ripe50 = 0.31; corridors (kelp 0.245, deg≤2 33 %) but detour ratio 1.0 — the
  nearest bed is manhattan-reachable; the walls matter after the first bed, not before it.
- **Replay (trauma-A-1 vs yuna-v05, a 264-pearl loss):** r0 SPLIT, then four dragons MOVE for 80
  rounds without a split (no length to split). r15: pearls locked in the next corridor behind
  kelp walls; r30: a full bed field in view showing countdowns 32–154 — **nothing ripe, nothing
  targeted** (`bed_wait=0`: a bed ripening in 16 rounds at distance 3 is worth 0), the dragon
  cruises on. The opening has no legal food target, so the target search returns exploration.
- **Claim (structure, not name):** *we lose the opening on maps where the expected number of
  beds ripening within walking range of the spawns is below ~1 (supply50 ≤ 1) or the bed field is
  slow and sparse (dilemma: supply50 1.67 × ripe50 0.136; default: ripe50 0.039); we hold where
  beds are fast (portals/slithery/schooltime) or dense enough that variance delivers early
  pearls (devil ripe50 0.295, trophy/autarky).* Cluster check: trauma_tr (supply8 3.0 / supply50
  0.75, r50 = 2 raw, win 0.69) behaves like Trauma; QoS (0.20) and pinwheel (**0.0/0.0** — no bed
  within 8 steps of any spawn) are the gen-side instances; crossroads_tr (0.0) is the mild form
  (win 0.69). Devil is the boundary case the claim must not swallow — see the gate below.

### Prisoners Dilemma — churn without growth (economy brick, pct 0.413)

- **Curve:** r50 0.78 → r100 **0.72** → r250 0.86: the deficit accumulates mid-game. units@100
  1.60 of median but total@100 1.00 — **the swarm is length-2 dust** (8 units, 18 total length).
  Births 22.5 by r100, **37.9 % of children die within 10 rounds**. Deaths low (wall 5.7, self
  7.2): the leak is production-into-starvation, not navigation error.
- **Replay (dilemma-A-1 vs fenrir, an 85-pearl loss):** lifespans are 5–30 rounds for almost
  every child (34: r51–56; 35: r55–64; 56: r193–202…). The view at r51: a bed field showing
  countdowns **426–438 on a 393-round game** — beds that will never ripen — with the few ground
  pearls walled off. Children are born into this and starve.
- **Claim:** same structural variable as Trauma (slow, sparse bed field), expressed after the
  opening as child churn. Any supply-gated fix must key on the *dragon's own* food knowledge, so
  Dilemma's parents (who see the same desert) get the same treatment as Trauma's openers.

### Portals — transit and collision leak (mixed brick: econ pct 0.506, win 0.844)

- **Ledger:** trapped 81.9 (4.4× top ten), portal 74.6 (V06 was 57.7 — worse on this base),
  newborn 37.0, crowd23 35.2 (13× top ten). Portal instrument: 471 transit steps/game, 41.7
  near-deaths per 100 steps (V06: 41.9 — unchanged), **same-pair doubles 85/game** (V06 pooled
  14.9). h2h-ally 13.1/1k = 16× the zoo median; its field percentile is **0.056** — the single
  worst tier-2 cell in the pool table. length@100 0.868 = the pool's worst retention.
- **Replay (portals-A-1 vs chaewon, a 71-pearl loss):** dragon 865 at r411 does `SPLIT 7` at
  length 9 beside enemy bodies; the len-2 child spawns into contact and dies in one round. The
  same-pair doubles say two dragons dive one portal pair and meet at the blind exit.
- **Claim:** *on maps with many portal pairs and kelp corridors (portals_per100 ≳ 0.5, deg≤2
  ≳ 0.25), the leak is post-transit collision, not volume* — r3's conclusion, now with the
  h2h-ally row and the same-pair count as the map-specific face. Cluster: portals_tr only.

### Gen fight-loss trio (the mega-cluster's bricks, classified separately)

Pinwheel (0.31), seam_market (0.38), commons_shared/spread (0.50) lose with deaths that are
**63–100 % enemy-caused** and near-zero self-inflicted rates — the opposite profile of the pool
leak maps. seam_market: units@100 collapses to 3 and pearls freeze at 67 from r100 on. These are
C2-0's "pricing rule" losses (contest concentration: bed mass where contact is short — the seam,
the commons centre) and are not structure-gateable the way supply is; they are recorded in the
map × mechanism table as the cluster where fight pricing, not navigation, pays.

## Part 3 — the loop

(version-by-version in the sections below as they run)

### esquie-02-starve-wait — supply-gated bed anticipation (target: Trauma/Dilemma cluster)

Mechanism: `bed_wait_eff = 64` only when the dragon (age ≥ 12) knows no food anywhere — no
visible/remembered pearl, no seen bed ripening within 8 rounds — else 0 (= parent). The renoir
bed-wait value term, gated on the starved observable so dense (Devil: ground pearls always
visible) and fast-bed (Portals: ripe50 1.0) maps never wait. Expected sign *before any run*:
Trauma/Dilemma r50 and r100 up, QoS up; Devil/Schooltime/Portals unchanged; pooled small +
(n=10 pool maps, three of them in the starved cluster).

Divergence profile (mechanism acts only where designed): switch-off 0 divergent / 19,403 turns
vs esquie-01 recordings (trauma/dilemma/portals-A); switch-on: trauma 35, dilemma 30,
portals **0**, schooltime 26/13,578.

Results: **REJECT (first form) — with the local gain real and the leak diagnosed.**

| read | number (paired vs esquie-01, z1 seeds 1+2 unless said) |
|---|---|
| pooled gate | econ −0.0241, win −2.19pp, dragons −0.023, length −0.039; no tier-2 rate up >10 % (ally-body −12 %) → **fail** |
| **local gain** | Trauma p@50\|map **0.111 → 0.222** (opening doubled), Dilemma p@250\|map 0.863 → **0.970**, Dilemma win 0.812 → **0.875** |
| guards held | Portals bit-identical (all cells equal), Devil ≈ unchanged (0.680 → 0.675, win 0.500 → 0.531) — the gate does what it was designed to do |
| leak | **Trophy** econ_pct 0.594 → **0.470**, win 0.719 → **0.562**; Default 0.518 → 0.506; Schooltime win 0.688 → 0.594 |
| transfer (gen s1) | pinwheel **+0.125 win, +17 p@250** (the supply-0 map — transfers ✓); portal_quartet +0.125; trauma_tr p@250 **−29**; equatorial_belt p@250 **−53**; 17/29 gen maps bit-identical medians (the gate never fires there) |

**Diagnosis (the gate observable was wrong, not the mechanism):** `food_soon` counted a bed as
food only while its countdown ran (`spawn_at ≥ rnd`). A known bed whose countdown had *passed*
plausibly holds a sitting pearl — the parent's own `cell_value` gives it full value through the
`bed_stale` = 60 window — but the gate could not see it. On slow-dense maps (Trophy: 100 %-bed,
ripe50 0.09) dragons were "starved" while known pearls sat elsewhere, and they loitered at
ripening beds instead of collecting them: exactly the Trophy/late-Trauma losses. Transcript
check: v02 diverges 14 turns on a trophy recording; the fixed gate (esquie-03) diverges **1**.

### esquie-03-starve-wait2 — the gate observable fixed (stale-ripe beds are food)

One change: `food_soon` widened to `spawn_at − rnd ≤ 8 && rnd − spawn_at ≤ bed_stale` (the same
staleness window `cell_value` uses). Divergence: trauma 21 turns (down from 35 — the false-starve
loitering gone), dilemma 30, portals 0, trophy 1.

Results: **local gains kept, leak closed, transfer positive — pooled economy still a hair
negative (reject-as-is; the D-032 interval straddles zero).**

| read | number (paired vs esquie-01, z1 seeds 1+2) |
|---|---|
| paired Δeconomy | **−0.0041**, bootstrap 90 % [−0.0248, +0.0170] (n=320) |
| pooled gate | economy mean −0.021 (median form), **win +0.62pp** (229–91), dragons −0.010, length −0.021; no tier-2 up >10 % |
| local gain | Trauma p@50\|map **0.222 held** (opening doubled), p@250 restored 1.022 → **1.130**, win 0.750 → **0.812**; Dilemma p@250 **0.970**, win **0.875** |
| leak closed | Trophy p@250 1.068 → **1.132** (base 1.265), win 0.562 → 0.656; equatorial_belt p@250 −53 → **0** |
| **transfer (gen s1)** | **trauma_tr +0.312 win, +31.5 p@250** (the cluster twin — the v1 loss fully inverted), trophy_tr +0.188 win, pinwheel +0.125 win held, spring_wells +14.5 p@250, Autarky tr +0.125 win; 20/29 gen maps bit-identical; losses: default_tr −0.125 win / −6 p@250 only |
| residual | pooled r50 −0.026: the *transient* starve — rounds 12–24 where even rich maps have seen no food yet and the wait buys nothing |

### esquie-03b-starve-wait3 — one parameter: min_age 12 → 24

Skips the opening transient. Divergence profile now surgical: trauma 21 turns (the true starved
state, which lasts to r80+ there, still caught), **schooltime 0** (was 26/13,578 in v1),
**trophy 0** (was 14 in v1). If the panels keep the local gains with the pooled r50 recovered,
this is the local-hold candidate.

Results: (panels queued after esquie-04)

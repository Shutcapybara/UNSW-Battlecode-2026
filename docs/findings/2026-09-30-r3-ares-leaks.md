---
id: r3-ares-leaks
author: glm/r3
kind: measurement+fixes
title: R-3 — the C1-F leak switches re-targeted at Ares V06, at real transit volume
task: R-3
evidence: game_stats/runs/r3-v06-{ledger,portal}.json, r3-yuna-v05-ledger.json (step 1, reused
R-4 V06 z1 seed-1 panel, 160 games); build/rp-r30{1,2}-z1.log, r3-*-z1-s1.json/.md, r3-*-ledger.json
(step 2, fresh panels); golden transcripts build/cx/golden/{portals-A,schooltime-B}-1/
---

# R-3 — the Tyr-lineage leaks on Ares, and the switches re-targeted at them

Branch `r/r3` (worktree ../wt-r3, r/r4 tooling merged). Base: **Ares V06** (no `claude/r1-status.md`
exists yet; V06's own finding holds and my R-4 rerun reproduced it). Atlas note: `atlas_try` is
**never called** in V06 — the atlas is dead scaffold code, so Ares is atlas-off by construction and
the out-of-sample rule is satisfied without a build variant; the R-4 z1 seed-1 panel of V06
(160 games, fingerprint-identical) is valid step-1 data.

## Step 1 — the leaks on Ares V06 (the lineage claim holds)

Instrument: `tools/analysis/r3_ledger.py` — the exact C1-C leak classes (newborn / trapped /
portal-geographic / crowd23 on the F1 per-death rows; currency length lost per 1k dragon-turns,
rounds 0–99, medians over side-games) plus the exact C1-D portal walk
(`tools/replay_stats/portal_deaths.py` core; 2.38 M move walks verified, 0 mismatches).

Pooled ledger (z1 panel, seed 1, both seats, 160 side-games; references from C1-C):

| row (len lost / 1k dt, r0–99) | top 10 | band 55–85 | yuna-v05 local¹ | **Ares V06** |
|---|---:|---:|---:|---:|
| trapped (enclosed at death) | 18.5 | 32.8 | 39.3 | **36.1** |
| newborn (≤10 rounds) | 24.0 | 18.4 | 24.9 | **19.3** |
| portal (≤2 cells of a portal) | 3.5 | 3.1 | 10.3 | **6.3** |
| crowd23 (len≤3 into own side) | 2.7 | 10.2 | 18.5 | **11.4** |
| wall (cause class) | 0 | 0.7 | 9.2² | **8.2²** |

¹ same ledger over the F1 z1 round-robin (yuna-v05-core side-games) — the Tyr-lineage reference
bot locally; ² wall is deaths/1k, not length-lost. Per-map peaks (V06): trapped Slithery 101.5 /
Portals 75.7 / Devil 66.2; portal Portals 57.7; newborn Slithery 70.6 — the same three-map
concentration C1-C measured for team 7.

Portal transit (the C1-D form, V06 replays):

| | team 7 live | **Ares V06** | team 306 |
|---|---:|---:|---:|
| steps / game | 49 | **62.5** | 47 |
| near-deaths / game | 11 | **14.5** | 6.0 |
| **deaths / 100 steps** | 28.2 | **29.4** | 12.5 |
| Portals map steps/game | 399 | **513** | 72 |
| Portals map / 100 steps | 36.0 | **41.9** | 27.1 |
| wall+self near (per game) | 17.8 | **15.9** | 0.06 |
| same-pair doubles / game | 15.7 | **14.9** | 4.3 |

**Verdict: Ares V06 carries the Tyr-lineage leak profile at real transit volume** — trapped above
the band and 2× the top ten, the portal-safety signature (29.4/100 vs 306's 12.5) with the
wall+self bucket and same-pair doubles, crowd23 at 4× the top ten. The C++ port did not fix them
(V06 is marginally better than yuna-v05 on every row). Proceeding to step 2 was correct.

## Step 2 — the switches on the right host

Carrier: one code base (four params variants `bots/r3-01…04`), the R-3 block at the end of
`params.hpp`, each flag default-off. **Golden parity: the all-off carrier is identical to V06 on
15,178 transcript turns (0 divergent)** over fresh V06 recordings on Portals (397 dragons, 8,487
turns — the transit-heavy map) and Schooltime (129 dragons, 6,691 turns). The flag-on r3-01
diverges on 29/8,487 Portals turns (0.34%) — the mechanism acts only at portal entries.

The switches (C1-F semantics, re-read for Ares):

- **r3-01 `r3_pair_memory` (F-1)** — World records the last *survived* transit per portal pair
  (being alive this round verifies every earlier transit; death ends the process so no false
  positives); exit-side danger derives from enemy DragonMem (last round an enemy head was
  remembered within 2 of the landing). A portal-entering step whose exit is not verified within
  `r3_pair_fresh` (8) rounds pays `r3_pair_cost` (2.0), `r3_pair_danger_cost` (4.0) with recent
  remembered danger. Verified pairs cost nothing — this is not the chassis's volume throttle.
- **r3-02 `r3_exit_known` (F-2)** — a portal-entering step whose landing is not known-clear
  (terrain seen ≤12 rounds, no body seen recently, no remembered exit danger, transit survived
  recently, **or the last sonar fan was enemy-clean** — Ares's four radio rays make the probe
  nearly free) is skipped while a livable ungated option exists; the gate yields (second scoring
  pass) only when every alternative is certain death. C1-F's throttle result is not assumed
  either way.
- **r3-03 `r3_escape_early`** — V06 escape-splits only at all-steps-dead (`best_score < -900`);
  this fires the same split (child keeps len−2, head at tail, ≥1 legal child step — **never gated
  by room size**, per C1-F's negative result) while the room flood is below 0.75×need.
  The measurement of "what Ares's trapped escape already does": its flood-per-path already
  prices enclosure (`trap_weight` 30) and the escape split exists; the switch only moves its
  trigger earlier.
- **r3-04 `r3_kelp_cost` (F-4 analog)** — inside the existing cramped-landing trap penalty, a
  landing with <3 known-open edges pays 2.0 more (the kelp-corridor mouth). On the chassis this
  rule never flipped a decision; the Ares test may measure the same no-op.

## Step 2 — per-switch results (z1 seed 1, both seats, 160 games vs V06)

The battery per version: golden parity (shared carrier), z1 panel scored with the fixed references
(the R-4 scorecard), the r3 ledger and the portal instrument on the same replays, and — for the
versions that survive — the gen panel and the sandbox CPU probe. All panels are fingerprint-keyed;
every number below is from runs executed here.

### The targeted rows (ledger + portal instrument, medians)

| switch | targeted row | V06 | switch | moved? | volume (steps/game) | per-100-steps |
|---|---|---:|---:|---|---:|---:|
| r3-01 pair memory | portal len/1k | 6.3 | 4.9 | yes, −22% | 62.5 → **48.5** (−22%) | 29.4 → **31.8** (worse) |
| r3-02 exit-known | portal len/1k | 6.3 | 2.8 | yes, −56% | 62.5 → **20.0** (−68%) | 29.4 → **32.6** (worse) |
| r3-03 escape-early (v2) | trapped len/1k | 36.1 | 33.8 | barely (−6%; Slithery 101.5→112.1) | 62.0 (unchanged) | 29.1 (unchanged) |
| r3-04 kelp cost | wall len/1k | 19.8 | **14.5** | yes, −27% (trapped also 36.1→**25.4**, −30%) | 62.5 (n/a) | n/a |

Wall+self near-portal per 100 steps: V06 12.9, r3-01 14.3, r3-02 13.0 — **the per-transit death
rate never improved; every portal-row gain is exposure reduction (fewer transits), exactly the
C1-F chassis throttle signature.** C1-D's diagnosis ("volume is not the leak — safety is")
transfers to Ares: the wall+self deaths are contact and post-transit navigation deaths, which a
pre-entry cost or gate cannot see.

### The gate rows (BENCHMARKS three-number form)

| switch | economy mean | win share | tier-2 guardrail | verdict |
|---|---|---|---|---|
| r3-01 pair memory | 1.1107 → 1.0600 (**−0.051**) | −5.62pp | own-body +14% | **fail** |
| r3-02 exit-known | 1.1107 → 0.9903 (**−0.120**) | −8.12pp | none up (all down: h2h-ally −54%, wall −17%) | **fail** |
| r3-03 escape-early v2 | 1.1107 → 1.1454 (**+0.035**) | **+5.00pp** (130–30 vs 122–38) | own-body +10.9%, h2h-ally +11.5% | **fail on the 10% guardrail** → seed-2 rerun (below) |
| r3-04 kelp cost | 1.1107 → 1.0388 (**−0.072**) | −7.81pp | none up | **fail** |

Reading against the task's own acceptance rule ("a fix that moves its row and costs pearls is a
hold with the trade stated"):

- **r3-01 (hold-shape, trade: 1.4 portal len/1k saved for 0.051 economy):** the row moved only by
  transiting 22% less; per-transit survival worsened. On the chassis F-1 was neutral; on Ares at
  real volume it is a pure throttle. Not the mechanism.
- **r3-02 (hold-shape, trade: 3.5 portal len/1k — and every cause rate down — for 0.120 economy):**
  the strongest safety lever measured (portal 6.3→2.8, trapped on Portals 75.7→32.0, newborn
  19.3→17.4, all tier-2 rates down) and the clearest sakura trap: −68% transit volume, per-100-steps
  *worse*. The exit is not made safe; it is made unfamiliar.
- **r3-03 (near-miss):** the only economy- and win-positive version, but its targeted row did not
  move — the −10 escape-split score acts as a *split-when-cramped production lever* (births +0.018|map,
  pearls r50 +0.053|map), not as trap escape; the hygiene rise (+11% own-body, +12% h2h-ally) is the
  churn price of those extra small dragons. v1 was wired inert (the escape still required
  best_score < −500, so 160 games were bit-identical to V06 — reported as the wiring find, not a
  no-op); v2 competes at −10 while enclosed and diverges on 38/8,487 Portals transcript turns, 0 on
  Schooltime.
- **r3-04 (hold-shape, trade: 5.3 wall + 10.7 trapped + 2.9 newborn len/1k saved for 0.072 economy):**
  the biggest row movements of the four — wall −27%, trapped −30%, newborn −15% — at a heavy economy
  price. Unlike the portal switches this is not volume throttling; it pays pearls for survival
  directly (the classic BENCHMARKS guardrail case: hygiene that the economy does not hold).

Gen panels (29 maps, seed 1, 464 games): r3-01 W–L–D 277–187 vs V06 294–170 (−3.7pp, raw economy
flat: pearls +1.5, dragons +1.0, length +0.5); r3-02 281–183 (−2.8pp, r250 pearls −14). The portal
switches cost less off-pool (fewer portal maps) but still lose games; r3-03/r3-04 gen below with the
stack.

CPU probe (r3-03, the survivor): sandbox 4 fixtures vs yuna-v05 — see the stack section.

### Seed-2 confirmation (r3-03, the near-miss)

Seed 2 was run per BENCHMARKS ("rerun at seed 2 before deciding"): both sides, 160 games per bot.
Seed-2-only: W–L–D **129–31 vs 121–39 (+5.0pp again)**, economy 1.1990 vs 1.1860 (+0.013), own-body
**4.673 vs 4.210 (+11.0% again)**, h2h-ally +5.8% (inside the guardrail at this seed). Pooled over
seeds 1+2 (320 side-games): win share +5.00pp (259–61 vs 243–77), economy +0.0264, length +0.049,
dragons +0.007, own-body +11.0%, wall +1.4%, ally-body −4.6%.

**Verdict: hold, with the trade stated.** The gain (+5pp expected score, +0.03 economy at seed 1 /
+0.013 at seed 2, length up) replicates; the cost is a persistent ~11% own-body death rise — the
churn of the extra small dragons the cramped split creates (its targeted trapped row did not move:
this is a production lever, not an escape fix). Not registered; if the director wants it, the
attribution to check first is newborn churn from `ACT:tsplit` children (the C1-C newborn row at
28.6/100 births vs V06's 25.0 at seed 1). CPU: sandbox probe p50 4.7M / p99 7.3M / max 8.7M /
0 errors over the 4 fixtures — V06's own envelope (4.7/7.4/8.7M), the switch is compute-free.

### Gen panels (r3-03; 29 unseen maps, seed 1, 464 games)

r3-03: W–L–D **288–176 vs V06's 294–170** (−1.3pp — neutral off-pool), raw pearls r250 +4.5,
dragons +1.0, length +1.0. The +5pp z1 gain is live-pool-concentrated; off-pool the switch neither
helps nor harms. (r3-01: −3.7pp with flat raw economy; r3-02: −2.8pp with r250 pearls −14 —
reported above.) No atlas is involved in any of this (dead code in V06), so nothing here is
map-identity dependence.



## Step 3 — the stack

## Step 3 — the stack (r3-05-stack-escape-kelp)

Stacked the two complementary step-2 directions — r3-04 (the biggest row movements: wall −27%,
trapped −30%) and r3-03 (the only economy/win-positive switch) — as `bots/r3-05-stack-escape-kelp`
(both flags on, one addition over r3-03's v2 carrier; golden parity carried by the shared all-off
build).

z1 seed 1 vs V06 seed 1 (160 games): **FAIL — economy 1.1107 → 1.0042 (−0.107), win share
−1.25pp**, dragons −0.075, births −0.161. The hygiene wins survive (wall −33%, own-body −3%,
ally-body −6%; ledger: trapped 36.1 → 25.6, wall 19.8 → 16.2, newborn 19.3 → 17.3) but the two
costs **compound** (r3-04 alone cost −0.072; with r3-03's splits feeding more small dragons into
the kelp-avoiding policy the loss deepens to −0.107 rather than recovering). Per the protocol
("stop when a stack step fails the gate"), the stack stops here; r3-05's gen panel was not run.


## What is closed, what is open

## What is closed, what is open

**Closed (measured, negative):**

1. **Pre-entry portal pricing does not fix Ares's portal leak at any setting that moves the row.**
   F-1's cost (r3-01) and F-2's gate (r3-02) both cut the portal ledger row only by transiting
   22–68% less; the per-100-steps death rate stayed flat or worsened (29.4 → 31.8 / 32.6) and
   wall+self per 100 steps never fell (12.9 → 14.3 / 13.0). C1-D's "volume is not the leak — safety
   is" is now measured on the production lineage itself: the deaths are contact and post-transit
   navigation deaths at the exits, which no crossing-side rule can see. The C1-F throttle result
   **does** transfer to Ares.
2. **The kelp/room surcharge (F-4 analog, r3-04) is the strongest hygiene lever on Ares** — wall
   −27%, trapped −30%, newborn −15% pooled, every tier-2 rate down — and it still fails because the
   economy pays −0.072 (and −0.107 stacked): BENCHMARKS' "hygiene counts only while the economy
   holds" is the binding constraint, not the mechanism.
3. **Ares V06's escape split already complies with C1-F's negative result** (no room-size gate;
   ≥1 legal child step). Firing it earlier (r3-03) does not move the trapped row — the trapped
   leak is not "the split fires too late" — and the earlier wiring (only-at-all-dead) was measured
   bit-identical to V06 over 160 games, so V06's current escape behaviour is exactly what those
   games show.

**Open (where the leaks actually live, for the next task):**

1. **Post-transit navigation** — the per-100-steps rate is the invariant (29–33 across every arm
   and V06 itself). A mechanism that steers the first 2–3 steps *after* a transit toward open
   ground / away from kelp and own body is the untested shape; the portal instrument
   (`tools/analysis/r3_ledger.py --portal`) scores it directly.
2. **Newborn siting** — C1-C's fix #2 ("child's first bed chosen at birth for arrival-earliness
   and crowd-freedom") was not in R-3's switch list and remains untested on Ares; r3-03's +11%
   own-body churn from extra cramped splits points at the same row (crowd23 11.4 vs top-10's 2.7).
3. **r3-03 as a production lever** — win +5pp / economy +0.03 (seed 1) and +0.013 (seed 2),
   neutral off-pool, compute-free, persistent own-body +11%. A hold, not registered: if the
   director wants it, the newborn-churn attribution should be paid down first (a siting rule on
   the `ACT:tsplit` children), which is also open item 2.

**Nothing is registered; no CANDIDATE is marked ready for `register.json`.** All five r3 bots stay
in `bots/` with their measured CANDIDATE.tomls. BENCHMARKS compliance note: every number above is
atlas-off by construction (V06 never calls `atlas_try`), live pool and gen panel reported
separately throughout.


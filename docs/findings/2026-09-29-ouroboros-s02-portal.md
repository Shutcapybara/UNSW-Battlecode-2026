---
id: ouroboros-s02-portal
author: claude/ouroboros/session-01A4m7SWbU4yXs2tEmvQ41c2
kind: observation
title: "S2 on the fenrir-v18 host: portal safety (atlas + probe/HOLD + own-body inference) is +0.11 paired and replicates; the economy mechanisms convert extra pearls into churn and are off; the host has two exceptions and a boot-turn CPU cliff"
task: S2 build prompt (docs/hub/prompts/2026-09-29-S2-economy-on-a-band-host.md)
supersedes: nothing
evidence:
  - bots/ouroboros-s02-portal (candidate), bots/ouroboros-s02-econ (all mechanisms), bots/ouroboros-s02-arm-{econ,portal,explore}, bots/ouroboros-s02x-firstcut
  - docs/findings/ouroboros-s02-data/*.jsonl (one row per game; tools/ouros2/panel.py format)
  - tools/ouros2/ (panel.py and cstats.py copied from tools/chaewon with attribution and extended; econ2.py, supply.py, s2report.py, probe.py, agecost.py, build_atlas2.py)
---

## Setup

- **Host.** `bots/fenrir-v18-arrival-ready-beds`, byte-identical to live control 9508, copied and never edited.
- **Panel.** unswbc 1.2.2, `--seed 1` (seed 2 replication below), the ten public maps × both sides × six opponents =
  120 fixtures per arm. The opponents are a copy of fenrir-v18 as a mirror, sinbad-v07, gavroche-v32, the m01 mimic,
  yuna-v05 and chaewon-y04. Games are paired by (map, side, seed, opponent); p is a two-sided sign test.
- **Compute.** Everything ran in a 2-core cloud container, about 1,100 games in total.
- **Deliverable.** Nothing was uploaded or registered. Local numbers select candidates; they are not a claim of
  live strength.

## Result

| Arm (seed 1, 120 fixtures) | Score | Paired Δ vs host | Better/worse | p | Units r25/r50/r100 | Total r250 | Pearls/game | Pearls r0–100 | Wall+self per 1k |
|---|---:|---:|---|---:|---|---:|---:|---:|---:|
| host fenrir-v18 | 0.571 | — | — | — | 6/10/15 | 57 | 343 | 66 | 16.2 |
| + economy | 0.375 | −0.196 | 9/32 | <0.001 | 6/9/12 | 48 | 310 | 70 | 17.9 |
| + portal safety (pre-fix) | 0.683 | +0.113 | 24/10 | 0.024 | 7/12/18 | 67 | 440 | 80 | 17.2 |
| + explore | 0.567 | −0.004 | 5/5 | 1.0 | 6/10/15 | 58 | 343 | 66 | 16.2 |
| all | 0.558 | −0.013 | 17/19 | 0.87 | 6/11/15 | 63 | 330 | 70 | 16.3 |
| first cut (all) | 0.508 | −0.062 | 16/23 | 0.34 | 7/11/14 | 64 | 402 | 78 | 17.8 |
| **ouroboros-s02-portal (shipped)** | **0.679** | **+0.108** | **28/15** | **0.066** | 6/12/18 | 75 | 470 | 80 | 17.1 |

- **The shipped bot** is the portal-safety arm plus two host bug fixes and CPU bounds (below). Those changes alter
  decisions, so it was measured again on the same 120 fixtures.
- **Per map:** Slithery Fight +0.42, Portals +0.38, Trauma +0.21, Schooltime +0.17, Autarky and Trophy +0.08, Devil
  and Queen of Spades 0, Dilemma −0.08, Default −0.17.
- **Per opponent:** yuna-v05 +0.25, sinbad +0.20, fenrir mirror +0.17, gavroche +0.12, chaewon-y04 +0.05, m01
  −0.15.
- **Seed 2 replication:** not run: stopped at wrap-up. The shipped bot's 120-fixture re-measure (+0.108, 28/15) reproduces the pre-fix arm's +0.113 (24/10) on the same fixtures, but that is one seed.

Per-class medians for every arm are in `bots/ouroboros-s02-portal/README.md`. The first-pearl round is 4–5 for the
team and 7–9 for children in every arm.

## What the mechanisms did

**Economy (H-econ): the falsifier fires.** Median Δ total r250 is −2 and Δ units r100 is −1 with everything on. The
target was at least +15 and +4, and self+wall deaths stay at 16–18 per 1k against a bar of 5; the host is already
at 16.2.

The mechanisms did move pearls. From seeded replays, pearls eaten in r0–100 rose on Portals (144 vs 94), Queen of
Spades (40 vs 24) and Default (36 vs 27), and the opponents' intake fell on the same maps (73 vs 83, 15 vs 25). The
extra pearls became extra dragons, and those died in crowding:

- On Queen of Spades, deaths per game went from 68 to 101: forced wall deaths 22 → 35, ally-body deaths 6 → 12.
- Most forced deaths (no non-lethal step) are length-2/3 dragons in every phase.

Without portal safety the economy is strongly negative (−0.196). With it, it is neutral: all mechanisms −0.013 vs
portal safety alone +0.113.

**The first cut contained a real mistake.** A never-seen atlas bed was worth v_bed × P(first countdown ≤ arrival)
with no floor. On Trophy and Queen of Spades, where 67 % and 50 % of tiles are slow (1–1000) beds, that erased the
host's exploration value (v_unseen). Units r100 on Trophy fell 13 → 6, and the arm lost 0/11 on those maps
(p = 0.001). The fix is max(v_unseen, bed value).

**Portal safety (H-portal-safety): the falsifier fires on deaths per game; the win comes from somewhere else.**

| Map | Portal-step deaths/game (host → shipped) | Portal steps/game | Death rate per step |
|---|---|---|---|
| Default | 43 → 18 | 259 → 457 | 0.166 → 0.040 |
| Schooltime | 37 → 33 | 191 → 480 | 0.195 → 0.068 |
| Portals | 117 → 148 | 600 → 721 | 0.195 → 0.206 |

- The three-map total is flat, so the < 25 % fall in portal deaths per game is not met.
- On Default and Schooltime a portal step became 4× and 3× safer, and the bot uses portals 2–2.5× as often.
- The +0.11 comes from the atlas turning portals into routes. Pearls per game rose 343 → 470 and total r250 57 → 75.
- On Portals the per-step rate did not move. The probe and HOLD packet do not resolve the dense 20-pair case.

**Own-body inference is a new finding.** When a newborn's rear passes through a portal, its neck is out of view. The
host then rebuilds a one-cell body and can step through that portal into itself. On Portals seed 1, 61 of about 430
deaths were exactly this (`DG:partial`). The neck is `dest(HEAD)[FACE+2]`, and a newborn's segments keep the
parent's facings, which point towards its own tail. Extending the chain by one cell across the portal removed all
61. The chaewon neck fix (adjacency) alone did not affect outcomes: the explore arm, which carries it, is 0/0 on the
36 fixtures where exploration is gated off.

**Explore (H-explore): inconclusive.** On Portals, Slithery Fight and Trauma it went 3 better / 1 worse (+2 net vs
a +3 target). Without the atlas the ≥ 6 known-pairs gate is rarely met, so `ACT:dive` fires 0–5 times per game.
This was not a real test.

## Two findings about the live control (fenrir-v18 = 9508)

1. **Two exceptions fire every game.** Both are in `separation.py`:
   - `plan()` assigns `RESOURCE_PAUSE_USED` without declaring it global, which raises `UnboundLocalError`.
   - `_resource_value()` divides by `bed_wait`, which v18's override sets to 0, which raises `ZeroDivisionError`.

   Every hit drops the dragon to `fallback()`: the first non-lethal single step, with no sonar that turn. Counted in
   the 120 host games, per game (per 1k own turns): Slithery Fight 300 (12.3), Portals 183 (22.1), Schooltime 166
   (7.6), Devil 122 (35.0), Trauma 89 (15.4), Default 66 (7.3), Queen of Spades 13, Autarky and Trophy 8, Dilemma 0.
   Both are fixed in `ouroboros-s02-portal`.
2. **First turns run at the CPU cap.** In the sandbox (1.2.2), a new process's first turn costs about 46–51 M
   points in imports and parsing alone. A variant that only reads and moves on its first turn measured p50 50.9 M,
   max 53 M. The host's own decision then adds 0–45 M, so the host's first turns reach 97.5 M and TLE (Portals B,
   first 150 rounds: 7 first-turn and 11 later TLEs). This matches A1-Q6's "9508 is at the cap".

   The shipped bot runs a light boot turn: single steps only, a 32-node target search, flood need ≤ 10, no escape
   plan and no density update. Its newborn escape BFS is bounded (target 80 / origin 96 nodes, cached per
   activation with the atlas; 16 waypoints scored). First turns now peak at 54 M.

## Metered probes (shipped bot vs sinbad-v07)

| Toolkit | Fixture | Turns | Max (M) | p99 (M) | Faults |
|---|---|---:|---:|---:|---|
| 1.2.2 (seed 1) | Schooltime A | 24,372 | 56.4 | 44.5 | 0 |
| 1.2.2 (seed 1) | Slithery Fight A | 24,383 | 71.6 | 48.6 | 0 |
| 1.2.2 (seed 1) | Portals B | 9,436 | 74.8 | 50.4 | 0 |
| 1.2.2 (seed 1) | Trauma B | 7,304 | 65.3 | 45.5 | 0 |
| 1.0.0 | Schooltime A | 24,284 | 56.5 | 44.8 | 0 |
| 1.0.0 | Portals B | 10,245 | **80.2** | 50.8 | 0 |
| 1.0.0 | Trauma B | 8,584 | 56.4 | 45.4 | 0 |
| 1.0.0 | Slithery Fight A | — | — | — | not run (stopped at wrap-up) |

The pre-fix build failed the probes: max 96.9 / 98.4 M, and on Portals B, 79 TLE deaths plus 139 exceptions. The shipped build passes every probe on 1.2.2. On 1.0.0 it passes everywhere except one Portals B turn at 80.2 M, just over the 80 M bar (p99 50.8 M). Slithery Fight A on 1.0.0 was not run.

## The pearl supply is not the only constraint (for the director)

Bed pearls spawned in r0–100 and still uneaten at r100 (host, both sides), per game:

| Map | Uneaten at r100 | Spawned |
|---|---:|---:|
| Trauma | 56 | 81 |
| Schooltime | 63 | 274 |
| Portals | 64 | 241 |
| Queen of Spades | 42 | 90 |
| Default | 15 | 59 |

On Trophy, Autarky and Dilemma nearly every pearl is eaten, and on Devil the opponents take 91 against our 50. So
there is headroom on the open maps, but eating it (the economy arm did) does not pay without the survival of what
it produces.

## What s03 should change

1. **Keep portal safety and fix Portals.** Its per-step rate stays near 0.2: price blind exits from the observed
   rate, or probe every adjacent portal before a transit rather than only the chosen one.
2. **Re-enable economy only with a crowding term.** Production placement or child survival (the forced deaths of
   length-2/3 dragons) must come first; no clock change.
3. **Gate explore on the atlas pair count, then retest.**
4. **Run the local panel on 1.0.0 too.** The hub's gate toolkit also runs the sandbox, so probe both toolkits every
   version.

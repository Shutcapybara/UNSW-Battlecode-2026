# ouroboros-s02-portal

Claude, Ouroboros lineage, S2 build (`docs/hub/prompts/2026-09-29-S2-economy-on-a-band-host.md`). Host
`fenrir-v18-arrival-ready-beds` (byte-identical to live control 9508), copied, never edited. This is the
**portal-safety arm** of the S2 ablation, shipped because it is the only arm that beat the host. The economy and
exploration mechanisms the prompt asked for are in the code and **off** (`params.py`), because they lost.

## Headline

Seeded paired panel, unswbc 1.2.2, `--seed 1`, the ten public maps × both sides × six opponents (fenrir-v18 mirror,
sinbad-v07, gavroche-v32, m01 mimic, yuna-v05, chaewon-y04) = 120 fixtures, paired by (map, side, seed, opponent):

- **This bot (shipped): +0.108 vs fenrir-v18** (0.679 vs 0.571), 28 better / 15 worse, sign p = 0.066. Median
  units r100 18 vs 15, total r250 75 vs 57, pearls 470 vs 343 per game.
- The same arm before the host bug fixes and CPU bounds (`ouroboros-s02-arm-portal`): +0.113, 24/10, p = 0.024.
- **Per map:** Slithery Fight +0.42, Portals +0.38, Trauma +0.21, Schooltime +0.17, Autarky +0.08, Trophy +0.08,
  Devil 0, Queen of Spades 0, Dilemma −0.08, Default −0.17.
- **Per opponent:** yuna-v05 +0.25, sinbad +0.20, fenrir mirror +0.17, gavroche +0.12, chaewon-y04 +0.05, m01 −0.15.

Local numbers select; they are not a claim of live strength.

**Host fixes in this version.** `separation.py` of the host raises `UnboundLocalError` (`RESOURCE_PAUSE_USED` not
declared global) and `ZeroDivisionError` (`bed_wait` = 0). Every hit falls back to the first safe single step with
no sonar, 8–300 times per game. Both are fixed here.

**CPU bounds.** A light boot turn (single steps, 32-node search, flood ≤ 10, no escape plan, no density update) and a
bounded, cached newborn escape BFS. The host's first turns pay ~46–51 M of imports and reach the cap.

## What changed vs the host (all switches in `params.py`)

| Switch | Default | What it does |
|---|---|---|
| neck fix (always) | on | A newborn's segments keep the parent's facings; the neck is linked by adjacency (chaewon fix). |
| `atlas_on` | 1 | Loads the matching public map's terrain on the first 7×7 view (unique match only; atlas modules built by `tools/ouros2/build_atlas2.py` from `maps/*.map`, after chaewon's atlas). Pearls and countdowns are still learnt by sight. |
| `probe_on` | 1 | When the chosen move leaves the head next to a portal whose landing it cannot see, it casts one ray through that portal alone, carrying a HOLD packet (type 8). Next turn's echo says whether a dragon stands on the far line; an ally hit by the packet treats the landing as held for `hold_ttl` = 2 rounds. After chaewon-y04/y05. |
| `infer_body` | 1 | A partial own chain is extended behind the head (`dest(HEAD)[FACE+2]`, through a portal) and, for a newborn, across the portal its rear passes through (its segments' parent facings point towards its tail). In one Portals game, 61 of about 430 deaths were newborns stepping through a portal into their own unseen neck. `infer_body` removed all 61. |
| economy: `bed_atlas`, `atlas_far`, `pre_wait`, `sprint_pearl`, `v_contest`, `enemy_disc` | off / host values | Present for s03. On, they cost −0.196 (see ablation). |
| `explore_on` | 0 | Present; neutral (−0.004). |

No production, conversion or crown clock is changed. The crown, beacon and feeding layer is the host's.

## Ablation (same 120 fixtures, seed 1, unswbc 1.2.2)

| Arm | Paired Δ vs base | Better/worse | p | Units r25/r50/r100 | Total r250 | Portal-step deaths/game | Pearls/game | Pearls r0–100 | Wall+self per 1k |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|
| base fenrir-v18 (0.571) | — | — | — | 6 / 10 / 15 | 57 | 8 | 343 | 66 | 16.2 |
| + economy | −0.196 | 9/32 | <0.001 | 6 / 9 / 12 | 48 | 16 | 310 | 70 | 17.9 |
| **+ portal safety (this bot)** | **+0.113** | **24/10** | **0.024** | 7 / 12 / 18 | 67 | 8 | 440 | 80 | 17.2 |
| + explore | −0.004 | 5/5 | 1.0 | 6 / 10 / 15 | 58 | 8 | 343 | 66 | 16.2 |
| all (`ouroboros-s02-econ`) | −0.013 | 17/19 | 0.87 | 6 / 11 / 15 | 63 | 8 | 330 | 70 | 16.3 |

Medians over all 120 games. The first-pearl round is 4 in every arm (team) and 7–8 (children). Per-class tables are
in the findings file.

## Six-line report (S1 §8)

- **Strategy.** The host's value function is unchanged (λ weights, crown from r250, feeding from ~r420). The gain is
  in information: the atlas turns portals from unknowns into routes. Pearls per game +97 and units r100 +3 with the
  same clocks. No dissolve arm, so no funnel.
- **Execution.** Options on: the host's options plus the portal probe (`ACT:probe`: median 1,868 per game on
  Portals, 1,260 on Default, 1,563 on Schooltime, 799 on Autarky, 0 on Devil, which has no portals). Every chosen action is still a primitive that passed
  the host's exact simulation.
- **Implementation.** See the metered-probe table below.
- **State.** Atlas terrain → routing, flood fill, portal pairing. `PRES` (probe results, TTL 1) → blind-exit risk.
  `HOLD` (ally-held landings, TTL 2) → blind-exit risk. Inferred rear cells → exact simulation.
- **Messaging.** One new packet, HOLD (type 8: cell and round), sent only on probe rays. It replaces that turn's
  other rays so the echo is attributable. Rays are free in points (A1-Q6/Q7).
- **Momentum.** Unchanged from the host (target hysteresis 1.25). The neck fix and `infer_body` fix a
  newborn's body knowledge. Newborn deaths within 10 rounds: 41.4 vs 41.3 per 100 births.

## Metered probes (vs sinbad-v07; `tools/ouros2/probe.py`)

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

## Hypotheses (S2 §2)

- **H-portal-safety — fired on the stated metric, positive on outcome.** Portal-step deaths per game: Default 43.1 →
  19.4 (−55 %), Schooltime 37.3 → 35.5 (−5 %), Portals 117 → 152 (+30 %, with 720 steps per game vs 600: the
  per-step rate barely moved, 0.195 → 0.21). The 3-map total is up 5 %, so the < 25 % falsifier fires. The win comes
  from using portals more with the same per-step risk, not from making them safer.
- **H-econ — fired.** See `ouroboros-s02-econ`.
- **H-explore — inconclusive.** Portals, Slithery Fight and Trauma: 3 better / 1 worse, so +2 net pairs. That misses
  the +3 target, but the "≤ 0" falsifier does not fire. The arm barely ran: without the atlas, the ≥ 6 known pairs
  gate is rarely met, and `ACT:dive` fires 0–5 times per game. It is a weak test. s03 should gate it on the atlas.

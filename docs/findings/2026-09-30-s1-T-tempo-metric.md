---
id: S1-T-tempo-metric
author: s1
kind: proposal + validation
title: Tempo lag — an early-game objective in rounds, with a decision rule
code: tools/s1/tempo.py (build | validate | score | compare)   reference: build/s1/out/tempo/reference.pkl (top-10 curves, 30 Sep)
---

## Definition

For one side-game on one map, take the side's **net income** at round t:

  N(t) = I(t) − [D(t) − D_ref(t)]

- **I(t), income:** bed pearls plus enemy-corpse pearls eaten by t. This is new mass entering the side. Eating our own
  corpses is not income, so churn cannot inflate it.
- **D(t), unrecovered loss:** length lost to our deaths by t, minus our own corpse pearls that we ate back.
  - A death whose corpse we eat back costs nothing, so the top ten's deliberate recycling is not penalised.
  - A death that feeds the enemy or rots costs its full length.
- **D_ref(t):** the top ten's median unrecovered loss at t. Deaths beyond it are charged as income not earned, and fewer
  deaths are credited.

Let R(u) be the **top-10 median income curve on the same map**, made non-decreasing. The **tempo lag** at t is

  τ(t) = t − R⁻¹(N(t))

This is how many rounds ago the top ten were where we are now: a horizontal distance, not a vertical one. It is clipped
to [−60, t].

**Summaries.**

- **Tempo** = the mean of τ(t) over t = 10, 20, …, 150, in rounds behind the top ten.
- **Drift** = τ(150) − τ(50):
  - drift ≈ 0 means we match their rate and are merely late (the shifted curve you described);
  - drift > 0 means we are falling further behind;
  - drift < 0 means we are catching up.
- **Aggregation:** the median over side-games on each map, then the mean over maps, with maps weighted equally.
- **Maps without a top-10 reference** (maps/new, `_tr` variants) use the incumbent's median curve as R. Tempo there reads
  as rounds ahead of or behind the incumbent.

**Why horizontal.**

- A vertical gap scales with the curve (16 length at r25, 67 at r150), so an integral of vertical gaps overweights late
  rounds and needs a map normaliser.
- A lag is in rounds on every map, and a constant lag separates "late" from "slow".
- Income is used as the axis because it is strictly increasing. Material (total length) plateaus on the elimination
  maps (the top ten's PD total is flat 17 → 20 from r25 to r150), where R⁻¹ is undefined.

## Validation on the corpus

20,575 side-games; at most 900 games per map, plus all 1,019 of ours.

| metric | within-map AUC for the win | logit per SD, Elo held | team mean vs Elo (Spearman, 75 teams) | split-half r of team means | SD within team × map |
|---|---|---|---|---|---|
| z-gap of material (vertical integral) | 0.797 | 1.27 | 0.65 | **0.87** | 0.68 SD |
| lag on material | 0.807 | 1.26 | 0.67 | 0.85 | 33 rounds |
| lag on income only | 0.772 | 1.10 | 0.52 | 0.86 | 23 rounds |
| **tempo (net income)** | **0.815** | **1.35** | 0.65 | 0.83 | **20 rounds** |
| tempo at r50 only | 0.738 | 0.91 | 0.55 | 0.81 | 15 rounds |
| drift (r150 − r50) | 0.830 | 1.41 | 0.69 | 0.78 | 30 rounds |

Tempo predicts the game best of the level metrics. It ranks teams as well as the vertical z-integral, and it is in
rounds. It cannot be raised by churn: income ignores recycled corpses, and loss nets out what we eat back.

**What a round is worth.** One round of tempo is −0.067 logit with Elo held; the within-map SD is 24 rounds.

| rounds faster | win at 50 % becomes | Elo-equivalent |
|---|---|---|
| 3 | 55 % | ≈ 48 |
| 5 | 58 % | ≈ 80 |
| 10 | 66 % | ≈ 160 |
| 25 | 84 % | ≈ 400 |

This is an association across games, not a controlled effect.

**Where everyone stands** (median over side-games, maps weighted equally):

| cohort | tempo (rounds behind) | tempo at r50 | drift |
|---|---|---|---|
| top 10 | 0.9 | −1.0 | 9.5 |
| r11–30 | 10.4 | 2.6 | 25.8 |
| r31–50 | 12.6 | 4.0 | 28.1 |
| **us** (all team-7 games) | **25.1** | 12.7 | 36.0 |
| us_now (since 29 Sep 06:00) | 21.8 | 8.6 | 36.9 |
| local renoir-00-base (Ares V06 base) vs the local pool | 1.4 | | |

The local figure is panel-relative: the local pool is weaker than the ladder.

- **Per map, us / top 10:** PD 10 59 / −5, PD 42 / 2, Devil 34 / 4, Trophy 33 / 1, Autarky 31 / 0, Trauma 28 / 3,
  QoS 24 / 2, Portals 13 / 2, Default 11 / 0, Slithery 9 / 1, Schooltime −6 / −1.
- **Drift is positive for everyone**, because the top-10 median is the reference and single games are noisy. Compare
  drift between arms, never against zero.
- **Decomposition:** our 25 rounds are almost all income. The loss term adds about 0.5 rounds. Churn costs us through
  the income our dead newborns never collect, not through the length itself.

## Decision rule

Compare the candidate with the incumbent on the same panel (same maps, opponents and seeds):

  Δ = tempo(candidate) − tempo(incumbent)

Δ is per map (median), averaged over maps, with a 95 % bootstrap CI over games.

- **ACCEPT** if Δ ≤ −3 rounds, the CI's upper bound is < 0, and no single map is significantly slower by more than
  5 rounds (per-map lower bound ≤ +5).
- **REJECT** if the CI's lower bound is > 0.
- **Otherwise: INCONCLUSIVE.** Extend the panel; do not tune on it.

**Why 3 rounds:**

- It is worth ≈ 5 win points at 50 % (≈ 50 Elo).
- It is one eighth of our gap to the top ten, and a third of the gap between the top ten and ranks 11–30.
- It is detectable at current panel sizes. On the local pool, the within-map SD of tempo is **10 rounds** (field: 20). For
  80 % power at 95 %, that needs ~170 side-games per arm unpaired, ~120 with seed pairing (ρ ≈ 0.3), and ~85 at ρ ≈ 0.5.
  A renoir pool run is 125–160 side-games.

Command: `python3 tools/s1/tempo.py compare --cand <bot> --inc <bot> --where "run like '%/pool'"`

**For black-box training** (SPSA, CMA, bandits):

- **Objective:** −tempo, maps weighted equally, on a fixed seeded panel.
- **Per-evaluation noise:** SD ≈ 10 / √n rounds.
- **Promotion:** only through `compare` with the rule above, on a panel the optimiser has not seen (maps/new counts,
  with the incumbent as reference).

**Guards to print beside it** (not in the objective): ally head-on per 1k, per-transit died-3, newborn survival at 10
rounds, and material at r150. A candidate that gains tempo by starving the late game shows up as positive drift or lower
r150 material.

## Caveats

- **Opponent dependence.** Income and deaths depend on who you play, so tempo is only comparable within one panel. The
  field numbers above are for orientation. The decision uses Δ on a fixed panel.
- **The reference is frozen** (`reference.pkl`, top ten as of 30 Sep). Rebuild it only on purpose, and never between a
  candidate and its incumbent.
- **Elimination** carries the last state forward, so an eliminated side's lag grows one round per round. That is
  intended: losing everything is maximal tempo loss.

## Update (30 Sep, later): the reference excludes SSS and Cutlery; the gate is packaged

- **Reference.** `docs/analysis/benchmarks/tempo_reference.json` is now the median of eight top-ten teams. SSS (91) and
  Cutlery (306) are excluded because their unranked games are not their rated bot. Cohort values against it:

| cohort | rounds behind |
|---|---|
| top 10 (all ten) | 3.1 |
| r11–30 | 12.0 |
| r31–50 | 14.1 |
| us | 26.1 |
| us_now | 22.9 |

  Validation is unchanged: AUC 0.815, logit per SD 1.35, within-team × map SD 19.9 rounds.
- **The team-facing gate** is `tools/s1/tempo_gate.py CAND PARENT`, documented in `docs/analysis/BENCHMARKS.md`
  ("Tempo"). It pairs fixtures by file name and needs no store. It adds a **NO GAIN** verdict for when the CI excludes a
  3-round gain.
- **First real use.** Renoir 07c vs 00-base comes out NO GAIN on both panels:
  - pool: −1.2 rounds [−2.4, 0.0];
  - generalisation: +0.1 [−1.6, +1.9];
  - ally head-on +42 %.
  Its +0.11 under the old economy bar was churn.

---
id: S1-F-fingerprinting
author: s1 (Claude, Ouroboros lane)
kind: proposal + first evidence
title: Fingerprinting teams — is this replay the bot the rating belongs to?
data: s1 corpus store (40,593 decoded top-50 live games, 28–30 Sep; games.parquet has ranked / autoscrim / Elo snapshot)
code: none committed yet. The scratch queries behind the numbers are in "Reproduce" at the end.
---

## Problem

A team's rating is earned in **ranked** games. Some teams deploy a different, weaker bot in **unranked** games, so
their unranked replays are not evidence about the bot that holds the rating. This is plausibly deliberate, to hide
the real bot's behaviour from scouting.

Anything that pools replays by team is contaminated:

- the field references and `tempo_reference.json` (which already excludes SSS and Cutlery by hand);
- the strategy atlas and its niches (SSS 09-28 sits in N12, Cutlery in N1);
- the "top 10" cohort curves;
- scouting of a specific opponent;
- Elo-calibration studies.

Live replays carry **no bot identity**: the `bot` field is empty for every live side in the store. There are four
modes, and "forced" (autoscrim) does not imply ranked:

| mode | games | meaning |
|---|---|---|
| RA | 10,096 | ranked autoscrim: opponent not chosen, rating at stake |
| R- | 11,618 | ranked, not autoscrim: challenge; rating at stake |
| -A | 12,733 | unranked autoscrim |
| -- | 23,593 | unranked, not autoscrim |

**The anchor is "ranked", not "forced".** SSS's decoy appears in unranked autoscrims as well. RA is the cleanest
anchor, because the opponent is not chosen either.

## Evidence so far

**1. Win rate against the Elo expectation, by mode.** The residual is the win rate minus the expected score from the
Elo snapshot at game time. Rows are side-games.

| team | -- | -A | R- | RA |
|---|---|---|---|---|
| **SSS (91)** | 857: 0.34 vs 0.62 (**−0.28**) | 627: 0.40 vs 0.66 (**−0.25**) | 48: −0.11 | 91: 0.52 vs 0.50 (+0.02) |
| **Cutlery (306)** | 1,671: 0.57 vs 0.83 (**−0.26**) | 1,041: −0.15 | 58: −0.24 | 100: −0.04 |
| controls: 545, 7, 112 | +0.07 / −0.12 / +0.15 | +0.08 / −0.03 / −0.28 (n 11) | ~0 | −0.10 / +0.06 / −0.01 |
| all teams, weighted | 0.000 | −0.002 | +0.001 | +0.003 |

The residual is centred at zero in every mode overall. Only a few teams carry a large negative unranked residual.

**2. The behaviour differs, and splits cleanly for SSS.** Medians per mode:

| team | mode | units at r50 | pearls at r50 | splits r0–50 | rays per 1k dragon-turns | invalid deaths per 1k |
|---|---|---|---|---|---|---|
| SSS | -- | 4 | 16 | 2 | **0.04** | 0 |
| SSS | RA | 9 | 29 | 12 | **2.83** | 0 |
| Cutlery | -- | 10 | 28 | 13 | 2.60 | **3.5** |
| Cutlery | RA | 11 | 33 | 16 | 2.48 | **16.5** |
| 545 (control) | -- / RA | 12 / 13 | 36 / 35 | 15 / 15.5 | 3.87 / 3.97 | 0 / 0 |
| 7 (us) | -- / RA | 8 / 9 | 21 / 24 | 10 / 11 | 4.01 / 4.01 | 0 / 0 |

**SSS on a single feature.** Split SSS's games at 1 ray per 1k dragon-turns:

| mode | sonar-silent: n, won, expected | sonar-active: n, won, expected |
|---|---|---|
| -- | 499: 0.12 vs 0.69 | 358: 0.65 vs 0.52 |
| -A | 336: 0.16 vs 0.72 | 291: 0.68 vs 0.58 |
| RA | 23: 0.43 | 68: 0.54 |

So SSS runs two bots in unranked play. The sonar-silent one is the decoy. The sonar-active one looks like the ranked
bot and wins as the rating implies, or better.

**Cutlery over time.** Cutlery's invalid-action rate is:

- 09-28: 0 in `--`, 8 in `-A`, 19 in RA;
- 09-29: 7.7 in `--`, 12.3 in `-A`, 15 in RA.

Its ranked bot recycles by invalid action and its unranked bot mostly did not. This is weaker than SSS: Cutlery also
changed versions during the window.

**3. What does not work: a naive ranked-vs-unranked scan.** Across 68 teams with at least 40 ranked and 80 unranked
side-games, a two-sample test on signature features flags many teams (KS ≥ 0.3 for 91, 456, 249, 241, 733, 229, 306,
485, 28, 280). Most of them show no Elo residual. Two confounds explain it:

- **Version churn.** Ranked and unranked games are not spread evenly over time, so a team that resubmits shows a
  "mode" difference that is really a time difference.
- **Outcome dependence.** Within ranked games, winners and losers of the same team differ on sonar rate (median KS
  0.22). Rate features partly measure how the game went, not who played it.

**Conclusion so far.** A decoy shows up as both a behaviour cluster present in unranked games and absent from ranked
ones in the **same time window**, and a negative Elo residual in that cluster. On current data only SSS and Cutlery
clearly meet both conditions. Team 75 (−0.27 on 86 `-A` games) and 485 are worth a look.

## Proposed mechanism

### 1. Anchor

For each team and time window, the reference set is its **ranked** games in that window; RA is preferred and R- is
used when RA is thin. A window is a detected version segment (step 4), or 12 hours when none is detected. By
construction these are the games the rating belongs to.

### 2. Fingerprint features

The features should be **implementation constants**, not outcome summaries. The rules for choosing them:

- **Invariant to outcome.** Within a team's ranked games, winners and losers must not differ (KS < 0.15). Refraction
  share and death-type mix pass. The raw sonar rate only partly does.
- **Invariant to opponent.** The feature must be measured before first contact, or depend on the bot's own code
  rather than on the game state.
- **Distinctive.** Variation between teams must be well above variation within a team and version.

Candidates, strongest first:

| feature | why | status |
|---|---|---|
| **Opening trace**: the exact moves and splits of the starting dragons for rounds 1–N, per map, until first enemy contact | deterministic for a given bot, map and seed, independent of the opponent before contact; an exact match is near-proof | needs extraction from replays (per-dragon actions r0–20); the replay has them |
| **Sonar payload patterns**: header bits, value ranges, per-direction usage | a protocol is a code constant | check whether replays record payloads. The docs say the replay "shows the ray", so the values may be absent |
| sonar ray-direction shares, refraction share, ray-target shares | code constants, weakly dependent on the game | in the store (`rays_*_share`, `ray_refracted_share`) |
| deliberate death types (suicide, invalid) per 1k, and the length and age at death | recycling policy is a constant | in the store and the deaths table |
| split size and child-length mix, first split and first pearl rounds | policy constants early in the game | in the store |
| rays per 1k dragon-turns, units and pearls at r50 | strong but partly outcome-dependent | use with lower weight, or condition on r25 state |

### 3. Per-game score

For each unranked game of team X, compute p(real) = how well its fingerprint matches X's ranked reference in the same
window.

- **Exact layer.** If the opening trace on that map and seed class matches a ranked opening, p = 1. If it matches no
  ranked opening and the ranked set covers the map, count that as strong evidence of a different bot.
- **Soft layer.** Use a robust (median/MAD-scaled) distance to the k nearest ranked games on the invariant features,
  calibrated against the within-ranked leave-one-out distance distribution. p(real) is the percentile.
- **Cluster layer.** Cluster all of X's games in the window. A cluster with no ranked members and a negative Elo
  residual is a **decoy cluster**, and its games are tagged decoy.

Do **not** use the result or the win rate as a feature. The Elo residual is a check on clusters, never a per-game
input.

### 4. Version segmentation

Track each team's ranked fingerprint over time and detect change points on the invariant features. Games are compared
only against ranked games from the same segment. This removes the version-churn false positives in evidence item 3.

### 5. Validation before use

- **Ground truth from our own bots.** The local stores (`build/s1/local`, 133k local results) carry real bot names.
  Measure how well the fingerprint separates versions of the same lineage (e.g. kraken v03 vs v04) against repeat games
  of the same version. Report the false-match rate at the chosen threshold.
- **Live controls.** On teams with no Elo residual in any mode (545, 112, 7), the unranked-games-flagged-decoy rate is
  the false-positive rate. It should be under 5 %.
- **Known decoys.** On SSS, the tagger should recover the sonar-silent cluster without being given the sonar
  threshold.

### 6. Outputs and use

- New table `authenticity(game, side, team, window, p_real, cluster, decoy)` in the s1 store, and a view `sides_auth`
  holding ranked games plus unranked games with p_real ≥ 0.8.
- Rebuild what depends on "top team behaviour" from `sides_auth`. Do it only on purpose, and never between a candidate
  and its parent:
  - the atlas niches;
  - the cohort curves;
  - the next tempo reference, which would let SSS and Cutlery back in.
- **Scouting.** For an opponent, report its real-bot fingerprint (ranked plus authenticated games), with the opening
  trace per map.

## Effort and order

| step | work | estimate |
|---|---|---|
| 1 | segment by time, and cluster on the in-store invariant features, per team; flag clusters with an Elo residual | 2–3 h, store only |
| 2 | validate on local bot names (lineage separation) | 2 h |
| 3 | extract the opening trace (per-dragon actions r0–20) from replays; exact-match layer | 3–4 h, plus a re-decode (~1 h on the Mac) |
| 4 | check whether sonar payloads are in the replay format; add them if so | 1 h |
| 5 | `authenticity` table plus `sides_auth` view; rebuild the atlas on it | 2 h |

Step 1 alone is enough to replace the hand exclusion list. Step 3 is what makes the call per game rather than per
cluster.

## Limits

- **Ranked samples are small** (SSS 139, Cutlery 158 in the window). Some teams have almost none, and those cannot be
  authenticated. Leave them unknown rather than guessing.
- **A team can run its real bot in unranked games too.** SSS does in about 40 % of them. That is fine, because we tag
  games, not teams.
- **A deliberately disguised decoy is possible.** One could copy the opening and differ later. That is unlikely at
  this contest's stakes, and the soft layer still catches differences in outcome-invariant policy.
- **Elo snapshots lag** (`snap_lag_min`). A fast-improving team shows a positive residual in every mode. That is the
  reason to use the residual on clusters, never on single games.

## Reproduce

Run from the repo root. On the Cowork VM, set `PYTHONPATH=build/s1-pylib`.

- Join `read_parquet('build/s1/corpus/sides/*.parquet', union_by_name=true)` to `build/s1/corpus/games.parquet`
  on `game`.
- Take `elo_me` and `elo_op` by side.
- expected = 1 / (1 + 10^(−(elo_me − elo_op) / 400)).
- mode = ranked × autoscrim.
- Group by team and mode.

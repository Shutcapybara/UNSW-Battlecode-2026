# Rome: H-SZ1 Schooltime cage package dose screen

**Date:** 2026-10-04  
**Parent:** `carthage-05-free-sprint` (submission 14585), post-M2 zero  
**Runtime:** `unswbc 1.2.3`  
**Screen:** seed 1, both seats, official outcomes; D-044 screen only, not the D-042 shipping gate  
**Map era:** pool = post-m2 `LIVE_MAPS_M2`; gen = current/unflagged maps plus separately labelled stale pre-swap twins

## Preregistration and doses

The board preregistered one Schooltime cage-safety package: C (split to retain two segments when all moves are fatal;
short non-queen issues an invalid action to avoid a lethal ally collision), D (original queen pays no sprint segments),
and E (non-queens use a lower unit cap to reserve a slot for the queen). Doses were 0=unchanged parent, 1=C+D+E1,
and 3=C+D+E3. Dose 1 and 3 therefore compare package effects against the parent; they **do not isolate E** from C+D.
An E-specific response curve would need a C+D/E0 reference arm. The E reserve is global on non-queen turns in these
versions; it is not cage-conditional. This screen measures its off-cage costs rather than claiming it is safe there.

The fixed primary was Schooltime queen survival at r490. Expected sign: the package increases survival and improves
queen-decided conversions there; dose 3 should reduce cap deaths at least as much as dose 1, with possible material or
win cost on other maps. The preregistered screen was 272 M2 pool fixtures per dose and 464 gen fixtures per dose.
All completed with official outcomes and zero nonzero runner return codes. Gen includes 64 seed-1 fixtures on four
stale twins (`Autarky tr`, `Default tr`, `Prisoners Dilemma tr`, `Trophy tr`); those are historical only, leaving 400
current or unflagged fixtures. The missing Schooltime open4 and PD 10-dragon live variants are not in these panels.

## Dose response

| Panel / map set | Dose | W–L–D | Expected score | Mean pearls r50 / r100 / r150 / r250 | Mean units / total @100 | Queen reached / alive r490 | Queen decided W–L |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pool M2, 17 maps | 0 parent | 226–46–0 | 0.831 | 42.31 / 126.04 / 215.82 / 395.07 | 28.48 / 71.35 | 149 / 0 | 0–5 |
| Pool M2 | 1 | 229–43–0 | 0.842 (+1.1 pp) | 43.87 / 125.98 / 211.03 / 388.14 | 28.70 / 73.50 | 147 / 11 | 9–4 |
| Pool M2 | 3 | 224–48–0 | 0.824 (−0.7 pp) | 43.84 / 125.06 / 208.80 / 383.99 | 28.44 / 73.86 | 150 / 14 | 11–3 |
| Gen, all 29 templates | 0 parent | 349–115–0 | 0.752 | 44.65 / 123.34 / 193.51 / 286.57 | 29.56 / 73.96 | 71 / 2 | 2–2 |
| Gen, all | 1 | 353–111–0 | 0.761 (+0.9 pp) | 45.13 / 124.82 / 197.37 / 294.81 | 29.97 / 75.96 | 72 / 0 | 0–3 |
| Gen, all | 3 | 355–109–0 | 0.765 (+1.3 pp) | 45.18 / 123.73 / 194.83 / 291.97 | 29.78 / 75.73 | 71 / 0 | 0–2 |

Pool queen survival conditional on reaching r490 was 0/149 at dose 0, 11/147 (7.5%) at dose 1, and 14/150 (9.3%) at
dose 3. Joint reached-and-alive over all 272 games was 0, 11 (4.0%), and 14 (5.1%). The target file's provisional
all-map queen target is ≥0.42 among RL-reached games; these seed-1 package screens remain below it and are not
comparable to a map-specific percentile target. Parent-relative differences are descriptive only; no post-M2 field
economy reference has been published for this panel.

On the frozen Schooltime template (16 fixtures per dose), parent was 14–2 and the queen reached/alive counts were
16/0. Dose 1 was 16–0, with 12 reaching r490 and 11 alive (91.7% among reached; 11/16 joint). Dose 3 was 15–1, with
13 reaching and all 13 alive (100% among reached; 13/16 joint). The template's queen-decided result shifted from 0–2
to 9–0 (dose 1) and 11–0 (dose 3). The M2 set omits the open4 Schooltime variant, so this is not a transfer check
across both live hashes.

On gen current/unflagged maps alone, parent was 288–112–0 (0.720), dose 1 was 292–108–0 (0.730), and dose 3 was
294–106–0 (0.735). The 64 stale-twin fixtures were 61–3 for all three arms, so they do not explain the current-gen
win increase. The gen queen r490 counts above include stale twins; current-map queen survival was zero for both
positive doses in this seed-1 sample.

## Side effects and map/regime deltas

Pool mean r100/r250 pearls changed by −0.07/−6.93 at dose 1 and −0.99/−11.08 at dose 3. Current-gen means changed
by +1.79/+10.05 at dose 1 and +0.53/+6.57 at dose 3. Units@100 and total@100 were +0.22/+2.15 (dose 1) and
−0.04/+2.51 (dose 3) on pool; current-gen changes were +0.48/+2.33 and +0.26/+2.07.

Deaths per 1,000 dragon-turns, pool parent → dose 1 / dose 3: wall 7.21 → 1.46 / 1.48; own body 3.58 → 2.28 / 2.34;
ally body 1.56 → 0.78 / 0.81; ally head-on 1.24 → 1.28 / 1.27; invalid 0 → 8.07 / 8.11. Gen all-map invalid deaths
rose from 0 to 2.44 / 2.44 per 1,000, while wall deaths fell 2.13 → 0.79 / 0.79. The invalid-action increase is a
direct cost of C's deliberate short-dragon deaths and is a tier-2 guard concern; the seed-1 screen cannot make a gate
claim.

On the pool, elimination win delta was −0.8 pp at dose 1 and −0.8 pp at dose 3; round-limit win delta was +2.7 pp and
−0.7 pp respectively. On current gen maps, elimination win delta was +2.1 pp and +1.8 pp; round-limit was −5.1 pp
and 0.0 pp. Each regime has only seed-1 fixtures. Full per-map/hash checkpoint and side-effect deltas, and per-regime
rows split by map era, are in [`rome-SZ1-dose-screen-permap.csv`](../../game_stats/runs/rome-SZ1-dose-screen-permap.csv)
and [`rome-SZ1-dose-screen-regime.csv`](../../game_stats/runs/rome-SZ1-dose-screen-regime.csv). Machine-readable
absolute panel values are in [`rome-SZ1-dose-screen`](../../game_stats/runs/rome-SZ1-dose-screen).

The sandbox CPU probe peaked at 10.14M points for E1 on live Schooltime, 10.28M for E3 on Schooltime, and 10.37M for
E3 on live Slithery Fight, below the 30M/turn cap.

## Finding

HOLD at screen stage. Dose 1 has the clearest Schooltime win count and a modest positive M2/gen current win response;
dose 3 has the better reached-queen survival fraction but a lower pool win score than the parent. Both raise invalid
deaths and neither establishes full-panel D-042 acceptance. Do not stack. If continuing this family, first add a C+D/E0
control to attribute E, then restrict any reserve to a measured cage/cap state and run seeds 1–3 on both panels before
considering a temporary candidate.

## D-044 RL translation

- **Observation:** exact one-step legality for all four directions; original-queen identity, alive state, position,
  and whether every move is fatal; current unit count and cap; nearby body/head occupancy and accessible exits. The
  reserve rule also needs a reliable team-level cage signal and cap overshoot state. A static kelp-only destination
  pocket feature is relevant to the separate H-KZ12/H-H6 pathway, not a substitute for current body-aware legality.
- **Action:** choose a legality-checked rescue split that preserves the queen's two-segment parent; otherwise choose
  a legal route or safe escape. A learned action could allocate production under a predicted cap-overshoot risk rather
  than issue routine invalid commands to non-queens.
- **Value/reward:** queen alive at r490 and queen-decided win are sparse terminal rewards; shaping can include queen
  survival over the next k rounds, available exits after action, expected cap legality, and team win potential. Penalize
  invalid deaths, lost length/units, and foregone food so that a queen-survival gain does not mask broad costs.
- **Demonstration:** top-team post-M2 data shows high queen survival on Schooltime (Nara's 51/53 top-ten reached RL
  sides), and Shenzhen's C+D+E simulator probe preserved the queen in its selected Schooltime fixtures. The exact
  reserve threshold and global non-queen policy are not established by top-team action traces here; those require
  more demonstrations or exploration with the missing live variant and an E0 control.

# P-hinata-03 (R2, BC direction head in carthage-05's prior slot) — Sugawara review (council round 2, mechanism seat)

4 Oct 2026, 15:29Z. Claude-family card reviewed by a Claude-family seat: this review does not stand alone; it
needs Tanaka's or Nishinoya's. No bot run, no confirmation row, no held-out label read.

## Verdict: AMEND (three exact changes, none changes the intervention)

1. **Train on `cd_known = 1` rows only (or drop the `pearl_in` channels for every row), and report the share.**
   The card keeps variant games with `cd_known = 0` in the training rows (§1, §4). `tools/learn/encode.py` l.51, Data's
   own contract, says: "Train P/V on rows with cd_known = 1 or drop pearl_in, else the model sees a distribution the
   bot never sees." The deployed bot always has `cd_known = 1` (it reads real bed timers). Rows reach `cd_known = 0`
   not only on the two variant maps but on any game where the oracle has no seed or mismatches the rebuild
   (`dataset.py` l.45–53 falls back to `rebuild_redacted`). Schooltime and Prisoners Dilemma alone are 297 of 1,925
   teacher sides (15.4 %, `teachers_v1.parquet`); the smoke file is 11,838 of 11,838 `rebuild_redacted`. Exact change:
   §4 "Rows" adds "rows with `x_cd_known = 0` are excluded from fitting; their count and share per map are reported;
   the confirmation population's oracle coverage is reported per map before release, and confirmation accuracy is
   reported on `cd_known = 1` rows (binding) and on all rows".
2. **State the B class in the C++ slot.** The parent's HB-1 model is 3-class (F/R/L). In `policy.hpp` l.1416–1428,
   `hb_logp[]` starts at 0.0 and only the three predicted directions get `λ·log p < 0`, so the **reverse first step
   receives the largest prior (0)**. P1 is 4-class (labels v1, F/R/B/L), so the swap also changes how reverse moves
   are priced. That is inside the slot, but it is a second behaviour change and must be written down. Exact change:
   §1 "The one switch" adds "all four first steps read λ·log p₁(d), floored at 1e-4 as the parent; with the switch
   off, the parent's reverse = 0 is kept bit for bit". G-parent is then scored on all move rows with HB-1 credited
   0 on B labels, and the B share is printed (smoke: 0.43 %, so this tilts G-parent by under half a point).
3. **G-parent is close to a certainty, so add one cheap check that can fail.** P1 is fitted on top-ten post-m2 play
   and scored on top-ten post-m2 play; HB-1 was fitted on one team before m2. Beating HB-1 on those rows measures
   population fit, not whether the switch moves our play. Keep G-parent as the offline gate (I prefer it to G-macro,
   for the card's reason), and add a report-only **flip rate**: on REG-000's own panel decision logs (existing gate
   fixtures, no new run beyond the parent replay Asahi already produces), the share of move decisions whose argmax
   changes when P1's prior replaces HB-1's. Pre-register: flip rate < 1 % of move decisions → the panel stage is
   not run (the switch cannot move Δwin by a measurable amount). Also print the mean entropy of P1 and HB-1 on the
   confirmation rows: λ = 1 was tuned for HB-1's sharpness, and a sharper P1 at the same λ is a larger dose.

## Mechanism checks

- **Legal observation.** Encoder v1 is the per-process view plus own memory, no absolute x/y, W/H or facing; R0 parity
  40,002 turns. Features I checked in the smoke schema (`x_round`, `x_rounds_left`, echo counts, `x_ownq_*`,
  `x_enemyq_*`, `x_home_*`, `x_mirror_*`) are all computable at TurnStart from the IO block and own memory. The one
  skew is `pearl_in`/`cd_known` (item 1).
- **Complete RL translation.** Yes (§6). Missing piece: covariate shift. Accuracy is measured on teachers' states,
  and the prior acts on ours (the DAgger problem). The flip rate (item 3) is the cheapest proxy until R6 refits on
  search targets.
- **Simpler known method.** A direction prior from a frequency table keyed on the 3×3 local cells would be simpler,
  but the parent already has a learned prior; replacing it with a better-fitted one is the minimal step. No objection.
- **Leakage.** Teacher list v1 has 14 training maps; Autarky, Maze and Trauma are absent (checked `maps` in
  `kageyama-teachers-v1.json`); smoke audit 0 held-out-map hits. Series-grouped folds. Confirmation teams are the same
  teams as training, so the held-out read is map transfer, not opponent transfer; the card says so.
- **Train/deploy skew besides item 1:** labels v1 are relative to facing at turn start, as the C++ slot reads them.
  Turns on which the teacher did not move (split, cull) are excluded from training but the prior is applied on every
  move-search turn; that is the same conditioning as HB-1 and acceptable.

## Replication (frozen inputs, cloud copy of `smoke.parquet`, no write to other lanes' dirs)

- Move-turn class shares, smoke file, both sides, 11,594 move rows (one team, 3 games, census, no interval):
  F 0.510, R 0.221, **B 0.0043**, L 0.265. Side A only: F 0.551 (matches the card's majority 0.551 on its 6,289 rows).
- B occurs at length 2 (28/6,559), 3 (16/3,946) and 6 (4/625): reverse first steps are rare but real, so item 2 is
  not empty.
- `blocks_src` = `rebuild_redacted` for 11,838/11,838 smoke rows (`cd_known = 0`), which is why item 1 needs a
  per-map share from the real build.

## Numbers (subjective forecasts)

- Development accuracy ≥ 0.75 (falsifier not triggered): **0.55**. HB-1's 0.83–0.85 was one team with per-candidate
  features; ten pooled styles with encoder v1 alone lose both.
- **P(G-macro) = 0.10.**
- **P(G-parent) = 0.85**, conditional on HB-1 being scored on the same rows. The card's 0.45 is too low for an
  in-distribution model against an out-of-distribution one.
- P(D-046 §4 panel gate pass at λ = 1, given an offline pass) = **0.20**. Expected pool Δwin +0.5 pp (80 %: −2 to +3).
- P(flip rate < 1 %) = 0.15.

## Dissent

The card's mechanism quote (HB-1 accuracy → win rate against Ares V04) is a between-model curve on one team's own
play. It does not transfer to "a more accurate prior on others' play raises our win rate" — the prior is one term,
outbid by the search's own scores. I expect the panel effect to be near zero unless λ is raised, and λ is the dose.

## Precedent

- AlphaGo's SL policy (57 % move accuracy) as the search prior: accuracy mattered through the prior, with diminishing
  returns past the search's own strength.
- Kaggle Hungry Geese and Lux: imitation of top replays plus a light search was a common top-tier recipe. Pooling
  conflicting styles raises irreducible label disagreement (the card's own G-parent argument); per-teacher accuracy
  should be read before pooling is judged.
- DAgger (Ross et al. 2011): covariate shift is the expected failure of pure BC priors; expert iteration (R6) is the
  standard fix.

# P-2 (P-hinata-02, R1 V0b logistic) — Sugawara council review (mechanism seat)

2026-10-04, round 1 (D-047/D-049/D-051 §6). Verdict: **AMEND.** Bind Tanaka's corrected G-amend on a pre-declared
**ranked ∩ series-clean** held-out population, with the full held-out population as a pre-declared sensitivity column.
Separately: V0b is a **privileged (spectator) value**, not a deployable search leaf. The card's R5 claim must be struck
or rerouted (§3). Tanaka's eligibility HOLD stands. I read no held-out label.

## 1. Replication (frozen inputs only)

- `build/hinata/v0/fit-lq/oof.parquet` (frozen 10:51Z), my own sklearn AUC: RL ΔAUC r50 **+0.01969** (3,503 games),
  r250 **+0.05574** (3,273), r400 **+0.10172** (3,141). This matches the card and Tanaka's table to 5 decimals.
  Post-m2, mixed ranked and unranked, 14 development maps.
- `train_rows.parquet`: 5,799 games / 1,777 series. This matches Tanaka.
- **New count (answers part of D-051 §6 ahead of Kageyama).** I joined `build/s1/corpus/games.parquet` (snapshot
  mtime 11:13Z; the store is still growing, so this is not a frozen manifest) to the training rows' series ids. The
  rows are held-out-map post-m2 games, `in_scope`, decisive. **No outcome column was read for these.**

  | map | ranked: games / in a consumed series | unranked: games / consumed |
  |---|---|---|
  | Autarky | 659 / 264 | 348 / 170 |
  | Maze | 675 / 276 | 304 / 157 |
  | Trauma | 685 / 285 | 395 / 191 |

  Total **3,066 games / 2,193 series**. **1,723 games (56 %) / 1,262 series are series-clean.** Ranked and clean is
  **≈1,194 games** (Autarky 395, Maze 399, Trauma 400). A post-m2 series has a median of 5 games on 5 maps, so
  consumption is substantial but does not empty the pool. The clean population stays usable.

## 2. Mechanism: what series overlap can and cannot leak

- V0b has 8 coefficients per cell, no intercept, no opponent or map identity, and was fitted on ~4–7 k rows per cell.
  Sharing a series between training and scoring can bias an 8-parameter linear model only through series-level
  covariance of (features, outcome). With no identity features, I expect that bias to be negligible. The real damage
  is to the **independence of the scoring units**: the intervals are optimistic. It is not a bias in the point ΔAUC.
- Tanaka's prerequisite (bind on clean series) is still right, for a different reason: **selection.** "Clean"
  correlates with *time*. Series whose games were not yet decoded at 10:51Z are newer, so the clean population sits
  later in the field's drift. Report the clean vs consumed point ΔAUC side by side. A large gap would be drift or
  selection, not leakage. Freeze which column binds **before** reading either. My recommendation is ranked ∩ clean.
- **Train/deploy check on features.** The inputs are `total_share`, `units_share`, `longest_rel`, `pearls_share`,
  `territory_share`, `deaths_share`, `q_alive_c` and `q_len_c`. All of them are built from **replay truth for both
  teams** (`tools/hinata/v0.py` `load()`: `opp_*`, `qd_opp`, `ql*_opp`). Kageyama's legal encoder
  (`tools/learn/encode.py` SC list) has own `length`/`unit_count` and *visible* enemy parts and queen sightings only. It
  has no opponent total, opponent pearl count, opponent queen length, or opponent queen-death flag. The regime is also
  a map-name lookup (the card says so). So V0b answers "who wins from a spectator's state". It is a legitimate R1
  object (outcome structure, value target), but **no dragon can evaluate it at its turn start.**

## 3. RL translation and the simpler known method

- **What V0b is:** a privileged/asymmetric critic. The precedents are asymmetric actor-critic (Pinto et al. 2017) and
  MAPPO/CTDE centralised value functions. For that use (training-time critic, advantage baseline, potential for
  shaping in self-play rollouts where the engine supplies both sides), it is directly usable as it stands.
- **What it is not:** the card's "most usable as a search leaf (R5)". A leaf evaluated at deployment needs inputs from
  the legal observation. Plugging in our *estimates* of opponent totals or queen state would be exactly the encoder skew
  I flagged at intake (§3). Recommendation (information-adding, not a gate change): once the decode completes, fit
  **V-legal**, the same logistic on encoder-legal features (own length/units, visible-enemy aggregates,
  `enemyq_visible/age/vis_parts`, `ownq_*`), on the same rows and folds. Report ΔAUC(V0b − V-legal) per cell. That gap
  is the **value of opponent information**, and it is what sonar relays (R3/R4) could buy back. It sizes the
  information-propagation track with a number rather than a belief. AlphaStar's value network saw opponent
  information during training while its policy acted on legal observations. That split is the known-good pattern.
  (Hungry Geese and Lux are fully observed, so they offer no precedent on this point.)

## 4. Gate recommendation

Tanaka's corrected G-amend: series-bootstrap 5th-percentile ΔAUC > −0.01 every cell; RL r150/250/400 lower bound > 0;
|slope_V − 1| ≤ |slope_Φ − 1| + 0.05 from r25 (the two-sided form closes the under-confidence loophole in the card's
one-sided clause); ranked RL r50 AUC ≥ 0.66 and ≥ AUC_Φ. Population: ranked ∩ clean binds, full held-out reported.
Comparator Φ is frozen on c958e8c7 rows (D-051 §6 already orders this).

**One amend to flag, not to impose:** the elim r10 cell (AUC 0.54, near-noise) is the most likely single failure. In
development its Δ is −0.003 [−0.005, −0.000] on 2,274 games. Only Autarky (~395 ranked-clean games, ~1/6 of the
development n) scores elim cells, so the 5th percentile widens to roughly −0.003 − 1.645 × 0.0037 ≈ −0.009. That puts
**about 40 % chance of failing the −0.01 margin on that cell alone**, with no information content. The Chair could
make r10 report-only. Because the development r10 result has been seen, this must be decided by the Chair in D-052 on
the stated reason (r10 carries no gating information in either regime), not by any lane after confirmation.

## 5. P(pass) (confirmation passes, frozen weights, ranked ∩ clean)

| reading | P(pass) |
|---|---|
| G-asis | **0.03** |
| G-amend as written (card) | **0.45** |
| Tanaka-corrected, r10 gating | **0.40** |
| Tanaka-corrected, r10 report-only | **0.55** |

Expected effect: RL ΔAUC ≈ +0.02 (r50) / +0.05 (r250) / +0.09 (r400) on Maze + Trauma; elim ≈ 0 to r150 on Autarky.
The main risks are elim r10 noise, the Autarky-only elim cells (one map), and Trauma's queen-death profile (our queen
dies unusually often there, so q_alive variance is higher). The last is more likely to help ΔAUC than hurt it.

## 6. Dissent

- With Tanaka against the "calibration slope cannot pass" framing: Platt recalibration within training folds
  preserves AUC. It is not needed for R1, but it is the cheap fix if slopes are ever binding.
- With Nishinoya on the 0.60. That figure ignores the one-map elim cells and the 1/6 sample. 0.40–0.55 is my range.
- Against reading a pass as "V0b is the R5 leaf". See §3. A pass certifies the spectator value only.

Inputs read: card, `tools/hinata/v0.py` (load, lomo), `tools/learn/encode.py` (SC list), P-2-tanaka, P-2-nishinoya,
D-047/049/051 BOARD lines. Compute: cloud container copy of the four frozen files, no writes to other lanes' dirs.

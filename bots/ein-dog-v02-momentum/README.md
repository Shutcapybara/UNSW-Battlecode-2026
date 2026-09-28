# ein-dog-v02-momentum: EWMA move-continuity, scoped off compact maps

Ein_dog lineage frontier candidate 2 (2026-09-28). Parent: ein-dog-v01-control
(byte-frozen newton-x10: fafnir policy + fast-bed contest + conversion stop
200). One mechanism added — **the owner's move-continuity idea**:

- **Direction EWMA** (`w_dir 0.8`, `dir_alpha 0.3`, `w_dir_nc 256`): each
  dragon process keeps an exponentially-weighted mean of its chosen
  first-step directions; single-step candidates score
  `+ w_dir * (ewma[d] - 0.25)`. Continuing the recent heading wins near-ties;
  reversals are mildly penalised; newborns start flat (momentum is earned).
  Inactive on maps of at most 256 tiles, where swarm brawls need agility.

Measured (deterministic engine, paired per fixture vs ein-dog-v01-control):

| Battery | Control | v02 | Verdict |
|---|---|---|---|
| Screen 32 | 25-7 | **30-2 (+5, +5/−0 flips)** | PASS (gate ≥ +2) |
| Reserve 16 (frozen families) | 13-3 | **14-2** | PASS (no regression, +1) |
| Gauntlet 182 (7 refs × 13 maps) | 145-35 | **146-36 (+1; +17/−17)** | **the ≥ +3 promotion gate is NOT met** |
| Broad synthetic 280 | — | in flight | — |

Per-map on the gauntlet, momentum is **bistable**: +10 combined on Queen of
Spades 14-0 (+2), Trophy 14-0 (+3), Autarky 13-1 (+3), Trauma 13-1 (+2);
−8 on the farm-economy trio Schooltime 10-4 (−3), stronghold 11-3 (−3),
Default 10-4 (−2). Autopsy: on Schooltime the control's micro-dither wins by
r339 elimination while momentum's committed farming runs to r500 with ~50%
more deaths and loses the length race — the farm loop is an economy, and
heading commitment amplifies it. A room-gated variant (x15: momentum only
where flood area ≥ body + 2) recovered Schooltime (+0) but diluted the
open-map gains (gauntlet 145-37); no tested observable (kelp fraction, bed
fraction, renewable-bed share, size) separates the two map classes without
overfitting. w_dir dose-response at this scope: 0.4 → +1, **0.8 → +5**,
1.6 → ±0 (stable interior optimum).

**Status: measured frontier candidate, not promoted.** By the strict
pre-registered gate (gauntlet ≥ +3), ein-dog-v01 remains the release. Adopt
v02 if the four-map gains (incl. the two 14-0 shutouts) are worth the
farm-trio cost on the expected map distribution — the ledger's weighted
synthetic evaluation (running) informs that trade.

Full evidence and failed-arm autopsies (entry-gating, eat-vacancy, crown
tail-transfer, three conversion-trigger variants, sensitivity arms):
`experiment_data/eindog_20260928/{DESIGN,LEDGER,SYNTHESIS}.md`.

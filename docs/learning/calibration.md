# Council calibration (Chair)

Each seat states P(pass) for the card's frozen objective before the run. After the result card, the Chair scores
`Brier = (P(pass) − outcome)²`, with outcome 1 for pass and 0 for fail or reject. A card that ends INCOMPLETE or is
withdrawn is not scored. After 10 scored cards, rotation frequency follows mean Brier score, not model family
(macro §3.6).

## Seats

| Seat | Model family | Style | Since |
|---|---|---|---|
| Tanaka | GPT | auditor (standing seat on every statistics-bearing card) | 4 Oct 10:43Z |
| Sugawara | Claude | mechanism | 4 Oct 10:40Z |
| Nishinoya | GLM | probe (results are `unaudited` until an auditor replicates them) | 4 Oct 10:52Z |

## Predictions on file (scored when the result card lands)

| Card | Event | Seat | P(pass) | Filed |
|---|---|---|---|---|
| P-2 | confirmation passes under G-asis | Nishinoya | 0.03 | 4 Oct 11:50Z |
| P-2 | confirmation passes under G-amend as written | Nishinoya | 0.60 | 4 Oct 11:50Z |
| P-2 | confirmation passes under G-asis | Tanaka | 0.03 | 4 Oct 12:02Z |
| P-2 | confirmation passes under G-amend as written | Tanaka | 0.35 | 4 Oct 12:02Z |
| P-2 | confirmation passes under Tanaka's corrected G-amend | Tanaka | 0.20 | 4 Oct 12:02Z |
| P-2 | development fit passes G-amend (author, before the fit) | Hinata | 0.60 | 4 Oct 10:51Z; outcome pass; not a council seat, not scored |
| P-2 | confirmation passes under G-asis / card G-amend / corrected / corrected with r10 report-only | Sugawara | 0.03 / 0.45 / 0.40 / 0.55 | 4 Oct 12:30Z |
| P-2 | clean confirmation under G-amend (revision) | Nishinoya | 0.50 | 4 Oct 12:50Z |

**Scored event (D-052 §A.8):** the confirmation returns PASS under `P-2-gate-spec.D-052.json`. Forecasts filed for
this exact event before the claim: **Tanaka 0.40** (13:55Z), **Sugawara 0.50** (13:42Z), **Nishinoya 0.50** (13:46Z).

**Scored event (D-053 §D):** `asahi-05-kz12-k16` passes the D-046 §4 gate on seeds 2–3. Forecasts filed before the
card: **Sugawara 0.35** (14:45Z), **Nishinoya 0.40** (14:46Z), **Tanaka 0.35** (14:51Z).

**Scored event (D-054 §C):** P-4's seed-1 screen returns support at m = 0. Forecasts: **Sugawara 0.35** (revised
15:29Z; 0.40 at 14:58Z stays on record), **Tanaka 0.30** (14:58Z); Nishinoya open.

**Scored event (D-054 §C), update:** Nishinoya filed 0.45 for P-4 (15:58Z).

**Scored event (D-055 §E):** P-5's binding offline gate passes (paired with the parent's prior, series-clean cohort).
Forecasts for the amended card: **Sugawara 0.70** (16:28Z), **Tanaka 0.60** (16:00Z, union features), **Nishinoya
0.55** (15:58Z, amended).

**Scored events (D-055 §F), P-6:** no falsifier triggered: Sugawara 0.80, Tanaka 0.80, Nishinoya 0.80. V-legal ≥ Φ at
round-limit r50: 0.20 each.

**Scored event (D-056 §C), LS-1:** the frozen rule of D-055 §B says PASS, including the declared extension.
Forecasts: **Sugawara 0.50** (17:29Z, before dispatch), **Nishinoya 0.45** (17:52Z, after dispatch and before
outcomes; flagged). Tanaka's 0.45 (17:56Z) is declared by its author not a calibration entry and is not scored.

**Scored events (D-063 §D), P-7** (entry throughput / head-to-head ≥ 0.55 / panel ≥ +0.02 / live promotion):
Sugawara 0.75 (0.60 before replication) / 0.45 / 0.25 / 0.15; Tanaka 0.55 / 0.40 / 0.20 / 0.10; Nishinoya 0.50 / 0.50
/ 0.20 / 0.10.

**Earlier round-2 numbers, kept on record, not scored:** Sugawara on P-5: accuracy ≥ 0.83: 0.10; beats the parent's prior: 0.85; panel gate given an
offline pass: 0.20. On P-6: falsifier not triggered 0.85; V-legal ≥ Φ at round-limit r50: 0.20. The scored events are
fixed in D-055.

## Scores

| Card | Objective | Outcome | Seat | P(pass) | Brier |
|---|---|---|---|---|---|
| P-2 | D-052 §A: one confirmation on the held-out maps | **fail** (elimination r25 −0.0099 [−0.0152, −0.0049]) | Tanaka | 0.40 | 0.16 |
| P-2 | same | fail | Sugawara | 0.50 | 0.25 |
| P-2 | same | fail | Nishinoya | 0.50 | 0.25 |
| P-4 | D-054 §C: support at m = 0 (strike-hazard ratio < 0.90 with the guards) | **refuted** (1.069 [0.685, 1.788]) | Sugawara | 0.35 | 0.1225 |
| P-4 | same | refuted | Tanaka | 0.30 | 0.09 |
| P-4 | same | refuted | Nishinoya | 0.45 | 0.2025 |
| P-A02 (REG-002) | D-053 §D: local gate passes on seeds 2–3 | **hold** (pool +1.10 [−0.37, +2.76]) | Sugawara | 0.35 | 0.1225 |
| P-A02 (REG-002) | same | hold | Nishinoya | 0.40 | 0.16 |
| P-A02 (REG-002) | same | hold | Tanaka | 0.35 | 0.1225 |

## Running means

| Seat | Cards scored | Mean Brier |
|---|---|---|
| Tanaka | 3 | 0.124 |
| Sugawara | 3 | 0.165 |
| Nishinoya | 3 | 0.204 |

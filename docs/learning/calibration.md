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
**Outcome (D-069 §A): not scored.** The screen expired at 75 of its 102 planned pairs with the letter HOLD and the
extension was not run, so the event ended incomplete.

**Scored events (D-063 §D), P-7** (entry throughput / head-to-head ≥ 0.55 / panel ≥ +0.02 / live promotion):
Sugawara 0.75 (0.60 before replication) / 0.45 / 0.25 / 0.15; Tanaka 0.55 / 0.40 / 0.20 / 0.10; Nishinoya 0.50 / 0.50
/ 0.20 / 0.10.

**Scored event (D-064 §B), k = 16:** no rollback under D-052 §B within the first 120 ranked games, given promotion
and observation to 120 games. Forecasts: **Tanaka 0.85** (22:25Z), **Sugawara 0.87** (22:30Z), **Nishinoya 0.85** (22:52Z).
**Outcome (D-075 §A): 0.** D-052 §B fired at 45 ranked games and 16979 was rolled back at 5 Oct 04:53:55Z. Sugawara, 02:28Z: P(D-052 §B fires within 16979's first 40 ranked games) 0.08, revised to 0.75 at 29 games (03:34Z); neither is council-scored. Nishinoya also gave P(LS-1 shows harm) 0.10 and P(live Weakhold gain ≥ 10 points sustained) 0.60 (not scored).

**Author's forecasts, full-row refit (D-065 §C), not council-scored:** Hinata: best tree ≥ 0.75 on the full rows 0.40;
A10b on the full rows beats the trees (paired 5th percentile > 0) 0.15.

**Single-seat forecast (D-066 §E), recorded:** Sugawara: the selected arm's in-bot parity stays under 1e-6 on at least
three maps at the first attempt: 0.85 (00:29Z).

**Forecasts on file (D-068 §C), Sugawara 01:31Z:** the A1 placeholder at λ = 1.41 within −2 points on the pool 0.35;
slot fallback on more than 1 % of turns on some map 0.15; carthage-05 with no prior at or below −7 points 0.55.
Nishinoya asked. Asahi's own forecast for the placeholder screen was +1 point (outcome −7.0; not a council seat).
Asahi's forecasts for the D-068 queue (02:15Z, not a council seat): A1 at λ 1 −4 points; no prior −8; λ 1.41 −3.

**P-8 (D-068 §D), author's forecasts, not council-scored:** S0 0.60; S0 on direction 0.25; S1 given S0 0.20; S2 0.20;
live within the season 0.07.

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
| P-7 | D-063 §D, entry throughput ≥ 1×10⁷ decisions an hour on ≤ 8 cores | **pass** (1.89×10⁸; at least 8.4×10⁷ under the worst core accounting; D-066 §B) | Sugawara | 0.75 | 0.0625 |
| P-7 | same | pass | Tanaka | 0.55 | 0.2025 |
| P-7 | same | pass | Nishinoya | 0.50 | 0.25 |
| P-A02 (REG-002) | D-064 §B: no rollback under D-052 §B within the first 120 ranked games | **rolled back** at 45 games (−0.263 against 14585's last 120; 95th percentile −0.126; D-075 §A) | Tanaka | 0.85 | 0.7225 |
| P-A02 (REG-002) | same | rolled back | Sugawara | 0.87 | 0.7569 |
| P-A02 (REG-002) | same | rolled back | Nishinoya | 0.85 | 0.7225 |

## Running means

| Seat | Cards scored | Mean Brier |
|---|---|---|
| Tanaka | 5 | 0.260 |
| Sugawara | 5 | 0.263 |
| Nishinoya | 5 | 0.317 |

**Closed (D-075 §A).** The council was dissolved by D-072 §B; no further events are scored. Ten scored cards were
never reached, so rotation by score did not come into use. The largest single error of every seat is the last
entry: all three put at least 0.85 on the k = 16 promotion surviving its rollback rule.

**Chair's forecast on file (D-075 §E), not council-scored:** the team-213 prior at λ 1 is not below the incumbent on
the seed-1 pool (paired 5th percentile above −5 points): 0.12; point forecast −8 points.

**Chair's forecasts on file (D-076 §D), not council-scored** (pool difference against carthage-05; P that the paired
5th percentile is above −5 points): A1-400 at λ 1.72: −2 points, 0.35. The team-213 prior at λ 1.45: −4 points,
0.25. Sugawara (owner, 05:30Z): q2b's pool 5th percentile above −5 points 0.55; q2b at least +5 points over
carthage-05 on the queen-keeper panel 0.40.
**Outcome of the owner's two q2b forecasts (Asahi, 06:19Z):** pool −2.39 points [−5.89, +0.92] (5th percentile below
−5: event failed, Brier 0.3025); keeper panel against `bokuto-04-queen` 12 of 34 against 16 of 34 (event failed,
Brier 0.16).

**Outcome of the Chair's λ 1.72 forecast (Asahi, 07:21Z):** A1-400 at λ 1.72 −7.35 points [−12.15, −2.21] (forecast −2;
event "5th percentile above −5" at 0.35 did not occur; Brier 0.1225).

**Chair's forecasts on file (D-077), not council-scored.** Trial 2 (`bokuto-13-cull`, primary statistic at rating
1725): point +0.10; exceeds 14585's reference (−0.043) by more than 0.03: 0.75; highest of the three windows: 0.60.
A1 on the full rows at λ 1.76 on the seed-1 pool: −6 points; 5th percentile above −5: 0.15.

**Outcomes of the 213 arms (Asahi, 08:11Z):** λ 1 −12.50 points [−17.28, −7.35] (Chair −8, 0.12: Brier 0.0144; Hinata
−9, 0.08: 0.0064); λ 1.45 −12.68 [−17.83, −7.54] (Chair −4, 0.25: 0.0625; Hinata −5, 0.25: 0.0625). Hinata's
forecasts on file (07:38Z): A1-full at λ 1.76 −7 points, 0.12; the stop rule fires 0.62; P-9 stage S1: +1 point,
0.30 that the point is positive and the 5th percentile above −3. The Chair's point forecasts for the clone arms
have been too optimistic on every arm so far (three of three).

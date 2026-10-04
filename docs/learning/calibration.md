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

**Scored event (D-053 §D):** `asahi-05-kz12-k16` passes the D-046 §4 gate on seeds 2–3. Forecasts to be filed on the
BOARD before Asahi posts the card.

## Scores

| Card | Objective | Outcome | Seat | P(pass) | Brier |
|---|---|---|---|---|---|
| (none yet) | | | | | |

## Running means

| Seat | Cards scored | Mean Brier |
|---|---|---|
| Tanaka | 0 | n/a |
| Sugawara | 0 | n/a |
| Nishinoya | 0 | n/a |

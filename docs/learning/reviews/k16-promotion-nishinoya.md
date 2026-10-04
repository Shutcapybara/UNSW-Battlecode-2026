# k16 promotion round — Nishinoya (GLM, probe seat)

D-063 §B's immediate round (due 23:30Z): promote `asahi-05-kz12-k16` at LS-1's stop unless LS-1 shows
harm. Unaudited until Tanaka replicates.

## 1. Verdict

**Agree with the proposed rule, with two reporting amendments.** Promote unless LS-1 shows harm
(95th percentile of the paired mean below 0 on opponent × map clusters, or any runtime fault or
timeout of the candidate); the basis is the local stratified readout over three seeds; LS-1 serves as
the harm check only.

Amendments (neither blocks):
1. **Flag the five bed-variant maps in the post-activation monitor** (Slithery, Schooltime, QoS,
   Dilemma, Devil — my 16:45Z probe) as separate rows beside Weakhold, so a Weakhold-specific gain is
   not read as field-wide improvement and any regression there gets seen early.
2. **Invalid-command deaths of 16979 as a monitor row, not a blocker**: the harm clause covers faults
   and timeouts (API-visible); local invalid deaths were 0 on all seeds, and if a live rise occurs it
   should be *seen* from downloaded replays even though it does not gate.

## 2. Replication (from the frozen cards, read-only)

- Per-seed Weakhold rows (REG-002-k16-gate-s23.md l.44 + seed-1 card): cand **15/16, 14/16, 14/16**
  vs parent **8/16, 10/16, 9/16** — net +7, +4, +5 per seed, 43/48 vs 27/48 pooled; seeds 2–3 stratum
  Δwin **+28.12 [+15.62, +40.62]**; pool without the stratum −0.59 [−1.56, +0.39] (inside the −2
  off-target margin); gen +0.22 [+0.00, +0.54]. Stratum econ −8.02 and wall deaths −19.3/1k — the
  mechanism (veto → fewer pocket entries) travels with the win, on every seed.
- Weakhold's beds are clean: it is not among the five oracle-diverging maps, so local Weakhold
  evidence transfers to server geometry (the panel's systematic bias does not touch this stratum).
- Rule-consistency: the local letter is HOLD, not FAIL, so D-055 §C's "if the local gate has finished
  and failed, no promotion" does not bite; the carve-out touches only D-057 §D's REJECT sentence, for
  the one case (mean ≤ 0 with interval covering 0) where a small-effect luck draw would block a
  three-seed replicated stratum gain. Pre-declared before LS-1's stop; the Chair's disclosure (10-pair
  figure only) is stated.

## 3. Numbers

- **P(LS-1 shows harm under this rule) = 0.10.** Faults: 80/204 games so far with none; a clearly
  negative paired mean at ~102–170 pairs against a true effect of ~+1 point overall requires a tail
  draw.
- **P(the promotion is a true net positive — live Weakhold gain ≥ +10 pp sustained) = 0.60.** For:
  three independent seeds, one map, same sign and magnitude; consistent veto exposure (90–98 per 1k
  queen decisions); our live Weakhold record is −0.329 over 62 ranked games — the second-worst map —
  and wall deaths are precisely its failure mode; rollback containment exists with Weakhold printed
  as its own row. Against: pool excluding Weakhold is slightly negative (−0.59), stratum economy
  costs 8 points, the zoo is not the ladder, and the field adapts. Expected if it transfers at even a
  third of local strength: ~+0.5–1 point of overall win rate on the ladder.
- For calibration: my 0.40 on the seeds 2–3 gate PASS scored Brier 0.16 (the letter was HOLD) — the
  stratum-replication half of my reasoning was right, the pooled-LB half was not.

## 4. Dissent

None on the rule. One flag: after activation, LS-std screens for later candidates should not treat
16985-era Weakhold cells as stable anchors — the incumbent's Weakhold distribution just moved; the
roster class rules (D-056 §D.3) already replace all-tie opponents, but Weakhold's changed baseline
affects every future screen's expectation model.

## 5. Precedent

Stratified promotion with an harm-only confirmatory check is the standard group-sequential
trial pattern (interim look for harm, final for efficacy) — here inverted by evidence order (efficacy
local, harm live). The pre-declared carve-out for interval-zero REJECTs mirrors non-inferiority
logic. The programme's own precedent is D-046 §4.6, written for exactly this shape.

*Nishinoya, 4 Oct 2026, ~21:55Z.*

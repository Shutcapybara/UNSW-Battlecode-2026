# P-2 review — Nishinoya (GLM, probe seat)

Card `P-hinata-02-R1-V0-logistic.md` (P-2, R1 V0b: Φ's symmetric logistic + two queen terms).
Council round 1, due 13:00Z. Seat: probe. All counts I produced are **unaudited** until Tanaka (or
another auditor) replicates them.

## 1. Verdict

**Agree with G-amend as the binding reading.** One amendment offered, non-decisive: keep the macro's
absolute floor (RL r50 AUC ≥ 0.66) as a **report-only** column on the confirmation card, so a
"V0b ≥ Φ but both < 0.66 on held-out RL maps" outcome stays visible instead of silently passing.

## 2. Replication (cheap parts re-derived; the fit itself not re-run)

- Recomputed both gates clause-by-clause from the card's development table:
  **G-amend passes** — min ΔAUC 90 % LB = −0.005 (elim r10) > −0.01; RL r150/250/400 LBs
  +0.023/+0.046/+0.089 > 0; worst slope deficit vs Φ = −0.03 (elim r10, ≥ −0.05); RL r50 0.671 ≥ 0.651.
  **G-asis fails** — point ΔAUC < 0 in 4 elimination cells (min −0.003) and slope outside [0.9, 1.1] at
  elim r10 (0.37) and RL r25/r50 (0.74/0.84). Both match the card's claims.
- Confirmed the Chair's fact from the table: Φ's own slopes fail the band at RL r25–r150
  (0.73/0.82/0.88/0.89). So G-asis's slope clause is unpassable by construction for any Φ-like model,
  independent of the data — it does not measure what R1 claims.
- Artifact check (main checkout): `build/hinata/v0/fit-lq/registry.json` records code_sha `3138d107`,
  held-out `['Autarky','Maze','Trauma']`; 12 cell files carry exactly 8 coefficients each (Φ's six
  shares + `q_alive_c` + `q_len_c`), matching the card's model description.
- **Not re-derived:** the fit, the bootstrap intervals, and the LOMO per-game scores — that is
  Tanaka's assigned replication and my slot has no cheap path that avoids duplicating a heavy job.

## 3. Why G-amend

1. A gate the baseline comparator itself fails (G-asis on slopes) converts R1 from "added information
   over Φ" into an absolute-calibration rung the macro never evidenced; Φ = 0.651 at r50 was the anchor.
2. G-amend is a standard non-inferiority-with-superiority design: no-worse everywhere (Δ LB > −0.01),
   better where the mechanism claims (late RL, LB > 0), calibration no worse than the comparator. That
   is exactly the claim structure of the card.
3. The post-hoc authorship of G-amend is survivable **because** the confirmation maps were never
   scored by any model (D-049 §1) and the artifact is frozen (no refit). The discovery/verdict split
   holds for this card.
4. Transfer is mechanically supported: every development number is already leave-one-map-out, so the
   RL gains are aggregated out-of-map predictions; Trauma is corridor/queen-decided (share 0.84,
   Chongqing C5-02/C7-03), where queen information should matter more than the training average, and
   Maze is long-open where Φ's late-game weakness was measured.

## 4. P(pass) — the confirmation on Autarky/Maze/Trauma, one shot, model as fitted

- **Under G-amend: 0.60.** Residual risks: (a) the RL r150 superiority clause is the tightest —
  development Δ +0.031, LB +0.023 on 3,387 games; held-out RL rows (Maze+Trauma, decoded by the
  deadline) will be fewer, widening intervals ~1.3–1.5×, LB ≈ +0.015–0.02 — positive but thin;
  (b) elimination regime rests on Autarky alone (my 10:44Z census: 874 in-scope post-m2 games total,
  per-cell n ≈ 150–600 at the late checkpoints), so a noise Δ LB < −0.01 in an elim cell where the
  card itself predicts ≈ 0 is a live failure mode; (c) decode completeness — at my 11:50Z census
  11,455/17,206 in-scope post-m2 decoded, queue 5,751 draining ~1.9k/h under the lead's writer, so the
  5 Oct 00:00Z backstop (D-047 §2) looks comfortable, not marginal.
- **Under G-asis: 0.03.** The slope clause from r25 fails structurally (development slopes 0.74/0.84
  at RL r25/r50; the model class has no mechanism to lift them into band on new maps).
- Expected effect if G-amend passes: RL ΔAUC ≈ +0.02 (r50) / +0.05 (r250) / +0.08–0.10 (r400);
  elimination ≈ 0 [−0.005, +0.005].

## 5. Dissent (stated plainly for the Chair)

1. **Class changes after reading results should cost more next time.** D-049 accepts the
   discovery/verdict split for P-2; I flag that any *future* model-class change on the same rows
   should force a fresh development fold set, or the discovery/verdict line erodes one rung at a time.
2. **Report the absolute floor.** If V0b ≥ Φ but < 0.66 on held-out RL r50, that belongs in the result
   card (see §1's amendment), not just the relative comparison.
3. **Elim-cell failure ≠ mechanism failure.** If G-amend fails only in an Autarky elimination cell on
   thin n, that should route to Tanaka's power assessment before being read as "queen terms don't
   transfer" — the elimination class carries no queen claim (C7-03: class A is where the queen does
   not decide).

## 6. Known precedent

Linear/logistic evaluation tuned on game outcomes is the classical Texel-tuning family (chess);
non-inferiority margin plus superiority on the claimed domain is standard two-arm trial design; the
centred no-intercept antisymmetric logit is the standard tiebreak-safe win-probability form. The
programme's own precedent is Φ itself; the nearest public analogue is Halite-family linear/GBT
win-model baselines.

*Nishinoya, 4 Oct 2026, ~11:55Z.*

---

## Addendum (4 Oct 12:45Z) — after Tanaka's P-2 review and the Chair's D-051 hold

1. **What my replication did not check.** My §2 verified held-out **map** exclusion (no
   Autarky/Maze/Trauma rows; artifact hashes). I did not check the D-046 §3 **series buckets**.
   Tanaka did: the 10:52Z fit trained on 539/5,799 games of the reserved test bucket (173/1,777 series)
   and 555/5,799 of validation (175/1,777), and within the LOMO folds 28,216/35,948 scored
   game-checkpoint rows shared a series with that fold's training set. My §3.3 sentence "the
   confirmation population … was never scored by any model" is therefore true only at map level, not at
   series level. The Chair's hold (D-051 §6) is correct.
2. **Verdict unchanged where it applies.** My G-amend recommendation was and is about the gate FORM
   (non-inferiority everywhere + superiority where the mechanism claims), which the leak does not
   change; G-asis remains structurally unpassable.
3. **P(pass) revised down.** My 0.60 under G-amend was conditioned on a clean frozen artifact and on
   LOMO-as-transfer evidence. With the leak, the development intervals are series-optimistic, so for a
   D-052-authorized confirmation on a prospectively defined clean population I revise to **0.50**
   (added failure mode: the late-RL Δ shrinks when series transfer is actually tested). Expected effect
   if it passes: unchanged in sign, wider bands (RL r250 +0.03–0.06, r400 +0.06–0.10).
4. For calibration scoring: the original 11:55Z P(pass) lines stand as filed for Brier scoring against
   whatever D-052 freezes; this addendum is context, not a refile.

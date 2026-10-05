# D-066 §C.4 / D-067 §G / P1-slot screen — Sugawara (council, mechanism), 5 Oct 2026 01:25–01:50Z

Three items: (1) the A8b precedent the Chair cited from memory (D-066 §C.4, assigned); (2) the check that Hinata's
inventory change is configuration only (D-067 §G, assigned now that the auditor seat is vacant); (3) a mechanism
reading of Asahi's two P1-slot screen FAILs (01:10Z), unassigned, with a replication from frozen battery files.

No LS-1 index, job file or outcome was read.

## 1. A8b — precedent check and replication

**Verdict: AGREE.** The precedent is real and closer than the Chair's wording. One wording correction.

- **AlphaGo (Silver et al., Nature 2016, Methods, "Symmetries").** The paper names two forms. In the *explicit
  symmetry ensemble*, all 8 dihedral transforms of a position go through the policy or value network in one batch.
  The policy planes are transformed back and averaged, and the values are averaged. In the *implicit symmetry
  ensemble*, used inside the asynchronous tree search, each evaluation uses one transform chosen at random. **A8b is
  the explicit ensemble restricted to the one symmetry our game has (left-right reflection of the egocentric
  frame).** Source quoted from memory of the Methods text: the search did not return a snippet I could quote from.
  Confidence high; still, check it against the paper before citing it in a D-record.
- **AlphaGo Zero (Silver et al., Nature 2017).** Leaf positions are evaluated under one random rotation or reflection,
  i.e. the implicit form, and the training data are augmented by the 8 symmetries. **Correction to D-066 §C.4:** "AlphaGo
  Zero evaluated each position under a random board symmetry" is right, but that is the *implicit* form, which
  averages only across the many visits of a search. The *averaged* form (A8b) is AlphaGo 2016's explicit ensemble.
  AlphaZero (arXiv 1712.01815) dropped both for chess and shogi because those games are not symmetric.
- **Test-time augmentation in vision.** Krizhevsky, Sutskever and Hinton (2012, AlexNet): at test time the softmax was
  averaged over ten patches, five crops and their horizontal reflections. A standard, sourced instance.
- **Where ours departs.** (a) The *teachers* are not reflection-symmetric: Hinata measured that only 0.891 of A1's
  argmax decisions survive the reflection. Averaging therefore biases the prediction towards a symmetric policy. It
  gains anyway (+0.0040), so the noise removed exceeds the asymmetry lost. (b) The engine has small asymmetries: the
  sonar cast order is N, E, S, W, and moves resolve in id order. Neither enters a single-step direction label. (c)
  The 7 value-mapped columns (map-position terms from get_map_size) must be reflected exactly in C++ too. That is a
  parity item for Kageyama, not a modelling issue.
- **Replication** from frozen files (staged `p_A1-400.npy`, `p_A8b-A1-400.npy`, `rows.parquet` sha a0b1ea2e…;
  188,250 F/R/L rows, 49 series; paired series bootstrap 1,000 × seed 7). **A8b-A1 − A1 = +0.00401 [+0.00294,
  +0.00521]** against Hinata's +0.0040 [+0.0029, +0.0053]. The point estimate matches exactly; the 95th percentile
  differs by 0.0001 (resampling detail). A1 − A0 = +0.02075 and A3 − A0 = +0.01681, both matching Tanaka and Hinata.
  A8b also improves the log-probability of the label: +0.0070 [+0.0059, +0.0084] nats a row.
- **Cost at play:** two evaluations of the same 400-round model for each decision; the zip size does not change.
  Kageyama states the points (today's maximum is 9.90 M a turn including turn 0).
- **Selection hazard (rec 11 restated):** A8b-A1-400 now leads the selectable arms by 0.0040 over its own base. The
  selector picks the maximum of 8 pooled entries, so the winner's curse applies. A8b and its base share every
  error except the reflection, so the selection-induced bias on the *difference* is small. The frozen-cohort
  confirmation is still the right check.

## 2. Inventory change (rev 7 → rev 8): configuration only for selection, PASS with one note

Diff of `tools/hinata/r2_battery.py` between hub commits e20eeab36 (rev 7) and d00f58c32 (rev 8, sha b5346f3c…,
matching the file on disk):

- POOLED_NAMES, DESCRIPTIVE, TS_PLANNED and MIN_COHORT_SERIES are read from `r2_inventory.json` (838de555…). The
  selection functions are unchanged. The output adds the inventory path and sha. **Selection logic is untouched:
  PASS.**
- **Note.** `cols()` changed: A6 and A7 now take the `ts_base` inputs (A1's HB-1 vector or A3's encoder) instead of
  ENC + HBP. That is a change to the *fitting* path, ordered by D-066 §C.3, so it is not a defect. It does mean that
  `r2_inventory_rev7_equiv.json` cannot reproduce rev 7's A6/A7 inputs: ts_base admits only A1 or A3, and rev 7 used
  ENC + HBP. The equivalence Hinata showed holds for selection on synthetic registries, which is what D-066 §C.5
  asks for. It does not hold for refitting A6/A7. Any rev-7 A6/A7 registry stays descriptive.
- The inventory lists A8b-A1-400 and A8b-A3-400 as pooled, and A4/A5 as descriptive, consistent with D-066 §C.1 and
  §C.4.

## 3. P1-slot screen FAIL (Asahi 01:10Z): what the prior gives the search

Replicated from Asahi's counts. Pool λ 1: 207/272 − 226/272 = −6.99 pp. λ 0.5: 194/272 − 226/272 = −11.76 pp. Gen
315/464 − 341/464 = −5.60 pp and 311/464 − 341/464 = −6.47 pp. The censuses (better / worse) give exact two-sided
sign tests of p = 0.040 (29/48) and p = 0.0007 (27/59). These sign tests are descriptive: the pairs are not
cluster-adjusted.

**Mechanism.** The slot adds λ·log p(first step) to a hand-tuned search score (policy.hpp l.1424–1444), with p
floored at 1e-4, so the floor is −9.21 at λ 1. Read on the same 188,250 dev rows (these are teacher states, not our
states; see the caveat below):

| prior on F/R/L | accuracy | mean log p(label) | entropy | rows with an option < 1e-4 | mean gap best − 2nd (nats, clipped) |
|---|---|---|---|---|---|
| A0 = the live HB-1 prior | 0.6977 | −0.748 | 0.425 | **0.389** | **3.14** |
| A3-400 (the placeholder's arm) | 0.7145 | −0.606 | 0.605 | 0.089 | 2.15 |
| A1-400 | 0.7184 | −0.602 | 0.585 | 0.018 | 2.23 |
| A8b-A1-400 | 0.7224 | −0.595 | 0.593 | 0.010 | 2.20 |

The live prior is less accurate and worse calibrated, but much sharper. On 39 % of rows it sets at least one option
to the floor, which acts as a near-veto worth 9.2 points of search score. The cloned priors are softer: they have a
~30 % smaller gap between the best and second-best option, and the floor is reached on a quarter of the rows or
fewer. **Halving λ made play worse (−11.8 vs −7.0 pp).** That is the direction expected if the search's other terms
were tuned (hb1-12) against a prior of HB-1's strength, and a weaker prior lets moves through that the search
alone mis-scores. It is not the direction expected if the new prior pointed the search at bad moves. Devil, the worst
map in play (−68.8 pp), shows the same pattern: there A3 is *more* accurate than A0 (0.786 vs 0.778), its entropy is
0.418 against 0.261, and its mean log p of the label is −0.430 against −0.595.

**Reading (not proven):** the selection metric (argmax accuracy on teacher moves) is not the quantity the search
consumes (λ·log p as a score term against hand-tuned weights). Precedent: AlphaGo 2016 found that its stronger
RL policy was a *worse* tree-search prior than the SL policy. Their explanation was diversity of the prior, so the
direction there is the opposite of ours, but the lesson is the same: standalone policy strength does not
transfer to prior quality inside search. **Caveats:** these are teacher states, not ours (states seen in our own
games are a different distribution); and a slot defect is not excluded. The `catch (...)` around `slot.observe` in
main.cpp l.44 is silent, so a throw leaves p1_p null and the turn runs with **no prior at all** (hb_logp all 0).
On a map where observe throws, that is λ = 0.

**Recommendation 19 (before any selected model is screened in the slot):**

1. Make the observe fallback countable: add `LOG p1_fallback` in the catch, and count it per map on a seed-1 pool
   rerun of λ 1. This is free and settles the defect question. Do this together with the ≥ 3-map e2e parity
   (rec 18), with Devil and Dilemma first.
2. A pre-declared **strength-matched λ**: choose λ* on dev rows so that the mean λ·(best − 2nd) log-gap equals
   A0's at λ 1. That gives about 1.46 for A3-400, 1.41 for A1-400 and 1.43 for A8b-A1. Screen λ* as the slot's one
   variant, not a dose sweep.
3. A **λ = 0 control** at seed 1 (pool only) on the same binary, to price the prior. If λ 0 ≈ the placeholder at λ 1,
   the clone currently adds nothing to search. If λ 0 is far below, prior strength is what matters, and λ* should
   recover much of the loss.
4. Report log-loss, entropy and floor share beside accuracy in the battery table (descriptive; the selection rule
   is unchanged unless the Chair rules otherwise).

P(λ* placeholder screen not worse than carthage-05 by more than 2 pp on pool, seed 1) = **0.35**.
P(p1_fallback count > 1 % of turns on some map) = **0.15**.
P(λ = 0 pool Δwin ≤ −7 pp, i.e. at or below the λ 1 placeholder) = **0.55**.

RL translation: the prior is a fixed-temperature policy term inside a hand-written value. Any learned policy that
enters the search this way needs its temperature fitted *in play*. That is one scalar, so a three-dose panel or a
small CMA-ES run is enough. Offline accuracy cannot fit it. This binds P-7's network if it ever feeds the search
rather than replacing it.

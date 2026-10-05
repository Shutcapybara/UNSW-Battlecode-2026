# P-7 review — Nishinoya (GLM, probe seat)

Card `P-sugawara-03-selfplay-finetune-scoping.md` (P-7, scoping: KL-anchored PPO self-play fine-tune
of the cloned network). Due 22:00Z per D-061 §C. Unaudited until Tanaka replicates.

## 1. Verdict

**Agree, as a scoping card, with four amendments** (one of which promotes the author's own dissent
into the plan).

1. **Step 0 = the filtered self-imitation probe, required, not dissent.** Same wrapper, no critic,
   one night. If outcome-filtered re-cloning moves head-to-head < +0.02, PPO at 2–3 orders less
   compute than precedent is unlikely to do better — the author wrote this; I would make it the
   card's first falsifier. The cost asymmetry (one night vs 1–2 engineering days + 15 Mac-hours)
   is the whole argument.
2. **E2 lands before the PPO learner engineering starts**, not merely before training. The card's
   entry list implies it; make it explicit — if in-loop throughput misses 1×10⁷/h, the learner
   engineering is sunk cost. Asahi's measurement (D-061 §C) is already ordered.
3. **Reconcile the engine arithmetic before E2 is read.** The card says "raw engine ≈ 80
   µs/decision/core" but also reports the measured 28.63 M callback decisions/h at 3.05 average
   cores ≈ 2.6k decisions/s/core ≈ 383 µs/decision/core including orchestration — a ~4.8× gap.
   State which constant enters the 1–3×10⁷/h projection; the projection's honesty depends on it.
4. **Death-mix visibility from iteration 1.** Invalid-command and self-harm columns are part of the
   stop rule (double → stop); they must be printed per iteration, not only at the falsifier read —
   P-4's refutation showed the readout columns are where eligibility dies.

## 2. Replication

- **A10 inference cost, re-measured on this Mac** (numpy fp32, exact A10 shape, single core,
  nice 15): **0.076 ms/forward at batch 1 = 13.1k decisions/s/core; 32.7k/s at batch 8; 44.9k/s at
  batch 64; 36.3k/s at batch 256.** The card's 0.059 ms/17k at batch 1 and 25–29k at batch 8–256
  are reproduced or better — the claim is conservative on this machine. Inference is not the E2
  risk; orchestration is (amendment 3).
- **Toad Brigade write-up fetched in full** (see my BOARD correction): "starting from a random
  initialization" with reward shaping for 20 M steps and a **frozen self-teacher KL ladder**
  (8-block → 16 → 24), "I had a frozen teacher model perform inference on all states, and added a
  KL loss term … helped to stabilize behavior and prevent strategic cycles". Two consequences:
  my earlier "the Lux winner bootstrapped by imitation" was WRONG (withdrawn; D-061 §A's strike is
  correct), and P-7's KL-to-clone anchor gains a direct, quotable precedent at personal-PC scale
  (8-core/16-thread dual-GPU — compute close to ours, modulo the two GPUs).
- Not re-derived: the antioch 28.63 M/h engine measurement, the microRTS and AlphaStar rows
  (Sugawara's source file is the assigned verification of those).

## 3. P(pass) — the author's four events

- **E2 (A10 in-loop ≥ 1×10⁷ decisions/h on ≤ 8 Mac cores): 0.50** (author 0.60). Inference is
  confirmed cheap here; the risk is the orchestration constant of amendment 3 — if the effective
  engine cost is nearer 383 µs than 80 µs per decision-core, 8 cores clear 1×10⁷/h only with
  near-perfect batching.
- **Head-to-head ≥ 0.55 vs the frozen clone after 6 iterations: 0.50** (author 0.45). The KL anchor
  stabilises; head-to-head on training maps is the most overfit-friendly metric in the plan; but
  1.2×10⁸ decisions is thin for PPO.
- **Seed-1 panel Δwin ≥ +0.02 vs the clone: 0.20** (author 0.25). League overfit transfers weakly;
  P-4 just demonstrated how fast eligibility dies at readout.
- **A later LS-std-1 live promotion from this line within the season: 0.10** (author 0.15).
  Promotion-grade evidence is a high bar (cluster sign test at p ≤ 0.075) against live noise.
- Expected effect if it works: agree with the card (+0.02–0.05 panel win per two-night budget,
  falling per iteration).

## 4. Dissent (plainly)

1. To the Chair: the self-imitation probe (amendment 1) should be a required step, not an author's
   footnote — it is the cheapest possible read on "does outcome signal help at our sample sizes".
2. If the battery selects trees and P-7 voids, the outcome-signal question does not die with it:
   ExIt/R6 should inherit the same step-0 probe so the ladder does not drop the thread for another
   rung cycle.

## 5. Known precedent

AlphaStar (supervised clone → league RL with KL to the supervised policy — the exact recipe shape);
microRTS 2023 (cloning then DRL fine-tune as an efficient start); and, from this review's fetch,
Toad Brigade (frozen-teacher KL at personal-PC compute, from random init with shaped reward — the
anchor mechanism, though not the clone start). No precedent at our compute for 20–40 decentralised
agents under 7×7 partial observation — that part rests on evidence, as the card says.

*Nishinoya, 4 Oct 2026, ~21:05Z.*

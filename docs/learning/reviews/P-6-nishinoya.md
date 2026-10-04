# P-6 review — Nishinoya (GLM, probe seat)

Card `P-hinata-04-R1b-V-legal.md` (P-6, R1b: value model on the legal encoder; prices opponent
information for R5). Council round 2, due 17:00Z. Unaudited until Tanaka replicates.

## 1. Verdict

**Agree, with two amendments** (one interpretive, one reporting).

**Amendment 1 — decompose what ΔAUC(V0b − V-legal) measures.** The card reads the gap as "the value
of opponent (and whole-team) information" and says it "prices what a learned sonar/relay block (R4)
could recover". With a 16-scalar feature set the measured gap is
`privileged − full-legal-view` PLUS `full-legal-view − 16-legal-scalars`: an **upper bound** on what
sonar/relay could recover, and a **lower bound** on the total information gap to V0b. Write the
decomposition into §1/§2 so a large gap is not over-read as recoverable (the tightener — V on the full
encoder vector — is R7-shaped capacity and is not this card).

**Amendment 2 — era-anchor the held-out read.** The proposed post-claim-time population (ranked
post-m2 Autarky/Maze/Trauma games started after P-2's claim) is the right one-look discipline, but it
is a different era from P-2's confirmation rows: the field is moving (second tier +10 pp queen
survival in two days; Chongqing C8-01), so V-legal's held-out ΔAUC will not be directly comparable to
P-2's confirmation numbers. Print Φ on the same new rows as the anchor (Φ's shares are privileged, so
Φ-vs-V-legal on identical rows is the legal-information gap under the same era), and label the era.

## 2. Replication (cheap parts)

- Consistency of the design against D-052 §A: V0b's OOF predictions are the frozen 35,948 side-A rows
  (not refitted) — the card §4 matches; folds are P-2's LOMO unchanged, which is the correct reading
  of the D-052 §A.6 fresh-fold rule (that rule binds on a change of model class; logistic → logistic
  with intercept + z-scoring is a form change forced by losing antisymmetry, not a class change — I
  agree with the card's reading, and the intercept/z-score change is itself worth one sentence in the
  registry entry).
- Feature legality spot-check: all 16 named scalars are own-process observables in encoder v1
  (length, unit_count, headroom, deltas from sonar/echo counts, own/enemy queen visibility with age)
  — no absolute position, no map identity, no opponent-truth channel. Consistent with the R0
  constraints.
- Not re-derived: the ≈0.5 M encoder-row cost estimate (needs the per-game block rebuild; Data's
  estimate governs).

## 3. P(pass) — by the card's own events

- Falsifier NOT triggered (ΔAUC 5th percentile > 0 on ≥ 3 of 6 round-limit cells from r25):
  **0.80** (card 0.85 — close; V0b reads global pearl/territory/death shares that no legal scalar
  carries, so the gap at r150–r400 is nearly certain; the early cells are where my 0.05 sits).
- V-legal AUC ≥ Φ at round-limit r50 on the same folds: **0.20** (card 0.25). Φ is itself
  privileged-truth; the legal 16 scalars must beat six global shares using one process's local view —
  the queen/enemy-visibility features are real information Φ lacks, but r50 outcomes are mostly
  driven by economy V-legal cannot see. Slightly below the author.
- Expected effect (my prior, matching the card's direction): ΔAUC(V0b − V-legal) RL r50 ≈ +0.05–0.08,
  r400 ≈ +0.07–0.10; elimination +0.02–0.05; pooled-view variant closes ~25–40 % of the gap.

## 4. Dissent (plainly)

None material. One note: the "pooled-view variant" (mean logit over all alive processes) is the most
decision-relevant number in the card for R4's sonar-relay design — it upper-bounds what TODAY's
broadcast channel could carry if perfectly pooled. I would print it per cell with the same bootstrap,
not only as a summary.

## 5. Known precedent

Privileged-critic vs deployable-actor information asymmetry is the standard asymmetric
actor-critic / centralised-training-decentralised-execution pattern (MAPPO's CTDE critic; Sukhbaatar
& Fergusson 2016 privileged baselines). Measuring the gap by holding the learner fixed and swapping
the input information set is the clean form of the experiment. No invented method here.

*Nishinoya, 4 Oct 2026, ~15:55Z.*

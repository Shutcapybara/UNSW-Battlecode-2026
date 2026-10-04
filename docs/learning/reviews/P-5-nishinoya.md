# P-5 review — Nishinoya (GLM, probe seat)

Card `P-hinata-03-R2-P1-bc-direction.md` (P-5, R2: BC direction head as carthage-05's prior).
Council round 2, due 17:00Z. Unaudited until Tanaka replicates.

## 1. Verdict

**Amend.** The card's structure is right (one switch, exact parent, series-grouped folds, LOMO,
learning curve, two pre-registered gate forms, honest cost), and G-parent is the correct binding form
— a paired comparison against the parent's prior on the same rows measures the switch; the fixed 0.83
bar measured HB-1 on its own team's games and mostly measures the population when ten teachers are
pooled. The amendment is the feature set, and it is the same issue the Chair flagged in D-054 §D:

**Train the R2 attempt on encoder v1 + hb1's per-candidate direction scores (+ the queen block), not
encoder v1 alone.** Keep encoder-v1-only as an ablation column printed beside it.

Why: (a) the macro's R2 row says "hb1's features plus the queen block" — the card follows D-053 §F's
"encoder v1" instead, and D-054 §D already leans back to the macro; (b) the features are deployable —
hb1-14 shipped them inside this same chassis, so there is no legality or budget obstacle; (c) HB-1's
measured steepness (0.73 → 7.5 % win, 0.854 → 55 %) was achieved WITH those features; the card's own
expectation (0.79 dev accuracy vs HB-1's 0.829+) concedes the weaker set; (d) the ladder rule is "a
failed rung is diagnosed, not skipped" — a first attempt on the knowingly weaker variant risks burning
the rung and buying a diagnosis we can already write (R2b exists as the card's own remedy). If the
amended feature set still misses the falsifier, the ablation column tells us whether information or
features were the constraint.

If the Chair keeps the card as written (encoder v1 only), it should be with eyes open that this is the
R2b-shaped attempt first; my numbers below cover both.

## 2. Replication (cheap parts)

- Verified the parent-prior hook exists as described: `policy.hpp` direction term
  `hb1_dir_lambda × log p(first step)`, λ = 1.0 in the parent (card §1) — the switch site is real and
  single. (Read-only code check on main.)
- Cross-checked the teacher exposure arithmetic: teacher list v1 = 1,925 sides over 1,735 ranked
  post-m2 games on 14 training maps ≈ matches the store's per-map ranked volumes (my 4 Oct censuses:
  487–615 ranked in-scope games per map, top-ten involvement ~110–160 per map — 1,735 games is a
  plausible top-ten-ranked subset of that).
- Not re-derived: the 0.551 majority-class smoke number and the 6,500 dragon-turns/side row estimate
  (needs the teacher rows built; Data owns them).

## 3. P(pass) — by the card's own events

- Development falsifier NOT triggered (series-grouped dev accuracy ≥ 0.75): **0.65** as written
  (encoder v1 alone; the bar is low vs majority 0.55, but ten-teacher label disagreement drags pooled
  accuracy down); **0.80** with the amended feature set.
- G-parent passes (paired vs parent prior, whole-series 5th percentile > 0, on the held-out maps,
  conditional on the dev fit running): **0.40** as written, **0.55** amended. The drift argument is
  strong — the parent's prior was cloned from ONE team on 29 Sep pre-m2; P1 is cloned from the current
  top ten on post-m2 games and conditions on the queen block. The residual risk is λ-scale mismatch
  (below).
- G-macro (fixed 0.83): **0.15** as written, **0.30** amended — irreducible teacher disagreement caps
  pooled accuracy regardless of features.
- Panel gate at λ = 1 given an offline pass: **0.25** — agree with the author; a prior is one term of
  many, and λ = 1 was tuned for HB-1's log-p distribution, not a LightGBM 4-class softmax's. The
  λ ∈ {0.5, 1, 2} dial at panel stage is the right mitigation and I would screen λ = 0.5 and 1, not
  1 alone.

## 4. Dissent (plainly)

1. To the card: the λ = 1 first screen is a scale gamble — the dial exists in §4, use it at the
   screen, not only at the gate.
2. To the Chair (if the card stays as written): record explicitly that R2 is being attempted on the
   weaker feature variant, so a fail routes to R2b without re-litigating whether the rung was tried.

## 5. Known precedent

BC from top replays with a per-candidate score head is the Lux S1 UNet-lineage pattern; a cloned
prior inside a tuned search is exactly the hb1-14 precedent this programme already shipped. Pooled
multi-teacher BC with style heterogeneity is standard mixture-imitation; per-teacher reporting (the
card promises it) is the right diagnostic.

*Nishinoya, 4 Oct 2026, ~15:55Z.*

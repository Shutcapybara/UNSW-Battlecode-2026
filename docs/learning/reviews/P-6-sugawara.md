# P-6 (P-hinata-04, R1b V-legal) — Sugawara, council round 2 addendum

2026-10-04 16:28Z. My review is `P-hinata-04-sugawara.md` (15:29Z, AGREE + 2 amendments). This addendum responds to
Nishinoya (BOARD 15:58Z) and Tanaka (`P-6-tanaka.md`, 1582bb308). **Verdict: AGREE with amendments** (now four).

- **Accept Nishinoya (1) and Tanaka's wording:** ΔAUC(V0b − V-legal) is a paired predictive diagnostic, not an
  identified information price or a guaranteed upper bound (feature sets, model geometry and speaker selection all
  differ). Card text should say so; R4/R5 headroom must not be read off it.
- **Accept Nishinoya (2):** print Φ on the same post-claim rows (era anchor).
- **Accept Tanaka:** the post-claim read needs whole-series disjointness, not a game-time cutoff alone (same defect as
  P-5 §2). A lower bound ≤ 0 is non-significance, not equivalence.
- My amendment (2) (queen-speaker-only ΔAUC) is strengthened by Tanaka's point that under queen-else-lowest-alive
  selection is_queen = 0 implies queen death in this dataset; restrict R5 claims to queen-speaker rows.
- Timer-free scalars: the oracle-provenance filter of P-5 §3 does not apply, but report the rebuild_redacted share
  per cell anyway (dev120: 17.2 % of rows, concentrated on four maps).

Forecasts unchanged except the falsifier: P(not triggered) **0.80** (was 0.85; series-clean cohort is smaller);
P(V-legal ≥ Φ at rl r50) 0.20. Not replicated: no new fit, and I did not read held-out labels.

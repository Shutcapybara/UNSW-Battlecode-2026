---
id: 2026-09-28-analysis-rating-min-evidence
author: glm/analysis/a1
kind: correction
title: "The campaign rating table cannot order the queue: n=2 rows outrank n=100+ rows; minimum-evidence rule and shrinkage patch proposed"
task: "A1 §3.10 — rating-table sanity"
supersedes: []
evidence: "experiment_data/bot-ratings/latest.json (2026-09-28T12:22 UTC, 299 bots, 108,527 fixtures); live shares from A1 loss anatomy (verified controlled field games). Cross-check of the director's two probes: tidus-t02-spread-only local 77.6% (110 fixtures) vs live share 0.34 (n=29); fenrir-v18-arrival-ready-beds local 78.9% (85 fixtures) vs live 0.43 for the same code as incumbent 9508 (n=123)."
---

# The failure

Today's table sorts by raw model score, and model scores for nearly-unplayed bots regress to a high prior: **8 of the top 26 rows have 2 fixtures vs 1 opponent on 1 map** (e.g. yuna-x43-local-crown-donor 78.6% at rank 4 on n=2; jet-v04 77.4% on n=2 at rank 9), placing them above bots with 70–122 fixtures. The entire top-26 is flagged Sparse. The two director probes confirm direction: local 77–79% vs live 34–43% — a gap of 34–45 pp, in the same direction for every mapped source (see the calibration finding: local minus live = +8 to +38 pp across five sources).

Caveat stated: local and live scores are against different opponent sets, so the gap is not a pure bias estimate — but it bounds how far the table's absolute numbers sit from live reality, and the ordering failure (n=2 above n=100) needs no calibration at all.

# The rule (implemented + patch)

`tools/analysis/rating_evidence.py` + patch `tools/analysis/patches/benchmark_ratings_min_evidence.patch` (applies to `tools/benchmark_ratings.py`, verified against today's latest.json):

- **Queue-eligible** = ≥60 fixtures AND ≥5 opponents AND ≥8 maps (mirrors the dashboard's Sparse definition, minus its map-weight clause).
- **Queue score** = raw score shrunk toward the established-panel mean with weight n/(n+60).
- Table sorts by (eligible, queue score); Sparse rows render display-only.

Effect on today's table: all n=2 rows drop from the top-10 to ranks ≥220; the top-12 becomes all-established (ein-dog-x04 72.8%, tidus-t02 72.5%, fenrir-v18 72.4%, …). Ordering among established rows barely changes — the fix removes phantom rows, it does not reshuffle real ones.

**Decision fed**: the campaign table may order the queue ONLY over queue-eligible rows, and only as a prior — absolute scores stay untrusted until the calibration expectation model has ≥5 sources (currently band-mean 0.372). Apply the patch (director's call — the analyst commit path excludes tools/ root by the rules of engagement).

**Falsifier**: after deployment, an n<60 row that reaches queue-eligibility-equivalent live share within 10 pp of its raw score (would mean sparse extrapolation is actually accurate); or any established row whose live share exceeds its queue score by >15 pp on n≥30 live games (the shrinkage is too weak).

# D-052 §B rollback rule — operating characteristics

Source: submission 14585, ranked, 849 games / 172 series with an expectation, anchor Elo 1694 (our rating at its first ranked game, 2026-10-02 04:23Z); mean residual +0.029, centred to 0. Sims per cell 4000; inner bootstrap 1000; rng seed 7.

## 1. Simulation (i.i.d. whole series)

| true new − old | P(rollback) | mean games in new window | mean games in reference |
|---|---|---|---|
| +0.00 | 0.073 (±0.008) | 40.6 | 121.3 |
| -0.05 | 0.200 (±0.012) | 40.6 | 121.3 |
| -0.08 | 0.291 (±0.014) | 40.6 | 121.3 |
| -0.10 | 0.366 (±0.015) | 40.5 | 121.3 |
| -0.15 | 0.576 (±0.015) | 40.6 | 121.3 |
| -0.20 | 0.781 (±0.013) | 40.6 | 121.3 |

## 2. Placebo looks on real sequential data (same submission both sides)

Looks: 138 (one per series boundary with >= 120 games before and >= 40 after; heavily overlapping, so not independent). Rule fired: **9 / 138 = 0.065**. Difference quantiles 5/50/95 %: -0.122 / -0.010 / +0.244.

## 3. The real transition in the window

14265 (last 123 ranked games / 26 series with an expectation) -> 14585 (first 40 / 10): difference -0.019, 95th pct +0.126 -> **keep** (anchor 1694).

Corpus: `public_replays/corpus/index.jsonl` sha256 8eff46354945… at 2026-10-04 13:53Z (the collector appends, so a few games newer than `live-inputs/20261004T1353Z-6578d155.json.gz`, index 9f0a8de27ab2). Rule: D-052 §B. This report is not a gate.

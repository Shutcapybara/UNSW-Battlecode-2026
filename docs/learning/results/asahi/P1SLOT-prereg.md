# P1-SLOT seed-1 screens: preregistration (Asahi, written 2026-10-05 00:15Z, before any on-arm game)

Arms (Kageyama, r/kageyama f536785f7, D-065 §D), parent `carthage-05-free-sprint` (fp 7df05a3f, seed-1 runs on file):
- `kageyama-01-p1-slot` — direction prior from the PLACEHOLDER tree model A3-400 fold f0 on encoder v1, λ = 1.0.
- `kageyama-01-p1-slot-l05` — identical, λ = 0.5.
- `asahi-10-p1slot-off` — the switch off (+ carthage-05's two HB-1 headers): golden-parity build.

Order: off-build pool s1 parity first (expected 272/272 identical games; any difference stops the on-arm reading until
explained). Then pool s1 and gen s1 for both on-arms; CPU/zip probe on λ 1; census table (better / worse / tied per map).

Objective: screen the deploy path, not select a model (the model is a placeholder, not selected). Cards are
`screen-` letters under card.py's frozen conventions (map × opp clusters, 1,000 × seed 7, linear 5–95 %).
Expected sign: pool Δwin ≥ 0 (A3-400 dev accuracy 0.7145 vs the live prior's 0.6977, D-065 §C), small; my forecast
pool Δwin +1 pp, P(Δwin > 0) = 0.55 for λ 1, 0.55 for λ 0.5. Side effects reported: economy, units/total, tier-2
deaths, per class and map, runtime errors (any error = FAIL of the deploy check).
Stop rule: one seed-1 screen per arm; no re-runs for a better draw; seeds 2–3 only if the Chair orders a gate.

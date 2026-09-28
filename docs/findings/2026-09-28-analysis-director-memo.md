# Director memo: A1 statistics decisions

**Evidence snapshot:** 2026-09-28 workspace state; all live counts below use verified, controlled, field-pool A-side games only. Current eligible n=265 across sources 9508, 9663, 8540, 9639 and 9980, against opponent submissions 9343/9433/6350/6985. Units are games unless stated. Stage values are medians. Repeated games in a block are not independent randomized samples.

## Five findings that should shape the next work

1. **Investigate early production and survival first.** 9508 has 28 elimination losses among 51 compact-map games; its compact/open median units at r100 are 6/13. Across 9508's 70 losses, 43 end by elimination, median elimination round 169. Falsifier: a matched seeded production/survival panel fails to improve unit count or elimination outcomes while a late-conversion intervention improves terminal outcomes.
2. **Do not infer a live-wide runtime budget from source maxima.** 9508 (n=123) reached 100M game max; 9663 (n=50) reached 97.46M; three sources n=29–32 peaked 77.39–79.72M. Falsifier: probe-level per-turn data shows the peaks are record artifacts or remain within verified safe headroom under peak-load conditions.
3. **Treat layout as a blocking design stratum.** Map hash/seed/request metadata is recorded, but the assignment rule is unresolved. Falsifier: repeated same-map/same-seed observations and an alternating-request experiment establish deterministic assignment.
4. **Exact matched contrasts are needed before retiring mechanisms.** The prior summary's screen-block samples have not been reconstructed into exact map/side/opponent-submission/layout pairs here. Hub cycle functions now report paired effects by those exact cells. Falsifier: no exact common cells exist; then the proposed historical comparison cannot answer the mechanism question.
5. **Keep local ratings out of truth-label decisions for now.** This runtime could not read the parquet ledger (PyArrow unavailable), and hub-state's calibration export contains zero rows. Falsifier: re-derived, version-stratified paired transfer reaches ≥70% sign agreement on at least 10 independent pairs.

## Three lineage claims not reproduced

- The public-replay “exact before 13:00 UTC / ~92% after” replay-drive fidelity claim; requires replay-drive reproduction and message/input comparison.
- The ladder-band ranks and team behavioral-cluster recommendation; no version-stratified fresh band corpus was analyzed.
- The ranked-exposure Elo impact/K-factor claim; this pass did not access the legacy series-detail cache or independently map upload timestamps to inherited counts.

**Next authorization:** No upload or API-key action was taken. Complete the S1 panels, recover teammate archives, and run the layout experiment before selecting a new mechanism or recalibrating the local queue.

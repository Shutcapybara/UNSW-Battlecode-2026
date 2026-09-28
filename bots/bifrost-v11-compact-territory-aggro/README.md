# Bifröst v11 — compact-map territory aggro

This experiment keeps Bifröst v01's portal, split, bed and threat policies. It enables the existing allied-minus-enemy density-gradient push only on maps with at most 625 cells, after the team reaches 15% of its unit limit and before round 200. The change tests whether Bifröst should contest opponent-held space on Devil, Prisoner's Dilemma and Trophy; those maps contain four of the five losses in the focused V01 control.

See the [family notes](../../docs/bifrost-family.md) and the matched control report (`../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md`).


## Test result

Rejected after a 60-game focused screen: 36 wins and 24 losses, with no errors or runtime faults. It lost 3–9 to Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v11 scored 33–15; v11 gained two results and regressed on 12. Its two gains were one Devil fixture against Godel and one Trophy fixture against Gavroche; it lost both Hydra Dilemma games. See the candidate report (`../../experiment_data/bifrost-v11-compact-territory-aggro_20260927124937481171/summary.md`) and matched V01 control (`../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md`).

# Kenma 07 — keeper moves with parent splits

Parent: kenma-04-keeper-action. The only runtime change is in kenma_action.hpp: preserve every parent SPLIT decision, and use only the four movement probabilities from the existing queen action model when the parent selected MOVE. Model, timing (from round zero), legality mask, matching safe free sprints, pocket rescue and all nonqueen behavior are unchanged. No retraining or new parameter fitted.

Hypothesis: Kenma 04 scored 50–52 versus Carthage despite improved queen survival in retained Weakhold replays. The learned controller's rare split actions may suppress opening expansion. This variant separates movement imitation from split control without adding a time cutoff.

Status: prepared, unmeasured. Full 102-game Carthage screen required before calling an improvement. Exact-source deploy checks and Kageyama/pool checks required if this becomes best. Reserved seeds 11–13/new maps untouched.

Completed Carthage screen: **51–51/102**, all 17 ranked maps, both seats, seeds 1–3; zero errors. Rejected versus Kenma 03 (58–44). Exact fixture results and map breakdown: main build/kenma/k07-v-carthage-s123/score.json. No reserved validation used.

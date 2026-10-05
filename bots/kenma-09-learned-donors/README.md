# Kenma 09 — learned nonqueen donors

Parent: kenma-08-lossless-direction (Kenma 03 strategy with exact smaller direction storage). Adds a binary LightGBM clone of teacher 306's invalid-command donor actions. Original queens are excluded; eligibility is length <= 8, at least two team units and a visible allied head. Probability >= 0.9 emits SPLIT 1 to deliberately die and leave food. Existing sealed-pocket donors run first; all other parent decisions are preserved.

Training: 208,158 eligible oracle turns, 4,311 culls, original train split only, held-out maps excluded. Fixed 160 rounds, 31 leaves, no class reweighting. Development validation holds out 12 series (46,316 rows) from 48 training series: at the preselected 0.9 threshold, 653 TP, 2 FP, 231 FN, 45,430 TN (precision 99.69%, recall 73.87%). These numbers do not establish playing strength or calibration on this bot's own states. Final model refits the fixed settings on all eligible rows.

Model SHA-256: 484c315dc5030ae74b7ea99ed9b77c20fb19cdbd0a475daeeff15d28d6ff0b60. Uses only the same 270 legal HB-1 inputs; no map identity. Reproduce with tools/kenma/feeder_train.py and prepare_feeder.py, output main build/kenma/feeder-v1/. Binary inference applies sigmoid to the raw margin, not the generic multiclass softmax.

Export verification: 20000 native rows, all threshold decisions equal, maximum probability error 3.2361124890911697e-08. Status: unmeasured, not best. Full native comparison and exact-source sandbox checks required. Seeds 11–13/new maps remain reserved.

Mechanism caveat: all 299 high-confidence donor predictions in the 20,000-row export sample have n_exit_any = 0 (295 also have free_dirs = 0; 3 are split-eligible). Nominal exit features do not fully model tail movement, so this is not proof of identical actions, but high imitation accuracy may largely reflect terminal traps. The full screen must establish useful changes in play; do not promote from classifier accuracy. Evidence main build/kenma/feeder-v1/activation-census.json.

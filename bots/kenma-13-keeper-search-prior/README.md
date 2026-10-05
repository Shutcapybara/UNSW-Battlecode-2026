# Kenma 13 — keeper model inside movement search

Parent: kenma-08-lossless-direction (strategy equivalent to 03). For original queens only, replace the Heartbreaker first-step log prior with the existing Kenma 04 keeper model's four movement probabilities, conditioned on movement and mapped F/R/B/L to absolute directions. Keep the parent's prior weight 1.0. All search terms, candidate paths, splits, sealed-pocket rescue, population reserve and nonqueen behavior remain parent code. No direct action override, orbit, retraining, map identity or tuned cutoff.

Motivation: direct keeper action variants 04/05/07 improved some queen survival but scored below 03. This tests whether their direction information helps when evaluated alongside parent room, threat, growth and sprint scoring. The model's existing export parity is already verified; this variant changes only integration. Seven-class split mass is removed by normalizing the four movement probabilities, so it cannot distort move-versus-split scores simply because the teacher preferred to split.

Status: completed **54–48/102**, zero errors; rejected against03 at58–44. Reserved seeds11–13 and new maps untouched. Output main build/kenma/k13-v-carthage-s123/.

Full-executable observation-stream check: all163 recorded queen turns parse and return actions;87 differ from recorded12, so the new prior has real influence. These counterfactual choices are not playing-strength evidence. Output main build/kenma/orbit-audit/candidate-counterfactual-actions.json.

| Map | Wins | Losses |
|---|---:|---:|
| live/schooltime | 6 | 0 |
| live/portals | 4 | 2 |
| live/slithery_fight | 2 | 4 |
| live/queen_of_spades | 3 | 3 |
| live/default | 1 | 5 |
| live/trophy | 3 | 3 |
| live/dilemma | 2 | 4 |
| live/autarky | 2 | 4 |
| live/devil | 5 | 1 |
| live/trauma | 3 | 3 |
| live/australia | 3 | 3 |
| live/islands | 2 | 4 |
| live/unsw | 3 | 3 |
| live/maze | 3 | 3 |
| live/weakhold | 6 | 0 |
| live/stripes | 5 | 1 |
| live/tower_defense | 1 | 5 |

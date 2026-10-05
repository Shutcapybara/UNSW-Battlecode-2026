# Kenma 04 — keeper action clone

Parent: kenma-03-pocket-queen, exact pocket behavior and one reserved slot retained. Outside sealed pockets, original queens use a seven-class action model: F/R/B/L, split two, retain two, split half. Immediately lethal single steps are masked; the parent supplies a safe free sprint when its first step agrees. Other dragons use the parent unchanged.

Training: 26,820 oracle queen turns from keeper teams 91, 213, 507, 842, 55, training split only, no map-identity inputs. The same 270 HB-1 inputs are bound in the verified parent order. A fixed 128-round, 15-leaf LightGBM model scored 81.75% action accuracy on 7,223 rows from 17 held-out development series (majority 32.71%), then refit on all 26,820 rows. This is offline imitation evidence, not play strength.

Model SHA-256: e8bb884fe8e798ddd475be7ba841e901f302bfe1e9d0fabdadd039f2da61c99d. Reproduce with tools/kenma/queen_train.py and prepare_queen.py; output main build/kenma/queen-action-v1/.

Status: rejected as an improvement. Full Carthage panel: **50–52**, no draws or runtime errors, 17 live ranked maps × both seats × seeds 1–3. Kenma 03 remains best at 58–44. No sandbox checks spent on this weaker candidate. Output main build/kenma/k04-v-carthage-s123/score.json.

| Map | W | L |
|---|---:|---:|
| schooltime | 6 | 0 |
| portals | 4 | 2 |
| slithery_fight | 2 | 4 |
| queen_of_spades | 3 | 3 |
| default | 3 | 3 |
| trophy | 0 | 6 |
| dilemma | 1 | 5 |
| autarky | 2 | 4 |
| devil | 3 | 3 |
| trauma | 5 | 1 |
| australia | 3 | 3 |
| islands | 3 | 3 |
| unsw | 5 | 1 |
| maze | 3 | 3 |
| weakhold | 4 | 2 |
| stripes | 2 | 4 |
| tower_defense | 1 | 5 |

# Kenma 03 — sealed-pocket queen

Parent: carthage-05-free-sprint at ea8ada4e2. Independent of Kenma 01/02.

Proves a connected component of at most eight cells from known nonportal terrain. In such a pocket, original queens (id 0/1, as in the current engine maps) split down to length two whenever possible and otherwise take a safe single step. Nonqueen dragons seeing the original queen in their sealed pocket deliberately cull using SPLIT 1, before the queen next moves. Other dragons reserve one population slot for emergency queen splits. No map identity condition.

Precedent: Rome 06 cage E1; this variant confines donor culling and queen movement to observed sealed pockets and selects the complete single-step action instead of truncating a scored sprint.

Status: provisional lane best. Native Carthage and Kageyama scorecards and four sandbox checks complete; 272-game zoo panel complete. No upload requested.

## Carthage scorecard

17 current ranked maps, both seats, seeds 1–3: **58 wins, 44 losses, no draws or runtime errors**. Provisional lane best; Zoo scorecard 220–52, below the supplied parent reference 226–46. No ladder recommendation yet.

| Map | W | L |
|---|---:|---:|
| schooltime | 6 | 0 |
| portals | 3 | 3 |
| slithery_fight | 4 | 2 |
| queen_of_spades | 3 | 3 |
| default | 3 | 3 |
| trophy | 3 | 3 |
| dilemma | 3 | 3 |
| autarky | 3 | 3 |
| devil | 3 | 3 |
| trauma | 3 | 3 |
| australia | 4 | 2 |
| islands | 2 | 4 |
| unsw | 5 | 1 |
| maze | 4 | 2 |
| weakhold | 3 | 3 |
| stripes | 3 | 3 |
| tower_defense | 3 | 3 |

Deployment: four sandbox games (Schooltime and UNSW, both seats, seed 1), zero runtime errors; max 10,910,667 points, max first-turn 10,814,937; zip 3,923,010 bytes. Results main build/kenma/deploy/kenma-03-pocket-queen/summary.json.

## Kageyama scorecard

17 current ranked maps, both seats, seeds 1–3: **61 wins, 41 losses, no draws or runtime errors**. Opponent kageyama-01-p1-slot. Output main build/kenma/k03-v-kageyama-s123/score.json.

| Map | W | L |
|---|---:|---:|
| schooltime | 6 | 0 |
| portals | 3 | 3 |
| slithery_fight | 5 | 1 |
| queen_of_spades | 5 | 1 |
| default | 4 | 2 |
| trophy | 3 | 3 |
| dilemma | 3 | 3 |
| autarky | 2 | 4 |
| devil | 6 | 0 |
| trauma | 4 | 2 |
| australia | 5 | 1 |
| islands | 5 | 1 |
| unsw | 4 | 2 |
| maze | 2 | 4 |
| weakhold | 0 | 6 |
| stripes | 1 | 5 |
| tower_defense | 3 | 3 |

## Development robustness check

Schooltime seed 5, both seats versus Carthage: **2–0**, queen length 3–0, zero runtime errors. Both Kenma queens survived all 500 rounds; sampled population reached 63. This did not reproduce the earlier Shenzhen reserve-1 failure in a different cage implementation, but does not establish safety against all population bursts. Output main build/kenma/k03-schooltime-s5/ and k03-schooltime-s5-diagnostics.json. Reserved seeds 11–13 remain untouched.

## Zoo scorecard

Eight canonical opponents × 17 live ranked maps × both seats, seed 1: **220–52**, zero draws or runtime errors. This is six fewer wins than the brief’s **226–46** Carthage reference. It does not support a pool improvement; the provisional-best choice is based on the direct Carthage/Kageyama results, and no ladder promotion is requested. The 226–46 reference has the same roster and parent fingerprint but was not reproduced by this lane on the same host.

| Map | W | L |
|---|---:|---:|
| schooltime | 15 | 1 |
| portals | 12 | 4 |
| slithery_fight | 12 | 4 |
| queen_of_spades | 16 | 0 |
| default | 13 | 3 |
| trophy | 15 | 1 |
| dilemma | 15 | 1 |
| autarky | 16 | 0 |
| devil | 15 | 1 |
| trauma | 13 | 3 |
| australia | 11 | 5 |
| islands | 16 | 0 |
| unsw | 9 | 7 |
| maze | 14 | 2 |
| weakhold | 8 | 8 |
| stripes | 5 | 11 |
| tower_defense | 15 | 1 |

| Opponent | W | L |
|---|---:|---:|
| fenrir-v18-arrival-ready-beds | 24 | 10 |
| yuna-v05-core | 24 | 10 |
| chaewon-y04-probe | 27 | 7 |
| sinbad-v07-divecap | 30 | 4 |
| gavroche-v32-supported-divecap | 27 | 7 |
| ouroboros-m01-vibing-mimic | 28 | 6 |
| kazuha-s01-swarm-dissolve | 29 | 5 |
| hunter-v20-portal-scouts | 31 | 3 |

Output main build/kenma/k03-zoo-s1/score.json. Two resource-interrupted attempts are retained separately; both fixtures were retried successfully. No other free-lane best found in the main BOARD at completion. Reserved-seed confirmation remains outstanding.

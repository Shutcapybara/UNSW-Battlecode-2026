# Kenma 05 — post-opening keeper

Parent: kenma-04-keeper-action. One runtime change: the learned queen controller starts at round 25 instead of round 0. The pocket rescue remains active from the start; all other behavior and the model are identical.

Motivation: Kenma 04 keeps more queens but its seed-1 losses on Trophy and Tower Defense show a population deficit by rounds 50–100. This candidate preserves the parent policy through the opening before switching the queen to the keeper action model. This mechanism is a hypothesis; no score is claimed before paired games finish.

Model provenance and original export parity: main build/kenma/queen-action-v1/. Status: prepared, unmeasured.

## Completed Carthage screen

17 live ranked maps × both seats × seeds 1–3: **54–48**, zero draws or runtime errors. Improved over Kenma 04 (50–52), but rejected as an improvement over Kenma 03 (58–44). Weakhold 0–6. The first two interrupted infrastructure attempts are preserved under the run’s attempts directory and were retried successfully; they are not bot runtime failures. Output main build/kenma/k05-v-carthage-s123/score.json.

| Map | W | L |
|---|---:|---:|
| schooltime | 6 | 0 |
| portals | 4 | 2 |
| slithery_fight | 5 | 1 |
| queen_of_spades | 3 | 3 |
| default | 3 | 3 |
| trophy | 4 | 2 |
| dilemma | 2 | 4 |
| autarky | 3 | 3 |
| devil | 3 | 3 |
| trauma | 3 | 3 |
| australia | 4 | 2 |
| islands | 1 | 5 |
| unsw | 4 | 2 |
| maze | 4 | 2 |
| weakhold | 0 | 6 |
| stripes | 3 | 3 |
| tower_defense | 2 | 4 |

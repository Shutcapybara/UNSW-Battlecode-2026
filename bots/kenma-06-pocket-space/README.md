# Kenma 06 — pocket rescue plus queen space filter

Parent: kenma-03-pocket-queen. Copies policy.hpp and params.hpp byte-for-byte from asahi-05-kz12-k16 in the main checkout. All other runtime files are the Kenma 03 parent.

Retains the sealed-pocket rescue, donor culling and one-slot reserve. Adds Asahi's candidate-specific optimistic reachable-space check for original queens: veto a safe single step into fewer than 16 reachable cells without a sufficiently large cycle; if every step is vetoed, fall back to maximal reachable space. Unknown terrain, immediate dive/head-to-head outcomes and multi-step paths retain the parent's treatment. No map-identity inputs or new fitted parameters. The source's diagnostic fields remain present, but main.cpp does not emit Asahi's extra log line.

Motivation: Kenma 03 lost all six Weakhold games to Kageyama; Asahi's documented seed 2–3 pool improvement replicated on Weakhold. This is a composition hypothesis, not evidence that the combination improves play.

Status: not selected over Kenma 03. Full Carthage comparison finished **57–45**, zero draws or runtime errors, 17 ranked maps × both seats × seeds 1–3. Weakhold improved from 3–3 to 5–1, offset by one fewer win each on Portals, Slithery Fight and Tower Defense. Kenma 03 remains best at 58–44. No deployment checks spent on this weaker common-opponent result. Reserved seeds 11–13 and new maps untouched.

| Map | W | L |
|---|---:|---:|
| schooltime | 6 | 0 |
| portals | 2 | 4 |
| slithery_fight | 3 | 3 |
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
| weakhold | 5 | 1 |
| stripes | 3 | 3 |
| tower_defense | 2 | 4 |

Output: main build/kenma/k06-v-carthage-s123/score.json.

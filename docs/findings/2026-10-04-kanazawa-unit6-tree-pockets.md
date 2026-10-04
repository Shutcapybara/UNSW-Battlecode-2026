# Acyclic (tree) pockets are terminal for every queen; cyclic micro-pockets are safe

4 October 2026, 05:46 UTC. Kanazawa unit 6. Corpus analysis only; no bot run.

## Contract
Himeji H24-01 is accepted: `q_deadend.py` (ca9feb38a) counted cells other than v. Here **C(u→v)** = cells reachable from v in terrain minus u, **including v** (C = E + 1). For every single-step queen move with C ≤ 5, the pocket P is classified by the longest simple cycle in P ∪ {u}:
- **tree**: P ∪ {u} has no cycle, so the queen cannot orbit
- **cyc_short**: there is a cycle, but it is shorter than L + 1 (L = queen length after the move)
- **orbit_ok**: there is a cycle of length ≥ L + 1

Label `w6` (peer label): queen wall death with 0 ≤ death − (t+1) ≤ 6.
Tools: `tools/kanazawa/q_cycle.py` (with `--holdout`) and `tools/kanazawa/q_tree_escape.py`.

## Pre-declared prediction (unit 5, next step 1)
Opponents' surviving low-C entries are cyclic and ours are acyclic. This was declared before the run. The holdout set is index positions 192–285, the 94 games that Himeji H24-02 showed lie outside the unit-5 selection.

## Results (first low-C entry per queen, team 7, post-m2)
| set | us: tree | us: cyc_short | us: orbit_ok | opp: tree | opp: cyc_short | opp: orbit_ok |
|---|---|---|---|---|---|---|
| unit-5 selection (96 games) | 18/19 | 2/3 | 1/4 | 8/14 | 0/0 | 0/8 |
| **holdout (94 games)** | **19/19** | 0/2 | 1/1 | 8/12 | 0/0 | 0/9 |

Move level, opponents: orbit_ok gives 0 wall deaths in about 7,500 moves. Nearly all of these come from one queen per game orbiting for 495–999 moves. Himeji traced these queens to Schooltime, so this is an opponent spawn-pocket behaviour, not general skill. Our own moves: tree 110/114, orbit_ok 4/15.

## Nobody escapes a tree pocket (H-KZ16 falsified)
`q_tree_escape.py` lists every first tree entry that is not followed by a wall death within the window (190 games):
- 10 opponent queens: 8 died within 3–8 rounds by **self** or **invalid**, usually after splitting while trapped (lengths fall to 2 and new ids appear). One died by wall at t + 8, and one entered at r499 (game end).
- 1 of ours died by self at t + 6.

Every pocket entry made before r499 ended in death. Combined over the 190 games: **38 of our queens (20 %) and 25 opponent queens (13 %) entered a tree pocket with C ≤ 5 and died.** The `wall` cause label undercounts the trap, because self and invalid deaths after entry are the same event.

## Consequences
1. **The H-KZ12 dial should be the tree form.** Reject u→v when C ≤ 5 and P ∪ {u} has no cycle of length ≥ L + 1. This removes the Schooltime false positives that a bare C < k dose would hit, and it is static per (map, u, v, L ≤ 5). It addresses about one game in five, and survival given entry is roughly 0 %. The k ∈ {8, 16} doses still need the same cycle rule; extending the classification beyond C = 5 is next.
2. **The opponents leak the same trap (13 % of queens), so it is targetable.** See the blue-sky H-KZ17 below.
3. **D-044 labels:** post-entry labels should be "any queen death within 8 rounds", not wall only (for Himeji and Osaka).

Caveats: the data are observational. Entry may be forced, for example when every alternative is worse; that is H-KZ11 and remains untested. "Before" counts against 'after' are not a causal effect. Opponent team ids pool all opponents, not only the top ten.

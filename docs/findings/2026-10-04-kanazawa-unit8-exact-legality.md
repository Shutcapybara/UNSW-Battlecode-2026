# Kanazawa unit 8 (4 Oct 06:41–07:00Z): exact turn-start legality re-test of H-KZ11; weakhold entry branches

## Why
Himeji H26-05 (reading 57bfbb463): my unit-7 alternatives removed every dragon's tail and ignored id order, so the own
tail (always fatal) counted as free and higher-id dragons' tails were wrongly vacated. Requested exact TurnStart legality
before the H-KZ11 falsification stands.

## Method (`tools/kanazawa/q_forced2.py`, frozen 06:50Z before running)
Occupancy at our queen's turn in round t: dragons with id < q use R[t+1] (already acted; absent = died), id > q use R[t]
including tails, new ids use R[t+1] (conservative), own body all cells including the tail. Single-step alternatives only
(sprint ignored, so conservative). `avoid2` adds a 2-ply check: the alternative has at least one legal onward cell.
Rule: exact avoidable share ≥ 0.7 keeps H-KZ11 falsified; ≤ 0.5 reverts it to open.

## Result (our queen's first tree-pocket entry)
| set | n | avoid (exact) | of which avoid2 | other (only tree/short-cycle alt) | no free cell | unit-7 approx |
|---|---|---|---|---|---|---|
| in-sample stride 96 | 19 | **14 (0.74)** | 13 | 1 | 4 | 16 |
| consumed holdout 192+ (replication only) | 19 | **12 (0.63)** | 11 | 3 | 4 | 12 |
| pooled | 38 | 26 (0.68) | 24 | 4 | 8 | 28 |

Opponents: in-sample 11/14 avoidable, holdout 6/12.

Reading: the in-sample set holds the frozen falsification band; the holdout sits between bands. Himeji's correction
lands on 2 of 38 entries. "Mostly avoidable at the entry step" stands; about one third are forced at the entry step, i.e.
the decision point is upstream. H-KZ11 weight 0.2 → 0.3. The pearl association (17/19, 18/19) remains associational,
not a causal planted-bait value (accepted from H26-05).

## Weakhold (all 16 post-m2 team-7 games; `tools/kanazawa/q_weakhold.py`)
Our queen enters a tree pocket at length 2 in 16/16 games and dies 5–7 rounds later; we win 1/16. Two branches:
- r24, (8,8)→(8,7), death r30: 8 games. At the entry step the only free alternatives are tree/short-cycle (class
  `other`): already sealed upstream, consistent with Himeji H22-01.
- r40, (29,14)→(28,14), death r45: 7 games. A legal open alternative with a legal onward cell exists at the entry step
  (`avoid2`). A one-step veto (H-KZ12, k ≥ 5) would remove this branch.
- r77 (28,0)→(27,0): 1 game.
This replicates Chongqing C3-01 (weakhold deterministic r29/r44, 15/16) and splits it: the r40 branch is a veto target,
the r24 branch needs an upstream rule (Himeji H22-01: sealed before the final split).
Opponents enter the same cells in 6/16 games, usually later (r22–r377).

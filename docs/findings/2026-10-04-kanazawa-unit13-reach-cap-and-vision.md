# Kanazawa unit 13: the reach cap does not move H-KZ26; strikes are vision-triggered (4 Oct, 09:10–09:35Z)

Inputs: Himeji 17e6a73c7 (H31-01 strike vision at the attacker's TurnStart 20/20; H31-02 BFS cap 11 misses L12/B13 in pure fixtures, selected-case incidence unmeasured), Nara f9fff6a72 (H-KZ26 reading: value/feature gap; suggests a death-round-shift column), Rome 1ac66fa62 and Himeji H31-08 (H-KZ12 k4 272/272 games done, KZ12 logs absent), Chongqing 646811d6e C8-01..04.

## 1. Reach cap (answers H31-02)
`tools/kanazawa/q_avoid2.py` = unit-12 q_avoid with the BFS cap lifted from 11 to 60. Objective frozen 09:20Z: primary safe1 on our 20, expected unchanged; a drop of ≥ 2 would send H-KZ26 back to 0.5 and require uncapped reach in the spec. Same in-sample 96 (descriptive; consumed set).

| | ours (n 20) | opp (n 4) |
|---|---|---|
| safe1, cap 11 (unit 12) | 15 | 2 |
| **safe1, cap 60** | **15** | 2 |
| safe1 at B+1 (dose m=1) | 14 | 2 |
| any enemy head L ≥ 10 at decision | 1 | 1 |

The selected-case incidence of the cap defect is **0/20**: all 20 killers have L 3–5 (B ≤ 5), and the one case with an L ≥ 10 enemy on the board does not change. H31-02's fixture point stands for the tester implementation (the bot must use uncapped reach, since queens meet long enemies later in the game), but the 15/20 does not depend on it. The m=1 dose costs one case (15 → 14). The "approximate alternatives, not verified rescues" scope (H31-02) is accepted: 15/20 remains a geometric availability count.

## 2. Vision timing (H31-01) → H-KZ28 / H-KZ29
At the attacker's own TurnStart our queen was within its vision **20/20** (my R[dr] measure, 15/20, used the wrong clock). My frozen H-KZ28 falsifier was "≥ 6/20 unseen"; 0/20 unseen means **H-KZ28 (strikers act on their own vision) is supported, 0.35 → 0.6**, as geometric consistency, not intent. **H-KZ29 (tracking beyond vision) is not needed by these endpoints, 0.25 → 0.1.**

Consequence for the filter: the striker always sees the queen, and vision is symmetric (Chebyshev 3), so the queen always has the striker in view at its own move, one round earlier, unless the striker enters view during the round. A queen-local filter needs no sonar or shared threat information.

## 3. Blue-sky H-KZ30, bodyguard (exploratory, tested here)
Claim: the head-on is mutual (killer died 43/43), so an ally child that could strike the striker first turns a queen loss into a child-for-child trade. Measure: some ally non-queen head within B(L_ally) of the killer's head at R[dr]. **2/20.** At the last turn there is almost never an interceptor in place, so a passive bodyguard does not exist; only a proactive escort (keep an ally within reach of the queen) would. **H-KZ30 0.1.** An escort costs production and does not beat the H-KZ26 filter at 15/20.

## 4. New blue-sky H-KZ31, invisibility rule
If strikes are vision-triggered (§2), a queen that keeps every enemy head at Chebyshev ≥ 4 after its move is outside every striker's view at the striker's TurnStart. For L ≤ 4 strikers, B ≤ 3 < 4, so this is weaker than reach for short enemies and stronger for L 5+. Test: in the 20 cases, count steps with Chebyshev ≥ 4 from all enemy heads and Cb ≥ 4, and compare with safe1. Falsifier: the invisible-step count is < 10/20 (too restrictive to use as a rule). Cost: one corpus pass. Weight 0.25.

## Hypothesis moves
H-KZ26 0.6 (unchanged, reach-cap robust); H-KZ28 0.35 → 0.6; H-KZ29 0.25 → 0.1; H-KZ30 new 0.1; H-KZ31 new 0.25.

Data: `docs/findings/kanazawa-data/unit13-q_avoid2.txt`.

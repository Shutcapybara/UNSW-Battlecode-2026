# Kanazawa unit 11: our queen's head-to-head deaths are mostly enemy sprint strikes, not avoidable contests

4 October 2026, 08:11–08:35Z. Tool `tools/kanazawa/q_h2h.py`; the raw rows are in `docs/findings/kanazawa-data/unit11-q_h2h.txt`. The sample is the same in-sample 96 as q_dose: stride 96 of the first 286 eligible post-m2 team-7 games, 96/96 decoded.

## Frozen objective (08:20Z, before the run)
- H-KZ24 is supported if at least 1/3 of our queen h2h deaths are foreseeable and had an uncontested alternative.
  - Foreseeable: the killer's head is on or next to the death cell at R[dr].
  - Uncontested alternative: Cb ≥ 4, not next to any head, tails exempt. This is optimistic and is not a legality check (H29-02).
- Secondary: if ally killers make up at least 50 % of these deaths, redirect to the P-04 ally guard.
- Pre-move state is R[dr] (checked on game 1).

## Results (Himeji H29-04 separations)
| | us (n = 43) | opp (n = 36) |
|---|---|---|
| killer enemy / ally | 42 / 1 | 31 / 5 |
| queen was the mover | 9 | 16 |
| killer also died that round | 43 | 36 |
| queen shorter / equal / longer than killer | 16 / 20 / 5 | 0 / 18 / 17 |
| killer distance 1 / 2 / ≥ 3 / unknown (portal?) | 21 / 14 / 6 / 2 | 31 / 4 / 0 / 1 |
| foreseeable and uncontested alternative | **11 (26 %)** | 19 (53 %) |

- **The frozen bar fails (11/43 < 1/3), so H-KZ24 as specified drops to 0.2.** Ally share is 1/43, so this is not P-04.
- Every queen h2h death is a mutual collision: heads that collide both die. The 'mutual' event flag is set on one record only, so a count of that flag undercounts.
- Post hoc (labelled in the source): **20 of our 43 queen h2h deaths (21 % of all 95 queen deaths) come from an enemy dragon whose head was 2–5 steps away at round start.**
  - Killer length is 3–5 (17 of 20 are length 3). Our queen is length 2–3 (19/20).
  - Rounds 14–210 (median about 80), on 10 maps (Around UNSW 4, Trophy 3, Australia 3, …).
  - Opponent queens suffer this 4/36 times, all after r130.
  - This reads as a sprint strike: a length-3 unit trades itself for our queen. Other lanes already document this primitive (the `Strike` rule: sprint into an enemy head, gain from V(their length) − V(our length) − sprint cost).
  - In 19 of the 20 cases an uncontested Cb ≥ 4 alternative existed. "Uncontested" checks adjacency only, not sprint reach, so this does **not** show the strike was avoidable.

## Hypothesis
- **H-KZ26 (0.45): a queen standoff radius.** Our queen keeps enemy heads outside sprint reach, using distance ≥ the enemy's length (a length-3 unit can sprint 2), or stays behind an ally body.
  - Size if true: up to 20/96 games of queen deaths. The H-KZ12 ceiling is about 15.
  - Falsifier: at R[dr−1] and R[dr−2], fewer than half of the 20 cases had a legal queen move that kept the killer outside its reach, or the killer was outside our vision.
  - Cost: one corpus pass (next unit), then one switch in a carthage-05 copy.
  - Suited to: Kanazawa (corpus), then Rome or Seoul (ladder).
- Caveat: snapshot semantics are R[t] approximations (H27-05). The sprint mechanics (cost, maximum steps) are inferred from killer distance, not read from the engine.

# Kanazawa unit 12 — queen sprint strikes: avoidable at the last turn (H-KZ26 supported, 0.6)

4 Oct 2026, 08:40–09:05Z. Tools `tools/kanazawa/q_avoid.py` (frozen 08:50Z), `tools/kanazawa/q_seen.py` (frozen 08:58Z).
Raw output: `docs/findings/kanazawa-data/unit12-q_avoid.txt`, `unit12-q_seen.txt`. Sample: the 24 unit-11 strike cases
(kdist ≥ 2 and killer died; 20 ours, 4 opponent), from the consumed in-sample stride-96 set. Descriptive; not out of sample.

## Inputs taken
- Himeji H30-01: food-free sprint budget **B(L) = ceil(L/4) + L − 2** (L2→1, L3→2, L4→3, L5→5, L6→6, L9→10). The unit-11
  "distance ≥ enemy length" rule is unsafe for L ≥ 5; H-KZ26 is restated with B.
- Himeji H30-02: all 20 confirmed as enemy multi-step attacks; 4 exceed B via meals (869494, 881387, 857671, 869498).
- Himeji H30-04: H-KZ24's 11/43 is a frozen point decision, not a population refutation (CI 8.9–45.7 %). Accepted.

## Test (objective frozen before the run)
Decision state D = R[dr]: the queen (id 0/1) acts before any child in round dr; the killer strikes after, from its own TurnStart.
A queen move w is **safe** if it is a free neighbour (not kelp, neck or occupied; tails exempt, so approximate), no enemy head e
has body-ignoring BFS distance to w ≤ B(len e), and Cb(u→w) ≥ 4. Bar: ≥ 10/20 safe → 0.6; ≤ 4/20 → 0.2; else 0.4.

| ours (n = 20) | count |
|---|---:|
| a safe single step existed (all enemies, food-free) | **15** |
| …excluding the 4 food-extended strikes (conservative) | **11** |
| safe against the killer only | 17 |
| safe with a queen multistep within its own B | 17 |
| killer head within the queen's vision (Chebyshev 3) at D | 15 |
| killer within vision of any ally head at D | 19 |
| killer already within B of the queen at R[dr−1] | **0** (4 within B+1) |

Opponent queens (4): safe 2/4, killer-only 4/4.

**Reading.** Both counts clear the frozen bar (15 and conservative 11 ≥ 10), so **H-KZ26 goes to 0.6**. None of the 20 queens began
the previous round within the killer's reach: the queen walks into the reach zone (or the two close together in one round), it is
not caught standing. A one-step filter at the queen's own move would have had an escape in about 11–15 of 20 cases. The four
food-extended cases are exactly the ones the food-free filter misses, which supports Himeji's H-H8 (food-aware reach) as the
upgrade path, not a replacement. 5/20 killers are outside the queen's vision at D, but 19/20 are visible to some ally: a pure
own-vision rule covers about 15, and ally sharing (sonar packet) covers the rest.

## Blue-sky H-KZ28 (strikers act on their own vision) — inconclusive, 0.35
Frozen: supported if the killer saw the queen at R[dr] in ≥ 16/20 and first saw it ≤ 2 rounds earlier in ≥ 10/20; refuted if
it could not see the queen in ≥ 6/20. Result 15/20 and 12/20; 5/20 unseen (the four food cases plus the L5 striker 858816, all
long-range at Chebyshev 4). Neither bar met. Side observation: in about 8/20 the killer closes monotonically from Chebyshev
8–12 over 5–6 rounds before contact (852909: 12, 11, 10, 9, 7, 5, 3), i.e. it approaches from beyond vision. That is either
pearl-driven drift or shared tracking; it is the next thing to separate (H-KZ29 below).

## Exploratory exposure (H-KZ27) — not usable
Per-round exposure (enemy head at distance 2..B at round start) counted only 92 queen-rounds with 6 strikes, against 51 917
child-rounds with 1 676 strikes. The definition misses the dominant pattern (queens step into reach on their own move), so this
is not a per-exposure rate and does not test H-KZ27. Needs move-level exposure with matched non-queens (Himeji H30-04).

## Spec for a tester (one mechanism, three doses)
Queen move filter: veto w if some **visible** enemy head e has BFS(ignoring bodies) dist(e, w) ≤ B(len e) + m, unless no
alternative with Cb ≥ 4 remains (then fall back to the parent ranking). Doses m ∈ {off, 0, 1}. Keep H-KZ12 off or fixed.
Expected sign: fewer queen h2h-strike deaths (target 20/95 of queen deaths in-sample), possible food cost from retreat.
Report all-cause queen deaths, cause split, food, official wins, by map hash; Rome/Seoul when free (Rome runs H-KZ12 now).
Food-aware reach (H-H8) is the next dose family, not mixed in.

## Hypotheses
- H-KZ26 0.45 → **0.6** (frozen bar met: 15/20, conservative 11/20).
- H-KZ28 (blue-sky) 0.35: inconclusive.
- **H-KZ29 (blue-sky, new) 0.25**: strikers track our queen beyond vision (sonar or packets). Falsifier: approach paths from
  Chebyshev > 3 point at pearls/corpses at least as well as at the queen. Cost: corpus, one unit. Kanazawa.

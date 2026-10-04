# Kanazawa unit 14 (4 Oct 09:41–09:47Z): H-KZ31 invisibility rule fails; H-SZ34 does not cover queen strikes

Data: `kanazawa-data/unit14-q_invis.txt` (tool `tools/kanazawa/q_invis.py`, frozen 09:43Z), and unit-13 rows (`unit13-q_avoid2.txt`).
Population: the same 20 (ours) + 4 (opponent) queen sprint-strike deaths (in-sample stride 96, consumed; descriptive).

## 1. H-KZ31 (invisibility: step to a cell with every enemy head at Chebyshev >= 4): falsified
Frozen expectation: <= 6/20 (15/20 killers already within Cheb 3; one step lifts Cheb by at most 1). Falsifier: < 10/20.

| ours, n=20 | cases with >= 1 such step |
|---|---|
| invisible to every enemy head and Cb >= 4 | **4** |
| invisible to the killer only | 6 |
| invisible and outside every reach B(Le) | 3 |
| reach-safe (safe1, unit 13) | 15 |
| queen already at Cheb >= 4 from every enemy at R[dr] | 2 |

At the last turn the queen sits at Chebyshev 1–3 from the striker in 18/20 cases. Hiding from vision is no longer possible by then, but leaving the reach still is. **H-KZ31 falls to 0.1.** The reach veto (H-KZ26) remains the last-turn lever. A vision-standoff rule could only act earlier, at R[dr-1] or before, which is H-KZ26's dose m=1 territory.

## 2. Cross-lane: Shenzhen H-SZ34 ("be the mover"; reach = min(L-1, 3); applies when we are longer)
Measured on the 20 queen strikes:
- **Length polarity is reversed.** The striker (the mover) is longer than our queen in 12/20 cases, equal in 7/20 and shorter in 1/20 (queen L6 vs striker L3). H-SZ34 fires only when we are longer than the visible head, so it would cover at most 1/20 queen strikes. H-SZ34 and H-KZ26 are therefore complementary and do not overlap: H-SZ34 covers the long-partner children, and H-KZ26 covers the short queen.
- **Reach form.** min(L-1, 3) misses 5/20 strikes: the 4 food-extended ones, plus one L5 striker at distance 5 (B(5) = 5). The food-free form B(L) = ceil(L/4)+L-2 misses only the 4 food-extended cases. For L <= 4 the two forms agree (2 at L3, 3 at L4). Recommendation: H-SZ34 should use B(L), or note that the cap at 3 is deliberate for L >= 5.
- All 20 strikes killed both sides (the unit-11 selection is kdied). This agrees with Shenzhen's "every h2h kills both" (sim). Enemies are trading an L3 for our queen, and that trade is cheap for them.

## 3. H-KZ28 revision (Himeji H32-03)
Himeji is right that "the queen was in the striker's vision 20/20" is necessary for own-vision striking but does not show it is sufficient. H-KZ28 goes back to 0.45 from 0.6. The 5 queens that were unseen before the strike remain open.

## 4. Blue-sky: H-KZ32 portal shadow
Vision is Chebyshev <= 3 with wrap, and it does not pass through portals, while reach BFS does. If strikers act only on their own vision, a queen whose nearby enemy heads connect to it only through portal paths is reachable but never targeted. Falsifier: in the corpus, >= 3 queen strikes whose striker path used a portal while the striker head was at Cheb >= 4. Size: portal maps only (the C8-02 portals cluster). Cost: one corpus pass that tags BFS paths through portal edges.

# Kanazawa unit 15 — strike sufficiency, veto precision, and who dodges (4 Oct 10:20–10:35Z)

Tool: `tools/kanazawa/q_suff.py` (frozen 10:20Z; the exploratory chase/flee follow-up was added 10:24Z after the primary). Data: `docs/findings/kanazawa-data/unit15-q_suff.txt`. Set: in-sample stride-96 (first 286 eligible post-m2 team-7 games). It is consumed, so the results are descriptive.

## Definition
An opportunity at state R[r] is an enemy head e and a target head t (other team) with Cheb(e,t) ≤ 3 (wrap), so t is in e's TurnStart vision, and 2 ≤ BFS(e→t) ≤ B(Le)+1, where B(L) = ceil(L/4)+L−2 (Himeji H30-01). The +1 is there because the queen moves first. The target is struck if it dies by h2h in round r and the killer is e. Target classes: Q is a queen (id ≤ 1); CL is a child longer than the striker; CS is any other child.

## Results
| target | hit / opp | rate | Le 2–3 | chase | flee |
|---|---|---|---|---|---|
| our Q | 25 / 264 | **9.5 %** | 24/221 = 10.9 % | 31 % | 69 % |
| our CL | 513 / 11,036 | 4.65 % | 4.6 % | 32 % | 61 % |
| opp Q (our strikers) | 18 / 586 | **3.1 %** | 18/420 = 4.3 % | 36 % | 78 % |
| opp CL | 984 / 10,809 | 9.1 % | 10.3 % | 32 % | 64 % |

Chase and flee are measured on non-hit opportunities with both dragons alive at R[r+1]. Chase means the striker's head moved closer to the target's old head. Flee means the target's head moved farther from the striker's old head.

Veto firing: our queen has ≥ 1 opportunity in 238 of 9,324 alive queen-rounds, which is 25.5 per 1k (opponent queens 29.5 per 1k). That is about 10 firings per strike.

## Reading against the frozen predictions
- Prediction "Q rate ≤ 0.05" failed: the rate is 0.095. It did not reach the 0.15 sufficiency bar either, so **H-KZ28 stays at 0.45**: in-vision plus in-reach makes a strike likely, but it does not determine one.
- Prediction "Q/CL ≥ 2" held at exactly 2.0. The 95 % binomial CI on 25/264 is about 6–14 %, so the ratio CI is about 1.3–2.9. Correlated consecutive rounds make the interval wider still.
- The exploratory follow-up separates the cause. Enemy strikers do not chase our queen more than our children (31 % vs 32 %). Our queen steps away less often than the field's queens (69 % vs 78 %) and is struck about 3× as often per opportunity. **H-KZ27 (targeting) drops to 0.15. H-KZ26 rises to 0.65**: the field's queens already behave as if they had a reach veto.
- Caveats: the opponent pool is mixed, and opponent queens are alive for 2× as many rounds (ours die earlier). The flee measure is crude (one step, from the striker's old head).

## Cross-lane
- Nara (N2 queen hunting): our strikers convert 3.1 % of opponent-queen opportunities against 9.1 % on long children. That gap comes from opponent queens dodging, not from our strikers failing to try (36 % chase). A hunter therefore needs a forcing pattern (H-KZ35 below), not just a "go for the queen" weight.
- Seoul (H-KZ26 spec): cost guard. The veto constrains about 2.5 % of queen moves.

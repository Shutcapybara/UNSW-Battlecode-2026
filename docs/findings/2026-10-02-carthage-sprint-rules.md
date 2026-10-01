# Carthage — 1.2.3 sprint pricing on the prior base (carthage-04; 05 pending) (2 Oct 2026)

Setup as in `2026-10-01-carthage-base-and-queen.md` (pool + gen, seeds 1–3, both seats, D-032 as coded in
`tools/carthage/lane.py`; absolute and parent-relative numbers).

The base's simulator charges one segment for every step after the first and forbids any sprint at length 2 (the
pre-1.2.3 price), and its move generator proposes 2- and 3-step moves only when an enemy head is within Chebyshev 4.

## carthage-04-sprint123 (switch `sprint_rules_123`; parent 00)

Mechanism: simulator and move score charge `max(0, steps − ceil(L/4))` segments; with the switch off the code reduces
to the old price exactly. Expected: small, since sprints are only proposed near threats.

| | pool | gen |
|---|---|---|
| Δecon~ [5 %, 95 %] | −0.001 [−0.003, +0.002] | +0.001 [−0.001, +0.007] |
| Δwin [5 %, 95 %] | **+0.040 [+0.016, +0.065]** (pairs 37/425/18, p = 0.015) | +0.003 [−0.011, +0.017] |
| units / total@100 | +0.000 / +0.000 | +0.000 / +0.000 |
| tier-2 | within ±1 % | within ±1 % |

Pool wins by map: schooltime +9, slithery +6, portals +4, default +1, autarky −1; by verdict, 16 of the net come from
"longest dragon" r500 games (the long dragons now price their threat-time sprints correctly). Gen twins (slithery_rec,
portals_rec, portals_tr, default_tr): net +1 over 96 pairs (18/17) — **no transfer**, so not a D-036 local hold.

**Verdict: REJECT** by the letter (pool econ lb −0.003 ≤ 0; every guard passes). It is a correctness fix with no
measured cost; reasonable to carry in any 1.2.3 base, but it is not a gain off the pool.

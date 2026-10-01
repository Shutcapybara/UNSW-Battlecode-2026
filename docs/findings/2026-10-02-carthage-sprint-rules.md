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

## carthage-05-free-sprint (switch `free_sprint`; parent 04)

Mechanism: the forward search carries 2- and 3-move shortest-route prefix masks; with no enemy head within Chebyshev 4
and ≥ 2 free steps (length ≥ 5), the dragon is also offered the on-route 2-step moves (3-step at length ≥ 9), scored as
`steps` units of route progress. Threat-time sprint generation unchanged. CPU max 11.30 M (base 10.83 M). In single
games it multiplies multi-step moves ~10× (Big Empty: 481 → 6,655).

| | pool vs 04 | gen vs 04 | pool vs 00 | gen vs 00 |
|---|---|---|---|---|
| Δecon~ [5 %, 95 %] | +0.002 [−0.002, +0.004] | +0.003 [−0.007, +0.008] | +0.001 [−0.003, +0.004] | +0.003 [−0.005, +0.011] |
| Δwin [5 %, 95 %] | +0.005 [−0.020, +0.029] | +0.014 [+0.000, +0.028] | **+0.045 [+0.019, +0.074]** | **+0.017 [+0.003, +0.031]** |
| Δunits / Δtotal@100 | 0 / 0 | +0.026 / +0.028 | 0 / 0 | +0.026 / +0.028 |
| tier-2 (rates vs parent) | wall +2 %, ally body +5 %, ally h2h +5 % | ally body +6 %, ally h2h +4 % | within +6 % | within +6 % |

Per-map pool Δecon vs 04: schooltime +0.058, everything else within ±0.003. Gen: relay_depots −0.215 is the one large
loss; nursery_bays +0.038, archipelago +0.035.

**Verdict: REJECT** by the letter (pool econ lb −0.002 vs 04, −0.003 vs 00); every guard passes. The economy medians
do not move because the free sprints happen mostly for long dragons (length ≥ 5), i.e. after r100, where the
medians are dominated by small dragons; the gain shows in wins and in gen material (units/total@100 +0.03). 04 + 05 is
the only stack in this lane with a win lower bound above 0 on **both** panels.

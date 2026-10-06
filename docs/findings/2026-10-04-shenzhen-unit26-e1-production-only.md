---
id: shenzhen-unit26-e1-production-only
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator screen (analysis copies only) — H-SZ53
title: Unit 26 — a reserve on production splits only (E1p) keeps the Schooltime queen 6/6 and removes the Slithery cost (total +19 %, wins 4–2), where plain E1 cost −7 %
evidence: unswbc 1.2.9; `c05e1p` vs `c05d` (carthage-05 + C + D); Schooltime template and Slithery Fight, seeds 1–3, both seats, 6 games per map
---

# 1. Probe E1p (H-SZ53)

Non-queens decide with the real unit limit. If the decision is a split other than an escape split (`why != 't'`) and
units ≥ limit − 1, they decide again with limit − 1. Probe C's sealed split runs after the decision with the real
limit, as before. In effect, only production gives up the last slot. No map identity, no observation beyond the
team's own unit count.

# 2. Result (6 games per map; E1 rows from units 24–25, other sets)

| map | arm | our queen alive at end | wins | pool total |
|---|---|---|---|---|
| Schooltime (cage) | C+D | 4/6 (2 invalid) | 2 | 857 |
| | E1 (unit 24) | 6/6 | 5 | +69 % |
| | **E1p** | **6/6** | **4** | **928 (+8 %)** |
| Slithery Fight | C+D | 0/6 | 2 | 609 |
| | E1 (unit 25) | 0/6 | 2 vs 4 | −7 % |
| | **E1p** | 0/6 | **4** | **726 (+19 %)** |

Deaths by cause barely move on either map (Slithery invalid 1,824 → 1,867, wall 253 → 246). The gain is not a
death-count effect.

# 3. Reading

* **H-SZ53 supported (0.45 → 0.6):** the production-only reserve keeps the cage fix whole (6/6 queens) and the
  Slithery cost is gone (−7 % → +19 %). In these two small sets, plain E1's cost on cap maps came from blocking escape
  splits, not from the reserve itself.
* Small n: the C+D baseline on Slithery moved between sets (741 in unit 25, 609 here) because the opponent instance
  differs. The sign is consistent with the mechanism, but the size is not established.
* **Recommendation to the evaluator:** if E is screened on `LIVE_MAPS_M2`, screen it in this form, as
  **C+D+E1p**: one switch, ungated, the reserve on production splits only. Predictions: Schooltime queen alive@RL ≥ 12/16 on each
  variant; pool pearls@250 ≥ −3 vs C+D (the E1/E3 pool cost was −7/−11).

# 4. Hypotheses

* **H-SZ53 → 0.6.** H-SZ50 holds at 0.65, and E1p is its preferred form.
* **H-SZ54 (0.35, new) — production at headroom 1 has low value anyway.** A child produced when the team is one slot
  from the cap has a shorter useful life: the next cull or seal at the cap will need that slot. Prediction, from the
  sim: children born at units ≥ limit − 1 die sooner than children born at headroom ≥ 8, and with fewer meals.
  Falsifier: the same median lifetime and meals. Size: one log pass over existing sim replays (spawn round, units at
  spawn via the frame's per-round unit counts). Suits this lane.

**RL translation.** Observation: unit headroom per decision. Action: the split-type distinction (production vs escape)
is a label the BC heads should keep. Value: the last slot is worth more as an escape than as a child.

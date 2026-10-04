---
id: shenzhen-unit27-e1p-wider-check
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator check (analysis copies only), H-SZ53 at a wider map set
title: Unit 27 — E1p on four more maps: the open-4 Schooltime queen is saved 5/6 (C+D 3/6), but on the three open maps E1p loses 6–12 in wins and ~4 % in total. The unit-26 Slithery gain does not generalise; the reserve is a Schooltime-for-open-maps trade
evidence: unswbc 1.2.9; `c05e1p` vs `c05d` (carthage-05 + C + D); Schooltime open-4, Around UNSW, Islands, Australia; seeds 1–3, both seats, 6 games per map
---

# 1. Result

| map | C+D queen alive | E1p queen alive | wins C+D–E1p | total C+D → E1p |
|---|---|---|---|---|
| Schooltime open-4 | 3/6 (3 invalid) | **5/6** (1 invalid, r373) | 3–3 | 807 → 863 (+7 %) |
| Around UNSW | 0/6 | 0/6 | **5–1** | 1,112 → 1,064 (−4 %) |
| Islands | 0/6 | 0/6 | 3–3 | 661 → 644 (−3 %) |
| Australia | 1/6 | 0/6 | 4–2 | 881 → 842 (−4 %) |
| three open maps | | | **12–6** | 2,654 → 2,550 (−4 %) |

Together with unit 26: on the Schooltime cage, E1p's queen survives 6/6 (C+D 4/6), with wins 4–2, and Slithery gives total +19 %, wins 4–2.

# 2. Reading

* **The cage benefit replicates.** Across both Schooltime variants, E1p's queen is alive 11/12 against 7/12 for C+D.
  The one open-4 death is still `invalid`. The production reserve covers the forced cage meal in most cases but not all:
  an escape split by another dragon can take the slot at the wrong moment.
* **The cost is real on the open maps.** Over three maps and 18 games, wins go 12–6 for C+D and total falls 4 %. In unit 26,
  Slithery showed the opposite sign on 6 games. With 6 games per map, the pooled open-map count (18) is the better
  estimate. **H-SZ53 → 0.5:** E1p is cheaper than plain E1 on Slithery, but not free.
* For the Chair, the trade is about +4 Schooltime queens per 12 (live Schooltime score −0.45) against roughly −4 % total
  and fewer wins on open cap maps. The live screen is where to price that. My sim cannot settle it at n = 6 per map.

# 3. Hypotheses

* **H-SZ53 → 0.5** (cost exists on the open maps; the cage fix holds).
* Two gates considered and **dropped before testing**, recorded so nobody re-derives them:
  (a) a time gate (reserve before round ~150 only) fails because the cage bed keeps spawning all game (gap 20–200);
  (b) a "reserve for one round after the queen eats" gate fails because no teammate can observe the caged queen's meal.
  The cage needs a slot at unobservable moments, so any legal fix is a standing reserve, and a standing reserve has a cost
  on cap maps. That trade is a Chair decision (a D-record with a live screen), not more sim.
* **H-SZ55 (0.35, new) — let the screen decide by map class.** Prediction for the live screen of C+D+E1p vs C+D:
  Schooltime score up by more than the summed loss on class-B open maps (Around UNSW, Australia, Islands). Falsifier: the
  pooled score minus expectation over all maps is ≤ 0. Size: the D-056 standard live screen. Suits Daichi/Asahi.

**RL translation.** Value: the last unit slot has a map-dependent value (high on cage maps, negative on cap maps) that
no observable at r0 reveals. A learned policy will face the same trade. The structural cue it might learn is "own
unit count stalls at the cap while a teammate never moves" — not available to any teammate under 7×7 vision.

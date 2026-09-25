# sinbad-v04-strike

- **Lineage:** Sinbad. **Parent:** `sinbad-v03-hunt`. Frozen experiment: `build/sinbad/exp/e14`
  with `reach_cap_crown = 3` (arena variant `e14@cr3`); this directory writes that value into
  `params.py` (identical play, checked on Colosseum).
- **Borrowed:** nothing.
- **Hypothesis:** (1) the trap penalty paralyses small dragons in lanes and crowded
  areas — a pocket that still holds the whole body is only a *soft* shortfall; (2) enemy
  crowns can be struck from further than our 3-step sprint candidates.

## Changes (from v03)

| Change | Layer | Evidence |
|---|---|---|
| no 3-step sprints for dragons of length ≥ 12; 2-step only with an enemy head within 3 (CPU) | decision | v03 sandbox max 81M was a 44-long crown evaluating 52 sprints; native replay peak 1.43 → 0.86 ms; outcomes ≈ v03 (82–26 vs 83–25) |
| two-tier trap: `w_trap_soft = 5` while the flood area still exceeds our length, `w_trap = 30` below it | decision | quick+quickT 78–30 → 84–24 (soft 12: 79–29) |
| **strike search**: BFS up to min(len−1, 6) steps onto visible enemy heads worth a trade; strikes pay no sprint cost (we die anyway) | decision | neutral off big maps once the crown-reach change below is removed |
| crown threat map treats an enemy running out of view as reaching 3 (`reach_cap_crown`) | features | reach 6 was tested: −7 fixtures off big maps (crown too timid) |

## Measured (native, both sides, deterministic fixtures)

| Set | v03 | **v04** |
|---|---|---|
| quick + quickT (108; ouroboros-v13, leviathan-v09, hunter-v22) | 83–25 | **84–24** |
| big + bigT (16; big_empty, schooltime, and transposes vs ouroboros-v13, hunter-v22) | 13–3 | **13–3** |

v04 by opponent (quick+quickT): ouroboros-v13 25–11, leviathan-v09 27–9, hunter-v22 32–4.
Big+bigT: ouroboros-v13 6–2, hunter-v22 7–1.
Per map (quick / quickT): arena 2–4 / 3–3, Colosseum 5–1 / 6–0, default_small 3–3 / 5–1,
devil 4–2 / 4–2, trophy 4–2 / 5–1, default 6–0 / 5–1, queen 6–0 / 6–0,
stronghold 6–0 / 4–2, trauma 6–0 / 4–2.

A sibling experiment (`e15`: long strikes only against heads ≥ 8, sprint cost kept for
small strikes, a long newborn claims the crown) scored 85–23 off big maps but 9–7 on
big+bigT, so it was not promoted.

## CPU (sandbox)

stronghold vs hunter-v22, full game, `unswbc run --sandbox -v` (15,609 of our turns):
p50 28.3M, p90 36.4M, p99 47.3M, **max 60.6M** points; no "exceeded CPU limit"
(v03 on the same fixture: max 81.1M). Only this one sandbox game was run.

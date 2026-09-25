# sinbad-v03-hunt

- **Lineage:** Sinbad. **Parent:** `sinbad-v02-crown`.
- **Borrowed:** nothing new (ideas only: dead-end farming and rear handoffs from the
  public-replay review; crown strikes from ouroboros' `crown_kill_round`).
- **Hypothesis:** the round-500 length race is decided by (a) whether our crown
  survives traps and (b) whether theirs survives us. Add escape splits with a
  crown handoff, farm-aware trap pricing, and a hunting behaviour for small
  foragers against the longest known enemy; stop portal collisions by sharing
  portal pairs.

## Changes (from v02, in the order they were tested)

| Exp | Change | Layer |
|---|---|---|
| e7 | **escape split** when every move dies (child keeps all but 2 segments); **crown handoff** packet sent back through our own body so the child becomes crown; **farm** pricing: a pocket whose visible pearls let us grow past `split_min` and whose depth our tail exceeds is priced at `farm_factor`·trap; unpaired-portal risk `p_dive` separate from `p_blind`; far targets steered through a **waypoint** inside the search instead of torus distance; crown claims need `claim_len` and are spread over 120 rounds | decision / macro / encoding |
| e8 | feeders die within 4; long dragons' flood need +L/3 (cap 40); others leave pearls within 3 of the crown from `crown_from` | decision |
| e9 | trap penalty × max(1, V(me)/v_ref) (the crown prices traps by what it carries); feeders avoid the crown's flanks | decision |
| e10 | **hunting**: every dragon records the longest enemy head it sees (PREY, relayed by sonar); from round 200, foragers of length ≤ 5 value its head at 1/segment | state / encoding / decision |
| e11 | **portal sharing**: every other turn one ray carries a known portal pairing (both edge keys + id), so one dive teaches the team | encoding |

## Measured (native, both sides, deterministic fixtures)

Pool: ouroboros-v13-ladder, leviathan-v09-arrival, hunter-v22-frontier-exploration.
`quick` = arena, Colosseum, default_small, devil, trophy, default, queen_of_spades,
stronghold, trauma; `quickT` = their transposes (`tools/ouroboros/maps/*_T`);
`big` = big_empty, schooltime vs ouroboros-v13 and hunter-v22.

| Set | v02 | e7 | e9 | e10 | **v03 (e11)** |
|---|---|---|---|---|---|
| quick (54) | 39–15 | 43–11 | — | — | **44–10** |
| quick + quickT (108) | — | 83–25 | 80–28 | 79–29 | **83–25** |
| big (8) | 3–5 | 4–4 | 4–4 | 7–1 | **7–1** |

v03 by opponent (quick + quickT): ouroboros-v13 24–12, leviathan-v09 29–7, hunter-v22 30–6.
Big maps: ouroboros-v13 4–0 (crowns 35–59 vs 34–53), hunter-v22 3–1.

Per map (quick + quickT): arena 2–4 / 3–3, Colosseum 6–0 / 6–0, default_small 5–1 / 5–1,
devil 4–2 / 4–2, trophy 5–1 / 4–2, default 6–0 / 4–2, queen 4–2 / 4–2,
stronghold 6–0 / 6–0, trauma 6–0 / 3–3.

Portal sharing, one default game vs ouroboros-v13: friendly head-on deaths ~20 → 1
(allies diving into the same unpaired portal from both ends).

## Remaining weaknesses

- arena (and arena_T): the opening race; no parameter tried (threat 0.5, split 8,
  p_long 0.5, γ 0.88, attack with 1 unit) did better than 4–8 of 12 fixtures.
- devil vs ouroboros-v13: its ladder swarm out-harvests us 4× on the 2-wide lanes.
- Crown safety at the very end (a 39-long crown died trapped at r493 in one game).

## CPU (sandbox)

stronghold vs hunter-v22, full game (16,044 of our turns): p50 28.3M, p90 36.5M,
p99 47.0M, **max 81.1M**, no "exceeded CPU limit". The maximum is the crown at
length 43–44 in rounds 455–461, when enemy heads near it make it evaluate 52
sprint paths, each copying its body and flooding 40 tiles. That is within the
limit but with little margin; the next version drops 3-step sprints for dragons
of length ≥ 12 (native replay of the same input: peak 1.43 ms → 0.86 ms).

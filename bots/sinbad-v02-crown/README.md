# sinbad-v02-crown

- **Lineage:** Sinbad. **Parent:** `sinbad-v01-core`.
- **Borrowed ideas (no code):** crown + feeding endgame and portal "dives" from the
  ouroboros line; farming/handoff concepts from the public-replay review.
- **Hypothesis:** v01's losses come from (1) trades it walks into, (2) never leaving
  walled bases, (3) no length conversion at round 500, and (4) — found while testing —
  judge CPU: v01's 1500-node searches exceed the 100M-point turn limit.

## What changed (layer by layer)

| Layer | Change |
|---|---|
| State | vacancy model for other bodies (segment i from the visible tail frees at our move i+2; chains running out of view `+t_hidden`); `cut` set of enemies longer than seen; sector bookkeeping of unseen tiles |
| Features | flood fill pessimistic on unknown edges (+`fcred` per rim cell, +`fcred_portal` per unpaired portal); threat reach uses hidden length |
| Decision | threat by length comparison (`p_long/p_eq/p_short`, `p_sprint`, loss = V(me) − ½V(them)); strike only strictly longer heads; portal risk: `p_blind`·V(me) for an unseen exit; dives into unpaired portals as exploration targets (never for the crown); newborn needs `child_area`; target search scores cells as discovered and stops when no farther cell can win |
| Macro | crown elected by relayed beacons (staggered claims, length margin 3), `lv_crown`; feeders within `feed_range` die next to the crown from `500 − 40 − 0.6(W+H)` |
| Encoding | 64-bit packets: tag, type, payload, 8-bit check. CROWN (x,y,len,round,id), FOOD (two pearls / due beds). Food gossip on rays not used by the crown beacon |
| CPU | target search cap 160 nodes (60 on a dragon's first two turns), no reverse search (first-move bitmasks), flood need ≤ 24, sprints only near enemy heads |

## Measured (native, both sides, deterministic fixtures, `tools/sinbad/arena.py`)

Quick set = arena, Colosseum, default_small, devil, trophy, default, queen_of_spades, stronghold, trauma.

| Opponent | v01 | **v02** |
|---|---|---|
| ouroboros-v13-ladder | 9–9 | **11–7** |
| leviathan-v09-arrival | 10–8 | **13–5** |
| hunter-v22-frontier-exploration | 13–5 | **15–3** |
| **total (54)** | 32–22 (0.593) | **39–15 (0.722)** |

Per map v02: arena 2–4, Colosseum 6–0, default_small 5–1, devil 4–2, trophy 6–0,
default 4–2, queen 5–1, stronghold 6–0 (crowns of 43–64), trauma 1–5.

Big maps (big_empty, schooltime) vs ouroboros-v13 and hunter-v22: 3–5 (v01 also 3–5);
0–4 against ouroboros-v13, whose crowns reach 45–67.

Ablations that shaped it (compact + default + queen, vs v13/lev09, 28 fixtures):
head_block=1 −8, p_blind 0.3→1.0 +5, min_area 10→5 +4, food gossip +3 (20–8 vs 17–11),
w_threat 2.0: 5–15 (vs 12–8 at 1.0).

## CPU (sandbox, `unswbc run --sandbox`, default map vs hunter-v22)

p50 26.9M, p90 33.2M, p99 40.7M, max 60.0M points per turn over 12,669 turns; no
"exceeded CPU limit". (v01 exceeded the limit on first turns and some later turns:
its results above are native only and would be worse under the judge.)

## Known weaknesses

- trauma (1–5): huge economy (40+ units by r250) but several small crowns in
  isolated clusters (rays stop at kelp), so the length is never concentrated.
- big maps vs ouroboros-v13: crown conversion 17–42 vs 45–67.
- arena: loses the opening race (2–4).

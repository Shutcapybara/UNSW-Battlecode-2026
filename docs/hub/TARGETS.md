# Targets — the analysts' current statistical goals (each analyst writes under its own heading; testers read)

Era column: `pre` = games before the live server adopted `unswbc 1.2.3` rules; `post` = after. Pre-era references are
in `docs/analysis/benchmarks/`; post-era references are published here as they stabilise.

## Director (seed; replaced by the analysts' sections)

| cluster / map | phase | metric | top-10 value | us (pre) | gap | era | query |
|---|---|---|---|---|---|---|---|
| all | r0–25 | total length vs same opposition (field SD) | +0.11 | −0.49 | 0.60 SD | pre | S-1 Q3 |
| all | r50 | same | — | — | 0.80 SD | pre | S-1 Q3 |
| all | r100+ | same | — | — | ~1.0 SD | pre | S-1 Q3 |
| all | r0–150 | transit ends in death within 3 rounds | 0.201 | 0.279 | +0.078 | pre | S-1 Q4 |
| all | r490 | round-limit losses with a material lead | 0.32–0.43 (cheji/Stockfish) | 0.33 (V06), 0.57 (hb1-12) | — | pre | TT concentration |
| all | r490 | **queen length / survival** | unknown | unknown | — | post | **analysts: first target to fill** |

## Nara (glm, P2-A)

**Era rule (unit 1, refined unit 2):** server switched in the 1 Oct 05:54–09:23 UTC window; I adopt the replay
lead's store tag (**post ⟺ started_at ≥ 2026-10-01T06:00Z**, equivalent — no games in the gap) and their
engine-verdict patch as the decoder fix (better than recomputing; my independent derivation agrees: 2,135 rl games,
0 violations). Queen = **original lowest-id initial robot, dead → 0, no inheritance**; then longest, then total.
⚠ Until the verdict patch lands, replay-extracted W-L-D is wrong in queen-decided games (8.2 % of rl games
queen-decided, 4.8 % flipped, full post sample).

**Post-era reference status: NOT stable** (58–132 field sides/map in my samples vs ~1,500 pre). Per-map pre→post
medians (unit 2, corrected): pearls@50 flat on most maps but **Schooltime +67 %/+171 %** at r50/r100 and
**Trauma ×4** at r50 (broad-based, not one team); Slithery −13 %; units@100 flat-to-down (median −3 %);
**own-goal deaths +12 % field-wide** (7/10 maps up 10–24 %) — tier-2 guards need era-matched baselines. Formal
re-derivation when the store rebuild + ≥300 games/map.

| cluster / map | phase | metric | top-10 value | us | gap / target | era | query |
|---|---|---|---|---|---|---|---|
| all | r0–25 | total length vs same opposition (field SD) | +0.11 | −0.49 (pre) | 0.60 SD | pre (carried) | S-1 Q3; post pending store |
| all | r50 | bed pearls ÷ field median | 1.07 | 0.83 (pre) | target ≥ 1.0 | pre (carried) | S-1 Q3; `tools/nara/opening_probe.py` |
| sparse/large (Schooltime, Trauma, QoS) | r50–100 | pearls ÷ field median | +67 %/+171 % (Schooltime, post vs pre field) | — | the era's economy mover; watch item until store volume | post (provisional) | unit 2 §2 table |
| all | r0–150 | own-goal deaths /1k dt | pre-era references stale (+12 % era shift) | — | compare vs era-matched parent only | post | `tools/nara/era_shift_probe.py` |
| **rl maps excl. pockets** (Portals, Trauma, Schooltime; NOT Slithery/Autarky/PD — H-Q3: queen dies r4–5 in a spawn pocket there, mechanically) | r490 | **queen survival** | field ~5 % (vol-weighted); Cutlery 26 % since 13:00Z | base 0.9–1 % (carthage-00) | **target ≥ 0.5** short-term (antioch's line), ≥ 0.9 for a full build; guard: econ LB > −0.03, elimination wins flat | post | `tools/nara/queen_probe.py` |
| rl maps excl. pockets | r490 | **queen length** (fed form) | Cutlery: 22 by r400, up to 65; field 0 | — | ≥ 1 beats every dead queen; **20–30 by r400** is the measured fed form | post | same |
| rl maps | r490 | **queen-decided losses** (ours dead, theirs alive) | — | — | target 0 | post | same (join index winner) |
| all | r490 | longest dragon | 40–46 (cheji/Stockfish, pre); post pending (rl-side samples too small yet) | 25–28 (pre) | post re-derivation when store lands | post-pending | TT method |
| all | r490 | round-limit losses with a material lead | 0.32–0.43 (pre) | 0.33 V06 / 0.57 hb1-12 (pre) | **< 0.10** with a kept queen | post | `tools/tt/endgame_gate.py` |

Design note from the field's reference build (unit 2 §4, mechanism in unit 3 §3): Cutlery's queen is **the crown
from birth** — moves 454/500 rounds, eats 30 pearls (field queen: 3), keeps production-splitting, grows 4→22 by
r400 — and the 13:00Z flip was simply **stopping the invalid-command cull** (65 % of its queen deaths pre-flip),
kept as a state-keyed cull on pocket maps only. No avoidance premium (exposure = teammates). The live arms:
crown-election-to-queen (N6) and queen-keyed enclosure avoidance (unit 3 §1: contact-map queens die to enemies,
corridor/pool-map queens die to geometry — match the mechanism to the map's hazard class; pocket maps: culling is
correct). Note: h2h length is not armor (victim longer 857 / shorter 496) — q_len's value is tiebreak margin and
queen-vs-queen duels, both rising as protectors appear.



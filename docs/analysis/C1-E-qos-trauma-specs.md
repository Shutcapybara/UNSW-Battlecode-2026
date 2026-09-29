# C1-E (b, c) — Queen Of Spades and Trauma, the next two levers, described from replays

Same method as the Schooltime spec: ten top-ten ranked wins per map, read from the cached frames
(`tools/analysis/c1e_qos_trauma.py`, raw dump in `build/c1e/qos_trauma_anatomy.jsonl`; pooled numbers below are
medians unless noted). Context numbers: `docs/analysis/C1-pace-targets.md`.

## (b) Queen Of Spades — the land-grab map

25×35, 2 initial dragons per side, 2 portal pairs, **472 live beds** (442 in the local file; use
`game_stats/live_beds.json`) with slow spawn rates (median 1.0/1000 rounds, 288 cells below 1/1000). The top ten
hold **74 % of cells at r100 and 92 % at r250** while the band sits at 49 % — territory *is* the strategy, and with
slow beds, territory means claimed bed clusters. h2h is the leading death cause (45 of 110 across the ten wins) —
this map is fought.

**The anatomy (ten wins, teams 306, 70, 801, 91, 264, 213):**

- Units 2 at r0 → 4 by r20 → 7.5 at r50 → 12 at r100 → 19.5 at r200. Splits run at a **steady 2–4 per decade from
  r10 to r100** — no Schooltime-style flywheel; production is paced by claiming, not by pearl intake.
- First pearl r8–15 (beds spawn from r0–6 and are eaten immediately — no Schooltime trickle).
- Children move 4–13 cells from birth, claim the next unclaimed bed cluster, and park: 78–100 % of heads sit within
  2 of a bed at r100; 14–42 % of the 472 beds are covered by ~12 heads. Nearest allied head median 3–6 cells.
- The two portal pairs are covered early (1–2 of 2 within 3 from r25) and transited 8–20 times per 100 rounds —
  QoS's portals connect the halves and are part of the claim route, not an afterthought.

**The takeover mechanic:** the band parks on its own half (49 % forever). The top ten's children keep claiming
*across the midline* once the home half is seeded — by r250 they hold 92 % of cells, i.e. they eat the opponent's
bed field out from under them and win by elimination/starvation. Team 7 already matches the headcount (12 units at
r100 vs the top ten's 11, n=5) — our gap on QoS is not production, it is that our 12 heads stay home.

**Spec for C1-B:** steady split cadence (~3/decade), child claims nearest *unclaimed* bed cluster with no midline
bias once home beds have heads, portals usable on claim routes, expect to fight for the far half (h2h deaths are
the cost of doing business; newborn deaths 2–12/100 births).

## (c) Trauma — the late-compounding map

48×24, 2 initial dragons per side, 6 portal pairs, **142 beds** (local file matches), enclosed share 0.42 — the
highest of the pool: corridors box dragons in. Top ten: 16 units at r100 vs the band's 8 (splits 29 vs 12), and
**46 units by r200** — Trauma compounds late. Territory stays 50/50 for every cohort (0.50 at r250): nobody owns
the map; it is pure production and survival. Team 7's collapse map (6 units at r100, n=3, splits 7).

**The anatomy (ten wins, teams 264, 70, 213, 20, 249):**

- Units 2 → 4 at r5 (both starters split immediately) → flat 4–5 until r40 → 7 at r50 → 11 at r70 → 18.5 at r100 →
  **46 at r200**. The curve that looks like a modest r100 lead is a doubling machine that has not finished; the
  real gap opens after r100.
- Splits: 2 at r0–10, then 2–5 per decade from r40. first_spawn r0 in every game; first pearl r11–36 (median ~19).
- **Invalid-action deaths dominate: 97 of 110 deaths** across the ten winning sides (24, 21, 27 in the heaviest
  games) — dragons boxed in corridors die with no valid move, and the winners *accept this churn* and keep
  splitting. Wall/body/h2h deaths are almost absent (7/1/5). This is the opposite lesson of C1-D's portal
  discipline: on Trauma, enclosed-death churn is the price of density.
- Children travel 2–22 cells (median ~7); portal use splits the winners (24/19/19 transits in three games, 3–9 in
  the rest) — 3 of 6 pairs covered. Heads park on beds less than elsewhere (38–90 %, median ~56 %) — more mobile,
  more corridor-patrol.
- Crowns: none by r100 (as on Schooltime and QoS).

**Spec for C1-B:** split starters at r0 (2→4), hold ~4 units until pearls (r19), then split continuously
(~3/decade) *without* waiting for safety — budget for enclosed/invalid losses (up to ~2/decade at the top) and
out-replace them; the r100 target is 16 units but the win condition is the r200 curve (46). Do not chase territory
on this map; it cannot be held.

## Caveats

Ten wins per map, six and five distinct teams respectively, version mixing as everywhere post-D-023; QoS territory
percentages come from the pace table (F1 territory feature, start-of-round snapshots); Trauma invalid-death counts
are engine cause labels (no valid action — includes boxed-in; TLE is counted separately and is near zero for these
sides).

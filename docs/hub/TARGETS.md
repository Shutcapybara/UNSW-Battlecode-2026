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

## antioch (Claude analyst, replay lead) — 2026-10-01 22:45 ACST

Source: `docs/findings/2026-10-01-antioch-era-and-queen.md`. Era `post` = started ≥ 2026-10-01 06:00Z. Post-change n is
small (1,603 games, 308 top-ten side-games) and five of the top ten have **no** post-change games yet, so every post value
below is **provisional**.

**Endgame and queen** (post, field side-games; round-limit = RL; the queen is the original lowest-id dragon):

| cluster / map | phase | metric | field | top-10 | us | target | era | query |
|---|---|---|---|---|---|---|---|---|
| RL maps exc. Slithery (Portals, Trauma, Schooltime, Default, QoS) | r500 | **queen alive at the end of RL games** | 0.022 | 0.007 | — | **≥ 0.5** (H-Q1 falsifier); each kept queen wins 98 % of RL games outright today | post | queen.py, end_reason = 1 |
| all | r0–150 | queen death round, median | r41 | r41 | — | no queen death before r150 except pocket maps | post | queen.py |
| Slithery, Autarky, PD | r0–5 | queen alive | 0.000 | 0.000 | — | **none possible**: spawn pocket, dies r4–5 (H-Q3 falsified); tiebreak there = longest → total | both | queen.py + probe |
| all | r490 | queen length when alive (RL) | median 10.5 (p75 ~20) | n/a | — | > opponent queen; today any length ≥ 2 suffices (98 % of opponents' queens are dead) | post | queen.py |
| all | r500 | RL losses with a total-length lead | 0.347 | **0.511** | — | ≤ 0.25 (pre-change field was 0.241) | post | queen.py |
| all | r500 | RL win rate | 0.53 | 0.691 | — | — (report it; the gate's win share is old-rule until the frame patch lands) | post | queen.py |
| all | r500 | longest at end (RL), median | 28 | 42.5 | — | ≥ 42 (top-10) | post | queen.py |
| all | r500 | total at end (RL), median | 70 | 98 | — | ≥ 98 (top-10); *map pool changed at the switch, compare on the ten ladder maps only* | post | queen.py |


**Win potential Φ (shaped-reward and early-game benchmark; replaces tempo as the opening guard proposal).** Opponent-relative
shares (total, longest, pearls, territory, deaths), two regimes, no map identity; LOMO AUC at r50 0.86 (elimination maps) /
0.63 (round-limit maps), calibrated; tempo-family own-income AUC 0.64. Coefficients `tools/antioch/phi_post_v1.json`.

| regime | phase | metric | top-10 | r11–30 | field | target | era | query |
|---|---|---|---|---|---|---|---|---|
| elimination maps | r50 / r100 | mean Φ | 0.632 / 0.698 | 0.580 / 0.606 | 0.5 | ≥ top-10 | post | value_target.py |
| round-limit maps | r50 / r100 | mean Φ | 0.546 / 0.570 | 0.522 / 0.535 | 0.5 | ≥ top-10, and the queen (Φ adds `queen_diff` from r250) | post | value_target.py |

**Opening, post-change (S-1 Q3's components; 2,862 post-change corpus games, ten ladder maps).**
- **Field stability at r50:** the 90 % half-width of the field median is ±4–5 % (bed pearls, splits, total) and ±12 %
  (transits). The top-ten percentile is known to ±8 points (about 87 top-ten side-games per map, only 5 teams); ±5 needs
  ~220 per map.
- **The field did not move:** post/pre field medians are 1.00 at r25 and r50 for every component (transits +10 % from
  r100; Trauma and Schooltime +9–20 % at r50). Pre-change opening references stay valid to r50 (agrees with nara N3).
- **"us"** is carthage-00-base's 1.2.3 pool panel (480 side-games), normalised against the post-change field. Its
  opponents are panel bots, so the absolute values are indicative and arm-to-arm deltas are what count.

| component | stat | r25 top-10 / us pctile | r50 top-10 / us pctile | top-10 − us (z) r25 / r50 / r100 | era | query |
|---|---|---|---|---|---|---|
| early portal use | transits (cum.) | 0.79 / 0.56 | 0.67 / 0.47 | **0.69 / 0.56 / 0.41** | post | opening_refs.py table |
| bed conversion | bed pearls (cum.) | 0.68 / 0.60 | 0.66 / 0.56 | 0.23 / **0.31** / 0.21 | post | same |
| | bed capture | 0.60 / 0.60 | 0.62 / 0.61 | 0.21 / 0.21 / −0.02 | post | same |
| production | splits (cum.) | 0.68 / 0.79 | 0.70 / 0.59 | 0.13 / **0.28** / 0.26 | post | same |
| territory | BFS territory | 0.59 / 0.62 | 0.66 / 0.68 | −0.09 / −0.15 / −0.21 (we lead) | post | same |
| outcome | total length | 0.69 / 0.67 | 0.67 / 0.61 | 0.14 / 0.18 / 0.13 | post | same |
| | units | 0.74 / 0.79 | 0.68 / 0.76 | −0.12 / −0.01 / −0.03 | post | same |

**Reading:**
- Phase 1's opening gap (total 0.80 SD at r50 for the live bot) is mostly closed by the prior base: 0.18.
- What remains is portal use first, then bed pearls and production at r50.
- Targets: transits@50 at the top-ten percentile (0.67) without raising transit died3. That is H-S1's job: portal memory
  makes the extra transits safe.

**Disagreement slots:** none yet.


## <analyst lineage B>

## <analyst lineage C>

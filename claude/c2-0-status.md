# C2-0 — fight anatomy from the corpus: status

**Delivered 29 Sep 2026 (GLM 5.3 session). Analysis only — no bot, no protocol design.**

## Deliverables

- `tools/analysis/features/fights.py` — contact/fight event detector on F1 frames (extend, don't fork: reuses
  `frame.decode`/`frame.load`, c1e_pace's ladder joins). CLI: `extract` (multiprocess over replays →
  `fights.parquet`) and `report` (cohort aggregation → md + json).
- `build/c2-0/fights.parquet` — 182,788 contact events over 10,331 of 10,340 ranked completed corpus games
  (16 workers, ~19 min, 0 failures; 9 games have no cross-team contact at all).
- `docs/analysis/C2-fight-anatomy.md` + `game_stats/fight_anatomy.json` — tables, reading, caveats.
- Cohorts as in C1-E (ladder snapshot nearest game start): top10 n=1913, r11_30 3110, band 6541, team7 114
  side-games.

## The answer to §0 (one paragraph)

The top ten do **not** fight differently in any observable coordination sense: they fight at the band's rate
(8.96 vs 8.58 group fights per side-game), converge before contact at the band's rate (heads-toward-centre
0.29 vs 0.27; ≥2 convergers 83.6% vs 80.6%; synced entries ~23% both; pre-fight rays 2.7 vs 2.5/head), and at
matched unit parity they initiate at the band's rate (50.3%/50.2% vs 50.9%/45.0% at even/behind). Their pooled
+3.7pp initiator edge is composition — they arrive **ahead in units** at 53.6% of fights vs the band's 44.8%.
The real separations are pricing and conversion: trade-while-ahead 55.1% vs 44.2%; net kill balance +3.5pp vs
−0.4pp; next-10 pearl swing +1.08 vs −0.81; and they refuse fights far from beds (initiate 38.5% vs band 54.8%
when nearest bed > 6 cells). **S-3 verdict: a pricing rule, not a protocol** — drop the leader-nomination
protocol; the falsifier fired on convergence (identical) and on initiation at matched parity (identical).

## Team 7 specifics (the "which of the two do we lack" answer)

We lack neither initiation (48.3% vs band 49.9%, n=114 side-games, CI ±10.5) nor appetite (7.55 vs 8.58 fights
per game). Our two measured gaps: **reinforcement** (convergence 0.18 vs 0.27 pooled; 0.12 vs 0.22 on compact
maps, where we initiate only 36.8% of group fights) and **cost** (11.6 own deaths and 32.9 length lost per fight
vs the band's 6.8/18.9 — our fights are twice as bloody, matching the C1-C trapped/newborn leak picture).
Actionable without any protocol: a local engage rule — converge ≥2 heads before contact or refuse it; never
trade when behind in units; treat fights >6 cells from a bed as not worth initiating.

## Numbers that decide (see the md for the tables)

- Parity-at-contact decomposition (the confound-killer) — top10 ahead 53.6% / band 44.8% of fights; at even
  parity initiator 50.3% vs 50.9%.
- Conditional win: fight outcomes move the top ten (+8.7pp fights-won vs fights-lost) but their best bucket is
  games with no group fights (70.9%); band/r11-30 flat everywhere — fights don't decide non-top-ten games.
- 2v1 contacts are rare (~0.3/side-game): no gang-hunting behaviour anywhere in the field.

## Caveats (full list in the md)

Manhattan distances (portals unfollowed — can only hide contacts, identical bias); adjacency from post-move
positions incl. death cells; participant deaths within last-contact+5 can be double-claimed by overlapping
events (~60% of all deaths are event-participant deaths on a 30-game check); team-7 parity cells are n=9–43;
beds observed from spawn events (live-true, sparse-bed caveat); no submission ids (D-023).

## What next (for the director, not for this task)

If S-3 proceeds at all, it proceeds as two `params.hpp`-style rules on the C1-A chassis (engage pricing +
converge-or-refuse), not as messaging. Anything protocol-shaped should wait for a payload-decoding study of the
teams that DO send fight-direction messages — this corpus study can only see movement, and no movement
signature distinguishes the top ten.

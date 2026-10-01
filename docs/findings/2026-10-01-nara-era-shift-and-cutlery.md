---
id: nara-era-shift-and-cutlery
author: glm/nara (P2-A analyst)
kind: measurement
title: Unit 2 — the era shift anatomy (deaths, economy by map), the Cutlery queen build, and a correction to unit 1
task: P2-A second unit
evidence: tools/nara/{era_shift_probe,opening_probe,queen_probe}.py; build/nara/{shift_pre,shift_post,open_pre,open_post,queen_cutlery}.jsonl (main checkout)
sample: pre 30 Sep 00:00–05:54Z, post 1 Oct 09:23–15:50Z; per-map n≥10 both eras; full post in-scope corpus for the queen rule check (3,978 games)
---

# 1. Correction to unit 1

`opening_probe.py` measured body length as `len(body[1])` — a coordinate tuple, always 2 — so unit 1's
`total@100` column was **2 × units**, and the pooled "+12.2 % total@100" was a units shift with a wrong name, and
composition-biased with it. The per-map cut with the fixed probe: **units@100 is flat to slightly down** (−16 %
Default, −13 % Devil, −9 % Autarky/Portals/Trauma; +29 % QoS, +12 % PD; median ≈ −3 %), longest@100 flat (4→4).
Pearls and splits columns were event-based and stand. Unit 1's queen columns are unaffected (different code path,
verified against the result block).

# 2. The era shift, per map (field = top-50 sides pooled, n 16–132 per map per era)

**Own-goal deaths rose ~+12 % field-wide** (wall+self+body per 1k dragon-turns to r150): up on 7/10 maps
(Portals +23 %, Schooltime +23 %, Trauma +24 %, Slithery +20 %), flat-to-down on Default/Devil/Trophy.
Cohort cut: top10 wall 4.8→8.8 (+83 %), self +53 %, body +56 %, h2h flat; rest50 wall +46 %, h2h +48 %.
The pre-era rates match the S-1 references (top10 own-goals ≈ 10/1k), so this is a genuine post-switch jump, not a
sample artifact. Mechanism (hypothesis, N5): multi-step moves are now free for L≥5, the field's bots propose more
of them (rest50 moves≥2 steps share 0.11 %→0.81 %), and a 2-3 step move that only checks its destination dies on
the mid-cell. **Testers: tier-2 guards on 1.2.3 panels will read high against stale pre-era references — compare
against era-matched baselines.**

**Economy split by map geometry.** Sparse/large maps up hard, dense/fast maps flat-to-down:

| map | pearls@50 | pearls@100 | own-goal deaths |
|---|---|---|---|
| Schooltime (2,400 tiles) | +67 % | **+171 %** (31→84, broad-based: 5+ mid teams at 60–127; not one farm) | +23 % |
| Trauma | **+288 %** (4→16, tiny base) | +35 % | +24 % |
| QoS | +18 % | +6 % | +10 % |
| Portals | +10 % | +11 % | +23 % |
| Slithery (fast/dense) | −14 % | −13 % | +20 % |
| Default | −9 % | −30 % | −10 % |

Interpretation (N4): free sprints turn movement into income where beds are far apart (Schooltime/Trauma/QoS) and
into collisions where the swarm already saturates (Slithery). The endgame material columns (longest@490 etc.) are
not yet comparable — my rl-side subsamples are too small (n 19–86); the store rebuild closes this.

# 3. The queen rule, verified at full scale

All post-era in-scope games (3,978 games, 7,956 side-rows, 09:23–15:50 UTC): **2,135 round-limit games, 175
(8.2 %) decided by the alive-vs-dead queen, 102 (4.8 %) against the longest-dragon order, zero violations** of
`queen (original lowest-id initial robot, dead→0) → longest → total`. Standing reference numbers for TARGETS.

Volume-weighted queen survival (all games / rl-only): top10 7.4 %/4.4 %, r11–30 4.6 %/1.0 %, r31–50 5.1 %/3.5 %,
other 5.7 %/6.4 %. Antioch's 0.7 % top-10 RL figure and mine reconcile by window + weighting: their analysis cut
off before Cutlery's 13:00 UTC submission (below) and the field's survival was ≈2 % before it.

# 4. Cutlery deployed queen play to its ranked bot at ~13:00 UTC

Team 306 (rank 1), all 146 post-era games decoded:

| start hour (UTC) | ranked surv/n | unranked surv/n |
|---|---|---|
| 11 | 0/15 | — |
| 12 | 1/47 | — |
| 13 | **8/32** | 4/9 |
| 14 | **6/23** | 3/11 |
| 15 | 1/9 | — |

- Survival 0 % → ~26 % from 13:00 in **ranked** games (real opponents: 213, 98, 798, 147, 801, 46) — a submission
  flip, not A/B testing.
- **Queen-alive games won 20/23 (87 %) vs 51 % (63/123) queen-dead** (n small, but the direction is loud).
- Queen length at r490 is bimodal: {3,4,4,4,5,9} (parked) and {15,17,18,20,22,23,26,27,29,31,32,34,39,40,44,48,65}
  (fed — up to 65, i.e. also the crown). Cutlery plays both forms.

**How it plays (23 queen-alive side-games, 8 fully re-walked):** the queen is **not parked — it is the crown from
birth**. Median 454 head-move rounds of ~500 (moves nearly every round), **median 30 pearls eaten** (field queen
median: 3), still production-splits (8 splits in 8 games, 3 before r150), grows 4 → 5.5 → 13 → 16 → 22 through
r50→400 (alive-game medians; the dead-queen games have it gone by ~r50–100). So Cutlery elects its lowest-id dragon
as the primary forager/crown and keeps it alive through play, not by hiding it.

**Direct implication for the H-Q1 arms (carthage, kyoto):** the arms that make the queen small, cautious or
split-less are the opposite shape — Cutlery's form keeps the queen *valuable* (fed crown, first tiebreak secured
with margin) rather than merely *alive*. The untested arm is "queen as crown-candidate from r0 with normal safety
pricing", not "queen as protected passenger".

# 5. Hypotheses proposed (director applies to the ledger)

| id | hypothesis | weight | falsifier / size |
|---|---|---|---|
| N4 | **Mobility-economy regime**: free sprints make distance cheap; opening value shifts toward coverage on sparse/large maps (Schooltime +171 %, Trauma ×4 at r50) and toward mid-cell path safety everywhere. Mechanisms: structure-keyed sprint openings (area/bed-density at init); whole-path safety pricing for multi-step moves. | 0.5 | Store rebuild at volume (>200 sides/map) erases the Schooltime/Trauma gains; bot test: sprint-opening arm on Schooltime-like gen maps wins ≥ +3 pp at equal deaths. |
| N5 | **Own-goal era tax**: the +12 % own-goal rise is mechanical (mid-cell collisions in now-free multi-step moves); pricing the full stepped path (intermediate cells, not just destination) recovers it. Explains why carthage-06's saved head-ons returned as trapped deaths. | 0.6 | A 1.2.3 panel arm with mid-cell safety cuts wall+self ≥ 20 % at econ flat; if the field's rates fall back to pre-era levels as teams patch, the window closes (re-check weekly). |
| N6 | **Queen-crown unification**: elect the *queen* as the crown **from r0** and feed it through the opening (Cutlery's measured form: 454/500 move-rounds, 30 eats, splits intact, length 22 by r400) rather than protecting a parked queen. Vs dead-queen opponents the first tiebreak alone wins; vs adapted opponents the queen-crown leads queen AND longest simultaneously. Merges H-Q1 with L39 and inverts the "hide the queen" arms. | 0.65 | carthage-08-style stack + crown-election retargeted to the queen from r0 vs crown-to-longest, RL-win LB > 0 on rl maps with econ LB > −0.03 (pocket maps excluded from the survival target, kept in the econ guard); downweight if the queen-crown carrier loses more eliminations than the verdicts gain. |
| N7 | **Adaptation decay** (reading, folded into N2's motivation): H-Q1's measured value (8.2 % of rl games queen-decided today) is an upper bound that decays as the field adopts protection — Cutlery went first at 13:00 UTC. Ship protection fast; start queen-hunting (N2) research now — its value rises symmetrically. | — | Weekly re-derivation of queen-decided share; when it exceeds ~15 % of rl games, hunting becomes the higher-EV lane. |

# 6. Reading of the testers' queen results (carthage-01/02/06/07, kyoto-02 pending)

- The four rejections are consistent with one mechanism story: single levers fail because the hazard is two-sided
  (carthage's own reading at 00:55: ally kills ≈ enemy kills once head-ons are removed). The stack (carthage-08)
  is the right next point, and Cutlery's replays shortcut the search space.
- On carthage's gate question (econ-led D-032 vs queen verdicts): my reading — judge queen arms on **RL-win LB > 0
  pooled across both panels with econ LB > −0.03 as guard**, per antioch's falsifier, with the per-regime split
  printed; exclude pocket maps (Slithery/Autarky/PD, H-Q3: the queen dies r4–5 regardless) from the *survival*
  target but keep them in the econ guard — any protection machinery that fires there is pure cost. The win-LB
  framing already exists in `tools/tt/endgame_gate.py`.
- carthage-04 (sprint pricing fix, pool win +0.040) is correctly called a neutral correctness fix — it should be
  carried into every later arm as a base property, not an arm.

# 7. Reproduction

```
python tools/nara/era_shift_probe.py --since "2026-09-30T00:00" --until "2026-10-01T05:54" --per-team 8 --out build/nara/shift_pre.jsonl
python tools/nara/era_shift_probe.py --since "2026-10-01T09:23" --per-team 8 --out build/nara/shift_post.jsonl
python tools/nara/queen_probe.py --since "2026-10-01T09:23" --per-team 999 --out build/nara/queen_cutlery.jsonl
```

---
id: 2026-09-28-sakura-s01-swarm-dissolve
author: glm/sakura/s01
kind: design
title: "Sakura S1: swarm-then-dissolve on the five-layer framework — build findings and the first 2x2"
task: "generation S1 build prompt (JKS director, 28 Sep 2026): one bot end to end, metered, contract-passing, honest paired numbers"
supersedes: ""
evidence:
  - docs/findings/sakura-s01-data/panel-{ctrl,prod,diss,both,extras,nocert}/results.jsonl (unswbc 1.2.2, --seed 1, ten live maps, both sides, 8-opponent reference pool)
  - docs/findings/sakura-s01-data/cp1-sandbox/results.jsonl (20 seeded sandbox games, schooltime vs sinbad-v07)
  - docs/findings/sakura-s01-data/cp2-fry/results.jsonl (checkpoint-2 acceptance vs fry-v14, 15-5)
  - tools/sakura/{panel,funnel,probe}.py (all numbers reproducible)
---

# Sakura S1 — what was built, what fired, what s02 should change

## What was built

`bots/sakura-s01-swarm-dissolve` (lineage_parent `ouroboros-v10-beacon`), one
file + `params.py`, every macro knob a map-conditioned parameter:

- **Production (H-prod).** `SPLIT 2` at `split_min_len=4` to a map-scaled cap
  `max(18, NC/unit_target_cells)` with `unit_target_cells=24`; λ_unit full to
  `produce_until=100`, decaying linearly to `produce_stop=380`. Swarm-push gates
  relax (`split_crowd_early=16`, `split_danger_early=0.45`) while under half
  target pre-r100. (64-on-512-cells measured 11.7 self-deaths/1k turns — a
  parking lot; NC/24 halved deaths and lengthened the crown.)
- **Salvage (deterministic, Vibing++ rule).** Every first step lethal → `SPLIT
  L−2` if L≥4 and under cap; head-on trade if an enemy head is adjacent with
  their loss ≥ ours; else the cheapest death (into our own body, pearls stay
  together). Includes a bug fix over the host: `emergency_split` now works with
  spawn-truncated trails (bodies longer than the 7×7 view) — v10 refused and
  died (dilemma's sealed corridor killed the 11-length spawn at r2 that way).
- **Crown + dissolution (H-dissolve).** Election from r250, id-staggered,
  relayed beacons with demotion (v10 machinery). Onset by map signature (no map
  name is given): **r300** when 63×27 (Slithery Fight, unique among live maps)
  or 512 cells with ≥6 portal pairs (Portals; Default has 6 pairs but is
  32×32; Dilemma/Devil share 512 with ≤2 pairs), **r400** elsewhere. From
  onset, L≤3 dragons within 30 escort the crown; at distance 1 they dissolve
  (move into own body) only when `recipient_eats_first` holds: crown belief
  fresh ≤2 rounds, a corpse-pearl cell adjacent to the crown head, and no
  fresh enemy within 3 of the crown.
- **Birth certificate (H-cert).** `K_CERT` (v1) on the backward ray at every
  split: tag+chk 12 | ver 4 | role 3 | phase 2 | target 12 | crown-id 16 |
  crown-len 7 | parent 8 — exactly 64 bits. Delivery verified: children log
  `ACT:cert` on their first turn (28–172 per game).
- **Momentum.** Target cache `hysteresis_margin=2.0`, TTL 12; switches logged
  `ACT:sw`. Trace markers in the one buffered write per turn:
  `ACT:prod|salv|crown|diss|esc|cert|sw`.

## The 2×2 (the experiment the self-audit asked for; nobody had run it)

unswbc 1.2.2, `--seed 1`, ten live maps, both sides, the 8-opponent reference
pool, paired by (map, side, seed, opponent); control = ouroboros-v10-beacon:

| arm | record | score | pairs better/worse/equal | net | sign-p |
|---|---|---|---|---|---|
| control (ouroboros-v10) | 63–77 | 45.0% | — | — | — |
| prod only | 52–108 | 32.5% | 7/29/104 | −22 | 0.0003 |
| dissolve only | 58–100 | 36.7% | 13/28/97 | −15 | 0.0275 |
| both (shipped) | 53–106 | 33.3% | 9/27/103 | −18 | 0.0039 |

Two extra attribution arms on the four most regressed maps (trauma, slithery,
portals, devil; 56 pairs each vs control):

| arm | better/worse/equal | net | per-map deltas vs control |
|---|---|---|---|
| extras only (no prod, no dissolve) | 2/18/36 | −16 | slithery −5, trauma −5, portals −3, devil −3 |
| both minus cert | 3/21/32 | −18 | slithery −5, trauma −6, portals −3, devil −4 |

**Attribution:** the framework strip — no scout/hunt roles, no voluntary
strikes, no v10 L≤20-from-r400 feeding — accounts for essentially the whole
regression on portal-heavy maps (the extras-only arm reproduces it). The
swarm and dissolve clocks themselves are close to neutral (prod adds a
further −2 on slithery; dissolve's only win is default +2). Control's
strength on these maps is exactly what the framework banned: v10's scouts
dive portals and learn the map's connectivity, hunters trade, and every
L≤20 dragon feeds the crown from r400.

Full 3-seed panel deviation: since no arm beats control at seed 1
(sign-p ≤ 0.03 for all three), the full panel on "the winning arm" was not
run — 960 more games would only sharpen a negative. Seed-1 full panels on
all four arms stand as the record.

## Which falsifiers fired

- **H-prod: half falsified.** units_r100 map-median 18.5 (floor ≥15 and
  target ≥18 hold in aggregate) but <15 on dilemma (6), queen_of_spades (6),
  trauma (5); wall/self deaths 5.19/1k dragon-turns in aggregate (>5
  falsifier), 29.5 on portals, 14.6 on slithery. Production works where
  pearls are reachable; the boxing deaths and the three starving maps are
  economy failures, not clock failures.
- **H-dissolve: falsified.** longest_r400 map-median 3.0 vs the ≥18 target
  and vs the base host's 3.0 — no conversion by r400. The swarm does not bank
  length (pearls eaten median ~300 per game per team across 500 rounds).
  The funnel (8 kept games on portals + slithery, seeds 1-2, both sides vs
  sinbad-v07): eligible-after-onset 2.4k/9.0k dragon-rounds → ACT:diss 0–8
  (portals) / 33–47 (slithery) → delivered 0–1 / 1–5 → **crown survived to
  the end 8/8 (recipient survival 100% ≥ 50% — the only H-dissolve bound
  that holds)** → final longest 13–26 / 26–28. units_r250 27.5 in the
  dissolve arm vs 13.5 control: it holds units, not length.
- **H-cert: falsified as an outcome lever.** Delivery works (children read
  the certificate), but newborn-deaths-per-100-births 32.1 (on) vs 31.5
  (off) and first-pearl round 16 vs 16 on identical fixtures — no movement.
  Retained: it is free and carries the phase bit that lets newborns escort
  from birth.

## Findings the prompt did not ask for

1. **Dilemma is a trap map.** Fertility: sealed 1-wide kelp corridors x=14 /
  x=17 with gap-1 firehose farms. Any dragon on a sealed path corridor dies
  at its ends (no turnaround in 1-wide); split-cycling only delays. The real
  field pearls are the x=10..21, y=3..12 diamond (gap 250), but field dragons
  spawn at x≤6 / x≥25 and starve en route. Sakura fields ~2–6 units at r100
  there; control fields 2. Both lose the map to the field-strong bots.
2. **Boxing salvage is the dominant self-death source** (portals ≈ 30/1k
  dragon-turns vs fry; ACT:salv own-body moves, not parser accidents: 0
  `noValidAction` in 100+ team-games incl. 20 sandbox). It scales with our
  own swarm density — the NC/24 cap is the measured dial.
3. **LOG lines reach the replay as per-dragon events on both toolkits**
  (`EventDragonLog{id,text}`); two LOG lines in one turn both survive. The
  activation contract is parseable with the repo capnp schema.
4. **Edge semantics of the live maps**: `EDGE a b tok` with `-1` = open (not
  kelp), integer = portal id; the ten live maps have essentially no kelp
  except maze maps (dilemma). The v10 vision parser matches the official
  protocol docs (8×7 north-edge rows + south-of-last-row; 7×8 west-edge
  columns + east-of-last-column).
5. **Sinbad-v07 runs the target swarm-crown game** (64 units by r125, L60
  crown by r175 on schooltime) and beats control 14–6 and every sakura arm
  worse; yuna-v02-core beats control 18–2. The pool's top is well above the
  v10 host — sakura's paired deltas are against a strong incumbent.

## What s02 should change

1. **Restore portal exploration inside the framework** — a `reposition`-level
   portal-dive bias for gatherers on portal-pair-rich maps (or an explicit
   `explorer` weight slice, not a scout role): the extras-only arm shows the
   portal maps are where v10's scouts earned their keep. This is the single
   biggest paired regression (slithery/trauma/portals).
2. **Feed the crown with more than L≤3 stragglers**: dissolve-only's default
   +2 came from conversion; but longest_r400 3.0 means the crown starves.
   s02 should raise `feed_max_len` toward v10's 20 on open maps (funnel
   numbers first), and/or bank crown length earlier via `crown_min_len`.
3. **Economy before clocks**: the family's standing gap (HANDOFF 5.2:
   hunter-grade opening economy) is what the three starving maps and the
   300-pearls-per-game totals expose. Bed pre-positioning and contested-pearl
   appetite (v10's own_disc/zonedanger) are the levers, not the onset round.
4. Keep: deterministic salvage (with the truncated-trail fix), map-scaled
   swarm cap, map-signature onset, ACT contracts, certificate (free),
   hysteresis margin as a tuned dial (ACT:sw is still high on portal maps).
5. Measure first: the funnel before moving any clock (per the brief), and
   the extras arm as the s02 control.

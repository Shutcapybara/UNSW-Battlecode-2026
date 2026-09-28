---
id: 2026-09-28-kazuha-s01-swarm-dissolve
author: glm/kazuha/s01
kind: design
title: "Kazuha s01: swarm-then-dissolve on the five-layer framework"
task: "S1 build prompt (director, 28 Sep 2026): one bot, five layers, swarm production + map-conditioned adjacent dissolution + birth certificate, with 2x2 ablation and a metered profile."
supersedes: ""
evidence:
  - "bots/kazuha-s01-swarm-dissolve (CANDIDATE.toml, README.md)"
  - "experiment_data/kazuha-* (compare_bot runs, seeded fixture_hash_v1, unswbc 1.2.2)"
  - "game_stats/runs/ (ledger publication)"
---

# Kazuha s01 — swarm-dissolve

(filled at delivery; numbers below are placeholders until the panel completes)

## What was built

- Host: ouroboros-v10-beacon (parser, exact step simulation, sonar packing, goal
  field, safety scoring). Policy layer rewritten on the five layers.
- Strategy: `V = lam_unit*units + lam_len*sum(len) + lam_crown*(ourLongest-theirLongest) - risk`;
  lam_unit 1 to r100 decaying to 0 at 380; lam_crown rising from 250 to the onset;
  lam_ctrl = 0 (hook only). Roles: gatherer + elected crown. No scouts, no hunters,
  no density gossip.
- Production: SPLIT 2 toward the 64-unit cap while lam_unit > 0 (crowd gate relaxed
  to 14 during the opening); split_min_len 4; deterministic salvage (SPLIT L-2 when
  boxed, trade when an enemy head is adjacent, cheapest death aimed at allies).
- Conversion: crown elected from r250 (stagger (id*7919)%120, demote 3, beacon ttl 3);
  from a map-conditioned onset — r300 when width==63 (Slithery Fight) or <=625 cells
  with >=6 portal pairs discovered (Portals), else r400 — dragons with L<=3 within
  30 route of a fresh crown escort it (ACT:esc) and dissolve (move into own body,
  ACT:diss) only when adjacent AND a corpse pearl sits one step from the crown head
  (recipient_eats_first).
- Birth certificate (K_CERT): proto4|role3|phase2|target12|crownId16|crownLen7|parent8,
  sent on the backward ray at every split; the child reads it on its first turn
  (delivery verified empirically: 107 backward-ray pings hit children on their first
  turn in the smoke game; 54 valid certs read).
- Hysteresis: sticky target with margin 1.0 length unit; ACT markers: prod/salv/
  crown/diss/esc/cert.

## Falsifier outcomes

(filled at delivery)

## 2x2 (paired vs control on the same seeded fixtures)

(filled at delivery)

## What s02 should change

(filled at delivery)

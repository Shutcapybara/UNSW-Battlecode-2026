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

## Falsifier outcomes (measured)

- **H-prod: PARTIAL FAIL.** Units at r100 ≥ 18 holds vs ladder-tier opponents
  (fry: 51 on schooltime, 55 on slithery, 20-23 on portals) but **not against
  the strong panel** (median 14, same as control — strong opponents contest the
  pearls). The survival clause fails on portal-dense maps: portals mirrors show
  ~240 self-collision deaths per game (≈30-48 per 1k dragon-turns, falsifier
  bar 5), newborn deaths ≤10 rounds 51%, split-churn 264-298 per game.
- **H-dissolve: MECHANISM WORKS, TARGET MISSED.** ACT:diss/esc fire in the
  onset windows (portals: 4-7 dissolves, 28 on slithery vs fry; crown grows
  11→22 over r400-500); median longest_r400 = 9 vs control 6 (panel) — but the
  ≥18 bar is only reached in games vs ladder-tier opposition. Adjacency +
  recipient-eats-first held (dissolves only beside a fresh crown).
- **H-cert: DELIVERY VERIFIED, SURVIVAL EFFECT SMALL.** The backward ray
  reaches every child on its first turn (hundreds of pings per game; 42-353
  valid certs read per game). Newborn death rate 24.7% (both arm) vs 27.9%
  (control, no cert) — a small improvement; first_pearl_round 36 vs 34.5
  (no change). The child's problem is crowding, not information.
- **Mirror vs host: 6-14.** The host wins both sides on schooltime, portals,
  slithery, queen_of_spades — kazuha is genuinely worse there, not
  initiative-affected.

## 2x2 (paired vs control on the same seeded fixtures; unswbc 1.2.2, seed fixture_hash_v1, 8 opponents x 10 live maps x 2 sides; 140 shared fixtures per arm — the control plays no self-pairing)

| arm | score /140 | pairs better/worse/tie vs control | sign p | biggest deltas |
|---|---|---|---|---|
| control (ouroboros-v10-beacon) | 51.0 (36.4%) | — | — | — |
| both (swarm + onset dissolve + cert) | 44.0 (31.4%) | 11/18/111 | 0.26 | default +8, witten +2; kraken −6, portals −4, slithery −4 |
| prod-only (swarm + salvage + cert, host endgame) | 53.0 (37.9%) | 16/14/110 | 0.86 | portals +2, trauma +2, default +2; slithery −2 |
| dissolve-only (host production + onset dissolve, no cert) | 42.0 (30.0%) | 7/16/117 | 0.093 | mimic +2, default +2; kraken −5, portals −4, slithery −4 |

Panel medians (replay-decoded):

| arm | units_r100 | longest_r400 | longest_r499 | newborn% ≤10r | first_pearl | pearls/game | prod/diss/esc/cert/crown tags |
|---|---|---|---|---|---|---|---|
| control | 14 | 6 | 10 | 27.9 | 34.5 | 255 | — |
| both | 14 | 9 | 12 | 24.7 | 36.0 | 322 | 75/1/3/42/14 |
| prod-only | 14 | 9 | 15 | 25.0 | 36.0 | 324 | 75/0/8/40/12 |
| dissolve-only | 14 | 7 | 12 | 25.6 | 36.0 | 356 | 84/2/12/0/18 |

**Attribution.** The early-onset dissolve layer is the negative component:
dissolve-only is the worst arm (7/16, p=0.09) and adding it to production
degrades prod-only (53.0 -> 44.0); both dissolve arms lose exactly portals −4
and slithery −4 — the two maps where the onset fires at r300. Harvesting
pearls is not the constraint (dissolve-only eats the most pearls, 356/game,
and wins the least): dissolving L<=3 dragons from r300-400 gives up swarm
presence and freed tiles to the opponent while the crown's banked length
(+3 median longest_r400) does not convert to round-limit wins against this
field. This reproduces, on a second host with a stricter dissolve, the
b01/b02 finding that moving the conversion clock alone does not pay.

**Net.** No arm beats the control significantly. The best measured
configuration of this codebase on this panel is `prod_swarm=1, dissolve_on=0`
(prod-only, 37.9%, 16/14/110) — a params.py flip, not a new version. The
committed s01 keeps the S1 defaults (both mechanisms on) because the bot is
the hypothesis; the finding is that half of it fails.

- **Metered probes (both toolkits, `--sandbox -v` vs sinbad-v07):**
  schooltime as A — unswbc 1.2.2 max 46.1 M / p99 37.5 M / 10 484 turns,
  1.0.0 max 50.2 M / p99 36.3 M; portals as B — 1.2.2 max 39.9 M / p99 30.5 M,
  1.0.0 max 45.1 M / p99 32.3 M. Zero faults, zero caught errors, zero
  invalid-action deaths everywhere. Activation markers all present in the
  probe windows (prod/salv/crown/diss/esc/cert).

## What s02 should change

1. **Drop the early onset; keep the crown.** The 2x2 says r300 dissolution
   loses games (portals/slithery −4 each in both dissolve arms). The crown
   election/beacon layer is harmless-to-good (longest_r400 6→9); the
   escort/dissolve path should return to r400+ (host parity) or fire only on
   elimination-loss maps where the round-limit is already lost.
2. **Map-condition the production gates, not just the onset.** The relaxed
   crowd gate (14) and 64-unit target are the churn engine on ≤1024-cell and
   portal-dense maps (portals mirrors: ~240 self-deaths/game, 51% newborn
   churn, 264-298 splits): keep the host's conservative gates there, swarm
   only on open maps (default +8/+2/+2 across arms is where the swarm pays).
3. **Newborn survival before newborn count.** Certificates deliver (verified)
   but barely move newborn deaths (27.9%→24.7%): the child's problem is
   crowding, not information. Split only with 2+ safe exits on crowded maps;
   delay splits at high local ally density.
4. **The economy hole is the ceiling.** dilemma/autarky eliminations
   (collapse to one len-3 dragon by r25, never re-reaching split length) are
   an opening-economy loss no macro schedule fixes: import confirmed-pearl
   sprint funding and bed pre-positioning from the leviathan/hunter lines.

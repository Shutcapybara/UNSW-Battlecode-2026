---
id: shenzhen-unit15-die-at-home-void-and-head-on-trades
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator probe + diagnosis (analysis copies only; no bot built for the ladder)
title: Unit 15 — H-SZ33 "die at home" is void (carthage-05 never culls itself in contact); contact deaths are head-on trades, and the trade pays the mover
evidence: unswbc 1.2.9 local runs, carthage-05 + C+D (cloud copy `c05d`) vs probes `c05m`/`c05m2`; Around UNSW, Islands, Australia (maps/live), seeds 1–2, both seats (12 games per probe); tools/shenzhen/szleak.py, tools/shenzhen/szh2h.py
---

# 1. H-SZ33 as written has no target

Probe M (step away from enemy heads before a self-cull at length ≤ 3) and probe M2 (same, for any split at the unit cap)
both produced games **identical** to their parent on all 12 games (wins 6/12, total 1,790, enemy share 0.328, contact
share 0.724 — same numbers, to the pearl). A logging copy (`LOG SZDBG` on every split, one Around UNSW game) shows why:

* carthage-05 never issues a split at length ≤ 3 (`tyr_split_option` needs length − 2 ≥ 2): 0 of 370 splits.
* the splits at the cap (the cull that kills a dragon as `invalid`) are 59 of 370, **all `why = z`** — probe C's sealed-cage
  split. A sealed dragon has no safe step by definition, so "step away first" never has a move to make.
* 'invalid' deaths (118 on side A): 63 follow a probe-C cage split, 23 have no split at all (invalid moves), the rest
  follow an ordinary split by one round (coincidence of timing, not a cull).

So the unit-14 contact half of the leak is not culls placed badly. H-SZ33 is **withdrawn** (no mechanism to move). The
self-play leak does reproduce the live one: enemy share of our corpse pearls 0.27 / 0.37 / 0.37 on Around UNSW / Islands /
Australia (live us 0.29 / 0.39 / 0.38), contact share 0.63–0.81 (live 0.59–0.70) — the simulator is a usable bed for this
question.

# 2. What contact death is: head-on trades

`szh2h.py` over the 12 M2 games (both sides carthage, deaths after r150, n = 5,640):

| cause | share |
|---|---|
| **h2h** | **0.59** (3,316) |
| invalid | 0.21 |
| self | 0.14 |
| body / wall | 0.03 / 0.03 |

Every h2h death is half of a pair (1,658 movers flagged mutual, 1,658 partners): a head-on always kills both. The mover —
the dragon whose move made the contact — is the **shorter** one: mean length 2.81 vs partner 4.30 (partner longer in 49 %
of pairs, equal 42 %, shorter 9 %). That is carthage's prey logic (`prey_min`, hunt longer heads) doing what it was built to do.

Trade ledger (1,558 cross-team pairs, r150..R−50, corpse pearls followed 50 rounds):

| | segments lost | corpse pearls born | eaten by mover side | eaten by partner side |
|---|---|---|---|---|
| mover's corpse | 2.81 | 1.64 | 1.00 | 0.64 |
| partner's corpse | 4.30 | 2.39 | 1.19 | 1.18 |

Per trade the mover side ends −2.81 + 2.19 = **−0.62**, the partner side −4.30 + 1.82 = **−2.48**: being the mover is worth
≈ **1.9 units per trade**, ~65 trades per side per game on these maps. The partner's corpse is split 50/50 — the
structural part of the leak: whoever stands at a trade point loses half of their corpse no matter what.

# 3. Hypotheses

* **H-SZ34 (0.55) — be the mover, not the partner.** On class-B maps the contact leak is the partner role in head-on
  trades. A dragon longer than a visible enemy head within its reach (enemy length − 1, ≤ 3 cells, as `mark_danger`
  already computes) should treat those cells as lethal unless it is itself moving into the trade; i.e. raise the danger
  weight when we are the longer side. Falsifier: in the simulator vs c05d, partner-role deaths per game fall ≥ 25 % and
  pool total does not fall > 5 % (seeds 1–3, the three maps, both seats = 18 games). Store check (Chongqing/Himeji, no
  bot): per ranked post-m2 side, h2h deaths split by mover/partner (frame `actor` = mover); prediction: the top ten's
  partner share is lower than ours on Around UNSW / Australia / Islands.
* **H-SZ35 (0.4) — trade-point collection.** After a cross-team head-on within 3 of an ally head, that ally collects the
  partner corpse first (it is the 50/50 pool). Same arm shape as H-SZ32 (salvage), narrower trigger; the two should not
  both be run.
* **H-SZ33 withdrawn** (§1). **H-SZ32 salvage** stands but narrows to H-SZ35's trigger: there is no "home" death to protect.

# 4. Caveats

Self-play only (one bot on both sides, so mover/partner shares are symmetric by construction); the per-trade value
assumes a pearl converts to one segment. Live mover/partner shares need the store's `actor` field, which I do not query
(Chongqing owns the store).

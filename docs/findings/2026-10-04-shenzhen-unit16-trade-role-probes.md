---
id: shenzhen-unit16-trade-role-probes
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator probes (analysis copies only; no ladder bot)
title: Unit 16 — both head-on role probes lose economy: yielding (H-SZ34) and striking first (H-SZ36) move the role count but cut total by 18 % and 10 %; the trade ledger is not a value function
evidence: unswbc 1.2.9 local runs, carthage-05 + C+D (`c05d`) vs probe N (`c05n`) and probe O (`c05o`); Around UNSW, Islands, Australia (maps/live), seeds 1–3, both seats (18 games per probe); tools/shenzhen/szh2h.py v2, tools/shenzhen/szleak.py
---

# 0. Ledger re-cut by event identity (Himeji H33-04)

`szh2h.py` v2 takes both lengths from the death records and counts corpse pearls by identity: spawns by donor id, eats by
the eat event's own `donor` field (age ≤ 50) — no cell/round matching. On the unit-15 games (1,558 cross-team pairs):
mover 2.81 vs partner 4.30 segments; mover's corpse eaten 0.98 by the mover side / 0.65 by the partner side; partner's
corpse 1.28 / 1.09. Net per trade **mover −0.55, partner −2.55** (unit 15: −0.62 / −2.48). The unit-15 ledger holds;
the partner's corpse is 54/46 to the mover side, not 50/50.

# 1. Probe N — H-SZ34 "yield" (be the mover, not the partner)

Rule: if the planned end cell is within one step (Manhattan, torus) of a visible enemy head no longer than us, take the safe
single step that maximises distance from such heads (fires ~100 times per game).

| | partner deaths / game | mover / game | total (18 games) | wins | enemy share of our corpses |
|---|---|---|---|---|---|
| c05d | 58.8 | 52.9 | 2,900 | 8 | 0.31 |
| **c05n** | **52.9 (−10 %)** | 58.8 | **2,378 (−18 %)** | 10 | 0.37 |

Per map total: Around UNSW −7 %, **Islands −55 %** (413 vs 921; c05n lower in 5/6 games), Australia +7 %. Falsifier
(partner −25 % at total ≥ −5 %) met on both counts → **H-SZ34 refuted at this form.** Kanazawa's B(L) reach (⌈L/4⌉ + L − 2)
would make the rule fire more, not less; not run.

# 2. Probe O — H-SZ36 "strike first" (new)

Rule: a non-queen of length ≤ 4 with an enemy head one step away, at least as long as itself, moves into it (~60 fires/game).

| | partner / game | mover / game | total (18 games) | wins | enemy share |
|---|---|---|---|---|---|
| c05d | 91.9 | 57.2 | 2,667 | 10 | 0.30 |
| **c05o** | 57.2 | **91.9 (+61 %)** | **2,402 (−10 %)** | 8 | 0.33 |

Per map total: Around UNSW +2 %, **Islands −32 %**, Australia −6 %. The role moved hard in our favour and the ledger still
says mover −0.8 / partner −2.1 per trade, yet the side that took the mover role lost total → **H-SZ36 refuted.** Queen alive
at the end: 0/18 for every bot in both sets (C+D does not keep the queen on these maps), so the win column is the
longest/total tiebreak and is noise at n = 18.

# 3. Reading

The per-trade ledger counts segments and corpse pearls but not the living dragon. A non-queen of length 2–4 alive at
r150/250/350 eats **1.59 pearls in the next 50 rounds** (n = 3,912 dragon-windows from the unit-15 games; 45 % die within
those 50 rounds anyway). Each trade removes that income on both sides. Extra trades also move the timing and place of
deaths, which the ledger does not price. The ledger shows who gains from trades that happen. It cannot say whether to
start or avoid one.

**Islands** is where both changes to contact behaviour cost most (−55 %, −32 %). Its chokepoints make contact and
territory the same thing: yielding gives up an island, and striking spends the collectors.

# 4. Hypotheses

* **H-SZ34 refuted**, **H-SZ36 refuted** (above). **H-SZ35** (trade-point collection) stays at 0.4: it adds collection
  without changing who trades.
* **H-SZ37 (0.5) — contact arms are priced in total, not trades.** Any contact rule must be screened on pool total per
  map, with Islands as the canary. Falsifier: a contact arm with total ≥ 0 on Islands and the role count moving the other
  way. Size: 18 simulator games. Suits any tester; zero bot cost.
* **H-SZ38 (0.45) — the field's lower leak is collector density, not trade role.** In self-play trade roles are symmetric
  by construction, yet the enemy still eats 0.30 of our corpse pearls (live us 0.29–0.39, top ten 0.16–0.19). Prediction:
  at our contact deaths the number of ally heads within 3 is lower than at the top ten's. Falsifier: top-ten ally-head
  count within 3 at contact deaths ≤ ours, on Around UNSW / Australia / Islands. Size: about 300 post-m2 games; store
  query (Chongqing/Himeji, deaths table + rounds).
* **H-SZ39 (0.35) — the option value of a small dragon sets the cull/trade threshold.** A rule that kills a dragon on
  purpose (trade, cull, cage split) pays only if its immediate yield beats about 1.6 pearls (the 50-round income above),
  discounted by its 45 % death rate. Falsifier: a cull arm whose immediate yield is below 1.6 pearls per death that still
  raises total in simulation. Size: re-read probes C/K/M2 with this threshold before new arms.

# 5. Caveats

Self-play against one parent; 18 games per probe; seeds 1–3 only. The per-map splits use six games each and are noisy.
The Islands collapse in probe N is 5 games out of 6.

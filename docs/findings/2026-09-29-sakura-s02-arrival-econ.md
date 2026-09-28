---
id: sakura-s02-arrival-econ
author: glm/sakura/session-s02
kind: observation
title: "S2 economy-on-a-band-host: sakura-s02-arrival-econ on yuna-v05-core (arrival-ready beds, funded sprints, appetite, chaewon portal-safety stack, mid-game dive bias) plus clone-62-v01"
task: docs/hub/prompts/2026-09-29-S2-economy-on-a-band-host.md
supersedes: 2026-09-28-sakura-s01-swarm-dissolve
evidence:
  - bots/sakura-s02-arrival-econ (+ arm-econ/arm-safety/arm-explore overlays) and CANDIDATE.toml
  - build/sakura-s02/{base,econ,safety,explore,all}-s1/results.jsonl (tools/sakura/panel.py, unswbc 1.2.2, seed 1)
  - bots/clone-62-v01 + build/clone62/{sweep,final}.log + target_profile.json + profile games
  - metered probes via tools/sakura/probe.py on the four S2 fixtures, both toolkits
---

# What was built

**Host** `yuna-v05-core` (with the host's own override.py: portal_mode 1, nb_mode 2,
mom_w 0.6 — the host as measured, untouched). Three lever groups, each behind an
`sk_*` master flag so the shipped bot and the three ablation arms are the same code
plus one `override.py`:

- **econ (H-econ)** — fenrir-v18's arrival-ready bed valuation (beds spawning later
  than arrival decay over `sk_ready_slack` 4 instead of `bed_wait` 12; a 1.15 premium
  when the pearl exists by arrival); 2–3-step sprints onto *confirmed* pearls
  (straight and one-bend, bounded by the host's sprint caps), funded +2.0 when an
  enemy head is within 4 of the pearl and +0.6 otherwise; contested-pearl appetite
  (enemy ownership discount 0.6 → 0.85 while r < 100 and units < 26).
- **portal-safety (H-portal-safety)** — chaewon's y04/y05 stack ported with
  attribution: the ten-public-map atlas matched on the first view, the newborn
  neck-by-adjacency fix, the solo probe ray through an adjacent portal carrying the
  HOLD packet, echo- and HOLD-based blind-risk pricing.
- **explore (H-explore)** — on maps with ≥ 6 known portal pairs, mid/end blind-transit
  risk 0.3/0.5 → 0.2/0.35, unpaired-portal value 3.0 → 4.5 and exploration chance
  0.12 → 0.2 in the mid game. The opening is untouched (see the negative result
  below). The gate counts known pairs, so it is exact from round 0 when the atlas
  matched and learns-as-you-go otherwise.

Markers (folded into the single per-turn write): `ACT:atlas`, `ACT:probe`,
`ACT:sprint`, `ACT:bed`, `ACT:dive`. No production or conversion clock was moved;
the crown/beacon layer is the host's own.

# Negative results on the way (these changed the design)

- **Bed camping is toxic.** Parking value on cells adjacent to soon-spawning beds
  (`sk_camp_w` 7.0, floor 0.3) made dragons idle: schooltime vs sinbad seed 1,
  total r250 135 → 52, pearls 1461 → 627, 1286 `ACT:bed` park-moves, wall+self
  deaths 8.6 → 11.3 per 1k. The ready lever alone already times arrivals, so camp
  ships at `sk_camp_w = 0` (code kept, gated off, documented here).
- **An opening-phase dive boost is catastrophic.** The first explore design
  (pb 0.1, vdive 8.0, eps 0.5 in the opening on rich maps, x41-portal-strong tuning)
  took schooltime from 135 → 42 total r250 with wall+self deaths 12.25 per 1k. The
  opening keeps the host's prices; only mid/end prices are touched now.
- **Porting bug found and fixed:** the HOLD packet port initially missed
  `comms.hold_packet`; every probe attempt raised and the exception handler silently
  downgraded the whole turn to the fallback move whenever a dragon ended next to a
  portal. Symptom: zero `ACT:probe`, wall+self deaths up to 37 per 1k on Portals.
  After the fix: probes fire (1266/game on Portals, 1334/game on Schooltime), zero
  MC_ERRORs, and Schooltime wall+self deaths fell to 6.0 per 1k (base 8.6).
  panel.py now counts MC_ERROR dragonLogs so this class of failure is visible in
  every future panel.

# Results

(paired panels, ten maps × both sides × seed 1, opponents: fenrir-v18-arrival-ready-beds,
sinbad-v07-divecap, gavroche-v32-supported-divecap, ouroboros-m01-vibing-mimic,
yuna-v05-core, chaewon-y04-probe, and clone-62-v01 for base/all; 97-100 paired
fixtures per arm after two persistent slithery/m01 timeouts; unswbc 1.2.2)

| arm | paired fixtures | better/worse | net | arm score | units r100 Δmed | total r250 Δmed | pearls Δmed | wall+self Δmed |
|---|---|---|---|---|---|---|---|---|
| base (yuna-v05-core) | 100 | — | — | 64.0/100 | — | — | — | — |
| +econ | 99 | 11/26 | **−15.0** | 48.0 | −1.0 | −4.0 | −25 | −0.9 |
| +portal-safety | 100 | 12/21 | **−9.0** | 55.0 | −2.0 | −6.0 | −15 | +0.8 |
| +explore | 100 | 5/4 | +1.0 | 65.0 | 0.0 | 0.0 | 0 | 0.0 |
| all (the s02 bot) | 97 | 6/28 | **−22.0** | 40.0 | −2.0 | −10.0 | −66 | −0.5 |

Against clone-62-v01 (20 fixtures each): base 14–6, the s02 bot 13–7 with more growth
(total r250 median 35.0 vs base 23.5; longest r400 3.5 vs 2.5) but many more
portal-step deaths (25.5 vs 8.5 per game) — the Heartbreaker profile punishes
portal traffic exactly the way the live eliminator is hypothesised to.

Deviations from the S2 measurement spec, stated: seed 1 only (the machine was
saturated by concurrent lineage sessions for most of the window; seeded 1.2.2
fixtures are deterministic and re-runnable — `panel.py run --seeds 2 3` appends);
two slithery/ouroboros-m01 fixtures time out persistently at both 600 s and 900 s
and are excluded from every arm symmetrically; the ablation arms did not play
clone-62 (clock) — base and the full bot did.

- **H-econ: FALSIFIED.** Total r250 median delta −4.0 (falsifier: < +8) and units
  r100 −1.0 (target ≥ +4) in 99 exact pairs. The one positive: deaths fell
  (wall+self −0.9/1k, all deaths −0.6/1k, portal deaths −11 on the portal subset)
  and schooltime alone gained (+3 net). The appetite/sprint levers trade economy
  for survival against band opponents — the inverse of the hypothesis.
- **H-portal-safety: FALSIFIED.** Portal-step deaths per game on the named subset
  moved +3.5 (falsifier: any fall < 25%); net −9.0. The host's own portal_mode
  pricing already handles portals as well as the probe/HOLD/atlas stack against
  this panel — consistent with chaewon's own caveat that the probe is one round
  stale exactly in the symmetric approach case.
- **H-explore: met exactly at the bar, weakly.** Net +3 pairs on
  Portals/Slithery/Trauma (falsifier ≤ 0 not fired; the hypothesis asked ≥ +3),
  driven entirely by Portals (+3). Every median metric is exactly zero — the
  mid-game bias changes few games, all of them on portal-dense maps.
- **The arms interact negatively:** all (−22) is worse than the sum of its parts
  (−15 −9 +1), and the deaths-for-economy trade compounds.

# clone-62-v01 (Heartbreaker imitation)

Recipe exactly the m01-mimic one: 258 v4 view+mem legal features (features_view.py)
rebuilt from the 130 current-era (sub 7233) public games in
`public_replays/team-62/packed`, HistGradientBoosting (120 × 31), exported
dependency-free. Test accuracy 0.804 (first-step recall F .914 / L .684 / R .676 /
split .807). Split emission follows their empirical rule: child takes L−2 while
L ≤ 8, child takes 2 from L = 9. Sonar emits 4 rays/turn from their payload
vocabulary {3,4,5,6} (fingerprint only). No suicide class exists (0 invalid
commands in 130 games, matching the recon).

Target profile (their own games, medians over 130): units r100 18, total r250 41.5,
longest r400 5, splits 100/game, pearls 279/game. Live-vs-ours reference (A1-Q4):
20 / 67 / 7.5.

Validation (20 seeded games per opponent class, medians, z = |clone − target| / target sd
from the 130-game public profile): vs ein-dog-v01-control (weak, the live reference
class) units r100 12.5 / total r250 22.5 / longest r400 5.0 — z = 0.33 / 0.35 / 0.00;
vs yuna-v05-core (band) 8.0 / 4.0 / 2.0 — z = 0.59 / 0.69 / 0.94. **Within one
standardised unit on all three metrics against both classes** (A1-Q4c bar).
Split behaviour: 58-71 splits/game (target 100), pearls 150-234/game (target 279),
wall+self deaths 0.0/1k (target 3.76) — the clone is more cautious than the target,
which costs it volume but not profile shape. Full record in
`build/clone62/clone_validation.json` (copied into the bot directory).

# Metering

| toolkit | fixture | turns | p50 | p99 | max | faults |
|---|---|---|---|---|---|---|
| 1.2.2 | Schooltime A | 22,706 | 18.2M | 62.3M | 72.5M | 0 |
| 1.2.2 | Portals B | 6,410 | 19.6M | 61.2M | 71.4M | 0 |
| 1.2.2 | Slithery A | 20,967 | 17.8M | 62.1M | 79.5M | 0 |
| 1.2.2 | Trauma B | 9,454 | 16.6M | 56.8M | 67.2M | 0 |
| 1.0.0 | Schooltime A | 10,087 | 17.3M | 61.2M | 70.1M | 0 (ended r221) |
| 1.0.0 | Portals B | 6,526 | 19.0M | 60.4M | 70.0M | 0 |
| 1.0.0 | Slithery A | 22,504 | 17.5M | 63.0M | 81.5M | 0 |
| 1.0.0 | Trauma B | 9,502 | 15.9M | 57.9M | 64.5M | 0 |

**The 1.0.0 hub gate FAILS as shipped**: zero faults and max < 80M hold on three
fixtures, but Slithery max 81.5M breaches, and p99 exceeds 60M on Schooltime,
Portals and Slithery (by 0.4-3.0M). For scale: the host alone meters p99
46.5-50.5M on the same fixtures and chaewon-y05-hold (atlas+probe+HOLD, no econ)
53.8-59.5M — most of the excess is the atlas-enabled target search, not the econ
levers. Two behavior-identical CPU fixes were applied and verified
(byte-identical trajectories) before these numbers: single-step marker computation
without a re-simulation, and skipping packet construction on probe turns. The
remaining trim (search cap when the atlas is loaded, atlas import deferral) changes
behavior and is deliberately left to s03 so this generation's ablation stays
internally consistent.

# What s03 should change

1. CPU first: trim the target-search cap when the atlas is loaded and defer the
   atlas import off round 0 (the host meters p99 46.5-50.5 where the s02 bot
   meters 56.8-63.0 — the gap is knowledge-driven search, not the levers); the
   candidate must clear the 1.0.0 gate before anything else is worth measuring.
2. Ship econ narrow: sprint funding only (race-tier), appetite off, ready lever on
   open maps only — schooltime (+3) is the one map where econ helped and compact
   maps (dilemma −6, pearls −75) are where it bled.
3. Keep the explore bias (it is free and Ports-positive) and drop the probe/HOLD
   stack unless a cheaper variant (probe only when the exit is *pair-unknown*)
   pays for itself.
4. clone-62-v01 is the panel addition that changed what we can see: it beats
   neither base nor s02 on wins but exposes the portal-death differential
   (25.5 vs 8.5) — every future candidate should be screened against it.

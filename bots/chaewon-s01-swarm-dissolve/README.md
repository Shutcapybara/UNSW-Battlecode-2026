# chaewon-s01-swarm-dissolve

Lineage **chaewon** (claude/chaewon/cowork-016ueqq). Host: `ouroboros-v10-beacon` (parser, exact step simulation,
flood/doom tests, threat model, beacon). Built to the S1 build prompt (`claude/next-gen-prompt-S1-swarm-dissolve.md`).
Every mechanism sits behind a parameter in `P` (overridden by `params.py`); the four 2×2 arms share one `main.py`:

| Arm | Directory | params.py |
|---|---|---|
| control (host + core fixes) | `chaewon-s01a-control` | `prod_on 0, diss_on 0` |
| production only | `chaewon-s01b-prod` | `prod_on 1` |
| dissolve only | `chaewon-s01c-diss` | `diss_on 1` |
| both (this bot) | `chaewon-s01-swarm-dissolve` | `prod_on 1, diss_on 1` |

**Core (all arms):** no scout role (scout share of the child mix → gatherers); `LOG ACT:<tag>` markers
(`prod`, `salv`, `cert`, `crown`, `esc`, `diss`); **newborn neck fix** (a split child's segments keep the
parent's facings, so v10's `seed_trail` failed to link the neck and newborns walked into it — linked by adjacency
now); an unpaired portal ranks above a body in the all-fatal fallback.

**prod_on:** `λ_unit(t)` = 1 until `produce_until` (100), linear to 0 at `produce_stop` (380); production target =
unit cap; crowding limit 16 while λ = 1; deterministic **salvage** when every first step is lethal (adjacent enemy
head → trade; else `SPLIT L−2` with a free child exit; else unpaired portal; else die in place); **birth certificate
v2** (role, target, map class, crown cell/length) on the backward ray. Delivery finding: the ray leaves the new tail
along body[n+1]→body[n], so it reaches the child only when the body is straight at the cut (35–49 % of splits
in probe games); production now prefers a straight cut (n or n+1), else pays `cert_bent_pen`.

**diss_on:** crown self-election from r250 staggered by `(id·7919) mod 40`, longest-known only; beacons carry the
crown id; map-conditioned onset (Portals: 32×16 with start length 3 or ≥5 portal pairs; Slithery Fight: 63×27 →
r300, else r400); L ≤ 3 dragons within 30 escort the crown and dissolve (no action → noValidAction) only when its
**visible head is adjacent through an open edge** and no enemy head is within 2.

## Six-line measurement report

Panel: 10 live maps × 2 sides × seed 1 × {yuna-v02-core (live source), sinbad-v07, ouroboros-m01-vibing-mimic,
ouroboros-v10-beacon (base)} = 80 paired fixtures per arm, unswbc **1.2.2** `--seed`, harness `tools/chaewon/panel.py`
(replay statistics `tools/chaewon/cstats.py`). Reference set cut from 8 to 4 opponents for compute (2-core container).

1. **Strategy.** V weights: λ_unit 1 → 0 over r100–r380 (prod arms), λ_crown from r250, onset r300 (Portals,
   Slithery Fight) / r400; λ_ctrl = 0. Funnel (per game, open maps, both-arm): 376 escort turns → 8.8 dissolves →
   12.5 corpse pearls → 8.1 eaten by the crown within 2 rounds (65 %) → crown alive at r500 in 40/64 games →
   longest margin at the end −4.3. Compact maps: ~0 dissolves (games end by elimination first).
   Recipient-first is efficient per corpse (65 % vs the 8–19 % measured for crash-feeding) but the volume is tiny and
   the escort time is paid in lost foraging.
2. **Execution.** Paired Δ vs control (better/worse pairs, sign p): prod −0.037 (7/10, 0.63); diss −0.087 (4/11,
   0.12); both −0.138 (4/15, **0.019**). Activation per game (both-arm): prod 110, salv 116, cert 76, crown 21,
   esc 302, diss 7.
3. **Implementation.** `--sandbox -v` vs sinbad-v07. unswbc 1.2.2 (seed 1): Schooltime as A p50 21.4M / p99 35.8M /
   max 45.2M (7,005 turns); Portals as B p50 18.2M / p99 31.7M / max 42.9M (10,412 turns). unswbc 1.0.0: Schooltime
   as A p99 35.5M / max 47.3M (13,001 turns); Portals as B p99 30.9M / max 43.9M (11,597 turns). 0 CPU faults,
   0 caught errors, 0 unmarked noValidAction deaths; all five contract markers fire on Portals-as-B on both toolkits.
   Degradation: v10's (boot turn = safest single step; searches capped by `bfs_cap`/`rbfs_cap`/`doom_cap`).
4. **State.** Map class (onset) ← dims + start length + portal count; crown belief (id, cell, length, TTL
   `beacon_memory`) ← beacons/self packets/certificate, consumed by escort/dissolve/production stop; certificate
   flag → ACT:cert; everything else is v10's (terrain, portal pairs, beds, pearls, enemies, allies).
5. **Messaging.** Packets: v10's self/enemy/portal/bed/doom/crown (crown now carries the id) + certificate v2
   (1 per split; 76 read per game against 168 births = 46 %: production splits prefer a straight cut, salvage
   splits cannot choose).
6. **Momentum.** No new hysteresis (v10's visit penalty). Certificate + salvage (prod arm): newborn deaths ≤ 10
   rounds 38.9 → 21.3 per 100 births and wall+self 6.4 → 2.8 per 1k turns — **confounded**: salvage turns trapped
   wall/self deaths into deliberate noValidAction deaths, which these statistics exclude. First-pearl round 6 → 7.

## 2×2 (80 paired fixtures, seed 1)

| Arm | Score | Δ vs control | better/worse | p | units r100 / r250 | longest r400 / r499 | total r499 |
|---|---|---|---|---|---|---|---|
| control | 0.438 | — | — | — | 12 / 17 | 10.5 / 12.5 | 34.5 |
| prod | 0.400 | −0.037 | 7/10 | 0.63 | 12 / 17.5 | 11 / 8 | 30.5 |
| diss | 0.350 | −0.087 | 4/11 | 0.12 | 12 / 24 | 11 / 9.5 | 54.5 |
| both | 0.300 | −0.138 | 4/15 | 0.019 | 12 / 22 | 12 / 6.5 | 39.5 |

By opponent (both-arm score): m01 0.45, v10 0.30, sinbad-v07 0.30, yuna-v02 (live) 0.15.

**Falsifiers that fired:** H-prod (units r100 = 12 < 15: production is pearl-limited, not rule-limited), H-dissolve
(longest r400 11–12, not above the host's; the rule rarely fires), H-cert inconclusive (see Momentum).
**Successor:** `chaewon-s02-atlas` (+0.15 over this bot on a 20-fixture screen) and the yuna-host line
(`chaewon-y01…y04`), see `docs/findings/2026-09-28-chaewon-s01-swarm-dissolve.md`.

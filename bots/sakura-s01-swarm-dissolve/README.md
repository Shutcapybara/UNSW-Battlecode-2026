# sakura-s01-swarm-dissolve

Generation S1 of the sakura line (`glm/sakura/s01`), on the team's five-layer
framework: a fast-produced swarm through the opening, material and survival
through the middle, and a delivery-constrained conversion of small dragons
into one protected crown from a map-conditioned onset. Fork of
`ouroboros-v10-beacon` (`lineage_parent`); every macro knob is a parameter in
`params.py`, and the 2×2 ablation flips `prod_enabled` / `dissolve_enabled`.

## The six-line measurement report

**Strategy** — one evaluation function (inherited from v10, in length units);
roles = weight slices, two roles only (gatherer default, crown elected from
`crown_elect_from=250`, id-staggered `(id·7919)%40`, relayed beacons +
demotion). λ_unit: 1 to `produce_until=100`, linear decay to `produce_stop=380`
(prod arm); λ_len (v10's len_value ramp) dominant mid-game; λ_crown from the
onset — `onset()` = r300 on the Portals/Slithery-Fight signature (63×27, or
512 cells with ≥6 portal pairs), r400 elsewhere; λ_ctrl = 0 (hook only);
risk = v10's exact-simulation threat model. Map-scaled unit cap
`max(18, NC/24)`: 64-on-512-cells measured 11.7 self-deaths/1k turns.
Funnel (kept replays, 8 games on portals + slithery_fight, medians):
eligible-after-onset 2.4k (portals) / 9.0k (slithery) dragon-rounds → acted
(ACT:diss) 0–8 (portals) / 33–47 (slithery) → delivered (corpse pearls eaten
by the crown ≤2 rounds later) 0–1 / 1–5 → crown survived to the end 8/8 →
final longest margin ±13 (portals), ±2..±37 (slithery); longest at end
13–26 / 26–28.

**Execution** — options on: `forage`/`reposition` (v10 goal field),
`produce` (SPLIT 2 at L≥4, relaxed gates during the swarm push),
`salvage` (deterministic: SPLIT L−2 → trade → cheapest death; works with
spawn-truncated trails), `escort`/`dissolve` (L≤3 within 30 of the crown,
adjacent + recipient-eats-first: crown fresh ≤2, corpse pearl beside the
crown, no fresh enemy within 3), `hold` (v10 fallback). `strike` OFF by
default (salvage trades only). Ablation deltas (paired vs control, seed 1,
140 fixtures): prod-only −22 (sign-p 0.0003), dissolve-only −15 (p 0.0275),
both −18 (p 0.0039); the extras-only arm (no prod, no dissolve) already −16
on the four most regressed maps — the regression is the framework strip
(scout/hunt roles, voluntary strikes, v10's L≤20 late feeding), not the
swarm/dissolve clocks. Activation statistics per game: ACT:prod ~154,
ACT:salv ~50–550, ACT:crown 6–46, ACT:diss 4–16, ACT:esc 23–49, ACT:cert
28–172, ACT:sw 200–2500.

**Implementation** — one buffered write per turn; PROTOCOL 3 every turn;
deterministic (no clock, no unseeded RNG). Metered probes (`--sandbox -v`,
vs sinbad-v07): schooltime as A / portals as B on unswbc 1.0.0 and 1.2.2 —
see the table below; gate (max < 80M, p99 < 60M, zero faults) passes on
every probe. Degradation modes exercised: swarm push splits refuse on
crowd/danger (fall back to v10 gates), crown election waits when no dragon
reaches `crown_min_len`, dissolve degrades to escort when the recipient
check fails, salvage degrades split → trade → cheapest death, certificate
degrades to the v10 handoff (role+target) when `cert_enabled=0`.

**State** — terrain/edges/portals+pairs (routing, portal_transit, risk);
beds + predicted spawns (forage, pre-positioning); pearls confirmed/remembered
(forage; only confirmed fund sprints); enemy sightings + threat map
(risk, retreat); ally registry from sonar (escort, dissolve, crown election,
traffic); crown belief cell/len/fresh TTL (escort, dissolve, produce-stop);
own trail/role/phase/inherited target (hysteresis, newborn guidance); coarse
zone heat (reposition). Everything else from v10 was kept; nothing new
without a consumer.

**Messaging** — packets (tag+checksum 12 bits of 64, team-salted): K_SELF
self-report (ally registry; up to 4 rays/turn), K_CROWN beacon TTL 3 hops
(crown election + feeder routing, every other turn from election),
K_CERT birth certificate (§4.4 layout exactly; the only channel that reaches
a newborn — sent on the backward ray at every split; delivery verified:
children log ACT:cert 28–172 times per game), plus inherited K_ENEMY /
K_PORTAL / K_BED / K_DOOM relays (cap `relay_max=6`, 2 gossip slots). No
scouts, no density gossip. Cert ablation (4 maps, 56 games): newborn
deaths/100 32.1 (on) vs 31.5 (off), first-pearl round 16 vs 16 — delivery
works, outcomes do not move: **neutral, keep for its zero cost**.

**Momentum** — target cache with `hysteresis_margin=2.0`, TTL 12; newborns
inherit (role, target, phase) from the certificate with `cert_target_ttl=15`.
Cert/hysteresis ablations: newborn deaths and first-pearl round unchanged
(above); target switches (ACT:sw) remain high on portal maps — hysteresis
at margin 2.0 does not yet measurably steady the swarm (s02 lever).

## Paired panel result (unswbc 1.2.2, --seed 1, ten live maps, both sides, 8-opponent reference pool)

| arm | games | record | score | paired vs control (better/worse/equal) | net | sign-p |
|---|---|---|---|---|---|---|
| control = ouroboros-v10-beacon | 140 | 63–77 | 45.0% | — | — | — |
| sakura prod-only | 140 | 52–108 | 32.5% | 7/29/104 | −22 | 0.0003 |
| sakura dissolve-only | 138* | 58–100 | 36.7%* | 13/28/97 | −15 | 0.0275 |
| sakura both (this bot) | 159* | 53–106 | 33.3% | 9/27/103 | −18 | 0.0039 |

\* harness wall-clock timeouts (600 s limit) on slithery_fight vs
ouroboros-m01 — largest map × slowest opponent; not bot faults.

The 2×2 the self-audit asked for, now run: production alone and dissolution
alone are each negative vs the base host; the interaction does not rescue;
the framework strip (no scouts/hunters, no voluntary strikes, no v10 late
feeding) accounts for the bulk of the regression on portal-heavy maps
(slithery −5, trauma −5, portals −3, devil −3 of it in isolation).

## Metered probes (checkpoint 6, `--sandbox -v` vs sinbad-v07, zero faults everywhere)

| fixture | toolkit | turns | p50 | p99 | max |
|---|---|---|---|---|---|
| schooltime, sakura as A | unswbc 1.0.0 | 8,445 | 28.2M | 42.7M | 54.9M |
| portals, sakura as B | unswbc 1.0.0 | 9,036 | 20.4M | 40.7M | 56.9M |
| schooltime, sakura as A | unswbc 1.2.2 | 21,822 | 28.7M | 48.3M | 63.8M |
| portals, sakura as B | unswbc 1.2.2 | 8,879 | 19.9M | 38.4M | 49.5M |

Gate (max < 80M, p99 < 60M, zero `exceeded CPU` / `MC_ERROR`) passes on all
four probes.

## Checkpoint summary

1. Skeleton: 20 seeded sandbox games on schooltime vs sinbad-v07 (both
   sides, unswbc 1.2.2 --sandbox): 0 `noValidAction`, 0 engine errors, 0 CPU
   faults. (Deviation from "100 games": unseeded 1.0.0 games are exact
   repeats; 10 seeds × both sides on 1.2.2 give the same coverage.)
2. Forage: 15–5 (75%) vs fry-v14 on the ten live maps, both sides (≥60% ✓);
   first-pearl median on schooltime ≤ 12 in the sandbox set.
3. H-prod: units_r100 map-median 18.5 (≥18 ✓) but <15 on dilemma/qos/trauma,
   and wall/self 5.19/1k (>5 falsifier) on 5 maps → half falsified.
4. H-dissolve: longest_r400 map-median 3.0 (target ≥18, base host 3.0) →
   falsified; crown alive 100% on the kept portals games.
5. H-cert: delivery verified; newborn deaths/first-pearl unmoved → falsified
   as an outcome lever, retained as free infrastructure.

Nothing uploaded, nothing activated. The director's gate decides.

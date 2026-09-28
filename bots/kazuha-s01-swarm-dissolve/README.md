# kazuha-s01-swarm-dissolve

`glm/kazuha/s01` — swarm-then-dissolve on the team's five-layer framework.
Host: **ouroboros-v10-beacon** (parser, exact 1–3-step simulation, sonar packing,
goal field and safety scoring are the host's; the policy layer is rewritten
against `docs/design-framework.md` / the S1 build prompt). Nothing here is
uploaded or activated.

## Six-line measurement report

**Strategy** — `V = lam_unit·units + lam_len·Σlen + lam_crown·(ourLongest−theirLongest) + lam_ctrl·control − risk`,
`lam_ctrl = 0` (hook only). `lam_unit` = 1 to r100, linear to 0 at r380 (production:
`SPLIT 2` toward the 64-unit cap, crowd gate relaxed to 14 during the opening);
`lam_len` = host ramp 1→3 from r340; `lam_crown` rises r250→onset, then dominates:
crown elected from r250 (stagger `(id·7919)%120`, demote 3, beacons ttl 3), and
from the map-conditioned onset — **r300** when `W==63` (Slithery Fight) or
`≤625 cells` with `≥6 portal pairs` discovered (Portals), **r400** elsewhere —
dragons with `L ≤ 3` within 30 route escort the crown and dissolve adjacent.
Funnel (portals-candidate-A vs fry): eligible→acted is gated by crown-knowledge
freshness (≤3 rounds); 5 dissolves, 4 escort tags; crown 11→22 over r400–r500.
[2×2 funnel medians: filled after the panel.]

**Execution** — options on: `forage`, `reposition`, `produce` (ACT:prod),
`salvage` (ACT:salv: SPLIT L−2 when boxed, adjacent-head trade when nothing is
safe, cheapest death aimed at allies), `retreat` (risk terms), `portal_transit`
(host dive), `escort` (ACT:esc), `dissolve` (ACT:diss, move into own body, only
when a corpse pearl sits one step from the crown head — recipient-eats-first),
`hold`. Off: `strike` (no new mechanism; host trade margins retained),
scouts, density gossip. Ablation deltas: see the 2×2 table below.

**Implementation** — one buffered write per turn incl. `PROTOCOL 3` and `LOG ACT:*`;
deterministic (id/round-salted, no clock, no unseeded RNG). Metered
(`--sandbox -v`, unswbc 1.2.2, schooltime as A / portals as B vs sinbad-v07):
[probes: filled at delivery]. Fault batch: 6 sandbox games vs sinbad-v07
(schooltime, both sides): 0 CPU faults, 0 crashes, 0 `no valid action` deaths,
max 46.2 M, p99 37.0 M. Degradation mode: every search is capped
(`bfs_cap` 180, `rbfs_cap` 260, `doom_cap` 40); the certificate and all sonar
kinds are skipped when their queues are empty; `dissolve` degrades to escort,
escort to normal forage, when crown belief is stale.

**State** — terrain/edges + portal pairs and exit history (routing, dive,
risk — portal head-ons are the dominant friendly-kill surface); beds with
predicted renewal (`forage` pre-positioning); pearls confirmed vs remembered
decaying (only confirmed fund sprints); enemy sightings decaying into the
threat map (strike/retreat/risk); ally registry from self-packets (collision
avoidance, crown election); crown belief with TTL; own trail/visits/role/birth
certificate (hysteresis, escort); coarse zone heat (reposition).

**Messaging** — `K_CERT` birth certificate (proto4|role3|phase2|target12|
crownId16|crownLen7|parent8) on the backward ray at every split — **delivery
verified empirically**: 293 first-turn child hits, 115 valid certs read in one
portals game (ACT:cert); consumer = child boot turn (role/target) and crown
belief. `K_CROWN` election beacon (ttl 3, every 4 rounds staggered); consumers
= election demotion, escort/dissolve targeting. `K_SELF/K_ENEMY/K_PORTAL/K_BED/K_DOOM`
(host kinds, unchanged); echo counts feed risk/reposition via the host.
Ablation delta of cert: [2×2]. Density/hotspot gossip: off (never built).

**Momentum** — sticky target with `hysteresis_margin` 1.0 length unit and
3-round keep-TTL (switch only when the old target is dead and the new beats the
old score + margin); visits penalty (anti-dither); waypoint cache. Certificate
→ child's first step pulls toward the assigned target. Newborn deaths ≤10
rounds: [2×2 numbers] (cert arm vs no-cert arm).

## Screens and panels (all unswbc 1.2.2, seeded `fixture_hash_v1`)

- **Checkpoint 2 vs fry-v14** (10 live maps × both sides, 20 games):
  **14–0–6 (70 %)** — bar was ≥60 %. Losses: dilemma ×2 (elimination ~r180),
  autarky ×2 (elimination ~r385), trophy A (r268), slithery A (round-limit).
  Loss mode (replay decode): economy — on dilemma the team collapses to one
  len-3 dragon by r25 and never re-reaches split length; on autarky 19 of our
  newborn deaths are head-to-head trades fry initiates. Not a crash mode:
  0 invalid-action deaths anywhere.
- **2×2 ablation** (same 160 seeded fixtures per arm: 8 reference opponents ×
  10 live maps × 2 sides): [filled at delivery].
- **Full panel** (winning arm + control, 3 seed variants): [filled if run].

## Reproducing

```
PATH=~/.venvs/bc122/bin:$PATH python3 tools/compare_bot.py \
    bots/kazuha-s01-swarm-dissolve --config comparison-kazuha.toml
python3 tools/kazuha/kazuha_stats.py A <replay>          # ACT/funnel stats
python3 tools/kazuha/probe_parse.py A <sandbox -v log>   # CPU profile
```

Parameters: `params.py` (macro schedule §4.2 of the build prompt); the 2×2 arm
switches are `prod_swarm`, `dissolve_on`, `cert_enabled`.

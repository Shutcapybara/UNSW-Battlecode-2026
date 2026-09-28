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
Funnel (panel medians, this arm): 1 dissolve and 3 escort tags per game;
recipient-adjacency held on every dissolve (ACT:diss only beside a fresh
crown); crown grows through the window (e.g. portals vs fry: longest 11→22
over r400–r500) — but see the 2×2: this layer is net negative against the
panel.

**Execution** — options on: `forage`, `reposition`, `produce` (ACT:prod,
panel median 75/game), `salvage` (ACT:salv: SPLIT L−2 when boxed, adjacent-head
trade when nothing is safe, cheapest death aimed at allies; median 52/game),
`retreat` (risk terms), `portal_transit` (host dive), `escort` (ACT:esc,
median 3/game on this arm), `dissolve` (ACT:diss, median 1/game; move into own
body, only when a corpse pearl sits one step from the crown head —
recipient-eats-first), `hold`. Off: `strike` (no new mechanism; host trade
margins retained), scouts, density gossip. Ablation deltas (paired vs control,
140 fixtures): prod-only +2.0 score (16/14/110, p=0.86); dissolve layer −9.0
(7/16/117, p=0.093) — see the 2×2 table.

**Implementation** — one buffered write per turn incl. `PROTOCOL 3` and `LOG ACT:*`;
deterministic (id/round-salted, no clock, no unseeded RNG). Metered probes
(`--sandbox -v` vs sinbad-v07, both toolkits): schooltime as A — unswbc 1.2.2
max 46.1 M / p99 37.5 M / 10 484 turns, unswbc 1.0.0 max 50.2 M / p99 36.3 M /
7 890 turns; portals as B — 1.2.2 max 39.9 M / p99 30.5 M, 1.0.0 max 45.1 M /
p99 32.3 M. **Zero faults, zero caught errors on all four** (gate: max < 80 M,
p99 < 60 M). Fault batch: 6 further sandbox games vs sinbad (schooltime, both
sides): 0 CPU faults, 0 crashes, 0 `no valid action` deaths. Degradation
mode: every search is capped (`bfs_cap` 180, `rbfs_cap` 260, `doom_cap` 40);
the certificate and all sonar kinds are skipped when their queues are empty;
`dissolve` degrades to escort, escort to normal forage, when crown belief is
stale.

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
Cert ablation (2×2): newborn deaths 27.9 % → 24.7 % with the certificate;
first-pearl round unchanged. Density/hotspot gossip: off (never built).

**Momentum** — sticky target with `hysteresis_margin` 1.0 length unit and
3-round keep-TTL (switch only when the old target is dead and the new beats the
old score + margin); visits penalty (anti-dither); waypoint cache. Certificate
→ child's first step pulls toward the assigned target. Cert ablation (2×2):
newborn deaths ≤10 rounds 27.9 % (no cert) → 24.7–25.0 % (cert arms) — small;
first_pearl_round 34.5 → 36.0 — no change. Delivery verified; the newborn's
binding constraint is crowding, not information.

## Screens and panels (all unswbc 1.2.2, seeded `fixture_hash_v1`)

- **Checkpoint 2 vs fry-v14** (10 live maps × both sides, 20 games):
  **14–0–6 (70 %)** — bar was ≥60 %. Losses: dilemma ×2 (elimination ~r180),
  autarky ×2 (elimination ~r385), trophy A (r268), slithery A (round-limit).
  Loss mode (replay decode): economy — on dilemma the team collapses to one
  len-3 dragon by r25 and never re-reaches split length; on autarky 19 of our
  newborn deaths are head-to-head trades fry initiates. Not a crash mode:
  0 invalid-action deaths anywhere.
- **2×2 ablation** (same seeded fixtures per arm: 8 reference opponents ×
  10 live maps × 2 sides; 140 shared fixtures — the control plays no
  self-pairing):

  | arm | score/140 | pairs b/w/t vs control | sign p |
  |---|---|---|---|
  | control (ouroboros-v10-beacon) | 51.0 (36.4 %) | — | — |
  | both (this bot, S1 defaults) | 44.0 (31.4 %) | 11/18/111 | 0.26 |
  | prod-only (`dissolve_on=0`) | **53.0 (37.9 %)** | 16/14/110 | 0.86 |
  | dissolve-only (`prod_swarm=0,cert_enabled=0`) | 42.0 (30.0 %) | 7/16/117 | 0.093 |

  Attribution: the early-onset dissolve layer is the negative component —
  both dissolve arms lose exactly portals −4 and slithery −4 (the two
  onset-300 maps); dissolve-only eats the most pearls (356/game median) and
  wins the least. Panel medians: units_r100 14 in every arm (the swarm does
  not out-produce this field); longest_r400 6 (control) → 9 (both/prod);
  newborn deaths ≤10r 27.9 % (control) → 24.7–25.6 % (cert arms);
  first_pearl_round ~35–36 in all arms. Mirror vs own host: 6–14.
  **Best measured configuration of this codebase is `dissolve_on=0`
  (prod-only, 37.9 %) — a params.py flip, not a new version.** The committed
  defaults keep both mechanisms on because the bot is the S1 hypothesis; the
  2×2 is the finding that the onset-dissolve half of it fails (full detail:
  `docs/findings/2026-09-28-kazuha-s01-swarm-dissolve.md`).
- **Full 3-seed panel on the winning arm + control: not run** — the 4×140
  paired panel above already separates the arms (the best arm's edge over
  control is +2/140, p=0.86); three seeds would refine a null, not flip it.
  Compute was left to the director's live gate.

## Reproducing

```
PATH=~/.venvs/bc122/bin:$PATH python3 tools/compare_bot.py \
    bots/kazuha-s01-swarm-dissolve --config comparison-kazuha.toml
python3 tools/kazuha/kazuha_stats.py A <replay>          # ACT/funnel stats
python3 tools/kazuha/probe_parse.py A <sandbox -v log>   # CPU profile
```

Parameters: `params.py` (macro schedule §4.2 of the build prompt); the 2×2 arm
switches are `prod_swarm`, `dissolve_on`, `cert_enabled`.

# Feynman: context-dependent density decisions on a frozen execution layer

Lineage owner: Kimi. Started 2026-09-26. Mission, from the strategy brief and
the strategic statistics summary (`STRATEGIC_STATS_SUMMARY.md`): pick a sensible
baseline given measured performance and design simplicity, freeze everything
not related to features, and develop **EWMA-density-based features** —
friendly and enemy dragon density, size-weighted density, time and topology
conditioning, messaging protocol, multi-window EWMAs, and density gradients —
on a **fixed execution layer**, with all strategic choices game-relative
(frontier, support, region, mass — never compass directions or spawn side).

## 1. Baseline choice

**Baseline: `valjean-v01-portal-memory`, copied byte-identically to
`bots/feynman-x01-frozen`** (SHA-256 manifest `tools/feynman/frozen.json`;
17 files, zero mismatches, frozen before any Feynman screen outcome was read).

| Candidate | Measured strength | Fit to this mission | Verdict |
|---|---|---|---|
| **valjean-v01-portal-memory** | **101–55** vs Monte Christo v01's 94–62 on identical fixtures (13 maps × ouroboros-v13, leviathan-v09, hunter-v22, aramis-v02, sinbad-v06, avery-v08, both sides); 16–10 vs sinbad-v06 | Aramis intention vocabulary with `Q = objective_value(features) + executor_value(preview)`; features enter *only* through `objective_value`; every feature default-off with verified 54/54 MC-parity; EWMA density field (`density.py`), mass/length sonar (`mass.py`, T_MASS), topology room floods (`topology.py`) and regions already implemented as dormant machinery; purpose-built experiment loop (cached deterministic `arena.py`, paired `compare.py`, `override.py` variants, frozen fresh/holdout map sets) | **chosen** |
| javert-v01-game-relative | Fresh reserve 10–2 vs density control 7–5 and MC 5–7; but loses every MC head-to-head 2–4 | Already carries the proven type-7 length-density radio and F2 features (openness, phase, saturation) on the Aramis contract; judge-verified (max 97.0M, 3.04M margin) | rejected as baseline: weaker measured base and thin CPU margin; **kept as the reference implementation** for F1's packet discipline and as a screen opponent |
| drake-v09-density-tuned | 0.366 aggregate (ties v07's 0.370); flips big_empty 2–20 → 9–13 | The only *validated* EWMA estimator + messaging (K_DENS) line; halflife methodology and the dual-EWMA failure record | rejected as baseline: evaluator architecture without the intention contract, weaker field position; **kept as the methodological reference** for estimator validation (§6) |
| sinbad-v07-divecap | Strongest raw measurement in the repo (150–48 shared comparison, 11 maps); judge worst turn 66.7M | Monolithic arrival-aware evaluator; no intention/candidate separation, so "context-dependent choices on a fixed execution layer" has no fixed layer to sit on; its validated mechanics are already ported into valjean's RELEASE (bed_wait, trap, strike, hunt, crown settings) | rejected: architecture, and parameters at a local optimum; kept as a screen opponent |
| monte_christo-v01-core | 94–62 on the same fixtures | The playing control of the whole programme; density machinery lives in later MC versions (v06/v07), not v01 | rejected as baseline (valjean strictly supersedes it); **remains the playing control** |
| aramis-v01/v02, dartegnan-v01 | Known strength regressions; dartegnan fails judge CPU (100.16–114.13M turns reproduced) | Semantic but heavyweight | rejected |

The deciding factors: valjean-v01 is the strongest measured bot on the
intention contract, its feature-flag discipline (default = parity, one switch
per feature) is exactly the "freeze everything not related to features"
workflow, and its harness makes a feature comparison a two-command operation.
Its one open risk — judge CPU had never been run on the release source — was
Gate Zero (§3), which passed. If a later judge check fails beyond cheap
repair, fall back to **javert-v01** (judge-verified, same contract family)
and port valjean's portal memory instead.

## 2. Freeze discipline

Frozen from x01 (feature work must not touch these, and a change to any of
them is an *executor* or *mechanics* experiment, not a feature experiment):

- `executors.py`, `tactics.py`, `candidates.py` (candidate enumeration and
  kinds), `world.py`, `protocol.py`, `main.py`, `roles.py` — the execution
  layer: intention kinds (GATHER, SCOUT, ATTACK, RETREAT, FEED_ALLY,
  REPRODUCE), move previews, collision/sprint/split mechanics, commit rules.
- Every parameter outside the feature blocks: material, production, target
  values, move evaluation, combat, crown/feeding endgame, and the RELEASE
  bundle itself (`blind_mem`, `bed_wait`, `hunt_max_len`, `w_trap_soft`,
  `crown_cut_full`, `strike_reach`).
- The harness: toolkit 1.0.0, map sets, opponent roster, fixture lists.

Iteration surface (each behind its own default-off parameter, so every
variant reproduces x01 byte-for-byte when off):

- `density.py` — EWMA estimator internals and the features read from it.
- `mass.py` / `radio.py` / `comms.py` — what is reported, the encoding, the
  ray schedule. Radio changes are *information* changes: classified honestly,
  measured with info-only cells before any consumption.
- `topology.py` / `regions.py` — room and connected-space measurements that
  normalize density.
- `policy.py` and `valuation.py` — *consumption only*: how existing candidate
  scores read features. Policy must not touch legality, routing, tie-breaks,
  or executor search depth.

Context dependence is expressed as objective modes over game-relative fields
(toward/away from the density frontier, toward support, toward a region),
resolved to waypoints by candidates — the policy never emits a compass
direction as strategic intent. Approach vs completed contact stays distinct
(the Aramis lesson); a feature may change which objective is nominated, never
what an executor's outcome class means.

## 3. Gate Zero — results (completed 2026-09-26)

All runs native or sandbox under toolkit 1.0.0 on this machine, cached in
`build/valjean/cache.jsonl` (feynman-x01 and valjean-v01 share one content
hash, so the cache serves both).

1. **Judge CPU — PASS, with the expected thin margin.** Sandbox games vs
   hunter-v22-frontier-exploration: stronghold A/B (W/W on length, r500,
   worst turn 66.7M) and big_empty A/B (W/L on length, r500, worst turn
   **81.4M**, p99 64.2M, p50 31.5M) plus arena A vs sinbad-v06 (60.2M).
   Five sandbox games, zero timeouts, zero errors. The release configuration's
   worst observed turn leaves **18.6M points of headroom**; this is the
   budget ceiling every F-variant is metered against, and F2's extra floods
   must be costed against it. Finite coverage (5 games, 2 opponents), not a
   universal guarantee — metering is repeated on every promoted variant.
2. **Parity — PASS.** feynman-x01 and valjean-v01 hash identically under the
   arena's content addressing (`b4509665ddc8`); run from an empty cache
   against sinbad-v06 on default_small/devil/queen_of_spades, both sides,
   all six games reproduced valjean-v01's cached outcomes exactly (results,
   reasons, rounds, final units/longest/total and all counters).
3. **Baseline fresh-map record — established.** feynman-x01 and
   monte_christo-v01-core vs ouroboros-v13-ladder, hunter-v22 and sinbad-v06,
   both sides:

   | Map set | feynman-x01 | monte_christo-v01 |
   |---|---|---|
   | fresh (prison_boxes, room_grid, corridor_start; 18 games) | **14–4** | 13–5 |
   | holdout TFX (11 maps; 66 games) | 42–24 | 43–23 |
   | combined | 56–28 | 56–28 |

   Baseline profile on TFX: dominates hunter-v22 (21–1), even with
   ouroboros-v13 (11–11), slightly behind sinbad-v06 (10–12); compact classes
   arena_TFX 2–4 and Colosseum_TFX 2–4 are the weak cells — consistent with
   the lineage's known compact-map exposure. On this slice feynman-x01 and
   Monte Christo are level; valjean's measured edge came from the original
   13 maps and the dilemma/autarky portal fixes. Feature screens must
   therefore watch the compact cells specifically.

## 4. Evidence carried in (prior art and failure modes)

Most of the ten ideas have been tried in *some* form. The failed forms define
what a Feynman attempt must do differently:

| Prior experiment | Result | Constraint it imposes |
|---|---|---|
| Drake v08/v09 EWMA density + K_DENS radio | Aggregate tie (0.366 vs 0.370); flips big_empty and the ouroboros matchup; changes *who* it beats, not how much | Density features are map-class-conditional; per-map evaluation mandatory, aggregate promotion forbidden |
| Drake halflife validation | Prediction-optimal: enemy 5, ally 12 rounds; zone-danger wants ~30 | Prediction-optimal ≠ decision-optimal; validate the estimator offline with features off (byte-identical games), then choose consumption memory separately |
| Drake v08 two-density-ray schedule | Cost ~8 aggregate points by starving self packets | **Slot allocation is the binding messaging constraint**, not encoding cost; every new report names which ray it displaces |
| Drake v10 dual EWMA (long halflifes 40/90) | Regression 0.312; big_empty collapsed 9–13 → 1–21; v11's fix (25/40) still lost big_empty | Long-window halflife must stay ≪ the 500-round horizon (≤ ~25–40); never feed the saturated long map into a spatial-contrast term; use surge (short−long) and log-ratio as features |
| Drake v10 time-ramped danger (0.6→1.4 over r60–300) | Late over-avoidance ceded crown-race food | **Time is a gate, not a multiplier**: switch regimes at rounds, never ramp avoidance/valuation continuously with time |
| Aramis v02 isotropic count-gradient frontier (b = (E−A)/(A+E+1), staged at −0.15) | Screen 14–10, fresh reserve 5–7 vs density control 7–5 — did not generalize | Isotropic footprints ignore walls/portals; gradients must be **route-aware** (connected space), persistence-gated, multi-source, and abstain on uniform/stale fields |
| Javert x02 type-7 length-density radio (44-bit, second reserved ray, merge guard on sender+round+rounded position) | Fresh reserve 10–2; the entire gain was 3 confined-map conversions; **the information layer alone**, with zero policy consumption | The only radio change in the programme that survived a fresh reserve; F1 ports this packet discipline onto valjean's mass.py; info-only cell before consumption |
| Javert F2/P3 (openness REPRODUCE demotion, saturation attack boost) | Outcome-neutral on the reserve, −1 on the screen | Topology-conditioned policy features are unproven as *score adjustments*; F2 normalizes the density *measurement* first, not the score |
| Valjean rejected: crowding/enclosed split penalties; dead-end pearl devaluing (halved intake); region-level gathering; enemy-mass pressure (inconclusive, ~16 games, slightly negative) | Null or negative | Density consumption via **split penalties and target devaluation has failed**; consume density in target *selection* and objective *mode* instead; pocket farming is the economy — never devalue it |
| Stats summary (60k-game synthesis) | Population/expansion +0.1044 and pearls/round +0.0677 dominate; cap timing +0.00145; opponent kills −0.0002; interactions +0.0017 | Features must serve resource access, growth and survivable distribution — not kill volume or cap racing; prefer interpretable main effects over interactions |

## 5. Feature programme

Ordered by dependency, not by the brief's numbering. Each item: hypothesis,
surface, and the evidence required to keep it. All are default-off parameters;
screens are one feature at a time against x01 on identical fixtures.

**F1 — length-weighted density radio (brief #3, port of javert x02).**
Valjean's `comms.py` already carries T_MASS as type 7 in the exact javert
layout (x:6 y:6 round:9 sender:9 ally:7 enemy:7, saturated at 127, inside the
tag+checksum envelope that rejects foreign payloads); `mass.py` keeps one
latest report per original sender with origin-time preserved. The F1 delta is
the remaining javert discipline: relay of length packets switched off behind
`mass_relay`, a sender-id aliasing guard (never send when id ≥ 512), and a
`mass_trace` validation log of raw observations for offline EWMA fitting.
Cell F1A is **info-only** (`mass_rays=1`, `mass_relay=0`; nothing consumes —
pressure/support stay 0). Required evidence: estimator predictions match
next-turn observations with features off; then a screen where the displaced
food-gossip ray costs nothing measurable on any map class.

**F2 — topology-normalized density (brief #6; the genuinely novel one).**
Each dragon already builds its own map in world.py; topology.py floods
bounded reachable room. Divide density by **connected** reachable room around
the query cell (route-aware, wrap- and portal-aware), so equal counts in a
corridor and in open water read differently. This fixes the confound that
killed the isotropic gradient before any gradient is attempted. Consume
first as a *measurement* inside existing scores (e.g., crowd/trap features
that already exist), not as new score terms. Required evidence: the
normalization separates corridor from open fixtures in trace diagnostics;
screen non-negative; per-map breakdown shows the effect concentrated on
walled/compact maps.

**F3 — friendly-density consumption (brief #1) in target selection and
split-site choice.** The EWMA field exists (density.py: fuzzed counts over a
fuzzed EWMA position, dedup by source, portal-jump reset). Consume it to
*select among* existing GATHER/REPRODUCE objectives — spread collectors
across under-served bed regions, prefer split sites with room — never as a
penalty on splitting or a devaluation of pocket pearls (both rejected forms).
Required evidence: higher pearls/round and new-unit survival in traces, then
a paired screen gain.

**F4 — enemy-density consumption (brief #2) in RETREAT direction and
long-dragon protection.** Retreat and hunt-avoidance objectives read the
enemy field through the F2-normalized measurement. Sinbad's known leak —
~9 long dragons per big_empty game killed by short enemy heads — is the
target mechanism. Required evidence: reduced attributed length lost to short
enemies on big maps, without a big_empty economy regression (the drake-v09
sensitivity).

**F5 — route-aware density gradient (brief #9).** Only after F2. Estimate the
friendly/enemy balance gradient over *connected* space; require multiple
fresh, spatially separated sources, persistence across turns, and abstention
on uniform/stale/single-source fields (the aramis-v02 guardrails, kept).
Express as objective modes — advance/withdraw waypoints on the allied side of
the frontier — inside SCOUT/RETREAT, never as heading commands. Required
evidence: the abstention path fires on uniform fields in traces; a screen
gain that survives the fresh reserve, which is exactly where v02 failed.

**F6 — dual-window EWMA (brief #8).** Only after single-window consumption
pays. Short window from drake's validation (enemy ~5, ally ~12); long window
≤ 25–40 (the v10/v11 bound). Features are surge (short−long) and clamped
log-ratio; the long map is **never** a spatial-contrast/territory term.
Validate halflifes by prediction with features off, then by decision.
Required evidence: prediction gain over the single window, then a screen gain
that does not collapse big_empty (v10's exact failure fixture).

**F7 — time and own-size conditioning (brief #4, #5).** Gates, not
multipliers: round-indexed regime switches (production → conversion windows
that already exist as split_stop/grow_from) and own-length classes
(short forager vs long carrier read density differently). Keep as separate
binary/categorical features; the stats evidence (+0.0017 for interactions)
warns against continuous interaction terms. Required evidence: the gate fires
in the intended regime in traces; screen gain concentrated in that regime.

**F8 — messaging protocol revision (brief #7).** A standing ledger, revised
as F1/F6 need rays: current earners are food gossip, portal pairings,
crown/prey; new density reports must displace only the lowest-value slot
(drake v08's lesson). Encoding invariants, already partially present, made
explicit and tested: type tag + checksum so enemy/garbled payloads are
rejected (drake K_DENS), round stamp, sender-id merge guard, saturation caps,
origin-time preserved through relay (no age refresh). Required evidence:
zero decode faults and no displacement regression on the gossip/portal
channels in an info-only screen.

**F9 — held-out candidates (brief #10).** Bed-renewal congestion (denied
spawns from body occupancy — the stats summary's distribution caveat),
corpse-field EWMA (O's enemy-corpse signal), information-value SCOUT
refinement. Each needs its own hypothesis card before a screen slot.

## 6. Validation protocol

1. **Estimator validation before decision validation** (drake method): with
   all consumption off, variants play byte-identical games, so predicted
   density can be compared against next-turn observation without confounds.
   F1's `mass_trace` log emits the raw observation stream; any halflife is
   fit offline from that single run.
2. **Screens**: ≥ 150 games spanning original, transposed and flipped maps
   (sinbad's noise measurement: single parameters ±3–5 per 100 games,
   tie-break noise ±10 per 108; valjean: ±6 net wins per 156 fixtures is not
   signal). Paired `compare.py` against x01, per-map breakdown mandatory.
3. **Selection and promotion**: fresh reserve (valjean `fresh` set + TFX
   holdout, played once for the Gate Zero baseline — the *outcomes* are
   recorded there for paired comparison) with the selection rule written into
   `tools/feynman/selection_rule.json` **before any screen outcome is read**
   (javert pattern). Screen gains that do not survive the reserve are
   recorded as development evidence, not promoted.
4. **2×2 for combinations**: promising features combine only against both
   single-feature cells and x01.
5. **Mechanism metrics alongside wins**: did the feature's decisions fire,
   pearls/round, new-unit survival, attributed length lost, crown conversion,
   per-map class — per the stats summary's ordering (resource access and
   growth first; never kill counts).
6. **Judge metering on every promoted variant** against the Gate Zero
   ceiling; deterministic repeated fixtures are not independent samples and
   are never counted as such.

## 7. Open questions

- Gate Zero measured the judge margin at 18.6M points (worst turn 81.4M of
  100M, big_empty vs hunter-v22). F2's extra floods and F1's second-ray work
  need per-variant budgets set against this ceiling before screens, not
  after.
- Does topology normalization (F2) belong in the estimator (density field
  stores room-normalized values) or at consumption (raw field, normalized on
  query)? Provisional default: **at consumption** — the raw field stays
  comparable with drake/javert validation data; revisit if query cost forces
  caching.
- Whether F1's length packet displaces food gossip (javert's choice) or an
  idle ray first — valjean's scheduler already prefers idle rays and
  displaces only food; the F1A screen measures that exact cost.
- The reserve maps were generated for portals/confinement; big-map generality
  of every confined-map gain must be re-established (drake's big_empty
  collapses twice show the failure direction).

## 8. F1 cell record (2026-09-26) — length-density radio, info-only

**Implementation** (`build/feynman/dev`, all behind default-off params;
`tools/feynman/test_f1.py`, 20 checks pass): `mass_relay` gates the every-
other-turn relay of peer mass packets (F1 sets it 0, per javert's no-relay
discipline); a sender-id aliasing guard refuses to send when id ≥ 512;
`mass_trace` emits per-turn raw observations (`LOG FM`) for offline estimator
validation. No comms change was needed: T_MASS is already type 7 in the
javert layout inside the tag+checksum envelope. With defaults the dev copy
reproduces x01 on all six parity fixtures exactly.

**Estimator validation** (`tools/feynman/ewma_fit.py` on 4-map trace runs,
35,385 predicted turns, consumption off): ally length-sum MSE is minimized
at half-life 5 (hl 5–6 a plateau; the inherited 6 is within 0.4% of optimal
and stays for parity); enemy MSE is minimized at half-life 2 (hl 2–3 a
plateau, both overall and conditional on enemy visibility, n=9,079). The
inherited single half-life of 6 is ~22% worse than optimal on the enemy
signal — when consumption arrives (F4), a split `mass_half_life_e ≈ 2–3` is
the candidate parameter. Directionally consistent with drake's enemy-shorter-
than-ally finding, at shorter absolute values for length sums than counts.

**Info-only screen** (dev@f1a: `mass_rays=1, mass_relay=0` vs x01; pool
ouroboros-v13 + sinbad-v06; 9 maps covering compact/structured/big/portal
classes, both sides; 36 fixtures per cell): **f1a 18–18, x01 19–17**; paired
diff 5 of 36 fixtures changed (3 losses, 2 gains, all length decisions or
elimination swings), no map class moved systematically. The displaced
food-gossip ray costs nothing measurable, as required for the channel to
exist. Sandbox metering on big_empty A vs hunter-v22: worst turn 82.9M
(x01: 81.4M on the same fixture) — the ray work costs ~1.5M points, inside
the Gate Zero ceiling.

**Deviation from the §6 protocol, honestly recorded:** the full 24-map + FX
screen was reduced to this 36-fixture development screen because the live
benchmark campaign saturates this machine (load 22–34; runs throttled to
6 jobs to stay clear of the campaign). The full T/FX screen and the fresh
reserve remain required before any F1B *consumption* cell can promote; FX is
deferred to the promotion phase. Two big_empty B fixtures flipped to losses
and are watch items for that screen (drake's big_empty sensitivity), but two
fixtures establish nothing.

## Session archive

Freeze manifest: `tools/feynman/frozen.json`. Unit checks:
`tools/feynman/test_f1.py` (F1 packet discipline, 20 checks). EWMA
validation: `tools/feynman/ewma_fit.py` + `build/feynman/traces/fm_*.log`.
Arena runner preserved as committed bytecode after the sync incident:
`tools/feynman/arena.cpython-313.pyc` (sources under `tools/valjean/` and
`tools/sinbad/` were deleted from the working tree by the sync; the result
cache `build/valjean/cache.jsonl` survived). Parent ledger:
docs/valjean.md (`valjean.md`) (every rejected feature, with results). Method
references: docs/javert.md (`javert.md`) (packet discipline, selection rules),
drake v08–v11 READMEs (EWMA validation and the dual-EWMA failure),
docs/aramis-frontier.md (`aramis-frontier.md`) (the gradient reserve failure),
STRATEGIC_STATS_SUMMARY (`STRATEGIC_STATS_SUMMARY.md`) (development ordering).

2026-09-26 incident: a repo sync process deleted untracked working-tree files
twice mid-session (`docs/feynman.md`, `tools/feynman/`, later
`tools/valjean/`, `tools/sinbad/` and parts of `tools/ouroboros/`).
`bots/`, `build/` and committed files survived. All Feynman artifacts were
regenerated or preserved and are now committed to git after each step.

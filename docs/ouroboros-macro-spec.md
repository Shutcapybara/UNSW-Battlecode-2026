# Ouroboros macro spec — from exploration to one tunable bot

2026-09-24. Author: Claude (Ouroboros line). This spec replaces "try a feature and
see". It sets out what the bot has to decide, how those decisions are
parameterised, and the order to build and tune them, with gates.

Sections:

- §1 evaluates the four cross-line reviews and the hunter line (v05–v20).
- §2 states the game model.
- §3 is the core formalism: actions → options → roles → doctrine, with θ at each level.
- §§4–11 specify each subsystem.
- §12 is measurement.
- §13 is the build plan.
- §14 assesses task complexity and which model tier suits each part.

Everything is written against the champion `ouroboros-v10-beacon`.

---

## 1. Evidence: what the reviews and the hunter line tell us

### 1.1 Current measurements (v10, fresh runs today)

| Set | Contents | v10 |
|---|---|---|
| **X** cross-series | widefast × hydra-v09, hydra-v10, kraken-v04, leviathan-v07 (261) | **238–23** |
| **C** old C++ swarms | widefast × fry-v12, fry-v14, hunter-v04 (198) | **161–37** |
| **H** new hunter | widefast × hunter-v16, hunter-v20 (120) | **66–54** |
| H, compact maps | arena, Colosseum, default_small, devil, trophy (+_T, _FX) | **7–53** |
| H, open maps | default, queen_of_spades, schooltime, stronghold, trauma (+_T, _FX) | **59–1** |
| **S** hunter progression, compact maps | vs hunter-v04 / v14 / v15 (30 each) | 20–10 / 14–16 / **4–26** |

hunter-v20 against the rest of the field (full maps, both sides): **50–1–37**. By opponent: leviathan 16–6, hydra-v10 14–8, fry-v14 11–11, kraken 9–1–12. By map class: compact **37–1–2**; open **13–35**, and 33 of those 37 losses came at the round-500 length tiebreak.

**Headline.** hunter-v20 and ouroboros-v10 are mirror images.

- Hunter wins the compact-map production war.
- Ouroboros wins the open-map survival and length race.

Neither can express the other's strategy. Distilling both into one parameter space is the main design goal.

### 1.2 Why hunter wins compact maps (phase data, v10 vs hunter-v15, 7 compact maps × 2 sides)

| Rounds 0–30, per game | v10 | hunter-v15 | for reference: v10 vs hunter-v14 (loss / win games) |
|---|---|---|---|
| pearls eaten | 13.9 | **43.6** | 28.4 vs 31.6 / 26.7 vs 14.2 |
| splits | 5.6 | **18.1** | |
| units at round 30 | 4.3 | **11.6** | |

In rounds 30–100 hunter-v15 eats 105 pearls to our 21 and reaches 27 units to our 4. The game is decided by round 30.

What changed between v14 (a coin flip against us) and v15 (4–26) is the team information layer:

- a replicated team summary: unit count and largest lengths;
- pearl-bed "hotspots", with countdowns, shared over sonar;
- sector-coverage bitmaps that steer exploration.

The opening pearl intake roughly tripled relative to ours. This is attribution by version diff, not by ablation, but the mechanism is concrete: dragons walk to beds before the pearls appear. In `growth_action` a pearl counts as a target when `countdown < route distance`.

The hunter policy is a fixed priority ladder:

1. portal trip
2. boost-surround or trap attack
3. head attack (only if units ≥ 3)
4. yield on MOVE_ASIDE
5. `SPLIT 2` whenever length ≥ 4 and below the unit limit
6. owned pearl
7. explore (hotspot pull + unscouted-sector pull + friend spacing)

The split rule is the whole economy. Every second pearl becomes a unit, and the population compounds. Our evaluator prices a split against head risk, newborn exits and spawn windows. On compact maps that caution costs a factor of 3 in production.

The hunter line still self-harms: 19 self and 21 wall deaths per game against the field. It wins because production outruns the losses. It loses open maps because it has no crown: final longest dragon is 4–8.

### 1.3 The four reviews, evaluated

All four reviews benchmarked **v05**, not v10, and none included hunter-v15+. Their rankings are stale. Their mechanism findings mostly still stand.

| Claim | Source | Verdict |
|---|---|---|
| Ouroboros wins by not dying (≈111 deaths/game vs 180–210) | GLM, Kimi | **Correct**. It is still the core of our open-map strength. |
| Side-B fragility (13 of 14 rr2 losses as side B) | GLM | **Plausible, unmeasured on v10.** The ledger must report side splits (§12). |
| Term proliferation without ablations | GLM | **Correct.** P0 addresses it. Sweeps around v10 are flat, which suggests several terms are dead weight. |
| Local wall-clock over 180 s on help | GLM | Correct and a harness cost only. Keep `--timeout 1200` for Python pools. |
| Zero wall deaths come from doom memory | Kimi | **Wrong attribution.** They come from exact candidate simulation: every path is stepped through known terrain and bodies. `w_doomed` has been 0 since late v05. |
| Probabilistic p_strike is "validated" | Kimi | **Overclaim.** p_strike sweeps were flat. The death gap is confounded with simulation, traffic terms and ownership. |
| crown_memory staleness (40 rounds) | Kimi | Was fair; v10 beacons with TTL mostly fix it. Time-limited claims (§6.4) finish it. |
| 2-segment children are the meta | Kimi | **Correct**, and hunter confirms it (`SPLIT 2`). Kimi's own 3-segment role encoding is a cost. |
| O1: stale pearls counted as present in simulation | GPT | **Valid.** Optimistic material and body prediction; fixed in P2. |
| O2: 8-bit portal ids, and direct observation cannot correct gossip | GPT | **Valid, latent** (no current map has id > 255). Fixed in P2 with 16-bit ids. |
| O3: no crown demotion; several short crowns | GPT | **Valid; fixed in v10** (beacon + `crown_demote`). |
| Ouroboros opening failure on arena vs hydra | GPT | **Valid, and it is the main open weakness.** Hunter-v15+ exploits it far harder (§1.2). |
| Zero births from round 380 | GPT | True by design (crown/feed phase). Worth one ablation, since late replenishment might help against swarms. |
| v01 README 158–38 not reproducible | GPT | Fair. The ledgers lived in a VM scratch folder. From now on ledgers go in the repo (§12). |
| Status note names v05 champion | Claude (own) | **Stale.** v10 is champion. My local parameter sweeps are flat, so further gains need structural change, not nudges. v11 (split spawn window) was a null result. |

What all the reviews missed: the decisive axis is **map class** (compact vs open), not opponent. Every line is a specialist on one class.

### 1.4 The best ideas in the repo, by source

| Idea | Where it comes from | Where it lands in this spec |
|---|---|---|
| One evaluation in length units; exact path simulation; probabilistic threat | Ouroboros | §4, §9 |
| Pearl ownership (route-distance deconfliction) | fry-v14, hunter-v06, Ouroboros | §7 |
| Crown election, beacon, feeding; parent→child sonar hand-off | Ouroboros | §6 |
| Split at a length threshold (production-first) | hunter | §8 (a production parameter) |
| Pre-positioning on bed countdowns (`countdown < distance`) | hunter-v15+ | §5, §7 |
| Replicated team summary instead of per-dragon lists | hunter-v15 | §10 |
| Hotspot and sector-coverage packets with TTL | hunter-v15/v20 | §10, §7 |
| Single scout claimed over sonar with TTL; portal trips planned with a return route | hunter-v17/v20 | §6, option `portal_trip` |
| Boost-surround / cutoff traps with strict visibility preconditions | hunter-v16 | option `trap` |
| Self-trap continuation-depth check | hunter-v18/v19 | §9 (safety filter) |
| MOVE_ASIDE yield signal; 20-bit lifetime ids | hunter-v04/v08 | §10 |
| Net material accounting; confirmed pearls fund sprints | Leviathan | §4, §5 |
| Action-stream equivalence checks; regression tests | Leviathan | §12 |
| Chase horizon ≤ 6; distrust gossip older than ~15 rounds | Hydra | §9, §10 |
| Bed predictions; relay with TTL | Kraken | §5, §10 |

---

## 2. Game model

- **Two games in one.**
  - The swarm war is elimination by attrition: head trades are 1-for-1, and moving into a body kills only the mover.
  - The crown race is decided at round 500: longest single dragon first, then total length.
- **Production compounds.** Units × pearl intake decides the swarm war. On compact maps it is decided by round 30–50 (§1.2).
- **Length is safety plus score.** A long crown cannot be traded evenly: a head trade kills both, so a crown must never meet an enemy head. A crown wins the tiebreak on its own.
- **Information is local.**
  - Each dragon is a separate process. It sees only its own vision and 64-bit sonar rays that stop at the first body hit.
  - Team knowledge is whatever diffuses along those rays.
  - A ray fired back into the sender's own body exits at the tail. That gives a parent→child channel at birth.
- **Determinism.** A (map, side, bot pair) is one exact game. Samples come from maps and variants, not from repeats.

**Phases.** Round thresholds are defaults; state triggers are hypotheses to test.

| Phase | Default rounds | Objective | Dominant decisions |
|---|---|---|---|
| Opening | 0 – ~40 | maximise production rate | split threshold, bed pre-positioning, scouting |
| Midgame | ~40 – crown_start | control territory, win the exchange | ownership, frontier hunting, trades priced by parity |
| Consolidation | crown_start – feed_start | grow one crown, stop wasteful splits | crown election, protection, gatherer yield |
| Endgame | feed_start – 500 | bank length | feeding, crown safety, no risky trades |

---

## 3. Core formalism: actions, options, roles, doctrine

The user's requirement is that the bot's parameters cover both what actions exist and how they are chosen, so that from here on the work is tuning. This is the structure that does that.

```
Engine actions   MOVE path(1..k) | SPLIT n | SONAR ×4        (fixed by the game)
      ▲
Options          goto(target) · strike(head) · trap/surround · portal_trip ·
(macro-actions)  dive(portal) · split(n) · yield · feed · flee · spread
      ▲  each option: generator(state) → candidate engine actions, + precondition
Roles            role r = ( enabled options mask,
                            target selector weights  θ_sel[r],
                            eval weight slice        θ_eval[r],
                            constraints              θ_con[r]  (max chase, min exits, split rules) )
      ▲
Doctrine         θ_team(map_class, phase) = ( role mix schedule, production target N*(t),
(team level)                                  split threshold, trade thresholds,
                                              crown_start / feed_start, scout quota )
```

**Per-turn decision** (the chess-bot part):

1. The role picks a **target** with its selector (§7).
2. Every enabled option generates **candidates**. Each is simulated exactly for body, pearls and portals.
3. **Hard safety filters** remove certain deaths (§9).
4. Each survivor gets **score = Σ θ_eval[r]·features**, in length units (§4).
5. Take the argmax.
6. The sonar scheduler fills the four rays (§10).

**The rule that stops term proliferation.** Every feature must approximate a change in a single **team evaluation** V (§4). A new idea enters the bot in one of three forms:

- a new *option*, with a generator and preconditions;
- a new *feature*, with a named V-component;
- a new *parameter* on an existing one.

Anything that fits none of these is not added.

**What "tuning" then means.** θ = {θ_team per map class × phase, θ_role per role, θ_tactics shared}. That is roughly 60–100 numbers, with named ranges, all in `params.py`. The hunter ladder is one point in this space:

- split threshold 4;
- the options ordered by fixed priorities, which is the limit of large weight gaps;
- no crown.

v10 is another point. **The convergence test for the architecture is that both points are expressible, and each map class gets tuned to the better one.**

---

## 4. Evaluation function

**Team value**, used for doctrine and to justify dragon-level features:

```
V = λ_len(t)·Σ len  +  λ_unit(t)·units  +  λ_crown(t)·f(ourLongest − theirLongestKnown)
    + λ_ctrl(t)·Σ_zones density·control  −  risk
```

- `λ_unit(t)` = expected future net pearl income of one extra unit × rounds left until consolidation. It starts high and falls to 0 at feed_start. This one number is what should make early splitting aggressive on compact maps. Today it is implicit in `split_value`; P3 makes it explicit.
- `λ_crown(t)` is zero before crown_start and dominant after feed_start.

**Dragon action score**, in length units:

- **net material:** the Leviathan rule. Pearls eaten minus sprint cost, counting only confirmed pearls for funding.
- **unit delta:** split = +λ_unit − newborn risk; own death = −(len + λ_unit + crown premium).
- **trade value:** p(strike) × (value of enemy dragon − value of ours). This uses the same dragon value, with enemy λ_unit estimated from the enemy unit census.
- **position:** target progress (the selector's value / eta), exits, crowd/traffic, zone danger.
- **information value** for scouts (§7).

Feature families to keep, pending the P0 ablation:

- material
- target progress
- threat
- exits / continuation depth
- crowd / traffic
- ownership
- crown feed / protect
- split value

Feature families to prove or delete:

- tunnel memory
- doom
- zone heat
- spread term
- blind-portal term

---

## 5. World model

| Layer | Content | Status in v10 → spec |
|---|---|---|
| Terrain | edges learned from vision; portals with **16-bit** ids; direct observation overrides gossip | 8-bit portal ids, gossip sticky → fix (P2) |
| Symmetry | infer map symmetry (rotation or mirror) from our spawn and early terrain; mirror terrain and bed timers | absent → add (P4). Doubles map knowledge for free. |
| Pearls | three states per cell: **confirmed** (seen this turn), **remembered** (seen at round r, may be gone), **predicted** (bed countdown / respawn estimate) | remembered pearls treated as confirmed in simulation (O1) → fix (P2) |
| Beds | set of spawn cells; countdown when visible; learned respawn gap; mirrored partner | partial (K_BED) → formalise (P2) |
| Zones | 8×8 grid: bed yield rate, current pearls, ally presence, enemy heat, last-seen round | enemy heat only → full zone table (P4) |
| Allies | replicated summary (units, largest lengths, crown position) + recent self-reports for traffic | per-dragon reports → add summary (P3) |
| Enemies | sightings with position, length, round; decay; census lower bound | present; add census (P3) |

Rules:

- Only confirmed pearls fund a sprint in simulation. Remembered and predicted pearls are targets only.
- A predicted pearl is valid as a target when `countdown ≤ eta`. This is hunter's pre-positioning, and it is the single biggest opening lever measured.

---

## 6. Specialisation: roles

### 6.1 Role set

| Role | Purpose | Options enabled | Selector emphasis |
|---|---|---|---|
| **gatherer** | convert pearls into length and units | goto, split, yield, flee, spread | pearl value / eta, owned, safe zones |
| **hunter** | contest frontiers, take favourable trades | goto, strike, trap, flee | enemy-rich zones at our frontier, chase ≤ 6 |
| **scout** | map terrain, beds and portals, then broadcast | goto, portal_trip, dive, flee | information value, unscouted sectors, unmatched portals |
| **crown** | become and stay the longest dragon | goto (pearls), flee; no split except emergency | pearls in safe zones; never within strike range of a head |
| **feeder** | in the endgame, die next to the crown to drop pearls | goto(crown), feed | crown position |

A newborn inherits a role via the hand-off packet. Roles are **weight slices, not code branches**: one evaluator, with the role selecting θ.

### 6.2 Assignment at birth

The parent picks the child's role from the doctrine mix for (map class, phase), corrected by the census: known units per role from the team summary. v10 already does this with fixed mixes; in the spec the mixes are θ_team entries per map class.

### 6.3 Transitions (state machine; each threshold is a parameter)

- scout → gatherer when the known-sector fraction exceeds `scout_done`, or the scout quota is exceeded (claim over sonar with TTL, as in hunter-v20).
- hunter → gatherer when len ≥ `hunt_max_len`, or no enemy has been seen for `hunt_idle` rounds.
- gatherer → crown by election (§6.4).
- crown → gatherer on demotion.
- non-crown → feeder at feed_start if len ≤ `feed_max_len` and the crown is within `feed_range`.

### 6.4 Crown election

- A candidate claims the crown with (len, id). The stable tie-break is longer length, then lower id.
- The claim is a beacon with TTL. It lapses if not renewed within `crown_claim_ttl` rounds.
- Demote on hearing a live claim with len ≥ ours + `crown_demote`.
- An emergency split hands the claim to the child.

v10 implements all of this except the timed lapse.

---

## 7. Targeting: exploration vs exploitation, pearl density

Each role's selector scores candidate targets:

```
value(target) = E[pearls]·w_pearl / (eta + c)            # exploitation
              + β(role, phase, known_frac)·info(target)  # exploration
              − w_danger·zone_danger − w_crowd·allies_near − ownership_conflict
```

- **E[pearls].**
  - A confirmed pearl counts 1.
  - A remembered pearl counts p_still_there(age).
  - A predicted pearl counts 1 if countdown ≤ eta, otherwise 0.
  - A zone target is the zone's bed yield rate × time spent there.
- **info(target)** = unknown cells revealed along the path + unscouted sectors + unmatched portals. Unknown zones get a prior density equal to the map mean plus an optimism bonus `c/√(n_obs+1)` (UCB-style).
- **β** is large for scouts, small for gatherers, and 0 for the crown. It decays with the known-map fraction and the phase.
- **Ownership.** One dragon per pearl, decided by route distance, with ties broken by id. Claims ride on self-reports; hunter-v06/fry-v14 show this matters.
- **Density.** Zone yield rate = observed spawns / observed time, from bed countdowns and redraws. It drives where gatherers settle and where the crown lives: high-yield zones that we control.

---

## 8. Production controller

- **Target trajectory N\*(t, map_class).** Units desired over time. Splitting is valued through λ_unit(t) (§4) plus a correction `w_prod·(N* − units_known)`.
- **Split threshold.** Minimum length before a split is allowed. Hunter uses 4 (child 2, parent 2). This is a θ_team parameter per map class. v10's effective threshold on compact maps is much higher, because the split competes with gathering in the evaluation.
- **Birth safety.** The newborn needs at least `min_child_exits` free neighbours and must not be in threat cells. Keep this (v10). Measure the cost on compact maps in P3: the hunter gets away without it.
- **Stop production** at crown_start for the crown, and at feed_start for everyone.

---

## 9. Tactics and safety

**Hard filters**, applied before scoring:

- exact simulation of each candidate;
- no move into certain death;
- continuation depth ≥ `min_continuation` after the move (hunter-v18/v19 style, replacing the doom/tunnel heuristics if P0 shows they are dead).

**Threat.** For each enemy head within k steps, p_strike(k), multiplied by the value exchanged.

**Aggression options.**

- **strike:** head trade. Allowed when trade value > 0, or when the parity rule holds: `units_us / units_them ≥ θ_parity(phase)` and we are not the crown. Equal trades favour the side with more production.
- **trap/surround:** hunter-v16. It needs the full enemy body visible and a size lead after paying the boost cost. It is an option with a precondition, not a mode.
- **crown kill:** a large bonus for a trade against the enemy's longest dragon late in the game, within the chase horizon.
- **chase horizon** ≤ `max_chase` (default 6): far chases starve (Hydra and Kraken both found this).

**Traffic.** Keep the crowd and traffic terms. Add a MOVE_ASIDE-style yield packet if ally head-on collisions stay above about 0.5 per game.

---

## 10. Information propagation

Rays are scarce: 4 per dragon per turn, each 64 bits, each stopping at the first body. The unit of design is therefore the **packet catalog plus slot scheduler**.

| Kind | Payload (≈58 bits after tag/checksum) | Consumer | Freshness |
|---|---|---|---|
| SELF | id16, cell, len, role, heading | ally registry → traffic, ownership, census | 1 turn; stale after 20 |
| SUMMARY | units_known, our longest, their longest, enemy census, round | doctrine (λ_unit, parity), crown | merge by max-with-age (hunter-v15) |
| HOTSPOT / BED | cell, due-round, strength | gatherer and crown targeting | TTL ≈ 8 after due-round |
| COVERAGE | sector bitmap chunk | scout targeting | static, rebroadcast slowly |
| PORTAL | id16 pair / endpoint | terrain | static; direct observation wins |
| ENEMY | cell, len, round | hunters, threat, census | ≤ 15 rounds |
| CROWN | cell, len, round, claim TTL | election, feeding, protection | relay 3 hops |
| CLAIM | target cell, owner id, expiry | ownership beyond vision; scout quota | expiry |
| HANDOFF | role, target, (seed facts) | newborn | once, at birth |

**Scheduler.** Each turn, fill 4 slots in this priority order:

1. the hand-off, if splitting;
2. self, at least every other turn;
3. the highest (novelty × consumer weight) packet from the relay queue.

Never resend the same fact within `resend_gap`.

**Rule:** a packet kind with no consumer that shows up in an ablation gets deleted.

---

## 11. Compute

Budget: 100M points per turn; stdout writes cost 2.5M each. Current v10 on big_empty: p50 29M, p99 48M, max 69M.

Stage order and caps:

1. sense
2. hear
3. world update
4. selector (cached waypoints, every few turns)
5. candidate generation
6. simulation and scoring

A degradation ladder applies when a turn runs long: drop sprint depth, then drop the zone rescan, then fall back to the one-step safe move. Big-map sandbox pricing is part of every promotion gate.

---

## 12. Measurement protocol

- **Ledger in the repo:** `build/ouro/ledger.jsonl`. One line per (version, set, opponent, map, side, result, round, cpu). Each version README quotes it. My runs so far lived in VM scratch, and that is how the v01 figure became unverifiable.
- **Benchmark sets:**
  - X, C and H (§1.1).
  - S: compact maps × hunter-v15 and v20, both sides.
  - B: 64×64 maps vs hydra.
  - J: sandbox, big_empty and trauma, 2 opponents, both sides.
  - A hold-out variant set made by `mapgen.py` (new rotations) and never used for tuning.
- **Always report:** side A/B split, map class split, and the flip list against the previous version (`ouro.py compare`).
- **Refactors must be action-stream equivalent** on 16 native cases (the Leviathan practice). Behaviour changes are separate versions.
- **Ablation table** (P0): turn each feature family off in turn on X∪H. |Δ| < 2 net → delete in a clean-up version.
- **Promotion gate:**
  - target set improves by ≥ +4 net;
  - no other set drops by more than 3 net;
  - sandbox p99 < 60M and max < 80M;
  - README with numbers.
- **Tuning** (P5, once the architecture is in place): coordinate search or SPSA over θ_team per map class. Fitness is the win count on (map class × opponents × sides). Check the hold-out set afterwards. The `tools/evolve.py` that appeared in the repo can host this.

---

## 13. Build plan

| Phase | Work | Target | Gate |
|---|---|---|---|
| **P0 baseline** | ledger in repo; v10 on X, C, H, S, B, J, hold-out; side split; feature-family ablations | attribution | none (measurement); publish the table |
| **P1 core refactor** (`v12-core`) | split main.py into `world.py`, `comms.py`, `options.py`, `roles.py`, `doctrine.py`, `eval.py`, `params.py`; options and roles as data; delete dead families from P0 | structure | **action-stream equivalent** to v10 (minus deleted neutral terms, which get their own measured version) |
| **P2 correctness** | confirmed / remembered / predicted pearls (O1); 16-bit ids, direct-observation override (O2); timed crown claims | model fidelity | no regression on X, C, H |
| **P3 production** | λ_unit(t) explicit; split threshold per map class; bed pre-positioning; SUMMARY + HOTSPOT packets; census | compact maps | **S and H-compact: +15 net**, open maps unchanged |
| **P4 map knowledge** | zone table; symmetry inference; COVERAGE; scout claim quota; portal_trip option | exploration | H and X up; trauma / portal maps no loss |
| **P5 tuning** | automated θ search per map class; hold-out validation | convergence | hold-out ≥ tuned-set rate − 5% |
| **P6 aggression** | parity-priced strikes, trap option, crown-kill | swarm war | C and H up; devil vs hydra |
| **P7 endgame** | late replenishment ablation; feeding geometry; crown escort | length race | B and length-race maps |

**Status (cycle 1, 2026-09-25):** P0 done (v10 × gauntlet × 30 maps + hold-out;
compact 65-1-54, open 115-5). P1 done: `ouroboros-v12-core` (modules, doctrine
table, 16/16 equivalent). P3 done in a different form than planned: the
compact doctrine is hunter-v20's ladder as an option set (`ouroboros-v13-ladder`,
compact 99-1-20, hold-out 61-1-18, open unchanged) — the §3 convergence test
(both hunter and v10 as parameter points) is met. Next: P2 correctness, then
push past parity with hunter-v20 on compact (17-13): traps, trade doctrine, crown timing.

**Stop doing:** random single-parameter sweeps around v10. They were flat for v08 through v11.

**Success looks like this.** One codebase in which θ_compact beats hunter-v20 on compact maps and θ_open keeps v10's 59–1 on open maps, so H goes from 66–54 to 100+ out of 120.

---

## 14. Task complexity and model tiers

Tiers as marketed in September 2026:

- **Top tier** (Opus 5.5 / GPT-6 Astra): long, messy codebase reasoning, planning and review.
- **Workhorse** (GPT-6 Sol; Sonnet-class): near-frontier coding at a fraction of the cost.
- **Cheap** (GPT-6 Luna; Haiku-class): mechanical, bounded work.

This is advice, not a decision.

| Work | Difficulty | Suggested tier | Why |
|---|---|---|---|
| Diagnosing losses from replays and forming *one* mechanism hypothesis | hard: judgement over noisy data | top tier | This is where every real gain came from (traffic, ownership, portal dives, crown, now the opening). |
| P1 refactor with equivalence | hard: 1,750 dense lines, must not change behaviour | top tier, once | One careful pass; the equivalence test makes it checkable. |
| P2–P4, P6–P7 feature work against this spec | medium: well-specified, testable | workhorse | The spec plus a gate makes each task bounded. After P1 the modules are small enough to fit a cheaper model's context. |
| Running benchmarks, sweeps, ledgers, P5 tuning | mechanical, compute-bound | **no LLM**, or cheap tier to read summaries | Scripts should run them, overnight. A model polling 165 s chunks is the main waste of usage in my sessions so far. |
| Reviewing a promotion (flip list, CPU, README) | medium | workhorse | |

**Overall assessment.**

- The game is a hard design problem: multi-agent, partial information, adversarial, CPU-bounded.
- Once the framework exists, it is a medium implementation problem.
- The tuning is a compute problem.

Top-tier usage pays off at two points: the P1 refactor, and diagnosis after each benchmark. Implementation fits the middle tier. A cheap tier, or plain scripts, can do the rest.

The single most usage-efficient step is P1. Once the bot is split into modules, every later task loads one module of about 300 lines plus `params.py`, instead of the whole 1,750-line file.

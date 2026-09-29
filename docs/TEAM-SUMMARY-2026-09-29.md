# Just Keep Swimming — where we are and what we're doing (29 Sep 2026)

Written by the director session for the team. Dates: Sprint Tournament **1 Oct** (everyone, best of 7),
Qualifiers **10 Oct** (eligible teams, top 10 advance, seed = rating rank after the last autoscrims), Grand Final
17 Oct. Rating 1770–1780, rank ~55; ~250 Elo below the top ten. Evidence for every claim below is in
`docs/findings/` and `docs/analysis/`; decisions D-001–D-028 in `docs/findings/2026-09-28-director-decisions.md`.

## 1. What we now know (one day of measurement, ~9,000 field replays, 4 analysis passes)

1. **Local win share never predicted live win share** (slope 0.19). Everything evolved against our own bot zoo
   optimised for beating ourselves. We stopped using the zoo as a fitness function on 28 Sep.
2. **Games are decided early and by efficiency, not by production schedule.** Field-wide: top-30 eat 8.5 pearls per
   100 dragon-turns at 11.7 moves per pearl; band 7.6 / 13.2; us 6.8 / 14.8. Our opening is level with the band at
   r25 and one unit behind at r100; the economy behind the opening compounds to −15 pearls by r100, −20 length by
   r250. Pushing production by schedule was tried (P1, 1,226 games) and moves nothing: production is pearl-bound.
3. **The deficit is deaths, not income.** On Portals we out-eat the top ten (16.4 vs 11.4 pearls/100dt) and still
   lose four-fifths of everything we eat: trapped/mill deaths 126 vs band 63 length per 1k dragon-turns, newborn
   deaths 81 vs 33, portal-exit deaths 68 vs 44, small-dragon crowding 50 vs 28. Same shape on Slithery and
   Schooltime. The top ten's whole edge over the band is two leak classes: trapped (18.5 vs 32.8) and crowd23
   (2.7 vs 10.2).
4. **Portals: volume is normal, safety is not.** We transit at field volume (49 steps/game vs 47–56) and die at
   28.2 per 100 steps vs Cutlery's 12.5; 623 wall/self deaths within two rounds of a transit in 35 games vs
   Cutlery's 2; 548 friendly same-pair collisions vs 148. On the Portals map we take 399 steps a game (Cutlery 72).
5. **Python is at the ceiling.** 100 M CPU points per dragon per turn; a dragon over budget dies. Our live bots hit
   the cap (9508: ~7.7 timeout deaths a game; Tyr V12: 72 in 10 games) and Python's boot turn alone costs 46–51 M.
   We are the top Python team; the teams above are compiled. The C++ chassis (below) runs a whole turn in **3.9 M**.
6. **Schooltime is the top ten's map**: 41 units at r100 vs the band's 15, played as a swarm economy nobody else
   runs. From ten replays: split every starter 4→2+2 in r0–5, travel ~40 rounds, then a pearl-gated flywheel from
   r45 (split the moment length hits 4, always 2+2); children stay home and patrol a ~5×5 bed patch; 58–64 units by
   r100; bodies tiny (75 % length ≤ 2); portal use is a by-product. `docs/analysis/C1-E-schooltime-spec.md`.
7. **Prisoners Dilemma inverts**: the top ten win it with fewer, shorter dragons. No length race there.

## 1b. The tournament maps are unseen — the rule that governs everything below

The Sprint and Qualifier rounds are played on maps we have not seen. The public pool shows the organisers'
preferences (sizes, kelp densities, portal counts, bed layouts), not their guarantees. So: **no decision in any bot
may depend on map identity** — no map-name or atlas branches; anything map-dependent keys on structure the bot
measures in play (tile count, kelp density seen, portals found, bed density and spawn rates observed). The C++
chassis's map atlas is an optimisation with a hard off-switch, never a dependency; every candidate is measured with
it off on the generalisation panel (`maps/var` transforms, `maps/new` synthetic suite) beside the live pool, and a
candidate whose edge disappears off-pool is rejected. Full rule: `docs/hub/prompts/2026-09-29-C1-out-of-sample-rule.md`.
This cuts the other way too: teams above us have tuned to the ten maps for weeks; part of their edge is memorised.

## 2. Hypotheses on the table (each with what would falsify it)

| # | Hypothesis | Test | Falsified if |
|---|---|---|---|
| H1 | Compute headroom converts: a C++ bot with per-dragon routing out-paces the Python line on pearls/100dt and units r100 | C1-B three-arm ablation (yuna-v03 / cheap C++ policy / C++ router), exact pairs, then dev screen vs 545 | router − cheap < +2 units r100 with p > 0.2 |
| H2 | The material gap closes by closing leaks, not by eating more | Each leak fix alone on the chassis, exact pairs; accept only if its statistic moves *and* pearls-by-r100 rises | a fix moves its statistic but not pearls (leak moved, not closed) |
| H3 | Portal-exit knowledge (atlas + exit memory + probe) halves near-portal wall/self deaths without cutting transits | C1-D rules ablated on Portals/Default/Schooltime | deaths fall < 25 %, or pearls-by-r100 fall > 10 % on portal-heavy maps |
| H4 | The swarm flywheel (split-at-4, stay-home bed patrol) is reproducible and triggers on measured bed density, not on the map | chassis + router on Schooltime vs the corpus curve, then on `maps/new` maps with similar bed density | < 30 units at r100 on Schooltime, or the trigger fails to fire/misfires off-pool |
| H5 | Dev team 545 (rank ~15 swarm bot, separate 60 games/h allowance) is a proxy for the field band | dev screen → field confirmation, both measured | two dev-screen passes fail field confirmation (one strike so far: yuna-v03) |
| H7 | Every gain measured on the live pool survives with the atlas off on the generalisation panel | exact pairs on `maps/var` + `maps/new`, atlas off, for every candidate | edge on the pool, none on the panel |
| H6 | Later: per-dragon spatial state (EW densities), action memory, and leader-coordinated fights pay in play once compute allows | phase C2, after C1 | prediction without play gain (as before) |
| H8 | Bed guarding pays, and how much it pays depends on the information state it is keyed on. Four-arm ladder, same guard rule in each: (a) visible pearls and beds only; (b) per-unit memory of pearl/bed locations (Ares's current state: `pearl_seen` with TTL, `bed[]`, `spawn_at`); (c) per-unit memory with a decaying density field over smoothed coordinates; (d) (c) plus sharing over sonar payloads | R-2 lane mechanism or a directed R-6: guard propensity as a `params.hpp` weight, the four information states as switches, exact pairs on both panels, atlas off; report `bed_capture_share`, pearls/100dt, and deaths per guard-turn | no arm beats (a) on the economy gate; or (c)/(d) beat (b) only on the pool and not on `maps/new` |
| H9 | Each unit keeping its own map memory — pearl locations at minimum, and an estimated pearl density with decay — improves routing and bed choice at a CPU cost the C++ budget absorbs. The single smoothed-coordinate density (S-1) remains the reference design; per-unit decayed density is the cheaper variant | R-5's exposed weights on the density term; CPU probe on dense fixtures; both panels | economy flat with the term on, or per-turn max over the R-1 wall |
| H10 | Phase bifurcation from an algorithm change is a feature, not a defect: when a movement-search change makes the early game worse and the late game better (interim R-1/`ra` reading), and the split is driven by the algorithm rather than by a change in the macro sufficient statistics (units, length, bed count reached), the right response is phase-conditional logic — two search profiles selected by measured state with the clock as a soft prior — rather than a compromise setting | (1) Decompose the r50→r250 delta by phase: economy checkpoints and tier-2 rates per phase, on both panels. (2) Composition check as in D-030: condition the late gain on the state at r50 (units, length, pearls); if the late gain survives at matched r50 state, it is the algorithm. (3) Build the switch: profile A before the measured phase boundary, profile B after; exact pairs against each profile alone | the late gain disappears at matched r50 state (it was composition); or the switched bot fails to beat the better single profile on the economy gate; or the boundary only works as a round threshold and not as a state trigger (OOS rule) |
| H11 | Stretch: an offline-learned policy (RL or supervised on the corpus + self-play) can be distilled into a small parameter set behind a strong, complex policy that is cheap to run live. The live budget is 100 M points/turn, of which a C++ turn uses <10 M, so a compact model (a few thousand weights over the state Ares already keeps) fits; the learning is offline where compute is free | not before R-5: the tuner is the first, linear version of this and its surface says whether the weights are worth learning. Then: a fixed feature set from `world.hpp`, a corpus-supervised or self-play-trained scorer for the search's leaf evaluation, exported as a weights table, measured on the BENCHMARKS gate and the generalisation panel | the learned scorer does not beat the tuned linear one at equal CPU; or its edge is pool-only (learned the ten maps) |

## 3. The pipeline (how a change becomes the live bot)

Register a bot directory with a `CANDIDATE.toml` (copy `bots/kazuha-s01-swarm-dissolve/CANDIDATE.toml`) →
the hub daemon runs the **dev pass** (20 games vs 545/752, zero timeouts, CPU under gate) → **dev screen**
(3 blocks of 40 games vs 545, 752, 45; exact pairs, sign test) → **field confirmation** (6 blocks vs band teams)
→ automatic promotion with probation and rollback. Screens use the dev allowance nobody else competes for; the
field allowance (45/h) goes only to confirmations. Everything is in `hub-state/` (daemon.json, candidates.json,
experiments.json, review packets). **Hand-activating a bot freezes whatever comparison is running** — three
activations on 28 Sep each cost a running test. Please register instead; it takes one file.

## 4. Roadmap

- **Now → 30 Sep:** C1-B router on the chassis (Opus); the leak fixes and portal rules as separate switches
  (§5 below — this is where narrow iteration wins); the Sprint build chosen from what has passed the dev screen.
- **1 Oct, Sprint:** live slot locked the evening before on the best confirmed bot; no uploads, no switches
  through the event. Its best-of-7 series are free field evidence and land in the corpus.
- **2–5 Oct:** the C++ bot to production if it beats the Python line in the pipeline (decision point); ledger fixes
  and portal rules confirmed one at a time; Schooltime flywheel.
- **6 Oct:** candidate freeze. **7–9 Oct:** no experiments; rating protected (the seed is the rank after the last
  autoscrims). **10 Oct:** Qualifiers.
- **Deferred (C2):** spatial state, action memory, coordinated fights — `claude/ten-day-plan-2026-09-29.md`.

## 5. Where focused, narrow iteration is highest impact (the leak list, ranked by length lost)

This is the work the Gavroche and Bifrost iterations were good at — watch games, find the leak, fix one thing,
measure. Each item has a number to move and a gate. Fixes go on the C++ chassis (`bots/anna-a02-chassis`,
`params.hpp` switch each) for the Qualifiers; the same fixes in Python on the live line are worth doing for the
Sprint where they are cheap. Measure in exact pairs (map, side, seed) with `tools/cx/bench.py`; the ledger and
portal scripts re-run on any replay set.

| Rank | Leak (map) | Us vs band (length lost /1k dragon-turns, r0–99) | What to build | Gate |
|---|---|---|---|---|
| 1 | Trapped / mill (Portals, Slithery, Schooltime) | 126 vs 63; 111 vs 88; 25 vs 4 | enclosure probe every turn (reach ≤ k cells → break toward open space even at pearl cost); never enter a 1-wide dead end whose only exit is a split | trapped −30 % on Portals/Slithery pairs, pearls r100 not down |
| 2 | Newborn deaths (Portals, Slithery) | 81 vs 33; 82 vs 59 (60 of 100 newborns dead by r10 vs 35) | site the child's first bed at split time (arrival-earliest, crowd-free); the split rule from the Schooltime spec | newborn −25 % on Portals, pearls r100 up |
| 3 | Portal exits (everywhere; Portals map) | 28 deaths / 100 steps vs 12.5; wall+self near portals 623 vs 2 | exit memory; sonar probe along the entry direction the turn before; exit-cell one-step simulation in id order; id-parity rule against same-pair double transit | −25 % portal-step deaths, transits not down |
| 4 | Small-dragon crowding (Portals) | 50 vs 28 | spacing: one head per bed cluster, ≥ 3 cells from allied heads (the top ten's structure) | crowd23 −30 %, pearls r100 up |
| 5 | Sprint tax (pooled, ours only) | 0.023 length per pearl vs 0 | sprint only when the arrival margin beats the cost; cap per dragon | sprint/pearl halves, pearls r100 flat |
| 6 | Kelp walls (Slithery) | 26 vs 9 | kelp-aware routing cost (router) | wall −50 % on Slithery |
| 7 | Timeouts (live Python bot) | ~7 dragon deaths a game to the CPU cap; 8 invalid deaths /1k on Portals | bound the boot turn and the search (as `ouroboros-s02-portal` did: first turns 97 → 54 M); fix the two per-turn exceptions in `separation.py` | zero faults on the four probe fixtures under `--sandbox` |
| 8 | Dead-end feeding splits (from the Tyr loss review) | not yet measured | enter a dead end only when feeding value > minimum split cost to leave; choose that split size | length lost in dead ends per game |

Also from the 28 Sep loss review and worth a look each: two-step enemy dash reach on long dragons, route
convergence at the start (several dragons the same way), and portal exploration starting too late on Trauma and
Queen of Spades (first pearl r31 for us vs r19 for the field).

## 6. What the macro side is doing meanwhile

The C++ chassis and harness (done: `bots/anna-a02-chassis`, `tools/cx/`, 3.9 M points a turn, atlas of the ten
live maps, golden-decision replay), the router and bed assignment (in progress), the corpus (continuous, ~2,400
replays/h, 9,000+ so far, no submission ids — the API dropped them on 28 Sep), the field statistics, the hub. The
split of labour that has worked: narrow, measured fixes on the bot from people who watch games; structure,
instruments and the live pipeline from the director side. Both report through `docs/findings/` in the six-line
format (what, the number, pairs, sandbox, what failed, next).


### Ares V04 — Tyr V12 C++ parity port

Ares V04 on the Anna A02 runtime scaffold now matches Tyr V12's move, split,
and sonar outputs on identical ordered transcripts from ten live maps and both
seats: 168,123 turns across 5,089 dragons with zero divergences. On the
BENCHMARKS.md seed-1 panel (eight opponents × ten maps × both seats), it scored
117–43 with no draws. The field-normalized pearl checkpoint mean was 1.090;
r100 dragons were 1.118 and length 1.000. Its four principal self-inflicted death rates remain
above their absolute targets (no-valid-action deaths are zero), and no
parent-relative acceptance delta was measured, so it stays experimental. The
requested upload completed as contest submission v83 (ID 11244), which the API
lists as active; this server state is separate from local frontier promotion.
Full parity scope and field-reference scorecard:
[the V04 finding](findings/2026-09-29-ares-v04-behavior-parity.md).


### Ares V05 — Tyr V12 separation exception fixes

V05 fixes the zero-`bed_wait` division and the missing newborn resource-pause
counter. On the matched 160-game seed-1 panel it scored 118–41–1 versus V04's
117–43–0. The normalized pearl mean improved +0.007, but r100 units fell
(1.118 to 1.071), so the documented +0.05/no-drop gate is not met. Tier-2
self-inflicted death rates stayed within the 10% guardrail. V05 remains
experimental; V04 and active submission v83 are unchanged. Details:
[the V05 finding](findings/2026-09-29-ares-v05-separation-bugfix.md).


### Ares V06 — expanded search and supported threat evaluation

V06 restores bounded high-effort search settings from historical Tyr,
Bifröst, and Skadi work, and adds Skadi/Fafnir size-matched threat support.
Its seed-1 160-game panel scored 122–38–0 versus V05's 118–41–1. The
normalized pearl mean rose +0.013, below the +0.05 acceptance gate, while
r100 dragons rose from 1.071 to 1.200 and length from 1.009 to 1.035. No
Tier-2 death rate rose more than 10%. Four dense-map sandbox matches completed
with no timeout/crash errors (p99 max-of-games 7.4M points; maximum 8.6M).
V06 remains experimental and is not submitted; no follow-up iteration was run.
Details and artifacts:
[the V06 finding](findings/2026-09-29-ares-v06-expanded-search-support.md).

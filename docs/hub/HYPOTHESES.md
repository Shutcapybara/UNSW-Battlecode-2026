# Hypothesis ledger — weights, not verdicts (director, 29 Sep 2026 18:50 UTC)

**Rule (lead, 29 Sep):** hypotheses are *downweighted*, never killed. An experiment verdict is a fact about one test
on one host at one time and stays immutable (the D-rule: never re-run a completed gate or rewrite a verdict). A
hypothesis is a belief about an idea; it carries a weight that moves on evidence, and every row lists what would
move it and when it is re-examined. A row can be driven to dormancy by evidence, but it stays on the list with its
revival trigger, so nobody re-discovers a dead end or forgets a live one because of early data.

**Weights** are coarse plausibilities, not probabilities to defend: 0.9 near-established · 0.7 likely · 0.5 open ·
0.3 unlikely on current evidence · 0.1 dormant (tested negative or excluded by rule; revives only on its trigger).
**Review:** every time a finding lands (a task closes, a lane publishes its fifth version, a live confirmation
reads), the director re-scores the rows the finding touches, with the date and the evidence pointer, and appends a
line to the log at the end. Weights change only on evidence or on a stated rule, never on taste. Untouched rows are
left alone; a row untouched for two phases is re-read for staleness, not automatically decayed.

Numbering: `L` rows are the ledger's own ids; `H` ids in `docs/TEAM-SUMMARY-2026-09-29.md` §2 and `S` ids in the
ten-day plan are cross-referenced. Evidence pointers are findings files, decisions (D-nnn) and status files.

| Id | Hypothesis | Weight | Evidence for | Evidence against | What moves it / re-test trigger |
|---|---|---|---|---|---|
| L01 (H1') | Deeper bounded search on the Tyr lineage in C++ pays | 0.8 | Ares V06 +12.9 % dragons r100, +3.5 exp-score pts at 8.6 M max (`ares-v06` finding); no CPU wall in reach (R-1 probes: L3 9.3 M, unbounded 22 M) | V06 failed the +0.05 economy gate; r50 pearls −0.017; one seed, pool only | R-1 ladder slope per phase, both panels; seed 2 |
| L02 (new) | Selective depth and clock-aware search budget — Stockfish-style extensions/reductions keyed on local volatility (enemy heads in view, corridor degree, pending split, contact distance) and a node budget that follows the game clock and remaining CPU; or, simpler, two or three discrete search algorithms and a decision heuristic on measured state | 0.6 | Ares already has a crude version (`search_cap` by born/saturated/late/sparse, `sprint3_*` limits) and it is the only lever with a positive slope; L01; no CPU constraint | none yet; R-1's L0 cap is cap-bound 79 % of the time, i.e. today's caps bind where volatility is not measured | Build on R-1's best level: (a) volatility-keyed extension, (b) discrete profiles + heuristic; measure per phase (L03); falsified if neither beats the best fixed level on the economy gate at equal mean CPU |
| L03 (H10) | Phase bifurcation from an algorithm change is a feature; the answer is phase-conditional logic keyed on state | 0.5 | interim R-1/`ra` reading (early worse, late better); V06 r50 −0.017 / r100 +0.048 | none yet; could be composition | D-030 composition check at matched r50 state; switched bot vs best single profile |
| L04 (R-5) | Fitted evaluation weights beat hand weights | 0.6 | ~40 hand-set weights never fitted; `ra` shows several with non-zero slope (threat, revisit, trap) | `ra` 25/0: every single-knob move is 3–5× short of the gate — the surface may be flat | R-5 SPSA on paired fixtures; sensitivity table |
| L05 (H2', R-3) | The ranked leaks (trapped, newborn, portal-exit, crowd) live in the Tyr lineage and are fixable on Ares | 0.7 | C1-C ledger; C2-0: our fights cost 2× the band's deaths and length; C1-F: the chassis had 2 % of the transit deaths | none on Ares yet | R-3 step 1 ledger on Ares (if Ares does not leak, → 0.2 and the lineage claim is wrong) |
| L06 (H3) | Portal-exit knowledge (pair memory, exit-known, probe) halves near-portal deaths without cutting transits | 0.5 | C1-D: 28.2 deaths/100 portal steps vs Cutlery 12.5 at equal volume; `ouroboros-s02-portal` +0.11 paired (Python) | C1-F: exit-known acted as a throttle (−4.4 % pearls) on the chassis — wrong host, so weak evidence | R-3 step 2 on Ares at real transit volume |
| L07 (H1) | Per-dragon routing (Dijkstra router) is a lever | 0.2 | C1-B: router beat cheap policy, but atlas carried 2/3 of the gain | C1-B: "routing is not the lever; survival is"; measured on a chassis at 0.44–0.47 of field economy, never on Ares | Revive if R-1 flattens before any wall *and* R-5 finds the target/route weights dominate: then test a router on Ares |
| L08 | Map memorisation (atlas) as an economy switch | 0.1 (by rule) | C1-B/C1-F: atlas is an economy switch (+) | OOS rule: tournament maps are unseen; atlas is dead code in Ares anyway | Rule, not data; revives only if organisers announce public tournament maps |
| L09 (S-3) | Leader-coordinated fight protocol over sonar | 0.15 | one team reportedly does it | C2-0: no movement-observable coordination signature in the top ten; initiator edge is composition | A payload-decoding study showing top teams send fight direction; or a top-ten replay set with synchronised entries above the band |
| L10 (D-030) | Local fight rules: refuse contact far from beds; converge-or-refuse | 0.4 | C2-0: top ten initiate 38.5 % vs 54.8 % at bed distance >6; team-7 convergence 0.18 vs 0.27 | "trade only when ahead" is composition, not behaviour; small cells | `ra`/`rg` mechanism runs; expected sign on deaths per fight, economy flat |
| L11 (H8/S-6) | Bed guarding pays, keyed on information state (visible / memory / density / shared) | 0.4 | winners' bed_capture_share 0.61 vs 0.46; guard rule keyed on memory is cheap | `ra` 01a/01c bedwait (−0.06 econ, −0.09 win), 11 idlebed (−0.06): the crude "wait on a ripening bed" form loses on open maps (Devil −0.72, Schooltime −0.41) while winning on QoS/Trauma — the *keying* is the question, not the guard | R-6 ladder; a guard keyed on structure (bed density within reach, contact distance) not a flat wait; revives above 0.5 if arm (c) beats (b) off-pool |
| L12 (H9/S-7, S-1) | Per-unit map memory with decaying pearl density (and S-1's EW enemy/ally densities) improves targets and routes | 0.5 | Ares keeps locations only; density is the obvious missing term; CPU is free | earlier Python state-tracking predicted well but never paid in play (was competing for the 100 M budget) | R-5 exposes a density weight; `ra`/`rg` mechanism; falsified if economy flat with the term on |
| L13 (S-2) | Action memory / momentum (commitment through transits and dead ends) | 0.4 | Ares has `momentum_weight 0.6`/`momentum_decay 0.6` already; portal-step deaths are the target | not yet varied on Ares | R-5 sensitivity on the momentum weights; `ra` sweep; portal-step death rate |
| L14 (S-5) | Scout splits for one-way places; clock-probabilistic exploration | 0.4 | unseen maps are where exploration pays (OOS) | `ra` 07b unseen8 −0.05, 16 infogain −0.22: *more* exploration value hurts on the pool — the pool is small and known; the panel is where this is tested | test on `maps/new/` first; pairs known by r50/r100; falsified if it loses on the panel too |
| L15 (S-4) | Crown location by decaying consensus | 0.3 | field-wide struggle with the crown; late-game consumer of a few packets | C1-E: winner's longest margin 0–1 in decided games — the crown may not be the currency; needs S-1 first | corpus: does crown survival/margin predict the win in the 28k set? if not, → 0.15 |
| L16 (H11) | Offline-learned policy distilled to a cheap live weight table | 0.5 (long-run) | live budget 100 M, C++ uses <10 M; corpus of 28k replays; R-5 is the linear first step | none; no infrastructure yet | after R-5: if the tuned linear scorer beats hand weights, → 0.6 and design the feature set; if the surface is flat, → 0.3 |
| L17 (P1) | Production pace can be forced (earlier/more births) | 0.1 | — | P1: pushing production moves nothing; pearl-bound | revives only if a bot shows a pearl surplus at r50 (then production is the bottleneck) |
| L18 (S1) | Swarm dissolve / density gossip between dragons | 0.15 | kazuha/sakura zero kelp deaths | S1: gossip measured negative for early economy consumers; screen rejects | revives as a *late* consumer (L15) only |
| L19 (H5) | Dev team 545 is a proxy for the 55–85 band | 0.6 | rank-15 swarm bot, separate allowance | one strike (yuna-v03 passed dev, failed field) | second strike → 0.3 and the panel reverts |
| L20 | Single-parameter moves on V06 can pass the gate | 0.2 | a few +0.02 moves (threat, revisit) | `ra` 25 screened / 0 accepted | joint moves (R-5) or structural changes are the route; revives if a knob shows a consistent seat-independent +0.03 |
| L21 | The +0.05 economy gate is the right shape for a search/retention gain | 0.5 | it protects against splitting-into-dust and hygiene-by-playing-small | V06 is the best evidence in the programme and failed it; its gain is retention, which the gate does not credit | R-1 per-phase decomposition; if retention gains convert to r150/r250 pearls, the gate is fine; if not, add a retention clause (decision, not lane-by-lane) |
| L22 | Complex logic costs the early game (the C++ question as first posed) | 0.2 | — | C1-A: the cheap C++ policy loses 60/60 to yuna-v03; Ares V06 (more logic) is the best bot | revives if R-1 shows an early-game loss that is CPU-caused (it is not: 9 M of 100 M) |

## How a lane uses this

A lane picks mechanisms from the rows with weight ≥ 0.3 first, and from ≤ 0.2 rows only when their trigger has
fired. A rejection in a lane lowers the row a step at most, with the number, and never below 0.1 by one result;
two independent rejections on the right host are needed to reach dormancy. A hold (hygiene up, economy flat) does
not move the weight; it is queued for stacking. Every finding file ends with the rows it touched and the proposed
new weight, and the director applies it here.

## Log

- 29 Sep 18:50 UTC — ledger created from H1–H11, S-1–S-7 and the C1/C2/`ra` results; L02 added (selective depth /
  clock-aware search, lead's note); L07 and L11 are the two rows whose old "rejected" reading was really
  "rejected on the wrong host or in the wrong form" and are kept live at 0.2 / 0.4 with explicit triggers.

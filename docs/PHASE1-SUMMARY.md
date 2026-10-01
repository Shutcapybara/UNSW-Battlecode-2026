# Phase 1 summary — 27 Sep to 1 Oct 2026 (director)

What the first phase of the research programme built, found and left open, written for the six-instance phase that
follows. Numbers are quoted from the findings they came from; the ledger (`docs/hub/HYPOTHESES.md`, 40 rows) carries
the current weights, the decisions file (`docs/findings/2026-09-28-director-decisions.md`, D-001–D-040) the reasoning.

## 1. The rules changed on 1 Oct (D-040) — every number below is pre-change

Toolkit `unswbc 1.2.3` (protocol 3 unchanged, so existing bots still run) carries two rule changes the docs site has
not yet caught up with. **Sprinting:** a dragon of length L takes its first ⌈L/4⌉ steps in a turn free and pays one
segment per step after, and must keep at least 2 segments (was: x steps cost x−1 segments). **Round-limit tiebreak:**
longer *queen* first (the queen is the team's lowest-id robot: "at the end of the mission, your queen … will be
extracted back to the surface"), then longest dragon, then total length (was: longest, then total). Verified by
running 1.2.3: verdicts now read "longest dragon, 9 to 5" only when the queens tie. Consequences: mobility is far
cheaper for long dragons (a length-12 dragon sprints 3 free; the sprint-cost findings and `sprint3_*` caps are
stale); the endgame is now literally a queen race — the top teams' conversion edge (L39) applies to one specific
dragon, and losing the queen may forfeit the first tiebreak; the field's behaviour will shift from the day the live
server adopted the rules, so the corpus and the BENCHMARKS references must be split into pre/post eras.

## 2. What was built

- **Measurement.** A 28k+ game public-replay corpus with a continuous collector; BENCHMARKS (field-median
  normalisation, top-ten gap, field percentile; tiers and guardrails); the feature lab; the R-4 scorecard with a
  `GATE:` line; the generalisation panel (29 unseen maps: `maps/new/`, transposed pool maps); the S-1 stats store and
  `q.py`; the tempo-lag metric; the map signature tool (Esquie); the death ledger and portal instrument (R-3).
- **The gate.** BENCHMARKS step 4 → D-032 (paired fixtures, seeds 1–3, bootstrap lower bounds, per-checkpoint,
  tier-2 ≤ +10 %, win not down) → D-036 (local hold with signature transfer) → D-037 (per-map opening percentiles as
  targets, r100/r250 as guards; predictability weighting from S-1 Q2). Known gaps: the economy mean stops at r250 so
  conversion is invisible; pool lower bound vs off-pool gains; cluster vs plain bootstrap (H-1 is auditing).
- **Infrastructure.** The hub (Mac): executor in shadow (no uploads/activations while teammates own the submission
  interface), corpus thread, git keeper with director controls (`merge`, `push_branches`, `fetch_all`,
  `checkout_main`, mode), registration with manifests and a 4 MiB archive cap. The desktop (4090, ~2,900 games/h)
  runs all panels and training. Lanes work in worktrees on `r/<lineage>` branches; the lead names lineages.
- **The C++ line.** Ares (teammates' port of Tyr V12, golden parity) → `lune-r1-07` (late-only search cap) → the
  prior bots (`hb1-14-prior-r540` 3.74 MiB, `verso-05-hb800-prior` 3.38 MiB) and `aline-17-sym-seal`. The state
  module and feature interface (Maelle), the feature dump, the ES loop (Alicia), the tree-export path (HB-1).

## 3. What was found

1. **Where the loss is.** The gap to the top ten opens in rounds 0–25 and is economy, not deaths (S-1 Q3): bed
   conversion (we reach beds as early, eat fewer), production (fewer splits by r50), early portal use, territory. By
   r50 it is 0.8 field-SD and stays. Deaths differ by 0.1 SD early and grow later. Our portal leak is exits into our
   own traffic (same-pair doubles, newborn transits, landings our dragons can see), not blind landings (S-1 Q4).
   Everyone is a map specialist; Portals is the least predictable map (S-1 Q1/Q2). The top teams' late edge is
   deliberate conversion — they cull small dragons from r250–300 and dissolve into one long dragon; Heartbreaker
   never converts (TT).
2. **The local optimum.** V06's evaluation is at a flat optimum for continuous moves: 44 single-knob moves
   (Renoir, Monoco), fitted feature weights with zero-weight optima (Maelle), ES drift in a bowl (Alicia). Caution
   costs economy one for one on this lineage (every hygiene fix: R-3, Renoir). Part of the pool edge is map
   identity (the `W==32 && H==16` terms; pool win 0.76 vs off-pool 0.52).
3. **What moved the gate.** Only information mechanisms: Heartbreaker's direction model as a prior inside Ares's
   search (win +0.15, economy +0.05; every death rate −30–40 %), and symmetry inference from the blind lane
   (economy +0.025, win +6 pp). Holds: the portal-mouth loitering tax (Gustave), the starved-opening bed
   anticipation gated on own food knowledge (Esquie, local hold), the cramped-split production lever (R-3).
4. **What did not.** Search depth beyond the late cap (R-1: no CPU wall, slope negative in the opening); pre-entry
   portal rules on either host (throttles); donor conversion rules ported without the donor's other behaviour (TT);
   the density grid as a value scaler (Sciel/Maelle: the economy gain generalises, retention pays); a leader
   fight protocol (C2-0: the top ten's edge is composition, not coordination); RNN/memory for mimicking the top
   teams (≤ 1 pp — their policies are mostly functions of the view).
5. **Opponent anatomy.** Heartbreaker is a rule wrapper around one learned decision (direction; 83 % predictable from
   the 7×7 view), static over the window. cheji bt and Stockfish are less predictable from the view (75–76 %), both
   cull deliberately, and about a quarter of their moves are undetermined by view plus simple memory.

## 4. What is open (the next phase's starting roster)

The rules change above, first. Then: whether the prior bots have left the bowl (H-1 first pass); whether the prior
and symmetry gains add; the state-keyed conversion trigger on our own feeder logic, now a *queen* trigger; the
per-map opening programme (D-037) component by component; the three-tier learned loop (Verso: priors are the lever,
bounded by 4 MiB and first-turn CPU; own-data heads next); synthetic maps by hazard signature (K-1) for
train-on-synthetic/test-on-real; the taxonomy (T-1) and the ledger (H-1) as the shared memory.

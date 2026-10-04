# Nara status — glm/nara, P2-A analyst

Worktree `../wt-nara`, branch `r/nara`, tools `tools/nara/`. Host: the Mac. I am **not** the replay lead: I read the
corpus/store, I never pull. Findings: unit 1 `docs/findings/2026-10-01-nara-era-and-queen.md`, unit 2
`docs/findings/2026-10-01-nara-era-shift-and-cutlery.md`.

## Unit 2 (1 Oct, ~16:05 UTC) — era-shift anatomy + Cutlery + corrections, done

1. **Correction (published on the board)**: unit-1's "total@100 +12 %" was a probe bug (len(coord)=2) × units —
   per-map units@100 is flat-to-down; pearls columns stand. Fixed both probes.
2. **Era shift, per map**: own-goal deaths **+12 % field-wide** (top10 wall 4.8→8.8/1k dt); economy split by
   geometry — Schooltime pearls@100 +171 %, Trauma r50 ×4 (broad-based), Slithery −13 %. Testers' tier-2 guards
   need era-matched baselines.
3. **Queen rule verified at full scale**: 3,978 post games → 2,135 rl, **8.2 % queen-decided, 4.8 % flipped, 0
   violations**. Volume-weighted survival: top10 7.4 %/4.4 % (all/rl), field ~5 %.
4. **Cutlery dissected** (the field's reference queen build): deployed to ranked ~13:00Z (0/62 → 23/84 survivals;
   queen-alive win 87 % vs 51 %). The queen is **the crown from birth**: moves 454/500 rounds, eats 30 pearls
   (field queen 3), still splits, grows 4→22 by r400. Bimodal parked/fed lengths 3–65.
5. Board: correction, era shift, Cutlery, readings on carthage's four H-Q1 rejections + gate answer (RL-win LB>0
   + econ LB>−0.03 + pocket-map exemption), convergence note to antioch (their 06:00Z tag + verdict patch adopted).
6. Hypotheses proposed: **N4 mobility-economy regime 0.5, N5 own-goal era tax 0.6, N6 queen-crown unification 0.65
   (Cutlery-measured; the live arm for carthage/kyoto), N7 adaptation-decay reading**.

## Live hypothesis list (mine; weights proposed, director applies)

- **N1 queen protection 0.7** — now reframed by the data: the winning form is N6 (fed crown), not hiding; park-only
  forms failed econ 4× on carthage's panel.
- **N2 queen hunting 0.4** — value rises as the field adopts protection (Cutlery first at 13:00Z). Spawn-geometry +
  L38 symmetry identification.
- **N3 opening-era continuity 0.6** — weakened: Schooltime/Trauma pearls moved >10 % already (2 maps, not 4); the
  carried targets survive only for the dense maps. Watch the store rebuild.
- **N4 mobility-economy regime 0.5** — sprint-assisted sparse-map openings; whole-path (mid-cell) safety pricing.
- **N5 own-goal era tax 0.6** — +12 % own-goal deaths is mechanical (free multi-step moves into mid-cells).
- **N6 queen-crown unification 0.65** — elect the queen as crown from r0; Cutlery's measured form; merges H-Q1+L39.
- **N7 adaptation decay** (reading) — protection value decays weekly; hunting rises symmetrically.

## Check-ins (3 Oct 23:00 UTC)

- 02:32 4 Oct — rome-03-queen-state-convert REJECT read: dead-queen triggers meant the crown pin never attached
  (rl conversion −5.6/−8.5pp); ordering conclusion = survival-from-r0 precedes crown pinning. H17-05 conceded
  (slice-1 = observed-loss shares, not counterfactuals; slice-2 spec: lineage closure, censoring, cluster CIs).
  Ladder: us #79/1702 (drifting), Vibing++ #2.

- 02:02 4 Oct — L47 decomposition SLICE 1 delivered (split_probe.py; PD r0-50 83% regret, Slithery ~63%, Portals
  late 57%; Schooltime/Trophy openings 7-9%; chosen-death caveat stated; slice 2 = chosen-vs-hazard attribution).
  H16-01 ack; H16-02/03 mechanics noted (unit-count legality bound at 63/64). No new tests (Rome04 running).

- 01:32 4 Oct — Rome03 REJECT read (95/96 dead-queen triggers = the arm never tested the live-queen path; gate the
  trigger on queen-alive). H15-04 conceded (Autarky 992701 was an open spawn, not a pocket — my "same mechanism"
  grouping wrong; weaker claim stands: pocket-ness is spawn-position, not map-level). H15-05 conceded (20+/cap-3
  labeled proposal in TARGETS). Ladder 01:25Z: us #77/1704 (still sliding), Vibing++ #3/2247. Rome04 running.

- 01:00 4 Oct — H14-04 conceded (3/4 leads not 4/4; "rare, not zero"). H14-01 holdout closes the pocket-survival
  question at field scale (33/34 first-split survive). Synthesis posted: queen-crown length is topology-conditional
  (feed to 20+ open; cap at 3 sealed — growth destroys the spare cell, H14-02). Bed-target provenance caveat noted
  (H14-03). Ladder: Vibing++ #1 again, us #73. Rome arm still running.

- 00:30 4 Oct — H13-05/H13-04 conceded (units-guard unit-sloppiness; 737 = 501×14265 + 236×14585 pooled).
  Pocket-survival synthesis with himeji H13-01/02: legal r0 split → freed-cell patrol is THE keeper mechanism
  (g992701 q41 + 21 Schooltime r0 deaths). Ladder: ftm #1, Vibing++ #2, SSS #3, Sponge #4; us #75/1707 sliding.
  Seoul split-opportunity decomposition still mine (full unit, not a check-in).

- 00:05 4 Oct — HIMEJI CORRECTIONS ACCEPTED (H11-02: RL 398 not 326, filter bug queued; H12-03: 14585=carthage-05
  live since 21:56Z, unit-4 = 14265-era). **First queen-decided ranked losses verified**: 4 rl losses with total
  leads 81–50 / 249–6 / 268–3 / 154–155; our queen 0/15 live games; keepers 1097/776/64 farm us. **H-Q3 pocket
  exception**: opp queen 41 alive on AUTARKY (g992701) — pocket-death is seat/layout-specific, re-derive before
  disabling queen logic on pocket maps. Endorsed H12-01/02 (L10 HOLD).

- 23:35 — ROME ACTIVE AGAIN (L10 HOLD read: estimand/units answered — median-checkpoint guard, Δlog −0.10 rule; it passes), Rome takes L39/L49 (endorsed + 306 field reference handed over). Seoul lane appeared (L47 boundary — split-opportunity decomposition queued to me). Team 7 resumed 22:57Z (1–4 vs 776); RANKED play now includes Australia/weakhold/Tower Defense — map pool widened. Himeji cautions 737 rows may mix two submissions (my window is all-14265 unless a later activation).

- 23:00 — no new tests/board traffic; 691 new field games, **team 7 silent since 05:43Z (19 h)** → watch note
  posted; ladder us #66/1718, Vibing++ #1/2298. Half-hourly cron automation-4f01e972 active.

## Unit 4 (3 Oct, ~22:40 UTC) — reorientation, corrections, team-7 live, done

Reoriented after 2 days: D-042 rulings (era 06:00Z, FRAME_VERSION 7, win-led gate), himeji's audit wave,
carthage wrapped 9 arms, my pairing tester Rome inactive (queue shared). Ladder re-shuffled: 306 (Cutlery →
Vibing++) back to #1 at 2309 (+172) — deployment-level N1/N6 confirmation; Sponge #4, fandagong #7 (queen-keepers
now in the top ten); cheji bt/Stockfish gone; team 7 #67 at 1723.

1. **Corrections (himeji H2-02/H5-03/H6-01/H6-02 answered on the board)**: RL-reached denominators adopted; my
   0/62→23/84 withdrawn (their 0/31→9/31 ranked RL reproduces from my files); the 5 IDs unrecoverable (sample
   overwritten, no input hash — samples now append-only); "cull" reframed as illegal-split deaths — the safe
   imitation is a queen-split legality check.
2. **Team 7 live (737 games)**: queen 0/326 rl survival, median death r59; ranked 56.6 %, unranked 23.6 % vs the
   new top ten; loss maps = rl maps exactly. Full-map pool returns in unranked.
3. **Units-guard ruling** posted (relative-to-parent Δlog LB −0.10; production guard for queen arms).
4. Queue repackaged for shared testing: N6 0.75, N2 0.5, L24-on-q0, N5, endorse H-S1.

## Unit 3 (1 Oct, ~17:00 UTC) — queen hazard anatomy, h2h rule, Cutlery mechanism, done

1. **Queen hazard by map** (1,054 post-era side-rows): pocket (Autarky/Slithery/PD) queens die 0 % enemy —
   wall/self/invalid culls; contact (Trophy/Default/QoS/Schooltime) 65–84 % enemy h2h; corridor (Devil/Trauma)
   mixed. Next arm for the testers: **queen-keyed enclosure avoidance** (L24 on q0) for pool survival; enemy
   avoidance only moves gen.
2. **h2h length rule**: length is not armor (857 victims longer vs 496 shorter; 2,161 mutual). N6's value =
   tiebreak margin + queen-vs-queen duels.
3. **Cutlery flip mechanism**: stop culling the queen (pre-flip 65 % invalid-culls; post-flip state-keyed retention
   — still culls on pockets). No avoidance premium. Trauma survival 11/13; 0 on pockets/Devil.
4. **Adaptation clock 16:50Z**: no second top-10 flipper; mid risers (fandagong, Shannon, No Idea, 😹, Settlers,
   SHINK AI); :3/Sponge persistent style. Queen-vs-queen duels coming.
5. Readings posted: carthage-05 promote-ready (agree, win-led gate), carthage-08 next arm, H-Q8 features + hazard
   regime, himeji Φ audit agreed.

## Next unit (queue)

1. Board + statuses first; answer anything addressed to nara.
2. When antioch's store rebuild lands here: post-era BENCHMARKS re-derivation (per-map medians at ≥300/map, era
   column), transits@50, endgame material columns (longest@490 post), Q3-style top10-vs-field component table.
3. Cutlery wrapper extraction (HB-1 method, `HB_TEAM=306` on post-era games): the queen-safety premium's exact form
   (what keeps it alive — the missing piece of the dissection).
4. Watch the ladder: does Cutlery's queen build hold rank 1; who copies it (adaptation-decay clock).

## Notes to self

- `len(body[1])` is a coordinate, not a length — use `len(body)` after unpacking `(team, body)`. Cost me a published
  number; per-map cuts before pooled cohort cuts, always.
- Raw death causes are ('wall','self','body','h2h','invalid') — the ally/enemy split is extract.py's, not the
  frame's.
- Board timestamps in UTC; some lanes post local time (carthage's desktop reads ~UTC+11).
- The other lanes' boards diverge until the keeper merges — restate load-bearing facts when addressing them.
- Cutlery queen-alive games decode cache: build/nara/queen_cutlery.jsonl has all 146 side rows.
- The corpus decoder stack needs `sys.path = [tools/leviathan, tools/analysis/features]` then `from frame import
  decode`; team values in events/rounds are **'A'/'B' strings** (not 0/1 — cost me two bugs).
- `paid` (sprint cost) is only trustworthy for moves whose actor survived the round.
- Team 7 has no post-era corpus games; "us post" comes from the testers' panels until the executor leaves shadow.

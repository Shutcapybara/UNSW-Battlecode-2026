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

# X-1 Verso — the three-tier learned loop on Ares

Prompt: `docs/hub/prompts/2026-10-01-X1-three-tier-loop.md`. Lineage **Verso**, branch `r/verso`, worktree
`../wt-verso`, bots `bots/verso-*`, tools `tools/verso/`. Running log with every table: `claude/verso-status.md`.
Desktop, 30 Sep 23:00 – 1 Oct 15:30 ACST. The host was shared with the top-teams mimic lane (`r/tt`), which had
priority; Verso games ran at `nice 19`. Paused on the lead's instruction (1 Oct) pending resources.

## Headline

1. **The learned part that pays is a donor's direction model used as a prior inside Ares's search, and it pays in
   proportion to its quality and size.** Cycle 0 (`verso-01-hb-dir-prior`, Heartbreaker prior, 300 rounds) is the
   first D-032 **ACCEPT** on the lanes' base: pool win 0.698 → 0.848, econ~ +0.052 [+0.019, +0.081]; off-pool win
   +5.0 pp; tempo −7.6 rounds. Raising the prior to 540 → 800 rounds (`verso-02`, `verso-05`) adds +12 pp off-pool
   win over cycle 0 (0.618 → 0.739) and +0.124 off-pool economy, pool unchanged to +3 pp; more Heartbreaker data at
   the same size (`verso-06`) adds +4 pp pool win (HOLD). **`verso-05-hb800-prior` is the lane parent** (the lead kept
   it despite D-032's letter, whose pool lower bounds sit just below the line), deployable: zip 3.38 MiB, sandbox max
   12.0 M points/turn.
2. **Learning our own targets did not beat imitation.** Monte-Carlo Q (20-round returns from ε-exploration) is noise
   at 214 k exploratory rows (advantage R² 0.015) and loses. Hindsight search over the recorded future gives very
   learnable labels (R² 0.76–0.86) and cuts wall deaths up to 70 %, but every version cost bed pearls; with S-1's
   tempo credit (we eat back 45 % of our own dead) the head becomes neutral. On this policy the first-step choice is
   no longer where tempo is lost.
3. **Tier 1 (CNN over the map-memory window + GRU) adds nothing over the hand features** (≤ ±0.2 pp at equal data;
   probes show it re-derives reach, food density, corridor length): dropped under the pre-registered rule. **Tier 4**
   (route features over the map memory) adds a little (+0.6 pp R², −7 % regret). Hand-built memory (seen-dragon
   densities, sonar, own-path window, pearl density, remembered pearls; four lengths each) adds at most +0.4 pp to
   imitating cheji bt (0.760) and +0.1 pp for Stockfish (0.779): the quarter of the top teams' moves the view does not
   determine is not this kind of memory.
4. **Phases.** Tempo as the opening objective: donor ensembles and opening-only heads give no lasting gain (HB +
   Stockfish −2.6 rounds at seed 1, −0.5 at seeds 1–3); SPSA over 18 opening knobs is noise-limited (per-iteration SE
   0.07–0.11 > effects). Late conversion (tt-05's earlier feeding, fixed or ramped hb → tt over r300–400) is neutral on
   these panels: no zoo opponent converts, so it is a ladder question.
5. **Deployment constraints found:** the judge charges the boot to turn 0 (100 M points); decoding a compressed
   1,000-round model costs ~185 points/node and kills every dragon on turn 0 (`verso-03/04`, not deployable). An
   in-place 16-bit node format fits 800 rounds in 3.38 MiB with no decode.

## Version table (seeds 1–3, D-032 paired, both panels)

| Bot | Change | vs | Pool win / econ~ | Gen win / econ~ | Tempo pool / gen | CPU max | Verdict |
|---|---|---|---|---|---|---|---|
| `verso-00-base` | platform (inert) | maelle-02 | identical | identical | — | — | base |
| `verso-01-hb-dir-prior` | Heartbreaker prior 300 rounds, λ 1 | 00 | +0.150 / +0.052 [+0.019, +0.081] | +0.050 / +0.013 | −7.6 / −7.7 | 11.5 M | **ACCEPT** |
| `verso-02-hb540-prior` | 540 rounds | 01 | +0.000 / −0.001 | **+0.097 / +0.107** | −1.0 / −6.3 | 11.7 M | REJECT (letter) |
| `verso-03-hb1000-prior` | 1,000 rounds, compact | 02 | +0.021 / +0.008 | +0.034 / +0.044 | — | **fails turn 0** | not deployable |
| `verso-05-hb800-prior` | 800 rounds, in place | 02 | **+0.033** / −0.017 | +0.024 / +0.017 | — | 12.0 M | **lane parent** |
| `verso-06-hb800-moredata` | 800 rounds, 2.3× data | 05 | **+0.040** / +0.005 | +0.005 / −0.021 | −1.6 / +1.9 | 12.3 M | HOLD |

Screens (pool seed 1 unless stated) of everything else are in the status file: donors (cheji bt, Stockfish, pooled),
MC-Q, five hindsight label versions, opening ensembles, hb1-14 / tt-05 / tt-06 and their parts on the Verso base,
λ 0.7 / 1.5, mirror-trained prior, the full 2,251-round model, pearls-per-crowding (below).

## Not finished at the pause

- **Pearls per crowding** (lead's design: decayed pearl / ally maps, a broadcast of the pearl-density centre and mass
  with ally and enemy counts, target value × exp(w (P − κA))) is built (`verso-p6-platform`, parity 0 divergent). One
  screen finished: own maps only, w = 0.5, vs `verso-05` seed 1 — pool win −0.013, econ~ +0.025 [−0.043, +0.062];
  gen win 0.000, econ~ −0.033, length@100 −0.174; ally head-on unchanged. No gain at that setting; w = 1 and the
  broadcast arms (w 0.5 / 1) were stopped unplayed (arms `c5-pd-*` registered; queue lines 52–54).
- Memory sweep for Heartbreaker (control) stopped after the base fit (0.840); the "all families" fits did not print.
- Tier 1 on top teams' imitation (the one untested place memory could matter) needs view tensors for corpus games
  (replay-drive the C++ bot); not built.

## §0 Decision memo — is the design reasonable? (written before the first training run)

Short answer: yes as a loop, with three changes to the sketch, each of which is a measured experiment below, not a
decision.

### What is kept

- **Search plus learned first-step terms** (hb1-12's architecture): the head never replaces Ares's path scoring; it
  adds a term to the score of each first step. This is the only learned form in the programme that has held
  (139–21 vs 122–38, two seeds) and it degrades to the parent when the term is zero.
- **Trees for tier 2**, exported as compiled 8-byte nodes (hb1-04's encoding). HB-1 measured trees ≥ MLP on every
  decision.
- **Tier 4 as hand-built memory** read by the heads as features of each candidate first step.

### What changes, and why

1. **Base.** hb1-12 sat on Ares V06. Verso sits on the lanes' base — `lune-r1-07-latecap8x-only` with the three
   `W == 32 && H == 16` terms off (D-033) and SF-1's `state.hpp` — i.e. `maelle-02-features` at zero weights.
   `verso-00-base` is that bot plus the Verso runtime, inert (golden parity below). Consequence: hb1-12's +10.6 pp
   has to be re-measured on this base and, for the first time, on the generalisation panel. That is cycle 0's
   control arm.
2. **One feature extractor.** The three Python learned-policy attempts died on train/live feature mismatch (L27).
   Here the C++ bot is the only place features are computed: it writes its own per-turn vector
   (`VERSO_DUMP`), and the trainers read that. The one exception is cycle 0's corpus imitation, which uses HB-1's
   v5 rows; those have proven bit-parity with `hb1_features.hpp` (19,553 rows × 276 columns, 0 mismatches), and the
   v5 block of the Verso vector is filled from that same code.
3. **The improvement operator (tier 3).** "Relabel with a deeper search" is weaker than it sounds on this bot:
   Ares's move choice is a one-step path score over a target BFS and a room flood, R-1 measured that raising its
   caps is not monotone (wide search costs the opening), and the live CPU headroom is 10× — a search that was
   simply better could be run live and would need no distillation. What a live search cannot have is the
   **outcome**. So the operator is outcome credit, in two forms to be run against each other:
   - **(A) Monte-Carlo Q.** Data games are played with ε-exploration on the first step; every logged decision gets
     the 20-round return of the dragon's lineage (Δ material: length of the dragon and its descendants plus a unit
     term, death = loss of both); a tree regressor per first step fits Q(features, step); the head adds
     `β · (Q(step) − max Q)` to the path score. This is one step of policy iteration with the hand score as the
     prior; the next cycle collects with the improved policy.
   - **(B) Hindsight search.** For each logged state, a full-information search over the *recorded* next 20
     rounds (true map, recorded movements of every other dragon, recorded pearl spawns) values each first step.
     Low variance and covers all three steps in every state, but clairvoyant (strategy-fusion bias). Built only if
     (A) stalls or is too noisy at the data budget.
   Exact counterfactual rollouts (re-running the engine from a logged state) were costed and rejected: bots are
   separate processes with private memory, so a fork costs a full re-run of the game to that round (~20–60 s per
   label).
   The `dir` head (softmax over F/R/L, used as `λ · log p`) is kept for imitation targets and for the distilled
   argmax-Q targets; whether the `q` form or the distilled `dir` form carries the gain is measured.

### The four questions the lead asked

1. **Does tier 1 (CNN + GRU) earn its place?** Unknown, and the prior is weaker than L34's text suggests in one
   direction and stronger in the other. Against: HB-1's memory test (+0.19 pp). For: the mimic lane's Q1 on the
   two top teams — direction from the local view is only 0.751 (cheji bt) and 0.771 (Stockfish) against
   Heartbreaker's 0.829, with the same features and model class. A quarter of the best teams' moves are not
   determined by the 7×7 view; that is room for state. The order of tests is cheapest first: tier-4 hand route
   features (memory-graph distances, reach, corridor depth, hazard grids) with and without, on our own targets;
   then the embedding on top. **Pre-registered drop rule:** tier 1 is dropped if it adds < 0.5 pp held-out
   agreement over v5 + tier-4 at equal data *and* does not move the gate; the linear probes (enclosure, food
   density, mode) are run either way and reported.
2. **Converge or oscillate?** Tracked per cycle: (a) held-out agreement of the new head with the previous cycle's
   head on a frozen state set (fidelity to the previous cycle), (b) the D-032 scorecard on both panels against the
   fixed base, (c) held-out fit of the head to its own targets. A cycle whose policy agreement moves by > 5 pp
   while (b) moves by less than its interval is recorded as churn and the previous cycle is kept.
3. **Data budget.** Measured, not assumed: the dump is 1.85 kB per actor-turn (447 floats), ~10 k actor-turns per
   side-game, so a 500-game cycle is ~5 M rows / ~9 GB raw (converted per game to compressed arrays, raw deleted).
   On the shared host the throughput will be well under 2,900 games/h; cycle sizes are set from the measured rate
   and reported.
4. **Leakage.** Three fences. (i) Training games never use a panel fixture: data games are played on
   `maps/{arena,big_empty,Colosseum,default_small,stronghold}` (in neither panel) and on the live pool
   at seeds ≥ 101; the generalisation panel's maps (`maps/new`, `maps/var/*_tr`, `maps/pub/*_rec`) never enter a
   training set. (ii) Held-out agreement is always by game. (iii) Features carry no map identity: the v5 block
   drops `W, H, x, y, xn, yn, facing_abs`; the dump header keeps `W, H, head` for joins only. The generalisation
   panel decides every accept.

### Order of work

Cycle 0: `dir` heads fitted on corpus targets from v5 features only — donors Heartbreaker (62), cheji bt (70),
Stockfish (206) and pooled — screened on the pool, the best taken through D-032 on both panels. Cycle 1: own
data with ε-exploration → `q` head (A), with and without the tier-4 block; tier-1 embedding test. Cycle 2+:
re-collect with the improved policy, refit, ES over `λ`, `β`. Phases enter as features first. Every cycle gets a
row in the status table whether or not it moves the gate.


## Ledger rows touched and proposed weights

| Row | Current | Proposed | Evidence |
|---|---:|---:|---|
| L27 learned decision functions beat hand rules for a specific decision at ≈ 0 live CPU | 0.7 | **0.8** | Cycle 0 ACCEPT under D-032 on the lanes' base (pool +15 pp win, econ~ +0.052); the size/quality dose–response (300 → 540 → 800 rounds, +12 pp off-pool) at 12 M points/turn |
| L16 offline-learned policy distilled to a cheap live table | 0.5 | 0.5 | Imitation transfers; learning our own targets did not (MC-Q noise, hindsight neutral under tempo credit). Unchanged until a self-generated target beats a donor's |
| L34 learned state compression (CNN + RNN) | 0.4 | **0.25** | Equal-data test: +0 pp over hand + tier-4 features; probes recover the hand state. Revive only through top-team imitation with corpus view tensors (untested) |
| L12 decayed food density improves targets | 0.7 | 0.6 | Pearls-per-crowding (own maps, w 0.5): no gain; broadcast untested. Third flat-or-negative density consumer on this lineage |
| L33 coordination as coupled beliefs over sonar | 0.5 | 0.5 | Broadcast built, not measured |
| L03 phase-conditional logic | 0.7 | 0.6 | Opening-specific donors / heads / knobs gave no lasting tempo gain; the gains came from a whole-game prior |
| new: deployable model size is bound by the judge's first-turn budget (boot = turn 0) as well as the 4 MiB zip | — | 0.9 | `verso-03/04` die on turn 0 decoding 1.5 M nodes; in-place format boots at 7.8 M |

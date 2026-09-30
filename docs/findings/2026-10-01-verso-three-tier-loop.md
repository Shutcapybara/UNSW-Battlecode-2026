# X-1 Verso — the three-tier learned loop on Ares

Prompt: `docs/hub/prompts/2026-10-01-X1-three-tier-loop.md`. Lineage **Verso**, branch `r/verso`, worktree
`../wt-verso`, bots `bots/verso-*`, tools `tools/verso/`. Running log with every table: `claude/verso-status.md`.
Desktop, from 30 Sep 2026 23:00 ACST. The host is shared with the top-teams mimic lane (`r/tt`), which has
priority; Verso games run at `nice 19`.

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
   `maps/{arena,big_empty,Colosseum,default_small,dilemma_10,stronghold}` (in neither panel) and on the live pool
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

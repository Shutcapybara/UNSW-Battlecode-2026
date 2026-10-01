# verso-00-base

Verso lineage (X-1, the three-tier learned loop). Parent: `maelle-02-features` (branch `r/maelle`) at zero
weights, i.e. `lune-r1-07-latecap8x-only` with the `W == 32 && H == 16` terms off (D-033) plus SF-1's `state.hpp`.
`state.hpp`, `params.hpp`, `world.hpp`, `nav.hpp`, `helper.hpp`, `atlas.hpp` are verbatim copies;
`hb1_features.hpp` is `hb1-12-direction-prior`'s (HB-1's v5 actor-local row in C++).

What this version adds (all inert at the compiled defaults):

- `verso.hpp` — configuration (`VERSO_PARAMS`, `VERSO_POLICY`, `VERSO_DUMP`, each with `_A` / `_B` per-team
  forms; local games only), the feature schema (447 columns: v5 270, Ares search outputs 58, tier-4 route
  features and state scalars 119; `VERSO_SCHEMA=1 <binary>` prints it), the head evaluator (8-byte preorder nodes,
  blob mapped from a file or embedded by an optional `verso_heads.hpp`), the per-turn dump and the exploration
  stream.
- `policy.hpp` — the path loop is two passes: pass 1 computes the parent's hand score of every path, pass 2 adds
  the learned first-step terms (`lam_dir · log p_dir(step)`, `beta_q · (q(step) − max q)`) to OK and DIVE paths and
  selects. `verso_build_x` assembles the feature vector; `verso_route` is the tier-4 block (bounded BFS over the
  map memory from each landing cell: reach, remembered pearls and ripening beds, unseen cells, unpaired portals,
  corridor depth, SF-1 grids).
- `main.cpp` — loads the configuration and heads, and runs the v5 feature process only when a head or the dump
  needs it.

Parity: golden replay of `maelle-01-nodevil`'s transcripts, 61,667 turns / 1,247 dragons, 0 divergent; with
`VERSO_DUMP` set, 0 divergent (trauma B, schooltime A).

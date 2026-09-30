# verso-p2-platform

Verso platform, revision 2 (not a candidate; inert at the compiled defaults). Parent `verso-00-base`. Used
through arms (`VERSO_POLICY`, `VERSO_PARAMS`) for data collection and screening; a cycle's bot is this directory
plus an embedded `verso_heads.hpp` and compiled weights.

Changes from `verso-00-base`:

- Schema 450 columns: `h_dir_{F,R,L}` appended — the `dir` head's log p per first step (0 with no head), so later
  heads read the prior's opinion as a feature instead of re-deriving it. The `dir` term is `lam_dir · h_dir`.
- `q` head may have a fourth output, the production split: `beta_s · clamp(q[S] − max q[move])` is added to the
  production and opening split scores (not to the escape split).
- Split exploration for data games: with probability `eps_split` a legal production split replaces the chosen
  move, or the best move replaces a chosen production split (dump flag bit 2; bit 3 = the greedy action was a
  split).
- File-mapped head loading is compiled out under `__wasm__` (the judge's sandbox has no files; heads are embedded).

Parity: golden replay of `maelle-01-nodevil`'s transcripts (trauma B, portals B): 13,982 turns, 0 divergent; with
the cycle-0 head at `lam_dir = 1`, the `c0-hb-small~l1` arm's transcript (trauma B, 12,217 turns): 0 divergent.

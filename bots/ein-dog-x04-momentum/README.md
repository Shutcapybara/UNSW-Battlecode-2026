# ein-dog-x04-momentum: EWMA move-continuity prior (owner idea)

Parent: ein-dog-v01-control. One feature, default off:

- `w_dir` (set 0.8), `dir_alpha` 0.3: each process keeps an EWMA of its
  chosen first-step directions; single-step candidates score
  `+ w_dir * (ewma[d] - 0.25)`. Continues recent heading in near-ties,
  mildly penalises reversals; newborns start flat (momentum is earned).
  Top-team movement doctrine (306: 0.0% reversals over 1.06M steps,
  straight ~42-50%) says heading persistence is the public-meta shape.

Off-state (`w_dir` 0) is behaviorally identical to the control (the
score term and the EWMA update are both gated).

# tidus-x01-spread: three-phase density/exploration schedule

Parent: tidus-v01-control (newton-x10 source). All knobs default to the
parent's exact behavior (phase_open 0, multipliers 1.0).

- `phase_open 80`: rounds before this are the opening/scouting phase.
- Opening: `crowd_open 2.5` (2.5x ally repulsion -- spread), `own_open 0.5`
  (2x stronger ally-claim discount on targets), `unseen_open 3.0` (unseen
  tiles 5.0 -> 8.0), `wall_open 0.5` (candidate cells with >=2 kelp
  neighbors penalised -- scouts travel open lanes instead of hugging walls;
  all 13 original maps are border-open/toroidal, so this acts on kelp
  structure, which is where walls actually live).
- Mid (80..380): the parent's base response -- density toward the frontier
  (contested-bed values, support) is then appropriate.
- Late (380+): the parent's crown/feeding clocks unchanged.

Owner observations addressed: insufficiently aggressive early exploration;
dragons clumping more than other teams.

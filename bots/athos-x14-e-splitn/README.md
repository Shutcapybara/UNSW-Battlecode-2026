# athos-x14-e-splitn

Athos x-experiment off `bots/athos-v01-core/`: REPRODUCE executor enumerates
all legal split points n=2..min(L-2, splitn_max=6) instead of fixed n=2; P0
scoring unchanged and picks the best point (child room, parent trap, threat
at parent and child head all vary with n).

Hypothesis: choosing the safest split point raises child survival and closes
part of the end-game unit deficit. Method: holdout-first (arbiter roster),
then dev roster; results in docs/athos.md.

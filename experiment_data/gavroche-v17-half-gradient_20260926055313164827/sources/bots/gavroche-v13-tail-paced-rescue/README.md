# Gavroche v13: paced tail rescue

Parent: `gavroche-v09-two-stage-rescue`. The tested policy retains the v09
`SPLIT (length - 2)` rescue, paced so a tail-born large piece can act before
its follow-up split. Unlike v02, it does not cascade the large tail through
multiple splits in the same round.

Full 16-game target-map screen against x12, Hunter v20, Hydra v07, and Sinbad
v04, both side assignments: **12 wins, 4 losses**, no runner errors. It swept
x12 4–0, went 2–2 against Hunter, 3–1 against Hydra, and 3–1 against Sinbad.
Hunter won both of its Prisoner's Dilemma games. This is the current family tip.
The recorded benchmark predates the family rename; policy files are unchanged.
Results are from native tournament runs; no sandbox validation has been run.

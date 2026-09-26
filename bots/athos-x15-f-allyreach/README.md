# athos-x15-f-allyreach

Athos x-experiment off `bots/athos-v01-core/`: new decision feature
`ally_reach` -- cells an allied head can enter next action (sprints included,
reach capped at 3) cost w_ally_reach=0.35 in move scoring. Friendly-fire
crossing hazard; sim cannot know allies' chosen moves, so this is predictive.

Hypothesis: fewer self-collision deaths (54% of devil-map deaths are
self/wall). Method: holdout-first, then dev roster.

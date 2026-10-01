# Expedition frontier challenge v1 — frozen before new games

Date: 2026-10-01. Hypothesis: the existing, unmeasured Expedition 05 exploration
change (unseen_value 5 to 3) improves productive opening choices on the identity-
free HB540 base even when the opponent is stronger or has a different opening.
The parent is Expedition 01. Both runtime snapshots remain immutable.

Why this test now: Clair reports substantial net opening gains from this change,
with collision and newborn costs, on its different HB540 base. The user warns
that local improvement of our current approach may still leave it behind the
frontier. This test combines an outstanding predeclared mechanism with a new
opposition check; it is not a further mouth-rule variant or a fresh dose sweep.

Opponents, both seats, all ten original LIVE maps, seeds 1 and 2:

- hb1-17-prior-lam20: strengthened direction-prior reference, as reported by TT.
- ouroboros-g01-hbmimic-ares-r150: fast mimic opening with an Ares handover.

There are 80 fixtures per arm, 160 new games before reuse. No map is selected
because Expedition previously won or lost there. Seed 1 is discovery and seed 2
confirmation; finish both without source tuning. Fix maps, opponents, references,
runtime and toolchain hashes through campaign.py under panel frontier-v1 and
screen explore-frontier-v1. Use the same exclusive single-game-worker lock.
The new panel has separate directories; old z1/gen contracts and scores stand.

Primary decision: report paired outcome differences overall, by opponent and
map, separately for each seed, with wins/draws/losses and changed-fixture counts.
Report absolute parent and candidate strength against each control, including
losses where local economy/tempo improves. Retain opening tempo curves through
r150, checkpoints, midgame material/pressure and final termination/conversion.
Use map clusters for uncertainty; do not treat seeds or the same-family
opponents as independent samples of the contest field.

Advance only to a new, broader validation stage if seed-2 expected-score delta
is positive overall, neither opponent delta is negative, no map loses more than
one expected-score point, and opening tempo is not slower overall. Otherwise
the screen is negative or unresolved. Equality is not improvement. Do not relax
these conditions after seeing results. Inspect collision/newborn costs and
midgame/endgame consequences even if the numerical screen passes.

This cannot justify contest promotion or a claim of beating top teams. Both
controls share parts of the local HB/Ares lineage; g01 is a large local-only
mimic and not an authenticated current top-team implementation. A positive
result still needs unfamiliar topology, more diverse/stronger authenticated
opposition and sandbox validation. The original full pool/gen scans remain due;
this panel is additional evidence, not a replacement D-032 accept.

Competing explanations: the prior base changes the cost of exploration; a lower
exploration bonus merely farms familiar beds; extra growth produces vulnerable
children; the gain exists only versus the older roster. Use this panel to decide
whether to invest further, versus resource-aware splitting, midgame pressure or
state-driven conversion. Do not automatically generate another parameter dose.

# The out-of-sample rule — tournament maps are unseen; nothing may depend on map identity (director, 29 Sep 00:45 UTC)

Applies to every C1/C2 task and to the Sprint and Qualifier builds. It corrects the director's own prompts:
C1-A was told to ship an atlas of the ten public maps, C1-B was told to special-case Prisoners Dilemma, and C1-C/E
targets were given per map. The lead's point stands over all of that: **the tournament rounds are played on maps we
have not seen.** The public pool reveals the organisers' preferences (sizes, kelp densities, portal counts,
bed layouts), not their guarantees. A bot that knows the ten maps and nothing else is a bot that has never been
tested on the contest.

## The rule

1. **No decision may depend on which map this is.** No map-name, map-hash or atlas-index branches in policy code.
   Anything that varies by map varies by *observable structure the bot measures in play*: tile count, width and
   height, kelp density in the seen area, portal pairs discovered, bed density and spawn rates observed, own and
   enemy unit counts. C1-B's "Prisoners Dilemma: hold and deny" becomes a rule keyed on what makes PD what it is
   (a tiny map with few beds and early contact), tested on PD *and* on unseen maps with the same signature.
2. **The atlas is an optimisation, never a dependency.** It may stay only if (a) the bot with `atlas = -1` is a
   complete, measured bot, and (b) every candidate is measured **with the atlas disabled** on the generalisation
   panel below, and its numbers there are reported beside its live-pool numbers. A candidate whose edge disappears
   without the atlas is rejected. `params.hpp` gets a hard switch (`ATLAS_ENABLED`) and the dev pass runs it both
   ways. The safe direction is the one the chassis already has: unknown or transformed layouts match nothing.
3. **Targets are functions, not tables.** C1-E's per-map medians are re-expressed as functions of observable
   structure (pearls per dragon-turn vs bed density; units at r100 vs bed count reachable by r50; first-pearl round
   vs distance to the nearest bed cluster). The JSON stays as the calibration set; the policy reads features.
4. **The generalisation panel is part of every measurement.** Beside the ten live maps: the transforms in
   `maps/var/*_tr.map` and `maps/pub/*_rec.map` (same maps, mirrored/transposed — the atlas cannot match them, so
   they are the cheapest "unseen" test of atlas dependence) and the synthetic suite in `maps/new/` (20 designed
   maps across 17 motif families, weights in `training_map_weights.csv`; read `maps/new/EXPLAINER.md`). Report
   exact pairs on the live pool and on the panel separately. A candidate that wins on the pool and loses on the
   panel has learned the pool.
5. **The dev screen and field confirmation stay on the live pool** (the server's choice, not ours); the local
   generalisation panel is the gate they cannot provide. Both numbers go in every findings file.

## What changes per task, now

- **C1-A:** add `ATLAS_ENABLED` (default on) and the boot-turn cost without it; report the cheap policy on
  `maps/var` and `maps/new` with the atlas off. The room flood and body-chain inference must not assume the atlas.
- **C1-B:** the router's costs and horizons key on tile count, kelp density and portal count as measured; no
  map special cases; the ablation runs on the live pool *and* the panel, atlas on and off; the Schooltime
  flywheel is specified by its trigger conditions (bed density above x within reach, contact distance above y),
  not by the map.
- **C1-C / C1-D:** fixes are measured on the panel as well; the portal rules must work with portals discovered
  in play (probe, exit memory), which they already do.
- **C1-E:** deliver the feature-keyed targets (rule 3); the `maps/new` suite's own game diagnostics can give the
  first check of whether the corpus relationships hold off-pool.
- **Sprint/Qualifier builds:** whatever is live on the day runs with `ATLAS_ENABLED` as measured; if the panel
  numbers are worse with it on, it ships off.

## Why this matters more for us than for them

The teams above us will have tuned to the pool for weeks. Some of their edge on the ten maps is memorised. A
bot built from measured structure with the same efficiency is the one that keeps its rating when the maps change,
and the qualifier is best of 7 on maps nobody has seen. This is the one place where being late is an advantage,
if we do not throw it away by shipping an atlas.

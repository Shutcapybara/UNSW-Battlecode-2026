# Ares V43 — exploration-only teammate separation

## Hypothesis

V42's approach cost can reduce growth because it applies to resource and prey
routes as well as exploration. Scoping it to exploration should preserve
dispersion while restoring productive movement toward pearls and prey.

## Changes

- Forked V42 as `ares-v43-exploration-only-dispersion`; V42 remains unchanged.
- Kept V42's removal of the Devil lane bonus and its remembered bedless-sector
  exploration discount.
- Applied the visible-teammate approach cost only while the goal is exploration
  (`x`, or an equivalent fallback/remembered target), not while pursuing a
  known pearl or bed, a hunt, an escape, or a portal dive.
- Kept the crown and feeder exemptions.

## Evidence and status

The V42 native ten-map screen against V41 scored 8–12. Replay timelines showed
lower pearl collection and population growth on several losing maps.

The native V43-vs-V41 screen used `unswbc 1.2.2`, the same ten maps, both
starting seats, and generated seeds. V43 scored **12–8**, with zero runner
errors, replay-analysis errors, or runtime faults. It swept Default, Dilemma,
Queen of Spades, Slithery Fight, and Trophy. V41 swept Devil, Portals, and
Schooltime; Autarky and Trauma split 1–1. This is one development screen, not
broad promotion evidence. V43 remains experimental.

The full report, seeds, logs, and replays are in the ignored
`experiment_data/ares-v43-exploration-only-dispersion_20260930125019196045/`
directory. The separate V42 and V43 screens used independent generated seeds,
so their 8–12 and 12–8 results do not isolate a causal win-count change.

The contest accepted V43 as submission **v95**, reported as processing. This
does not change the candidate's local experimental status.

# Ares V44 — shared sector exploration

## Hypothesis

V43's explored and bedless-sector memory is private to each dragon. Dragons
can therefore select the same apparently unexplored sectors, even after a
teammate has searched them. A short-lived target lease should also spread
explorers across remaining frontiers.

## Changes

- Forked V43 as `ares-v44-shared-sector-exploration`; V43 remains unchanged.
- Added a sonar sector report containing the sector index, strongest reported
  single-dragon coverage count, and whether any bed was found. Coverage reports
  are merged by maximum rather than sum, while bed sightings are merged by OR.
  Barren-sector value remains confidence-weighted and gradual.
- Added an eight-round exploration-sector claim, refreshed every three rounds.
  Active claims are relayed, unseen cells in another dragon's claimed sector
  receive a 0.10 value multiplier, and the sector fallback prefers unclaimed
  sectors. Pearl and prey goals do not create claims.
- Use existing low-priority sonar lanes for these packets. Current pearl,
  crown, prey, portal handoff, and split handoff behavior retains priority.
- Kept V43's visible-teammate approach penalty.

## Replay evidence

Match 710870 was Ares V43 (submission 13183) for Just Keep Swimming on Autarky.
The replay ended at round 447. The replay review recorded 616 distinct cells
visited by Team A, 270 pearls, and 95 splits. The visual replay prompted the
shared-memory change; internal target diagnostics were not recorded, so the
individual target choices cannot be reconstructed from the replay alone.

## Verification and status

The candidate compiled with C++20. A native `tools/cx/bench.py` screen used the
ten live maps, both sides, and seeds 1–3 against V43: V44 scored **32–28** in
60 games, with no draws or runner errors. Seed 1 alone was 8–12; seeds 2–3
were 24–16. Autarky was 4–2 across the three seeds. The Autarky pearl and
length r100 means were only 0.7 pearls and 2.5 length above V43 across six
fixtures. The small positive win margin is not strong evidence of a repeatable
gain, so V44 remains experimental and is not promoted.

Results are in `build/cx/ares-v44-vs-v43-20260930.jsonl` and
`build/cx/ares-v44-vs-v43-seeds2-3-20260930.jsonl`. V43 remains the measured
comparison parent and the current local Ares frontier reference.

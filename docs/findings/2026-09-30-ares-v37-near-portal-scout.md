id: 2026-09-30-ares-v37-near-portal-scout
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V37 keeps near-portal priority with a smaller exploration bonus
task: Narrow V36's portal value after its loss against V19
supersedes: ""
evidence:
  - Public match replay 674727
  - V36 seed-1 sandbox screen against V35 and V19
---

# Ares V37 — near-portal scout

V36 fixes the scoring mismatch by assigning a no-pearl unpaired portal target
value 8, above unseen ground at 5. Its seed-1, ten-live-map screen scored
13–7 against V35 but 9–11 against V19; V35's saved screen against V19 was
13–7. V36 is not being promoted.

V37 changes only that new value, reducing it to 6. At the reported approach,
the portal dive is two search steps away: its discounted target remains above
the nearest unseen-ground target. A farther portal can lose to closer
unexplored space. V37 retains V36's age-3 gate and 40-round pearl-memory
check, so remembered pearls and bed targets keep their existing priority.

The seed-1 sandbox screen used unswbc 1.2.2, the ten live maps, and both
seats, with zero runner errors. V37 scored **17–3 vs V35** and **10–10 vs
V19**. On Queen of Spades it scored 2–0 against both opponents. V35's saved
V19 screen was 13–7, so V37 still does not improve on the best V19 result. It
remains experimental and outside the local frontier. It was uploaded as
submission v92 (ID 12851) on 2026-09-30 08:44 UTC and became active. Its API
source hash is
`d0b6e74c95f9d98e1cbceb58c8d82179d21ad676b699aa2ab3e11d2248ca683f`.
Results are in the ignored
`build/ares-v37-vs-v35-vs-v19-live10-seed1-20260930/` directory.

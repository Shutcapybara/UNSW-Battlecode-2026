# bokuto — free lane bots (Fable instance), on the carthage-05 chassis

All `bokuto-NN-*` bots are `carthage-05-free-sprint` plus two headers and small edits in `policy.hpp` / `main.cpp`:

- `bokuto_branch.hpp` — dead-end branches of the known terrain (leaf stripping over `World::dest`), per-branch
  pearl prediction (seen, remembered, due to spawn, or a known gap-1 bed) and the harvesting rule: a visit nets
  (pearls − 2) because the head part of 2 dies at the dead end; a dragon enters only when that is ≥ 1, never the
  queen, never when the team is within 2 of the unit cap or after round 340. `branch_allowed()` gates
  `cell_value` (pearls in a pocket that does not pay are worth 0) and the trap "farm" discount in `decide`.
- `bokuto.hpp` — `Guard::apply` runs after `Policy::decide` and may replace the action:
  - send-back split (`H`): when exactly 2 of our segments remain inside a corridor we are leaving and the corridor
    holds ≥ 3 pearls, split 2 — the child faces inward and harvests; the piece left at the dead end has died first;
  - escape split when stuck with an unknown body (`E`), cage split (`C`: the Schooltime 2×2 boxes), unit-slot
    reserve for the queen (`R`), the policy's deliberate feed deaths and head-on strikes are left alone;
  - the queen (ids 0/1): a hard dodge (`Q`) — never end a step where an enemy head can reach this round, next to any
    head, on a blind portal landing, or in a one-way corridor when a safer step exists; a 6-turn survival search
    over known terrain only (`G`/`g`), relaxed when it blocks everything;
  - allies yield to the queen (`Y`): never end next to her head when another 3-turn-safe step exists;
  - the swarm otherwise plays carthage's game; only a pocket that does not pay and a certain-death step are vetoed.
- `policy.hpp` — the queen hides (`target_why 'q'`) once the team has 6 units or from round 120: a BFS target far
  from every enemy head ever seen (half-life 150 rounds) and reported, toward home, uncrowded, open, never a pocket;
  she sheds length to 2–3 by splitting (production) until round 380, then values length (fed as the crown). She never
  hunts, dives or strikes, pays 3× for threats and 6 for danger cells. Crown election is carthage's among
  non-queens; the queen broadcasts a type-1 beacon from round 200 (allies rebroadcast), and from `feed_from` feeders
  feed her first. Queen production splits are allowed only in the opening (round ≤ 60) or while shedding.

Versions: 01 survive (K=7 guard) · 02 vac · 03 harvest · 04 queen · 05 hider · 06 feedqueen · 07 dodge ·
08 yield · 09 rooms (escape rescue outside branches, queen trusts known terrain, foraging queen on small teams) ·
10 letfarm (non-queen guard reduced to pockets and certain death). Scorecards in `claude/bokuto-status.md`.

---
id: antioch-queen-director
author: antioch (P2-A Claude analyst)
kind: hypotheses + evidence
question: Is the queen a natural director? Does it change the portal-exploration problem, and is a latent-state swarm (scouts triggered by the queen) worth testing?
evidence: s1 store, post-change transits (611 k transit steps) and deaths, ten ladder maps; HB-1 / C2-0 / Q4 findings
query: SQL in this file (DuckDB over build/s1/corpus/{transits,deaths}, games.era = 'post')
---

## Why the queen changes the problem (lead's framing)

- **Phase 1's portal finding:** the leak was traffic, not blindness (S-1 Q4). Exits into our own traffic, same-pair
  doubles and newborn transits killed dragons. Pre-entry portal rules were throttles that cost economy one for one.
- **Before 1 Oct, risk was cheap.** No dragon was special, so losing one to a bad exit cost only its length. The economy
  gradient rewarded running dragons through portals and accepting the losses, and no hand rule beat that.
- **The queen breaks the symmetry.** One dragon must not take the gamble, and every other dragon becomes expendable
  relative to it. That makes a division of labour natural:
  - the queen is conservative and anchors the swarm;
  - cheap scouts split off to take the risks and report back;
  - the rest act on the reports.
- **The queen is already a natural director.** It is the one dragon both teams can identify from turn 0 (id 0 / 1). Its
  position is a meaningful rendezvous, and its survival is the one state every other dragon's best action depends on (H-Q7).

## Evidence: portal danger persists, so a scout's report has value

Post-change transits. "Last own transit" is this team's most recent transit through the same portal pair 4–30 rounds
earlier.

| condition | transits | die within 3 | blind exit |
|---|---|---|---|
| no own transit on this pair in the last 4–30 rounds | 71,498 | 0.249 | 0.592 |
| last own transit there **survived** 3 rounds | 413,767 | **0.194** | 0.239 |
| last own transit there **died** within 3 | 131,927 | **0.574** | 0.386 |

- **Danger at a portal exit persists across rounds:** 3× the risk after a death there. So one scout's outcome is
  informative for the next 4–30 rounds.
- **The field ignores it.** 21 % of all transits go through a pair whose last own transit just died, and 57 % of those
  die.
- **This is the cheapest version of the scouting idea.** It needs no new behaviour: it only needs the outcome of the last
  transit through each pair to be known.
  - Possible sources: a death seen in view; a missing heartbeat (H-Q6); a scout's "alive after exit" ping.
  - Caveats: this is association within the same games and maps (some pairs are just bad), and transit rows are per
    step. Persistence is exactly what makes a report useful, though, whatever its cause.
- **The queen and portals today:**
  - queens make 0.8 % of transits (4,918 of 611 k) and die within 3 less often (0.159 vs 0.282);
  - 17.7 % of queen deaths happen within 3 rounds of a transit (others 19.4 %).
  - So the field already mostly keeps queens off portals by accident: the queen is small and early-dead. A kept-alive
    queen (H-Q1) will face the portal question directly.

## Hypotheses

| id | claim | ledger | falsifier | size | tester |
|---|---|---|---|---|---|
| **H-S1 portal memory** | Do not transit a pair whose last known own transit died within 3 rounds in the last 30 rounds (team knowledge from view + sonar). Cuts transit deaths without the throttle cost of phase 1's pre-entry rules, because it only blocks the 21 % of transits that face 57 % risk. | L06 (portal-exit knowledge, 0.3 → propose 0.5), L23 | transit died3 on the panel not down by ≥ 25 %, **or** economy lower bound < −0.02 (it became a throttle again) | pool + gen, seeds 1–3; Portals / Trauma / Schooltime per-map deltas reported | any tester (CPU) |
| **H-S2 scout-and-return** | The queen (or any dragon at a portal mouth) splits off a length-2 scout. The scout transits, survives or not, and its fate is reported: a return ray (alive) or the queen's missed-heartbeat logic (dead). Only then do others follow. The queen never transits an unscouted pair. | new; relates to L14 (scout splits, 0.25), L33 | panel transit died3 not lower than H-S1 alone, or queen alive@490 unchanged, or economy LB < −0.02 | after H-S1 and H-Q1 | Claude tester (needs H-Q6's sonar packing) |
| **H-S3 latent-state swarm, directed by the queen** | Each dragon carries a latent state (forage, scout, escort, feed, hunt, turtle) that biases its move scoring. Transitions fire on local input and on sonar commands, notably the queen's (mode from H-Q7, "scout this pair", "escort", "feed me"). A small state machine over today's search beats both the stateless bot and each single hand rule tried so far (carthage-01/02/06/07). | L31 (0.5), L32 (0.4), L33 (0.5): this is their concrete form, anchored on the queen | stacked state-machine arm not > the best single queen arm on overall paired win, both panels | 2–3 arms; after H-Q1 has a winning arm to build on | Claude tester; GBT-learned transition rules later (H-RL5 can learn per-state priors) |

## What the field tells us about latent states

- **The top teams look memoryless.** HB-1 found Heartbreaker's policy about 83 % predictable from the current 7×7 view.
  History features added 0.2 pp. cheji bt and Stockfish are 75–76 % predictable; a quarter of their moves are
  undetermined by view plus simple memory. C2-0 found the top ten's fight edge is composition, not coordination.
- **That is an opening, not a refutation.** Nobody in the corpus visibly runs a directed swarm, so the payoff of
  coordination is untested, not shown to be small. The queen rule is the first rule that makes coordination pay
  structurally.
- **Order:**
  1. H-S1 (a memory rule, no new behaviour);
  2. H-Q1's winning arm;
  3. H-S2 (scouts);
  4. H-S3 (states).
  This order stops a state machine being judged before its parts are known to work.

## Mechanics check: sonar rays pass through portals (settled)

- On 12 post-change Portals games, 29,458 of 412,677 unrefracted rays ended **off their own straight line**. Example:
  g800149 r3, a ray sent south from (3,6) ended at (27,9) on kelp. So rays traverse portals.
- A scout on the far side can report back by ray when it is aligned with a portal mouth. The queen's heartbeat can also
  reach dragons beyond a portal.

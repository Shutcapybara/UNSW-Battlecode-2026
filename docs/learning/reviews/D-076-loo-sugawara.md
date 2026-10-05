# D-076 §C: leave-one-out on the free-lane base. Owner's decision (Sugawara, 5 Oct 2026 06:40Z)

**Decision: I take the Chair's suggestion.** The queen work moves from adding layers to carthage-05 to removing layers
from the free-lane base, one at a time. I add one exception: a single cheap Q1r build (below). q2a stays parked. The
Q2b line of the plan is closed.

## Evidence (my replication from frozen inputs)

Source: Asahi's pool index files `wt-asahi/build/asahi/runs/<bot>/<fp>/pool/index.jsonl`. Filter: seed 1, 272
fixtures (map × opponent × seat), 0 missing, unswbc 1.2.3, same host. Paired against carthage-05 (7df05a3f, seed-1
rows only; that file also holds seeds 2–3, so it has to be filtered). "Disc" counts fixtures where winner or rounds differ.

| bot | layers relative to c05 | wins | Δ wins | gains / losses | disc |
|---|---|---|---|---|---|
| carthage-05 | — | 226 | — | — | — |
| asahi-21-q1cage-c05 | Kenma pocket, no reserve | 226 | 0 | 0 / 0 | 2 (Schooltime) |
| kenma-03-pocket-queen | pocket + global reserve | 220 | −6 | 5 / 11 | 27 |
| asahi-25-q2bcrown-c05 | bokuto-04 queen hunks only | 219 | −7 | 14 / 21 | 134 |
| **bokuto-02-vac** | guard + cage split | **195** | **−31** | 21 / 52 | 169 |
| bokuto-04-queen | 02 + 03 branch gate + 04 queen | 226 | 0 | 31 / 31 | 172 |

Readings:

1. **The Bokuto layers do not add up.** The guard alone (02) costs 31 wins: losses spread over 12 maps (Autarky 7,
   Trauma 7, Islands 5, Dilemma 5, UNSW 5) and gains concentrated on Weakhold (8). Layers 03 and 04 together win them
   back. The queen hunks alone on c05 cost 7. Whatever a layer is worth depends on the layers below it, so moving
   layers across to c05 measures the wrong thing. That is two failures at the first step (Q1 and Q2b), as the Chair said.
2. **Kenma's pool cost is the global reserve, and it falls off the pocket.** Off Schooltime, kenma-03 loses on
   UNSW (5) and Australia (4), mostly to `longest dragon`. Q1 (no reserve) is pool-identical to c05. That leaves a
   targeted build that remains a single switch (Q1r below).
3. **Information legality, bokuto-13-cull:** the bokuto-06 queen beacon is set from sonar unpack (policy.hpp l.454),
   from the observer's own sight (l.563) or from the queen herself (l.565). That is per-process and legal. The
   bokuto-12 queen gate uses `w.me & 4095`, `w.units` and `w.rnd`, all observable. I found no map identity in the
   tagged lines. bokuto-13's corridor rule comes from a harvest audit on Trauma, but the rule itself is structural:
   a corridor holding at least 3 remembered pearls.

## The layers of bokuto-13-cull (tags in the tree)

02 guard (bokuto.hpp) · 03 branch gate (bokuto_branch.hpp, policy l.835/1646) · 04 queen no-split after r60 +
careful (l.1150/1199/1580/1623) · 05 queen hiding/shedding (l.1181/1221/1449) · 06 queen beacon/feeder/crown
(l.109/597/661/788) · 08 yield to the queen (bokuto.hpp l.317) · 09 queen forages while the team is small (l.1238) ·
11 keep ≥ 3 cells from enemy heads (bokuto.hpp l.97) · 12 queen fights while the team is small (l.73; bokuto.hpp
l.313) · 13 corridor target + spare-dragon cull (l.1416; bokuto.hpp l.270).
Six of the ten layers are about the queen (04, 05, 06, 08, 09, 12).

## The plan (Q-sugawara-01 §8)

- **Base = whichever bot D-076 §B puts into trial 2.** If its pool reaches ≥ 226 by 07:45Z, the base is
  `bokuto-13-cull`, otherwise `bokuto-04-queen`. The ladder trial tells us whether the base is worth adopting. The
  leave-one-outs tell us which layers carry it, and they are only worth running if the base is a candidate.
- **Order (queen first, one switch each, `-DSG_NO_<tag>` guards around the tagged hunks, on a byte copy):**
  (1) −04+05 together: "no queen caution". Both tags guard the same decision, so removing only one would leave the
  other doing the work, which tells us little. (2) −06: no beacon, no feeders, no crown. (3) −12+09: the queen as a
  plain worker while the team is small. (4) −02: no guard. This is the largest layer on the lineage evidence. Others
  (03, 08, 11, 13) only if the base is adopted.
- **Readings for each build:** the seed-1 pool **paired against the base, not against c05**, with queen columns
  (queen-decided W–L, queen alive at the limit), and qk (68). A layer "carries" if removing it costs ≥ 5 pp of pool
  wins with the 95th percentile below 0, or if the queen-decided W–L on pool + qk falls by ≥ 5 net.
- **Q1r (cheap, parallel, on c05):** Q1 plus Kenma's reserve (`w.limit − 1` for id > 1), applied **only while
  `w.rnd < 60`**. The Schooltime cage deaths are round-0/early (Unit 18: 5 cage deaths at r0). Expected: pool parity with
  c05 outside Schooltime ≥ 268/272, Schooltime queen alive ≥ 10/14. If the early window is not enough (alive < 10/14),
  the reserve is needed late too, and the cage fix belongs to the base's own queen layers.

## What I am not doing

Q2b on k16, more crown variants on c05, and q2a are all off: the transfer direction has been answered. The k16 twins
in build/asahi/hold stay held.

## Precedent

These are standard ablations in the AlphaStar and OpenAI Five reports: components are measured by removing them
from the full agent, because their effects interact. In Lux S2 and Halite IV write-ups, feature transplants between
bots routinely failed for the same reason.

Owner forecasts are closed (D-072 §B), so these are not for Brier. For the record: P(at least one queen layer of the base
"carries" by the rule above) 0.6. P(Q1r Schooltime queen alive ≥ 10/14 with parity ≥ 268) 0.5.

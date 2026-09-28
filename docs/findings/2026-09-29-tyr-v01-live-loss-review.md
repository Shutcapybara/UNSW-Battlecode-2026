---
id: 2026-09-29-tyr-v01-live-loss-review
author: gpt/codex/2026-09-29
kind: observation
title: September 28 losses identify early resource control, dead-end split efficiency, and long-dragon safety as Tyr V01 iteration targets
task: User-provided public replay notes for future strategy iteration
supersedes: ""
evidence:
  - Public match replays 499792, 499794, 499795, 499797, 499798, 500737-500745, 500751, 500754-500756
  - Battlecode API submission listing: submission 10413, tyr-v01-yuna-momentum, uploaded 2026-09-28T15:14:16Z; listed active
  - Battle metadata: Just Keep Swimming (team 7), game maps, opponents, outcomes, and start times
---

# Live replay loss review — 28 September 2026

These 18 replay notes are a focused iteration record, not a benchmark estimate.
They cover three opponent series: ComTamSuonNuong, dev test 1 :P, and dev test 2.
Battle metadata confirms that the opponent won all 18 selected games.

## Model attribution

**Best-supported attribution: Tyr V01 — Yuna Momentum, submission #10413.** The
team submission listing reports that version uploaded at 15:14:16 UTC and was
active; the reviewed games started between 15:15 and 15:30 UTC. The battle
metadata returned for these games does not include a per-game submission ID,
so the link to #10413 is a time-and-status-based attribution rather than an
exact historical version check. Correct it if the live-run manifest or another
provenance record identifies a different submission.

Tyr V01 combines Fenrir V20's production, portal memory, threat model, and
newborn separation with Yuna V03's direction-momentum mechanism. These replays
identify decision classes for follow-up; they do not isolate which part of that
combination caused each failure.

## Game-by-game record

| Replay | Map · opponent | Loss observation | Future iteration target |
|---|---|---|---|
| [500737](https://game.battlecode.au/visualiser?match=500737) | Portals · dev test 1 :P | At round 54, a dragon moves into a wall instead of splitting. | Add a wall-aware fallback that compares safe split actions when movement has no viable exit. |
| [500738](https://game.battlecode.au/visualiser?match=500738) | Slithery Fight · dev test 1 :P | A length-2 enemy can dash twice to kill a longer dragon. We could have dashed away, and feeding the longest dragon starts too late to recover the length gap. | Forecast two-step enemy reach, value a defensive dash even when it costs length, and begin feeding before the deficit becomes unrecoverable. |
| [500739](https://game.battlecode.au/visualiser?match=500739) | Queen Of Spades · dev test 1 :P | We explore the portal too late and concede resource control. | Give early portal discovery and access a stronger opening priority. |
| [500740](https://game.battlecode.au/visualiser?match=500740) | Default · dev test 1 :P | We reach the yellow and blue portals too late, allowing the opponent to control resources. | Assign early scouting coverage to both portal routes. |
| [500741](https://game.battlecode.au/visualiser?match=500741) | Trophy · dev test 1 :P | At round 14, a dragon could head north for an easy extra pearl; we lose the early resource race. | Include nearby, low-risk pearl detours in early route choice. |
| [500742](https://game.battlecode.au/visualiser?match=500742) | Prisoners Dilemma · dev test 1 :P | The opponent controls the central feeding dead ends and can profit by reaching the end and splitting at a net segment cost of two. | Model the net resource value of dead-end feeding and contest or deny profitable central access. |
| [500743](https://game.battlecode.au/visualiser?match=500743) | Autarky · dev test 1 :P | Dead-end spawner feeding uses an inefficient split: we should kill two and let the rest escape, rather than killing three. | Evaluate split size against the minimum sacrifice needed to collect and exit. |
| [500744](https://game.battlecode.au/visualiser?match=500744) | Devil · dev test 1 :P | Too many dragons take the same route, so the opponent reaches central resources first. | Deconflict opening routes and preserve coverage of the center. |
| [500745](https://game.battlecode.au/visualiser?match=500745) | Trauma · dev test 1 :P | Portal exploration starts too late and the opponent gains resource control. | Improve the timing and assignment of early portal scouts. |
| [500751](https://game.battlecode.au/visualiser?match=500751) | Queen Of Spades · dev test 2 | Portal exploration starts too late and the opponent gains resource control. | Check portal scouting across another opponent and map. |
| [500754](https://game.battlecode.au/visualiser?match=500754) | Prisoners Dilemma · dev test 2 | Dead-end spawner feeding wastes segments because the split is not maximal. | Compare candidate split sizes and minimize the cost of clearing a feeding route. |
| [500755](https://game.battlecode.au/visualiser?match=500755) | Autarky · dev test 2 | Dead-end spawner feeding again wastes segments through a suboptimal split. | Validate the split-cost rule across dead-end layouts. |
| [500756](https://game.battlecode.au/visualiser?match=500756) | Devil · dev test 2 | Long dragons sometimes path into walls or remain exposed to repeated enemy dashes; dashing and losing length is preferable to being killed. | Protect high-value dragons with wall-safe routing and an explicit survival-versus-length tradeoff. |
| [499792](https://game.battlecode.au/visualiser?match=499792) | Devil · ComTamSuonNuong | Too many dragons travel in the same direction and we lose early center control. | Reduce opening route convergence and measure time to first central resource. |
| [499794](https://game.battlecode.au/visualiser?match=499794) | Prisoners Dilemma · ComTamSuonNuong | Dead-end feeding again uses suboptimal splits. | Tune minimum-cost sacrifice and escape timing. |
| [499795](https://game.battlecode.au/visualiser?match=499795) | Queen Of Spades · ComTamSuonNuong | Long snakes expose themselves to an opponent suicide attack. | Apply the same enemy-dash reach and crown-survival response to long dragons. |
| [499797](https://game.battlecode.au/visualiser?match=499797) | Slithery Fight · ComTamSuonNuong | Dead-end feeding again uses suboptimal splits. | Test split efficiency on a second opponent and map geometry. |
| [499798](https://game.battlecode.au/visualiser?match=499798) | Trauma · ComTamSuonNuong | Portal exploration starts too late and we lose the resource race. | Confirm early portal access as a recurring opening weakness. |

## Iteration themes

1. **Open with distributed resource access.** Assign separate dragons to
   portal routes and central lanes; score nearby pearls early enough to prevent
   an opponent from taking uncontested control.
2. **Keep long dragons alive.** Compare ordinary movement, dash, and split
   escape under wall and enemy two-step threats. Accept a small length loss
   when it prevents a likely kill, and move the feeding start earlier when the
   resource race is already slipping.
3. **Make dead-end feeding economical.** Compare the likely pearl return,
   minimum sacrifice, exit route, and opponent access before choosing a split.
   The repeated observations point to wasting segments, while the Prisoners
   Dilemma loss also shows that an opponent can profit from owning the center.

The next candidate should report these as separate outcomes: early portal and
center arrival, pearl lead by round 30, segments spent per dead-end harvest,
largest-dragon length and survival, and avoidable wall deaths. A change should
be evaluated against Tyr V01 on matched maps and both sides before promotion.

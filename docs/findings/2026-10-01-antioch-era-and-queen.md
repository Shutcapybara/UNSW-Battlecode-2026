---
id: antioch-era-queen
author: antioch (P2-A Claude analyst, replay lead)
kind: observation
question: When did the live server adopt unswbc 1.2.3, what exactly is "the queen", and who keeps it alive?
evidence: >
  1,804 corpus games 30 Sep 00:00Z – 1 Oct 12:40Z (a time-stratified sample, plus every game 03:30–10:30Z) for the era;
  3,055 games (all 1,603 post-change games to 12:40Z + 1,452 pre-change from the sample) for the queen; local probes on
  slithery_fight / autarky / dilemma
queries: tools/antioch/era.py, tools/antioch/queen.py (outputs build/antioch/, not committed); SQL below
---

## Answer

1. **Switch-over: between 05:57:53Z and 09:26:58Z on 1 Oct.** No games were played in that gap.
   - Every sprint priced before the gap costs k − 1. Every sprint after costs max(0, k − ⌈L/4⌉).
   - Of 1,804 games, 744 have a sprint that tells the two rules apart; **none mixes the two**.
   - The engine's new queen field is non-zero in 0 % of pre-change games and 3.5 % of post-change games.
   - **Era rule:** `post` ⇔ `started_at ≥ 2026-10-01T06:00Z`. The store carries it as `games.era`; `S1_ERA=post` scopes
     the `q.py` views and field norms.
   - The live **map pool changed at the switch.** Pre-change games on 30 Sep include Around UNSW, Australia, Islands,
     Maze, Stripes, Tower Defense and weakhold. Post-change games are only the ten ladder maps.
2. **The queen is the team's original lowest-id dragon, and there is no succession.**
   - The engine writes a new 4th int32 into each side's `TeamStanding` in the replay. It equals that dragon's length at
     the end, and 0 once it has died: in 33 of 44 checked sides it was dead and lower-id dragons were alive.
   - On a split the parent keeps its id **and the head end** (12,039 of 12,039 splits). The queen survives splitting but
     keeps only the head piece. 41 % of field splits leave the tail child longer than the parent.
3. **Almost nobody keeps the queen.** Post-change, the queen is alive at the end of a round-limit game for **2.2 %** of
   sides (top ten **0.7 %**, r11–30 0.3 %, others 3.3 %).
   - Median queen death round: **r41** (pre-change r83). 54 % are dead by r50, 84 % by r150.
   - Causes: wall 35 %, h2h 37 %, self 15 %, invalid 10 %. Only 31 % are enemy-credited.
4. **Three maps kill the queen by design.** On Slithery Fight, Autarky and Prisoners Dilemma the queen spawns in a
   dead-end pocket: 2–3 reachable cells from its head, its own body behind it.
   - It dies on r4–5 in **100 %** of games in both eras.
   - A dragon cannot pass: no action and a 0-step move are both fatal (local probe, every dragon dead on round 1).
   - On these maps the queen level is 0 = 0 for every team, and the tiebreak falls to longest.
   - **Splitting cannot get the queen out (H-Q3, closed).** On Slithery the head starts at (8,10), facing into a 3-cell
     dead end, (8,8)–(8,10). Its own body blocks the only exit, and the parent always keeps the head. Splitting 7 → 5 → 3
     buys two stall turns, then two forced moves end at the wall. Engine probe
     (`build/antioch/probe-pocket`, split to 2 on r0, 2 seeds × 3 maps): the queen dies on r3–4 every time.
   - So the queen level is moot on 3 of the 10 ladder maps, including Slithery, a round-limit map.
5. **Where one queen survives, it decides the game.**
   - In post-change round-limit games where exactly one queen was alive, its side won **36 of 36**.
   - **26 of those 36 winners were behind on total length.**
   - Under the new rule the queen decided 36 of 833 round-limit games, longest 786, total 11.
   - **Counterfactual:** our queen is alive at the end of every round-limit game, except on the three pocket maps, and
     nothing else changes. The opponent's queen is already dead in 98 % of round-limit games.

     | cohort | win rate now | win rate with queen kept |
     |---|---|---|
     | top ten | 0.773 | 0.877 (+10 pp) |
     | r11–30 | 0.661 | 0.778 (+12 pp) |

   - The gain sits on the round-limit maps: Portals, Trauma, Schooltime and Default each give the top ten +22–26 pp.
     QoS gives +12 pp. Devil, Trophy and the pocket maps give 0.
   - This is an upper bound: it ignores the cost of protecting the queen and the field adapting.
6. **The gate's win share uses the old tiebreak.**
   - `tools/analysis/features/frame.py:224-233` works out the winner as longest → total and never reads the engine's
     verdict.
   - `extract.py:411` takes `won` from it, and `scorecard.py:141` takes win share from `won`.
   - In the field this gets the winner wrong in **2.8 %** of post-change round-limit games. It will grow as teams start
     keeping queens.
   - The fix reads the engine's own winner, end reason and queen field, and bumps FRAME_VERSION 5 → 6:
     `tools/antioch/patches/frame-engine-verdict.patch`. It is not in my lane; the director applies it.

## Surviving queens (post-change, round-limit, n = 36)

- Length by checkpoint, median (mean): r100 3 (3.7), r250 3 (5.7), r400 5.5 (10.1), end 10.5 (15.8).
- They are their team's longest dragon in 58 % of cases and 39 % of their team's length.
- From r300 they eat a median of 7 pearls (1.5 from ally corpses), sprint rarely and move about 10 cells net.
- They come mostly from lower-ranked teams (segmentation fault, :3, uoa, miga bot, Tony S, …), not from deliberate
  queen play by the top ten.
- Maps: Trauma 21, Schooltime 6, Portals 5, Default 3, QoS 1. Queens on Trauma and Schooltime are the long-lived ones
  (median death r115 / r104). On Devil, Trophy and QoS they are dead by r41–87.

## Hypotheses

| id | claim | ledger | falsifier | size | tester |
|---|---|---|---|---|---|
| H-Q1 | **Queen preservation**: a queen-protection rule from r0 (no h2h risk, no wall or self moves, no sprint into contact; split children off its tail rather than shed its head) raises round-limit wins by ≥ 10 pp (Portals, Trauma, Schooltime, Default, QoS: the pool maps where it can matter) at a cost of ≤ 0.02 in economy. | new row, proposed 0.7 (relates to L39, L31) | queen alive at r490 on the pool < 0.5, **or** round-limit win Δ lower bound ≤ 0 | pool + gen, seeds 1–3: one panel run resolves a 10 pp win change (n ≈ 300 round-limit side-games) | any; the Claude tester first (queen measurement is already in its first unit) |
| H-Q2 | **Feed the queen late**: once the queen is secure, routing the r300+ cull into the queen (TT's 82 % feed-beside-the-long-one pattern, keyed on the queen id) wins the both-alive round-limit games. | L39 (re-keyed to the queen) | both-alive round-limit win ≤ 0.5 against queen-keeping opponents | needs queen-keeping opponents: a mirror of H-Q1 vs H-Q1+H-Q2, about 200 games | after H-Q1 |
| H-Q3 | ~~Pocket escape by splitting on Slithery, Autarky, PD~~ — **falsified 1 Oct** (see answer 4). The queen is doomed on these three maps; tiebreak there is longest → total. | — | — | — | — |
| H-Q4 | **Kill the queen**: once the field keeps queens, hunting the enemy queen (lowest id, known from turn 0 by symmetry) is worth more than material. | new, 0.3 for now | field queen survival in round-limit games stays < 10 % for a week (then there is nothing to hunt) | corpus watch; no test yet | — |

## Queries

```sh
python3 tools/antioch/era.py --index public_replays/corpus/index.jsonl --dir public_replays/corpus/replays --since 2026-09-30 --out build/antioch/era.parquet
python3 tools/antioch/queen.py --index public_replays/corpus/index.jsonl --dir public_replays/corpus/replays --since 2026-09-30 --out build/antioch/queen.parquet
# then in pandas: join games.parquet (era) and teams.parquet (cohort), filter end_reason == 1 for round-limit games
```

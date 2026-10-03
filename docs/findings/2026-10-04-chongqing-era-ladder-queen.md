# Chongqing unit 1 — the ladder was reset, the top teams now keep queens, and our live bot forfeits the queen on Schooltime at round 0

Claude analyst (Opus 5.5), replay lead, Phase 2 wave 2. 4 Oct 2026, 00:10 UTC. Host: the Mac (Cowork VM over the mounted
repo), worktree `wt-chongqing`, branch `r/chongqing`. Store queries: `tools/chongqing/qq.py` (light DuckDB connector over
the post-change parts; `tools/s1/q.py` binds too slowly over the mount) with the queen views in §A. Era: `post` ⇔
`started_at ≥ 2026-10-01T06:00Z` (D-042), unchanged. **Every number below is provisional**: the store holds 3,535 of the
23,035 in-scope post-change games (§1), and the 2 Oct top-ten games it holds are almost all unranked games against us.

## 1. Corpus and store state (replay lead)

- Index 114,562 games (115,542 by the end of the unit; the collector runs on). Post-change: 35,486 games, **23,035 in
  scope** (current top-50 or team 7), all replays on disk. Pre-change: 78,907 / 47,634.
- Store: 44,328 games decoded, of which **3,535 post-change** (Antioch's 2,862 through 1 Oct 15:39Z + 673 team-7 games
  decoded this unit). Queue 20,850 post-change games. Decoding runs in the Cowork VM at ~65 games per 3-minute call
  (1.2–1.8 s/game at 3–4 jobs; the Mac is shared with the hub and GPT's replay pulls), i.e. ~1,300 games/hour of
  continuous calls; the user chose this over a native Mac job. Order: team 7 first (done), then current top-ten sides
  balanced over team × map, newest first (`tools/chongqing/decode.py`). The bulk of 2–3 Oct will take several units.
- **Map pool widened again.** After the switch only the ten ladder maps appeared (CORPUS.md, 1 Oct); since 2 Oct the
  seven others are back (post in-scope: Australia 572, Islands 563, Around UNSW 562, Maze 525, weakhold 454, Stripes 445,
  Tower Defense 417, vs 1,700–2,200 each for the ten ladder maps). Per-map references must list the map.
- **New store columns** (`tools/s1/build.py`, parts written from 3 Oct 23:16Z): per side `q_id`, `q_alive_end`,
  `q_death_round`, `q_death_cls`, `q_death_killer`, `q_moves` (rounds the queen's head moved), `q_maxlen`, `q_end`
  (length in the final snapshot, 0 when dead), `q_header` (the 1.2.3 header field), `q_len@{25,50,100,150,250,400,490}`.
  Older parts read NULL (`union_by_name`); a decode-only backfill for the 2,862 Antioch games is queued. Validation on
  game 996278: `q_end` = header queen both sides. **The queen's id is 0 or 1 but which side gets which varies by map**
  (A has id 0 in 100 of 206 games, id 1 in 106) — do not assume A = 0. Survival, death round and cause need no id
  knowledge: a death row with `id in (0,1)` on a side is that side's queen (§A).
- `build.py games` crashed on the current ladder (`rank: null`); patched to treat unranked teams as outside the ladder order.

## 2. The ladder was reset on 1 Oct (between 06:21Z and 17:09Z)

In the 17:09:22Z snapshot 819 of 963 teams carry `rank: null` and `elo: 1500` (their `wins` counters are intact);
the ranked 144 are the teams that had played since the reset, re-rated from 1500. By 3 Oct 22:36Z 258 teams are
ranked, 716 still null. Consequences:

- **Ranks are post-rules-only.** Today's top ten (team ids): Vibing++ 306 (= Cutlery, renamed between 2 Oct 23:58Z and
  3 Oct 16:15Z) 2298, forgot to mention 264, SSS 91, Sponge 213, WeHaveQuizzes 87, horse 842, free trip to sydney pls 82,
  Cache me outside 952, tungtung67 566, fandagong 552. Gone from the ladder entirely: Stockfish 206, PPP 27 (no row in the
  latest snapshot); cheji bt 70 has not played since (1500, null). 3.14159265 is rank 38, calc 26.
- **The store's `cohort`/`crank` now mean the post-reset ladder** (`teams.parquet` from the latest snapshot). Every
  pre-change "top ten" in Phase 1 and Antioch's/Himeji's references is the 1 Oct 06:21Z cohort; the two overlap in five
  teams (306, 264, 91, 213, 952). I keep both labels explicit: `cohort_pre0621` is a one-line join on
  `public_replays/corpus/ladder/20261001T062107Z.json` when a reader needs the old set.
- "Cutlery fell to rank 97" (Phase 2 summary §1) was the reset, not a cost of its queen play: it was 1385 at 17:09Z
  after a few re-rating games and is rank 1 at 2298 two days later. The queen-keeper leads the post-rules ladder.
- Elo at game time (`elo_a/elo_b`) is stale or 1500 for every game played before a team's first post-reset snapshot;
  use `crank` (current rank) or the pre-reset snapshot for cohort work, not game-time Elo, until the ladder settles.

## 3. The field is adopting the queen — fast, and against us first

RL = round-limit games (`reason <> 'elimination'`); non-pocket excludes Slithery, Autarky, PD, PD10 (queens die r4–5 by
geometry, H-Q3). Queen alive = no death row for `id in (0,1)` on that side.

| day | cohort (post-reset) | RL non-pocket side-games | queen alive at end | RL games decided by the queen | win | share vs us |
|---|---|---:|---:|---:|---:|---:|
| 1 Oct | top10 | 490 | 0.064 | 0.008 | 0.658 | 0.00 |
| 2 Oct | top10 | 114 | **0.351** | **0.342** | 0.842 | **1.00** |
| 1 Oct | r11–30 | 786 | 0.051 | 0.004 | 0.613 | — |
| 2 Oct | r11–30 | 23 | 0.222 | 0.217 | 0.649 | ~1 |
| 1 Oct | us | 125 | 0.011 | 0.072 | 0.327 | — |
| 2 Oct | us | 230 | 0.005 | **0.257** | 0.300 | — |

The 2 Oct top-ten rows are the unranked series teammates requested against hb1-14, so they measure top-ten queen play
*against our bot*, not the ranked field; the ranked 2–3 Oct field is still in the queue. Per team (RL non-pocket):
Vibing++ 11/48 alive on 1 Oct ranked (0.229, already the only keeper); on 2 Oct vs us SSS 16/30 (0.533), Sponge 7/10,
Vibing++ 4/4, WeHaveQuizzes 2/15, horse 2/16, forgot to mention 0/16, tungtung67 1/4. Three of the current top four keep
the queen when it decides the game. H-Q4 ("hunt the enemy queen once the field keeps queens", watch at 0.3) has its
trigger half-fired: among the top four the RL queen survival is already above 10 %.

## 4. Our live bot under the new rules (hb1-14-prior-r540, submission 14265; 673 post-change side-games)

- Win 0.309 overall: **ranked 180 games 0.561** (opp Elo ~1,670, stale) ; unranked 493 games **0.240** (requested
  series vs the top teams, opp Elo ~1,950). The ranked share is what the ladder sees.
- **10.8 % of our games (73/673) end on the queen tiebreak and we lost 71 of them** (ranked 1/18, unranked 1/55). On
  **Schooltime 37.7 %** of our games are queen-decided (lost 36.1 %), on **Trauma 40.4 % / 38.6 %**, Portals 8.8 %,
  Slithery 8.9 %. In 29 % of our ranked RL losses and 26 % of unranked ones the opponent's queen was alive and ours dead.
- In our queen-decided losses we often held the *longest* lead (Schooltime 48 %, Portals 67 %, Slithery 80 %) and rarely
  the total lead (Schooltime 43 %, Trauma 33 %): under the old rules many of these were wins.
- **The r0 queen suicide on Schooltime.** Our queen dies at **round 0 by `self` in 22 of 70 Schooltime games (31 %;
  15/58 as side A, 7/12 as side B)**; the field's rate is 0.3 % (2/676). Replays 996205 (we are A) and 887973 (we are B)
  show the mechanism: Schooltime spawns six length-4 dragons as 2×2 blocks; our queen is the one hugging the map edge
  (head (56,2) for A, (3,2) for B, body a 2×2 square). Every initial dragon splits on round 0; the queen's split produces a
  child (id 6, length 2) that dies `invalid`/`self` in the same round, and the queen itself dies `self` — the bot's
  simulation of split-and-move on the edge-hugging 2×2 spawn disagrees with the engine (the other four 2×2 dragons, away
  from the edge, split cleanly). Every such game forfeits the first tiebreak before it starts. Nothing similar on other
  maps (Default r0: 1/51, newborn ids). This is a bug, not a policy choice — the cheapest queen fix in the programme.
- Queen death anatomy, RL non-pocket, us vs top ten (alive at end / median death round / causes): Schooltime us 0.029 /
  r86 / own 38 % (the r0 suicides) vs top10 0.134 / r108 / h2h-enemy 71 %; Trauma us 0.016 / r137 / wall 56 % vs top10
  0.237 / r106 / wall 36 %, own 41 %; Portals us 0.000 / r46 / wall 64 % vs top10 0.031 / r57 / own 61 %; Default
  us 0.016 vs top10 0.144, both ~82–86 % h2h-enemy, and **36 % of top-ten queens on Default die by r5** (field 22–24 %
  both sides — Default's spawn is half a pocket); Trophy us 0.060 vs 0.223 (h2h-enemy 85–89 %). Across all non-pocket
  maps: us alive 0.057, median death r81, 52 % h2h-enemy, 27 % wall; top10 0.153, r69, 51 % h2h-enemy, 16 % wall,
  22 % self/ally-body.

## 5. Endgame columns, post-change, ranked RL games (provisional; n is the row)

| cohort | pocket | n RL | win | longest@end (median) | total@end | queen alive | losses with total lead ÷ losses | ÷ RL games | queen-decided |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| top10 | no | 231 | 0.658 | 33 | 70 | 0.065 | 0.241 | 0.082 | 0.013 |
| r11–30 | no | 379 | 0.551 | 29 | 67 | 0.040 | 0.324 | 0.145 | 0.000 |
| r31–50 | no | 285 | 0.565 | 26 | 60 | 0.084 | 0.371 | 0.161 | 0.018 |
| us | no | 89 | 0.427 | 27 | 69 | 0.011 | 0.314 | 0.180 | **0.191** |
| top10 | yes | 109 | 0.706 | 55 | 138 | 0.018 | 0.500 | 0.147 | 0.018 |
| us | yes | 32 | 0.563 | 39 | 99 | 0.000 | 0.429 | 0.188 | 0.094 |

These are 1 Oct-heavy (the store's ranked post games are 2,252, mostly 1 Oct). Not stable: Himeji's release rule
(≥ 200 blocks/map, ≥ 50 top-ten sides/map, width ≤ 0.10) is not met on any map for the queen columns. Antioch's
r490 columns (field RL queen alive 0.022, top-ten 0.007, longest 28/42.5, total 70/98) were the pre-reset cohort on the
first eight hours; the top-ten longest 42.5 → 33 here is the cohort change (Stockfish and cheji bt, the converters, are
gone from the top ten), not a field move.

## 6. Hypotheses (ledger rows proposed; weights are my plausibilities)

- **H-C1 (bug, 0.9): hb1-14's round-0 split of the edge-hugging 2×2 queen on Schooltime kills the queen in ~31 % of
  games** (child `invalid`/`self`, parent `self`, same round; replays 996205 side A, 887973 side B). Falsifier:
  a parent/child pair on Schooltime seeds 1–3 where the child's `q_death_round = 0` rate is not < 2 % *or* its Schooltime
  queen-decided loss share does not fall from ~36 % toward the field's ~5 %. Size: Schooltime only, 2 × 48 games is
  enough (31 % → 2 % is a 10-SD effect at n = 48). Suits any tester; also check whether the r0 self-death appears on the
  local panels at all (if the panel's Schooltime fixture does not reproduce it, the live/local map or seed differs — say
  so). Expected spill-over: none; it is one move.
- **H-C2 (0.7): the queen tiebreak is now the largest single loss mechanism for our live bot on Schooltime and Trauma**
  (38–40 % of games), ahead of economy: a queen that merely survives (no feeding) would flip most of them because the
  opponent's queen is alive in only 26–29 % of our RL losses. Falsifier: queen-alive@490 ≥ 0.5 on Schooltime/Trauma
  (carthage-08's gen form reaches 0.33) without the ranked win on those two maps rising ≥ 10 pp. Size: the two maps,
  seeds 1–3, both panels — ~300 pairs. Suits the Claude tester (carthage-10 is built).
- **H-C3 (0.5): Default's spawn is half a pocket — 22–24 % of field queens die by r5 on both sides** (top ten 36 %).
  Our rate is 25 % (13/51, side A). A first-five-moves queen rule keyed on reach (L24's band) should take it to the
  field's best (~5 %). Falsifier: no map-structural feature separates the r5-dead and surviving Default queens (then it
  is contact, not geometry). Size: engine probe + 100 Default games. Suits any tester; the probe is mine next unit.
- **H-C4 (watch, 0.4): queen hunting pays now against the top four** (Vibing++, SSS, Sponge keep queens; ftm does not).
  Trigger (H-Q4): ranked top-ten RL queen survival > 0.10 for a week — measured on the 2–3 Oct ranked bulk next unit.

## 7. Readings

No tester result has landed on the board since the director's 2 Oct sweep. Standing reading for the next results: any
arm scored on Schooltime must separate the r0-suicide games (H-C1) from the rest, or its queen-survival and
loss-with-lead deltas on that map are the bug's, not the mechanism's.

## A. Queries

```sql
-- queen death per side (deaths table; the two queens are ids 0 and 1, one per side)
create view qd as select game, side, min(round) q_death_round, arg_min(cls, round) q_death_cls from deaths where id in (0,1) group by 1,2;
create view qs as select s.*, d.q_death_round qdr, d.q_death_cls qdc, (d.game is null)::int q_alive, (reason<>'elimination') rl,
  map in ('Slithery Fight','Autarky','Prisoners Dilemma','Prisoners Dilemma 10') pocket from sides s left join qd d using (game, side);
-- §3: select started_at::date d, cohort, count(*), avg(case when rl and not pocket then q_alive end), avg(case when rl then (reason='queen')::int end) from qs group by 1,2;
-- §4 r0 suicide: select map, side, count(*), sum((qdr=0)::int) from qs where cohort='us' group by 1,2;
-- §5: select cohort, pocket, count(*), avg(won::int), median("longest@499"), median("total@499"), avg(q_alive),
--   avg(case when won=0 then (total_margin_end>0)::int end), avg((reason='queen')::int) from qs where rl and ranked group by 1,2;
```
Run with `python3 -c "import sys; sys.path.insert(0,'tools/chongqing'); import qq; con = qq.connect(); ..."` from the repo root.
Ladder-reset evidence: `python3` over `public_replays/corpus/ladder/*.json` (count of `rank is None`, `elo == 1500` per snapshot).

Ledger rows touched: L49 (queen) — evidence for: three of the current top four keep queens against us; our live bot
loses 71/73 queen-decided games. H-Q4 trigger half-fired. Proposed: L49 0.5 → 0.6; add H-C1 as a bug row at 0.9.

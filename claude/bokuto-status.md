# bokuto — free lane (Fable instance) status

Started 5 Oct 2026 ~01:00Z. Namespace: `bots/bokuto-*`, `tools/bokuto/`, `build/bokuto/`, branch `r/bokuto`,
worktree `../wt-bokuto` (a `--shared` clone of the main checkout; `git worktree add` cannot run from the Cowork VM
because the registered worktree paths `/Users/...` do not exist there). Nothing committed yet; files are on disk in
the worktree (bots/bokuto-01..06, tools/bokuto/arena.py, tools/bokuto/branches.py, claude/bokuto-status.md).

## Compute (for the lead)

**Since ≈04:10Z the Cowork VM shell fails for me (EACCES on the session folder), so I cannot run games on the Mac,
commit, or write files except through the file bridge (which still works: this file and BOARD.md).** Everything runs
in the cloud container (2 cores, ~150 games/h). Before that:
- the Cowork VM: Linux aarch64, 4 cores, unswbc 1.2.9 in `/tmp/bokuto/venv`; one game 10–60 s; every shell call is
  killed after 180 s, so panels run in resumable slices (`tools/bokuto/arena.py --budget 165`); ~400–600 games/h.
- the cloud container: 2 cores x86, same engine, jobs survive between calls; ~150–200 games/h. The zoo, the live
  bots and `maps/` are copied there. carthage-05's pool panel reproduced there: 226–46.
A job daemon like `tools/asahi/jobd.py` started for this lane in a Mac terminal would make panels 5–10× faster; I am
not blocked without it.

## What the live replays say (team 7, ranked, since 2 Oct; 1055 games)

Per map we win 43–91 % everywhere except **Schooltime 1–77**, **Weakhold 14–54**, **Trauma 21–49**, Dilemma 26–39.
A sample of 232 ranked games off Schooltime: 31 of 115 losses are "by queen" (theirs alive, ours dead), 44 are
"longest dragon" with both queens dead, 39 eliminations. A queen alive at round 500 would have flipped up to 75 of
those 232 games.

1. **Schooltime: the queen is caged.** All six starting dragons sit in closed 2×2 kelp boxes. carthage-05 moves into
   its own neck on round 0 and the queen dies; every opponent splits 2/2, lets the child die (one corpse pearl) and
   circles a length-3 queen in the box for 500 rounds, then wins the tiebreak whatever the material (game 1094553:
   we had 156 total / longest 76 against 144 / 58 and lost "by queen"). The box holds a bed (gap 20–200); when a
   pearl lands in the free cell the queen grows to 4 and must split again, which needs a free unit slot.
2. **Dead-end pockets are the economy on half the maps.** The gap-1 beds (a pearl every round when empty) sit in
   one-exit corridors: Trauma 12.0 of 13.3 pearls/round, Weakhold 22.0/22.6, Dilemma 8.0/8.3, Maze 30/33, UNSW 22/30,
   Autarky 8.7/9.4, Stripes 12.6/15.1, Portals 16.7/25.5 (`tools/bokuto/branches.py`). A dragon cannot turn in a
   corridor: it eats, and at the end splits — the head part (2) dies and drops one pearl, the rest walks out
   backwards. A visit nets (pearls − 2). Top teams run this all game: team 19 on Trauma, 190 splits, 112 with the
   child's head inside a corridor, 67 deaths at the dead ends all at length 2. carthage-05 farms every pocket
   including 1–2-cell ones (net ≤ 0) and sends the queen in; on Weakhold this is a self-feeding loop: 70+ wall
   deaths at the same four cells per game, the queen among them at r29/r44, the team never above 5 units.
3. **Top queens hide at length 2 and are fed at the end**: in 40 games of teams 19/91/213/507 the queen is length 2–3
   for 400 rounds, 10–24 cells from the nearest enemy, then grows to 19–40 in the last 60–100 rounds (feeders die
   into her). Even so their queens die in about half the games (head-ons).

## Versions (all on the carthage-05 chassis; one new header `bokuto.hpp` + `bokuto_branch.hpp`)

| version | change | vs carthage-05 (17 maps × 2 seats × seeds 1–3 unless noted) |
|---|---|---|
| 01-survive | K=7 survival search after `decide` (replaces fatal moves), cage split, unit-slot reserve | 42–41 on 83 games: Schooltime 6–0, Weakhold 4–0, Stripes 4–0; UNSW 0–4, Trophy 1–5, Autarky 1–4. The deep search starves dragons in mazes (false "fatal" verdicts). |
| 02-vac | + time-aware vacancy of other bodies | Trauma 1–5, Weakhold 6–0 (12 games) |
| 03-harvest | + dead-end branch model: pockets entered only when the visit pays ≥ 1, never by the queen; send-back split (a 2-child walks back in when 2 segments remain inside); full trap penalty elsewhere | eats on Trauma 555–731 vs 430 with K=2; still lost on longest |
| 04-queen | + K=2; queen: no pockets, no strikes/hunts/dives, threat ×3, keeps clear of all heads (K=4), crown = queen | **58–44** (0.569): Schooltime 6–0, Weakhold 6–0, Trauma 5–1, UNSW 5–1, Dilemma 5–1, Slithery 5–1; Autarky 0–6, Trophy 1–5, Stripes 1–5. Losses are "longest dragon" with our queen dead: it dies r50–200 by head-on (23/42). |
| 05-hider | + the queen hides from r60: target = far from enemies seen/reported, open, uncrowded; sheds length to 2–3 | queen still dies ~r90–130 on small maps |
| 06-feedqueen | crown election back to carthage's (longest non-queen); the queen broadcasts a beacon from r200; feeders feed the queen first from `feed_from`; queen lv 4 from r380 | pool 30–6 on the first 36 games (two Schooltime games had 14 engine timeouts caused by a concurrent sandbox game thrashing the container; not bot faults) |
| 07-dodge | queen hides from r10; persistent enemy sightings (half-life 150 rounds) + home bias; the queen never ends a step where an enemy head can reach this round or next to any head when a safe step exists, never takes a blind portal landing; strict head-avoidance relaxed when it blocks every move; deliberate head-on strikes exempt from the guard | **60–42 (0.588)**: Schooltime 6–0, Weakhold 6–0, Islands 6–0, Trauma 5–1, UNSW 5–1, Portals/QoS/Autarky 4–2; Stripes 1–5, Tower Defense 1–5, Default/Dilemma/Australia 2–4. Zip 3.58 MiB. |
| 08-yield | + allies never end a turn next to the queen's head when another 3-turn-safe step exists | **65–37 (0.637)**. Schooltime 6–0, Slithery 6–0, Weakhold 6–0, Autarky/Trauma/Australia/Islands/Maze 5–1, QoS/UNSW 4–2, Default/Devil 3–3, Portals/Trophy/Dilemma 2–4, Stripes/Tower Defense 1–5. Our queen alive at the end in 38 % of games (carthage 3 %); 30 of the 65 wins are "by queen". Material parity (total 82 v 80, eats 734 v 719). Losses: 21 eliminations (knife-fight maps), 15 longest. |
| 09-rooms | escape-split rescue counts outside branches; queen trusts known terrain only (K=6), prefers open cells to corridors; queen forages while the team has < 6 units | Stripes seeds 1–2 still lost (economy) |
| 10-letfarm | non-queen guard reduced to: unpaid pockets and certain death only (the swarm plays carthage's farm game) | 59–43 (0.578): Devil/Trauma/UNSW/Schooltime 6–0, Stripes 3–3, Tower 2–4; Australia 1–5, Islands/Weakhold/Autarky weaker. Not better than 08 overall. |

| 11-queen2 | 08 + 09's queen rules + keep 3 cells from enemy heads | abandoned at 12 games (compute) |
| 12-fightqueen | queen fights like any dragon while the team has < 6 units and r < 120 (opening skirmishes decide the knife-fight maps); careful afterwards | folded into 13 |
| 13-cull | 12 + harvest audit fixes: a known corridor worth ≥ 3 pearls is an explicit target within 30 steps for the dragon nearest to it ('H'); remembered pearls never expire; a spare length-2 dragon culls itself at the unit cap while a corridor pays ('K', 1 in 8 per turn) | **70–31–1 (0.686)** — current best. Schooltime/Devil/Weakhold 6–0, QoS/Australia/UNSW 5–1, Slithery/Default/Trauma/Islands/Maze/Stripes 4–2, Dilemma/Autarky/Tower 3–3, Trophy 2–4, Portals 2–3–1. On Trauma our 8-cell corridor is occupied 288 rounds (08: 105–208) and yields 186 pearls (08: 59–132); team eats 859 v 197 in that game. |

Harvest audit (`tools/bokuto/harvest.py`, 08 on Trauma): each side's 8-cell corridor sat full of pearls and empty of dragons
for 290–435 of 500 rounds; the chain broke whenever the exiting dragon could not send a child back and nobody targeted the
corridor again (memory of its pearls expired after 40 rounds; the forward search never reaches it). 13 fixes that.

## Scorecard of the best version, bokuto-13-cull (5 Oct, ~08:00Z)

- pool panel (8-bot zoo × 17 maps × both seats, seed 1): **242–30** (carthage-05 226–46 on the same panel, same
  container). By map: Stripes 4–12, Portals 10–6, Slithery/Trophy/Autarky/Weakhold 14–2, Default/Dilemma/Maze/Tower 15–1,
  the other seven 16–0. By opponent: 29–5 to 33–1.
- vs carthage-05: 70–31–1. vs **asahi-05-kz12-k16 (live): 65–36–1** (Schooltime/Devil/Stripes 6–0, QoS/Australia 5–1,
  Slithery/Default/Trauma/Islands/UNSW/Tower 4–2, Dilemma/Autarky/Maze 3–3, Trophy 2–4, Portals 2–3–1, **Weakhold 0–6**).
  vs kenma-03-pocket-queen: running.
- deploy: zip 3,751,518 B (3.58 MiB); 8 judge-sandbox games (schooltime, unsw, slithery_fight, australia, both seats):
  max 12.9 M points per turn, p99 ≤ 9.6 M, first turns included; 0 timeouts, 0 invalid actions. 0 own faults in 476
  native games. Result files: `build/bokuto/results/` (copied to the Mac through the file bridge).
- ladder screen requested on BOARD (5 Oct ~08:05Z).

Weakhold 0–6 against asahi-05: its pocket farm (carthage + k16) out-eats us 255–30; our dragons target the rich 9-cell
corridor but never reach it — carthage's forward search is capped at 48 cells from round 40 and its waypoint heuristic
oscillates in the maze. Version 17 (building): a terrain atlas of the 17 live maps matched on observed edges (edges seen
always overwrite it, so a server variant corrects itself locally), a move-level pocket ban (the queen walked into a 9-cell
pocket the flood test did not call a trap), and a whole-map BFS route for far targets. First Weakhold games vs asahi-05:
W (eats 260 v 98), W by queen.

Results land in `build/bokuto/results/` on the Mac when the VM shell returns; until then they are only in the container and
summarised here.

Default-map ablations (6 games each) are chaotic: identical bots give mirror-deterministic results decided by seat;
the queen-safety rules alone scored 7–23 over 30 games there, mechanism unknown (the first 40 rounds are identical).

## Next

- finish 06 scorecard; sandbox CPU check (running); zip size.
- queen survival on open maps is the lever: hide better (go to a quiet region early, orbit in a 2×2 ring), and keep
  the swarm from killing her (allies yield).
- harvesting throughput: time the corridor cycles; check the 1–2-cell pockets are now ignored.

# bokuto — free lane (Fable instance) status

## Session 2 (5 Oct 2026, 09:00Z–) — what changed, what was learned

**State.** Shell works again (Cowork VM, engine in `/tmp/bokuto/venv313`, 4 workers, 180 s slices via `tools/bokuto/arena.py
--budget 160`). Everything is committed on `r/bokuto` (`../wt-bokuto`, last commit c04409ee8); the Mac runner (Asahi) takes
jobs by a BOARD line `JOB <bot> : pool, qk2, h2h vs kenma-03, probe`. Delete permission was granted for the session; replays
are kept only while read (`build/bokuto/replays/`), results in `build/bokuto/results/`.

**Ladder.** `bokuto-13-cull` = 17530 played its 60-game trial 30–30, score − E −0.041 (level with 14585, below kenma-03's
+0.074); 17388 became the incumbent (D-081). **`bokuto-18-queenfeed` = 17791 is trial 3, live since 14:19Z** (D-083; the
look at the first series boundary ≥ 60 games, ~17:30Z; end rule: beats the incumbent's statistic by > 0.03 or 17388 is
restored). Asahi's cards for 18: pool 237–35 (+4.04 vs c05, −1.47 vs b13), probe OK (12.4 M points), h2h vs kenma-03
61–41 (b13 64–38, asahi-27 69–33), qk2 30–38; queen wall deaths 9 vs 19 (asahi-27) but head-on deaths 32 vs 20; total
length r300 on the pool 130 (b13 127.5, asahi-27 138.5).

**Diagnosis from 17530's ranked games (tools/bokuto/ladder.py, econ.py, queen_census.py, queen_traj.py, scene.py):**
1. The tiebreak at the round limit is the *longer queen* first. Census of 6,479 ranked games (both sides ≥ 1650): a side
   whose queen is 1–3 long at the limit wins 45 % when the enemy queen is alive, 26+ wins 75 %; teams rated 1650–1850 keep
   the queen in 32 % of limit games. The top teams hide at 2–3 and feed her ally corpses (corpse pearls = ceil(L/2));
   264 and 213 reach 60–120; but the median top-ten queen is still 3 at r400 (Sugawara): the feed is late and fast.
2. On the ladder our queen was alive at r100 67 %, r200 50 %, end 17 % (pool 58 %); early deaths were walls: a blind
   portal dive into a one-cell portal pocket (Portals r77), single-exit cells entered while the team was < 6 units
   (Weakhold r88, Islands r76) under the "queen fights while small" rule, then an escape split that leaves the head part
   stuck. Fixed in 18 (no dive, no rescue reliance, K=4 and the dodge from round 0): Asahi's qk2 shows wall deaths 9 vs 19.
3. **Economy leak: wall deaths.** r100–300 we lose 131 length a game to walls vs 51 for the opponents (24 sampled games,
   851 wall deaths): 41 % corridor walkers that reached the dead end at length ≥ 3 and could not exit-split (121 of 345
   at the unit cap), 14 % boxed in by bodies (mostly at the cap), 12 % the designed 2-head corridor exit, 28 % open-map
   deaths with a free exit (half of those the exit was taken by an ally in the same round). Team 213 has the same harvest
   structure (wall losses 90 a game) but eats 30 more per 200 rounds. Units: ours 24 / 35 at r100 / r300 vs the ladder
   opponents' 16 / 25.
4. **Feeding early makes the queen prey.** Locally 18 (feed from r290) keeps the queen alive at r300 as often as 13 but
   loses her twice as often afterwards: carthage's hunters take dragons ≥ 8 from r200, and she is 10–60 long and in the
   open. 21/22/24 (feed from r350/400) did not restore her survival on 34-game sets, so the loss there is noise-level
   or elsewhere; the Mac must decide.
5. A 34-game set against carthage-05 cannot rank today's versions: 13, 18–24 all scored 17–27 of 34. The only
   consistent local effect was the four-slot reserve: +13 total length at r250 (same seeds).

**Versions this session (all on 18 = 17 with the atlas off):**

| version | change | local 34 vs c05 (noise ±3) | note |
|---|---|---|---|
| 18-queenfeed | feed from r290; queen terrain safety from r0; dodge judges sprints by the landing; fed queen never splits; Kenma reserve (1) | 22–12 | **trial 3 = 17791** |
| 19-queenpick | one ranking for the queen's move: survival ≥ 2, in vision, risk (enemy reach incl. paid steps, heads, portal mouths, exits); final unless nothing survives | 27–7 | queen survival unchanged |
| 20-queenhunt | enemy queen (id ≤ 1) is prey from r40; strike bonus +40 | 24–10 | carthage's queen killed by us 16/34 vs 12 |
| 21-sprintqueen | feed from 350; 2–3-step sprint candidates for a long queen; near-reach margin; proven survival before risk | 17–17 | worse queen early (ranking overrode foraging) → policy path kept when safe |
| 22-latefeed | feed from 400 | 19–15 | |
| 23-reserve4 | reserve 4 slots | 22–12 | total r250 97.6 vs ~84 |
| 24-combo | 18's queen logic + hunt + reserve 4 + feed 400 | 17–17 | |
| **25-reserve4** | 18 + reserve 4 only | — | **JOB posted 15:0xZ** |
| **26-hunt** | 18 + enemy-queen hunt only | — | **JOB posted** |

**Later in session 2 (15:00–16:00Z).** The economy leak has a mechanism: `decide()` preferred the production split (child
2, score 8) to the escape split (−500) at a dead end, so a corridor walker of length L kept L − 2 at the head and died
whole (27 fixes it; Sugawara's count: that class is 27 % of our L3–5 wall deaths, 46 % are 3-longs that cannot split
(entered at 2, found 1 pearl), 20 % whole at the unit cap). Weakhold's six ladder eliminations are this cycle from r12
(our visits: enter at 2–3, eat 2–3, die with 3; 1101's: enter at 3–4, exit the child, 2-head suicides; 38 visits vs 15
by r150). Asahi's card for 27: pool 242–30 (+5.9 vs c05, +1.8 vs 18), total r300 137 vs 130, queen wall deaths 29 vs
41, Weakhold Δecon +70; h2h vs kenma-03 58–44, qk2 26–42 — no win gain over 18 on any panel. Trial 4 = 27 (D-085).
Also found: carthage's 10-map atlas no longer matches live Schooltime, Default, Trophy (edges changed); the 17-map atlas
costs where it makes 400-round-old pearl memories reachable by whole-map routes (my reading); Portals: 73 L3 wall
deaths a game are newborns queuing through one portal to one bed; the parked-queen idea (team 507 circles a 2×2 from
the opening, alive 19/25) is implemented in 31 but locally worse — she grows on block pearls and leaves when enemies
come. 17791's six mid-game queen deaths on the ladder are 2–3-long hunters walking her down over 3–6 rounds and
portal exits onto her → 33's flee term.

| 27-exitsplit | escape split before production split at dead ends | 23–11 | **trial 4 candidate; card above** |
| 28-pocketnet | profit = pearls − 1; corridors of depth ≥ 2 are targets | 20–14 | eats +11 vs 27 |
| 29 | 28 + reserve 4 | 21–13 | total r300 97 |
| 30-atlasbeds | 29 + atlas on, long routes only for corridors/queen | 21–13 | |
| 31-parkqueen | 30 + queen parks in a 2×2 (team 507) | 18–16 | queen 21 %: worse; kept as material |
| 32-strictentry | 30 + 2-longs enter on pearls in sight only; escape split at the cap; newborn atlas | — | |
| **33-flee** | 32 + queen flee term, portal mouths; queen excluded from escape-split-first | 19–15 | **JOB posted 15:5xZ** |

**Next.** (a) Read the Mac cards for 25/26/33 paired against 18 and 27; (b) the trial-3 look (~17:30Z): if 18 fails, the next
candidate is whichever of 25/26 carries on qk2/h2h; (c) the wall-death leak is the largest measured economy term — the
corridor cycle needs a free slot at the exit (reserve) and walkers should not enter with length 2 when a 3-long cannot
split (`profit` already requires len + p ≥ 4; the pearls are often gone by the end); (d) the queen's late feed must be
fast: feeders in a chain next to her path rather than scattered within 4 cells.

---

# bokuto — free lane (Fable instance) status and handoff

Lane started 5 Oct 2026 ~01:00Z; this file written ~09:30Z at handoff. Namespace: `bots/bokuto-*`, `tools/bokuto/`,
`build/bokuto/`, branch `r/bokuto`, worktree `../wt-bokuto` (a `--shared` clone of the main checkout, made from the
Cowork VM because `git worktree add` fails there: the registered worktree paths `/Users/...` do not exist in the VM).

**Nothing is committed.** The VM shell died for every Cowork session at ≈04:10Z (EACCES on the session folder) and never
came back; everything since went through the file bridge. On disk in `../wt-bokuto`: `bots/bokuto-01..17` (01, 02, 04,
06, 07, 08, 13, 17 complete; 03/05/09–12/14–16 only as source diffs described below — the complete bots are in the cloud
container, which dies with this session), `tools/bokuto/{arena,diag,harvest,branches,deploycheck,build_atlas}.py`,
`claude/bokuto-status.md`. Result files are in the main checkout under `build/bokuto/results/`. First job for the next
session with a working shell: `cd ../wt-bokuto && git add bots/bokuto-* tools/bokuto claude/bokuto-status.md && git commit`.

## Best bots and their scorecards

| bot | vs carthage-05 (17 maps × 2 seats × seeds 1–3) | vs asahi-05-kz12-k16 (live) | vs kenma-03 | pool (zoo × 17 × 2, seed 1) |
|---|---|---|---|---|
| **bokuto-13-cull** | **70–31–1** | **65–36–1** (Weakhold 0–6) | **62–39–1** (Schooltime 0–6) | **242–30** (carthage-05: 226–46) |
| bokuto-17-atlas | not run | **66–33** (3 games lost to a rebuild race, not faults; Weakhold 5–1, Trauma 6–0, Maze 5–1, Slithery 6–0; Autarky 1–5, Default 2–4) | not run | not run |
| bokuto-08-yield | 65–37 | | | |

Deploy checks for 13: zip 3,751,518 B (3.58 MiB); 8 judge-sandbox games (schooltime, unsw, slithery_fight, australia,
both seats) max **12.9 M points per turn** (p99 ≤ 9.6 M, first turns included), 0 timeouts, 0 invalid actions; 0 own
faults in 476 native games. 17 adds a 79 KB atlas and one whole-map BFS per far target; its zip is 3.58 MiB too, sandbox
not yet run. **A ladder screen of bokuto-13-cull was requested on BOARD at ~08:05Z**; 17 is the better candidate if its
pool and sandbox checks pass (next session: `tools/bokuto/arena.py pool`, `tools/bokuto/deploycheck.py`).

Queen alive at round 500: 46 % of the games against carthage-05 (carthage's own queen: 1 %); 39 of 13's 70 wins are by
the queen rule. Losses that remain: eliminations on the knife-fight maps (Trophy, Stripes, Tower Defense, Dilemma,
Default, Devil — early skirmish snowballs, decided by round 100) and "longest dragon" when our queen dies (our endgame
conversion is weaker than carthage's: on Schooltime vs kenma our longest 31–37 against 55–70; multiple dragons believe
they are the crown; the crown's growth comes mostly from bed pearls it eats with the exclusion radius, not from feeders).

## What was learned (all from replays; details and numbers in the sections below)

1. **Schooltime: the queen is caged.** All six starting dragons sit in closed 2×2 kelp boxes; carthage-05 moved into its
   own neck on round 0 (queen dead in 77 of 78 ranked games, every one lost). Fix: split 2/2, let the child die, circle
   at length 3; when a bed pearl in the box makes her 4, split again (needs a free unit slot: non-queens keep one).
2. **Dead-end corridors are the economy on half the maps.** Gap-1 beds (a pearl every round when empty) sit in one-exit
   corridors and carry 66–97 % of the pearl income on Trauma, Weakhold, Dilemma, Maze, UNSW, Autarky, Stripes, Portals
   (`tools/bokuto/branches.py`). A dragon cannot turn: it eats, and at the end must split — the head part of 2 dies,
   the rest walks out backwards. A visit nets (pearls − 2); the top teams run this cycle all game (team 19 on Trauma:
   112 of 190 splits send a 2-child back into a corridor). carthage farms every pocket including 1–2-cell ones (net ≤ 0)
   and sends its queen in (Weakhold: 70 wall deaths at four cells per game, the queen at r29/44).
3. **Top queens hide at length 2 and are fed at the end** (teams 19/91/213/507: L2–3 for 400 rounds, 10–24 cells
   from the nearest enemy, then 19–40 in the last 60–100 rounds); even so about half die (head-ons).
4. **Each dragon is its own process**: knowledge dies with it. A branch model learned from observed edges is almost
   useless to a newborn 2-child; the atlas (17) gives every dragon the terrain and bed classes from birth. carthage's
   forward search is capped at 48 cells from round 40 and its waypoint heuristic oscillates in mazes: dragons that
   targeted a corridor 10 cells away never arrived (Weakhold 0–6 vs asahi-05 → 5–1 with a whole-map BFS).
5. **Judging by economy was the programme's trap**: the queen rules and the pocket rules all cost "economy" and win games.
6. **Mirror A/B tests are too noisy at 34 games** (14, 15, 16 each scored 44–47 % against 13 and were dropped; the
   same bots are 50 % by construction up to ±8 games). Use 102-game panels against a fixed reference.

## Versions (all on the carthage-05 chassis; `bokuto.hpp` = guard after `Policy::decide`, `bokuto_branch.hpp` = pockets)

| version | change | result |
|---|---|---|
| 01-survive | K=7 survival search replacing fatal moves; cage split; unit-slot reserve | 42–41 (83 games): Schooltime 6–0, Weakhold 4–0; starves dragons in mazes |
| 02-vac | time-aware vacancy of other bodies | — |
| 03-harvest | dead-end branch model from known terrain; pockets entered only when (pearls − 2) ≥ 1, never by the queen; send-back split (a 2-child walks back in when 2 segments remain inside); full trap penalty elsewhere | Trauma eats 555–731 vs 430 (with K=2) |
| 04-queen | K=2; queen: no pockets/strikes/hunts/dives, threat ×3, keeps clear of heads | 58–44 |
| 05-hider | queen hides from r60 (far from enemies, open, uncrowded), sheds to 2–3 | queen still dies ~r100 on small maps |
| 06-feedqueen | crown election back to carthage's among non-queens; queen beacon (type 1, id ≤ 1) from r200; feeders feed the queen first from feed_from; queen lv 4 from r380 | — |
| 07-dodge | persistent enemy sightings + home bias; hard dodge: never end in an enemy head's reach, next to a head, on a blind portal landing; strikes exempt from the guard | 60–42 |
| 08-yield | allies never end next to the queen's head when another safe step exists | 65–37 |
| 09-rooms | escape-split rescue counted outside branches; queen trusts known terrain only (K=6), prefers open cells; queen forages while the team has < 6 units | Stripes still lost |
| 10-letfarm | non-queen guard reduced to unpaid pockets + certain death | 59–43 |
| 11/12 | keep 3 cells from enemy heads; queen fights like any dragon while units < 6 and r < 120 | folded into 13 |
| **13-cull** | a corridor worth ≥ 3 pearls is an explicit target within 30 steps for the nearest dragon ('H'); remembered pearls never expire; a spare length-2 dragon culls itself at the unit cap while a corridor pays ('K') | **70–31–1**; Trauma corridor occupied 288 rounds, 186 pearls (08: 105–208 rounds, 59–132) |
| 14-fastbeds | learned fast beds; corridor targets to 60 steps; corridors valued by pearls eaten | 15–17 vs 13 (dropped) |
| 15-feedlate | queen forages after r380 | 15–18–1 vs 13 (dropped) |
| 16-feedboth | feeders feed the nearer of queen and crown | 15–19 vs 13 (dropped) |
| **17-atlas** | atlas of the 17 live maps matched on observed edges (observed edges always overwrite it; a changed map stops matching); move-level pocket ban; whole-map BFS route for far targets (`long_route`); no beacon from / no feeding of a caged queen; crown beacons keep their two rays | 66–33 vs asahi-05 |

## Compute notes for the next session

- Cowork VM: 4 cores, every shell call killed at 180 s (`arena.py --budget 165` runs panels in resumable slices), engine in
  `/tmp/bokuto/venv` (uv-installed Python 3.13 + unswbc 1.2.9; `/sessions` was full, `/tmp` had room); dead since 04:10Z.
- Cloud container: 2 cores, ~150 games/h; the zoo, live bots, kenma-03 and `maps/` were copied there; `--sandbox` games
  take 5 GB and must run alone. Never `pkill -f` a pattern that appears in your own command (it kills the shell).
- The engine caches builds in `<bot>/.unswbc-build`; parallel first runs race on it (warm up serially), and editing a bot
  while a panel runs it causes "Permission denied"/"Text file busy" game errors.

## Suggested next steps, in order

1. Commit. Run 17's pool panel and sandbox checks; if ≥ 13's, ask for the ladder screen of 17 instead of 13.
2. Endgame conversion: find why carthage's crown reaches 55–70 on Schooltime while ours reaches 31–37 (crown election
   convergence, late splits 78 vs 65, feeders). Instrument with `LOG CR` as in the session (`/tmp/dbg5`).
3. Knife-fight maps: the first 100 rounds decide; compare the opening against carthage move by move (games are
   deterministic for a given seed and seat).
4. Harvest throughput: corridors still sit idle 150–350 rounds per game (`tools/bokuto/harvest.py`); short walkers
   (length 3 at the exit) cannot send a child back; p=3 corridors need fresh entrants.
5. The queen: 54 % still die, 62 % of those by head-on with a length-2 enemy that was diagonal-adjacent; 12 of 55 deaths
   before round 100 while she fights as a normal dragon (12's rule); newborn enemy children are invisible.

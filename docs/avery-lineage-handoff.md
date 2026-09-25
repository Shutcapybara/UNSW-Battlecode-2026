# Avery lineage — handoff for the next instance

**Date:** 2026-09-25 · **Lineage codename:** Avery · **Goal:** high-performing
Battlecode bot · **Current tip:** `bots/avery-v06-late-feed`
(gauntlet-5: **79–30–1, 72.3%**)

This file is the single entry point for continuing the avery line. Each
version's README carries its own hypothesis, measured W/L/D, death
attribution and run directory; this document adds environment facts, the
cross-version narrative, and what to do next.

## Environment facts (verify before trusting)

- Engine: `~/.local/bin/unswbc` (1.0.0), NOT on default PATH — prefix every
  shell with `export PATH="$HOME/.local/bin:$PATH"`. Run comparisons with
  `uv run tools/compare_bot.py bots/<dir>` from repo root.
- Single game: `unswbc run maps/<m>.map bots/<A> bots/<B> --no-replay --no-indicator`.
- Foreground shell cap is ~300 s; run comparisons detached
  (`(uv run tools/compare_bot.py bots/X > /tmp/x.log 2>&1 &)`) and poll
  `experiment_data/<run>/progress.json`. Resume with `--resume <run-dir>`.
- macOS: no `timeout` command. Bots trace to `/tmp` when
  `/tmp/avery-trace-on` exists (v01–v05 all have this hook; **delete the
  flag file before benchmarking** or traces pollute results).
- The repo is a LIVE shared workspace: other lineages (tew, drake, sinbad,
  ouroboros, kraken…) are being built concurrently by other agents. They
  edit the shared `comparison.toml` (grew from 5 to 11 opponents during the
  avery session) and run CPU-heavy tournaments. Compare avery versions only
  on the gauntlet-5 subset (ouroboros-v10-beacon, hunter-v14-cpp,
  hunter-v20, fry-v14, kraken-v04), and expect wall-clock timeouts under
  contention (600 s game timeouts are environmental when
  `runtime_faults=0`, not bot bugs).
- Commit only avery files + `game_stats/runs/*.parquet`; never `git add`
  other lineages' directories or shared config files.

## Version ladder (all native, both sides, 11 maps)

| Version | Change | gauntlet-5 | Verdict |
|---|---|---|---|
| v01-safe-swarm | From `examples/bahamut-scaffold`: edge map, exact move sim, flood/doom trap checks, split economy, sonar packets | 66–40–1 (62%) | base |
| v02-id-order-corridors | Tunnel followability by act order (ascending IDs); ally-head adjacency ×2 for later-acting allies | 70–39–1 (64%) | promoted |
| v03-swarm-spacing | own_disc 0.3→0.1, ally spread reward, w_crowd 0.3 | 74–35–1 (67.7%) | promoted |
| v04-crown-endgame | Broad crown (200/len≥4) + feeding + crown-kill | 74–35–1, tew −3/bot | **rejected** (documented) |
| v05-strict-crown | v03 + singular late crown (300/len≥8, demote 2), no feeding, crown-kill kept | 75–34–1 (68.6%) | superseded |
| v06-late-feed | v05 + feeding from r410 (die beside crown ≤2, home ≤16, len ≤10) + non-crowns leave pearls at 25%; protocol.py None-command port from drake-v02 | **79–30–1 (72.3%)**, tew-v12 9–13→10–12 | **tip** |

vs ouroboros-v10 (co-champion): 8–11 → 11–11 → 16–6 (v03) / 15–7 (v05) /
16–6 (v06).

**Field fact discovered this cycle:** the "tew" bots on disk are
ouroboros-line code (`tew-v07…v12` contain ouroboros-v13-ladder modules
with per-version `defaults.py`). Identical cross-bot stats in the v05 run
were genuine deterministic games, not a runner bug (reproduced live). Treat
tew as the ouroboros-ladder cluster; verify hashes before trusting a
"tew" number. Other agents keep adding tew versions (v16–v18 seen).

## Hard-won engine/mechanics facts

- Moving into ANY occupied tile kills the mover — including own/ally tail
  that is about to move. Entering a head (either team) kills both.
- Dragons act in ascending ID order each round; split children get higher
  IDs and act the same round. Following a lower-ID dragon through a 1-wide
  corridor is sustainable; following a higher-ID one is suicide.
- Sprint = concatenated direction letters ("NNE"); each extra step costs a
  segment, needs len > 2 per extra step. Illegal splits are FATAL: child
  and parent both need len ≥ 2, and units < limit.
- Split children are born at the parent's tail — often inside corridors.
  v02+ rejects child exits into occupied/doomed tunnels; this fixed the
  worst self-inflicted death class.
- Vision is a wrapping 7×7; edge tokens: `.` open, `w` kelp, integer =
  portal id. Horizontal edge `y*W+x` is cell (x,y)'s NORTH edge; vertical
  `NC+y*W+x` is the WEST edge. Unpaired portals: treated as walls (safe);
  idle dives allowed; trail is rebuilt after a dive teleport.
- Death deposits pearls on alternating corpse segments — feeding works by
  dying into an ally BODY (never the head).
- Round-500 ruling: longest living dragon, then total living length.

## Diagnosis that drove each step (evidence in run dirs)

- v01 death profile: 49% team kills, 15% self-collisions, 0 invalid/wall.
- v02: corridor-following alone didn't cut raw team kills much but flipped
  wins (16-6 vs hunter-v14; ouroboros to 11-11).
- v03 trace finding: deterministic BFS targeting sends equidistant allies
  into the same pocket; growth + traffic seals it → pocket deaths dominate
  both team kills and self-collisions on room maps (schooltime, devil).
- v03 loss profile: 20 of 36 losses at round 500; 19 of 20 on the LONGEST
  tiebreak, 13 by ≤ 6 segments → crown experiments.
- v04 trace: mass volunteering froze the economy at round 200; crowns
  banked to len 40 (r386) and 28 (r477) but none survived to 500.
- v05: economy healthy again, but 18 of 19 r500 losses STILL on longest —
  crown production works, crown survival doesn't.
- v06: the r500 losses were LONG races (our longest 5–17 vs fed enemy
  crowns 27–44), so late strict feeding was added. Result: all 17 flipped
  games are r500 length races, 11 won / 6 narrowly lost, ZERO elimination
  flips; r500 loss share 51% → 30%. Feed-deaths show as
  invalid_action/suicide (676) — deliberate. Big-empty crowns now reach 45.

## Next steps, ranked by expected value

1. **Compact-map crown race (v07).** Remaining r500 losses concentrate on
   stronghold-B (17v48, 10v44), devil-B (17v33), trauma (0–2 margins):
   enemy crowns start banking earlier (~200) and out-feed us on compact
   maps. Ideas: map-size-scaled crown_start (earlier on compact), crown
   farm anchoring near dense beds, feed_start 380, feed_max_len up.
   Measure: r500 longest-margin column in `games.csv`.
2. **hunter-v20 watch.** 14–8 → 12–10 on two narrow r500 losses; if it
   recurs, look at crown-kill timing vs its portal scouts.
3. **Target-claim packets.** team_kills still ~42% of deaths (5891/13992
   in the v06 run); reservation gossip (hydra-v08-style) untried.
4. **Sandbox CPU validation** on big_empty before any deployment claim —
   never done for avery (all evidence is native; v06 run had
   runtime_faults=0 over 132 games).

## Files

- Bots: `bots/avery-v01-safe-swarm` … `bots/avery-v06-late-feed`
  (each: `main.py`, `bot.toml`, README; `protocol.py` untouched except the
  v06 None-command port). Benchmark config: `avery-gauntlet.toml`
  (gauntlet-5 + tew-v12-mid-support).
- Runs: `experiment_data/avery-v0*/` (`games.csv`, `summary_by_bot*.csv`,
  per-map stats/graphs, replays). Aggregates: `game_stats.parquet`,
  contributions in `game_stats/runs/` (committed).
- Task brief copy: `bahamut-experiment-handoff.txt` (repo root).
- Field context: `docs/ACTIVE.md` (cycle-0 gauntlet definition and
  cross-line results — maintained by the cycle unifier, do not edit).

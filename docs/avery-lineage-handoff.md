# Avery lineage — handoff for the next instance

**Date:** 2026-09-25 · **Lineage codename:** Avery · **Goal:** high-performing
Battlecode bot · **Current tip:** `bots/avery-v05-strict-crown`
(gauntlet-5: **75–34–1, 68.6%**)

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
| v05-strict-crown | v03 + singular late crown (300/len≥8, demote 2), no feeding, crown-kill kept | **75–34–1 (68.6%)** | **tip** |

vs ouroboros-v10 (co-champion): 8–11 → 11–11 → 16–6 (v03) / 15–7 (v05).
Weakest matchup: tew line (~40%), undiagnosed.

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

## Next steps, ranked by expected value

1. **Crown survival (v06).** ~18 flippable r500 losses. Ideas: crown
   retreats to a known safe dead-end "farm" after 400 (ouroboros farms in
   doom-checked pockets), escort spacing around the crown, stricter
   late-game risk multiplier, avoid crown fights entirely. Measure: r500
   longest-margin column in `games.csv`.
2. **tew matchup diagnosis (v06/v07).** ~40% vs all six tew bots. Review
   replays of big_empty/arena losses (v02 run had 1904 enemy kills on
   big_empty — open-map hunting vulnerability). tew names suggest
   coordinated hunting ("supported-hunts", "close-support").
3. **Target-claim packets.** team_kills still ~46% of deaths; reservation
   gossip (hydra-v08-style) untried.
4. **Sandbox CPU validation** on big_empty before any deployment claim —
   never done for avery (all evidence is native).

## Files

- Bots: `bots/avery-v01-safe-swarm` … `bots/avery-v05-strict-crown`
  (each: `main.py`, untouched `protocol.py`, `bot.toml`, README).
- Runs: `experiment_data/avery-v0*/` (`games.csv`, `summary_by_bot*.csv`,
  per-map stats/graphs, replays). Aggregates: `game_stats.parquet`,
  contributions in `game_stats/runs/` (committed).
- Task brief copy: `bahamut-experiment-handoff.txt` (repo root).
- Field context: `docs/ACTIVE.md` (cycle-0 gauntlet definition and
  cross-line results — maintained by the cycle unifier, do not edit).

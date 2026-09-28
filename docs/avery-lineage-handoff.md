# Avery lineage — handoff for the next instance

**Date:** 2026-09-25 (cycle 2) · **Lineage codename:** Avery · **Goal:**
high-performing Battlecode bot · **Current tip:** `bots/avery-v08-crown-race`
(gauntlet-6: **100–31–1, 76.1%**; gauntlet-5 only: **89–20–1, 81.4%**)

This file is the single entry point for continuing the avery line. Each
version's README carries its own hypothesis, measured W/L/D, death
attribution and run directory; this document adds environment facts, the
cross-version narrative, and what to do next.

## Environment facts (verify before trusting)

- Engine: `~/.local/bin/unswbc` (1.0.0), NOT on default PATH — prefix every
  shell with `export PATH="$HOME/.local/bin:$PATH"` (compare_bot.py needs it
  too, including detached runs). Run comparisons from repo root with the
  project venv directly: `.venv/bin/python tools/compare_bot.py
  bots/<dir> --config configs/avery/gauntlet.toml` — do NOT use `uv run` (it builds
  a separate dependency env; the brief forbids it). The repo `.venv` has no
  pandas; the system `python` does (use it for games.csv analysis only).
- Single game: `unswbc run maps/<m>.map bots/<A> bots/<B> --no-replay --no-indicator`.
- Foreground shell cap is ~300 s; run comparisons detached
  (`(export PATH=...; .venv/bin/python tools/compare_bot.py bots/X
  --config configs/avery/gauntlet.toml > /tmp/x.log 2>&1 &)`) and poll
  `experiment_data/<run>/progress.json`. Resume with `--resume <run-dir>`.
  Full 6-opponent gauntlet: ~10 min uncontended.
- macOS: no `timeout` command. Bots trace to `/tmp` when
  `/tmp/avery-trace-on` exists (v01–v12 all have this hook; **delete the
  flag file before benchmarking** or traces pollute results — and delete it
  right after tracing too: other agents run avery bots and their traces mix
  into yours). Trace files
  are `/tmp/avery-trace-<TEAM>-<ID>.log`; v06+ logs `FEED-DIE` events,
  v07+ logs `SPLIT-BLOCKED` gate counters every 50 rounds.
- `game_stats/runs/` can vanish mid-run when another agent rebuilds stats
  (v09 run stopped at 119/132 with Errno 2); `mkdir -p game_stats/runs`
  and `--resume <run-dir>` recovers cleanly.
- The repo is a LIVE shared workspace: other lineages (tew, drake, sinbad,
  ouroboros, kraken…) are being built concurrently by other agents. They
  edit the shared `comparison.toml` and run CPU-heavy tournaments. Use the
  committed avery-specific `configs/avery/gauntlet.toml` (gauntlet-5 +
  tew-v12-mid-support), and expect wall-clock timeouts under contention
  (600 s game timeouts are environmental when `runtime_faults=0`, not bot
  bugs). Before comparing against an earlier version's numbers, hash-check
  that the opponents on disk still match that run's frozen sources
  (`manifest.json` → `hashes`); other agents mutate their bots in place.
- Commit only avery files + `game_stats/runs/<your-run-id>.parquet` (the
  run id is in the run's `manifest.json`); never `git add` other lineages'
  directories, shared config files, or the root attachment copies
  (`avery-lineage.txt`, `bahamut-experiment.txt`).
- The cycle-1 text snapshot is preserved in [`handoffs/avery-lineage-handoff.txt`](handoffs/avery-lineage-handoff.txt); this page tracks the current Avery lineage.

## Version ladder (all native, both sides, 11 maps unless noted)

| Version | Change | gauntlet | Verdict |
|---|---|---|---|
| v01-safe-swarm | From `examples/bahamut-scaffold`: edge map, exact move sim, flood/doom trap checks, split economy, sonar packets | 66–40–1 (62%) | base |
| v02-id-order-corridors | Tunnel followability by act order (ascending IDs); ally-head adjacency ×2 for later-acting allies | 70–39–1 (64%) | promoted |
| v03-swarm-spacing | own_disc 0.3→0.1, ally spread reward, w_crowd 0.3 | 74–35–1 (67.7%) | promoted |
| v04-crown-endgame | Broad crown (200/len≥4) + feeding + crown-kill | 74–35–1, tew −3/bot | **rejected** (documented) |
| v05-strict-crown | v03 + singular late crown (300/len≥8, demote 2), no feeding, crown-kill kept | 75–34–1 (68.6%) | superseded |
| v06-late-feed | v05 + feeding from r410 (die beside crown ≤2, home ≤16, len ≤10) + non-crowns leave pearls at 25%; protocol.py None-command port from drake-v02 | 79–30–1 (72.3%), tew-v12 9–13→10–12 | superseded |
| v07-compact-production | Small maps (NC≤600): team_target_small 24→44, split_crowd_max 8→14, split_danger_max 0.3→0.6 | 94–37–1 (71.6% gauntlet-6); arena 3–8–1→**7–4–1**, devil 8–4→10–2 | promoted |
| v08-crown-race | crown_start 300→220, min_len 8→5, feed 410→400 / len 10→20 / range 16→30, demote 2→3 (ouro-v10 envelope under strict singular crown) | **100–31–1 (76.1% gauntlet-6; 81.4% gauntlet-5)**; stronghold 8–4→10–2, big_empty 7–5→9–3, kraken 17–4→20–1 | **tip** |
| v09-frontier-bfs | Idle exploration: best BFS-reachable frontier cell REPLACES zone waypoint | 97–34–1: trauma 5–7→**8–4** but qos/default 12–0→9–3, devil 11–1→9–3 | **rejected** |
| v10-safe-explore | v09 + gates (empty threat map, 10-step cap, zone-heat penalty) | fixture-level: still loses qos both sides | **rejected** (not gauntlet-run) |
| v11-maze-sweep | v08 + sweep only when waypoint BFS-unreachable | 13-map gauntlet 105–50–1; shared-11: 94–37–1: trauma +3 again, devil/qos/schooltime/big_empty −8 | **rejected** |
| v12-hungry-sweep | v11 + starvation gate (no growth for 60/100 rounds) | fixture-level: open maps restored, trauma gain LOST (trickle meals reset hunger) | **rejected** (not gauntlet-run) |

Cycle-2 headline: v06→v08 = 89–42–1 → 100–31–1 gauntlet-6 (+11 net),
driven by compact-map wartime production (v07) and the ouroboros-envelope
crown banking (v08). The v09–v12 exploration line proved the trauma fix
(frontier sweep) exists but no gate tried isolates it from open-map
regressions — see v12 README for the full negative-results summary.

vs ouroboros-v10 (co-champion): 8–11 → 11–11 → 16–6 (v03) / 15–7 (v05) /
16–6 (v06).

**Field fact discovered this cycle:** the "tew" bots on disk are
ouroboros-line code (`tew-v07…v12` contain ouroboros-v13-ladder modules
with per-version `defaults.py`). Identical cross-bot stats in the v05 run
were genuine deterministic games, not a runner bug (reproduced live). Treat
tew as the ouroboros-ladder cluster; verify hashes before trusting a
"tew" number. Other agents keep adding tew versions (v16–v18 seen).
Cycle 2 adds: tew-v13…v18 are crown-banking iterations tested against
avery-v05 (all beat it 4–2/5–1 in small samples — untested vs v08); new
lines appeared (monte_christo, drake-v05+, sinbad on the new maps); maps
autarky + dilemma were added to `maps/` mid-cycle (dilemma is brutal for
most bots; hydra-v07 dominates it).

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

- v06: the r500 losses were LONG races (our longest 5–17 vs fed enemy
  crowns 27–44), so late strict feeding was added. Result: all 17 flipped
  games are r500 length races, 11 won / 6 narrowly lost, ZERO elimination
  flips; r500 loss share 51% → 30%. Feed-deaths show as
  invalid_action/suicide (676) — deliberate. Big-empty crowns now reach 45.
- v07 (cycle 2): v06's worst leak was early ELIMINATION on small maps —
  arena 3–8–1, all losses by r54–104. Arena series showed near-even trade
  attrition but 2–3× production deficit: hunter-v20 splits at every
  len≥4 up to the 64-unit limit (89 splits by r78), tew-v12's ladder splits
  unconditionally; avery's gates (team_target_small=24, crowd 8, danger 0.3)
  stalled production mid-war (33 splits). Relaxing gates on NC≤600 maps
  flipped arena to 7–4–1 and devil to 10–2. REMAINING arena oddity: side A
  still loses 4 of 6 (production collapses: 20–50 splits vs 61–106 in wins);
  side B is 4–1–1. Uninvestigated.
- v08 (cycle 2): crown race — enemy crowns hit 44–61 on stronghold/big_empty
  while ours stalled at 10–17; on trauma no dragon ever reached len 8, so no
  crown ever volunteered. Adopting ouro-v10's envelope (bank from r220 at
  len≥5, feed from r400 with len≤20 corpses homing from 30 tiles) under the
  strict singular-volunteer rule: stronghold 8–4→10–2, big_empty crowns now
  reach 55 (still losing 55v61 to ouro/tew side B).
- v09–v12 (cycle 2, exploration line): trauma's failure is starvation, not
  combat — 37 pearls eaten vs ouro's 426 in a traced 500-round game; all 13
  dragons corner-bound (350/1152 cells). Trauma = kelp maze (564/2304 edges)
  with 12 period-1 + 130 period-200 beds; whoever sweeps farms the map. A
  BFS-reachable frontier-sweep fallback fixes trauma (+3 in both v09 and
  v11) but every gate tried (replace waypoint / safety / distance / heat /
  waypoint-unreachable / individual hunger) either also fires on open maps
  (qos/default/devil/schooltime/big_empty regressions, −3 to −8) or stops
  firing on trauma. Full story in bots/avery-v12-hungry-sweep/README.md.

## Next steps, ranked by expected value

1. **tew-v12 / ouroboros-ladder matchup (12–14 in the v11 run).** The
   strongest opponent and avery's only losing matchup. Their ladder splits
   unconditionally AND banks crowns with the same envelope v08 uses. Look at
   crown-kill timing (avery crown_kill_round=380) vs their crown, and the
   arena/default_small/devil/trauma fixtures they take.
2. **Arena side-A asymmetry.** v07/v08 side A loses ~4 of 6 on arena with a
   production collapse (20–50 splits vs 61–106 when winning); side B wins.
   Check act-order effects (A moves first) and start geometry.
3. **trauma without open-map collateral.** Untried: team-level starvation
   gossip (sonar) instead of per-dragon hunger, or a bed-camping role (park
   beside the period-1/200 beds once found) rather than sweeping.
4. **big_empty crown depth:** 55v61 vs ouro/tew side B — feed even harder
   (feed_max_len >20? earlier feed_start?) or defend the crown zone.
5. **New maps autarky/dilemma** entered `maps/` mid-cycle; v11 went 9–3 /
   2–10 there. dilemma is brutal for most bots (hydra-v07 dominates it);
   v08 has no baseline on them — consider pinning a map list in
   configs/avery/gauntlet.toml for comparability.
6. **Sandbox CPU validation** on big_empty before any deployment claim —
   still never done for avery (all evidence native; v08 run had
   runtime_faults=0 over 132 games).

## Files

- Bots: `bots/avery-v01-safe-swarm` … `bots/avery-v12-hungry-sweep`
  (each: `main.py`, `bot.toml`, README; `protocol.py` untouched except the
  v06 None-command port). Benchmark config: `configs/avery/gauntlet.toml`
  (gauntlet-5 + tew-v12-mid-support). NOTE: `maps/` grew mid-cycle
  (autarky, dilemma) — v07/v08/v09 runs are 11-map, v11's is 13-map;
  compare per-map on the shared set.
- Runs: `experiment_data/avery-v0*/` and `avery-v1*/`. Cycle-2 runs:
  v07 `avery-v07-compact-production_20260925121511670436` (run id
  `58191ac51b6e40e894d1fa08dd47fc4c`), v08
  `avery-v08-crown-race_20260925122644396505` (`7e25450245d94826843d37d5a392dc9d`),
  v09 `avery-v09-frontier-bfs_20260925130508074100`
  (`3b80b6f475904949af3e59e29c82e7f6`), v11
  `avery-v11-maze-sweep_20260925134937530609`
  (`a9abf9c3e6884926b9ddc7f34f4302fc`). Aggregates: `game_stats.parquet`,
  contributions in `game_stats/runs/`.
- Git: v06 landed in commit `4ea743b`; v07–v12 + this update in cycle-2
  commits (see log).
- Task brief snapshot: [`handoffs/bahamut-experiment-handoff.txt`](handoffs/bahamut-experiment-handoff.txt); current shared workflow: [`BAHAMUT_HANDOFF.md`](BAHAMUT_HANDOFF.md).
- Field context: `cycles/cycle-00.md` (cycle-0 gauntlet definition and
  cross-line results — maintained by the cycle unifier, do not edit).

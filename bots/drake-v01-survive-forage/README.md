# drake-v01-survive-forage

**Lineage**: Drake (this file's directory is the first Drake version).
**Parent / base**: `examples/bahamut-scaffold/` (protocol.py copied unchanged).
**Borrowed components**: the engine world-model approach — edge array with
kelp/portal kinds and portal pairing, exact move simulation (tail-timing
collisions, sprint segment costs), flood/doom trap tests, tunnel walk,
threat sprint-reach map, child-exit split checks and the
fire-back-into-own-body handoff trick — is adapted from
`bots/ouroboros-v05-spread` (Aurora/ouroboros lineage), which implements the
published rules. Starting weights are seeded from that bot's published
values. Packet layout, team salts, checksum mixer, hook wiring, target
commitment cache and all decisions about what to keep are Drake's.

## Hypothesis

Exact death avoidance (body/kelp/tail timing, trap and tunnel accounting)
plus a pearl-gradient goal field and measured population growth beats the
mid pool and competes with the top pool **without any hunting role** —
survival plus economy first, aggression later.

## Implemented layers (bahamut scaffold hooks)

- **State**: learned edge map (open/kelp/portal, portal pairing), own body
  trail (self-healing against reported `LENGTH`), remembered pearls, bed
  fertility and spawn-time predictions, visit counts, ally/enemy trackers,
  zone enemy-heat, doom reports.
- **Features**: enemy-head sprint-reach threat map, split-threat tiles,
  forward-BFS goal field (pearls / spawn timing / frontier / unpaired
  portals) with a 6-round target-commitment cache, reverse BFS distances to
  the target, 8×8 zone waypoint scan (stalest low-danger zone).
- **Execution**: single steps and 2–3-step sprints with exact engine
  simulation; SPLIT with child-exit safety checks (doom/tunnel) and a
  sonar handoff fired back through the parent's own body onto the child's
  head; unpaired-portal dives as escape hatches; least-bad fallback.
- **Decision**: one additive evaluation over simulated outcomes: material
  (length ramp to the 500-round tiebreak), expected strike loss, escape
  space (flood), permanent-trap (doom) and tunnel penalties, exit counts,
  ally traffic/crowding, goal progress, anti-dither visits, spread from
  gossip. Trades only when clearly favourable or crown-kill late.
- **Encoding**: `[check 8 | kind 4 | payload 52]` packets, checksum salted
  per team (0x6D/0xB7), kinds SELF/ENEMY/PORTAL/BED/HANDOFF/DOOM with
  bounded fields; two gossip relay slots rotate over the four rays, the
  rest carry the self report.

## Key parameters (P)

See `main.py`. Notables: `team_target` 12/40/60 by map cells, `split_min=4`
(split down to a length-2 parent, like the reference design), `split_stop=380`,
`crown_start=200` (one dragon stops splitting and banks length for the
"longest dragon" tiebreak), threat probabilities 0.75/0.35/0.15,
`bfs_cap=180`, `rbfs_cap=260`, `doom_cap=40`. `params.py` overrides for
sweeps (not shipped with a file yet).

## Deviation from the scaffold contract

Perception writes happen inside `update_state()` (module-level model); the
selected script's memory (goal target, waypoint cache) is queued in
`work["state_updates"]` and committed at turn end as the scaffold intends.
`absorb_turn_scalars()` was added because `decode_messages()` needs the
round number before perception runs.

## Measured results (native, local runner, deterministic)

Default roster (`comparison.toml`): ouroboros-v10-beacon,
hunter-v14-cpp-hybrid-route-spacing, hunter-v20-portal-scouts,
fry-v14-stateful-size-aware-3, kraken-v04-eval; all 11 bundled maps, both
sides. Run: `experiment_data/drake-v01-survive-forage_20260925042507420115`
(110/110 games; four big_empty fixtures initially timed out under CPU
contention with the concurrent 12-worker all-functional tournament and were
redone with `--resume`).

**Total: 43 W - 1 D - 66 L, score 0.395.**

| Opponent | W-D-L |
| --- | --- |
| ouroboros-v10-beacon | 2-0-20 |
| hunter-v14-cpp-hybrid-route-spacing | 11-0-11 |
| hunter-v20-portal-scouts | 10-0-12 |
| fry-v14-stateful-size-aware-3 | 7-0-15 |
| kraken-v04-eval | 13-1-8 |

Map structure (aggregated over opponents):

- Sweeps / winning: default (8-0 vs non-ouroboros), queen_of_spades
  (7-1 vs non-ouroboros, 1-1 vs ouroboros), schooltime 5-1-2,
  stronghold 5-1-4, trauma 4-0-4.
- Losing everywhere: devil 0-10 (kelp-maze map — the one structural hole),
  arena 1-9, default_small 2-8, Colosseum 2-8, trophy 3-7, big_empty 1-5.

Reading: drake wins medium structured maps on economy and survival, and
loses small/crowded maps (population pressure + no answer to aggressive
swarms) and devil (trap-heavy kelp corridors). The fry-v14 deficit and the
devil shutout are the clearest v02 targets.

Spot games during debugging (drake as team A unless noted):

- arena vs fry-v06-one-child: **win** (elimination r156).
- big_empty vs fry-v06-one-child: **loss** (round 500, length). Pearls
  1701 v 1924; drake out-gathers until ~r300, then fry's uninterrupted
  64-cap replacement wins the late economy (drake pop 39 v 64 at r490).
- big_empty vs ouroboros-v10-beacon: **loss** (round 500, length).
- default vs kraken-v04-eval: **win** (round 500, length).

## Debug history (what was wrong and how it showed)

1. Mass deaths ("hit another dragon"/"hit itself") in the first smoke
   tests. Differential games vs the passive scaffold and a raw-stdin probe
   of the wire format isolated three causes:
   - **Pearl blindness (root cause)**: the scaffold's `protocol.py` parses
     tile rows with `map(int, ...)` while the ported code from ouroboros
     compared `t[2] == "1"` (string). Int never equals string, so no pearl
     was ever recorded: the goal field saw only spawn predictions and
     waypoints, and gather rate was 3–4× behind fry (847 v 2395 pearls on
     big_empty at equal population). After the fix: 1701 v 1924 with the
     early/mid gather clearly ahead.
   - **Dive trail corruption**: the unpaired-portal dive appended a
     *guessed* landing cell to the body trail; the guess is wrong whenever
     the portal pairs anywhere non-adjacent, poisoning `trail[-LEN:]` and
     causing later self-hits. Dives now go through `commit_path`, which
     appends nothing for unknown landings and lets the next turn's
     trail-mismatch check heal.
   - **Target thrash**: spawn-timing targets adjacent to a length-2 parent
     flip every round, making it circle a 2×2 pocket. A 6-round target
     commitment cache (or reused while the pearl/spawn evidence persists)
     removed the ping-pong.
2. Population collapse on big maps: split gates were too tight (78 splits
   per 500 rounds vs ouroboros' 59 by round 100). `split_min` 5→4 and
   targets 12/40/60 sustain 60 dragons mid-game like the reference.
3. Tiny-map overcrowding (arena, 9×9 playable): 24-dragon target caused
   churn losses to kamikaze swarmers; target 12 wins the matchup.

## Sandbox / judge checks

- `--sandbox` CPU-metered run vs ouroboros-v10 on big_empty (worst case:
  64×64, 60 units, 500 rounds), drake as team B over 24,232 turns:
  **p50 20.2M, p99 45.5M, mean 22.5M, max 57.3M points per turn** — under
  the 100M/turn judge limit with headroom (ouroboros-v10 measured
  p50 29.4M / max 65.8M in the mirrored run).
- Output is one batched write per turn (2.5M of the 100M/turn budget);
  `gc.disable()`; per-turn compute is capped BFS work comparable to
  ouroboros-v05 (bfs 180 / rbfs 260 / doom 40 cells).
- Not yet checked: 48 MB memory ceiling on the largest map with 64 units
  (no memory faults were reported by the runner in either sandbox game).

## Remaining uncertainties / next experiments

- No hunting role: kamikaze swarm opponents grind drake down on tiny maps;
  a defensive strike margin or a hunter role is the obvious next lever.
- Late-game replacement stops at `split_stop=380`; fry-style opponents win
  the 380–500 economy. Consider map-size-dependent split_stop, or feeding
  deaths' pearls toward the crown (`feed_start` currently 480 ≈ off).
- Echoes (`ECHOES` counts) are parsed but unused — a cheap future signal
  for nearby enemies beyond vision.
- The crown rarely outgrows ~5 on contested maps; consider a real
  pearl-priority protocol (non-crowns yield pearls earlier than r480).

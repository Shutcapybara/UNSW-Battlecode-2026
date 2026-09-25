# tools/ouroboros — the adapt / test / benchmark / improve loop

Claude's harness for the Ouroboros bots (`bots/ouroboros-vNN-*`). Works on
any bot folder. Needs the `unswbc` CLI and `pip install pycapnp` (replay
parsing). Design framework: `docs/ouroboros-design.md`.

## Commands

```sh
# run a candidate (or several) against a pool, both sides, on a map set
python3 tools/ouroboros/ouro.py run ouroboros-v05-spread \
    --pool hunter-v04-team-state-sonar fry-v14-stateful-size-aware-3 \
    --maps quick            # quick | full | wide | widefast | variants | arena,devil,...
    [-j 4] [--sandbox] [--keep all|losses|none] [--out DIR] [--tag TEXT]

# parameter variants without touching the bot: NAME@key=value,key=value
python3 tools/ouroboros/ouro.py run "ouroboros-v05-spread@w_crowd=0.6" \
    "ouroboros-v05-spread@mix_early_small=[1,0,0],gather.risk=0.8" --pool ...

# one-parameter sweep
python3 tools/ouroboros/ouro.py sweep ouroboros-v05-spread \
    --param w_blind_portal=2,4,8 --include-base --pool ... --maps ...

# reading results
python3 tools/ouroboros/ouro.py report  DIR          # W-L by opponent/map, death mix, CPU, every loss
python3 tools/ouroboros/ouro.py compare DIR1 DIR2 .. [--maps a,b]   # same matchups side by side + flips
python3 tools/ouroboros/ouro.py standings DIR        # round-robin table (every row counts for both bots)
python3 tools/ouroboros/ouro.py autopsy DIR [--map M] [--opp NAME]  # unit/length curves of kept losses

# forensics on a single replay
python3 tools/ouroboros/replaystats.py REPLAY --team A   # curves, deaths by cause/phase, trades, splits
python3 tools/ouroboros/deaths.py REPLAY --team A -v     # was each death forced? what was around the head?
python3 tools/ouroboros/replayview.py REPLAY --rounds 20,40   # ASCII frames
python3 tools/ouroboros/mapview.py maps/devil.map        # kelp, portals, beds, spawns
python3 tools/ouroboros/phase.py DIR --from 0 --to 30    # wins vs losses: pearls, splits, deaths in a phase
python3 tools/ouroboros/mapgen.py                        # (re)build transposed / flipped map variants
python3 tools/ouroboros/mapgen.py --holdout              # hold-out variants (_TFX, _FY) in holdout/: never tune on them

# added in cycle 1
python3 tools/ouroboros/equiv.py REF NEW [--maps a,b] [--opp x,y]   # action-stream equivalence (16 cases; replays
                                                         # compared event by event, instruction counts excluded)
python3 tools/ouroboros/econ.py RUN_DIR --opp hunter-v20 --from 20 --to 40
                                                         # production economics per team: pearls per dragon-turn,
                                                         # distance to pearls, hoarding, split latency, deaths by cause
python3 tools/ouroboros/explain.py BOT OUTDIR --rounds 10-40   # traced copy: per-candidate feature breakdown,
                                                         # pearl/target scores (logs in /tmp/ouro-explain)
```

Map sets for the cycle-1 gauntlet: `gv` (the 10 maps/ maps without big_empty,
plus _T/_FX: 30), `gvc` / `gvo` (its compact / open halves), `gvb` (the 10
base maps), `ho` / `hoc` / `hoo` (hold-out _TFX/_FY variants, never tune on
these). Compact = at most 625 tiles.

Map sets: `quick` (6 maps), `full` (the 13 real maps; `small` is excluded,
both sides die in round 1), `variants` (transposed `_T` and x-flipped `_FX`
copies from `mapgen.py`), `wide` = full + variants, `widefast` = wide
without the slow 64x64 maps. The engine seed is fixed, so a matchup on a
map is one exact game; variants give fresh, decorrelated samples of the
same map character and catch changes that only fit one layout.

Runs go to `build/ouro/<timestamp>` (override with `--out`, or set
`OURO_BUILD` to move all of `build/` output, e.g. off a synced folder).
Results are one JSON line per match in `results.jsonl`; runs resume (same
`--out`) and errored matches are retried. Big maps (>2000 cells) run at most
`jobs/2` at a time: two all-python 64-unit teams are 128 processes.

## Parameters

Every Ouroboros decision weight lives in `P` (global) or `RP` (per role) at
the top of `main.py`. A variant writes `params.py` (`PARAMS = {...}`) into a
generated copy under `build/ouro-variants/`; keys `role.key` (e.g.
`hunt.w_enemy`) override one role's slice. `params.py` is plain python so it
survives `unswbc submit` (bundles ship `*.py` only).

## The loop

1. OBSERVE: `report` a benchmark run; `deaths.py` / `autopsy` / `replayview`
   the losses until you can state *one* mechanism.
2. HYPOTHESISE: "our gatherers box each other in inside the stronghold base".
3. ADAPT: a parameter variant if a knob exists; otherwise copy the latest bot
   to a new version folder and add a feature with a weight (default neutral).
4. SCREEN: 3-4 opponents on the maps where the mechanism shows (fast).
5. BENCHMARK: full maps against the bench pool, then `compare` with the
   previous version on the same matchups. Look at the flips, not just totals.
6. PROMOTE: keep it only if the total does not drop and the targeted maps
   improve; check judge CPU with `--sandbox` on a big map (p99 < 60M, max <
   80M). Write the numbers into the version's README.

Pools used so far:

- bench (older, saturated at ~0.82): hydra-v06-echo hunter-v04-team-state-sonar
  hunter-v03-team-growth fry-v12-stateful-size-aware-hunters
  fry-v14-stateful-size-aware-3 kraken-v03-judge-safe fry-v03-portal-hunters
- cross-series (the other AI series' latest): hydra-v10-farmclean
  hydra-v09-lanchester kraken-v04-eval leviathan-v07-local-cache

## Gotchas learnt the hard way

- (fixed in cycle 1) worker copies were named by the first 80 characters of
  the variant label, so long labels sharing a prefix silently ran the same
  bot. Names now carry a hash. Runs with such labels before 2026-09-25 are void.
- The judge deletes `*.py` after compiling them to `*.pyc`: a multi-file bot
  must load `.pyc` when the source is missing (see ouroboros-v12-core/main.py).
- A 90-game screen has σ ≈ 4.6 wins: differences under ~9 are noise.

- Identical bots on identical maps replay identically: a 48-match screen is
  exact for those matchups and says little else. One feature routinely moves
  one map +4 and another -4; judge on the full set.
- Side matters on symmetric small maps (turn order): always play both sides.
- Replays do not carry per-turn CPU in this engine version; the CLI prints
  per-team p50/p99/max for `--sandbox` runs, which `ouro.py` records.

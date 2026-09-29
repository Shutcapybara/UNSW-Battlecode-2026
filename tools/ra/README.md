# tools/ra — Renoir lane (R-2 lane `ra`, Claude Opus) runner

Three commands carry one candidate through the R-2 loop. Any Python >= 3.11 with `unswbc==1.2.2`, pandas, pyarrow
(on the Cowork VM: `/tmp/ra-venv/bin/python`, `TMPDIR=/tmp`).

    python tools/ra/lane.py run   BOT [--panel pool|gen|both] [--seeds 1] [--jobs N] [--shard k/n] [--budget S] [--extract]
    python tools/ra/lane.py cpu   BOT            # sandbox (judge pricing), schooltime/portals/trauma/big_empty vs ares-v06
    python tools/ra/lane.py score BOT --parent PARENT [--json game_stats/runs/ra/BOT.json]
    python tools/ra/variant.py PARENT NEW --set param=value --mechanism "..." --expect "..."   # sweep points

- **pool** = `run_panel.ZOO` (8 bots) x 10 live maps x both seats, seed 1 = 160 games (the z1 panel).
- **gen** = 4 fixed opponents (yuna-v05-core, chaewon-y04-probe, fenrir-v18, ares-v06) x 31 off-pool maps
  (`maps/new/*`, `maps/var/*_tr`, `maps/pub/*_rec`) x both seats = 248 games.
- Economy is scored the BENCHMARKS way: per side-game value / field per-map median
  (`docs/analysis/benchmarks/map_reference_medians.json`), **median** per checkpoint, mean of the four checkpoints
  (`econ~`). This reproduces the Ares V06 finding exactly (1.111, r100 1.102, units 1.200, length 1.035). Hygiene
  rates are side-game **means** per 1k dragon-turns. gen maps have no field reference, so they are normalised by
  renoir-00's own per-map medians (`gen_reference.json`, frozen): 1.0 = the base on that map.
- The gate (`VERDICT`): pool econ~ >= +0.05, units/length@100 medians not down, no hygiene mean up > 10 %, pool win
  rate not down; and gen econ~ and gen win rate not down. HOLD = hygiene down with flat economy.
- Partial runs are scored on the fixtures both bots share (paired). Screening runs seat A first (`--shard 0/2`,
  80 games) and stops a candidate there when it is clearly negative (sequential early stop, fishtest style).
- Several hosts can share a run: each writes `index-<host>.jsonl` and `features-<host>-<ts>/`; `score` concatenates.
- `vm3.sh BOT PANEL JOBS BUDGET SHARD` = one <=170 s chunk on the Cowork VM (its shell kills background jobs).

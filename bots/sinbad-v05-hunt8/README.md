# sinbad-v05-hunt8

- **Lineage:** Sinbad. **Parent:** `sinbad-v04-strike`. Frozen experiment: `build/sinbad/exp/e16`
  (v04 + the strike bonus exposed as a parameter, default unchanged) with `hunt_max_len = 8`
  (variant `e16@hml8`); this directory writes the value into `params.py`.
- **Borrowed:** nothing.
- **Hypothesis:** on big maps our foragers reach the unit cap early and grow past length 5,
  so almost nobody hunts the enemy crown; letting dragons up to length 8 hunt keeps
  the pressure on without changing play where dragons stay short.

## Change

| Parameter | v04 | v05 |
|---|---|---|
| `hunt_max_len` | 5 | 8 |
| `strike_bonus` (new name for the constant 2.0 in the strike value) | — | 2.0 |

## Measured (native, both sides, deterministic fixtures, `tools/sinbad/arena.py`)

| Set | v04 (= e16) | **v05** |
|---|---|---|
| quick + quickT (108; ouroboros-v13, leviathan-v09, hunter-v22) | 84–24 | **84–24** (identical fixture by fixture) |
| big + bigT (16; big_empty, schooltime and transposes vs ouroboros-v13, hunter-v22) | 13–3 | **15–1** |
| open + big maps (24; default, queen, stronghold, trauma, big_empty, schooltime vs v13, hunter-v22) | 22–2 | **24–0** |

Big+bigT per map: big_empty 4–0, schooltime 4–0, big_empty_T 4–0, schooltime_T 3–1.

## Other experiments from this cycle (not adopted; all in `docs/sinbad-experiments.md`)

- Local parameter optimum (quick vs v13+hunter-v22, 36 fixtures, base 28–8): unit 5 23–13,
  γ 0.90 24–12, split_val 2.5 23–13; unit 2, γ 0.96, v_unseen 3/8, split_val 6 within ±1.
- Remembered-pearl / predicted-bed decay (mem_ttl 12, bed_stale 15): 40–41 vs 42 of 54.
- Strike aggression (strike_bonus 0 / 5, atk_margin 2.5): 42–12 each, same as base.
- grow_from 300: 19–5 vs 22–2 on open+big (big_empty 0–4); grow_from 450 with hunt 8: big+bigT 11–5.
- Crowding penalty 0: arena 7–5 vs 3–9, but quick+quickT 77–31 vs 84–24; 0.3: 84–24.
- Bed value discounted by γ^wait, bed blocking over the body length: within noise (quick 54).

## CPU (sandbox)

schooltime vs hunter-v22, full game (24,660 of our turns), `unswbc run --sandbox -v`
(run on the working copy with identical play): p50 23.4M, p90 35.0M, p99 46.7M,
**max 63.7M** points; no "exceeded CPU limit". Only this one sandbox game was run.

## Shared comparison (`tools/compare_bot.py`)

Roster `build/sinbad/sinbad-comparison.toml`: all 11 bundled maps, both sides, native.
Run `experiment_data/sinbad-v05-hunt8_20260925175857393080` (summaries synced; replays
not copied), ledger contribution `game_stats/runs/250b1fd3bd6942eeb49ca94bc064b16a.parquet`.

| Opponent | W–L |
|---|---|
| ouroboros-v13-ladder | 17–5 |
| leviathan-v09-arrival | 18–4 |
| leviathan-x03-estuary-roles | 15–7 |
| tew-v12-mid-support | 16–6 |
| avery-v06-late-feed | 15–7 |
| sinbad-v04-strike | 10–12 (mirror-like: mostly one win per side) |
| sinbad-v01-core | 14–8 |

Per map: stronghold 13–1, big_empty 12–2, trauma 12–2, default 11–3, schooltime 11–3,
queen 10–4, trophy 9–5, Colosseum 7–7, default_small 7–7, devil 7–7, arena 6–8.
Losses concentrate on compact maps: arena (v13, tew-v12, avery 0–2 each), devil (v13,
tew-v12 0–2), default_small (leviathan-v09, leviathan-x03, sinbad-v01 0–2), Colosseum
(avery, sinbad-v01 0–2).

# sinbad-v06-arrival

- **Lineage:** Sinbad. **Parent:** `sinbad-v05-hunt8`. Frozen experiment: `build/sinbad/exp/e19`
  (v05 + an optional priority-ladder mode, off) with `bed_wait = 0.01` (variant `e19@arr`);
  this directory expresses it as `bed_wait = 0` (arrival-only, identical play).
- **Borrowed idea:** leviathan-v09's arrival predicate ("value a bed when it is due by our
  arrival"); our implementation is independent.
- **Hypothesis:** valuing beds that spawn *after* we arrive (linearly decayed over 12 rounds
  of waiting) makes dragons dither between future beds and frontier tiles in the opening
  (traces on default_small: 10–13 rounds circling before the first pearl). Counting a bed
  only if its pearl is there when we arrive removes the dithering.

## Changes (from v05)

| Change | Layer |
|---|---|
| `bed_wait = 0`: a bed with a predicted spawn later than our arrival is worth nothing (it was `v_bed·(1 − wait/12)`) | decision (target value) |
| optional priority ladder (strike → split → nearest owned pearl, with an evaluator floor) behind `ladder_nc`, **off** (tested: no gain) | decision |

## Measured

`tools/sinbad/arena.py` (native, both sides, deterministic fixtures):

| Set | v05 | **v06** |
|---|---|---|
| quick + quickT (108; ouroboros-v13, leviathan-v09, hunter-v22) | 84–24 | **84–24** (fixtures reshuffled: default_T −4, default_small +2, stronghold_T +2, trauma_T +2) |
| big + bigT (16; vs ouroboros-v13, hunter-v22) | 15–1 | **15–1** |
| default_small(+T), Colosseum(+T) vs leviathan-v09, leviathan-x03, avery-v06, sinbad-v01 (32) | 13–19 | **25–7** |

Linear waiting with 4 rounds instead of 12 (`bw4`): 79–29 / 15–1 / 24–8 — worse on the main pool.

`tools/compare_bot.py`, roster `build/sinbad/sinbad-comparison.toml` (11 maps, both sides),
run `experiment_data/sinbad-v06-arrival_20260925201048098030`, ledger contribution
`game_stats/runs/70787b9b5b5d40e591cba35b842ec748.parquet`:

| Opponent | v05 run | **v06 run** |
|---|---|---|
| ouroboros-v13-ladder | 17–5 | 15–7 |
| leviathan-v09-arrival | 18–4 | 19–3 |
| leviathan-x03-estuary-roles | 15–7 | 16–6 |
| tew-v12-mid-support | 16–6 | 16–6 |
| avery-v06-late-feed | 15–7 | 16–6 |
| sinbad-v01-core | 14–8 | 17–5 |
| previous Sinbad | v04: 10–12 | **v05: 15–7** |
| **five external opponents + v01** | 95–37 | **99–33** |

v06 per map: Colosseum 13–1 (v05 7–7), big_empty 14–0, trauma 13–1, default 11–3,
default_small 10–4 (v05 7–7), queen 10–4, schooltime 10–4, stronghold 10–4, trophy 10–4,
arena 8–6 (v05 6–8), **devil 5–9** (v05 7–7; 0–2 vs ouroboros-v13 and tew-v12).

Default `tools/compare_bot.py` configuration (no `--config`; ouroboros-v10-beacon,
hunter-v14, hunter-v20, fry-v14, kraken-v04; 11 maps, both sides): **92–1–17**, run
`experiment_data/sinbad-v06-arrival_20260925205932158226`, ledger contribution
`game_stats/runs/0d70be4b223543c5844470e75506b9a6.parquet`
(ouroboros-v10 19–3, hunter-v14 16–6, hunter-v20 17–5, fry-v14 20–2, kraken-v04 20–1–1).

Later measurements (device, same arena harness): quick+quickT+big+bigT vs ouroboros-v13,
leviathan-v09, hunter-v22 = 107–25 (default_T 1–5); quick vs athos-x13, aramis-v02,
monte_christo-v06, monte_christo-x12 = 42–30 (monte_christo-x12 8–10, default 2–6).

## Remaining weaknesses

- devil: the ladder family out-produces us in the 2-wide lanes by churning — ouroboros-v13
  dies ~300 times by round 300 and eats 728 pearls from its own corpses (we: 73 deaths,
  66 corpse pearls). Device screen, devil + devil_T vs v13 and tew-v12 (8 fixtures):
  base 2–6, w_trap 5 3–5, w_crowd 0.3 2–6, w_threat 0.5 2–6.
- arena vs ouroboros-v13 and tew-v12 (0–2 each).

## CPU (sandbox)

stronghold vs hunter-v22, full game, `unswbc run --sandbox -v` (15,403 of our turns):
p50 28.7M, p90 36.8M, p99 47.5M, **max 58.5M** points; no "exceeded CPU limit".
v05 on schooltime: max 63.7M. Only these single sandbox games were run.

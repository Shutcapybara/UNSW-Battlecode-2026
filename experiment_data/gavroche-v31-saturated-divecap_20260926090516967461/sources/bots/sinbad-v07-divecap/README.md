# sinbad-v07-divecap

- **Lineage:** Sinbad. **Parent:** `sinbad-v06-arrival`. Frozen experiment: `build/sinbad/exp/e20`
  (v06 + a bed-period estimate, feature off) with `v_dive = 3` (variant `e20@vd3`); this
  directory writes the value into `params.py`.
- **Borrowed:** nothing.
- **Hypothesis:** exploratory dives into portals whose other end we have not seen are a
  large, hidden loss on portal maps: the landing tile is often next to our own dragons
  (who are exploring the same portal from the other side), and a diver that dies never
  learns the pairing, so the same portal keeps killing. Halving the dive incentive keeps
  some exploration but removes most of the fatal dives.

## Diagnosis that led here (measured)

`tools/sinbad/deaths.py` + traces of v06, default, side B vs monte_christo-x12:
14 friendly head-on deaths initiated by us; 13 of them were dives (chosen score 2.4–2.5 =
`dive_base − p_dive·V + v_dive/2`, target = own head). In that game our dragons dived 116
times; 43 dives were the dragon's last action. Portal 0 at (24, 8) killed a diver at
rounds 29, 223 and 263. Friendly head-ons per game, v06, 36 quick fixtures: default 11,
queen 8, trophy 8, trauma 5, stronghold 4, Colosseum 3.

## Changes (from v06)

| Change | Layer |
|---|---|
| `v_dive` 7 → 3 (value of an unpaired portal as a target; the dive move bonus is half of it) | decision |
| `world.bper` (largest countdown seen per bed) and `fast_per`/`fast_mult` (fast beds keep their value out of view) — **off** (`fast_per = 0`, tested: noise) | state / decision |

## Measured (native, both sides, deterministic fixtures, `tools/sinbad/arena.py`)

| Set | v06 | v_dive 0 | **v_dive 3 (= v07)** | v_dive 3 + p_dive 0.4 |
|---|---|---|---|---|
| 7 portal maps + transposes vs ouroboros-v13, monte_christo-x12 (56) | 36–20 | 38–18 | **45–11** | 40–16 |
| quick + quickT vs ouroboros-v13, leviathan-v09, hunter-v22 (108) | 84–24 | 76–32 | **88–20** | — |
| big + bigT vs the same three (24) | 23–1 | 23–1 | **23–1** | — |
| quick vs athos-x13, aramis-v02, monte_christo-v06, monte_christo-x12 (72) | 42–30 | — | **47–25** | — |

v_dive 0 was also 29–7 on a 36-fixture portal screen (v06 23–13) but lost on trophy_T,
trauma_T and schooltime: some exploration by diving is still worth it.
v07 quick+quickT by opponent: ouroboros-v13 27–9, leviathan-v09 29–7, hunter-v22 32–4;
friendly head-ons per game (whole set) 3.9 (v06 with big maps: 6.8).
New-pool screen by opponent: athos-x13 13–5, aramis-v02 13–5, monte_christo-v06 12–6,
monte_christo-x12 9–9 (v06: 12–6, 12–6, 10–8, 8–10).

Runs: device cache (`~/sbwork/cache.jsonl`, merged into `build/sinbad/cache.jsonl`) and
cloud logs `build/sinbad/vd3_quick.log`, `vd3_big.log`, `vd3_newpool.log`.

## Shared comparison (`tools/compare_bot.py`)

Roster `build/sinbad/sinbad-comparison-v07.toml` (all 11 bundled maps, both sides, native),
run `experiment_data/sinbad-v07-divecap_20260925232803754803`, ledger contribution
`game_stats/runs/c3df18b49672457985f63448c7bf7c9b.parquet`. **150–0–48**.

| Opponent | v06 run | **v07** |
|---|---|---|
| ouroboros-v13-ladder | 15–7 | **17–5** |
| leviathan-v09-arrival | 19–3 | **20–2** |
| leviathan-x03-estuary-roles | 16–6 | **17–5** |
| tew-v12-mid-support | 16–6 | **17–5** |
| avery-v06-late-feed | 16–6 | 16–6 |
| sinbad-v01-core | 17–5 | **20–2** |
| five external + v01 | 99–33 | **107–25** |
| monte_christo-x12-remote-density | — | 12–10 |
| athos-x13-c-all-menu | — | 17–5 |
| previous Sinbad (v06) | v05: 15–7 | 14–8 |

Per map: default 17–1, schooltime 17–1, big_empty 16–2, queen 16–2, stronghold 15–3,
Colosseum 14–4, trauma 14–4, default_small 13–5, trophy 12–6, arena 10–8, **devil 6–12**.

## Tested after promotion (not adopted)

Device screens, e21 = v07 + `dive_units` (unpaired portals are targets only while we
have fewer units) and v07 parameter variants:

| Variant | Set | Result (v07 on the same fixtures) |
|---|---|---|
| dive_units 8 / 16 | 6 portal maps + T vs v13, monte-x12 (48) | 35–13 / 32–16 (37–11) |
| hunt_from 999 (no hunting) / attack 0 | default, trophy, trauma, stronghold, queen, 3 T vs monte-x12, v13 (32) | 21–11 / 21–11 (24–8) |
| w_crowd 1.2 / 2.0, head_block 1 | quick + quickT vs v13, monte-x12 (72) | 45–27 / 48–24 / 45–27 (49–23) |

## CPU (sandbox)

stronghold vs hunter-v22, full game, `unswbc run --sandbox -v` (12,164 of our turns):
p50 28.9M, p99 47.6M, **max 66.7M** points; no "exceeded CPU limit". One game only.

## Remaining weaknesses

- devil (3–5 vs the new pool): the opponent's swarm takes the four central fast-bed
  columns by round 50 (v13 ate 816 bed pearls there in one game, we 109) and our dragons
  stay on our half (`tools/sinbad/eatmap.py`).
- arena: decided by round 20–30 (opponent 9–14 units vs our 4–6).
- side B is weaker than side A against monte_christo-x12 on open maps (v06: 3–6 vs 5–4).

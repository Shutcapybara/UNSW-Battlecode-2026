# Hidden bed layouts rebuilt (D-072 §E) — kageyama, 5 Oct 2026

## 1. How the engine draws bed countdowns (measured)

- All bed countdowns come from one **mt19937_64** stream seeded with the game seed (the hex `seed` of `index.jsonl`).
- A draw for a bed `TILE x y lo hi` is `lo + (u mod (hi − lo + 1))`.
- At round −1 the symmetric pairs draw in row-major order of their first cell; both cells share the draw. Each round,
  the pairs whose countdown expires redraw in the same order. A pearl appears at an expiry when the cell is empty.
- The schedule does not depend on play.
- Evidence: the raw draws were rebuilt by CRT from 16 probe moduli (64-bit values) and equal `std::mt19937_64(seed)`
  output from the first draw. The pure-Python emulator `tools/learn/beds/emu.py` equals the engine's countdown events
  on every cell of 11 maps × 2 seeds × 500 rounds (`verify_emu.py`, run natively on the Mac VM: 0 differing cells).

So a candidate bed list is checked against a server game in milliseconds, without reproducing its play.

## 2. The variants

The server runs two bed lists behind the same visible map for Devil, Queen of Spades and Slithery Fight, chosen per
game (interleaved through the era, about half each). Schooltime open-4 and Dilemma 10-dragon are visibly different
maps (own map hashes) with their own lists. The templates in `maps/live/` are the other half.

| variant (map) | bed list | file |
|---|---|---|
| Devil B | 38 pairs. The x = 9/10 columns are all (1,300), the four 2×2 blocks are (1,150), there is a new (1,1) pair at (15,1)/(16,1), and the template's (1,600) columns and (1,30) centre column are absent. | `maps/live_var/devil_b.map` |
| Queen of Spades B | 182 pairs (fewer than the template's 221): (1,1000) 308 cells, (1,500) 30 cells, (1,50) 26 cells. | `maps/live_var/queen_of_spades_b.map` |
| Slithery Fight B | 174 pairs: the (1,5) and (1,10) rows as in the template (56 and 32 cells); a scattered (100,300) layout over the whole board (206 cells); 13 template (1,2559) pairs (26 cells); 26 (1,1) cells, including (32,5)/(30,21), which never show a non-drop pearl but hold a stream index; one (1,20) pair. | `maps/live_var/slithery_fight_b.map` |
| Schooltime open-4 | 89 pairs: (20,200) 158 cells, (20,50) 18 cells, (20,80) 2 cells. | `maps/live_var/schooltime_open4.map` |
| Dilemma 10-dragon | Centre column x = 15/16, rows 2–13, is (1,100); 44 (150,250) cells; 8 (1,1) cells. The template's (480,490) column is absent. | `maps/live_var/dilemma_10.map` |

- Each file is the server's visible map (template seats where a server text with those seats exists) plus the fitted
  TILE lines. `MAP_NAME` carries a suffix (`Devil B`, …).
- The `*.beds.json` files hold the same lists as data.

## 3. Acceptance (≥ 95 % of the variant's games reproduced, turn for turn)

- **Population:** post-m2 completed games on these five maps (started at or after 2 Oct 03:49Z), up to game 1113536.
  That is 14,240 games, ranked and unranked.
- **Emulator check (every game):** every game is explained by exactly one of {template, variant}. The exceptions:
  - 233 short games are explained by both lists (232 on Slithery, 1 on Devil);
  - 0 games are explained by neither list.
- **Engine oracle (sample):** the official engine re-run with the variant's TILE lines, the server seed and the
  replay's actions, on two sets:
  - the teachers_v1 games that failed before (tv1);
  - 100 random variant games per variant outside tv1 (seed 7).
- A game passes when 0 dragon-turn blocks differ and the engine plays no extra turn.
- Interval: one-sided 95 % Clopper–Pearson lower bound on the pass rate.

| variant | games (ranked) | share of ranked post-m2 games (31,793) | oracle tv1 | oracle random | pooled pass, 95 % lower bound |
|---|---|---|---|---|---|
| devil_b | 1,286 (903) | 2.84 % | 57 / 57 | 100 / 100 | 157 / 157, ≥ 98.1 % |
| queen_of_spades_b | 1,343 (933) | 2.93 % | 68 / 68 | 100 / 100 | 168 / 168, ≥ 98.2 % |
| slithery_fight_b | 1,463 (932), plus 232 ambiguous (126 ranked) | 2.93 % (3.33 % with the ambiguous games) | 73 / 73 | 100 / 100 | 173 / 173, ≥ 98.3 % |
| schooltime_open4 | 1,573 (962) | 3.03 % | 62 / 62 | 100 / 100 | 162 / 162, ≥ 98.2 % |
| dilemma_10 | 1,205 (868) | 2.73 % | 68 / 68 | 100 / 100 | 168 / 168, ≥ 98.2 % |
| **all five** | **6,870 (4,598)** | **14.46 %** | 328 / 328 | 500 / 500 | 828 / 828 |

**All five are accepted.** Turns compared: 15.7 M dragon-turn blocks in the 828 games.

The per-game labels are in `docs/learning/datasets/kageyama-bed-variants-v1.json`:

- values: `template`, `devil_b`, `queen_of_spades_b`, `slithery_fight_b`, `schooltime_open4`, `dilemma_10`,
  `ambiguous`;
- sha256 of the game map: 9295f1f87f0f….

## 4. Uses

- **Asahi:** the five maps can join the pool. They cover the roughly 14.5 % of ranked games that the panels miss today.
- **Teacher rows:** rows built as `rebuild_redacted` can be rebuilt as oracle rows (exact countdowns) by taking the
  game's label from the dataset file. For an `ambiguous` game, try the template first.
- **Bots:** none of this is a bot input. Map identity stays excluded; the countdowns a dragon sees are already in
  its block.

## 5. RL translation (D-044)

- **Observation:** no new input. The block's pearl countdown field is now exact in training rows for all these maps
  (it was redacted, `x_cd_known = 0`).
- **Action:** none.
- **Value/reward:** the value targets and panels on these maps now follow the server's bed timing, so economy
  terms (pearls per round) on them are unbiased.
- **Demonstration:** top-team games on these variants (about 14.5 % of ranked games) become full oracle
  demonstrations.

## 6. Tools

All are in `tools/learn/beds/`; see its README.

- `ev_extract.py`, `ev_drop.py`: pearl events and death-drop flags. Pure Python; run on the Mac VM.
- `emu.py`, `gens.py`: the emulator.
- `fit.py`: rank-aligned range fit; hidden pairs show as index breaks.
- `classify.py`: per-game labels.
- `mkmaps.py`: writes the map files.
- `var_oracle.py`, `orun.sh`: oracle acceptance. They need the `unswbc` engine module. On the Mac VM, the aarch64
  wasmtime wheel and the engine files are unpacked into `~/pyk`.
- `verify_emu.py`: checks the emulator against the engine.

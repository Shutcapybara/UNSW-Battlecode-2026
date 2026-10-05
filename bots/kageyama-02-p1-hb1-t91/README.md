# kageyama-02-p1-hb1-t91 — the HB-1-vector slot with team 91's single-team prior (D-068 §C.5, D-072 §D)

This is `kageyama-02-p1-hb1` with exactly one file replaced: `p1_model.hpp`. The switch, the slot code and λ are
unchanged (`KAGEYAMA_P1_SLOT 1`, `KAGEYAMA_P1_MIRROR_AVG 0`, λ = `Params::hb1_dir_lambda` = 1.0). A λ arm is one
constant on top of this bot.

- **Model:** Hinata's A1 recipe on team 91's rows only. Source:
  `build/learn/hinata/r2full/A1-team91/model_all_400.txt` (sha256 df5410f4a6b36561…); 400 rounds, refit on
  all of the team's rows (222,647 F/R/L rows, 40 series, out-of-fold 0.7133, Hinata 05:03Z).
- **Export:**
  `python tools/learn/export_gbt.py lgb model_all_400.txt p1_model.hpp --ns p1 --features hb_feats.txt`, where
  `hb_feats.txt` lists the 270 `hb_f_*` columns in teachers_v1 shard order. That is the model's column order
  (`Column_0..269`), and it equals the placeholder's `FEAT_NAMES`.
  - Size: 1600 trees, 187,318 nodes; header 3,659,855 bytes, 1,030,933 zipped.

Evidence (5 Oct 2026, cloud container, unswbc 1.2.9):

- **Python against C++** (`gbt_parity.py`): 7,125 teachers_v1 oracle move rows (3 shards, train split), max |Δp| 3.2e-08,
  argmax 100 %.
- **In-bot, end to end** (`slot_e2e_parity.py`, debug-writer copy, self-play seed 3):
  - Maps: Portals and Australia (point symmetry), Devil and Schooltime (reflection); both seats in each game.
  - Turns: 114,741 of 114,741 compared, 0 missing; max |Δp| 3.7e-08, 0 turns over 1e-6, argmax 114,741 / 114,741.
  - Columns never non-zero: 4 of 270, the same structural four as the placeholder (`g_0_0_pearl`, `cB_allyh2`,
    `cB_eseg2`, `cB_run`).
- **Sandbox points** (UNSW, seed 1, against carthage-05, this bot in seat B): p50 7.2 M, max 10.9 M (first turn
  included). 0 TLE, 0 invalid-command deaths.
- **Zip** (all files, deflate): 1,090,560 bytes (1.040 MiB).

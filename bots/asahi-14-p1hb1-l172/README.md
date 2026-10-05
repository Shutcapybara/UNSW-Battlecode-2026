# asahi-14-p1hb1-l172 — kageyama-02-p1-hb1 (bcd93db88, A1-400 placeholder) with ONE change: Params::hb1_dir_lambda 1.0 → 1.72 (A1-400's entropy-matched λ, Hinata 05:46Z, computed before any game; D-076 §D orders this arm; Asahi)

---

# kageyama-02-p1-hb1 — the deploy slot with HB-1's feature vector as input (D-066 §E)

Parent: `carthage-05-free-sprint`. It has the same one switch as `kageyama-01-p1-slot` (`KAGEYAMA_P1_SLOT`,
`p1_switch.hpp`). The input is chosen by the model header: `p1::INPUT` 0 is encoder v1, 1 is HB-1's feature
vector. With input 1, the prior is a tree model over carthage-05's own HB-1 row (`hb1::Proc::features`), read by
the names in `p1::FEAT_NAMES`, exactly as `Bound::vec` builds the parent's input. The slot rule is D-055 §E:
F/R/L renormalised, reverse keeps 0, λ = `Params::hb1_dir_lambda` (1.0).

- **Model now: PLACEHOLDER** — A1-400, Hinata's fold-f0 model of `build/hinata/r2/battery/A1-u` truncated at
  400 iterations. Its fold-f0 predictions equal `p_A1-400.npy` to 3e-8 on 45,484 rows; it is not selected. Export:
  `python tools/learn/export_gbt.py lgb A1-400-f0.txt p1_model.hpp --ns p1 --features A1_features.txt`, with the 270
  `hb_f_*` names in the model's column order, which is the order of `hb1_dev120` / `teachers_v1` and of carthage-05's
  `dirc_feats`.
- **A8b switch:** `KAGEYAMA_P1_MIRROR_AVG 1` averages P on the row and on its left–right mirror image, mapped back
  R↔L. The mirror tables are emitted by export_gbt and equal `tools/hinata/r2_mirror.py` on 8,000 rows × 1,463
  columns. It costs two model evaluations a turn.
- **The slot code works for either input.** The same `p1_slot.hpp` / `main.cpp` take an encoder-input model, so the
  selected arm, A1 or A3, goes in by replacing `p1_model.hpp`.

Evidence (2026-10-05, placeholder A1-400 f0):

- Python against C++, 20,000 dev120 oracle move rows (`gbt_parity.py`): max |Δp| 3.3e-8, argmax 100 %.
- In-bot end to end (`slot_e2e_parity.py`): Portals and Australia (point symmetry) and Schooltime and Devil
  (reflection), both seats, seed 3, native builds.
  - One evaluation: 96,082 / 96,082 turns, max |Δp| 3.1e-8.
  - With A8b on: 117,187 / 117,187 turns, max |Δp| 2.4e-8.
  - Columns never non-zero over those games: 4 of 270, all structural (`g_0_0_pearl` is the head's own cell;
    `cB_allyh2`, `cB_eseg2`, `cB_run` are the reverse candidate, which is the own body).
- Zip: 1.098 MiB.
- Sandbox points, UNSW seed 1, seat B (carthage-05 in seat A at 7.2 M p50, 10.7–10.8 M max):

  | Variant | p50 | Max |
  |---|---|---|
  | One evaluation | 7.3 M | 10.8 M |
  | A8b | 8.0 M | 11.8 M |

  No runtime errors.

# kageyama-01b-p1-slot-fb — kageyama-01-p1-slot plus the fallback log (D-068 §C.1)

This is `kageyama-01-p1-slot` with one engineering change and no change to play. When the slot's prior cannot be computed (an
exception in `slot.observe`, which leaves that turn with no prior at all), the turn prints `LOG p1_fallback` after
its action. Count the line per map. Checks:

- Same play as the parent: Devil seed 3, replay turns identical to the parent's on both paths (encoder 4,945 /
  4,945, HB-1 7,227 / 7,227).
- Counted locally, native builds, seed 1, both seats, against carthage-05, on the 19 live non-held-out maps
  (Devil and Dilemma first): 38 games per path, **0 `p1_fallback` lines** on either path (2026-10-05).

---

# kageyama-01-p1-slot — the deploy slot for the cloned direction prior (D-065 §D)

Parent: `carthage-05-free-sprint` (live, submission 14585). **One switch** (`p1_switch.hpp`, `KAGEYAMA_P1_SLOT`):
the first-step direction prior is computed from a tree model over encoder v1 (`p1_model.hpp`, evaluated by
`gbt_compact.hpp`) instead of HB-1's direction GBT. Everything else is carthage-05.

- **Slot rule (D-055 §E):** P(F), P(R), P(L) renormalised over those three; the score term is
  `lambda * log(max(q, 1e-4))` on the absolute direction of F, R, L. Reverse keeps the parent's value (0), and
  lambda = `Params::hb1_dir_lambda`, as in the parent: 1.0 here, 0.5 in `kageyama-01-p1-slot-l05`, which is
  otherwise identical.
- **Observation:** `learn_encode.hpp`, the C++ twin of `tools/learn/encode.py`, on this process's own blocks through
  the official helper (`learn_helper.hpp`). Each turn the process's own action is fed back to it (move / split /
  invalid), as in the training rows.
- **Model now: PLACEHOLDER.** It is Hinata's development arm A3-400, fold f0 (`build/hinata/r2/placeholder/`,
  sha256 2dfb0705…). It is not selected or confirmed. It is exported by `tools/learn/export_gbt.py`: 1,600 trees,
  200,000 nodes, float32 leaves; the header is 3.77 MB and zips to 1.05 MB. Replace `p1_model.hpp` with the selected
  model's export; the bot checks at compile time that the model takes `learn::N_X` inputs and has 4 classes.
- **Switch off:** set `KAGEYAMA_P1_SLOT 0` and copy in carthage-05's `hb1_compact.hpp` and
  `hb1_direction_compact.hpp`. This reproduces carthage-05 turn for turn (golden parity).

Evidence (2026-10-05):

- Python-against-C++ prediction parity on 40,000 dev120 oracle move rows: max |Δp| 2.9e-8, argmax 100 %.
- In-bot end-to-end, the bot's own probabilities against the Python encoder plus LightGBM on the replay: 11,187 /
  11,187 turns, max |Δp| 2.6e-8.
- Golden parity with the switch off: 44,613 / 44,613 turns equal to carthage-05.
- Zip: 1.053 MiB as `unswbc submit` builds it; carthage-05 is 3.740 MiB.
- Sandbox CPU points per turn (`unswbc run --sandbox`, seed 1), slot against carthage-05: Schooltime p50 5.7 M,
  max 9.2 M; UNSW p50 6.0 M, max 10.1 M. The parent in the same games: max 10.2 M and 10.7 M. No runtime errors.

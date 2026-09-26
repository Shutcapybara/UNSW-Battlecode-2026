# serre-v02-doctrine

- **Lineage:** Serre (super-lineage). **Parent:** `serre-v01-foundation` (byte-copy of
  sinbad `build/sinbad/exp/e23` = sinbad-v07 + newborn body fix).
- **Borrowed:** map-class doctrine mechanism from `ouroboros-v13-ladder`
  (compact maps ≤ 625 tiles get a different parameter set than open maps;
  1428 fixtures of evidence for the approach). Contested-fast-bed rule is the
  serre G1 graft (devil leak diagnosis in `docs/serre.md` §6).

## Changes (from v01)

| Change | Layer | Default |
|---|---|---|
| `compact_max`, `doctrine_compact`, `doctrine_open` params + `apply_doctrine()` in `main.initialize_state` (after `w.init()`, before the ladder flag is read) | params/main | **off** (empty dicts → byte-parity with v01) |
| `fast_contest`: a fast bed (observed period ≤ `fast_per`) keeps full value even when an enemy head is closer — renewable beds are worth contesting | decision | **off** |

With default parameters v02 plays identically to serre-v01-foundation; graft
arms are `override.py` variants under `build/serre/variants/`:

| Variant | Doctrine (compact ≤ 625 cells) | Target leak |
|---|---|---|
| `v02a-ladder` | `ladder_nc=625` (hunter-style priority ladder: strike > split > own-pearl step, evaluator veto) | arena/Colosseum rush + opening production (G4) |
| `v02b-fastbed` | `fast_per=5, fast_mult=2.0, fast_contest=1` | devil contested centre (G1) |
| `v02c-both` | both | combination cell (selection_rule 2×2) |

## Measured

See `docs/serre.md` §8 experiment log and the run directories under
`experiment_data/`.

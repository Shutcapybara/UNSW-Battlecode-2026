# spike-x08-v32-compactprod — Gavroche v32 + Newton/Ouroboros compact production doctrine

- **Lineage:** Spike. Parent: `gavroche-v32-supported-divecap`.
- **Change:** v32's `split_option` gains Newton x10's compact-map production doctrine (maps <= 625 tiles only):
  keep splitting up to 26 units even past split_stop, +2 split score, no ambient threat charge on the split branch,
  newborn pocket gate 3 instead of 4, parent-trap penalty halved. With `compact_nc` 0 it is exactly v32.
- **Why (SPIKE-25):** v32's weakest maps are compact: arena and spring wells (0.38 on panel A). There it
  under-produces: by r200 it makes 7-34 splits vs 43-113 for the opponents that beat it, and on spring wells it
  collects 3-9 pearls by r50 vs 9-26. Newton x10 (with this doctrine) scores 0.54 on spring wells and 0.79 on
  delayed commons vs v32's 0.38 / 0.58. Risk: Newton is weak on devil (0.50 vs v32 0.83).

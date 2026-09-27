# Bifröst v16 — empty-route repeat penalty

This experiment keeps V01's policy and adds a capped revisit cost only after a
cell has been revisited more than twice, and only when no remembered pearl,
known pearl bed, nearby enemy head, or fresh crown is within five movement
steps. It targets the low-value Devil loops reported by the user while
retaining the baseline scoring near resources and visible combat.

The screen uses the same six maps and five opponent entries as V15. Results are
recorded in the [family notes](../../docs/bifrost-family.md).

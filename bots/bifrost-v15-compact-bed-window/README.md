# Bifröst v15 — compact bed window

This experiment keeps Bifröst v01's strategy and changes only bed timing on maps up to 625 cells during the first 200 rounds. It reduces the linear wait window from 12 to 6 rounds, testing whether stale or not-yet-ready beds draw dragons into low-value routes. V10's arrival-only rule was too aggressive; V15 keeps some value for beds due shortly after arrival.

The screen uses the same six maps and five opponent entries. See the [family notes](../../docs/bifrost-family.md).

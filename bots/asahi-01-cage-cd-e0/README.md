# asahi-01-cage-cd-e0 — Schooltime cage rule C+D, reserve E = 0 (P-A01)

Copy of `r/rome:bots/rome-06-cage-e1` (Rome06, parent `carthage-05-free-sprint`) with the E component removed: no unit
slot is reserved (`w.limit` is not touched). C and D are byte-identical to Rome06:

- C: when every simulated one-step move is fatal, a dragon of length >= 4 splits and keeps 2 segments; a shorter
  non-queen (id > 1) issues the invalid command (`SPLIT 99`, logged `SZ:cage_invalid`).
- D: the original queen (id <= 1) never pays segments for sprint steps (moves truncated to ceil(len/4) free steps).

Screening probe under D-044 (temporary hand rule). Preregistration: `docs/learning/proposals/P-A01-cage-cd-e0.md`.

# esquie-01-nodevil

Esquie lineage (M-1 map anatomy, GLM 5.3). Parent `lune-r1-07-latecap8x-only` (Lune R-1's
recommended level: Ares V06 with `search_cap_late` 48→384, `search_cap_sparse` 64→512).

The M-1 lane base per D-033: the three `W==32 && H==16` map-identity terms
(`devil_center_bonus`, `devil_lane_bonus`, `ally_body_buffer`) are off behind
`Params::shape_terms = false` (the renoir-23 ablation form). With `shape_terms = true`
the bot is transcript-identical to lune-r1-07 (golden parity verified at lane launch).

Purpose: the honest per-map starting point for the M-1 brick list — every pool/gen number
in `docs/findings/2026-10-01-esquie-map-anatomy.md` Part 1 is this bot's.

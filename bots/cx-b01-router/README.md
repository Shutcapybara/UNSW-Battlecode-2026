# cx-b01-router (C1-B, first cut; superseded by cx-b02-router)

anna-a02-chassis + `router.hpp`: arrival maps (own/enemy/ally BFS), bed valuation against the enemy's
earliest arrival, greedy assignment with spacing, patrol timing, de-convergence, dead-end trees and the
feeding rule, pearl-gated splits with a child target, big-child split when trapped, known-exit portals as
routes, `CX_ATLAS` switch (`cx-b01-router-noatlas` = off). Kept as a measured snapshot (dev screens v1–v7
in docs/findings/2026-09-30-cx-b01-router.md); the ablation arm (c) is cx-b02-router.

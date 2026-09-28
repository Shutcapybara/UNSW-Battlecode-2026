# yuna-v05-core — Yuna campaign finalist

Host: `gavroche-final` (= gavroche-v54-sparse-room, CPU-safe). Code: `yuna-v01-phase` layer (phase.py, yuna.py).
Enabled mechanisms (override.py):

- **Phase-scheduled portal policy** (`portal_mode 1`): blind-exit risk = 0.15/0.30/0.50 × V(me) in
  opening/mid/end (×0.4 when the exit tile was seen recently with no enemy head near it) instead of the host's
  flat 1.0 × V(me); unpaired-portal target value 6/3/1; deterministic per-dragon exploration dives
  (35%/12%/0% per 8-round window, dragons ≤ 8 long, halved if an older ally is adjacent).
  Phases: open r < 60, mid < 320, end ≥ 320.
- **Direction momentum** (`mom_w 0.6`, EWMA decay 0.6 of chosen first steps) — continuity between turns.
- **Newborn exit, tight births only** (`nb_mode 2`): a child born where its flood room < 12 ignores targets within 3
  of its parent's head and is pushed away from it for 6 turns.

Evidence (paired wins vs host on identical fixtures; see experiment_data/temporal_policy_20260927T173800Z_yuna/):
dev panels +13/113 (+11.5pp, 15 up / 6 down map×side clusters); fresh-opponent panel +10/109 (+9.2pp).
Sibling configs: yuna-v03-core (newborn exit ungated), yuna-x34-no-nb (no newborn exit) — statistically tied.

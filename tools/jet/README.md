# tools/jet — Jet lineage experiment tools (Claude)

Restored 2026-09-27 ~14:40 UTC after the untracked originals were lost in a repository pull/rebase;
a snapshot is also kept in experiment_data/cohort_research_20260927T011500Z_jet/tools_snapshot/.
(firstturn_cpu.py, a sandbox CPU helper that returned zeros, was not restored.)

- panel.py — paired arms x opponents x maps x seats panel on unswbc 1.0.0 native; resumable;
  `--deadline` stops starting new games (for 180 s device shells); records replay metrics,
  JET doctrine activations (verbose only for jet* bots) and native "ran out of time" counts.
- summ.py OUT [CONTROL] — per-arm/map/opp/seat scores and paired flips vs a control arm.
- backfill.py OUT — recompute replay metrics for rows lacking them.
- activation.py BOT CTRL OUT MAPS [DEADLINE] — count dispatcher doctrine choices per map.
- crown.py RESULTS A1 A2 — paired crown margin (own longest - enemy longest) at r400/450/500.
- newborn.py REPLAY — newborn survival and own-head crowding at self-inflicted deaths.
- make_dispatch.py HOST OUT — wrap any Python host in the Jet income-density dispatcher.
Setup: `uv venv -p 3.13 ~/bcenv && VIRTUAL_ENV=~/bcenv uv pip install unswbc==1.0.0 pycapnp pandas pyarrow`;
frozen bots in ~/w/bots, extra maps in ~/w/maps (panel.py looks there first).

# jet-v01-richladder — income-density doctrine dispatcher

Line: Jet (Claude). Host: gavroche-v32-supported-divecap (verbatim, `host/`).
Borrowed: ouroboros-v13-ladder (verbatim, `ladder/`). Dispatcher: `main.py`.
Each dragon process reads the init block and first turn and runs the ladder iff the
board is small (W*H <= 400) and the view is renewal-rich (>= 20 fertile tiles, >= 8
empty, >= 75% of empty ones respawning within 20 rounds); otherwise the host runs
unchanged. On the 33-map suite only arena fires.
Evidence: experiment_data/cohort_research_20260927T011500Z_jet/cycle_08_income_doctrine
and cycle_09_arena_panel_seat (arena 36/48 vs v32 16/48; 40/40 parity where it does not fire).
Research name: jet-v01c-richladder (identical files). Control for jet-v02.

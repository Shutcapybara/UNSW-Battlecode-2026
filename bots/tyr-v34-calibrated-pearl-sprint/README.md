# Tyr V34 — calibrated pearl-funded sprint defense

**Base:** Tyr V12 Devil scout tie-break.

**Change:** Retain V25's forecast of enemy sprint paths that collect a pearl
mid-action, but lower the threat-probability floor from 0.6 to 0.2. Fresh V33
replays showed severe pearl deficits on Autarky and Dilemma after introducing
the 0.6 floor. This arm isolates a more conservative calibration; it does not
include V33's portal or Trophy bonuses.

**Result:** **37–71** against V12 on fresh seeds 19–24 across the same nine
maps and both seats (108 games, zero draws or runner errors). Across 54 paired
map/seed sets, V34 swept 9, V12 swept 26, and 19 split. V34's map scores were
Trauma 11–1, Devil 6–6, Portals 5–7, Trophy 5–7, Default 4–8, Slithery Fight
4–8, Queen of Spades 2–10, Autarky 0–12, and Dilemma 0–12.

**Status:** Rejected as a V12 improvement. Lowering the pearl-threat floor to
0.2 did not repair the losses on Autarky or Dilemma. V12 remains the reference
winner in this matchup; V01 remains the family all-map baseline.

Runtime-source fingerprint (top-level Python and `bot.toml` files):
`7dbe3f29db08069eb08847614a106c0aeacec149a798f53f1b3adb2457b06989`.
Results are under `build/tyr-v34-vs-v12-seeds19-24-20260929/` (ignored local
output), run with `.venv` and native `unswbc 1.2.2`.

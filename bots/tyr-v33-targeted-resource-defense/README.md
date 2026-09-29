# Tyr V33 — targeted resource access and sprint defense

**Base:** Tyr V25 pearl-funded sprint defense.

**Changes:** Value an unexplored portal at 9 during the first 60 rounds on
32x16 maps, where the live review's Devil and Portals openings apply. On the
25x25 board, add 5 points for a pearl collected by a move during the first 40
rounds, targeting Trophy's reviewed early detour. Keep V12's movement, split,
and Devil opening behavior, plus V25's pearl-funded sprint forecast.

**Result:** **55–53** against Tyr V12 over six fixed seeds on the nine review
maps, both seats (108 games), with no draws or runner errors. Of 54 paired
map/seed sets, V33 swept 13, V12 swept 12, and 29 split. V33's map scores were
Portals 9–3, Trauma 9–3, Slithery Fight 8–4, Queen of Spades 7–5, Devil 7–5,
Default 6–6, Trophy 5–7, Autarky 2–10, and Prisoners' Dilemma 2–10.

**Status:** Experimental, with a narrow measured edge on this panel. It has no
all-map ELO or promotion claim; the Autarky and Prisoners' Dilemma losses remain
large.

Runtime fingerprint (Python files and `bot.toml`):
`c664bba60c1811d5bf1bb7c8cf80310473d41d3437d31fb693aa97ccfbac13c3`.

Results and replay statistics are under
`build/tyr-v33-paired-v12-seeds1-6-20260929/` (ignored local output), run by
`tools/pace/panel.py` with native `unswbc 1.2.2`.

## Fresh-seed validation

On fresh seeds 7–18, V33 scored **91–125** against V12 across the same nine
maps and both seats (216 games, zero draws, runner errors, or stats errors).
Across 108 paired map/seed sets, V33 swept 27, V12 swept 44, and 37 split.
Map scores were Trauma 23–1, Default 10–14, Devil 11–13, Portals 11–13,
Queen of Spades 11–13, Trophy 11–13, Slithery Fight 10–14, Dilemma 4–20, and
Autarky 0–24.

Combining seeds 1–18 gives V33 a **146–178** record over 324 games. Its Trauma
result is strong (32–4), but the Autarky (2–34) and Dilemma (6–30) losses
erase the initial six-seed edge. Keep V33 experimental and do not treat it as a
general V12 improvement. The fresh-seed run is under
`build/tyr-v33-fresh-v12-seeds7-18-absolute-20260929/` (ignored local output).

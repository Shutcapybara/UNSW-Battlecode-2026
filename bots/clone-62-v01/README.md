# clone-62-v01 — Heartbreaker imitation (team 62, sub 7233)

Trained with the ouroboros-m01-vibing-mimic recipe (tools/team_recon_claude):
v4 view+mem legal features (258) over the 130 current-era (sub 7233) public games
in `public_replays/team-62/packed`, HistGradientBoostingClassifier, exported
dependency-free to `model.json`. Splits follow the target's empirical rule
(child L-2 for L<=8, child 2 from L=9); sonar emits 4 rays/turn from the target's
payload vocabulary for fingerprint fidelity. Guarded mode masks certain-death
first steps. See docs/findings/2026-09-29-sakura-s02-arrival-econ.md for the
profile validation (units r100 / total r250 / longest r400 vs the live profile).

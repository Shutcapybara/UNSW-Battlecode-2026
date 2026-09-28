---
id: 2026-09-28-analysis-band-profiling-status
author: glm/analysis/a1
kind: observation
title: "Ladder-band opponent profiling is blocked on data access: no band-team replays exist locally and downloads need the API key; live-side fingerprints of the four field opponents are the available starter"
task: "A1 §3.5 — opponent models for the ladder band"
supersedes: []
evidence: "public_replays/ contains only teams 7/62/306/470 and battle-* corpora (checked 2026-09-28 22:xx local): zero replays for any of the ±8 band teams (534, 875, 473, 485, 347, 241, 75, 47, 790, 19, 406, 74, 722, 522, 977, 133). Ladder position from state/ladder.json: team 7 rank 68, elo 1742. Live-side fingerprints computed from opponent_stages (see loss-anatomy finding)."
---

# Status

The analysis as specified (fingerprint the ±8 band via their public replays) **cannot run from the analyst seat**: `tools/download_team_games.py` requires the API key, which the analyst does not touch. This is a director or executor action: ≤60 newest replays per band team, version-stratified by submission id.

# What exists now (starter table, from the live record)

Field opponents we actually face, verified controlled games (n = 90/93/72/10):

| opponent | their units r100 | their total r250 | their longest r499 | sonar/turn | portal steps | our share | they eliminate us at |
|---|---|---|---|---|---|---|---|
| 45 | 16 | 52 | 18 | 0.54 | 86 | 0.54 | r194 |
| 62 | 19 | 78 | 9 | 3.95 | 45 | 0.31 | r120 |
| 306 | 12 | 66 | 4 | 2.45 | 21 | 0.50 | r277 |
| 470 | 14 | 89 | 18 | 1.10 | 26 | 0.32 | r221 |

Reading: 62 wins with a fast strong opener (19 units by r100, kills by r120); 470 wins with economy scale (89 total by r250) and patience; 45 is portal-active and porous (0.54); 306 balanced. These four span the behaviours the band clones must cover: fast-opener, economy-scaler, portal-heavy, balanced.

# Recommended band representatives for clones (pending data)

Of the ±8 band (ranks 60–76), none is profiled. The clone recipe (boosted trees on legal inputs, `team_recon_306_20260927_claude/REPORT.md` §5a) costs ~½ day per two clones. Until their replays are fetched, the local panel should use the four live fingerprints above as its target diversity axes: any panel missing a fast-opener archetype (62-like) will overestimate compact-map performance — exactly the −75-to-−100 pp local/live cells in the calibration finding.

**Decision fed**: executor downloads band replays (one batch, ≤600 files); then descriptive.py fingerprints → behavioural clustering → pick 6 clones + recover teammate uploads from API zips (hours; every live control becomes a local opponent).

**Falsifier**: band fingerprints clustering entirely within the four live archetypes (then 2 clones suffice instead of 6); or clone-vs-live mismatch >15 pp share on shared maps (recipe fails for the band).

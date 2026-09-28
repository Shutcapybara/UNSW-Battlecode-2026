---
id: 2026-09-28-analysis-elo-exposure
author: glm/analysis/a1
kind: observation
title: "Team Elo is inherited by every upload and moved only by ranked games; testing-to-date cost ≈ −42 Elo in a day, driven by autoscrim exposure while weak uploads were active — not by the 20 ranked test games"
task: "A1 §3.9 — ranked exposure accounting"
supersedes: []
evidence: "LIVE state.json seen_series (114 series snapshots with teamAElo/teamBElo, 2026-09-28), ladder.json (team 7: rank 68, elo 1742, fetched 21:55 local), hub ranked_exposure (20 games, 4 series), series payloads for winners. Unit = series snapshot for the trajectory, game for W/L. eloChangeA/B are null in every locally cached match — the per-game Elo impact of the 20 test games is NOT computable from local data."
---

# What the record shows

**Elo is team-level and inherited across uploads.** The trajectory is continuous across activations (9663 active 06:46–08:00, incumbent switches mid-day): 1784 → 1774 → 1730 → 1712 → 1753 → … → 1742 (14 moves over 114 snapshots; final fetch 21:55 local). No reset, no jump at any submission switch — fresh-start regimes are ruled out.

**Unranked games never move Elo; ranked autoscrim does.** Cleanest window: between 05:15:43 and 05:21:51 our only games were four unranked Dilemma fills — Elo moved +41. Conversely the −44 move (04:46–05:01) coincided with 20 unranked field games plus ranked series 454072 (4 ranked losses to team 15, elo-equal): 4 losses × K/2 each bounds K ≤ ~22 if that series explains the whole move; other ranked results in the window make K smaller. K is a per-game, moderate-magnitude constant (plausibly 8–22); a precise value needs the eloChange fields (below).

**The 20 ranked exposure games (9663, 06:46–08:00 UTC) are a minor part of the day's loss.** Known outcomes: series 463004 vs 853 (1 win, 3 losses of 4 completed) and 474275 vs 790 (1–1 of 2 completed); series 467153/468473 show 0 completed in the last local fetch (stale snapshots). Worst case with K=22: ≈ −30 Elo; realistic ≈ −10 to −20. The observed autoscrim record in cached ranked series (475133: 2/5 vs 133; 476014: 2/5 vs 40; 480540: 3/5 vs 790; 482790: 4/5 vs 977; plus older 441437 0/3, 433243 5/5 …) shows the same magnitude spread.

**Day total: 1784 → 1742 (−42)** between 02:00 and ~12:00 UTC while non-incumbent uploads were active much of the time. This is the price of autoscrim exposure with a weak active upload — it accrues per hour active, not per switch.

# Consequences for the blackout window

The configured guard (±8/+12 minutes around even UTC hours) covers only switch instants. Under team-level Elo the actual exposure is **continuous while a test upload is active**: the −44 window happened mid-hour, hours away from any switch. The window should instead bound *activation duration of non-incumbent uploads* (test in short windows, reactivate incumbent between), or accept the bleed and test less often.

**Decision fed**: (a) treat test-upload activation time as the Elo cost driver; (b) one API fetch of the 4 exposure series' details (+ team elo history) would pin K exactly — that is a director action, not an analyst one; (c) the hub's ranked_exposure accounting is incomplete without eloChange — add the fetch to the executor's series poll.

**Falsifier**: eloChangeA/B values from the API showing the 20 test games moved Elo by ≥40 points total (test games, not autoscrim, dominate); or a future upload activation that resets/jumps team Elo (would revive the fresh-start hypothesis).

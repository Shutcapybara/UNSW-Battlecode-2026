# leviathan-x04-charybdis-replies

Line: Leviathan / Charybdis.

Base: fresh decision policy; borrowed: input parsing, terrain/portal geometry, own-body history and food-memory helpers from leviathan-x01-riptide-horizon. Its planner, reproduction rule and communications are replaced.

Hypothesis: explicitly minimizing over opponent replies enables useful blocking, forced trades and sacrifices. The local game models ID order, same-round newborn turns, movement, sprinting, splitting, food and deaths. Three half-turns, width six, and a leaf-accounted nominal budget of 450 bound search.

Production has per-unit value; a deterministic subset of IDs banks growth after maturity. There is no elected crown, feeding, sonar, trained network or online learning.

**Verdict: retained for phase-end comparison; mixed evidence for the reply-search hypothesis.**

Full G, five ACTIVE opponents × eleven maps × both sides:

| Set | W–L–D |
|---|---:|
| ALL | 31–79–0 |
| compact | 16–34–0 |
| side B | 16–39–0 |
| compact B | 10–15–0 |
| fry-v14-stateful-size-aware-3 | 5–17–0 |
| hunter-v14-cpp-hybrid-route-spacing | 8–14–0 |
| hunter-v20-portal-scouts | 7–15–0 |
| kraken-v04-eval | 9–13–0 |
| side A | 15–40–0 |
| compact A | 6–19–0 |
| ouroboros-v10-beacon | 2–20–0 |
| open | 15–45–0 |
| open B | 6–24–0 |
| open A | 9–21–0 |

Complementarity: 3 wins where v09 loses; 2 also lose for Riptide x02. V09 scores 85–25–0 and remains stronger overall.

Paired final screen, base=no-search, candidate=reply search:

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 5–19–0 | 4–20–0 | -1.0 | -2 |
| compact | 1–17–0 | 2–16–0 | +1.0 | +2 |
| side B | 3–9–0 | 3–9–0 | +0.0 | +0 |
| compact B | 1–8–0 | 2–7–0 | +1.0 | +2 |
| hunter-v14-cpp-hybrid-route-spacing | 2–6–0 | 2–6–0 | +0.0 | +0 |
| hunter-v20-portal-scouts | 2–6–0 | 1–7–0 | -1.0 | -2 |
| leviathan-v09-arrival | 1–7–0 | 1–7–0 | +0.0 | +0 |
| side A | 2–10–0 | 1–11–0 | -1.0 | -2 |
| compact A | 0–9–0 | 0–9–0 | +0.0 | +0 |
| open | 4–2–0 | 2–4–0 | -2.0 | -4 |
| open B | 2–1–0 | 1–2–0 | -1.0 | -2 |
| open A | 2–1–0 | 1–2–0 | -1.0 | -2 |

Improved: 1; regressed: 2; unchanged: 21. Deterministic fixtures.

Targeted open-orientation validation (24 games, not full G+V):

| Set | W–L–D |
|---|---:|
| ALL | 2–22–0 |
| open | 2–22–0 |
| side B | 1–11–0 |
| open B | 1–11–0 |
| hunter-v20-portal-scouts | 2–10–0 |
| leviathan-v09-arrival | 0–12–0 |
| side A | 1–11–0 |
| open A | 1–11–0 |

Judge CPU: arena, big_empty and trauma, both sides against Hunter v20 (six games):

| Metric | Per-game range, million points |
|---|---:|
| cpu_p50 | 4.7–7.9 |
| cpu_p99 | 5.8–34.4 |
| cpu_max | 5.9–57.0 |

Known limits: only one fully observed enemy is dynamic; other bodies are frozen, hidden information is unresolved, enemy population is unknown, and width/budget limits omit replies. Local material value is not a learned estimate of winning probability.

Design: docs/leviathan/CHARYBDIS.md. Full controls, traces, historical compute failures and results: docs/leviathan/CHARYBDIS_RESULTS.md. Parameters live in params.h; lab overrides only private snapshots.

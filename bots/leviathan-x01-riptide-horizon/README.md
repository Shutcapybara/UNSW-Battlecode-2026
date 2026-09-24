# leviathan-x01-riptide-horizon

Line: Leviathan / Riptide.

Base: fresh C++ implementation; borrowed: protocol and geometry concepts from leviathan-v07-local-cache. No Hunter/Ouroboros policy copied.

Hypothesis: resource-funded colonies plus bounded future-route planning can form a competitive alternative to crown/feeding evaluation.

**Verdict: archived from mainline promotion; retained as an experimental search baseline.** The user explicitly requested competitive diversity. This is not a claim of overall superiority.

Full G: five ACTIVE opponents × eleven maps × both sides. W–L–D:

| Set | W–L–D |
|---|---:|
| ALL | 33–77–0 |
| compact | 4–46–0 |
| side B | 16–39–0 |
| compact B | 1–24–0 |
| fry-v14-stateful-size-aware-3 | 9–13–0 |
| hunter-v14-cpp-hybrid-route-spacing | 7–15–0 |
| hunter-v20-portal-scouts | 8–14–0 |
| kraken-v04-eval | 9–13–0 |
| side A | 17–38–0 |
| compact A | 3–22–0 |
| ouroboros-v10-beacon | 0–22–0 |
| open | 29–31–0 |
| open B | 15–15–0 |
| open A | 14–16–0 |

Versus the v09 reference (85–25–0), there are 0 wins on fixtures v09 did not win and 52 v09 wins not retained. See the diversity file for exact cases.

Judge CPU: arena and big_empty, both sides against Hunter v20 (four sandbox fixtures).

| Metric | Per-game range, million points |
|---|---:|
| cpu_p50 | 5.7–11.3 |
| cpu_p99 | 9.8–15.2 |
| cpu_max | 10.0–17.6 |

All exposed decision parameters are documented in params.h. Run snapshot-only variants with tools/leviathan/lab.py --set key=value. No parameter-only folders.

31 regression tests pass, including the C++ rule checks for both branches. x02 with viability=False preserves x01 movement/split/sonar in all four neutral-control games.

Design, assumptions and reproducible commands: docs/leviathan/RIPTIDE.md. Full ablations, side/map-class results, validation and limits: docs/leviathan/RIPTIDE_RESULTS.md.

Important limits: future food and unknown edges are forecasts; other bodies are held stationary; capacity assumes tail release without intervening growth. No crown, feeding, active hunting, role assignment, or map-wide shared memory is present.

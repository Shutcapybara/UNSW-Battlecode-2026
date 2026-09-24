# leviathan-x02-riptide-viability

Line: Leviathan / Riptide.

Base: leviathan-x01-riptide-horizon; borrowed: its world model, planning and colony policy.

Hypothesis: own-tail release capacity filtering prevents traps missed by a short route horizon. Original fork-risk constant 0.35 is exposed without changing the default.

**Verdict: archived from mainline promotion; retained as an experimental search baseline.** The user explicitly requested competitive diversity. This is not a claim of overall superiority.

Full G: five ACTIVE opponents × eleven maps × both sides. W–L–D:

| Set | W–L–D |
|---|---:|
| ALL | 42–67–1 |
| compact | 3–46–1 |
| side B | 21–33–1 |
| compact B | 0–24–1 |
| fry-v14-stateful-size-aware-3 | 10–12–0 |
| hunter-v14-cpp-hybrid-route-spacing | 10–12–0 |
| hunter-v20-portal-scouts | 9–13–0 |
| kraken-v04-eval | 11–10–1 |
| side A | 21–34–0 |
| compact A | 3–22–0 |
| ouroboros-v10-beacon | 2–20–0 |
| open | 39–21–0 |
| open B | 21–9–0 |
| open A | 18–12–0 |

Versus the v09 reference (85–25–0), there are 4 wins on fixtures v09 did not win and 47 v09 wins not retained. See the diversity file for exact cases.

Paired structural changes against x01:

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 33–77–0 | 42–67–1 | +9.5 | +19 |
| compact | 4–46–0 | 3–46–1 | -0.5 | -1 |
| side B | 16–39–0 | 21–33–1 | +5.5 | +11 |
| compact B | 1–24–0 | 0–24–1 | -0.5 | -1 |
| fry-v14-stateful-size-aware-3 | 9–13–0 | 10–12–0 | +1.0 | +2 |
| hunter-v14-cpp-hybrid-route-spacing | 7–15–0 | 10–12–0 | +3.0 | +6 |
| hunter-v20-portal-scouts | 8–14–0 | 9–13–0 | +1.0 | +2 |
| kraken-v04-eval | 9–13–0 | 11–10–1 | +2.5 | +5 |
| side A | 17–38–0 | 21–34–0 | +4.0 | +8 |
| compact A | 3–22–0 | 3–22–0 | +0.0 | +0 |
| ouroboros-v10-beacon | 0–22–0 | 2–20–0 | +2.0 | +4 |
| open | 29–31–0 | 39–21–0 | +10.0 | +20 |
| open B | 15–15–0 | 21–9–0 | +6.0 | +12 |
| open A | 14–16–0 | 18–12–0 | +4.0 | +8 |

Improved: 15; regressed: 5; unchanged: 90. Deterministic fixtures.

Targeted orientation validation:

| Set | W–L–D |
|---|---:|
| ALL | 17–71–0 |
| compact | 1–39–0 |
| side B | 9–35–0 |
| compact B | 0–20–0 |
| hunter-v20-portal-scouts | 17–27–0 |
| leviathan-v09-arrival | 0–44–0 |
| side A | 8–36–0 |
| compact A | 1–19–0 |
| open | 16–32–0 |
| open B | 9–15–0 |
| open A | 7–17–0 |

Judge CPU: big_empty and trauma, both sides against Hunter v20 (four sandbox fixtures).

| Metric | Per-game range, million points |
|---|---:|
| cpu_p50 | 8.0–11.6 |
| cpu_p99 | 10.8–15.6 |
| cpu_max | 11.0–18.0 |

All exposed decision parameters are documented in params.h. Run snapshot-only variants with tools/leviathan/lab.py --set key=value. No parameter-only folders.

31 regression tests pass, including the C++ rule checks for both branches. x02 with viability=False preserves x01 movement/split/sonar in all four neutral-control games.

Design, assumptions and reproducible commands: docs/leviathan/RIPTIDE.md. Full ablations, side/map-class results, validation and limits: docs/leviathan/RIPTIDE_RESULTS.md.

Important limits: future food and unknown edges are forecasts; other bodies are held stationary; capacity assumes tail release without intervening growth. No crown, feeding, active hunting, role assignment, or map-wide shared memory is present.

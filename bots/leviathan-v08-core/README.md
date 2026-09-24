# leviathan-v08-core

Line: Leviathan (GPT). Base: ouroboros-v10-beacon; borrowed: complete evaluator,
terrain, safety, targeting, production, roles, crown/feeding and sonar from
ouroboros-v10-beacon. Standalone Python, no runtime dependency on another bot.

Hypothesis: adopting the measured survival/crown reference provides a stronger
convergence base than maintaining v07's missing components. The only refactor
extracts the unchanged P/RP table to config.py; policy functions remain identical.

**Verdict: null result in behavior, retained as the equivalence baseline.**
All 18 reference matchups have identical movement, split and sonar streams
(arena, default_small, default; Hunter v14/v20 and Kraken v04; both sides).
AST and parameter tests independently verify the extraction. This does not
claim native/sandbox stream equivalence or promote a duplicate into ACTIVE.

Sets: G = five gauntlet opponents × 11 maps × both sides (110); V = the same
opponents on 22 transpose/flip variants (220). G+V = 330. Variants were held
out until the candidate profile was frozen; no tuning used their outcomes.
These are deterministic fixtures, not independent random samples. Source/map
hashes and native/sandbox modes are checked by tools/leviathan/converge.py.
Raw evidence lives in build/leviathan/cycle1-*; tables here are durable.

## Paired G+V results (base column is v08)

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 229–99–2 | 244–86–0 | +14.0 | +28 |
| compact | 79–69–2 | 93–57–0 | +13.0 | +26 |
| side B | 116–47–2 | 122–43–0 | +5.0 | +10 |
| compact B | 39–34–2 | 45–30–0 | +5.0 | +10 |
| fry-v14-stateful-size-aware-3 | 53–13–0 | 56–10–0 | +3.0 | +6 |
| hunter-v14-cpp-hybrid-route-spacing | 46–20–0 | 51–15–0 | +5.0 | +10 |
| hunter-v20-portal-scouts | 35–31–0 | 42–24–0 | +7.0 | +14 |
| kraken-v04-eval | 62–2–2 | 63–3–0 | +0.0 | +0 |
| side A | 113–52–0 | 122–43–0 | +9.0 | +18 |
| compact A | 40–35–0 | 48–27–0 | +8.0 | +16 |
| ouroboros-v10-beacon | 33–33–0 | 32–34–0 | -1.0 | -2 |
| open | 150–30–0 | 151–29–0 | +1.0 | +2 |
| open B | 77–13–0 | 77–13–0 | +0.0 | +0 |
| open A | 73–17–0 | 74–16–0 | +1.0 | +2 |

Improved: 32; regressed: 17; unchanged: 281. Deterministic fixtures.

## Judge CPU

Four sandbox games: big_empty and trauma, both sides vs Hunter v20.

| Metric | Per-game range (million points) |
|---|---:|
| cpu_p50 | 18.4–28.9 |
| cpu_p99 | 28.7–47.9 |
| cpu_max | 41.4–66.0 |

Zero sampled timeouts. Feeding intentionally records no-action deaths.

Component boundaries and inherited limitations: docs/leviathan/CONVERGENCE.md.

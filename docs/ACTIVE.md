# ACTIVE — bots in contention (single source of truth)

**Cycle 0 · 2026-09-25 · Unifier: Claude (Ouroboros)**

This is the only file that says which bots matter right now. The unifier for
each cycle rewrites it (see `docs/HANDOFF.md` §8). Everyone else reads it and
does not edit it. The previous version moves to `docs/cycles/cycle-NN.md`.

## Deployed

| Slot | Bot | Notes |
|---|---|---|
| Live submission | **hunter line** (exact version: *owner to confirm*) | Team member's C++ line. Co-best in class with ouroboros-v10. |

## Gauntlet: the benchmark every candidate plays

Every candidate plays these bots on all 11 maps, both sides (110 games), plus
the variant maps where noted. Keep the gauntlet to 6 bots or fewer. Each one
earns its place by covering a strategy the others don't.

| Bot | Line | Cluster (HANDOFF §5) | Why it's here |
|---|---|---|---|
| `ouroboros-v10-beacon` | Claude | survival + crown evaluator | Co-champion. Best on open maps; the reference for conversion (crown and feeding). |
| `hunter-v14-cpp-hybrid-route-spacing` | user | swarm/churn ladder | Strongest hunter against the field on the 11 maps (GLM: 2.01 points/game). |
| `hunter-v20-portal-scouts` | user | swarm/churn ladder + traps + scouts | Hardest opponent for v10 on compact maps and variants. Adds trap tactics. |
| `fry-v14-stateful-size-aware-3` | user (fry) | pure swarm ladder | Plain production/aggression reference. Beats ouroboros-v05 14–8 on the 11 maps. |
| `kraken-v04-eval` | Kimi | length banker | Only bot with a winning record against hunter-v20 (12–9). Tests the round-500 race. |

Pool string (copy-paste):

```
ouroboros-v10-beacon hunter-v14-cpp-hybrid-route-spacing hunter-v20-portal-scouts fry-v14-stateful-size-aware-3 kraken-v04-eval
```

## Line tips (working bases, not in the gauntlet)

| Line | Tip | Status |
|---|---|---|
| Ouroboros (Claude) | `ouroboros-v10-beacon` | In the gauntlet. v11-opening was a null result (kept for history only). |
| Leviathan (GPT) | `leviathan-v07-local-cache` | Out of the gauntlet: loses 0–22 to v10 and 4–18 to hunter-v14. Cleanest small codebase. |
| Kraken (Kimi) | `kraken-v04-eval` | In the gauntlet. |
| Hydra (GLM) | `hydra-v10-farmclean` (v06-echo is the older flagship) | Out of the gauntlet. Its hunter-v03 C++ fork is dominated by hunter-v14. |
| Hunter (user) | `hunter-v20-portal-scouts` | In the gauntlet, alongside v14. |

## Cycle 0 evidence

All results are native (not sandbox), both sides, replays in `build/` (git-ignored).
Result format is W–L (–D).

**ouroboros-v10 against the field, 11 maps** (Claude, `ouro-build/act1`, 132
games): **108–23–1**.

| Opponent | Result |
|---|---|
| leviathan-v07 | 22–0 |
| kraken-v04 | 21–0–1 |
| hydra-v10 | 19–3 |
| fry-v14 | 18–4 |
| hunter-v14 | 16–6 |
| hunter-v20 | 12–10 |

By side: A 57–9, B 51–14. v10 lost only on compact maps:

| Map | Result |
|---|---|
| arena | 5–6–1 |
| default_small | 7–5 |
| devil | 8–4 |
| trophy | 8–4 |
| Colosseum | 10–2 |

**ouroboros-v10 against hunter-v16/v20, 33 widefast maps** (the 11 maps plus
transposed and flipped variants, without the big maps): **66–54**.

| Map class | Result |
|---|---|
| Compact | **7–53** |
| Open | **59–1** |

The base 11 maps understate the compact-map weakness. Always add variants.

**hunter-v20 against the field, 11 maps** (Claude, 88 games): **50–37–1**.

| Opponent | Result |
|---|---|
| leviathan-v07 | 16–6 |
| hydra-v10 | 14–8 |
| fry-v14 | 11–11 |
| kraken-v04 | 9–12–1 |

By map class it goes compact **37–2–1**, open **13–35**. Of its losses, 33 are
round-500 length tiebreaks.

**GLM's hunter fixtures, 11 maps** (from `cross-line-review.md` §7), each
against ouroboros-v05, kraken-v04, leviathan-v07 and hydra-v06:

| Bot | vs ouroboros-v05 | vs kraken-v04 | vs leviathan-v07 | vs hydra-v06 |
|---|---|---|---|---|
| hunter-v14 | 12–10 | 14–8 | 18–4 | 15–7 |
| hunter-v20 | 11–11 | 9–12 | 16–6 | 17–5 |
| fry-v14 | 14–8 | 12–10 | 5–17 | 11–11 |

**Opening mechanism** (Claude): v10 against hunter-v15 on compact maps, rounds
0–30.

| Measure | v10 | hunter-v15 |
|---|---|---|
| Pearls | 13.9 | 43.6 |
| Splits | 5.6 | 18.1 |
| Units at round 30 | 4.3 | 11.6 |

## Archived (dropped from comparisons this cycle, not deleted)

Each bot here is dominated by a gauntlet bot of the same cluster, or never beat its successor.

| Bot | Reason |
|---|---|
| fry-v01…v13 | Dominated by fry-v14 or hunter-v14. |
| hunter-v01…v13, v15…v19 | Dominated by v14 or v20. v15 is kept in mind only as the opening-economy reference (bed pre-positioning). |
| hydra-v01…v10 | v06–v10 are dominated by hunter-v14 (same ancestry, worse against every opponent). The Python v01–v03 are superseded. |
| kraken-v01…v03, kraken-s01/s02, kraken-prof | v04 behaves identically to v03; s01/s02 were rejected sweeps. |
| leviathan-v01…v06 | Superseded by v07 (identical action stream to v06). |
| ouroboros-v01…v09, v11 | Dominated by v10 on X, C and H (see the v10 README). |
| fry-v03-portal-hunters | The original baseline. Every active line beats it. |

## Open questions for next cycle's unifier

- Which hunter version is deployed? Pin it in the Deployed table.
- Run a gauntlet round-robin (5 bots, 11 maps plus variants) so the table isn't built from mixed sources.
- Sandbox CPU for every gauntlet Python bot on big_empty.

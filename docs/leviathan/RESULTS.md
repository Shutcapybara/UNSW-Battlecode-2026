# Cycle 1 convergence results

Gate: compact net W–L gain ≥4, no compact/open/opponent set below −3, sandbox p99 <60M and max <80M. Observed net deltas: `{'compact': 26.0, 'open': 2, 'fry-v14-stateful-size-aware-3': 6, 'hunter-v14-cpp-hybrid-route-spacing': 10, 'hunter-v20-portal-scouts': 14, 'kraken-v04-eval': 0.0, 'ouroboros-v10-beacon': -2}`. CPU gate: pass.

**Verdict: Promoted as the Leviathan working candidate for the next convergence; ACTIVE promotion remains with the unifier.**

Sets: G = five gauntlet opponents × 11 maps × both sides (110); V = the same
opponents on 22 transpose/flip variants (220). G+V = 330. Variants were held
out until the candidate profile was frozen; no tuning used their outcomes.
These are deterministic fixtures, not independent random samples. Source/map
hashes and native/sandbox modes are checked by tools/leviathan/converge.py.
Raw evidence lives in build/leviathan/cycle1-*; tables here are durable.

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

Candidate CPU:

| Metric | Per-game range (million points) |
|---|---:|
| cpu_p50 | 18.6–29.8 |
| cpu_p99 | 28.8–48.9 |
| cpu_max | 41.5–67.1 |

29 regression tests pass; 18 reference and six neutral full-stream equivalence cases pass. Both cores pass four sandbox games each, with no sampled timeouts.

See bots/leviathan-v09-arrival/README.md for ablations, flips, CPU, and inherited gaps; docs/leviathan/CONVERGENCE.md is the component handoff.

---

The following is the preserved v07 historical report.

# Leviathan results — 24 September 2026

**Current candidate: `bots/leviathan-v07-local-cache`.** Seven standalone Python
versions are preserved. No Hydra, Kraken, Ouroborous, shared runner, or shared
design-file edits were made by this work.

## Current measured strength

Both sides on arena, default, default_small, and queen_of_spades:

| Opponent | Wins | Draws | Losses |
|---|---:|---:|---:|
| fry-v03-portal-hunters | 8 | 0 | 0 |
| kraken-v03-judge-safe | 4 | 0 | 4 |
| hydra-v06-echo | 3 | 0 | 5 |
| **Total** | **15** | **0** | **9** |

Report: `build/leviathan/v07-diverse/report.md`.

On the separate four-map validation set (big_empty, small, schooltime,
queen_of_spades_but_she_ages), v07 scored **5–3 against Fry**. Combined with the
quick set, that is **13–3 on eight distinct maps with sides swapped**. The two
wins on `small` are one-round edge cases. The three losses are both big_empty
sides and one ageing-portal side. Those remain real weaknesses.

Report: `build/leviathan/v07-holdout/report.md`.

These are deterministic map/side cases, not independent random trials or a
ladder rating. The validation maps are now known and should not be called
untouched holdouts in subsequent tuning. No online submission was made.

## What each iteration taught us

| Version | Change / hypothesis | Evidence and decision |
|---|---|---|
| v01 evaluator | Fresh bounded action evaluator | 0–8 against Fry/Kraken on two maps. One Arena loss ate 27 pearls but made no children. |
| v02 expansion | Increase split value and growth threshold | 4–0 against v01, still 0–8 against external baselines. |
| v03 population | Remove map-area population cap | External score 1–7. Early production improved, but trades and sprints depleted useful material. |
| v04 material | Net length instead of gross pearls; price unit loss in trades | 4–0 vs v03; external score improved from 1/8 to 6/8, with five improved cases and no regressions. |
| v05 tail risk | Predict newborn enemies at visible tail candidates | Same 6/8 external score; 2–2 directly against v04. No evidence to select the added model. |
| v06 confirmed growth | Stale pearls may be targets but cannot fund legal sprints | One v04 replay said `can't pay for step 2`. Regression test added. Shared 24-case score improved 11→15, four improved cases and no regressions. |
| v07 local cache | Invalidate only affected terrain transitions; cheaper neighbors; skip unused leaf queue entries | All action streams identical to v06 in 32 native cases. Large-map judge margin improved substantially. Selected. |

Original baseline: `build/leviathan-v01-smoke`.
Experiments: `build/leviathan/v02-expansion`, `v03-population`, `v04-material`,
`v05-tail-risk`, `v06-diverse`, and `v07-diverse`.
Direct v06/v04 comparison: `build/leviathan/v06-v04` (2–2, two maps).

Full native action-stream comparisons are saved as `equivalence.json` in the
v07 diverse and holdout run folders. This checks every bot's action, not just
the final winner. Some v06/v07 sandbox large-map action streams differ despite
native equivalence; the cause was not isolated. Sandbox results were therefore
measured separately and are not treated as identical trajectories or mixed into
native paired comparisons.

## Judge validation

Ten v07 sandbox games against Fry, both sides on arena, default,
queen_of_spades, big_empty, and schooltime:

- **8 wins, 2 losses**; both losses are big_empty length tiebreaks.
- **Zero invalid-action deaths, reported timeouts, match errors, or replay-analysis errors.**
- Highest reported v07 turn cost: **83.6 million / 100 million points**.
- Highest v06 turn cost over the same tested map families: **99.1 million**.
- Big_empty v07 peaks: **76.7M / 71.1M**, compared with v06 **99.1M / 98.7M**.
- Native runs alone do not establish judge compatibility. These samples provide
  useful margin, not a worst-case proof on all maps or reachable positions.

Reports: `build/leviathan/v07-judge/report.md` and
`build/leviathan/v07-judge-large/report.md`. CPU figures are rounded runner
summaries. This installed runner leaves replay instruction fields absent, so
zero in the legacy raw field must not be interpreted as zero CPU work; the lab
now labels missing readings and records the rounded log-derived estimate.

## Verification and remaining work

All **16 focused regression tests pass**, including toroidal and portal routing,
local cache equivalence, own-tail collision, sprint affordability, stale-pearl
funding, last-unit trade protection, both enemy ID orders, replay pointer types,
and absent-meter handling. All Leviathan Python files compile.

The replay reader was cross-checked on 131 completed match replays for winner,
round count, death counts, and final population. Later harness runs perform the
same cross-checks per match. Official final lengths come from replay standings.
All runs retain source/map snapshots, manifests, logs, and replays.

Priority experiments next:

1. Concentrate late growth in a protected leading dragon. The large-open-map
   losses survive to round 500 but lose the longest-dragon comparison.
2. Reduce congestion and traps. Many wall/self deaths carry a `trapped`
   indicator; fix the decisions that enter the trap rather than the last move.
3. Improve combat against Hydra. The current model still loses most of that
   four-map matchup despite beating the original Fry baseline.
4. Make teammate reports useful for pearl allocation. Current sonar report
   storage is infrastructure only; target ownership and information relaying
   are not implemented yet.

Design: `docs/leviathan/DESIGN.md`.
Commands: `tools/leviathan/README.md`.
Submission archive: `build/leviathan/leviathan-v07-local-cache.zip`.

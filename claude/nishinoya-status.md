# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **D-055 (17:02Z) read — live-first.** My 16:45Z bed-variant probe was adopted as the deciding
  evidence ("about 15 % of live ranked games run on bed layouts our templates lack … Nishinoya's
  probe, unaudited"). Local gates no longer prerequisite uploads; LS-1 (k16 vs 14585, 204 games)
  ordered. P-5 approved as amended by all three seats (my feature-set amendment carried; λ∈{0.5,1}
  at screens — my dissent adopted). P-6 approved as amended (my diagnostic framing + Φ-same-rows).
  Scored forecasts recorded: P-5 offline 0.55 (mine), P-6 falsifier-not-triggered 0.80, V-legal ≥ Φ
  0.20 (all three seats).
- **Unit 17:44Z: LS-1 objective amendment (Sugawara 17:29Z) — I AGREE, posted before dispatch.**
  Replicated his sign-test minimums exactly (4–0 p=0.0625, 5–1 0.031, 6–1 0.109; 7–2 0.164 excluded);
  sparse premise consistent with the frozen JSON (net +7 lower-bounds changed at 7; JSON has no
  per-game rows → his print n+/n−/n0 ask is right); decisive defect = simulated null false-pass
  0.16–0.33 of the cluster rule at K=2–20. My forecasts: PASS as-written 0.45, **amended 0.30**.
  Asked that the amendment be frozen in a D-record immediately on acceptance.
- **Probe (unaudited): Tanaka's P-5 series-clean cohort** — manifest-level proxy gives 126 games /
  93 series (Autarky 49 / Trauma 40 / Maze 37), an upper bound consistent with his frozen 115/85
  (the gap ≈ the oracle-coverage filter). Both far above the gate's floor; not BOARD-material.
- **Last BOARD timestamp processed: 2026-10-04 17:29 UTC.** Next unit: LS-1 dispatch + D-056 (the
  amendment freeze?), P-5 teacher rows/fit (Hinata hourly at :35), P-2 rev 4.
- Required reading done: `_common.md`, `00-MACRO.md`, D-042–D-045, live-maps brief, BOARD tail,
  C5–C10 (chongqing wrap-up).

## First-session probes (unaudited) — `docs/findings/2026-10-04-nishinoya-r0-probes.md`

1. **Decode backlog:** 7,057/14,674 in-scope post-m2 decoded; queue 7,617 and growing (decode idle
   since 05:18Z; store +1,235 games in 4.5 h). Data's R0 one-off native decode needs a re-run.
2. **Splits feasibility:** all 17 live maps have 666–1,050 in-scope post-m2 games (487–615 ranked,
   ~110–160 top-ten-ranked); any ≥3-map held-out freeze spanning classes A–E is supportable; a
   held-out map costs only 10–23 of our 296 own games. QoS = "Queen Of Spades"; PD10 has no separate
   post-m2 map.
3. **Gate-tooling contradiction:** `lane.py --gate learned125` hard-codes run-record
   `runtime_version == '1.2.5'` (line 475); the main venv has `unswbc==1.2.3`; the Learner prompt
   pins 1.2.9. Every learned-arm gate run is blocked until the Chair rules one version canonical.

## Conventions I hold to

- Verdicts on assigned cards in `docs/learning/reviews/P-<n>-nishinoya.md` (agree/amend/reject,
  replication, P(pass) + expected effect, dissent, known precedent), one BOARD line each.
- My own proposals follow macro §3's card template; nothing that skips a rung or bundles changes.
- Numeric claims carry denominator, population, map_era; interval where sampled.
- Pushes only via the keeper (`hub-state/control/git.json`, `push_branches`), one request at a time.

## Stop

Holds if `claude/nishinoya-status.md` says STOP (this file, on main). Mac unreachable → one line, then stop.

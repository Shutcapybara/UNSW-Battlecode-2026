# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **R0 PASSED (D-053 §A, 14:28Z)** — my replications cited for items 1/3/4/5. Ladder at R1 (waiting on
  the P-2 confirmation release) and R2 (Hinata's card + teacher rows).
- **Unit 14:46Z 4 Oct:** filed my D-053 §D forecast before the card: **P(asahi-05-kz12-k16 gate PASS,
  seeds 2–3) = 0.40** (Chair 0.35, Sugawara 0.35). Probe replication (unaudited) from the frozen
  per-map rows: Sugawara's decomposition exact — Weakhold +43.75 pp (15–1 vs 8–8), other 16 maps net
  0, pool +2.57 pp all Weakhold; weakhold wall deaths −19.6/1k = mechanism visible there. Above the
  pack because the concentration is mechanism-consistent (class-C attrition, wall-death-dominated);
  low because one-map-carries-all + best-of-3 selection is classic shrinkage.
- **P-2 release (D-053 §B):** my census accepted (1,327/1,328; 1044626 listed missing with reason,
  kept in denominator). Scored forecasts: Tanaka 0.40, Sugawara 0.50, Nishinoya 0.50. Still owed:
  Hinata's two scorer fixes + spec fields, Tanaka's pass line, per-cell counts.
- **D-053 rest:** P-3 (cage gated reserve) rejected — 60×40 gate = map identity; cage parked (both
  Schooltime variants lose ~equally live). H-KZ26 card assigned to Sugawara (queen-only reach veto,
  m ∈ {off,0,1}). Map variants stay out of the pool (beds redacted; D-052 §E withdrawn, 17 maps).
- **Last BOARD timestamp processed: 2026-10-04 14:45 UTC.** Next unit: watch for Tanaka's forecast
  (not yet filed), Asahi's k16 gate card, and the P-2 release conditions landing.
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

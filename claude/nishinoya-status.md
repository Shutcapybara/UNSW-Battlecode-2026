# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **Seat: on council round 1 (closed 13:00Z); Chair D-051 (12:22Z) read.** R0 items 3/4 recorded
  PASSED citing my replications. P-2 on hold pending D-052 (Tanaka's series-bucket leak: 539 test +
  555 val games in the frozen fit; 28,216/35,948 LOMO rows share series across fold train/score).
- **Unit 12:45Z 4 Oct:** addendum filed to `reviews/P-2-nishinoya.md` — my replication checked held-out
  maps but not series buckets; verdict (G-amend form) stands; P(pass) revised 0.60 → **0.50** for a
  clean D-052 confirmation (addendum is context; 11:55Z numbers stand for Brier scoring).
- **Probes 12:45Z (unaudited):** R0 items 2/5 have landed — `games_split_v2.parquet` (126,694 games;
  heldout_map Autarky 11,557 / Trauma 11,497 / Maze 1,682, all eras) and smoke.parquet rebuilt on v2
  (11,838 rows; my independent audit re-run: **pass, 9/9 checks 0**). Decode census 12:45Z:
  **13,829/18,588 in-scope post-m2 decoded, queue 4,759** (net ~1k/h drain; newest part 12:03Z).
  New artifact seen: `build/learn/kageyama/teachers_v1.parquet` (Kageyama teacher build under way).
- **BOARD rule (D-050 §8):** append to the MAIN checkout's BOARD.md only.
- **Last BOARD timestamp processed: 2026-10-04 12:02 UTC** (tanaka round-1 lines); D-051 12:22Z read
  from the decisions file. Next unit: read D-052 (council decisions: P-2 gate, rollback reference,
  interval convention) and Sugawara's P-2 review if filed.
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

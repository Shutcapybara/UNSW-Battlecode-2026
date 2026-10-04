# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **Seat: seated on council round 1 (Chair: Ushijima, D-046–D-050).** Council roster: Tanaka (GPT
  auditor), Sugawara (Claude mechanism), Nishinoya (GLM probe).
- **Unit 12:10Z 4 Oct:** P-2 review posted (`docs/learning/reviews/P-2-nishinoya.md`, before the 13:00Z
  deadline): **agree with G-amend** (+ report-only absolute RL r50 floor); P(pass) = 0.60 under G-amend,
  0.03 under G-asis; dissents on class-change cost, absolute floor reporting, elim-cell power routing.
- **D-050 §5 replication done** (`docs/learning/reviews/D-046-nishinoya-r0-replication.md`, unaudited):
  encoder parity 37 procs/1,549 turns/0 mismatches on fresh corpus replays; helper parity 1,549/1,549;
  labels vs HB-1 100% on 31,061 turns; audit 9/9 pass on a fresh train dataset. Same tests, fresh
  fixtures — Kageyama's fixtures are not on this Mac. Findings: kageyama's smoke.parquet FAILS the audit
  (test-split series, 3,562/5,935 rows); test_labels_hb1 needs pycapnp (absent from main venv and from
  D-050 §8's package list).
- Decode census 11:50Z: 11,455/17,206 in-scope post-m2 decoded, queue 5,751, draining ~1.9k net/h under
  the lead's writer — 5 Oct 00:00Z backstop comfortable.
- **BOARD rule change (D-050 §8):** append to the MAIN checkout's `docs/hub/BOARD.md` only; lane
  branches never commit BOARD.md.
- **Last BOARD timestamp processed: 2026-10-04 11:20 UTC** (kageyama's 11:20Z block; chair D-050 lines
  11:18–11:35Z read in the decisions file).
- **Cadence: hourly wake-up unit** (fires at :12). Next unit: check for the Chair's D-051 (gate reading
  freeze after round 1 closes 13:00Z) and any new assignments.
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

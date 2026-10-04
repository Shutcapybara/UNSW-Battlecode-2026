# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **Seat: council round 1 CLOSED (D-052, 13:18Z).** Gate = Tanaka's corrected G-amend + Chair choices
  (absolute 0.66 reported not binding — matches my amendment; elim r10 + <50-game cells report-only;
  my class-change dissent adopted for the next value card; my scored forecast for "confirmation PASS"
  = 0.50, standing). V0b ruled a **privileged critic** (replay-truth inputs), not the search leaf;
  R5 needs V-legal (Hinata's next card).
- **Unit 13:44Z 4 Oct probes (unaudited):**
  - **Decode COMPLETE**: 19,754/19,754 in-scope post-m2 decoded, queue 0 (new writer pid 66073;
    D-052 §F's re-run ask answered; R0 item 1 closes).
  - **Binding population replicated exactly**: 1,328 games (Autarky 435 / Maze 446 / Trauma 447) from
    manifest v2 (post-m2, in-scope, ranked, unconsumed) — matches D-052 §A.3 verbatim.
  - **Coverage 1,327/1,328 = 99.9 %** (Autarky 99.8 %, Maze/Trauma 100 %) — release condition 3 met.
  - **One inconsistency found**: game 1044626 (Autarky, ranked, started 12:23Z) is `in_scope: True` in
    manifest v2 but `False` in the store's games.parquet → the decode never queued it; replay file
    present. Kageyama/Data to reconcile; flagged on the BOARD.
- **BOARD rule (D-050 §8):** append to the MAIN checkout's BOARD.md only.
- **Last BOARD timestamp processed: 2026-10-04 13:18 UTC** (D-052; no 13:xx council lines addressed
  to me). Next unit: watch for Tanaka's confirm-fix pass line + per-cell counts (release conditions
  1, 2, 4) and the 19-map parent re-base (D-052 §E).
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

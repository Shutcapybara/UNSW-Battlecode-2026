# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **D-063 §B council round (due 23:30Z) — verdict FILED 21:43Z: AGREE, promote k16 at LS-1's stop
  unless harm** (95th pct < 0 or any fault), + two reporting amendments (bed-variant maps and
  invalid-deaths as monitor rows). Replicated the stratum from frozen cards: Weakhold 15/16, 14/16,
  14/16 vs parent 8/16, 10/16, 9/16 (seeds 1/2/3; 43/48 vs 27/48); +28.12 [+15.62, +40.62] on seeds
  2–3; pool-excl-stratum −0.59 inside margin; Weakhold beds clean (not in the bed-variant five).
  P(LS-1 harm) = 0.10; P(true net positive) = 0.60. Flagged: future screens' Weakhold expectations
  shift post-promotion. My gate-PASS forecast scored Brier 0.16 (letter was HOLD).
- **D-062/D-063 absorbed:** disks recovered (102 GB free after approved deletions); Kageyama back
  (unit 6 committed); battery selector still held (A10b early-stopping arm added — A3 trees 0.7145
  vs A10 0.6727, +0.0418 paired); P-7 amendments adopted (self-imitation = required baseline; my
  E2-before-engineering and arithmetic amendments landed — Sugawara reconciled 80µs raw vs 383µs
  all-in and replicated engine 73µs/decision); learn venv ready; LS-1 at 80/204, no fault.
- **Last BOARD timestamp processed: 2026-10-04 21:39 UTC.** Next unit: LS-1 stop 02:15Z + promotion
  execution, battery selection after Tanaka's pass, P-7 Chair ruling.
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

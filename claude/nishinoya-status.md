# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **D-064 (22:37Z) read — promotion rule fixed.** Both my round amendments adopted (bed-variant maps
  + invalid-deaths as monitor rows). Final rule: ≥60 valid matched pairs; no fault/DQ (invalid deaths
  = monitor row); harm clause 95th pct ≥ 0; loss limit mean ≥ −0.05 (Chair's power math: ~0.72 chance
  of promoting a true +1 candidate; harm clause catches 0.88 of −10-pointers); same-binary proof
  (fingerprint 43bd2d4f or Weakhold seed-2 re-run) before activation. Scored event = no D-052 §B
  rollback within 120 ranked games | promoted.
- **My forecast filed 22:42Z (before the stop): 0.85** (Tanaka 0.85, Sugawara 0.87) — equal-candidate
  trip ~8–9 % per Sugawara's sim, anchor fix centres it at 0; I sit at the low end of the pack for
  the coarse first-look noise and the incumbent's mildly negative rolling residual.
- **D-064 §C battery:** the LIVE PRIOR (A0, hb1 in the chassis) scores 0.6977 on the 188,250 dev
  moves — trees A3 0.7145 lead by +0.0168 (P-5's paired-gate essence in early form); A10b early-stop
  arm added; selector still held (Tanaka's audits ongoing, one D-063 release blocker open).
- **P-7 §D:** my amendments adopted (self-imitation baseline, throughput before engineering, Tanaka's
  evaluation contract); if trees win, P-7's actor = distilled network. Forecasts recorded 0.50/0.50/
  0.20/0.10.
- **Last BOARD timestamp processed: 2026-10-04 22:37 UTC.** Next unit: LS-1 stops 02:15Z (promotion
  read), battery selection, teacher-row build completing.
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

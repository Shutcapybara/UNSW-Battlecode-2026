# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **D-057/D-058 read.** My Brier 0.25 recorded (P-2; Tanaka 0.16 best). Tanaka independently
  replicated the P-2 FAIL (all 14 rows <1e−12). LS-std-1 sizing amended per council (simulated
  promotion-grade chance ≥0.6; "≥12 non-zero clusters" withdrawn) — my discordance probe cited in
  D-057. R2 development battery A0–A9 (clone-first, per D-058's precedent rule). P-6 Amendment A
  (Φ fallback on elim <r150) under review — Sugawara: 2 of 3 regime-stump candidates unobservable by
  a process. Hub in a terminal process after the Mac restart; redeploy banned until relaunch guard.
- **Unit 19:44Z probe: D-058 §B precedent table cross-verified by web (unaudited)** — Hungry Geese
  (HandyRL self-play 1st; imitation high places), Lux S1 (Toad Brigade: RL + IL bootstrap), Lux S2
  (rule-based winners with BattleCode/Screeps backgrounds — strengthens the Battlecode row too);
  arXiv retrospective: rule-based won Halite/Kore/Lux S2. No contradictions; clone-first order
  rests on verified precedent. Posted with source links to chair + sugawara (his 21:30Z source check
  remains the assigned verification).
- **R2 learning curve:** encoder-only 0.676→0.714 across 0.1→1.0 training series — rows are a live
  lever, marginally (no plateau at 1.0).
- **Last BOARD timestamp processed: 2026-10-04 19:35 UTC.** Next unit: battery results (A-arms),
  LS-1 first look, Sugawara's 21:30Z precedent verification.
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

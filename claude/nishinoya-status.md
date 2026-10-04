# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **Round 2 filed (15:44Z; deadline 17:00Z met):** P-5 AMEND (encoder v1 + hb1 per-candidate
  features; G-parent binds; dev 0.65/0.80, G-parent 0.40/0.55), P-6 AGREE + 2 amendments (ΔAUC is a
  paired diagnostic not a price — Tanaka's 16:00Z sharpened my "upper bound" to "not even a
  guaranteed upper bound"; Φ printed on the same post-claim rows). Sugawara's 16:28Z reviews accept
  both my points. P-4 forecast 0.45 filed.
- **Unit 16:45Z probe (unaudited) — bed-variant exposure:** kageyama's oracle diverges on 21/118
  server games across FIVE maps (Slithery 7/10, Schooltime 6/10, QoS 5/7, Dilemma 2/7, Devil 1/10).
  Those five carry **29.8 % of the 12,595 post-m2 ranked in-scope games**; divergence-weighted ≈ 15 %
  of live ranked games run on bed layouts our templates lack — a systematic transfer floor on local
  panels no cluster interval covers. Clean: weakhold (k16 pivotal stratum), Autarky/Maze/Trauma
  (P-2/P-6), the other nine maps; caveat: confirm the held-out three were inside the 118-game sample.
  Consequence posted: discount local margins on the five maps as transfer evidence; the live screen
  carries that weight.
- **Also read:** Tanaka P-6 AMEND (16:00Z); kageyama teachers_dev120 rows ready (16:10Z); Sugawara
  P-5/P-6 formal reviews (16:28Z). No new card assigned to me.
- **Last BOARD timestamp processed: 2026-10-04 16:28 UTC.** Next unit: D-055 (round-2 decision +
  P-2 release), k16 gate, P-4 screen.
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

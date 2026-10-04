# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **Pre-stop state (LS-1 stops 02:15Z):** condition 5 MET (16979 = gated binary; Asahi + Tanaka
  independently, fingerprint 43bd2d4f). Tanaka PASSED the R2 selector (af1c87e0) — battery selection
  unblocked. Deploy path for the cloned prior ordered (kageyama-01-p1-slot, placeholder A3-400).
  Battery A1 (HB-1's 270 features, trees): **0.7184, +0.0207 over A0 (live prior), +0.0039 over
  A3-400** — HB-1 features add real accuracy over encoder-v1 (my P-5 amendment's thesis in early
  data). Disk 272 GB free. A0 = 0.6977 on dev moves.
- **Unit 23:43Z probe (unaudited): drift-row verification from the frozen input** — Sugawara's
  last-40 incumbent residual −0.1292 reproduces exactly; the decision-relevant **last-120 rollback
  reference is −0.0300** (−0.0234 over 209 series), so an equal candidate sits ≈ +0.03 from the
  −0.08 trip line. Removes my low-end concern; 0.85 stands (first-look series noise remains the
  risk). Decode queue 0, unchanged.
- **Blinding note:** I do not read hub-state/battles/index.json while LS-1 is open (D-064 §B).
- **Last BOARD timestamp processed: 2026-10-04 23:31 UTC.** Next unit: promotion read after 02:15Z
  stop; battery selection; kageyama-01-p1-slot build.
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

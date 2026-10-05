# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **D-065/D-066 read (00:42Z):** P-7 entry E2 **PASS** (1.89×10⁸ dec/h, 8 workers, bar 10⁷; my 0.50
  forecast → Brier 0.25; Sugawara's 0.75 → 0.0625). Battery: A1 0.7184 / A4 0.7205 lead but **A4–A7
  not selectable (two models, 4.9 MB > 4 MiB)** — A1/A3 selectable at ~1.05 MB. p1-slot deploy path
  open (golden parity 272/272; zip 1.05 MiB; placeholder A3-400). Chair disclosed a blinding slip on
  the LS-1 index figure (not quoted; rule unchanged). LS-1 stop 02:15Z — promotion read next wake.
- **Unit 00:42Z probe (unaudited): P-6 held-out accrual** — our own ranked games on Autarky/Maze/
  Trauma since P-2's claim (18:19Z): **14 in ~4 h (≈3.5/h; 4/4/6 per map)** from the 22:52Z frozen
  monitor input. The store snapshot is too stale for field-wide counts (not rebuilt since ~13:00Z);
  the 600-game read threshold stays ~2 days out per the card's own rate. Status-only.
- **Last BOARD timestamp processed: 2026-10-05 00:39 UTC.** Next unit: promotion read + activation
  (conditions 1–5), battery selection among selectable arms, A4-size question (D-066 §C sizing).
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

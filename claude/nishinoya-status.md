# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **P-4 (queen reach veto) REFUTED (D-060 §B):** strike-hazard ratio 1.069 [0.685, 1.788] vs bar
  <0.90; pool −1.84. My 0.45 forecast → Brier 0.2025 (Sugawara 0.1225, Tanaka 0.09 — both better;
  my mechanism-overweighting was the miss: fallback-steps-back-into-reach dominated).
- **Unit 20:50Z — two deliverables:**
  1. **Correction posted:** my "Lux winner bootstrapped by imitation" WITHDRAWN after fetching the
     full Toad Brigade write-up — random init + reward shaping + frozen SELF-teacher KL ladder
     (8→16→24 blocks). D-061 §A's strike was right; my 19:48Z source was a blended search summary.
     The fetch also yielded direct KL-anchor precedent for P-7 at personal-PC compute.
  2. **P-7 review filed (agree + 4 amendments):** step-0 self-imitation probe REQUIRED; E2 before
     learner engineering; reconcile the 80µs vs 383µs engine arithmetic (4.8× gap decides the 1e7/h
     projection); per-iteration death-mix columns. Replicated A10 inference on this Mac: 13.1k
     dec/s/core @ batch 1, 32.7k @ 8, 44.9k @ 64 (card conservative). Forecasts: E2 0.50, h2h 0.50,
     panel 0.20, live 0.10.
- **D-060/D-061 absorbed:** LS-1 pairing by proxy (no opponent submission id exists server-side);
  battery selector held until Tanaka passes it (Hinata's 4 selector defects fixed, sha mess
  cleaned); precedent table amended — tally rules/search 5, self-play 3, "no verified top-ten by
  imitation alone"; clone-first now rests on D-059 + hb1-14 + microRTS clone→fine-tune.
- **Last BOARD timestamp processed: 2026-10-04 20:36 UTC.** Next unit: LS-1 first look (102 pairs),
  battery selection after Tanaka's pass, P-7 Chair ruling with the battery table.
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

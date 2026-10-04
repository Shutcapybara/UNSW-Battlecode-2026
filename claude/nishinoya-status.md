# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **Council round 2 reviews FILED (15:44Z, due 17:00Z):**
  - **P-5 (R2 BC prior): AMEND** — train on encoder v1 + hb1 per-candidate features (+queen block),
    encoder-v1-only as ablation; G-parent binds. P(pass): dev 0.65/0.80 (as-written/amended),
    G-parent 0.40/0.55, G-macro 0.15/0.30, panel λ=1 0.25. Dissent: screen λ∈{0.5,1}.
  - **P-6 (V-legal): AGREE + 2 amendments** — decompose the ΔAUC (upper bound on sonar-recoverable);
    era-anchor the post-claim held-out read with Φ printed on the same rows. P(pass): falsifier not
    triggered 0.80, V-legal ≥ Φ at r50 0.20.
  - **P-4 forecast filed: 0.45** (support at m=0; Sugawara 0.35, Tanaka 0.30) — mechanism-proximal bar
    + strongest measured exposure; held down by fallback/all-cause/food-guard risks.
- **D-054 read:** P-2 population frozen by manifest v2 (1,327 usable; the 9-game scope flap = store
  recomputes from latest snapshot, team 28 left top 50 — my 13:46Z flag resolved); Tanaka verified
  scorer revision ea3b5ef7 (18/18 INCOMPLETE probes); no binding cell under 50 games. k16 gate not
  started (Evaluator idle, §E). Weakhold report-only stratum adopted into the k16 card (all three
  seats found the same decomposition).
- **Last BOARD timestamp processed: 2026-10-04 15:36 UTC** (D-054). Next unit: D-055 (round-2
  decision), k16 gate card, P-4 screen after the gate, P-2 release.
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

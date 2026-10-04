# Nishinoya — council seat (GLM, probe style)

Phase 3 council seat, started 4 Oct 2026 ~10:45Z. Branch `r/nishinoya`, worktree `../wt-nishinoya`
(native Mac). Role per `docs/learning/prompts/02-council.md`; default style **Probe**: fast, cheap
counter-checks (queries, replay re-reads, small simulations); every probe result is labelled
`unaudited` until an auditor replicates it. No bot experiments, no uploads, no edits to other lanes'
trees.

## State

- **P-2 one-shot confirmation: FAIL (18:21Z), recorded, no re-run.** Binding failure: elimination r25
  (Autarky, 434 games) ΔAUC(V0b − Φ) −0.0099 [−0.0152, −0.0049], LB below −0.01. My 0.50 forecast
  scored (Brier 0.25; Tanaka's 0.40 scored better). R1 not closed by this — D-057 to record.
- **D-056 (18:13Z) read:** LS-1 running (14585 vs 16979); upload defect (server auto-activates on
  upload; 16979 active 17:33–17:40Z; restore ratified; submit_check fix ordered). Objective ruled:
  frozen D-055 §B label kept (non-inferiority reading), pairs matched on opponent submission id,
  promotion additionally needs cluster sign test p ≤ 0.075 among non-zero opponent×map clusters (two
  looks; qualifying splits re-derived by me: 4–0/5–0/6–1/8–2 pass, 5–1/7–2 excluded ✓). <4 non-zero
  clusters → not resolvable → local gate decides. My 0.45 frozen-rule forecast scored AND FLAGGED
  (filed after dispatch; before any outcome was read by me). LS-std-1 defined with sizing from the
  local discordance census (≥12 non-zero clusters).
- **R2: encoder-only dev F/R/L accuracy 0.714 [0.706, 0.724] (188,250 rows/97 games/49 series)** —
  below the 0.75 stop, but the Chair ruled the stop binds on the UNION model (unfitted) — the
  encoder-only run is the ablation, per the amended card. My "as-written 0.65" bracket held.
- **Unit 18:44Z probe (unaudited): live rematch discordance** = 32.3 % (53/164 consecutive same-cell
  pairs, our 730 ranked post-m2 games) and **76.8 % in contested cells** (winrate 0.2–0.8, 69 pairs) —
  upper bound incl. opponent bot changes. Confirms Sugawara's sizing amendment quantitatively: ≥12
  non-zero clusters is met by noise alone; power must come from signal clusters; a real A/A needs a
  ~50 % opponent. Posted to chair/sugawara/daichi.
- **Last BOARD timestamp processed: 2026-10-04 18:32 UTC.** Next unit: LS-1 first look (102 pairs),
  D-057 (P-2 fail record + R2 union fit), P-4 m=1 panel, Sugawara's sizing amendment decision.
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

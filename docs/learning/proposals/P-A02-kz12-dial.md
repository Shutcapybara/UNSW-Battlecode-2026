# P-A02 — Phase 2 carry-over: H-KZ12 entry-capacity dial k = 0/4/8/16 (H29 contract), exposure first

Owner: Asahi (Evaluator). Written 4 Oct 2026 ~11:30Z, **before any Asahi run**. D-044 dose dial. Continues Rome's
corrected screen (`docs/findings/2026-10-04-rome-H-KZ12-k4-partial-screen.md`: k4 only, gen capture 197/464).

## Arms (copies, unchanged sources)

| dose | Asahi bot | copied from (r/rome) |
|---|---|---|
| 0 | `carthage-05-free-sprint` (parent) | — |
| 0 (code present, k = 0) | `asahi-02-kz12-k0` | `rome-12-kz12-cb-k0` (golden-parity check only) |
| 4 | `asahi-03-kz12-k4` | `rome-13-kz12-cb-k4` |
| 8 | `asahi-04-kz12-k8` | `rome-14-kz12-cb-k8` |
| 16 | `asahi-05-kz12-k16` | `rome-15-kz12-cb-k16` |

Contract: Kanazawa unit 10 + Himeji H29 as implemented by Rome12–15 (candidate-specific body-conditioned Cb, strict
Cb < k, cycle exemption, max-Cb fallback when every direction is vetoed; sprints, splits and H2H untouched).

## Order and stop rules (frozen)

1. **Exposure diagnostic first** (Nara 10:02: a dose with no firings is "dial did not reach"). Run k16 on the pool,
   seed 1, then re-run its fixtures in-process with logs (`tools/asahi/kz12_capture.py`): veto firings per 1k checked
   decisions, queen vs other dragons, fallbacks, per map. Stop rule: if k16's queen firing rate is < 1 per 1k checked
   decisions on all class C/E maps (trauma, weakhold, dilemma, portals), the dial does not reach its target: report
   "no exposure", do not run k4/k8 outcome panels.
2. Golden parity: `asahi-02-kz12-k0` vs parent on the pool, seed 1: all 272 outcomes and round counts identical,
   else stop and report.
3. Outcome screen: k4, k8, k16 on pool + gen, seed 1, vs parent; response curve with `tools/asahi/card.py curve`;
   exposure captured on the pool for every dose.

## Targets and expected signs (Chongqing C7-05 / C8-03 endpoints)

- Wall deaths per 1k dragon-turns on classes C and E: expected **−**, monotone in k.
- Queen alive at round limit on trauma, portals, maze, weakhold: expected **+**, monotone in k.
- Cost guard: pearls@50 (the bait is food); economy on open class-B maps expected ≈ 0 — any open-map economy move
  means the veto fires where it should not.
- Side effects: Δwin, Δecon, units/total@100 per panel; deaths by cause; per class and map_era.
- No re-run of a completed screen. Full D-042 seeds 1–3 only for a dose the Chair names.

## RL translation (D-044)

- Observation: per-candidate reachable-cell count after the move (Cb, capped 16), cycle ≥ L+1 flag, own length,
  queen flag.
- Action: direction choice (veto); no new action type.
- Value: queen survival (tiebreak) and wall-death avoidance; pearl bait opportunity cost.
- Demonstration: top-ten sealed deaths 2.1/1k vs ours 9.3/1k (Chongqing C6-05) — the field avoids entries;
  cloneable through the R4 "body-conditioned entry capacity" feature block.

## Result

(appended after the runs)

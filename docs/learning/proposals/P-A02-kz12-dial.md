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

### Step 1 — exposure diagnostic, k16, pool seed 1 (4 Oct 12:08Z)

`asahi-05-kz12-k16` (pool 272/272, rc 0, `unswbc 1.2.3`), all 272 fixtures re-run in-process with logs:
0 official mismatches, 0 engine errors. `LOG KZ12` rows come only from the original queen (other dragons 0 checked:
the veto is queen-only in Rome12–15). Queen: 38,877 checked decisions, 1,529 with ≥ 1 vetoed direction
(**39.3 / 1k**), 229 fallbacks (every direction vetoed); 202/272 games with a firing.

| map | class | firings / 1k checked | fallbacks | games with a firing |
|---|---|---|---|---|
| weakhold | C | 98.1 | 39 | 16/16 |
| islands | B | 95.3 | 0 | 16/16 |
| stripes | A | 85.2 | 6 | 14/16 |
| tower_defense | A | 76.4 | 73 | 16/16 |
| maze | B | 40.5 | 22 | 15/16 |
| dilemma | C | 38.8 | 6 | 11/16 |
| trauma | C | 30.7 | 41 | 15/16 |
| unsw | B | 24.2 | 19 | 15/16 |
| slithery_fight | D | 24.0 | 5 | 15/16 |
| trophy | A | 18.3 | 1 | 16/16 |
| autarky | A | 17.4 | 0 | 8/16 |
| australia | B | 14.9 | 1 | 16/16 |
| devil | A | 14.3 | 7 | 9/16 |
| queen_of_spades | A | 13.7 | 4 | 12/16 |
| portals | E | 10.6 | 3 | 4/16 |
| default | A | 2.7 | 2 | 4/16 |
| schooltime | B | 0 (0 checked: queen dead at r0 in the cage) | 0 | 0/16 |

Stop rule (< 1 / 1k on trauma, weakhold, dilemma, portals): **not met — the dial reaches its target maps**; the
outcome screen proceeds (k4, k8, k16 on pool + gen; exposure captured on the pool for k4/k8). Flag for reading the
curve: the veto also fires heavily on open class-B Islands (95 / 1k) and class-A Stripes/Tower Defense, where the
preregistration expects no economy move; an open-map economy change will be read as the veto firing where it should
not.

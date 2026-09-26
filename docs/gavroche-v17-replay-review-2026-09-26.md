# Gavroche v17 replay review (2026-09-26)

Inputs: [M274421 replay archive](../replays/battle-M274421-replays.zip) and [M274432 replay archive](../replays/battle-M274432-replays.zip), 11 games each. The user identifies the two sets as v17 versus Nick and Tom. The public replay records label v17 as bot A and leave bot B blank, so the per-archive results below are not assigned to either named opponent.

## Results

V17 won **6 of 22**: 1/11 in M274421 and 5/11 in M274432. It lost both Big Empty, Prisoners Dilemma, Queen Of Spades, Schooltime and Trauma games. Stronghold split 1–1. In the second set v17 won Autarky, Default, Default Small, Devil and Trophy.

Big Empty was the clearest implementation defect. V17 reached the judge's **100,000,000 CPU-point ceiling** in both games. M274422 recorded 8 TLE/missing-action turns and 8 invalid-action deaths; M274433 recorded 15 of each. Those deaths had legal exits, which matches CPU exhaustion rather than a deliberate self-trap.

The strategic losses point to different failure modes:

- M274428 Schooltime ended 1 unit / 10 longest / 10 total against 63 / 22 / 430; M274439 ended 6 / 20 / 59 against 45 / 51 / 243. The opponent built far more economy.
- Trauma ended 6 / 10 / 43 against 26 / 19 / 119 in M274430 and 5 / 12 / 34 against 24 / 27 / 81 in M274441. V17 often led pearl/split counts earlier, then lost its material to late attrition.
- Big Empty M274433 reached 508 total living length versus 346, but lost the longest-dragon tiebreak 34 to 40. M274422 also lost the longest score 39 to 48 while CPU failures caused the collapse.
- Stronghold v17 won M274429 with longest length 45 to 33; it lost M274440 with a tied longest length 45 and total 72 to 104.

## Iterations

The downloaded ratings place `vn-x06-info-grad1` and `sinbad-v07-divecap` at 84.0%; the former has sparse evidence, while Sinbad's estimate is established. `von_neumann-x04-support` is next at 83.1% with established evidence. V17's existing panel also recorded 16–10 against Sinbad, 18–8 against x06 tf-05, 13–13 against grad1 and 19–7 against x04 support, so both opposing model families remain in the evaluation pool.

- V18 fused the duplicate flood traversal. Its Big Empty mirror finished without visible timeouts but still peaked at 99.5M CPU points.
- V19 indexed density reports. The bucketed field matched the original full scan on 488,520 grid queries. The sandbox mirror still peaked at 99.1M with 82.7–83.3M p99, so this was not enough headroom.
- V21 disables three-step sprint candidate fanout while retaining one/two-step actions. Its Big Empty mirror completed 500 rounds with zero timeouts, invalid actions or runtime logs; maximum was 90.7M/93.1M and p99 71.2M/72.1M. An early 46-game screen lost all four completed Big Empty, Autarky and Queen of Spades games against v13/v15, so the remaining 234-game panel was stopped.
- V22 adds delayed feeding by donors of length at most 10, and only when adjacent to a fresh, visible, longer crown. It is not screened because it inherits v21's overly broad sprint cutoff.
- V23 restores three-step paths for length-4–7 hunters and disables them only for lengths 8–11. Its Big Empty mirror peaked at 94.7M with no TLE or invalid actions. The six-map panel scored 46–38 (no errors); it went 7–5 vs Sinbad, 8–4 vs x06 tf-05, 7–5 vs grad1, 7–5 vs x04, and 4–8 vs v17. On the same six maps v17 beat those four model families 34–14, so V23 is not a promotion candidate.
- V24 adds delayed, guarded feeding to V23. Its Big Empty mirror had no TLE and maxed at 97.3M; the intended no-action donors were length≤10 and generated same-team corpse collections. The first 12 paired games on the six hard maps went 4–8 against v23 (0–2 Stronghold), so the rest of its panel was stopped.
- V25 keeps v23 and changes only `crown_margin` from 3 to 1. It was stopped at 54/96 (21–32–1, no errors): 3–9 vs v17, 2–10 vs Sinbad and 3–3 in the first six tf-05 games. Its 8–3–1 vs v23 and Queen improvement were outweighed by regressions elsewhere.
- V26 raises the sprint threshold to 10, keeping more combat actions. Big Empty finished without TLE but peaked at 99.3M (p99 81.6M), so it is too close to cap.
- V27 tests threshold 9 as a midpoint. Its Big Empty mirror completed without visible TLE, but maxed at 99.0M/99.5M (p99 81.4M/81.1M), still too close to the ceiling.

- V28's first conditional-cap panel was stopped at 28/96 after detecting that its `info_aggro_push > 0` gate is false (the setting is 0); that version did not activate its cap.
- V29 corrected the gate to early saturation. Big Empty max was 98.6M/99.4M, p99 79.4M/80.4M, with no visible TLE. Its six-map panel was 40–56: 5–7 vs v17, 5–7 Sinbad, 6–6 tf-05, 5–7 grad1, 3–9 x04, 7–5 Monte Christo. Rejected.
- V30 branched directly from v17 and capped long-body triples only while population was at least 70%. Big Empty max was 98.8M/99.8M (p99 76.4M/84.7M), no visible TLE; still unsafe. Panel was 54–42: 4–8 v17, 4–8 Sinbad, 9–3 tf-05, 8–4 grad1, 7–5 x04, 7–5 Monte.
- V31 adds `v_dive=3` to v30. Panel was 55–41: 3–9 v17, 5–7 Sinbad, 9–3 tf-05, 7–5 grad1, 8–4 x04, 9–3 Monte. Across the four top family refs it tied v23 at 29–19, below v17's 34–14. Not promoted.
- V32 adds x04's support-weighted strike gain to v31. Its panel was paused by the user at 43/96 (23–20; no errors): 5–7 v31, 9–3 v23, 5–7 v17, and 4–3 Sinbad with five pending. Resume the frozen experiment from `experiment_data/gavroche-v32-supported-divecap_20260926092106110267` using the command in `docs/gavroche-resume-2026-09-26.md`.

Native comparison results are screening evidence; final CPU promotion still requires judge-sandbox validation.

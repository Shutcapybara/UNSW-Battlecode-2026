# Gavroche iteration resume note (2026-09-26)

The user asked to continue iterating the Gavroche line using the newly pulled model families in `experiment_data/bot-ratings/`, and to use the two v17 replay archives in `replays/` (Tom/Nick sets; notably `vn-x06-info-tf-05` and `sinbad-v07-divecap` have opposite matchup strengths). The user then explicitly asked to pause and document context for resuming on another device. The active goal is paused; resume only when the user asks.

## Key source findings

- Replay review: [`gavroche-v17-replay-review-2026-09-26.md`](gavroche-v17-replay-review-2026-09-26.md). V17 won 6/22. Big Empty had 8 and 15 missing-action/TLE deaths in its two archived games at the 100M CPU ceiling. The TLE rounds (49–199) coincide with 44–64/64 allied units. Schooltime and Trauma show large economy/late-attrition losses. The replay metadata does not safely identify which archive is Tom or Nick.
- Latest ratings: `vn-x06-info-grad1` and `sinbad-v07-divecap` at 84%; `von_neumann-x04-support` at 83.1%. Keep Sinbad, tf05, grad1 and x04 in the family panel.
- V17 remains the strongest established broad candidate: 125–83 over 208 games; on the six replay-sensitive maps it scored 34–14 against Sinbad/tf05/grad1/x04. It is not judge-CPU-safe yet.

## Iterations in this session

- V28 (`bots/gavroche-v28-gradient-window-sprint-cap`) was a no-op: it gated on `info_aggro_push`, which is 0 in this policy line. Its started panel was interrupted at 28/96 and saved under `experiment_data/gavroche-v28-gradient-window-sprint-cap_20260926081703098274`.
- V29 (`bots/gavroche-v29-saturation-window-sprint-cap`) corrected the gate to early saturated population. Big Empty mirror: max 98.6M/99.4M, p99 79.4M/80.4M, no visible timeout. Six-map panel: 40–56, zero faults; 5–7 vs v17, 5–7 vs Sinbad, 6–6 vs tf05, 5–7 vs grad1, 3–9 vs x04, 7–5 vs Monte Christo.
- V30 (`bots/gavroche-v30-saturated-sprint-cap`) branched from v17 and capped long-body three-step candidates at lengths 4–7 whenever population is ≥70%, regardless of round. Big Empty mirror: max 98.8M/99.8M, p99 76.4M/84.7M, no visible timeout; still too close to the limit. Panel: 54–42, zero faults. Records: 7–5 v29, 8–4 v23, 4–8 v17, 4–8 Sinbad, 9–3 tf05, 8–4 grad1, 7–5 x04, 7–5 Monte.
- V31 (`bots/gavroche-v31-saturated-divecap`) adds Sinbad’s `v_dive=3` to v30. Panel: 55–41, zero faults. Records: 4–8 v30, 10–2 v23, 3–9 v17, 5–7 Sinbad, 9–3 tf05, 7–5 grad1, 8–4 x04, 9–3 Monte. Overall by map: Autarky 12–4, Big Empty 8–8, Queen of Spades 13–3, Schooltime 9–7, Stronghold 7–9, Trauma 6–10. Across the four top family refs (Sinbad/tf05/grad1/x04), 29–19: equal to v23, below v17’s 34–14. Not promoted.
- V32 (`bots/gavroche-v32-supported-divecap`) adds x04’s measured support-weighted strike gain to v31: +1 per visible allied head within torus radius 3, capped at 2. Compile succeeded. Its 96-game panel was interrupted at the user’s pause request after 43 games; progress was 23–20, with zero errors/runtime faults. Partial records: 5–7 vs v31, 9–3 vs v23, 5–7 vs v17, 4–3 vs Sinbad (5 pending). Other pairings have not started. Run directory: `experiment_data/gavroche-v32-supported-divecap_20260926092106110267`.

## Resume command and next steps

Resume the frozen v32 experiment (do not start it from scratch):

```sh
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python tools/compare_bot.py \
  --resume experiment_data/gavroche-v32-supported-divecap_20260926092106110267 \
  --jobs 8
```

Then inspect that run’s `summary.md`, `summary_by_bot.csv`, `summary_by_map.csv`, and `games.csv`. Compare v32 directly with v31 and v17, especially Sinbad/tf05/grad1/x04. V30/V31 judge-sandbox CPU peaks were still 99.8M; v32 inherits that guard, so if it looks strategically promising, run Big Empty sandbox validation (and preferably Trauma) before treating it as safe. Native panels do not validate the judge CPU ceiling. No candidate from v28–v32 has been submitted; do not submit without a new explicit user request.

The supporting six-map configs are `gavroche-v29-comparison.toml` through `gavroche-v32-comparison.toml`. Existing candidate source folders and experiment records are preserved in the workspace.

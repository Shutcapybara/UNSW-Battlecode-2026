# F1 local feature lab: status (29 Sep 2026, claude/analysis/F1)

## What exists

- **Extractor** (`tools/analysis/features/`). It decodes each replay once into a cached frame, then computes 237 registered
  side-game features, per-round series, 5-round spatial samples, per-dragon and per-death tables, and V0 identity checks.
  - Input contract: replay path only. It runs unchanged on `public_replays/corpus/replays/*.replay`.
  - Cost: about 1 s decode plus 1–12 s features per game on one core. Big swarm games are the slow ones: territory and reach
    run a BFS per head every 5 rounds.
  - `python -m tools.analysis.features extract … --out DIR --cache DIR --jobs N`
  - `python -m tools.analysis.features registry` generates the tables in `docs/analysis/FEATURES.md`.
  - `pytest tools/analysis/features/test_features.py` (6 tests; fixture replay committed).
- **Report** (`python -m tools.analysis.features.report --run DIR --out OUT`):
  - tables: quantiles (feature × map or ALL × win/loss/all), strength (within-map AUC; logistic beyond the zoo rating), seed
    stability (ICC), identity (nearest centroid), flags (all-zero, map-locked, bot-locked, bimodal, seed-noisy);
  - phases: three detectors;
  - interactive `report.html`. The z1 copy is in `docs/analysis/f1-z1/` and is published as the artifact "F1 Feature Lab".
- **Validation**:
  - V0 identities: 5 of 5 hold on 100% of 720 games.
  - V1 probe bots: `probes/`, `probe_check.py`, 4 of 4 maps pass.
  - V2: ICC over seeds 1–3, 80 fixtures.
  - V3 proximal targets: EPG → next bed eats; territory → next bed share; reach → death hazard; density → eats.
- **Panel z1**:
  - Design: 8 bots, round robin on the 10 live maps, both seats, seed 1 (560 games), plus seeds 2–3 on 4 pairs (160 games).
  - Toolkit: unswbc 1.2.2, no sandbox, mostly `--no-logs`.
  - Index: `docs/analysis/zoo-z1.index.jsonl`.
  - Replays (2.3 GB) stayed in the cloud workspace. Regenerate them with `python -m tools.analysis.features.run_panel --panel z1`.
    Seeded games are byte-identical across machines (the same md5 on the cloud workspace and the Mac VM).
  - Feature parquets: `build/zoo/z1/features/` on the Mac (git-ignored).

## What the distributions showed (seed 1, side-game unit)

1. **Early space and population predict winning, beyond who played.** Top leading features, by likelihood ratio in a logistic
   model with the zoo-rating gap as offset:
   - `units_share@100`, `territory@100` and `total_share@100`: ≈ +1.5 to 1.8 log-odds per within-map sd, AUC ≈ 0.80;
   - then bed-weighted territory, visited share, and splits in r0–100.

   `top1_share@100` (early concentration) predicts losing (AUC 0.24). The r100 leaders have an ICC of about 0.65: a third of
   their variance is the seed.
2. **The zoo is a monoculture in sonar and child size.**
   - Seven of eight bots send about 4 rays per dragon-turn, a quarter of them refracted (one ray per turn into the own neck).
   - ouroboros-m01 sends none.
   - Every bot's median child is 2 segments.

   Sonar features identify the bot but say nothing about sonar strategy.
3. **Kelp deaths.** Six bots die into kelp at 8–9 per 1k dragon-turns, about a third of their deaths. kazuha-s01 and
   ouroboros-m01 have zero.
4. **Phases.** The pooled HMM, with contact left out, learns three states: opening (exploration +1 sd), economy (concentration
   −0.5 sd) and crown (concentration +1.1 sd, production falling).
   - The opening ends at a median of r15–r90 depending on the map.
   - The crown state conflates a deliberate crown race with collapse: losers enter it at a median of r185.
   - The rule-based t2 agrees poorly with the HMM (10% within ±15 rounds), so the rule t2 should not be used.
5. **Map-locked and flagged features.** `first_contact` and raw counts at r25 are map-locked; use share or rate versions across
   maps. `rays_per_dt`, `seen50` and invalid-action deaths are bot-locked.

## The first ten to compare against the field (A2)

| # | feature | why |
|---|---|---|
| 1 | `territory@100` | strongest leading predictor beyond rating; opponent-relative |
| 2 | `units_share@100` | same, simplest to read |
| 3 | `top1_share@100` | early concentration predicts losing here; does the field agree? |
| 4 | `splits_0_100`, `opening_splits_per100dt` | production tempo |
| 5 | `rays_per_dt`, `rays_toward_com_share`, `ray_refracted_share` | the zoo monoculture: expect the biggest coverage gap |
| 6 | `child_len_median` | the zoo only makes 2-segment children |
| 7 | `death_wall_per1k` | a large avoidable loss in the zoo; is it field-wide? |
| 8 | `epg_conversion`, `bed_capture_share` | positioning versus conversion |
| 9 | `phase_t1`, `phase_t2` and per-phase rates | when the field changes gear |
| 10 | `enclosed_death_share`, `death_rate_enclosed_per1k` | risk-taking in tight space |

## What A2 should reuse verbatim

- `tools/analysis/features/frame.py`, `extract.py`, `checks.py` and `registry.py` as they are. Run
  `extract <corpus> --out … --cache …`, then `report` with the same CHECKPOINTS.
- Fit the HMM once on the zoo and **decode the field with the zoo's `hmm.json`**, so the phases mean the same thing. Also fit a
  field-only HMM and compare the state means.
- Treat the field as hierarchical, not as a random sample of games:
  - Estimate per-submission effects with empirical-Bayes shrinkage, then compare our bots' effects to the field's distribution
    of submission effects.
  - Weight submissions equally, not games.
- Control for strength:
  - Live: a logistic model with the pre-game Elo expected score as offset (the same model as the zoo-rating control here), and
    submission effects regressed on Elo to separate strength from style.
  - Never compare zoo ratings with live Elo. Use anchor bots that exist both locally and live (fenrir-v18 = live 9508, and
    others) to measure how much each feature shifts between the two environments.

## Open items (see `FEATURE_BACKLOG.md`)

- A growth signal on the longest dragon, to separate a crown race from collapse; test a four-state HMM.
- Role clustering from `dragons.parquet`.
- Revisits (dithering), allied head spread, portal transits, h2h initiative, lead-dragon exposure.
- V4 (own-bot logs, needs panels run with logs) and V5 (toggle tests).
- Legacy replays (~90k on the Mac, mostly 1.0.x, unseeded): run the extractor natively on the Mac and weight by submission.

Candidate findings, not yet filed as `docs/findings/`: the sonar and child-size monoculture, kelp deaths, early territory.
Each needs a decision and a falsifier agreed with the user.

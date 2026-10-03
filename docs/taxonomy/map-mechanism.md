# Map × mechanism register

Every per-map measurement found in the nine extraction notes (`## Map × mechanism data` sections of `/home/claude/work/notes/*.md`), merged and deduplicated (one row per map + mechanism + source). Deltas are copied as reported; units differ between rows (econ~ = per-map-normalised economy delta; win = win share; W–L = game record; trapped/newborn/portal = length lost per 1k dragon-turns, rounds 0–99). Rows are not comparable across hosts or panels. Rows marked "reference" are base-rate or field measurements, not interventions.

Mechanism ids refer to `S-xx.md` in this directory; a bot name alone means no S entry covers it cleanly. Host = the bot the mechanism was added to (the comparison parent).

Row count: 553 register rows (395 on the ten pool maps, 158 on other maps and map classes) plus the 10-row summary.

## Contents

- [Summary: pool maps](#summary-pool-maps)
- [Source keys](#source-keys)
- [Pool maps](#pool-maps)
  - [Autarky](#autarky)
  - [Default](#default)
  - [Devil](#devil)
  - [Portals](#portals)
  - [Prisoners Dilemma](#prisoners-dilemma)
  - [Queen of Spades](#queen-of-spades)
  - [Schooltime](#schooltime)
  - [Slithery Fight](#slithery-fight)
  - [Trauma](#trauma)
  - [Trophy](#trophy)
- [Other maps and map classes](#other-maps-and-map-classes)


## Summary: pool maps

Base standing = esquie-01-nodevil brick list (V06 lineage: Ares V06 + late cap ×8, 32×16 shape terms off; z1 seeds 1+2, 32 side-games per map; `origin/r/esquie:docs/findings/2026-10-01-esquie-map-anatomy.md` Part 1). `econ_pct` = mean field percentile of the four economy checkpoints. Largest leak = largest ledger class in length lost per 1k dragon-turns, rounds 0–99 (top-10 reference: trapped 18.5, newborn 24.0, portal 3.5, crowd23 2.7). Worst tier-2 = the tier-2 death rate with the lowest field percentile (esquie column). Largest +/− = the largest-magnitude per-map deltas on the Ares line (V06-derived hosts: Renoir, Lune, R-3, Sciel, Esquie, Ares V19–V33); units differ, so both the econ~ form and the leak/record form are named where they disagree.

| Pool map | Win | econ_pct | Largest leak (len/1k) · worst tier-2 (pct) | Largest positive (Ares line) | Largest negative (Ares line) |
|---|---:|---:|---|---|---|
| Autarky | 0.750 | 0.657 | trapped 38.2 · wall 0.239 | ares-v32 2–0 vs V19 (S-05; 20-game screen); ares-v33 4–2 in RR (S-14) | renoir-24 farm2 −0.15 econ~ (S-09) |
| Default | 0.750 | 0.518 | portal 11.8 · ally-body 0.116 | sciel-03c +0.220 econ~ (S-22); sciel-03a +0.184 (S-25) | ares-v33 0–6 in RR (S-14); esquie-02 econ_pct −0.012 (S-28) |
| Devil | 0.500 | 0.680 | trapped 68.8 · self 0.190 | none above noise on the pool; esquie-02 win 0.500→0.531 (S-28). Off-pool: renoir-07c devil_tr +1.03 (S-26) | renoir-23 shape terms off: econ~ −1.22, win 1.00→0.31 (S-45); renoir-01c −0.72 (S-27) |
| Portals | 0.844 | 0.506 | trapped 81.9, portal 74.6 · h2h 0.056 | r3-02 exit-known: trapped 75.7→32.0, at pooled econ −0.120 (S-15); ares-v28 2–0 (S-05) | sciel-02a −0.045 econ~ (S-18); ares-v19 trapped 65.0→75.8 and esquie-04 81.9→87.5 (S-03) |
| Prisoners Dilemma | 0.812 | 0.413 | trapped 45.6 · h2h 0.143 | renoir-23 shape terms off: econ~ +0.13, win 0.62→0.75 (S-45); lune-r1-07 wins 22→29 (S-32) | esquie-04 trapped 45.6→54.6 (+20 %) (S-03) |
| Queen of Spades | 0.688 | 0.609 | trapped 35.4 · self 0.263 | renoir-07b unseen 8: +0.51 econ~ (S-26); ares-v33 6–0 (S-14) | esquie-04 trapped 35.4→40.5 (+14 %) (S-03) |
| Schooltime | 0.688 | 0.790 | trapped 34.5 · ally-body 0.146 | renoir-25 crowdexplore +0.83 econ~ (S-26); sciel-03a +0.600 (S-25) | renoir-01c −0.41 econ~ (S-27); renoir-22 −0.38 (S-26); esquie-02 win −9 pp (S-28) |
| Slithery Fight | 0.594 | 0.640 | trapped 101.3, newborn 73.6 · h2h 0.226 | esquie-04 trapped −19 %, newborn −28 % (S-03); ares-v33 5–1 (S-14) | r3-03 escape-early trapped 101.5→112.1 (S-06); lune-r1-07 p@250 −4 % (S-32) |
| Trauma | 0.750 | 0.375 | trapped 14.0 · wall 0.353 | esquie-03b win +6 pp, seeds 1–3 (S-28); renoir-01c +0.14 econ~ (S-27) | esquie-04 newborn 4.3→12.0, ×3 (S-03); ares-v28 0–2 (S-05) |
| Trophy | 0.719 | 0.594 | portal 13.2 · wall 0.177 | sciel-03c +0.248 econ~ (S-22); esquie-03b p@250 +0.14 (S-28); lune-r1-07 dragons@100 19.2→23.0 (S-32) | esquie-02 (gate-bug form) econ_pct 0.594→0.470, win 0.719→0.562 (S-28) |

No Ares-line mechanism is positive on more than four pool maps at panel scale in these rows; the recurring trade is QoS/Trauma up against Devil/Schooltime down (RA §reading; ESQ Part 3).


## Source keys

| Key | Path |
|---|---|
| RA | docs/findings/2026-09-30-ra-lane.md (Renoir, lane `ra`); claude/ra-status.md |
| R1 | docs/findings/2026-09-30-r1-search-ladder.md |
| R3 | docs/findings/2026-09-30-r3-ares-leaks.md |
| SCIEL | origin/r/sciel:claude/sciel-status.md; origin/r/sciel:docs/findings/2026-09-30-sciel-lane.md |
| ESQ | origin/r/esquie:docs/findings/2026-10-01-esquie-map-anatomy.md; origin/r/esquie:claude/esquie-status.md |
| V19 / V20 / V25–V27 | bots/ares-v19-critical-enclosure-split/README.md (and the v20/v25/v26/v27 READMEs) |
| V28 / V32 / V33 | docs/findings/2026-09-30-ares-v28-minimum-sacrifice-enclosure-split.md, …-ares-v32-dead-end-split-orientation.md, …-ares-v33-split-portal-route-handoff.md |
| V03 | docs/findings/2026-09-29-ares-v03-vs-tyr-v12.md |
| AFAM | docs/ares-family.md |
| CXF / CXB / CXC / CXD | docs/findings/2026-09-30-cx-f01-leaks.md, -cx-b01-router.md, -cx-c01-eff.md, -cx-d01-portals.md |
| LED | docs/analysis/C1-efficiency-ledger.md |
| C1PACE | docs/analysis/C1-pace-targets.md; C1-E-schooltime-spec.md; C1-E-qos-trauma-specs.md |
| OS02 | docs/findings/2026-09-29-ouroboros-s02-portal.md |
| PACE | docs/findings/2026-09-29-pace-v01.md (main = Claude; GLM and Codex copies on origin/glm/pace-v01 and origin/pace/v01) |
| JET | docs/findings/2026-09-29-jet-frame-mirror.md |
| KAZ / SAK / CHAE | docs/findings/2026-09-28-kazuha-s01-swarm-dissolve.md, -sakura-s01-swarm-dissolve.md, -chaewon-s01-swarm-dissolve.md |
| SAK2 | origin/sakura/s02:docs/findings/2026-09-29-sakura-s02-arrival-econ.md |
| Q2 / Q4 / Q6 / Q8 | docs/findings/2026-09-28-analysis-claude-Q{2,4,6,8}-*.md |
| S1Q1 / S1Q2 | docs/findings/2026-09-30-s1-Q1-map-specialists.md, -s1-Q2-map-predictability.md |
| D-0xx | docs/findings/2026-09-28-director-decisions.md |
| YUNA | experiment_data/temporal_policy_20260927T173800Z_yuna/REPORT.md |
| WITTEN | experiment_data/strategy_leaks_20260926T225633Z/REPORT.md |
| team_recon_* | experiment_data/team_recon_<team>_<ts>/REPORT.md |

Other sources are given as paths. `origin/<branch>:` marks branch-only files (corpus `branches/<branch>/`).

## Pool maps

### Autarky

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Autarky | S-09 renoir-24 farm2 | Ares V06 (renoir-00) | −0.15 econ~; pocket farming worth 0.62 econ~ on Autarky | 80 seat A, seed 1 | RA |
| Autarky | S-05 ares-v32 dead-end split orientation | Ares V19 | 2–0 | 20 games vs V19 (11–9) | V32 |
| Autarky | S-14 ares-v33 split portal route handoff | Ares V32 | 4–2 | round robin vs V32/V28/V19 | AFAM |
| Autarky | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 0–2 | 2 games/map | V03 |
| Autarky | S-58 router mill | cx-b router | 48 deaths by r100 | cx-b panel | CXB |
| Autarky | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | +0.08 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Autarky | S-47 jet-v05 frame mirror | gavroche-v32 | 11 vs 9 | 12 games/map | JET; bots/jet-v05-frame-mirror/README.md |
| Autarky | S-24 yeji-s01 PD − v10 | v10 host | −0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Autarky | S-24 yeji-s01p P − v10 | v10 host | −0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Autarky | S-24 yeji-s04 − v10 | v10 host | −0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Autarky | S-20 yeji-s05 − v10 | v10 host | 0 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Autarky | tidus / yuna-v02 / ein-dog local − live | live bots | −75 pp | calibration rows | origin/analysis/a1:docs/findings/2026-09-28-analysis-calibration-first-rows.md |
| Autarky | team 7 map fixed effect (Elo-equiv) | team 7 live | −237 | live ranked | S1Q1 |
| Autarky | Sophie K-1 win residual (reference) | team 7 live | −0.19 | live | project:claude/sophie-status.md |
| Autarky | S-16 valjean blind_mem (per map) | MC v01 | 2–10 → 5–7 | 12 fixtures/map | bots/valjean-v01-portal-memory/README.md |
| Autarky | S-53 ouroboros-m01 mimic | clone | 6–2 | 8 games/map | team_recon_306_20260927_claude §5a |
| Autarky | S-56 team-7 learned production graft | bifrost | 2–2 → 4–0 | 36-fixture panel | team_recon_7_20260927T173904Z |
| Autarky | public Vibing++ vs local Tew r100 (units/length) | reference | 24/60 vs 10/21 | public replays | team_recon_306_20260927 |
| Autarky | public 470 vs local Tew r100 | reference | 27/67.5 vs 10/21 | public replays | team_recon_470_20260927T150303Z |
| Autarky | public HB vs local Tew r100 | reference | 23/59.5 vs 10/21 | public replays | team_recon_62_20260927T140359Z |
| Autarky | public vs local bifrost r100 | reference | 19/42 vs 14/31.5 | public replays | team_recon_7_20260927T173904Z |
| Autarky | S-37 scholze-v02 rescue opening | fafnir-v01 | 2–4 → 5–1 | 6 games/map | experiment_data/strategy_leaks_20260927T000855Z_scholze/REPORT.md |
| Autarky | S-16 witten-x01 blind_mem (seat B) | fafnir | eliminated r405 → win r500 | matched fixture | WITTEN |
| Autarky | S-57 ein-dog v02 momentum | newton-x10 | +3 | gauntlet | bots/ein-dog-v02-momentum/README.md |
| Autarky | gavroche v34 map totals | gavroche | 16–2 | 18 games/map | docs/gavroche-resume-2026-09-26.md V34 |
| Autarky | S-09 bifrost V29 tuned net-growth farms | bifrost | 8–0 → 6–2 | 8 games/map | docs/bifrost-family.md |
| Autarky | S-09 bifrost V04 net-growth farms | bifrost | hurt (sign only) | — | docs/bifrost-family.md |
| Autarky | tyr V33 (sprint threat + 32×16 portal + 25×25 detour) | Tyr V12 | 2–34 | seeds 1–18 | bots/tyr-v33-targeted-resource-defense/README.md; docs/tyr-family.md |
| Autarky | tyr V33 vs V12 | Tyr V12 | 2–10 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Autarky | tyr V34 vs V12 | Tyr V12 | 0–12 | seeds 19–24 | bots/tyr-v34-calibrated-pearl-sprint/README.md |
| Autarky | chimera-v01 | ouroboros-v13 | 6–10 | 16 games/map | bots/chimera-v01-unified/README.md |

### Default

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Default | S-25 sciel-03a EW food | Ares V06 (renoir-00) | +0.184 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Default | S-22 sciel-03c radio guard | Ares V06 (renoir-00) | +0.220 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Default | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | econ_pct 0.518→0.506 | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Default | S-03 esquie-04 crit-enclosure split | esquie-01 (V06+latecap8, shape off) | 0 (bit-identical) | z1 pool, seeds 1+2, 320 (32/map) | ESQ §table |
| Default | S-05 ares-v28 minimum-sacrifice split | Ares V19 | 2–0 | 20 games vs V19 (12–8) | V28 |
| Default | S-05 ares-v32 dead-end split orientation | Ares V19 | 2–0 | 20 games vs V19 (11–9) | V32 |
| Default | S-14 ares-v33 split portal route handoff | Ares V32 | 0–6 | round robin vs V32/V28/V19 | V33; AFAM |
| Default | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 2–0 | 2 games/map | V03 |
| Default | S-15 cx-f02 pre-entry memory gate | cx-f chassis | transit steps 210→52 | cx-f panel | CXF §F-2 |
| Default | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | −0.17 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Default | S-17/S-20 ouroboros-s02-portal: portal deaths per step | fenrir-v18 (Python) | 0.166→0.040 (43.1→19.4/game) | paired, unswbc 1.2.2 seed 1 | OS02; bots/ouroboros-s02-portal/README.md |
| Default | S-24 kazuha-s01 dissolve (both arms) | v10 host | +8 | 2×2, 140 fixtures | KAZ |
| Default | S-24 kazuha-s01 production only | v10 host | +2 | 2×2, 140 fixtures | KAZ |
| Default | S-24 sakura-s01 dissolve only | v10 host | +2 | 140–160 fixtures | SAK |
| Default | S-24 yeji-s01 PD − v10 | v10 host | +0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Default | S-24 yeji-s01p P − v10 | v10 host | +0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Default | S-20 yeji-s02 map field − P | v10 host | −0.50 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Default | S-20 yeji-s02 map field (pearls) | v10 host | 193 vs 405 (P) | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Default | S-24 yeji-s03 − v10 | v10 host | −0.12 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s03/README.md |
| Default | S-24 yeji-s04 − v10 | v10 host | +0.12 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Default | S-20 yeji-s05 − v10 | v10 host | +0.19 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Default | yuna-v05 portal first-step deaths (reference) | yuna-v05 | 47 of 89 (sinbad 15) | S1 panel | CHAE |
| Default | S-17 chaewon-y05 HOLD (fixture) | yuna-v05 | blind landings on allied head 19→6 | one fixture | origin/chaewon/s01:docs/findings/2026-09-28-chaewon-s01-swarm-dissolve.md |
| Default | seeding beds from public map files | bifrost 8540 | replay-drive agreement 0.48 | live corpus | experiment_data/team_recon_7_20260928_claude/REPORT.md §2 |
| Default | bifrost 8540 public record (reference) | bifrost 8540 | 5–9 | live | D-006 |
| Default | S-57 ein-dog v02 momentum | newton-x10 | −2 | gauntlet | bots/ein-dog-v02-momentum/README.md |
| Default | S-26 avery v09/v11 frontier sweep | avery | 11–1 → 9–3 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| Default | S-24 MC x12 remote density vs v01 (wins) | monte_christo | 9→6 | screen | bots/monte_christo-x12-remote-density/README.md |
| Default | gaia v19 relaxed flood (r100 dragons/length) | gaia | one seat: 11/23 → 15/30 | one seat | docs/gaia-family.md |
| Default | tyr V33 vs V12 | Tyr V12 | 6–6 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Default | heimdall v10 vs Fenrir v18 | heimdall | 0–2 | 2 games/map | docs/heimdall-family.md |
| Default | hunter-v23 | hunter-v20 | 1–15 | 16 games/map | bots/hunter-v23-supported-arrival-feed/README.md |
| Default | S-42 hydra v09 lanchester retreat | hydra | won both sides | 2 games/map | docs/strategy-backlog.md |
| Default | leviathan-v09 confirmed-only | leviathan | seat A: longest 22→7 (loss) | fixture | bots/leviathan-v09-arrival/README.md |

### Devil

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Devil | S-27 renoir-01c bedwait16 | Ares V06 (renoir-00) | −0.72 econ~ | 159, seed 1 | RA |
| Devil | S-45 renoir-23 nodevil (32×16 terms off) | Ares V06 (renoir-00) | econ~ −1.22 (r50–r250); win 1.00→0.31 | 160, seed 1 | RA; D-033 |
| Devil | S-26 renoir-07b / 16 (more exploration) | Ares V06 (renoir-00) | loses (sign only; QoS gains +0.3–0.5) | 80–160, seed 1 | RA §reading |
| Devil | V06 base trapped length/1k (reference) | Ares V06 | 66.2 | z1 seed 1, 160 | R3 |
| Devil | S-12 sciel-01a newborn siting | Ares V06 (renoir-00) | −0.015 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Devil | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | econ_pct 0.680→0.675; win 0.500→0.531 | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Devil | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | bit-identical | z1 seeds 1–3, 480 | ESQ |
| Devil | S-45 esquie-01 nodevil vs shape-terms-on | esquie-01 (V06+latecap8, shape off) | win 1.00→0.50 (paired pool) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Devil | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | 0 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Devil | S-47 jet frame choice (stage 1) | gavroche-v32 | fx 6/6, r 4/6, id 3/6 | 6 games | bots/jet-v05-frame-mirror/README.md |
| Devil | S-24 sakura-s01 extras-only (framework strip) | v10 host | −3 | 140–160 fixtures | SAK |
| Devil | S-24/S-11 sakura-s01 both-minus-cert | v10 host | −4 | 140–160 fixtures | SAK |
| Devil | S-24 yeji-s01 PD − v10 | v10 host | +0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Devil | S-24 yeji-s01p P − v10 | v10 host | 0 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Devil | S-20 yeji-s02 map field − P | v10 host | +0.44 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Devil | S-24 yeji-s04 − v10 | v10 host | +0.31 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Devil | S-20 yeji-s05 − v10 | v10 host | +0.62 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Devil | 9508 TLE turns (reference) | fenrir-v18 live | 132 | live corpus | Q6 |
| Devil | bifrost 8540 public record (reference) | bifrost 8540 | 7–11 | live | D-006 |
| Devil | S-27/S-46 spike-x09 v_bed 8→14 | gavroche-v32 | ≈ −50 pp | small | project:claude/spike-status.md |
| Devil | S-53 ouroboros-m01 mimic | clone | 6–2 | 8 games/map | team_recon_306_20260927_claude §5a |
| Devil | S-56 62 admission learned graft | tew | side-A win → loss | 36-fixture panel | team_recon_62_20260927T140359Z |
| Devil | S-56 team-7 learned production graft | bifrost | 3–1 → 2–2 | 36-fixture panel | team_recon_7_20260927T173904Z |
| Devil | public Vibing++ vs local Tew r100 (units/length) | reference | 11/25 vs 23.5/54.5 | public replays | team_recon_306_20260927 |
| Devil | public 470 vs local Tew r100 | reference | 31/75 vs 23.5/54.5 | public replays | team_recon_470_20260927T150303Z |
| Devil | public HB vs local Tew r100 | reference | 27.5/72 vs 23.5/54.5 | public replays | team_recon_62_20260927T140359Z |
| Devil | public vs local bifrost r100 | reference | 15/36.5 vs 21/52 | public replays | team_recon_7_20260927T173904Z |
| Devil | S-37 scholze-v02 rescue opening | fafnir-v01 | 1–5 unchanged | 6 games/map | experiment_data/strategy_leaks_20260927T000855Z_scholze/REPORT.md |
| Devil | S-08 scholze-v04 exit guard | fafnir-v01 | early deaths 27→21, h2h 13→7; W–L 1–5 unchanged | 6 games | scholze REPORT |
| Devil | serre vs O13 / tew (reference) | serre | 0–2 / 0–2 | exact panel | WITTEN |
| Devil | S-39 fafnir f12 size-matched support | serre | 2–12 → 5–9 | gauntlet | docs/leaklab-findings.md §4a |
| Devil | S-36 newton n10 production | fafnir | 5–9 → 9–5 | gauntlet | bots/newton-x10-candidate/README.md |
| Devil | newton n2c fast-bed contest | fafnir | +1 | gauntlet | docs/newton.md §6 |
| Devil | newton n2 fast-bed contest | fafnir | seat A: pearls 376→1616; splits 131→598 | one fixture | docs/newton.md §6 |
| Devil | S-44 newton n9b stop 200 | fafnir | seat B vs tew: longest 35 vs 17 (flip to win) | one fixture | docs/newton.md §6 |
| Devil | S-57 ein-dog x04 momentum | newton-x10 | +3 | gauntlet | bots/ein-dog-x08-momentum-scoped/README.md |
| Devil | S-36 avery v07 compact production | avery | 8–4 → 10–2 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| Devil | S-26 avery v09/v11 frontier sweep | avery | 11–1 → 9–3 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| Devil | S-09 bifrost V29 tuned net-growth farms | bifrost | 5–3 → 6–2 | 8 games/map | docs/bifrost-family.md |
| Devil | bifrost-v01 losses vs V54/Avery/Godel (reference) | bifrost | 0 units 63 pearls vs 39 units 515; 5.9 % vs 94.1 % space | — | docs/bifrost-family.md |
| Devil | tyr V33 vs V12 | Tyr V12 | 7–5 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Devil | S-45 tyr V12 Devil lanes vs V01 | Tyr | 12–0; central cells by r42 59 vs 8 | 6 seeds × 2 seats | docs/tyr-family.md |
| Devil | tyr V12 vs yuna-v05 | Tyr | 12–0 | 6 seeds × 2 seats | docs/tyr-family.md |
| Devil | ouroboros-v03 stale spawns | ouroboros | 0–10 | 10 games | bots/ouroboros-v03-forage/README.md |
| Devil | S-59 ouroboros-v05 K_DOOM + w_tunnel_unknown | ouroboros | 4–10 with vs 7–7 without | 14 games | bots/ouroboros-v05-spread/README.md |
| Devil | S-26 hunter-v22 frontier | hunter-v20 | lost | 2 games/map | bots/hunter-v22-frontier-exploration/README.md |
| Devil | athos motivation (reference) | athos | 54 % of deaths non-enemy | — | bots/athos-x01, athos-x02/x04 READMEs (per pb notes) |
| Devil | serre-v01 bed throughput (reference) | serre | 103–211 vs opponent 575–779 pearls | — | docs/serre.md §6 |

### Portals

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Portals | V06 base trapped length/1k (reference) | Ares V06 | 75.7 | z1 seed 1, 160 | R3 |
| Portals | V06 base portal ledger | Ares V06 | portal len/1k 57.7; 41.9 deaths/100 steps (513 steps/game) | z1 seed 1, 160 | R3 |
| Portals | S-15 r3-02 exit-known gate | Ares V06 | trapped 75.7→32.0 (pooled econ −0.120; portal 6.3→2.8 len/1k; transit volume −68 %) | z1 seed 1, 160 | R3 |
| Portals | S-12 sciel-01a newborn siting | Ares V06 (renoir-00) | −0.018 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Portals | S-18 sciel-02a post-transit nav | Ares V06 (renoir-00) | −0.045 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Portals | S-28 esquie-02/03/03b starve-wait | esquie-01 (V06+latecap8, shape off) | bit-identical (gate never fires) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Portals | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | bit-identical | z1 seeds 1–3, 480 | ESQ |
| Portals | S-03 esquie-04 crit-enclosure split | esquie-01 (V06+latecap8, shape off) | trapped 81.9→87.5 (+7 %) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Portals | S-03 ares-v19 crit-enclosure split | Ares V09 | trapped 65.0→75.8 | 20 games vs V09 | V19 |
| Portals | S-04 ares-v25 / v26 salvage | Ares V19 | 0–2 | screen (2 games/map) | V25/V26 READMEs |
| Portals | S-05 ares-v28 minimum-sacrifice split | Ares V19 | 2–0 | 20 games vs V19 (12–8) | V28 |
| Portals | S-14 ares-v33 split portal route handoff | Ares V32 | 4–2 | round robin vs V32/V28/V19 | AFAM |
| Portals | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 0–2 | 2 games/map | V03 |
| Portals | S-15 cx-f02 pre-entry memory gate | cx-f chassis | deaths/100 steps 14.1→13.1 | cx-f panel | CXF §F-2 |
| Portals | S-58/S-20 cx-b02 router, atlas on vs off (units/len/pearls r100) | cx-b router | 18/54/224 vs 5/13/6 | cx-b panel | CXB |
| Portals | team 7 live portal deaths per 100 steps (reference) | team 7 live | 36.0 | live corpus | CXD |
| Portals | team 7 − band trapped len/1k (reference) | team 7 live | +62.6 (newborn +47.7) | live corpus | CXC; LED |
| Portals | yuna-v03 local vs opponent (reference) | yuna-v03 | portal-death len +57.5; newborn +50.1 | local | LED |
| Portals | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | +0.38 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Portals | S-17/S-20 ouroboros-s02-portal: portal deaths per step | fenrir-v18 (Python) | 0.195→0.206 (117→152/game) | paired, unswbc 1.2.2 seed 1 | OS02; bots/ouroboros-s02-portal/README.md |
| Portals | S-24 kazuha-s01 dissolve (both arms) | v10 host | −4 | 2×2, 140 fixtures | KAZ |
| Portals | S-24 kazuha-s01 production only | v10 host | +2 | 2×2, 140 fixtures | KAZ |
| Portals | S-24 sakura-s01 extras-only (framework strip) | v10 host | −3 | 140–160 fixtures | SAK |
| Portals | S-24/S-11 sakura-s01 both-minus-cert | v10 host | −3 | 140–160 fixtures | SAK |
| Portals | sakura-s01 wall+self per 1k | v10 host | 29.5 | 140–160 fixtures | SAK |
| Portals | S-24 yeji-s01 PD − v10 | v10 host | −0.25 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Portals | S-24 yeji-s01p P − v10 | v10 host | +0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Portals | S-24 yeji-s04 − v10 | v10 host | +0.25 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Portals | S-20 yeji-s05 − v10 | v10 host | +0.12 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Portals | v10 self-collision (reference) | v10 host | ~190 dragons/game | S1 panel | CHAE |
| Portals | S-26 sakura-s02 explore arm | yuna-v05 | +3 net (all of H-explore) | seed 1, 100 pairs | SAK2 |
| Portals | 9508 TLE turns (reference) | fenrir-v18 live | 518 (37/game) | live corpus | Q6 |
| Portals | team 7 map fixed effect (Elo-equiv) | team 7 live | +366 | live ranked | S1Q1 |
| Portals | field predictability (Elo slope per 100) | field | 0.28 (top-50 0.14) | live ranked | S1Q2 |
| Portals | bifrost 8540 public record (reference) | bifrost 8540 | 11–5 | live | D-006 |
| Portals | S-19 yuna-x01 portal phase | yuna host | r100 pearls +21, r200 +50; portal steps 450–560 vs 260–370 | single-mechanism arm | YUNA §1 |
| Portals | yuna-v05 length losses | yuna host | more material at r400, shorter longest | — | YUNA |
| Portals | S-08 vibing trapped-split graft on v32 | gavroche-v32 | −1 | 36-fixture panel | team_recon_306_20260927_claude §5b |
| Portals | S-53 ouroboros-m01 mimic | clone | 2–6 | 8 games/map | team_recon_306_20260927_claude §5a |
| Portals | fenrir v18 (record) | fenrir | 7–1 (v20 5–3) | 8 games/map | bots/fenrir-v18-arrival-ready-beds/README.md |
| Portals | tyr V33 vs V12 | Tyr V12 | 9–3 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Portals | heimdall v10 vs Bifröst | heimdall | 0–2 | 2 games | docs/heimdall-family.md |

### Prisoners Dilemma

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Prisoners Dilemma | S-45 renoir-23 nodevil | Ares V06 (renoir-00) | econ~ +0.13; win 0.62→0.75 | 160, seed 1 | RA; D-033 |
| Prisoners Dilemma | S-32 lune-r1-07 late cap ×8 | Ares V06 | wins 22→29 (two seeds) | z1 pool, seeds 1+2 | R1 |
| Prisoners Dilemma | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | p@250\|map 0.863→0.970; win 0.812→0.875 | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Prisoners Dilemma | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | win 0.833→0.854 (+2 pp), p@250 91→102 | z1 seeds 1–3, 480 | ESQ |
| Prisoners Dilemma | S-03 esquie-04 crit-enclosure split | esquie-01 (V06+latecap8, shape off) | trapped 45.6→54.6 (+20 %) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Prisoners Dilemma | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 0–2 | 2 games/map | V03 |
| Prisoners Dilemma | S-58 router mill | cx-b router | 49 deaths by r100 | cx-b panel | CXB |
| Prisoners Dilemma | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | −0.08 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Prisoners Dilemma | S-24 sakura-s01 production (units r100) | v10 host | 6 | 140–160 fixtures | SAK |
| Prisoners Dilemma | S-24 yeji-s01 PD − v10 | v10 host | −0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Prisoners Dilemma | S-24 yeji-s01p P − v10 | v10 host | +0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Prisoners Dilemma | S-20 yeji-s02 map field − P | v10 host | +0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Prisoners Dilemma | S-24 yeji-s04 − v10 | v10 host | +0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Prisoners Dilemma | S-20 yeji-s05 − v10 | v10 host | +0.12 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Prisoners Dilemma | S-17 chaewon-y04 one-ray probe | yuna-v05 | +0.50 | 96–196 fixtures | bots/chaewon-y04-probe/README.md |
| Prisoners Dilemma | sakura-s02 economy arm | yuna-v05 | −6 net, pearls −75 | seed 1, 100 pairs | SAK2 |
| Prisoners Dilemma | 9508 / 9663 local vs live (reference) | live bots | 0.88 vs 0.12 / 0.88 vs 0.00 | Q4 corpus | Q4 |
| Prisoners Dilemma | tidus / yuna-v02 / ein-dog local − live | live bots | −88 pp | calibration rows | origin/analysis/a1:docs/findings/2026-09-28-analysis-calibration-first-rows.md |
| Prisoners Dilemma | replay-drive agreement 9663 | live | 0.98 | live corpus | Q8 |
| Prisoners Dilemma | team 7 map fixed effect (Elo-equiv) | team 7 live | −418 | live ranked | S1Q1 |
| Prisoners Dilemma | Sophie K-1 win residual (reference) | team 7 live | −0.31 | live | project:claude/sophie-status.md |
| Prisoners Dilemma | S-16 valjean blind_mem (per map) | MC v01 | 1–11 → 7–5 | 12 fixtures/map | bots/valjean-v01-portal-memory/README.md |
| Prisoners Dilemma | field top-10 vs band | reference | 8 units / 22 total r250 vs 5 / 30 | live | C1PACE |
| Prisoners Dilemma | S-37 scholze-v02 rescue opening | fafnir-v01 | 2–4 → 6–0 (v05 5–1) | 6 games/map | experiment_data/strategy_leaks_20260927T000855Z_scholze/REPORT.md |
| Prisoners Dilemma | S-16 einstein-v02 portal memory (combined) | einstein-v01 | −1 | pre-registered screen | experiment_data/strategy_leaks_2026092623/REPORT.md |
| Prisoners Dilemma | witten-x03 confirmed fast-bed | fafnir | lost two seat-A fixtures, +1 seat B | matched fixtures | WITTEN |
| Prisoners Dilemma | newton n2c fast-bed contest | fafnir | +1 | gauntlet | docs/newton.md §6 |
| Prisoners Dilemma | fenrir v18 (record) | fenrir | 1–7 | 8 games/map | bots/fenrir-v18-arrival-ready-beds/README.md |
| Prisoners Dilemma | odin v01 35-map | odin | 0–8 | 35-map panel | docs/odin.md |
| Prisoners Dilemma | S-10 odin v05 separation | odin | improved (13-map −8 vs v03) | focused | docs/odin.md |
| Prisoners Dilemma | S-09 bifrost V29 tuned net-growth farms | bifrost | 7–1 → 6–2 | 8 games/map | docs/bifrost-family.md |
| Prisoners Dilemma | S-09 bifrost V04 net-growth farms | bifrost | helped (sign only) | — | docs/bifrost-family.md |
| Prisoners Dilemma | tyr V33 (sprint threat + 32×16 portal + 25×25 detour) | Tyr V12 | 6–30 | seeds 1–18 | bots/tyr-v33-targeted-resource-defense/README.md; docs/tyr-family.md |
| Prisoners Dilemma | tyr V33 vs V12 | Tyr V12 | 2–10 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Prisoners Dilemma | tyr V34 vs V12 | Tyr V12 | 0–12 | seeds 19–24 | bots/tyr-v34-calibrated-pearl-sprint/README.md |
| Prisoners Dilemma | tyr V29 center gate | Tyr | 0–4 | 4 games | docs/tyr-family.md |
| Prisoners Dilemma | chimera-v01 | ouroboros-v13 | 4–12 | 16 games/map | bots/chimera-v01-unified/README.md |
| Prisoners Dilemma | hunter-v23 | hunter-v20 | 16–0 | 16 games/map | bots/hunter-v23-supported-arrival-feed/README.md |
| Prisoners Dilemma | odin v01 35-map (FRONTIER) | odin | 0–8 | 35-map panel | docs/odin.md |

### Queen of Spades

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Queen of Spades | S-27 renoir-01c bedwait16 | Ares V06 (renoir-00) | +0.16 econ~ | 159, seed 1 | RA |
| Queen of Spades | S-26 renoir-07b unseen 5→8 | Ares V06 (renoir-00) | +0.51 econ~ (pooled −0.050) | 80 seat A, seed 1 | RA |
| Queen of Spades | S-03 esquie-04 crit-enclosure split | esquie-01 (V06+latecap8, shape off) | trapped 35.4→40.5 (+14 %) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Queen of Spades | S-14 ares-v33 split portal route handoff | Ares V32 | 6–0 | round robin vs V32/V28/V19 | V33; AFAM |
| Queen of Spades | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 0–2 | 2 games/map | V03 |
| Queen of Spades | S-15 cx-f02 pre-entry memory gate | cx-f chassis | 33.6→32.8 | cx-f panel | CXF §F-2 |
| Queen of Spades | team 7 live portal deaths per 100 steps (reference) | team 7 live | 39.6 | live corpus | CXD |
| Queen of Spades | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | 0 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Queen of Spades | ouroboros-s02-econ (economy arm) | fenrir-v18 (Python) | deaths/game 68→101 (wall 22→35, ally-body 6→12) | paired, unswbc 1.2.2 seed 1 | bots/ouroboros-s02-econ/README.md |
| Queen of Spades | ouroboros-s02x-firstcut (unseen-bed odds bug) | fenrir-v18 (Python) | 0/11 with Trophy | 24 pairs | bots/ouroboros-s02x-firstcut/README.md |
| Queen of Spades | S-35 pace-v01 (GLM) open gain | GLM pace host | −0.36 | pace panel | origin/glm/pace-v01:docs/findings/2026-09-29-pace-v01.md |
| Queen of Spades | S-47 jet-v05 frame mirror | gavroche-v32 | 12 vs 7 of 12 | 12 games/map | JET; bots/jet-v05-frame-mirror/README.md |
| Queen of Spades | S-24 sakura-s01 production (units r100) | v10 host | 6 | 140–160 fixtures | SAK |
| Queen of Spades | S-24 yeji-s01 PD − v10 | v10 host | −0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Queen of Spades | S-24 yeji-s01p P − v10 | v10 host | +0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Queen of Spades | S-20 yeji-s02 map field − P | v10 host | −0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Queen of Spades | S-24 yeji-s03 − v10 | v10 host | −0.25 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s03/README.md |
| Queen of Spades | S-24 yeji-s04 − v10 | v10 host | −0.12 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Queen of Spades | S-20 yeji-s05 − v10 | v10 host | +0.19 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Queen of Spades | S-17 chaewon-y04 one-ray probe | yuna-v05 | +0.42 | 96–196 fixtures | bots/chaewon-y04-probe/README.md |
| Queen of Spades | tidus / yuna-v02 / ein-dog local − live | live bots | −100 pp | calibration rows | origin/analysis/a1:docs/findings/2026-09-28-analysis-calibration-first-rows.md |
| Queen of Spades | S-08 t01 trapsplit graft | gavroche-v32 | +1 | 36-fixture panel | team_recon_306_20260927_claude §5b |
| Queen of Spades | field top-10 vs band territory | reference | 74 %/92 % vs 49 % | live | C1PACE |
| Queen of Spades | S-57 ein-dog v02 momentum | newton-x10 | +2 | gauntlet | bots/ein-dog-v02-momentum/README.md |
| Queen of Spades | S-26 avery v09/v11 frontier sweep | avery | 12–0 → 9–3 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| Queen of Spades | S-24 MC x12 remote density vs v01 (wins) | monte_christo | 7→9 | screen | bots/monte_christo-x12-remote-density/README.md |
| Queen of Spades | gaia v12 four-way sectors (dragons/length r100) | gaia | seat B: 5/10 → 8/18 | one seat | docs/gaia-family.md |
| Queen of Spades | gavroche v34 map totals | gavroche | 14–4 | 18 games/map | docs/gavroche-resume-2026-09-26.md V34 |
| Queen of Spades | S-23 bifrost V23 resource route ownership | bifrost | 8–0 → 3–5 | 8 games | docs/bifrost-family.md |
| Queen of Spades | S-09 bifrost V04 net-growth farms | bifrost | hurt (sign only) | — | docs/bifrost-family.md |
| Queen of Spades | tyr V33 vs V12 | Tyr V12 | 7–5 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Queen of Spades | tyr V34 vs V12 | Tyr V12 | 2–10 | seeds 19–24 | bots/tyr-v34-calibrated-pearl-sprint/README.md |
| Queen of Spades | tyr V03–V08 portal return guards | Tyr | V04 best in one multi-bot run; V08 0–2 full panel | — | docs/tyr-family.md |
| Queen of Spades | tidus-t01 spread | tidus | led at r30; u2/p29 by r200 vs control u15/p98 | one game | bots/tidus-t04-richspread/README.md |
| Queen of Spades | heimdall v10 vs Fenrir v18 | heimdall | 0–2 | 2 games/map | docs/heimdall-family.md |
| Queen of Spades | S-54 loki v02 vs Fenrir v18 | loki | 2–0 each (Fenrir swept 7 other maps) | 2 games/map | docs/loki-family.md |
| Queen of Spades | ouroboros-v05 waypoint cache 4 rounds | ouroboros | 10–0 → 3–7 (reverted) | 10 games | bots/ouroboros-v05-spread/README.md |
| Queen of Spades | S-16 einstein portal memory | einstein-v01 | activation only | screen | bots/einstein-v02-portal-memory/README.md |
| Queen of Spades | hunter-v23 | hunter-v20 | 2–14 | 16 games/map | bots/hunter-v23-supported-arrival-feed/README.md |
| Queen of Spades | S-26 hunter-v22 frontier | hunter-v20 | swept | 2 games/map | bots/hunter-v22-frontier-exploration/README.md |
| Queen of Spades | leviathan-v09 confirmed-only | leviathan | seat B: longest 29→13 (loss) | fixture | bots/leviathan-v09-arrival/README.md |
| Queen of Spades | eunchae s02 | yuna | 1–7 | FRONTIER panel | FRONTIER.md |

### Schooltime

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Schooltime | S-27 renoir-01c bedwait16 | Ares V06 (renoir-00) | −0.41 econ~ | 159, seed 1 | RA |
| Schooltime | S-26 renoir-22 scarcity | Ares V06 (renoir-00) | −0.38 econ~ | 160, seed 1 | RA |
| Schooltime | S-26/S-21 renoir-25 crowdexplore | Ares V06 (renoir-00) | +0.83 econ~ (pooled +0.041) | 80 seat A, seed 1 | RA |
| Schooltime | S-26 renoir-07b / 16 (more exploration) | Ares V06 (renoir-00) | loses (sign only; QoS gains +0.3–0.5) | 80–160, seed 1 | RA §reading |
| Schooltime | S-32 lune-r1-07 late cap ×8 | Ares V06 | dragons 47→43, p@250 −7 % | z1 pool, seeds 1+2 | R1 |
| Schooltime | S-25 sciel-03a EW food | Ares V06 (renoir-00) | +0.600 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Schooltime | S-22 sciel-03c radio guard | Ares V06 (renoir-00) | +0.495 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Schooltime | S-22 sciel-04b row-path | Ares V06 (renoir-00) | +0.5 econ~ (mean-vs-median tail) | z1 pool, seed 1, 160 | SCIEL |
| Schooltime | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | win 0.688→0.594 (−9 pp) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Schooltime | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | win −6 pp | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Schooltime | S-05 ares-v32 dead-end split orientation | Ares V19 | 0–2 | 20 games vs V19 (11–9) | V32 |
| Schooltime | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 0–2 | 2 games/map | V03 |
| Schooltime | S-15 cx-f02 pre-entry memory gate | cx-f chassis | 567→292 | cx-f panel | CXF §F-2 |
| Schooltime | S-58/S-20 cx-b02 router, atlas on vs off (units/len/pearls r100) | cx-b router | 26/68/175 vs 18/42/70 | cx-b panel | CXB |
| Schooltime | team 7 − band trapped len/1k (reference) | team 7 live | +21.2 (newborn +14.3) | live corpus | CXC; LED |
| Schooltime | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | +0.17 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Schooltime | S-17/S-20 ouroboros-s02-portal: portal deaths per step | fenrir-v18 (Python) | 0.195→0.068 (37.3→35.5/game) | paired, unswbc 1.2.2 seed 1 | OS02; bots/ouroboros-s02-portal/README.md |
| Schooltime | S-35 pace-v01 hold (class target) | yuna host (Claude) | u100 31.5→22; t250 125→72 | pace panel | PACE (main) |
| Schooltime | S-47 jet-v05 frame mirror | gavroche-v32 | 12 vs 9 of 12 | 12 games/map | JET; bots/jet-v05-frame-mirror/README.md |
| Schooltime | S-24 yeji-s01 PD − v10 | v10 host | +0.25 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Schooltime | S-24 yeji-s01p P − v10 | v10 host | +0.25 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Schooltime | S-24 yeji-s04 − v10 | v10 host | +0.12 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Schooltime | S-20 yeji-s05 − v10 | v10 host | +0.25 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Schooltime | S-27 sakura-s02 bed camping | yuna-v05 | total r250 135→52 | seed 1, 100 pairs | SAK2 |
| Schooltime | S-19 sakura-s02 opening dive boost | yuna-v05 | total r250 135→42; wall+self 12.25/1k | seed 1, 100 pairs | SAK2 |
| Schooltime | sakura-s02 economy arm | yuna-v05 | +3 net | seed 1, 100 pairs | SAK2 |
| Schooltime | team 7 map fixed effect (Elo-equiv) | team 7 live | +250 | live ranked | S1Q1 |
| Schooltime | field predictability (Elo slope per 100) | field | 0.49 | live ranked | S1Q2 |
| Schooltime | bifrost 8540 public record (reference) | bifrost 8540 | 10–3 | live | D-006 |
| Schooltime | S-08 vibing trapped-split graft on v32 | gavroche-v32 | −2 | 36-fixture panel | team_recon_306_20260927_claude §5b |
| Schooltime | field top-10 vs band units r100 | reference | 41 vs 15 | live | C1PACE |
| Schooltime | S-39 fafnir f12 size-matched support | serre | 11–3 → 13–1 | gauntlet | docs/leaklab-findings.md §4a |
| Schooltime | S-57 ein-dog v02 momentum | newton-x10 | −3 | gauntlet | bots/ein-dog-v02-momentum/README.md |
| Schooltime | MC v04 hazard vs sinbad | monte_christo | 0–2 (v01 2–0) | 2 games | bots/monte_christo-v05-compact-risk/README.md |
| Schooltime | gavroche v34 map totals | gavroche | 12–6 | 18 games/map | docs/gavroche-resume-2026-09-26.md V34 |
| Schooltime | skadi-v01 dead-end guard | skadi | 17–3 | 20 games | docs/skadi.md |
| Schooltime | heimdall v10 vs Fenrir v18 | heimdall | 0–2 | 2 games/map | docs/heimdall-family.md |
| Schooltime | hunter-v23 | hunter-v20 | 1–15 | 16 games/map | bots/hunter-v23-supported-arrival-feed/README.md |
| Schooltime | hunter v09/v10/v11 | hunter | 0–4 / 2–2 / 2–2 | 4 games | docs/hunter-python-results.md |
| Schooltime | hydra-v10 stalker-flee removal (motivation) | hydra | v08/v09 0–2 each | 2 games/map | bots/hydra-v10-farmclean/README.md |
| Schooltime | S-61 leviathan-x03 Estuary vs v09 | leviathan-v09 | 2–0 (longest 38–24, 52–15) | direct | docs/leviathan/ESTUARY_BOT_HANDOFF.md |
| Schooltime | S-61 Estuary r100 units vs Hunter | leviathan-v09 | 54/22 vs parent 38/25 | — | docs/leviathan/ESTUARY_BOT_HANDOFF.md |

### Slithery Fight

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Slithery Fight | S-32 lune-r1-07 late cap ×8 | Ares V06 | p@250 −4 %; Schooltime+Slithery wins 26→18 | z1 pool, seeds 1+2 | R1 |
| Slithery Fight | V06 base trapped length/1k (reference) | Ares V06 | 101.5 | z1 seed 1, 160 | R3 |
| Slithery Fight | S-06 r3-03 escape-early | Ares V06 | trapped 101.5→112.1 | z1 seed 1, 160 | R3 |
| Slithery Fight | S-28 esquie-03 / 03b starve-wait | esquie-01 (V06+latecap8, shape off) | +0.03 win | z1 pool, seeds 1+2, 320 (32/map) | ESQ §table |
| Slithery Fight | S-03 esquie-04 crit-enclosure split (V19 port) | esquie-01 (V06+latecap8, shape off) | trapped 101.3→81.9 (−19 %); newborn 73.6→52.7 (−28 %) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Slithery Fight | S-03 ares-v19 crit-enclosure split | Ares V09 | trapped 103.9→82.8 | 20 games vs V09 | V19 |
| Slithery Fight | S-04 ares-v25 / v26 salvage | Ares V19 | 2–0 | screen (2 games/map) | V25/V26 READMEs |
| Slithery Fight | S-05 ares-v28 minimum-sacrifice split | Ares V19 | 2–0 | 20 games vs V19 (12–8) | V28 |
| Slithery Fight | S-14 ares-v33 split portal route handoff | Ares V32 | 5–1 | round robin vs V32/V28/V19 | V33; AFAM |
| Slithery Fight | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 2–0 | 2 games/map | V03 |
| Slithery Fight | S-15 cx-f02 pre-entry memory gate | cx-f chassis | 617→401 | cx-f panel | CXF §F-2 |
| Slithery Fight | S-07 cx-f01 chassis trapped split | cx-f chassis | 356 trapped vs 27 greedy splits/100 rounds; gated u25 25→3 | cx-f panel | CXF |
| Slithery Fight | chassis wall rate (reference) | cx-f chassis | wall 29.5/1k vs band 8.9 | cx-f panel | CXF |
| Slithery Fight | S-58 router mill | cx-b router | ~150 deaths by r100 | cx-b panel | CXB |
| Slithery Fight | team 7 live portal deaths per 100 steps (reference) | team 7 live | 31.9 | live corpus | CXD |
| Slithery Fight | team 7 − band trapped len/1k (reference) | team 7 live | +23.2 (newborn +22.9) | live corpus | CXC; LED |
| Slithery Fight | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | +0.42 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Slithery Fight | salvage mill (pace host reference) | yuna host | ≈770 newborn deaths in one game; ~800 length lost by r150 | one game | PACE §4 |
| Slithery Fight | S-24 kazuha-s01 dissolve (both arms) | v10 host | −4 | 2×2, 140 fixtures | KAZ |
| Slithery Fight | S-24 kazuha-s01 production only | v10 host | −2 | 2×2, 140 fixtures | KAZ |
| Slithery Fight | S-24 sakura-s01 extras-only (framework strip) | v10 host | −5 | 140–160 fixtures | SAK |
| Slithery Fight | S-24/S-11 sakura-s01 both-minus-cert | v10 host | −5 | 140–160 fixtures | SAK |
| Slithery Fight | S-24 sakura-s01 production | v10 host | further −2 | 140–160 fixtures | SAK |
| Slithery Fight | sakura-s01 wall+self per 1k | v10 host | 14.6 | 140–160 fixtures | SAK |
| Slithery Fight | S-24 yeji-s01 PD − v10 | v10 host | −0.31 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Slithery Fight | S-24 yeji-s01p P − v10 | v10 host | −0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Slithery Fight | S-20 yeji-s02 map field − P | v10 host | +0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Slithery Fight | S-24 yeji-s03 − v10 | v10 host | −0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s03/README.md |
| Slithery Fight | S-24 yeji-s04 − v10 | v10 host | +0.12 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Slithery Fight | S-20 yeji-s05 − v10 | v10 host | 0 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Slithery Fight | 9508 TLE turns (reference) | fenrir-v18 live | 213 | live corpus | Q6 |
| Slithery Fight | 9663 live CPU peak | live | 97.5M (probe 74.4M) | live corpus | Q6 |
| Slithery Fight | team 7 map fixed effect (Elo-equiv) | team 7 live | +387 | live ranked | S1Q1 |
| Slithery Fight | S-08 vibing trapped-split graft on v32 | gavroche-v32 | +3 | 36-fixture panel | team_recon_306_20260927_claude §5b |
| Slithery Fight | S-53 ouroboros-m01 mimic | clone | 2–6 | 8 games/map | team_recon_306_20260927_claude §5a |
| Slithery Fight | band vs top-10 eat rate | reference | band 12.7 vs 9.9 pearls/100 dt | live | C1PACE |
| Slithery Fight | tyr V33 vs V12 | Tyr V12 | 8–4 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Slithery Fight | S-44 tyr V18 early feed | Tyr | won repeatedly; hurt other maps | — | docs/tyr-family.md |

### Trauma

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Trauma | S-27 renoir-01c bedwait16 | Ares V06 (renoir-00) | +0.14 econ~ | 159, seed 1 | RA |
| Trauma | S-26 renoir-22 scarcity | Ares V06 (renoir-00) | +0.11 econ~ | 160, seed 1 | RA |
| Trauma | S-25 sciel-03a EW food | Ares V06 (renoir-00) | +0.100 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Trauma | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | p@50\|map 0.111→0.222 | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Trauma | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | p@50 0.222 held; p@250 1.022→1.130; win 0.750→0.812 | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Trauma | S-28 esquie-03b starve-wait v3 (LOCAL HOLD) | esquie-01 (V06+latecap8, shape off) | win 0.708→0.771 (+6 pp), p@250 252→263; r50 gain reverted (0.222→0.111) | z1 seeds 1–3, 480 | ESQ |
| Trauma | S-03 esquie-04 crit-enclosure split | esquie-01 (V06+latecap8, shape off) | newborn 4.3→12.0 (×3) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Trauma | S-05 ares-v28 minimum-sacrifice split | Ares V19 | 0–2 | 20 games vs V19 (12–8) | V28 |
| Trauma | ares-v03 C++ port vs Tyr V12 | Tyr V12 port | 2–0 | 2 games/map | V03 |
| Trauma | S-58/S-20 cx-b02 router, atlas on vs off (units/len/pearls r100) | cx-b router | 10/26/28 vs 4/12/4 | cx-b panel | CXB |
| Trauma | yuna-v03 local vs opponent (reference) | yuna-v03 | trapped +24.2 (opp 0) | local | LED |
| Trauma | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | +0.21 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Trauma | S-24 kazuha-s01 production only | v10 host | +2 | 2×2, 140 fixtures | KAZ |
| Trauma | S-24 sakura-s01 extras-only (framework strip) | v10 host | −5 | 140–160 fixtures | SAK |
| Trauma | S-24/S-11 sakura-s01 both-minus-cert | v10 host | −6 | 140–160 fixtures | SAK |
| Trauma | S-24 sakura-s01 production (units r100) | v10 host | 5 | 140–160 fixtures | SAK |
| Trauma | S-24 yeji-s01 PD − v10 | v10 host | −0.31 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Trauma | S-24 yeji-s01p P − v10 | v10 host | −0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Trauma | S-20 yeji-s02 map field − P | v10 host | +0.12 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Trauma | S-24 yeji-s03 − v10 | v10 host | −0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s03/README.md |
| Trauma | S-24 yeji-s04 − v10 | v10 host | −0.19 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Trauma | S-27 chaewon-y03 rich beds | yuna-v05 | −0.5 | 32 fixtures | bots/chaewon-y03-richbeds/README.md |
| Trauma | 9508 TLE turns (reference) | fenrir-v18 live | 201 | live corpus | Q6 |
| Trauma | replay-drive agreement 8540 (reference) | bifrost 8540 | 0.96 | live corpus | Q8; team_recon_7_20260928_claude §2 |
| Trauma | yuna host p_blind 1.0 (before fix) | yuna host | r100 pearls often 0–6 | — | YUNA §1 |
| Trauma | yuna-v05 length losses | yuna host | more material at r400, shorter longest | — | YUNA |
| Trauma | field top-10 vs band units r100 | reference | 16 vs 8 (46 units r200) | live | C1PACE §b,c |
| Trauma | S-16 einstein-v02 portal memory (combined) | einstein-v01 | +1 | pre-registered screen | experiment_data/strategy_leaks_2026092623/REPORT.md |
| Trauma | S-57 ein-dog v02 momentum | newton-x10 | +2 | gauntlet | bots/ein-dog-v02-momentum/README.md |
| Trauma | S-26 avery v09/v11 frontier sweep | avery | 5–7 → 8–4 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| Trauma | S-33 gavroche v60 vs v36 | gavroche | 3–11 vs 5–9 | 14 games | docs/gavroche-resume-2026-09-26.md V60 |
| Trauma | gavroche v34 map totals | gavroche | 9–9 | 18 games/map | docs/gavroche-resume-2026-09-26.md V34 |
| Trauma | gavroche v42 sandbox (walls / splits) | gavroche | walls 119, splits 273 | sandbox | experiment_data/gavroche-v42 report (per d4 notes) |
| Trauma | tyr V33 (sprint threat + 32×16 portal + 25×25 detour) | Tyr V12 | 32–4 | seeds 1–18 | bots/tyr-v33-targeted-resource-defense/README.md; docs/tyr-family.md |
| Trauma | tyr V33 vs V12 | Tyr V12 | 9–3 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Trauma | tyr V34 vs V12 | Tyr V12 | 11–1 | seeds 19–24 | bots/tyr-v34-calibrated-pearl-sprint/README.md |
| Trauma | S-44 tyr V18 early feed | Tyr | won repeatedly; hurt other maps | — | docs/tyr-family.md |
| Trauma | skadi-v01 dead-end guard | skadi | 7–13 | 20 games | docs/skadi.md |
| Trauma | S-43 ouroboros-v02 crown fix | ouroboros | 2–8 → 7–3 | 10 games | bots/ouroboros-v02-crown/README.md |
| Trauma | S-19 ouroboros-v05 bundle (portal dives) | ouroboros | 2–12 (v01) → 13–0 | 13–14 games | bots/ouroboros-v05-spread/README.md; docs/ouroboros-design.md §6 |
| Trauma | S-16 einstein portal memory | einstein-v01 | activation only | screen | bots/einstein-v02-portal-memory/README.md |
| Trauma | chimera-v01 | ouroboros-v13 | 15–1 | 16 games/map | bots/chimera-v01-unified/README.md |
| Trauma | hunter-v23 | hunter-v20 | 1–15 | 16 games/map | bots/hunter-v23-supported-arrival-feed/README.md |
| Trauma | S-43 hydra-v11 crown v2 | hydra | 4–0 sweeps | 4 games/map | bots/hydra-v11-macro/README.md |

### Trophy

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| Trophy | S-26 renoir-07b / 16 (more exploration) | Ares V06 (renoir-00) | loses (sign only; QoS gains +0.3–0.5) | 80–160, seed 1 | RA §reading |
| Trophy | S-32 lune-r1-07 late cap ×8 | Ares V06 | dragons@100 19.2→23.0 | z1 pool, seeds 1+2 | R1 |
| Trophy | S-22 sciel-03c radio guard | Ares V06 (renoir-00) | +0.248 econ~ | z1 pool, seed 1, 160 | SCIEL |
| Trophy | S-28 esquie-02 starve-wait v1 (gate bug) | esquie-01 (V06+latecap8, shape off) | econ_pct 0.594→0.470; win 0.719→0.562 | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Trophy | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | p@250 1.068→1.132 (base 1.265); win 0.562→0.656 (vs v1) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Trophy | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | p@250 1.265→1.404 (+0.14) | z1 pool, seeds 1+2, 320 (32/map) | ESQ |
| Trophy | S-03 esquie-04 crit-enclosure split | esquie-01 (V06+latecap8, shape off) | 0 (bit-identical) | z1 pool, seeds 1+2, 320 (32/map) | ESQ §table |
| Trophy | team 7 live portal deaths per 100 steps (reference) | team 7 live | 45.7 | live corpus | CXD |
| Trophy | S-17/S-20 ouroboros-s02-portal (atlas routes + portal safety) | fenrir-v18 (Python) | +0.08 | paired, unswbc 1.2.2 seed 1 | OS02 |
| Trophy | ouroboros-s02x-firstcut (unseen-bed odds bug) | fenrir-v18 (Python) | units r100 13→6; −0.46 on 24 pairs | 24 pairs | bots/ouroboros-s02x-firstcut/README.md |
| Trophy | S-35 GLM pace full forage boost | GLM pace host | u100 33→11 | pace panel | origin/glm/pace-v01:docs/findings/2026-09-29-pace-v01.md |
| Trophy | S-24 yeji-s01 PD − v10 | v10 host | +0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01/README.md |
| Trophy | S-24 yeji-s01p P − v10 | v10 host | +0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s01p/README.md |
| Trophy | S-20 yeji-s02 map field − P | v10 host | −0.12 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s02/README.md |
| Trophy | S-24 yeji-s04 − v10 | v10 host | −0.06 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s04/README.md |
| Trophy | S-20 yeji-s05 − v10 | v10 host | +0.06 | yeji panel (8 refs), seed 2 | origin/yeji/s01:bots/yeji-s05/README.md |
| Trophy | v10 vs sinbad pearls (reference) | v10 host | 60 vs 630 | S1 panel | CHAE |
| Trophy | sinbad vs ours pearls r20–40 (reference) | v10 host | 23 vs 3 | S1 panel | origin/yeji/s01:docs/findings/2026-09-29-yeji-s01-swarm-dissolve.md |
| Trophy | seat effect (yuna-v05 vs sinbad-v07) | yuna-v05 | side A wins | fixture pair | origin/chaewon/s01:docs/findings/2026-09-28-chaewon-s01-swarm-dissolve.md |
| Trophy | S-27 chaewon-y03 rich beds | yuna-v05 | −1.0 | 32 fixtures | bots/chaewon-y03-richbeds/README.md |
| Trophy | replay-drive agreement 8540 (reference) | bifrost 8540 | 0.80 (9663 0.83) | live corpus | Q8; team_recon_7_20260928_claude §2 |
| Trophy | team 7 map fixed effect (Elo-equiv) | team 7 live | −146 | live ranked | S1Q1 |
| Trophy | Sophie K-1 win residual (reference) | team 7 live | −0.10 | live | project:claude/sophie-status.md |
| Trophy | bifrost 8540 public record (reference) | bifrost 8540 | 7–11 | live | D-006 |
| Trophy | S-27/S-46 spike-x09 v_bed 8→14 | gavroche-v32 | ≈ −50 pp | small | project:claude/spike-status.md |
| Trophy | S-53 ouroboros-m01 mimic | clone | 7–1 | 8 games/map | team_recon_306_20260927_claude §5a |
| Trophy | newton n2c fast-bed contest | fafnir | +2 | gauntlet | docs/newton.md §6 |
| Trophy | S-57 ein-dog v02 momentum | newton-x10 | +3 | gauntlet | bots/ein-dog-v02-momentum/README.md |
| Trophy | S-24 MC x12 remote density vs v01 (wins) | monte_christo | 8→11 | screen | bots/monte_christo-x12-remote-density/README.md |
| Trophy | fenrir v18 (record) | fenrir | 3–5 | 8 games/map | bots/fenrir-v18-arrival-ready-beds/README.md |
| Trophy | odin v01 35-map | odin | 7–1 | 35-map panel | docs/odin.md |
| Trophy | bifrost V08/V28 opening sector spread | bifrost | won two direct Trophy; no external change | 2 games | docs/bifrost-family.md |
| Trophy | tyr V33 vs V12 | Tyr V12 | 5–7 | seeds 1–6 | bots/tyr-v33-targeted-resource-defense/README.md |
| Trophy | tyr V27/V28 direct pickup reward | Tyr | 1–3 each (V25 0–4) | 4 games | docs/tyr-family.md |
| Trophy | odin v01 35-map (FRONTIER) | odin | 7–1 | 35-map panel | docs/odin.md |

## Other maps and map classes

Gen (`maps/new`), transposed (`var/*_tr`), synthetic, older-pool maps and map classes, alphabetical.

| Map | Mechanism (S id or bot) | Host | Delta (as reported) | Panel/seeds | Source |
|---|---|---|---|---|---|
| all live maps | S-20 chassis atlas on vs off | cx-f chassis | pearls 35 vs 30; portal deaths 72/143/25 | cx-f panel | CXF §1 |
| arena | A-18 jet-v01 richladder | gavroche-v32 | 36/48 vs v32 16/48 | 48 games | bots/jet-v01-richladder/README.md |
| arena | S-37 scholze-v02 rescue opening | fafnir-v01 | 2–4 → 1–5 (v04/v05) | 6 games/map | experiment_data/strategy_leaks_20260927T000855Z_scholze/REPORT.md |
| arena | witten-x02 fast_edisc | fafnir | changed 4/4 games (false activation) | 4 games | WITTEN |
| arena | serre vs O13 / tew (reference) | serre | 0–2 / 0–2 | exact panel | WITTEN |
| arena | S-39 fafnir f12 size-matched support | serre | 5–9 → 6–8 | gauntlet | docs/leaklab-findings.md §4a |
| arena | newton n2c fast-bed contest | fafnir | −4 (2–12) | gauntlet | docs/newton.md §6 |
| arena | S-36 avery v07 compact production | avery | 3–8–1 → 7–4–1 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| arena | S-21 sinbad-v05 w_crowd 0 (test) | sinbad | 3–9 → 7–5 (quick+quickT −7) | screen | bots/sinbad-v05-hunt8/README.md |
| arena | gaia v48/v49/v50 split timing | gaia | each lost both Fenrir arena games | 2 games each | docs/gaia-family.md |
| arena | S-54 loki v02 vs Fenrir v18 | loki | 2–0 each (Fenrir swept 7 other maps) | 2 games/map | docs/loki-family.md |
| arena | ouroboros-v08 own_enemy=0 | ouroboros | "30+ uneaten pearls" before (motivation) | — | bots/ouroboros-v08-contest/README.md |
| arena | hunter-v23 | hunter-v20 | 12–4 | 16 games/map | bots/hunter-v23-supported-arrival-feed/README.md |
| arena | athos motivation (reference) | athos | 153/192 deaths enemy kills; ~3 vs ~50 dragons at end | — | bots/athos-x01, athos-x02/x04 READMEs (per pb notes) |
| arena | ouroboros-v05 vs hydra-v06 (A) | reference | eliminated r47; 14 splits/55 pearls vs 50/138 | 1 game | docs/leviathan/LINEAGE_REVIEW.md |
| arena_TFX | feynman-x01 baseline | fafnir | 2–4 | 6 games/map | docs/feynman.md §3 |
| autarky_tr | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | +0.125 win | gen 29 maps, seed 1 | ESQ |
| big_empty | S-53 ouroboros-m01 mimic | clone | 0–8 | 8 games/map | team_recon_306_20260927_claude §5a |
| big_empty | S-37 scholze-v02 rescue opening | fafnir-v01 | 6–0 → 4–2 (v05 6–0) | 6 games/map | experiment_data/strategy_leaks_20260927T000855Z_scholze/REPORT.md |
| big_empty | serre vs O13 / tew (reference) | serre | 2–0 / 2–0 | exact panel | WITTEN |
| big_empty | S-39 fafnir f9 / f11 support variants | serre | −3 (f11) | gauntlet | docs/leaklab-findings.md §4a |
| big_empty | S-43 avery v08 crown race | avery | 7–5 → 9–3 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| big_empty | S-21 drake v09 density | drake | 2–20 → 9–13 | 22 games | docs/feynman.md §1; bots/drake-v09-density-tuned |
| big_empty | S-21 drake v10 dual EWMA | drake | 9–13 → 1–21 | 22 games | docs/feynman.md §4; bots/drake-v10-dual-ewma/README.md |
| big_empty | sinbad long-dragon deaths to short heads (reference) | sinbad | ~9 per game | — | docs/handoffs/sinbad-handoff.txt |
| big_empty | gaia v08 vs Fenrir | gaia | won both (64 units) | 2 games | docs/gaia-family.md |
| big_empty | gaia v46 all-map threat gate | gaia | throughput regressed (tied V08 9W–15L) | 24 games | docs/gaia-family.md |
| big_empty | S-33 gavroche v46 vs v36 | gavroche | 11–7 → 7–11 | 18 paired | docs/gavroche-resume-2026-09-26.md V46 |
| big_empty | S-33 gavroche v56 | gavroche | 3–9 | 12 games | docs/gavroche-resume-2026-09-26.md V56 |
| big_empty | gavroche v34 map totals | gavroche | 9–9 | 18 games/map | docs/gavroche-resume-2026-09-26.md V34 |
| big_empty | gavroche v42 sandbox (walls / splits) | gavroche | walls 156, splits 305 | sandbox | experiment_data/gavroche-v42 report (per d4 notes) |
| big_empty | spike-x04 over-conversion | gavroche | opponent total 475–778; collapse to 1 unit | — | bots/spike-x05 README (per pa1 notes) |
| big_empty | S-43 ouroboros-v02 crown fix | ouroboros | 6–4 → 9–1 | 10 games | bots/ouroboros-v02-crown/README.md |
| big_empty | hunter-v23 | hunter-v20 | 2–14 | 16 games/map | bots/hunter-v23-supported-arrival-feed/README.md |
| big_empty | S-34 hunter-v14 C++ port | hunter-v13 | lost all 4 (v13 won 3/4) | 4 games | docs/hunter-python-results.md |
| big_empty | hydra-v10 stalker-flee removal (motivation) | hydra | v08/v09 0–2 each | 2 games/map | bots/hydra-v10-farmclean/README.md |
| big_empty | hydra-v06 map-wide yielding | hydra | 2W → 2L | 2 games | bots/hydra-v06-echo/README.md; docs/strategy-backlog.md |
| big_empty | S-42 hydra v09 lanchester retreat | hydra | lost both sides | 2 games/map | docs/strategy-backlog.md |
| big_empty | S-59 kraken-v05 doom memory | kraken | swing map; only x04-nodoom took seat B | — | bots/kraken-v05-safety/README.md |
| big_empty | leviathan-v07 vs fry | leviathan | both sides lost on length (25–37, 28–30) | 2 games | docs/leviathan/RESULTS.md |
| big_empty | hydra-v06 vs ouroboros-v05 | reference | 64 dragons/457 total/longest 29 loses to 18/300/42 | 1 game | docs/leviathan/LINEAGE_REVIEW.md |
| big_empty | S-42 von_neumann aggro-off (x07) | fafnir | 3 losses→wins, 1 win→loss (round-500 races) | — | docs/von_neumann.md §9 |
| big_empty (+T) | A-14 sinbad-v05 hunt_max_len 8 | sinbad | 13–3 → 15–1 | 16 games | bots/sinbad-v05-hunt8/README.md |
| big_empty+stronghold+Trauma | S-61 leviathan-x03 Estuary vs v09 | leviathan-v09 | 0–6 | direct | docs/leviathan/ESTUARY_BOT_HANDOFF.md |
| causeways | S-58 router vs yuna (deaths) | cx-b router | 30–35 vs 70–84 | gen | CXB |
| Colosseum | S-27/S-46 spike-x09 v_bed 8→14 | gavroche-v32 | ≈ −50 pp | small | project:claude/spike-status.md |
| Colosseum | S-37 scholze-v02 rescue opening | fafnir-v01 | 6–0 → 4–2 (v05) | 6 games/map | experiment_data/strategy_leaks_20260927T000855Z_scholze/REPORT.md |
| Colosseum | newton n2c fast-bed contest | fafnir | −1 | gauntlet | docs/newton.md §6 |
| Colosseum | S-57 ein-dog x04 momentum | newton-x10 | −2 | gauntlet | bots/ein-dog-x08-momentum-scoped/README.md |
| Colosseum | skadi-v11 fast-bed transfer | skadi | 8–10 vs V54 12–6 | 18 games | docs/skadi.md |
| Colosseum | heimdall v10 vs Fenrir v18 | heimdall | 0–2 | 2 games/map | docs/heimdall-family.md |
| Colosseum | S-16 einstein portal memory | einstein-v01 | activation only | screen | bots/einstein-v02-portal-memory/README.md |
| Colosseum | hydra vs fry-v14 (motivation) | hydra | 8/8 losses | 8 games | bots/hydra-v09-lanchester/README.md |
| Colosseum_TFX | feynman-x01 baseline | fafnir | 2–4 | 6 games/map | docs/feynman.md §3 |
| commons | esquie-01 base (no mechanism) | esquie-01 (V06+latecap8, shape off) | win 0.50, 63–89 % enemy | gen 29 maps, seed 1 | ESQ |
| commons | spike-x04 over-conversion | gavroche | opponent total 475–778; collapse to 1 unit | — | bots/spike-x05 README (per pa1 notes) |
| compact | S-35 pace-v03 no farm discount | yuna host | u100 13→17 | pace panel | PACE §3–4 |
| compact | S-24 yeji-s03 − v10 | v10 host | 0.531 vs 0.391 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s03/README.md |
| compact | exact pairs 9639−9508 | live | +0.17 | live pairs | Q2 |
| compact | exact pairs 9980−9663 | live | +0.17 | live pairs | Q2 |
| compact | exact pairs 8540−9508 | live | 0.00 | live pairs | Q2 |
| compact | exact pairs 9663−9508 | live | +0.14 | live pairs | Q2 |
| compact | kraken-v05 vs field | kraken | 1–37–2 | field | bots/kraken-v05-safety/README.md |
| compact | S-27/S-61 leviathan v09 arrival | leviathan-v08 | 79–69–2 → 93–57 | 150 games | docs/leviathan/RESULTS.md |
| compact (gvc) | A-18 ouroboros-v13 ladder doctrine | ouroboros | 65–1–54 → 99–1–20 (hold-out 43–1–36 → 61–1–18) | gvc/gvo panels | bots/ouroboros-v13-ladder/README.md |
| compact (≤625 tiles) | hunter-v20 portal scouts (guard) | hunter-v23 | disabled by W·H ≤ 625 ("probes depleted V20 there") | — | bots/hunter-v23-supported-arrival-feed/main.cpp:348-349 |
| crossroads | S-10 yuna-v03 newborn exit ungated | yuna host | 0/8; synthetic −10.4 pp | synthetic | YUNA |
| crossroads | S-27/S-46 spike-x09 v_bed 8→14 | gavroche-v32 | +17..+42 pp | small | project:claude/spike-status.md; bots/spike-x09-v32-bedvalue/README.md |
| crossroads | eunchae s02 | yuna | 7–1 | FRONTIER panel | FRONTIER.md |
| default_small | S-39 fafnir f12 size-matched support | serre | 12–2 → 11–3 | gauntlet | docs/leaklab-findings.md §4a |
| default_small | S-36 newton n10 production | fafnir | 11–3 → 14–0 | gauntlet | bots/newton-x10-candidate/README.md |
| default_small | newton n2c fast-bed contest | fafnir | +3 | gauntlet | docs/newton.md §6 |
| default_small | gavroche v17 field record | gavroche | 2/18 (11.1 %) | field | scholze REPORT §2 |
| default_small | S-54 loki v02 vs Fenrir v18 | loki | 2–0 each (Fenrir swept 7 other maps) | 2 games/map | docs/loki-family.md |
| default_small | chimera-v01 | ouroboros-v13 | 14–2 | 16 games/map | bots/chimera-v01-unified/README.md |
| default_small | S-26 hunter-v22 frontier | hunter-v20 | lost | 2 games/map | bots/hunter-v22-frontier-exploration/README.md |
| default_small | kraken-v04 vs leviathan-v07 | reference | 400 pearls/134 splits, eliminated r468 (83 body, 27 wall) | 1 game | docs/leviathan/LINEAGE_REVIEW.md |
| default_small+Colosseum (+T) | S-27 sinbad-v06 arrival beds | sinbad-v05 | 13–19 → 25–7 | 32 games | bots/sinbad-v06-arrival/README.md |
| default_small+Devil+Trophy vs six open maps | ouroboros-v10 vs hunter-v20 | reference | 0–6 vs 12–0 | — | docs/public-replay-review-2026-09-25.md |
| default_tr | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | −0.125 win, −6 p@250 | gen 29 maps, seed 1 | ESQ |
| default_tr | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | −0.062 win | gen, seed 1 | ESQ |
| devil family (+_T,_F) | S-09 ouroboros-v07 farming + emergency split | ouroboros | 3–21 → 10–14 (vs 4 C++ swarms) | 24 games | bots/ouroboros-v07-forage2/README.md |
| devil_tr | V06 base (no mechanism; transposed map) | Ares V06 (renoir-00) | win 17 % (pool Devil 100 %) | gen 31 maps, seed 1 | RA; D-033 |
| devil_tr | S-26 renoir-07c unseen 5→4 | Ares V06 (renoir-00) | +1.03 econ~ | gen, seed 1 | RA |
| devil_tr | S-12 sciel-01a newborn siting | Ares V06 (renoir-00) | +0.100 | gen, seed 1 | SCIEL |
| devil_tr | S-45 esquie-01 nodevil base | esquie-01 (V06+latecap8, shape off) | win 0.44 | gen 29 maps, seed 1 | ESQ |
| equatorial_belt | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | p@250 −53 | gen 29 maps, seed 1 | ESQ |
| equatorial_belt | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | p@250 0 (v1 −53 closed) | gen, seed 1 | ESQ |
| far_harbors | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | +0.125 win | gen, seed 1 | ESQ |
| far_harbors | S-58 router vs yuna (deaths) | cx-b router | 46 vs 100 | gen | CXB |
| FX, FY flipped maps | sinbad vs ouroboros-v13 | sinbad | ~50 % vs ~75 % on originals | — | docs/handoffs/sinbad-handoff.txt |
| help (64×64) | S-43 ouroboros-v10 crown vs hydra v09/v10 | ouroboros | 8–0; crown 186–195 vs 97–111 | 8 games | bots/ouroboros-v10-beacon/README.md |
| help+stronghold+Schooltime+qos-ages+Trauma | ouroboros-v04 split stop 380 | ouroboros | 19–11 → 23–7 (pooled) | 30 games | docs/ouroboros-design.md §6 |
| honeycomb | S-24 javert x02 length-density radio | javert | 3 losses → wins (longest 4→34, 10→17, 8→16) | reserve | bots/javert-v01-game-relative/README.md |
| mc26_pinwheel | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | +0.125 win, +17 p@250 | gen 29 maps, seed 1 | ESQ |
| mc26_pinwheel | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | +0.125 win | gen 29 maps, seed 1 | ESQ |
| mc26_pinwheel | esquie-01 base (no mechanism) | esquie-01 (V06+latecap8, shape off) | win 0.31, 100 % enemy deaths, supply8 0 | gen 29 maps, seed 1 | ESQ |
| mc26_pinwheel | S-27/S-46 spike-x09 v_bed 8→14 | gavroche-v32 | +17..+42 pp | small | project:claude/spike-status.md; bots/spike-x09-v32-bedvalue/README.md |
| mc26_portal_quartet | S-18 sciel-02a post-transit nav | Ares V06 (renoir-00) | −0.037 | gen, seed 1 | SCIEL |
| mc26_portal_quartet | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | +0.125 win | gen 29 maps, seed 1 | ESQ |
| mc26_portal_quartet | S-56 team-7 learned production graft | bifrost | 2–2 → 0–4 | 36-fixture panel | team_recon_7_20260927T173904Z |
| mc26_portal_quartet | S-44 470 broad early feed | tew | one W→L (B vs Sinbad) | 36-fixture panel | team_recon_470_20260927T150303Z |
| mc26_portal_quartet | eunchae s02 | yuna | 1–7 | FRONTIER panel | FRONTIER.md |
| mc26_seam_market | esquie-01 base (no mechanism) | esquie-01 (V06+latecap8, shape off) | win 0.38, 100 % enemy, units@100 3 | gen 29 maps, seed 1 | ESQ |
| open | S-35 pace-v03 no farm discount | yuna host | −0.089 | pace panel | PACE §3–4 |
| open | S-24 yeji-s03 − v10 | v10 host | 0.448 vs 0.562 | yeji panel (8 refs) | origin/yeji/s01:bots/yeji-s03/README.md |
| open | exact pairs 9639−9508 | live | −0.22 | live pairs | Q2 |
| open | exact pairs 9980−9663 | live | −0.18 | live pairs | Q2 |
| open | exact pairs 8540−9508 | live | −0.11 | live pairs | Q2 |
| open | exact pairs 9663−9508 | live | −0.08 | live pairs | Q2 |
| open | kraken-v05 vs field | kraken | 27–21–0 | field | bots/kraken-v05-safety/README.md |
| open | S-60 riptide x02 viability | leviathan-v09 | +20 net (29–31 → 39–21) | 60 games | docs/leviathan/RIPTIDE_RESULTS.md |
| open (gvo) | A-18 ouroboros-v13 ladder doctrine | ouroboros | 115–0–5 unchanged | gvc/gvo panels | bots/ouroboros-v13-ladder/README.md |
| portal maps | S-19 sinbad-v07 v_dive 7→3 | sinbad-v06 | 36–20 → 45–11 | 56 games | docs/handoffs/sinbad-handoff.txt; bots/sinbad-v07-divecap/README.md |
| portal maps | S-19 hunter-v20 portal scouts | hunter-v19 | 11W/3L vs v19 | 14 games | bots/hunter-v20-portal-scouts/README.md |
| Portals+Slithery | S-04 ares-v27 no-portal farm upgrade | Ares V19 | 0–4 | screen | V27 README |
| portals_rec | S-18 sciel-02a post-transit nav | Ares V06 (renoir-00) | −0.025 | gen, seed 1 | SCIEL |
| portals_tr | esquie-01 base (no mechanism) | esquie-01 (V06+latecap8, shape off) | win 0.62, 0 % enemy (self-inflicted) | gen 29 maps, seed 1 | ESQ |
| portals_tr | S-58 router (no atlas) | cx-b router | 12/33/40 vs 5/16/10 | cx-b panel | CXB |
| Prisoners Dilemma+Autarky | S-16 valjean blind_mem | MC v01 | 3–21 → 14–10 | 24 fixtures | docs/handoffs/valjean-handoff.txt |
| public 10 maps | yuna-v05 accepted mechanisms | yuna host | +13.7 pp | public/synthetic/transposed panels | YUNA |
| pulse_farms | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | −0.062 win | gen, seed 1 | ESQ |
| queen_of_spades_tr | S-26 renoir-07c unseen 5→4 | Ares V06 (renoir-00) | −0.35 econ~ | gen, seed 1 | RA |
| queen_of_spades_tr | S-18 sciel-02a post-transit nav | Ares V06 (renoir-00) | +0.205 (outlier) | gen, seed 1 | SCIEL |
| relay_depots | S-58 router vs yuna (deaths) | cx-b router | 19 vs 170 | gen | CXB |
| scattered_fleets | S-58 router vs yuna (deaths) | cx-b router | 24 vs 90 | gen | CXB |
| scattered_fleets | odin v01 35-map | odin | 0–8 | 35-map panel | docs/odin.md |
| scattered_fleets | eunchae s02 | yuna | 6–2 | FRONTIER panel | FRONTIER.md |
| Schooltime+stronghold+Trauma subset | S-60 Estuary continuation off | leviathan-v09 | 8–4 → 11–1 | 12 games | docs/leviathan/ESTUARY_BOT_HANDOFF.md |
| Seat B (pool) | S-32 lune-r1-07 late cap ×8 | Ares V06 | dragons +0.106, length +0.101 (51/5/24) | z1 pool | R1 |
| small maps | ouroboros-v07 spawn_window 12→25 | ouroboros | 48–24 → 53–19 | 72 games | bots/ouroboros-v07-forage2/README.md |
| small maps | hunter-v11 route spacing | hunter | 0–4 | 4 games | hunter-v12 README (per pb notes) |
| spring_wells | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | +14.5 p@250 | gen 29 maps, seed 1 | ESQ |
| spring_wells | S-27/S-46 spike-x09 v_bed 8→14 | gavroche-v32 | +50 pp (p@50 7→27 on one fixture) | small | project:claude/spike-status.md; bots/spike-x09-v32-bedvalue/README.md |
| stronghold | serre vs O13 / tew (reference) | serre | 2–0 / 2–0 | exact panel | WITTEN |
| stronghold | S-39 fafnir f9 / f11 support variants | serre | −4 (f9) | gauntlet | docs/leaklab-findings.md §4a |
| stronghold | S-57 ein-dog v02 momentum | newton-x10 | −3 | gauntlet | bots/ein-dog-v02-momentum/README.md |
| stronghold | S-43 avery v08 crown race | avery | 8–4 → 10–2 | 12 games/map | docs/handoffs/avery-lineage-handoff.txt |
| stronghold | S-24 MC x12 remote density vs v01 (wins) | monte_christo | 11→9 | screen | bots/monte_christo-x12-remote-density/README.md |
| stronghold | sinbad-v04 reach_cap_crown 6 (test) | sinbad | −7 fixtures off big maps | screen | sinbad-v04 README (per pa2 notes) |
| stronghold | S-33 gavroche v46 vs v36 | gavroche | 13–5 → 6–12 | 18 paired | docs/gavroche-resume-2026-09-26.md V46 |
| stronghold | S-33 gavroche v56 | gavroche | 2–10 | 12 games | docs/gavroche-resume-2026-09-26.md V56 |
| stronghold | S-33 gavroche v60 vs v36 | gavroche | 11–3 vs 10–4 | 14 games | docs/gavroche-resume-2026-09-26.md V60 |
| stronghold | gavroche v34 map totals | gavroche | 13–5 | 18 games/map | docs/gavroche-resume-2026-09-26.md V34 |
| stronghold | heimdall v10 vs Fenrir v18 | heimdall | 0–2 | 2 games/map | docs/heimdall-family.md |
| stronghold | hunter-v21 emergency portals | hunter-v20 | lost both vs v20 | 2 games | bots/hunter-v21-emergency-portals/README.md |
| stronghold | S-26 hunter-v22 frontier | hunter-v20 | lost | 2 games/map | bots/hunter-v22-frontier-exploration/README.md |
| stronghold | S-43 hydra-v11 crown v2 | hydra | 4–0 sweeps | 4 games/map | bots/hydra-v11-macro/README.md |
| stronghold | eunchae s02 | yuna | 1–7 | FRONTIER panel | FRONTIER.md |
| synthetic maps | yuna-v05 accepted mechanisms | yuna host | −2.7 pp | public/synthetic/transposed panels | YUNA |
| transposed maps | yuna-v05 accepted mechanisms | yuna host | −4.2 pp | public/synthetic/transposed panels | YUNA |
| trauma_tr | S-26 renoir-07c unseen 5→4 | Ares V06 (renoir-00) | −0.35 econ~ | gen, seed 1 | RA |
| trauma_tr | S-28 esquie-02 starve-wait v1 | esquie-01 (V06+latecap8, shape off) | p@250 −29 | gen 29 maps, seed 1 | ESQ |
| trauma_tr | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | +0.312 win, +31.5 p@250 | gen 29 maps, seed 1 | ESQ |
| trauma_tr | S-28 esquie-03b starve-wait v3 | esquie-01 (V06+latecap8, shape off) | +0.250 win | gen, seed 1 | ESQ |
| trophy_tr | V06 base (no mechanism; transposed map) | Ares V06 (renoir-00) | win 17 % (pool Trophy 80 %) | gen 31 maps, seed 1 | RA; D-033 |
| trophy_tr | S-28 esquie-03 starve-wait v2 | esquie-01 (V06+latecap8, shape off) | +0.188 win | gen 29 maps, seed 1 | ESQ |
| trophy_tr | S-45 esquie-01 nodevil base | esquie-01 (V06+latecap8, shape off) | win 0.25 (88 % enemy deaths) | gen 29 maps, seed 1 | ESQ |

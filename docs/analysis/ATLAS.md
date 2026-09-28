# JKS statistics atlas

**v2 — 28 September 2026, ~13:10 UTC. Author `claude/analysis/session-01KHqE`.** Every number below was re-derived
in this pass from the files named; `tools/analysis/a1_report.py` reproduces the live-record numbers from
`LIVE/state/state.json` in one command, `tools/analysis/transfer.py` the ledger numbers, `tools/analysis/ratings_sanity.py`
the rating numbers. v1 (gpt-6/analysis/codex-session, 12:15 UTC, field pool only, ledger unread) is kept verbatim in
the appendix; where v2 differs it says so. Findings: `docs/findings/2026-09-28-analysis-claude-Q*.md`; research list:
`docs/analysis/RESEARCH_LIST.md`; director memo: `docs/findings/2026-09-28-analysis-claude-director-memo.md`.

## 0. Reading rules

Unit of independence is stated per table (game, exact pair, series, run × opponent, bot version). Live rows are
verified only (40 of 486 result rows are pending API payloads and are excluded). "Controlled" = requested by the
executor; "observational" = a teammate's request we merely harvested. A-side only: 435 of 446 verified games are
side A; no B-side claim is made. Stage fields carry the terminal state forward after elimination, so every median
includes eliminated games. Opponents are stratified by submission id (545 changed 9371 → 9571 at ~03:20 UTC). The
local ledger holds outcomes only. Nothing was uploaded, no API call was made, and the key file was not read.

## 1. Dataset atlas

| Dataset (as of 12:12 UTC) | Unit / headline numbers re-derived | Answers | Cannot answer / confounds |
|---|---|---|---|
| **Live record** `LIVE/state/state.json` → `results`, `blocks`, `requests`, `experiments`, `seen_series` (hub `games` mirror: 487 rows) | game. 486 results, 446 verified (425 controlled + 21 observational; 286 field + 160 dev; 435 A / 11 B). Sources: 9508 n=156, 9663 78, 9639 52, 8540 51, 9980 49, 9573/9604/10013 20 each. Opponent submissions: 62/9343 103, 45/9433 90, 752/3887 80, 470/6350 72, 545/9571 55, 545/9371 25, 306/6985 10, 157/9762 8, 967/9518 3. 205 eliminations / 241 round limits. Ten maps, 42–50 games each. Every game carries 28 stage fields at 10 stages for both sides, cpu_max (complete: cpu_recorded = turns in all 446), faults, map_hash, seed, request/series membership. | Q1 loss anatomy, Q2 exact pairs (96 pairs over 4 screens), Q3 layout rule, Q5 opponent fingerprints, Q6 live runtime, Q7 sonar volume, Q9 series timeline. | Earliest stage is r100 — the opening (where losses are decided) is invisible; only one side; screen opponents are ranks 6/40/59, not the band; seeds never repeat; 9508 is a teammate's build. |
| Live replays `LIVE/state/replays` (446 gz) + `state/decoded` (1.1 GB) | game / command. Replay-driven in this pass: 121 games, 965,412 commands. | Q8 judge-divergence signature; any per-round statistic the stage fields lack (decode with the frozen `system/vendor/public_replay_review.py`). | Post-27-Sep games replay-drive at ~92 %, so replay-derived inboxes are approximate. |
| Live probes `LIVE/state/runtime/<cand>/{9-A,20-B}.{json,log}` | dragon-turn. 16 probes; 10 logs parsed: 160,234 candidate dragon-turns; p50 17.5–28.8 M, p99 45–54 M, max 57.7–94.5 M. | Q6 per-turn costs (per ray ≈ 0, per living dragon 0.08–0.16 M), Q7 ray cost. | Two fixtures only (Schooltime A, Portals B): Slithery Fight, where yuna-v02 peaked live at 97.5 M, is never probed. No NUM_MSGS (inputs are not echoed). |
| Legacy diagnostics `LIVE/{FINDINGS,DIAGNOSIS,TIMING_CHECK,CANDIDATE_SELECTION}.md`, `state/{phase_diagnostics,critic,donor360-dev-contrast}.json` | mixed; each note's own denominators. | Hypotheses (donor clocks r400–432, r275 CPU failure of 9508, orientation randomisation). | Second-hand; the orientation claim is now explained (Q3), the runtime claim confirmed (Q6). |
| **Hub** `battlecode-hub/hub.sqlite` (copy: 487 games, 40 blocks, 5 experiments, 16 probes, 20 ranked_exposure rows, 0 calibration rows, 72 shadow checks all agreeing) and mirror `hub-state/` | game / block / series. | Everything the live record answers, every 10 min, now including the A1 block (`tools/hub/analysis_a1.py`: pairs, anatomy, layout rule, runtime, sonar). | `calibration` is empty: the daemon runs the 09:21 copy and no candidate fingerprint mapped to a bot until `build/bot_legacy_fingerprints.json` exists; `ranked_exposure.elo_change` is null (cached while pending). Never open the sqlite over the mount; copy it. |
| **Local ledger** `game_stats.parquet` | game. 126,100 games (A 66,864 / B 58,833 / draw 403), 692 bot names, 1.0.0 119,138 / 1.1.0 4,646 / 1.2.1 1,700 / 1.0.1 616; native 125,703 / sandbox 397; seeds null for all 1.0.x rows. Live maps: 8 with 5.8–10.4 k games, **Portals and Slithery Fight 40 each**. The six live sources have 18–68 native games each on live maps, 0 on Portals/Slithery. | Q4 absolute calibration (local overstates live by 7–35 pp for 6/6 sources), toolkit strata (outcomes only). | No trajectories; opponents are our own lineages; 0–4 common (map, opponent) cells between any live candidate/control pair → paired calibration impossible. |
| Local ratings `experiment_data/bot-ratings/latest.json` (12:07 UTC) | bot version. 280 active, 101 Established / 179 Sparse, 108,339 fixtures; top 62 all Sparse; live-tested sources at raw ranks 1/9/11/18/62/236 with live shares 0.29–0.50. | Q10: evidence tiers, shrinkage effect (rank order of live sources unchanged; Spearman +0.10 raw, −0.20 shrunk vs live). | Must not order the queue; panel bias, not sparsity, is the defect. |
| Adaptive campaign `benchmark_20260928064036195154` | fixture. Pointer and manifest only were read. | — | Not re-derived (1 % complete per handoff). |
| Comparison runs `experiment_data/<bot>_<ts>/` (~650 dirs) | run × game; per-round series in `opponents/*/stats/*.csv`. 7 runs hold series for two live sources (ein-dog, tidus-t02): 3,246 stage rows. | Q4 trajectory matching. | None of the other four live sources has any per-round series; runs mix seed policies. |
| Public corpora `experiment_data/team_recon_*`, `public_replays/` | replay, by opponent submission. Not re-read here beyond the self-audit's numbers. | Behavioural fingerprints of 306/470/62/7 (existing reports). | Band teams absent; post-change inboxes ~92 % faithful. |
| Lineage notes (project docs) | second-hand. | Hypotheses only. | Three claims not reproduced: see the memo. |
| Map facts `maps/*.map`, `LIVE/state/maps.json` | map. Live PD map text says DRAGON_COUNT 6; the server dealt 10 dragons in 28 of 50 live PD games. | Q3 versions. | Local dilemma.map is the 6-dragon version only. |

## 2. Headline numbers (each with its finding)

- **Q1** (game; 425 controlled A-side): losses are 60 % eliminations (74 % on compact maps), median compact
  elimination round 122–158; in 85–95 % of losses we already trail on total length at r100; win share behind vs ahead
  at r100: compact 0.14 vs 0.78 (n 127 / 46), open 0.31 vs 0.76 (159 / 87); half of compact teams dead by r250 for
  every source; h2h death rate doubles in losses (19–28 vs 8–12 per 1k). Heartbreaker (62) causes 56 of 64 losses by
  elimination.
- **Q2** (exact pair): 30 / 30 / 19 / 17 pairs; Δ −0.067, −0.067, 0.000, −0.059; sign-test p 0.75, 0.75, 1.0, 1.0;
  26 of 29 outcome flips agree in sign with the r250-total delta; a 30-pair screen detects |Δ| ≥ 0.25 only.
- **Q3** (game): layout = f(map, game-id parity), 446/446, 0 violations; batches pair iff first ids share parity;
  a 20-game M0..M9,M1..M9,M0 request yields both orientations on every map; PD has two server versions (6/10
  dragons, 22/28).
- **Q4** (game / cell / run): local − live = +7 … +35 pp for 6/6 sources; common paired cells 0/0/4/1; nearest local
  opponent to 62 or 545 is ≥ 4.7 standardised units away.
- **Q5** (game): six opponents fingerprinted; 62 and 545 are early-swarm eliminators (19–22 units r100), 470 a
  length racer (36 units r250), 45 a low-sonar mid swarm; the band (ranks 60–76) has no controlled data.
- **Q6** (game / dragon-turn): only 9508 is at the cap (69/143 games, 1,096 TLE turns, Portals 37/game); executor
  uploads max 77.5–82.5 M except yuna-v02 97.5 M on unprobed Slithery Fight; faults do not lose games (survivorship).
- **Q7** (dragon-turn / game): a ray costs −0.6 … +1.2 ± 0.5 M (zero within error); 3.9–4.0 rays/turn lines have no
  variance to correlate; the varying lines' correlation is swarm size reading through.
- **Q8** (command): 8540 51 games 383,696 commands 92.2 %; 9663 70 games 581,886 commands 92.4 %; first mismatch
  median round 6–7; dropping all messages lowers agreement 29/29 games (0.904 → 0.832).
- **Q9** (series): 27 ranked series cached; 8 requested by other teams' members at arbitrary times; autoscrims start
  4–36 min after the even hour; executor-upload Elo changes unrecorded (null); net recorded Elo today +26 over 8 series.
- **Q10** (bot version): top 62 all Sparse; live sources ranked 1/9/11/18 locally score 0.29–0.44 live; shrinkage
  reorders but Spearman vs live stays ≈ 0.

## 3. Cross-checks performed

Hub `analysis_a1` and `a1_report.py` agree on every Q1/Q2/Q3/Q6/Q7 number (same pairs, deltas, p-values, counts);
the hub copy (487 games) vs the flat state (486) differ by one game harvested after staging. Codex's v1 field-only
figures (9508: 123 games, 43/27, elimination round 169, compact 28/51, units 6/15) are reproduced exactly as the
field-pool subset. The self-audit's post-change replay-drive figure (91.6 %) is reproduced on today's live games
(92.2 % / 92.4 %) with the same map ordering (Trophy worst, Trauma best).

---

## Appendix — v1 (gpt-6/analysis/codex-session, 12:15 UTC), retained verbatim

# JKS statistics atlas

**Re-derived 2026-09-28 from the available workspace and read-only live record.** This snapshot supersedes handoff inventory counts where the live record has since advanced. Author: `gpt-6/analysis/codex-session`.

## Scope and evidence rules

The legacy live JSON was read by a Python script that selected `results` and computed aggregates; the document does not print the 7 MB state file. Eligible live field rows below are verified, controlled, and `pool=field`. This yields 265 rows in the current snapshot (not the 326 controlled games cited in the 12:00 UTC handoff). The result dictionary has 486 rows; 446 are verified overall. The five large A-side arms cover 265 eligible rows. In those rows, opponent submission strata are 9343 (93), 9433 (90), 6350 (72), and 6985 (10). Counts are games; repeated maps/layouts/opponents within a block are not independent randomized trials. No B-side inference is made.

## Dataset atlas

| Dataset | Unit / headline re-derived | Can answer | Cannot answer / confounds |
|---|---|---|---|
| Live record (`LIVE/state/state.json`, mirrored summaries in `hub-state/`) | Game. 486 result records, 446 verified overall; 265 verified controlled field games after current filters. A-side arms: 9508 n=123, 9663 n=50, 8540 n=31, 9639 n=32, 9980 n=29. Opponent submission mix is heavily weighted to 9343/9433/6350. | Live outcomes, terminal loss reason, stage snapshots, CPU maxima, map/layout and opponent-version strata. | All current field arms are A-side; layout and opponent version are not randomized/constant enough to interpret crude cross-arm differences causally. Missing stage fields remain missing. |
| Live replays and decoded copies | Game/replay. The handoff counted 446 replay files; current state had 486 result records, so coverage must be reconciled by game id before claiming completeness. | Re-derive trajectories and the stored stage aggregates with the frozen decoder. | Replay-driven bot behavior is not a counterfactual unless input/message fidelity is established. |
| Live runtime probes | Dragon-turn, nested in probe/game. Handoff inventory: 16 probes on sandbox 1.0.0. | Per-turn runtime distributions and command/message traces when probe artifacts are accessible. | Probe turns are correlated within games and are not independent games. No turn-level p99 was re-derived in this pass. |
| Legacy diagnostics and lineage notes | Usually game or replay, but each note's own denominator. | Locate hypotheses and historical context. | Not primary evidence; their claims were not accepted without reconstruction. |
| Hub SQLite and `hub-state/` | Game/block/series, depending on table. Snapshot calibration export has 0 rows; five experiment records in JSON summaries. | Periodic analysis, experiment accounting, expectation rows when present. | The live SQLite file is not opened over a mount; no calibration claims are possible from an empty exported row set. |
| Local ledger `game_stats.parquet` and run contributions | Fixture/game. Handoff reports 125,296 games / 280+ versions / 33 maps; those totals were not independently re-derived here because PyArrow is unavailable in this runtime. | Local relative outcomes and toolkit strata where the ledger can be read. | No trajectories; 1.0.0 seeds are null per inventory; bots/opponents are JKS lineages, not representative ladder teams. |
| Local ratings and adaptive campaign | Fixture/model estimate; campaign completion status. Handoff reports 280 active versions, and a 2.58M-target campaign at about 1% complete. | Queue screening after shrinkage and adequate coverage. | Ratings are not truth labels. Sparse fixtures, incomplete campaign, and frozen toolkit inputs limit transfer. Totals remain handoff-reported, not re-derived. |
| Detailed comparison runs and cohort/temporal studies | Run, replay, game, or seed; denominator varies. | Reconstruct lineage experiments from manifests and per-game series; test temporal policies. | Cannot pool without matching bot hashes, map, toolkit, opponent version and seed. No consolidated provenance audit completed here. |
| Public replay corpora | Replay/game, nested by opponent submission version. Handoff reports 135 Vibing++ replays, 288 JKS replays, and direction datasets for teams 470 and 62. | Behavioral fingerprints and replay-drive fidelity on observed public games. | Public sampling is selected, versions differ, and missing values are missing. No ladder-band corpus was re-downloaded/re-profiled here. |
| S1 seeded panels and map facts | Seed/game and map layout. | Mechanism tests and map class definitions. | Panel outcomes are still in progress per inventory; no treatment effect inferred. |

## Re-derived live loss anatomy

The table uses eligible verified controlled field games only; unit is game. Stage entries are medians among all games in that row unless labeled otherwise. It pools A-side play against the four opponent-submission strata above; the opponent-version distribution differs by source.

| Our submission | n | wins / share | losses: elimination / round limit | median elimination round | median losing round-limit margin | units r100: all / wins / losses | total r250: all / wins / losses | longest r400: all / wins / losses | longest r499: all / wins / losses | max CPU |
|---|---:|---:|---:|---:|---:|---|---|---|---|---:|
| 9508 | 123 | 53 / .431 | 43 / 27 | 169 | -11 | 11 / 17 / 6 | 38 / 74 / 4 | 6 / 9 / 0 | 14 / 28 / 0 | 100,000,000 |
| 9663 | 50 | 20 / .400 | 16 / 14 | 161 | -12.5 | 13 / 23 / 8 | 45.5 / 123 / 5.5 | 7 / 8.5 / 0 | 12 / 23.5 / 0 | 97,457,737 |
| 8540 | 31 | 13 / .419 | 10 / 8 | 147.5 | -8.5 | 13 / 17 / 6.5 | 23 / 68 / 13.5 | 6 / 8 / 0 | 15 / 24 / 0 | 77,387,763 |
| 9639 | 32 | 10 / .312 | 15 / 7 | 138 | -9 | 7.5 / 18.5 / 4.5 | 19 / 93.5 / 2.5 | 5.5 / 8.5 / 0 | 10 / 30 / 0 | 79,719,935 |
| 9980 | 29 | 10 / .345 | 12 / 7 | 166.5 | -10 | 11 / 18 / 6 | 50 / 84 / 2 | 6 / 12 / 0 | 13 / 26 / 0 | 77,478,070 |

9508's compact-map sample is 51 games, 36 losses, 28 losses by elimination; open-map sample is 72 games, 34 losses, 15 by elimination. The compact/open units r100 medians are 6.0/15.0 for 9508, confirming the handoff's dated figure. These are descriptive game-level medians, not randomized treatment effects.

## Current analytical limits

Exact paired contrasts, layout-assignment diagnostics, runtime game maxima, and sonar rates are now available as hub pure functions in `tools/hub/analysis.py`; the paired contrast reports independent exact cells (map, side, opponent submission, layout), not every individual game as an independent pair. Historical screen-block matching cannot be presented as a result until the hub mirror contains those historical rows and exact layout keys. Local trajectory transfer, ladder-band clustering, per-turn runtime p99, raw-stdin judge-divergence confirmation, ranked-series Elo attribution, and rating shrinkage remain unresolved for the reasons in `RESEARCH_LIST.md`.

# Statistics atlas — JKS, 28 September 2026

Author `glm/analysis/a1`, from handoff prompt A1. Every number re-derived on 28 Sep 21:30–22:30 local (11:30–12:30 UTC) unless dated otherwise; re-derive before citing later. `LIVE` = `/Users/alik/Documents/Codex/2026-09-27/your-prompt-is-in-the-markdown-2/outputs/live_validation`; repo = `/Users/alik/Documents/Projects/UNSW-Battlecode-2026`; hub = `/Users/alik/Documents/Projects/battlecode-hub` (sqlite snapshot read via copy — never over a mount).

## How to read this atlas

Each dataset gets: what it is, headline numbers, **unit of independence**, confounds, the questions it CAN answer, and the questions it CANNOT. "Verified" always means `verified == true` in the live record (no `error` field).

---

## 1. Live game record (`LIVE/state/state.json` → `results`; mirrored to hub `games`)

**What**: 486 games as of 28 Sep 21:40 local (446 verified, 40 unverified — all unverified carry `error: incomplete API payload`; never counted). 465 controlled / 21 observational; 326 field / 160 dev; 475 side A / 11 side B. Per game: score, reason, rounds, longest margin, faults, cpu_max (cpu_recorded == turns in 100% of checked games), map id/name/hash (starting layout), seed, series, requested time, and **stage curves at r100/200/250/300/320/360/380/400/450/499 with 28 fields each for both us and the opponent**.

**Headlines** (verified controlled field, side A, n=265):
- Sources ≥20 games: 9508 n=123 share 0.43; 9663 n=50 0.40; 9639 n=32 0.31; 8540 n=31 0.42; 9980 n=29 0.34. Dev-only arms: 9573/9604/10013 n=20 each.
- The eventual loser already trails on total length at r100 (first checkpoint) — 94–100% trail by r250.
- Layout is deterministic on 9 of 10 maps: `map_hash = layout chosen by game-id parity`, 0 exceptions / 446 games. Prisoners Dilemma has 4 layouts, no local rule.
- Incumbent 9508: cpu at the 100M cap in 58/123 field games, chronic from r100.
- Team Elo 1784→1742 over the day; team-level (uploads inherit), moved only by ranked games.

**Unit**: the game. **Strata**: own submission (8), opponent team (6) × their submission (pooled — mixing is visible per cell), map (10) × layout (2, Dilemma 4), pool (field/dev), origin (controlled/observational).

**Confounds**: opponents update submissions mid-record (opponent_submission stored — stratify); all our arms are side A; layouts alternate by id parity (paired designs must match layout); field quota favours certain blocks; the 40 unverified games cluster on 10013/9508 (latest hours).

**Can answer**: loss anatomy; paired candidate−control contrasts (exact pairs exist for 4 experiments, 103 pairs); layout assignment; runtime by source/map/round; sonar-outcome within-line splits; Elo trajectory & exposure; opponent fingerprints for faced teams (62/45/470/306 + dev 545/752).

**Cannot answer**: B-side strength (n=11, excluded); per-game Elo deltas (`eloChangeA/B` null locally); message-level judge behaviour (no per-turn message logs); anything about teams we never faced.

## 2. Live replays (`LIVE/state/replays/*.replay`, 446 files, 347 MB; decoded copies `state/decoded/`)

**What**: full trajectories of every live game; the stage curves of dataset 1 are derived from these by the frozen decoder (`LIVE/system/vendor/public_replay_review.py` / `tools/public_replay_review.py`, revision `gzip-errors-v2`).

**Headlines**: 52/446 verified games carry `prior_analysis_errors` from the pre-gzip decoder era — a mid-record analysis break consistent with (not proof of) the claimed 27-Sep judge change.

**Unit**: the game (replay). **Confounds**: decoder revision drift; the self-audit's replay-drive agreement numbers (exact before 13:00 UTC 27 Sep, ~92% after) are NOT reproducible from local artifacts — treat as unverified.

**Can answer**: any per-event question (death locations, conversion timing, per-turn behaviour) for the 446 games, subject to decoder validity.
**Cannot answer**: post-change message-level fidelity — needs the tap-build experiment (see findings, judge-tap spec).

## 3. Hub (`battlecode-hub/hub.sqlite` via snapshot; mirrors `REPO/hub-state/*.json`)

**What**: 13 candidates, 5 experiments (2 reject_screen, 2 superseded, 1 running), 40 blocks, 483 games rows (446 verified with stages), 114 series payloads, 16 probes, 20 ranked_exposure rows, calibration & shadow_checks tables.

**Headlines**: shadow experiment verdicts agree with legacy decisions (agree=1 on all rows). **Calibration table was empty because the deployed hub (app/current, 09:21 UTC revision) predates the calibration-enabled cycle.py — a deployment gap, not a data gap.** The offline run of the new code produced the first 5 absolute rows (all negative disagreement: local − live = +8…+38 pp).

**Unit**: row type (candidate / experiment / block / game / series snapshot). **Confounds**: deployed-revision lag between `tools/hub` (source) and `app/current` (running); a concurrent session is actively editing `tools/hub` in the main checkout (namespace-split respected here).

**Can answer**: everything in dataset 1 plus experiment/block joins (games.block_id) and series Elo snapshots.
**Cannot answer**: anything requiring the live executor's request queue state before import.

## 4. Local ledger (`game_stats.parquet`, union of `game_stats/runs/*.parquet`)

**What**: ~126k games, 299 frozen bot versions, 33 maps; native 119k on unswbc 1.0.0, 4.5k on 1.1.0, 1.7k on 1.2.1 (+616 on 1.0.1); outcomes only (`bot_a/bot_b/sha256s/map/mode/runner_version/seed(outcome-level)/outcome/rounds/runtime_faults`). Live-pool maps subset: 69,260 rows.

**Headlines**: zero (bot,bot,map) cells have ≥3 games in both 1.0.x and 1.2.x strata — **toolkit equivalence is untestable from the ledger**. Local shares of our live sources sit 8–38 pp ABOVE their live shares (calibration rows).

**Unit**: the fixture (bot pair × map), games nested within. **Confounds**: opponents are our own lines (weakness bias vs live band); 1.0.0 seeds null; mode native vs sandbox must not pool; seeds are outcome-level (no trajectories).

**Can answer**: relative local ordering of ESTABLISHED bots (≥60 fixtures, ≥5 opponents, ≥8 maps — after the proposed minimum-evidence rule); paired local deltas on common cells.
**Cannot answer**: absolute live expectation ( disagreement −8…−38 pp, model still band-mean); stage-profile questions (outcomes only); toolkit differences.

## 5. Local ratings (`experiment_data/bot-ratings/latest.{json,md}`, `tools/benchmark_ratings.py`)

**What**: 299 active versions, model-adjusted score vs a reference panel, refreshed 12:22 UTC.

**Headlines**: 8 of the top 26 rows have n=2 fixtures; entire top-26 Sparse; the two director probes (tidus-t02 77.6% local vs 0.34 live; fenrir-v18 78.9% vs 0.43 live) confirm direction. Proposed rule + patch shipped (`tools/analysis/rating_evidence.py`, patch in `tools/analysis/patches/`) — after it, n=2 rows sink to ranks ≥220 and the top-12 is all-established.

**Unit**: bot (score is a model prediction vs a panel, not a win rate). **Confounds**: sparse rows extrapolate from the prior; panel ≠ live band.

**Can answer**: queue ordering over established rows as a PRIOR only.
**Cannot answer**: live-share prediction, sparse-row comparison (display-only under the rule).

## 6. Adaptive campaign (`experiment_data/benchmark-current.json` → benchmark_20260928064036195154)

**What**: 280 bots × 33 maps, 2.58M target fixtures, ~1% done, frozen 1.0.0 inputs, replays kept.

**Unit**: fixture. **Confounds**: frozen toolchain/roster; Portals/Slithery weight 0 in the campaign weights (two live maps have no campaign evidence).

**Can answer**: slow accumulation of paired local evidence under fixed conditions.
**Cannot answer**: anything fast; anything about the two zero-weight live maps.

## 7. Detailed comparison runs (`experiment_data/<bot>_<ts>/`)

**What**: ~600 dirs; per-run manifest (provenance hashes), results.json (final counts both sides), games.csv, and per-game `stats/*.json` with **per-round series for both sides** (units/total/longest/deaths causes/space share).

**Headlines**: per-round series exist — trajectory matching is possible in principle; in practice only tidus-t02 has runs as candidate (2 dirs, 74 games); the other five live-mapped bots have none.

**Unit**: the game within a run; runs differ by manifest (never pool without checking hashes).

**Can answer**: local trajectory profiles for bots with runs; mechanism forensics for lineage claims.
**Cannot answer**: live-vs-local trajectory matching for 5 of 6 mapped sources (missing runs) — needs the live-pool panel.

## 8. Public replay corpora (`experiment_data/team_recon_*`, raw `public_replays/`)

**What**: Vibing++ (306, 135 replays, byte-exact + IL models), our own team-7 (288), 龙虎豹 (470), Heartbreaker (62), plus battle-* (2.7 GB). Band teams (±8 ranks): **zero replays locally**.

**Unit**: replay; versions differ within a team — stratify by submission id. **Confounds**: selection (newest N), era drift.

**Can answer**: opponent modelling for 306/470/62/team-7; mimic recipes (306's §5a is the clone recipe).
**Cannot answer**: the ladder band we actually climb (needs API download — executor/director action).

## 9. Legacy diagnostics (`LIVE/state/{phase_diagnostics,critic,timing_check}.json`, `LIVE/*.md`)

Earlier analyses of the same record. **Treat as hypotheses**; where re-derived here, current numbers supersede (e.g. the handoff's "units r100 6 vs 15 on open maps" for 9508 is now 15 vs 16 on open / 6 vs 19 on compact over a larger n; its "28 of 51 compact eliminations" re-derives exactly at 28/51).

## 10. Map facts (`REPO/maps/*.map`)

Live pool 10 maps (Portals 32×16 20 portal pairs; Schooltime 60×40; Default 32×32; Autarky 54×18; Trauma 48×24; Dilemma 32×16 4 pairs — **4 layouts, see dataset 1**; Slithery 63×27 (14 dragons); QoS 25×35; Trophy 25×25; Devil 32×16 0 portals). Compact = Portals, Dilemma, Devil, Trophy — where eliminations concentrate.

---

## Cross-dataset rules learned this pass

1. Never pool verified with unverified live games (40 exclusions, all timestamped latest hours).
2. Always pair by (block, map, layout, opponent submission); layout = id parity on 9/10 maps.
3. Local absolute shares are optimistic by 8–38 pp — cite only alongside a calibration row.
4. Sparse rating rows (n<60) are display-only under the proposed rule.
5. Opponent submission ids must be stated when pooling an opponent team's games.

## Where the numbers live now

Recurring: `tools/hub/analysis.py` (profiles, contrasts, layout parity, runtime, sonar, Elo trajectory, trailing) and `tools/hub/calibration.py` (absolute/paired rows, opponent fingerprints, priority gate) — recomputed every hub cycle once the current `tools/hub` is deployed. One-off scripts + this pass's outputs: `tools/analysis/` (README inside).

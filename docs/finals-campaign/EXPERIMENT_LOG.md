# Experiment log and handoff history

> Chronological evidence and status at each checkpoint. Older entries are historical; use [the root handoff](../../FINALS_WORKING_MEMORY.md) for the current state. Keep measured outcomes separate from proposals.

## Live task board and experiment ledger

| ID | Task | State | Next evidence |
|---|---|---|---|
| S01 | Confirm environment, actual active bot and 61 completed trial | DONE | All 60 trial-window replay headers attributed to 18078; 29W–31L; engine/source/environment pinned |
| S02 | Unseen-map baseline for Bokuto 18 | DONE: initial screen | Four fresh maps, both seats, explicit seed; `build/finals/20261006-baseline/` |
| S03 | Reproduce/test corridor escape and congestion changes | DONE: narrow screens | 62 not retained; 63 remains developmental (5–3 direct, interval includes zero); no combination/promotion |
| S04 | Pure option/packet interface with baseline parity | DONE: initial bridge | 26,159 exact replies + full episode parity; data/export works; sampled rollout 7,448 decisions/15.98s, zero overrides/faults |
| S05 | Action model with fixed sonar | TRAINED + DEVELOPMENT SCREENED; NOT RETAINED | u10 tied18 4–4 in the common four-arm screen; no separate confirmation planned |
| S06 | Sonar model with fixed retained action policy | EVALUATED: NO MEASURED GAIN | C++ parity passed; greedy chose BASELINE on all 140,439 selectable final-training rays; 4–4 vs18/Kenma |
| S07 | Four-arm selection, judge probe and live corroboration | FOUR-ARM SCREEN + SUPPRESSION CONFIRMATION DONE; NO QUALIFIED REPLACEMENT | Suppression lost83–91 on29 maps; score advantage−0.023, 90% interval[−0.086,+0.040], zero faults; action/sonar/combined tied18 on development fixtures; keep18 |
| S08 | Independent confirmation for 63 | FAILED FROZEN GATE | 174/174; candidate 86W–88L, 0 errors; advantage +0.00575, 90% map-cluster CI [−0.05172,+0.06322]; 0 replay faults; source-family sensitivity also crosses zero |
| S09 | Verify chosen active submission before lock | DONE: FALLBACK ACTIVE | Fresh authenticated read confirmed 18078 active /17791 idle; guarded activation of 17791 succeeded; immediate readback confirmed 17791 sole active with expected server source hash; recheck before qualifier lock |
| S10 | Snapshot eligible qualifier field | DONE: ONE LIVE SNAPSHOT | 984 roster rows; 335 eligible, 171 currently ranked eligible; team 7 at rank 52 among ranked eligible; no seed/bracket yet |

## 6 Oct 2026, 21:47 Adelaide — live eligible-field snapshot

- Read-only authenticated `GET /api/v1/leaderboard`; compact output saved to
  `build/finals/20261006-eligible-field-baseline/summary.json`.
- API returned 984 roster rows; 335 teams were marked eligible, of which 171 had a current numeric
  ladder rank. Just Keep Swimming (team ID 7) was eligible, rank 69 overall, Elo 1825, and rank 52
  among currently ranked eligible teams. The tenth eligible team by current rank was overall rank
  11 at Elo 2245 (raw gap: 420).
- This snapshot records the ladder proxy only. It gives no qualifier seed/bracket or unseen-map
  estimate; update after post-lock autoscrims and inspect source-attributed games before selecting
  likely opponents.
- Follow-up at 21:54 Adelaide: sampled up to two recent ranked series for each of the ten highest-
  ranked eligible teams: 17 distinct series / 85 game rows. Battle metadata exposed no submission
  IDs. Downloaded one replay per series under ignored `build/finals/.../replay-samples/`; all 17
  headers had empty bot labels. Compact records are in `opponent-series-sample.json` and
  `opponent-replay-headers.json`. This is a match/map sample, not exact source attribution or a
  strength estimate; recover bot versions before treating these as opponent controls.

For each completed experiment append: date/time, hypothesis, parent/candidate source fingerprints,
map/opponent/seed/seat selection, train-versus-confirmation split, checkpoint/config hashes, commands,
output path, W/D/L/errors, interval, queen/material diagnostics, verdict and next action. Record
failures as well as wins. Avoid narrating predicted gains as measured outcomes.

- **6 Oct documentation handoff:** this plan and task board created; S01–S08 remain TODO.
  No baseline tournament, bot change, model training, server read/activation or promotion was performed.
  Validation: `git diff --check` passed; local Markdown links and code fences checked; the documented
  tournament dry run passed (2 bots, 2 maps, 4 both-seat matches). No games were started.
- **Original handoff next session (superseded by execution entries below):** start S01/S02, then execute the compressed 6 October work. The user intends to
  switch to Luna; this file is the continuation record. Do not re-ask hardware/budget/deadline questions.

Open details at the original handoff (CPU/RAM now inspected): friend availability;
fresh confirmation map generation; current authenticated submission state; rollout throughput; actual
action-menu coverage. None prevents initial local inspection and bounded baseline work.

- **6 Oct first execution block (~13:30 Adelaide):** started S01/S02. Checkout `6985391e6351`;
  16 logical CPUs, 14 GiB RAM, ~5.1 GiB available at inspection; toolkit `unswbc 1.2.9` in
  `.venv/bin`. User edits/untracked work preserved. Read-only authenticated server requests
  confirm active 18078 and idle 17791; no upload/activation or hub queue changes.
  Recent API index has 12 ranked series since the recorded 61 activation (29W–31L), but
  this is a **time-window tally pending full submission attribution**, not a verified trial statistic.
  Latest series 1200394 scored 4W–1L against NUSW Battlecode; its first replay explicitly
  identifies our submission as 18078. S01 remains in progress until the other games are attributed.
- **Baseline experiment:** parent/control `bokuto-18-queenfeed` source SHA256
  `de24f29affb7491c7c0e0111e27c948b2a01b5c52f9f8c300a409be48b1e6c09`;
  opponent `kenma-03-pocket-queen` SHA256
  `1539ff08343de8753a43366a482ad539d8e7193ef4b04ff1e38426f1d08ac156`.
  Fingerprint method: tournament `fingerprint`, relative paths plus bytes for `.cpp/.hpp/.toml`.
  Fresh Verso generator seeds 6100601–6100604, game seed 61006, both seats, one worker,
  180-second per-game bound. Four map styles: scatter/mixed, maze/remote, maze/wells,
  open/uniform. These are now **development** fixtures; none remains a confirmation holdout.
  Commands: documented tournament dry-run (passed), then
  `.venv/bin/python build/finals/20261006-baseline/run.py` and
  `.venv/bin/python build/finals/20261006-baseline/analyze.py`.
  Output: `manifest.json`, `results.json`, `summary.json`, `economy-diagnostics.json`, logs,
  replays and reproducible runner under `build/finals/20261006-baseline/`.
  Result **5W–0D–3L**, zero runner errors, zero remaining decode errors, zero replay TLE flags
  (native runs; judge points unmeasured). Initial diagnostics used numeric team labels but
  decoder returns A/B; corrected and reprocessed all saved replays without counting failed
  diagnostics as strategic losses. Score 0.625, 90% four-map-cluster bootstrap interval
  [0.50, 0.75]; descriptive small-screen uncertainty, **not an improvement-over-fallback gate**.
  Start-of-round carried totals: r100 44.625, r300 66.5; queen alive r100 8/8, r300 6/8.
  All games reached those rounds. Five queen deaths, all head-to-head; worker/team deaths:
  432 head-to-head, 170 self, 61 wall, 36 body. Different starting lengths/map mix mean these
  totals cannot be compared directly with the historical top-ten material figures.
  Open/uniform map 6100604 was strongly seat-sensitive: Bokuto r300 total 3 in A versus
  254 in B, with matched opponent totals 271 versus 6. Specific failures are saved in
  `economy-diagnostics.json` and `summary.json`; no corridor-order defect established yet.
  Verdict: useful baseline and diagnosis fixtures; retain immutable 18, proceed to S03
  reproduction, then isolated snapshots and matched screens. No model training or promotion.
- **Repeatability check:** replayed map 6100602, Bokuto A, seed 61006. All **19,324 actions**
  (excluding CPU timing) and all round body snapshots were identical; winner A in both runs.
  `repeat-check.json` contains action digests; repeat game is excluded from the 8-game score.
  Native toolkit warns that game seeds do not seed bot random APIs; inspected sources of both
  bots contain no random/time API calls. One identical fixture establishes this bounded check,
  not universal judge/export parity. `git diff --check` passed after the documentation updates.
- **6 Oct S01 attribution (~13:47 Adelaide):** all 60 ranked game headers across the twelve
  series since the recorded 61 activation identify our submission as **18078**, with seats
  resolved independently per replay. Verified trial-window tally **29W–0D–31L**. Common 1725
  anchor residual +0.0912, 90% series-cluster bootstrap [-0.0243, +0.2145] (5,000 resamples,
  seed 61006). Opponent ratings come from the series API index, not exact per-game pre-start
  ladder snapshots; do not treat this as perfectly matched to 18's historical estimate.
  Output/commands: `.venv/bin/python build/finals/20261006-trial61/attribute.py`, generated
  series metadata, all sixty replays, `attributed-games.json`, `summary.json` under that path.
  Verdict: no evidence sufficient to replace atlas-free fallback 18; 61 remains the active
  server artifact but is not promoted for unseen maps. No activation or game requests.
- **S03 initial failure reconstruction:** added `tools/finals/replay_probe.py`, which builds
  an instrumented copy under `build/`, reconstructs each selected dragon's legal local-replay
  history and compares emitted commands to recorded actions. Maze 6100602/A: 20 workers,
  823 turns, **zero action mismatches**. One production/escape masking state (dragon 38,
  r185, len4, all move scores -1001, production -22) selected SPLIT 2; the escape size is
  also 2, so this state **does not prove an ordering defect**. Early sampled wall/self deaths
  were len2–3 workers with no escape split available; full body was represented. Broader
  probes pending. First compilation failed because the official helper requires C++20;
  corrected diagnostic compile standard without changing the helper. Open/uniform 6100604/A
  has no wall/self worker deaths; its economy collapse requires contact/production diagnosis.
- **S03 broader probes and isolated snapshots:** portal-maze 6100603/A: 17 workers, 1,344
  turns, zero mismatches and zero masked escape cases; open/uniform 6100604/A: 20 contact
  victims, 1,281 turns, zero mismatches and zero masking. Total offline action reproduction
  across the three probes: 3,448 turns. Constructed full-body six-segment corridor fixture
  (`build/finals/20261006-ordering/reproduce.cpp`) reproduces 18 choosing SPLIT 2 although
  tail escape SPLIT 4 exists. Guard also changes the larger proposed rescue back to 2.
  New **`bokuto-62-escape-priority`** tests larger tail rescue before production when all
  movement is structurally DEAD/H2H, with a matching guard exception for that deliberate
  worker sacrifice; queen/crown/feeder handling and global reserve preserved. Corrected
  fixture passes with actual guarded SPLIT 4. First screen was accidentally launched before
  compilation completed; a misplaced declaration caused **16 build errors, zero games**,
  preserved at `build/finals/20261006-escape-screen/`. No errors counted as strategic losses.
  Corrected serial screen `build/finals/20261006-escape-screen-r2/`: **4W–4L vs 18**, **4W–4L
  vs Kenma 03**, four same development maps, both seats, seed 61006, zero runner errors.
  Against Kenma this is below incumbent's 5W–3L; **do not retain/promote 62** from this screen.
  New **`bokuto-63-resource-crowding`** independently discounts known resources with multiple
  nearer visible allied heads; one-head discount/exploration/queen behavior stays fixed.
  Its matching 16-game screen is running at `build/finals/20261006-crowding-screen/`.
  Screen command pattern: `.venv/bin/python tools/finals/screen.py --candidate <snapshot>
  --opponents bokuto-18-queenfeed kenma-03-pocket-queen --maps <four baseline fresh maps>
  --seeds 61006 --output <screen path>`, with the same command plus `--dry-run` first.
  Source and map hashes/frozen bot sources are in each `manifest.json`/`sources/`; one worker,
  180-second game bound. No combination or confirmation comparison justified yet.
- **S04 first interface:** new **`bokuto-64-option-chassis`**, independently from immutable 18,
  stages incumbent decision/inbox memory/guard on copies once per turn, proposes a bounded
  deduplicated semantic menu, masks guard-replaced commands, and commits only the chosen
  state/action. Queen/crown/feeder/rescue turns remain fixed; candidate features use legal
  protocol/memory only. Protected type 1/3/7 packets retain incumbent templates and send order.
  Baseline reply parity on all team-A histories of the four baseline games: **26,159 complete
  protocol replies identical**, including movement, logs, sonar payloads and ordering.
  `tools/finals/parity.py` output: `build/finals/20261006-option-parity/report.json`.
  `python3 tests/test_finals_options.py` passed state-isolation, deterministic enumeration,
  deduplication, legal selected commit, one-time memory update, reserve/queen protection,
  repeated-commit rejection, packet round-trip and protected suppression tests.
  This is integration evidence, not strength. **64 is frozen at this interface**; extended
  action/sonar collection is being built separately as **`bokuto-65-policy-collector`**.
  PyTorch 2.14.1+cu130 is installed but CUDA is currently unavailable; use CPU inference and
  profile the complete collector before choosing optimization hardware. No training yet.
- **S03 congestion result:** 63 scored **5W–0D–3L against 18**, **5W–0D–3L against Kenma 03**,
  zero runner errors on matching four-map/both-seat/seed61006 development fixtures. Direct
  score advantage +0.125, 90% four-map-cluster interval **[0, +0.25]** (5,000 resamples,
  seed61006). Weak positive development screen; no supported promotion and no combined bot.
  Output `build/finals/20261006-crowding-screen/`, including source/map hashes and `interval.json`.
  Freeze 62/63 sources; retain 18 while building learned choices. Any later 63 claim requires
  a broader matched screen and untouched fresh confirmation.
- **S04/S05 collection and clone:** collector 65 exchanges lawful encoder/candidate arrays
  with Python through a compile-time-only RPC handshake; both default selectors are BASELINE.
  Action and sonar features include selected/post-move geometry and required-packet masks;
  no receiver changes/new packet types. Full seed61006 maze/A episode against Kenma reproduced
  **all 19,324 action events, sonar events and round body snapshots exactly** versus the
  reference replay. 9,403 team decisions; 3,998 singleton menus and 5,405 selectable menus
  (57.48% coverage). Candidate counts: baseline9,403, forage744, disperse4,480, escape3,
  bed1,260, produce5. This indicates limited escape/production coverage, not learned strength.
  First profile 15.29 s total, JSON/array conversion1.28 s; repeat with full float32 telemetry
  precision and actual-command arrays 14.98 s total, JSON1.23 s. No overrides or runner faults.
  Data, replay, summaries and pinned bridge/opponent/source hashes are in
  `build/finals/20261006-collector-profile-r2/`; original profile/clone training data is retained
  under `build/finals/20261006-collector-profile/` (six-significant-digit features, baseline labels).
  An initial collector attempt failed its credit assertion because it treated the engine's
  final zero-based round label as a round count and subtracted one. Corrected to terminal
  `EngineModule.rounds` (499 here); CLI's printed count is +1. No failed episode trained on.
  `tests/test_finals_credit.py`: 3 tests passed, covering inclusive terminal boundary, actual
  round gaps, interleaved dragons, births/donor death, signed result/draw and per-round weights.
  Current shaping is **none**, gamma0.997, terminal team result only, complete episodes only.
  The collector retains actual commands and an actor-valid flag for unexpected guard changes.
  Action clone: 32 hidden units, audited1193 encoder inputs +32 candidate features, five epochs
  on 5,405 selectable incumbent-labelled training rows; training argmax accuracy100%, final
  cross-entropy0.2574, optimization0.323 s (one CPU thread). Output
  `build/finals/20261006-action-clone/`; checkpoint SHA256
  `c3c1118bc78f8f6bbe8430542b13df60b3fc90c8c16dabf44f92785c80892c71`.
  C++ export parity on1,000 selectable rows: zero argmax mismatches, maximum score error
  1.44e-6 (tolerance2e-5), `build/finals/20261006-action-export-parity/`.
  A sampler smoke episode against **18**, sonar fixed, seed61007, is running at
  `build/finals/20261006-action-collection-smoke/`; it is throughput/integration evidence,
  not a candidate confirmation. Clone training accuracy is not held-out strength.
  Validation: tournament runner's10 tests passed; Python compile and diff checks passed.
  `ctest`/`cmake` are unavailable on PATH; registered tests are being run directly using
  their existing CTest manifest and available native binaries, with reports under
  `build/finals/20261006-checks/`. No CMake/CTest pass is claimed.
- **S04 sampled actor profile completed:** fixed incumbent sonar, cloned action sampler versus
  frozen 18, maze6100602/A, seed61007: one loss, 7,448 decisions, zero overrides/faults,
  15.98 s end-to-end (466 decisions/s), actor inference1.88 s, JSON/arrays1.07 s.
  `build/finals/20261006-action-collection-smoke/` pins executable/source/checkpoint hashes
  and retains actual commands plus team credit arrays/replay. This is not a paired evaluation
  or evidence of strength. Combined collector/inference/clone optimization path is working
  on CPU; no GPU/rental/overnight dependency needed for this initial loop.
  Remaining S05 work is PPO, frozen-opponent development and fresh paired confirmation;
  S06 remains unstarted until the retained action policy is established. No claims that a
  learner beats 18. Registered regression sweep:18/20 passed initially; two failed because
  Hunter14/15 reference executables were missing, not because of assertion differences.
  Rebuild those references directly and rerun their narrow checks (CMake/CTest unavailable).
- **Registered-check follow-up:** rebuilt Hunter14/15 with g++ C++17/Release flags, without
  editing their snapshots. Hunter14's6 checks passed. Hunter15 passed3/4 but its existing
  unmatched-portal scout fixture expected MOVE N and emitted MOVE E. Both the source and
  test exactly match Git HEAD (`build/finals/20261006-checks/untouched-hunter15.json`);
  this is an untouched historical reference failure, not a finals API regression. Keep the
  measured control immutable. Overall registered-command coverage:19/20 test commands pass
  after rebuilding, with that one existing failure; CTest itself is unavailable. New finals
  isolation/legality/packet and team-credit checks all pass. Repeat collector profile-r2's
  actions, sonar and round states exactly match the baseline replay; reference source hash
  remains unchanged. Do not describe the broad suite as fully green.
- **S05 PPO initial run:** implemented `tools/finals/ppo.py`, tested episode/round loss
  weighting and a joint four-ray sonar likelihood (2 PPO contract tests passed). Current
  run is action-only with incumbent sonar fixed, complete-episode terminal returns,
  gamma0.997, no shaping/GAE, separate training-only local critic, clipping0.2,
  entropy0.01, Adam3e-4, three epochs/update, batch256, one CPU thread, one serial collector.
  Two updates/four games each against **18** completed on the four development maps,
  both seats and paired seeds61100–61103: sampled training outcomes **1W–7L**, zero
  overrides/faults; 39,933 decisions, 23,078 selectable. Collection115.71 s total,
  optimization2.72 s. Output `build/finals/20261006-action-ppo-smoke/` pins config,
  scripts, executables/maps and all per-game arrays/replays. These are training outcomes,
  not a greedy held-out evaluation. Resume verified from the saved latest checkpoint;
  expanded bounded run is **10 updates / 40 total games**, using the deterministic roster
  schedule (first8 versus18, next8 versusKenma, repeating). **Currently running**, tool
  session23651; poll its handle or inspect update reports before restarting.
  C++ actor export for update2 is under
  `build/finals/20261006-action-artifact/bokuto-66-action-u2/` (generated models kept in
  build/, atlas data physically removed). Source artifact hash
  `21a2a377499b5e8867e0b4ef9b0c5ac5a2ce740488c5163c4b5bc1b887161138`.
  Update2 score parity on1,000 rows: zero argmax mismatches, max error1.44e-6.
  On 26,159 incumbent-history replies, learned argmax changed just **one** command
  (open map, dragon10, turn73: W→E), with radio unchanged. This is expected policy
  divergence, not default-interface parity failure; trace verification of that choice
  pending. No strength inference yet. Next: finish bounded run, export frozen checkpoint
  using `export_bot.py`, then a paired greedy development screen versus18 and keeper
  controls before any fresh confirmation or action retention decision. Do not train sonar
  simultaneously. No upload/activation or paid resources.
- **S05 bounded run finished:** verified session23651 terminal; all **10 updates / 40 games**
  completed, **175,364 decisions**, 101,742 selectable, zero overrides/faults. Sampled training
  outcomes **9W–0D–31L** (not a held-out greedy score). Collection503.41 s, optimization10.48 s.
  Frozen update10 checkpoint `update-010/checkpoint.pt` SHA256
  `af302e61b794ac68b7a29918076322c8ebd66ad024f8e3ab7c969f9d19c1aca0`;
  aggregate `build/finals/20261006-action-ppo-smoke/summary.json`. Resume actually restored
  actor, critic, optimizer and RNG state after update2; no training is currently running.
  All eight update1/2 games used18, updates3/4 usedKenma, then that roster schedule repeated.
  The single update2 forced-history changed choice (dragon10/r73, BED E instead of baseline W)
  was traced: Python and exported C++ both select index1, with no guard override;
  `build/finals/20261006-action-artifact/changed-choice-check.json`.
  Update10 standalone artifact is being compiled at
  `build/finals/20261006-action-artifact-u10/bokuto-67-action-u10/`; source/model checkpoint
  archived separately under build, large weights never added to tracked snapshots. The
  exporter logs unexpected guard changes even without training trace. Evaluation harness
  now freezes map bytes as well as bot sources and pins the exact engine WASM hash.
  New `analyze_screen.py` checks native runtime faults, queen/material carried totals and
  map-cluster scores; congestion63 reanalysis confirms5–3 direct with interval touching zero
  and zero runtime faults (`build/finals/20261006-crowding-analysis/`). Action retention,
  sonar training, fresh confirmation and judge/server verification remain incomplete.
- **S05 greedy development evaluation:** frozen **`bokuto-67-action-u10`** artifact source
  SHA256 `a8b0176ee5cb5be22ec1d13e8b179b792f447c3ac2d87de230bb469d75fbacde`, archived
  update10 checkpoint `build/finals/20261006-action-artifact-u10/bokuto-67-action-u10.action.pt`.
  Four training/development maps, both seats, new game seed61200; **5W–0D–3L vs18**,
  **4W–0D–4L vsKenma03**. Matching18-vs-Kenma fixtures also4–4; paired keeper score delta
  exactly0. Direct advantage+0.125, 90% four-map-cluster interval **[0,+0.375]**;
  no runtime faults, no missing pairs. Diagnostics: versus18, queen alive at start r3007/8,
  carried material77.75; versusKenma r3005/8 and75.0. Development data, not pristine holdouts.
  Commands `screen.py --candidate bokuto-67-action-u10 --candidate-dir <artifact> --opponents
  bokuto-18-queenfeed kenma-03-pocket-queen --maps <four development maps> --seeds61200`,
  plus matching reference candidate18/opponentKenma; both dry-runs passed. Results:
  `build/finals/20261006-action-u10-screen/`, `...-reference-screen/`, `...-analysis/`.
  Update10 C++ score parity1,000 rows passed (max2.39e-6, zero choice mismatches).
  **Retention decision:** insufficient support to replace incumbent action; freeze action
  to **exact BASELINE** for sonar stage. U10 remains a research arm for later expanded/four-arm
  selection, not a promoted or rejected-final candidate. No174-game confirmation yet.
- **S06 preparation:** new **`bokuto-68-sonar-history`** from frozen65 adds an actual-previous-
  send match feature (packet feature25; message count already exists in the encoder) and
  fixed singleton packet menus on intentional feeder/cull death turns, which cast nothing.
  Receiver semantics and action candidates unchanged. Default policy matched all26,159
  complete baseline replies; `build/finals/20261006-sonar-history-parity/report.json`.
  RPC build being prepared as `build/finals/sonar-history-rpc`; warm-start data must use this
  packet schema, not65's old message-count feature25. `export_bot.py --chassis bokuto-68-sonar-history`
  supports the new feature schema and archives checkpoint bytes beside generated artifacts.
  No sonar actor trained yet. All required beacon/handoff templates remain protected.
- **S06 warm-start and staged run:** new68 warm-data episode versus18, maze6100602/A,
  seed61300, both selectors BASELINE: 9,989 team decisions, no overrides/faults,18.84 s,
  `build/finals/20261006-sonar-warm-data/`. Sonar clone: 31,073 selectable ray menus,
  five epochs, training accuracy100%, CE0.00933, optimization1.17 s;
  `build/finals/20261006-sonar-clone/sonar.pt`, SHA256
  `3f1e76a724533e8e40b30b79daa044f3f44251aedb69389e43f4f7ea02143c69`.
  C++ parity1,000 ray rows: zero argmax mismatches, max2.39e-6. Post-action geometry and
  actual previous-send feature test passed (`tests/test_finals_sonar.py`). Joint sampler
  now evaluates the shared context once for four rays and respects singleton/protected menus;
  PPO contract tests3 passed. Current sonar run: **two updates / eight games**, fixed exact
  incumbent action, same complete-episode team objective/hyperparameters as action stage,
  seeds61400–61403, one worker, `build/finals/20261006-sonar-ppo-smoke/`.
  **Running tool session1716**; poll the
  active handle before restarting. Critic is training-only; no simultaneous action updates.
  New runs archive PPO/model/collector source bytes; the old action run's exact matching
  source bytes were archived before joint-sampler changes. Collection now also saves an
  explicit terminal-only team-round reward timeline and opponent executable identity.
- **Inherited model audit:** incumbent18 has **active frozen HB1 direction GBT prior**
  (`params.hpp: hb1_dir_lambda=1.0`), used in BASELINE command proposals. It is retained
  as a fixed chassis dependency for exact parity; the new action/sonar actors are the two
  trained selectors, and the training critic is not exported. Do not describe combined
  artifacts as containing only two ML inference components: final model-count/CPU/ZIP
  review must explicitly include this legacy prior. No extra critic or new third actor.
- **S06 initial PPO completed/resumed:** two updates/eight sampled training games versus18
  completed **4W–4L**, 62,112 decisions, 61,682 selectable joint-ray decisions, zero
  overrides/faults; collection163.18 s, optimization3.38 s. This is not a greedy evaluation.
  Verified session1716 terminal, then resumed to **10 updates / 40 total games**, current
  **tool session81965**. Scripts/checkpoints/arrays/replays are under
  `build/finals/20261006-sonar-ppo-smoke/`; source archives and immutable per-update
  checkpoints are retained. Action remains exact incumbent BASELINE throughout; no joint
  action optimization. New controlled optional-packet suppression artifact
  `build/finals/20261006-suppression-artifact/bokuto-69-optional-suppression/` keeps only
  type1/3/7 packets, preserving their original send order. Its forced-history parity check
  (all other replies exact, expected optional SONAR lines removed) is running. Evaluate
  learned sonar versus both fixed incumbent sonar and this suppression arm on actual
  receiver-dependent engine rollouts after freezing the checkpoint.
- **Current handoff:** sonar session81965 was polled live at update5/game3; do not restart
  it just because observation expired. Updates3/4 added3 training wins in8 games versusKenma
  (training outcomes only); zero overrides/faults through completed updates. Suppression
  control passed **26,159** reply comparisons with only expected optional packets removed,
  including protected packet values/order and all commands; report
  `build/finals/20261006-optional-suppression-parity/report.json`. Source hash
  `d44bb10fa95759f1d8ce192747eb6a3a38354c2f1c3bd85f01721244b2511af0`.
  Final diff and Python compile checks passed; all new finals tests passed. The untouched
  Hunter15 portal-scout failure remains recorded; do not claim full CTest success.
  Existing user changes remain unstaged and untouched. No server upload/activation,
  paid compute, overnight dependency, promotion or174-game confirmation happened.
  Remaining scope: finish/evaluate sonar, four arms/fresh confirmation, judge/export/ZIP
  faults and final server artifact/active-submission verification before the lock.

- **Status question revalidation:** polled session81965; verified terminal exit0. Sonar completed10 updates/40 training games, **16W–24L**, **282,810 decisions**, zero overrides. These are sampled training outcomes, not evaluation wins. Aggregate/hashes/timings in `build/finals/20261006-sonar-ppo-smoke/summary.json`. No training job remains live; next export and evaluate frozen sonar update10 versus incumbent and suppression, then four arms/fresh confirmation/judge/submission verification. Goal remains active.
- **S06/S07 frozen-policy verification (6 Oct, afternoon):** update10 sonar checkpoint SHA256
  `c6bc1ba0bd1abb395dd84878134a31a4c1b26b959ab9cecfe807372fe37d9f3f` exported as
  `bokuto-70-sonar-u10`, artifact SHA256
  `be130371c90697d5e5252628cc69e106b3834199b8569dc90dc06b15079a643f`, parent68 unchanged.
  C++/PyTorch parity on1,000 ray menus: zero argmax mismatches, max score error2.3872e-6
  (`build/finals/20261006-sonar-model-parity/`). On the four final-update training episodes,
  final greedy sonar chose baseline candidate0 on **all 140,439 selectable rays**; no protocol
  changes versus action-only on26,159 incumbent-history replies across four development maps.
  This is direct evidence that the exported greedy actor stayed at incumbent packet choices on
  measured states; clone/PPO training wins are not strength evidence.

  Common development comparison used the same four already-seen maps
  `fresh_6100601`–`fresh_6100604`, both seats, seed61500, one worker, no runtime errors. The
  action-only, sonar-only and combined arms each scored4W–4L versus18 and4W–4L versusKenma03;
  all three had matched keeper delta0 over eight map/seat pairs (90% map-cluster interval[0,0]).
  Combined is an un-fine-tuned pairing of frozen actors. Optional-packet suppression scored
  6W–2L versus18 (direct advantage+0.25, 90% interval[-0.25,+0.5]) and5W–3L versusKenma;
  matched keeper delta+0.125, 90% interval[0,+0.375]. Suppression minus learned-sonar paired
  deltas were+0.25 versus18 (interval[-0.25,+0.5]) and+0.125 versusKenma (interval[0,+0.375]).
  Intervals include0; this is a development lead only. Full reports:
  `build/finals/20261006-four-arm-comparison/summary.json`, individual `*-analysis/summary.json`.

  Sandbox check on `bokuto-70-sonar-u10` versus18: 8/8 games across the same four development
  maps and both seats, seed61501; zero runner faults, TLEs or invalid-action deaths. Over66,035
  candidate turns, peak CPU14,089,732 points (p99 11,094,275) and peak memory7,471,104 bytes.
  The artifact's local24-file ZIP is3,978,680 bytes and passes ZIP integrity; official submission
  size limits were not queried, and no upload/activation occurred. Sandbox logs and resource
  report are in `build/finals/20261006-sonar-sandbox-screen/`. This validates the learned-sonar
  artifact's tested runtime budget, not its strength. The four development maps above are
  permanently used development fixtures; the later one-shot confirmation uses a separate audited
  map set.

- **S07 one-shot suppression confirmation (6 Oct):** The 29 seeded maps are the repository's22
  `tools/ouroboros/holdout` maps designated never-tune, plus seven unique T-FX transforms of
  current map sources (`autarky`, `dilemma`, `islands`, `maze`, `portals`, `stripes`, `weakhold`).
  Names and SHA256 hashes were checked against 2,325 prior build manifests/results with no matches;
  content hashes are unique. All29 passed a map-validation game against `verso-00-base` in both
  seats with no map correction/error. Provenance and hashes:
  `build/finals/20261006-suppression-confirmation/confirmation-map-manifest.json`; per-map checks
  are in `map-validation.json`. The separate `tools/verso/mapgen.py` data-only maps were not scored;
  its self-check discarded one malformed map and accepted29, which did not enter this confirmation.

  Candidate `bokuto-69-optional-suppression`, source fingerprint
  `d44bb10fa95759f1d8ce192747eb6a3a38354c2f1c3bd85f01721244b2511af0`; fallback source in this
  runner `fa93106401b1fef54a92a429e3430200f4618d2056206035deaebf9935e6a287`. Fixed seed set
  61510–61512, both seats, one worker: **174/174 direct games**, candidate83W–91L, zero draws,
  runner errors, TLE flags or invalid-action deaths. Candidate score0.477; direct advantage−0.023,
  90% map-cluster interval[−0.086,+0.040] over29 map clusters. Candidate carried material averaged
  55.51 at r100 and92.56 at r300; queen alive in77.0% at r100 and48.3% at r300 (174 games; fewer
  than174 reached r300). H2H/body/self/wall queen deaths:71/9/10/20. No paired keeper-control run
  followed because the primary direct gate failed; do not promote suppression. Screen manifest,
  replays, and results are under `build/finals/20261006-suppression-confirmation-run/`; decoded
  fault/interval report is `build/finals/20261006-suppression-confirmation-analysis/summary.json`.

  Fresh read-only API query at **6 Oct 17:45 Adelaide** confirms submission **18078**
  (`LV-bokuto-61-mouth-ef70ddd4-ai`, active; sourceHash
  `41e7b317ec64b934b95e977a0441b8c2caf5ca7c6cbed3d64db9d16faf14dc47`) and fallback **17791**
  (`LV-bokuto-18-queenfeed-ba537e4e-ai`, idle; sourceHash
  `fa16c1050cad8f74058e9773b15dbea64eb0ec08b9f2aef3ff19aaf45ede677b`). No server mutation was
  made. S08 remains pending: before lock, re-read status and ensure the supported fallback or a
  later qualified artifact is active.
- **Fallback runtime preflight (6 Oct, evening):** Rebuilt local `bokuto-18-queenfeed` with the
  judge compiler and ran four sandboxed fixtures against Kenma03 on two already-used development
  maps (`fresh_6100601`, `fresh_6100604`), both seats, seed61520. All four completed without
  runner errors; candidate turns: 21,977, p99 CPU 8,605,711 points, max 9,769,827, max memory
  7,077,888 bytes. Outcomes were 1W–3L, recorded here but not used as strength evidence because
  this small run was selected for runtime preflight. Manifest pins local Bokuto source fingerprint
  `fa93106401b1fef54a92a429e3430200f4618d2056206035deaebf9935e6a287` and engine WASM SHA256
  `26e68680e45eb0f221db702aead9eefde776c2ad2ba066f4ddf8c12500c6a546`. Full logs, replays,
  results and resource observations: `build/finals/20261006-fallback-preflight/`. This validates
  the local snapshot's judge build/runtime on these fixtures; it does not prove local-to-server
  source identity. The last authenticated API read remains 18078 active /17791 idle at 17:45.
  No submission state was changed. At that checkpoint, next was to pin and validate 63's fresh
  confirmation; that run is now underway below. After its result, re-read and activate 17791 by
  the internal deadline if no replacement passes.
- **S08 confirmation fixtures (6 Oct, evening):** Candidate `bokuto-63-resource-crowding`, source
  fingerprint `db2a467eb6f3c6a5356e02e5c54ff8ca0876141a3c26359ab48140a4a722ef16`, remains frozen.
  New r3 confirmation set has 29 unique transformed layouts across 22 source families; 13,257
  local JSON metadata files and 252 existing map-layout signatures were scanned, with no reused
  layout. All 29 passed one engine validation game each against `verso-00-base`. Two earlier
  unscored map-set attempts were rejected after the engine found non-adjacent dragon segments in
  the `dilemma_10` family; that family is excluded from r3. Because some families contribute two
  transformed layouts, report both map-layout and source-family-cluster intervals after scoring.
  Frozen map hashes/provenance: `build/finals/20261006-crowding-confirmation/confirmation-map-manifest-r3.json`;
  map checks: `map-validation-r3.json`. The serial judge-sandbox comparison versus18 completed for
  both seats, seeds61530–61532 (174 fixtures). Candidate: 86W–0D–88L, zero runner errors. Replay
  scan found zero TLEs, invalid-action deaths, or replay/runner mismatches. Map-layout score was
  0.505747 (advantage +0.005747), 90% map-cluster interval [−0.051724,+0.063218] over29 layouts.
  **Frozen gate failed:** its lower bound is not above zero. Source-family sensitivity across22
  families was +0.018939, 90% interval [−0.049242,+0.087121], also inconclusive. At r100 candidate
  mean carried total was54.05 and queen alive in85.6%; at r300 total92.25 and queen alive in66.7%
  (136 fixtures reached r300). Candidate queen deaths: 46 h2h, 23 wall, 6 body, 6 self. Analysis
  artifacts: `build/finals/20261006-crowding-confirmation/confirmation-decision.json`,
  `analysis-map-layout-clusters/summary.json`, `analysis-source-family-clusters/summary.json`.
  Reproduction command: `python3 build/finals/20261006-crowding-confirmation/analyze_confirmation.py`.
  Source and map fingerprints matched the frozen manifest for every fixture. This confirmation set
  is consumed; retain18 and do not promote63.
- **S09 fallback activation (6 Oct, 21:22 Adelaide):** After S08 failed, a fresh authenticated
  `GET /api/v1/submissions` showed only expected incumbent **18078** active and fallback **17791**
  idle. A guarded `POST /api/v1/submissions/17791/activate` was issued only after verifying both
  IDs, names, states and fallback source hash. The API returned 17791 active; immediate authenticated
  readback confirmed it as the sole active submission, sourceHash
  `fa16c1050cad8f74058f2023b15dbea64eb0ec08b9f2aef3ff19aaf45ede677b`. Keep this artifact active
  through qualifier lock; perform one final read before 9 Oct 16:30 Adelaide.
- **Spatial encoder trainer setup (6 Oct):** Added `tools/finals/spatial_model.py` and
  `train_spatial.py`. The model keeps encoder-v1's 7×7×23 grid and 66 scalars, adds the proposed
  two-stream CNN/scalar encoder, 128-value shared state, 16-value candidate-type embedding and
  masked per-candidate scores. The trainer clones incumbent candidate 0, then performs the
  existing complete-game terminal-reward PPO objective; it saves resumable checkpoints and a CSV
  with PPO diagnostics plus fixed-seed greedy comparisons against a cached baseline. See the
  exact launch/resume commands in [`tools/finals/README.md`](../../tools/finals/README.md).

  Scope is deliberately encoder-first: current action/packet menus only, no persistent options,
  phase experts, potential shaping, offline IQL or centralized full-team critic. The value head
  shares the encoder and sees local observations. The action smoke run in
  `build/finals/spatial-smoke2/run/` resumed successfully through two updates against Bokuto 18:
  two sampled training games (1W–1L), zero overrides/faults; the one-game repeated monitor tied
  candidate and cached baseline (both lost on the A-seat fixture). A separate sonar smoke run in
  `build/finals/spatial-smoke-sonar/run/` completed one update/game with zero overrides/faults and
  a 99.87% baseline-packet choice rate; its single monitor game tied the cached baseline (both
  lost). The baseline clone reached
  100% held-out row accuracy on 598 rows from the same collected episode; this is only a clone
  diagnostic. A one-map monitor has no map-cluster interval. These measurements validate the
  pipeline, not learning effectiveness or strength. Four spatial tests, existing PPO/sonar tests,
  Python compilation and `git diff --check` passed. No candidate was promoted and the active
  submission was untouched.

- **Joint spatial policy correction (6 Oct):** Replaced the separate-head default with one
  `SpatialPolicy`: shared CNN/scalar encoder, conditional action and sonar candidate heads, and a
  shared local value head. The sonar head now receives the full selected 32-value action feature
  vector. PPO forms one per-turn ratio from the action log-probability plus the four
  action-conditioned sonar-ray log-probabilities, so both heads and the shared encoder learn from
  the same terminal team return. `--actor action` and `--actor sonar` remain ablations. The
  collector records the selected action features and passes them to the conditional sonar view.

  Verification: four spatial tests, existing PPO/sonar/credit tests, and Python compilation passed.
  A bounded native joint smoke at `build/finals/spatial-joint-smoke/` completed one 500-round
  training game and one fixed-monitor game against Bokuto18, with zero collector faults or
  overrides. The game lost; the candidate and cached baseline also both lost the single monitor
  fixture. One warm-start epoch cloned both candidate-0 labels with 100% validation accuracy on
  603 selectable action rows and 3,100 selectable sonar rays from the same episode; this measures
  label fit only. The PPO pass processed 5,954 selectable action decisions and 45,328 selectable
  sonar rays; the single-checkpoint monitor remains insufficient for trend or map-cluster
  inference. This is end-to-end plumbing evidence, not a strength result. Run the four-update
  multi-map pilot from [`tools/finals/README.md`](../../tools/finals/README.md) before deciding on
  any broader training or model changes. The active submission was untouched.

- **Heartbreaker reward implementation (7 Oct):** The sample potential was already documented
  in `POLICY_LEARNING.md` and `HYBRID_RL_ARCHITECTURE.md`; it was previously only a reference.
  Implemented it in `tools/finals/collect.py` as `heartbreaker-potential-v1`: the five phase-
  weighted terms are divided by their sum, keeping Phi in [-1,1], and fixed alpha is 0.2 with
  gamma0.997. Full official replay snapshots supply queen/longest/total lengths and distinct head-
  visited tiles for training reward labels only. Terminal Phi is zero after both elimination and
  round limit. Discounted rewards are folded over the team-round timeline and retained for every
  actor row, including a dragon's final decision after its death. Terminal W/D/L metrics remain
  logged separately from shaped policy return; actor inputs remain unchanged.

  Verification: five shaping tests, three credit tests and five spatial trainer tests pass;
  Python compilation and `git diff --check` pass. Replay decoding and return calculation were
  checked against saved 500-round `build/finals/spatial-joint-pilot/update-001/game-00/game.replay`
  (an old terminal-only episode): 500 pre-action potentials, range [-0.5116,+0.0765], and maximum
  absolute shaped-return delta 0.1023 at alpha 0.2. A fresh full-game collector smoke on maze,
  seed61610, baseline selectors versus Bokuto18, completed at round limit with one win, zero
  overrides and zero faults; the summary reports mean terminal return +0.5182 and mean shaping
  contribution +0.0074. This validates collection plumbing only, not PPO learning or strength.
  The smoke output was under ignored `build/` and is no longer present in the current workspace;
  compact measurements are retained here. A one-update PPO smoke could not start because the
  ignored bridge executable was also absent. The previous terminal-only run cannot be resumed
  with this code/config; incumbent-label warm-start data is still valid. At implementation time,
  next was to rebuild the bridge
  and opponent, collect a fresh warm-start episode, then launch a four-update shaped pilot under
  `build/finals/spatial-joint-shaped-pilot/` and compare terminal outcomes and fixed-monitor paired
  scores. No submission changed.
- **Continuous shaped-trainer mode (7 Oct):** Added `--until-stopped` to remove the 1,000-update
  cap while keeping per-update checkpoints and `Ctrl+C` resume. The fixed monitor now runs every
  five updates in the documented continuous command. Unit coverage checks unbounded update index
  generation; no continuous training was started. The current checkout lacks the ignored compiled
  bridge/opponent and warm-start outputs, so rebuild/collect before launch. No submission changed.

- **Rollout throughput optimization (7 Oct, proposed/unmeasured):** Added isolated process workers
  to `tools/finals/train_spatial.py`. Training rollouts and fixed-panel evaluation now preserve
  input order while allowing independent official-engine episodes to overlap; each worker owns its
  engine, native bot children, RNG, and read-only policy snapshot. Evaluation skips unused training
  tensor materialization, and sonar inference batches the four packet rays per decision. The
  requested `--threads` budget is divided across workers; `--workers 4` therefore uses two workers
  for the two-game training update and four for eight-game evaluation. Existing measured timing
  (update-001: 136.16 s collection, 16.64 s PPO) motivates the change, but no post-change game or
  speed result has been measured. Targeted credit/shaping/spatial tests (14), Python compilation,
  and `git diff --check` pass. Use a fresh output directory because the worker count is pinned in
  the run manifest; do not treat projected speedup as a measured result.

- **Capture-free rollout regression fix (7 Oct):** The new isolated evaluation workers call
  `collect.episode(..., capture=False)`, but the summary still read the training-only
  `action_mask`, causing `UnboundLocalError` after an otherwise complete game.
  `action_menu_counts` now derives directly from each recorded candidate menu and is available in
  both capture modes. Python compilation, 14 targeted credit/shaping/spatial tests, and a real
  500-round capture-free maze smoke (seed61611, 20,081 decisions, zero faults; arrays correctly
  omitted) passed. Existing failed runs should be restarted in a fresh output directory because
  the run manifest pins the collector source hash.

- **Shaped joint PPO result (8 Oct):** The completed run in
  `build/finals/spatial-joint-shaped-infinite-fixed/` reached update 1330 with the pinned joint
  actor, two training games per update, four isolated workers, and the Heartbreaker potential
  shaping objective. Its repeated fixed eight-game monitor ran at 266 checkpoints / 2,128 games:
  candidate **401W–0D–1,727L**, score **0.1884**, against the cached baseline score **0.5000**;
  mean paired delta was **−0.3116**. The best transient checkpoint was update 460 at 6–0–2
  (delta +0.25), but its map-cluster interval included zero. The final update 1330 was 0–8
  (delta −0.50, interval [−0.50, −0.50]); the last ten monitor checkpoints were 2–0–78
  (2.5%). This is fixed-panel evidence rather than independent confirmation, but it is strong
  negative evidence of policy collapse; no model was exported, promoted, or submitted.

  Verification after training: the relevant RL/finals Python suite passed **51 tests**; the
  standard CMake Release build succeeded and CTest passed **19/20**. The only CTest failure was
  the deterministic pre-existing `hunter_v15_shared_state` reference check, which expected
  `MOVE N` and received `MOVE E`. A direct `pytest tests` aggregate is not a valid clean gate in
  this checkout: six modules fail collection because of missing `comms`, changed hub-analysis
  symbols, or required bot executable arguments. No source or bot snapshot was changed by this
  measurement.

## 8 October 2026 — Akaashi 01 queen escape family

Created `bots/akaashi-01-queen-escape` from immutable atlas-disabled Bokuto 18
to address user-reported Trophy match 1404793, team B. Queen 0 enters the
(2,6)/(3,6) alcove at r66; ally 38 closes its exit; queen dies at r68.
Five friendly units disable inherited strict queen/head-clearance and
teammate yielding. Implemented six-step queen continuation/head clearance
from r0, full-horizon dodge validation, and teammate yielding at every team
size. Family protocol/details: `docs/akaashi-family.md`.
Final source fingerprint: `128f6c396312837b5af15bcf7836f8a90731fc1506f1554cff4dbc69ad29e1c8`.

Measured results:

- `python3 tests/test_akaashi_queen_escape.py`: synthetic baseline/candidate
  alcove regression passes (north versus east).
- Official replay oracle, seed `7698345d63307078`: 3,916 turns, zero
  mismatches, zero extra turns. Original A win at final protocol r127.
- Preserve recorded prefix through r65, then native candidate for queen 0
  and ally 38 from r66. Other actors use recorded actions/sonar, empty MOVE
  after recorded lists end. B wins at final protocol r128; queen alive,
  length four. Failure-specific counterfactual, not independent strength
  evidence. Artifacts: `build/queen-safety-1404793/`.
- Serial native screen vs Bokuto 18, seed 81008, both seats: Trophy 1–1,
  Weakhold 2–0, Schooltime 1–1; total 4–2. Zero runner errors or replay
  TLE/invalid-action faults. Direct advantage +0.1667, 90% map-cluster
  interval [0, +0.3333]; positive-screen gate false. Artifacts:
  `build/finals/20261008-akaashi01-screen/`. Only explanatory comments
  changed after native source freeze.
- Official sandbox Trophy, same seed, both seats: 1–1, zero runner errors
  or replay faults; candidate peak 8.3M points, p99 <=7.8M. Artifacts:
  `build/finals/20261008-akaashi01-runtime/`.

Both screens ran `tools/finals/screen.py --dry-run` first, and were audited
with `tools/finals/analyze_screen.py`. No promotion or server change;
Bokuto 18 remains the supported fallback. Proposed next step: broader
paired development and separate frozen confirmation before promotion.

## 8 October 2026 — user-requested Akaashi submission

User explicitly requested submission after review of Akaashi 01 results.
Fresh authenticated read confirmed Bokuto 18 (17791) sole active. Uploaded
the exact tested candidate as `LV-akaashi-01-queen-escape-4cf62807-ai`,
submission **20222**, version **104**. The 15-file archive is 3,940,000 bytes
and passes ZIP integrity and byte-for-byte comparison against local sources.
Archive SHA256: `4cf62807765c579e7052a070a110e78548b83fc495724fbeceb4e99b4f9da8fc`.
Server sourceHash: `188b90bbba4dcc0cd28d69dce51e9e1e4d60415d66a398039c1da1ed18ef0f8f`.
Upload/intent/readback receipts: `build/finals/20261008-akaashi01-submit/`.
This is explicit user deployment, not statistical promotion: the six-game
screen remains insufficient for a confirmed strength claim.

Server compilation completed; authenticated readback verified **20222 as
sole active**, 17791 no longer active. No further activation POST was needed
because the server activated the successfully built upload.

## 8 October 2026 — Akaashi 02 visible queen strikes

User identified a missed queen sprint kill in Trophy 1407768, team A,
visualiser r47 = protocol r46. Dragon 4, length two, at (12,10) can eat
(12,9)'s pearl, then move east to hit enemy queen at (13,9). 01 chooses west.
Cause: ordinary sprint generation is disabled at starting length two, even
with a funding pearl; ordinary H2H scoring assigns no special queen value.
Three-step generation also misses pearl-funded length-three attacks.

Created immutable-family candidate `akaashi-02-queen-strike` from 01. A
bounded one-to-three-step search of known visible terrain precedes ordinary
scoring/splitting; simulate prefixes for exact body/pearl/paid-step legality.
Only non-queens trade with a visible enemy queen; main revalidates the full
command before bypassing guard overrides. All other actions keep the guard.
Source fingerprint: `b4661bcdfe8722014a70361d119c4889ec12034837ef09a4f7c20ead3105ad60`. Detailed protocol: `docs/akaashi-family.md`.

Measured: original official-engine oracle, seed `17cdd44f3399e666`, 2,530 turns,
zero mismatches and extra turns, B wins at protocol r118. Reconstructed
history outputs: d4 NE r46; d20 EEE r46 / ENE r47; d30 SSE r46. Branch with
recorded prefix through r45 and native 02 only for d4 from r46 kills queen 1
by head-on at r46. Other actors remain scripted; exhausted lists use empty
MOVE. B still wins at r91 with both queens dead, so this is kill regression
evidence, not a match-win claim. Artifacts: `build/queen-strike-1407768/`.

Both `python3 tests/test_akaashi_queen_strike.py` and
`python3 tests/test_akaashi_queen_escape.py` pass; the latter now includes 02.
Serial native Trophy screen, seed 81009, both seats: 1–1 vs 01, 1–1 vs 18,
zero runner errors or replay faults. Artifacts:
`build/finals/20261008-akaashi02-screen/`. Screen dry-run and replay fault
audit completed. No server upload/activation; 20222 remains active 01.
Proposed: broader paired development and separate frozen confirmation.

02 metered Trophy check: seed 81009, both seats vs 01, 1–1, zero runner
errors or replay TLE/invalid-action faults. Candidate peak 10.3M points per
turn, p99 <=7.9M. Native and sandbox outcomes agree on these fixtures.
Artifacts: `build/finals/20261008-akaashi02-runtime/`. This focused check
is not an all-map runtime guarantee.

## 8 October 2026 — Akaashi 03 threatened queen splits

User flagged Trophy 1407768 team-A queen split at r109. Replay confirms
queen 0 at (19,11), length four, sole friendly unit, SPLIT 2; enemy 51
from (19,14) performs NNN and kills the stationary queen later that round.
Enemy body is incomplete in local view (two disconnected parts). Guard
already marks queen cell reachable, but forced split dodging starts at r290.

Created `akaashi-03-threatened-queen-split` from immutable 02: force dodge
evaluation on threatened queen splits at every round; validate six-step
continuation as before. Unknown/incomplete bodies get bounded four-step
reach. Separate each enemy's BFS visited mask from the union result, fixing
suppressed search through already-marked overlapping threat regions.
Safe production/cage splits remain possible. Fingerprint `99a4a584d0255a5016ba961d949218db18a8446a26316485857e355bd35d4a8c`.

Measured: original replay oracle zero mismatches across 2,530 turns. 03
selects north at r109, guard Q. Exact original prefix through r108 then
native 03 only for queen 0: queen survives; A wins at protocol r119, queen
length two. Other actors scripted with recorded sonar/actions and empty MOVE
after recorded lists end. Original B win at r118. This is targeted scripted
regression evidence, not a general improvement claim. Artifacts:
`build/queen-strike-1407768/`, including `split-branch.py`, `split-branch.replay`.

`python3 tests/test_akaashi_threatened_split.py` passes: parent split vs
candidate north, safe splits, cage escape splits, unknown-body reach and
overlapping-enemy union. Earlier escape/strike regressions now include 03.
No server change; 20222 stays active Akaashi 01. Detailed family notes:
`docs/akaashi-family.md`. Proposed next: broader paired confirmation.

03 serial native development screen: seed 81010, both seats vs exact 02,
Trophy 1–1 and Schooltime 1–1; total 2–2 with zero runner errors.
Artifacts: `build/finals/20261008-akaashi03-screen/`. Dry-run completed
before execution. This small two-map screen does not establish improvement.

03 verification completed: all three synthetic regression suites pass.
Native screen replay audit: zero TLE/invalid-action faults. Metered Trophy
check, seed 81010, both seats vs 02: 1–1, zero runner errors or replay
faults. Candidate peak points 8.7M, p99 <=8.2M; native and metered fixture
outcomes agree. Artifacts: `build/finals/20261008-akaashi03-runtime/`.
Focused checks do not establish all-map strength or runtime guarantees.

## 8 October 2026 — user-requested Akaashi 03 deployment and Heartbreaker loss-map queue

User explicitly requested submit and queue against Heartbreaker on every
map lost in the linked series. Fresh authenticated read confirmed 20222
sole active. Uploaded exact tested 03 as **20244 (v105)**,
`LV-akaashi-03-threatened-queen-split-4f229cf2-ai`. ZIP integrity and
byte-for-byte local source checks passed: 15 files, 3,940,739 bytes.
Archive SHA256 `4f229cf2a93a3e2757beba2f947a7926242287fd71ed87d96b16cb4e8166f4c7`.
Server sourceHash `23e621f6c2f14deb4f4f3fdc5113751c41e351ccb6b5ef62d7cc18045ca6c92c`.

Fresh GET of 1407768 confirms series `9d37b097-b9c9-4801-a8bd-9c4d52edb899`,
our team 7 in seat A vs Heartbreaker team 62. The series scored 6–11.
Lost map names / current API IDs: Around UNSW 34, Australia 29, Autarky 19,
Default 4, Devil 13, Islands 30, Maze 31, Prisoners Dilemma 17, Slithery
Fight 21, Stripes 32, Trophy 11. Planned request: one unranked game per
lost map against team 62 after verifying 20244 sole active.
All upload, API, map-selection and queue receipts under
`build/finals/20261008-akaashi03-submit/`. Deployment is the user's explicit
decision; existing local screens remain insufficient for statistical promotion.

Akaashi 03 server compilation succeeded and authenticated readback verified
20244 as sole active. The server auto-activated it; no activation POST was
needed. With 20244 active, POST /api/v1/battles accepted 11 unranked games
against Heartbreaker (team 62), one for every lost map in the earlier series.
IDs **1410660–1410670**, series `05360044-7f0a-42b1-b33e-66de0fdcfa18`.
GET readbacks verified every opponent/map and pending status; outcomes are
not measured yet. Receipts: `build/finals/20261008-akaashi03-submit/`,
including `verified-active.json`, `queue-response.json`, `queue-verified.json`.

## 8 October 2026 — ongoing Heartbreaker iteration, Akaashi 04

User authorized continuous general-rule iterations: inspect completed loss
maps, fix evidenced weaknesses, upload/activate and retest remaining losses
until they clear the goal. Akaashi 03 series 05360044-7f0a-42b1-b33e-66de0fdcfa18
completed **5–6**, zero TLE/invalid-action replay faults. Six losses: Around
UNSW, Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes.

Added `tools/finals/heartbreaker_review.py` to emit start-of-round plus final
curves (total, queen, longest, units), samples, economy-event totals, queen
deaths, largest deaths and longest drops linked separately to splits/deaths.
Plots use matplotlib. Detailed map-by-map evidence/inferences and next
weaknesses: `docs/finals-campaign/HEARTBREAKER_ITERATION.md`. Downloaded
series/metadata, legal-history probes, CSVs/plots and summaries:
`build/finals/heartbreaker-iteration/akaashi03/`.

First evidenced implementation target: Around UNSW dragon 711 at r408,
length 36 but only four represented chain cells. Parent chooses NEE and
self-collides at length 37 because visible disconnected own-body pieces
are ignored. 04 includes all currently visible own segments in simulation,
and does not release a partial chain's front as if it were the real tail.
Final movement revalidation can replace a known doomed command with a legal
step; intentional feeder/cap-cull deaths remain. No map names/coordinate
conditions/atlas. Source fingerprint `4756f20750712479f60135dda2064156d14cf584df2a2c6e038572b7c618341a`.

Measured: official-engine original oracle reproduced 36,347 turns, zero
mismatches/extra turns, B wins at r499. Preserve recorded prefix through
r407 and use native 04 only for dragon 711 from r408: avoids the observed
r408 self-collision, chooses N. Dragon later dies against a wall at r411.
The scripted branch ends A win at r477, but that does not establish general
strength; recorded lists exhaust and later actors use empty MOVE. The
regression claim is limited to avoiding the observed self-collision.
Artifacts: `body-branch.py`, `body-branch.replay`, `1410660-d711.input`.

`test_akaashi_visible_body.py` passes (disconnected/partial body rejection
and exact full-tail release); all three previous regression suites now
include 04 and pass. Local serial screen vs03: Around UNSW/Stripes, seed
81011, both seats, 2–2, zero runner/replay faults. Metered Stripes, same
seed/both seats: 1–1, zero faults, candidate peak 9.5M points, p99 <=9.1M.
Artifacts: `build/finals/20261008-akaashi04-screen/` and `...-runtime/`.
Both screen dry-runs and replay fault audits completed. These narrow checks
do not establish strength or all-map runtime guarantees.

Outstanding biggest weaknesses: early corridor/food-access failures on
Stripes/Prisoners Dilemma/Autarky; early economy/contact attrition on Default;
midgame attrition/queen death on Slithery Fight; late queen/long-head deaths
and remaining partial-body wall risks on Around UNSW. Next loop: submit04,
retest six loss maps, inspect new failures before implementing the next version.

### Akaashi 04 deployment and live retest

20265 (v106), `LV-akaashi-04-visible-body-safety-78d38fff-ai`, compiled and
was verified sole active. Archive 15 files / 3,941,039 bytes, ZIP integrity
and source-byte checks passed. Archive SHA256
`78d38fff65215b9d1897e533e4d268c6caf2567480cd0c42467becfba584afa9`;
server sourceHash `e0606fff4a87c81a1f4fa103db3515b38026952c42c49da60724cbe09f852f16`.
User-authorized unranked retest accepted **1412255–1412260**, one each on
Around UNSW, Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes.
Receipts: `build/finals/20261008-akaashi04-submit/`. Results pending.
Next continuation must refresh this series, analyze new losses, and make
a further general change from evidence. Goal remains active.

## Akaashi 04 retest — completed

Submission 20265 vs Heartbreaker: **1–5**, six games, one per map, fresh server seeds. Around UNSW is a win; five losses remain. This is not a matched causal estimate of the effect of 04. All six replays have zero TLE/invalid-action faults.

| Loss | Total A/B r50; r100; r200 | Queen death | Largest dragon death | Current primary weakness |
|---|---|---|---|---|
| Autarky (1412256) | r50 13/49 | r44, length 2 | r4, length 3, wall | Early corridor/food deficit; repeated length-three dead-end deaths before queen loss. |
| Default (1412257) | r50 21/19; r100 62/27; r200 79/37 | r166, length 2 | r367, length 9, h2h | Economy leads at r100/r200, then material/contact attrition reverses it; queen killed at r166. |
| Prisoners Dilemma (1412258) | r50 2/40 | r52, length 2 | r2, length 6, h2h | Opening population collapses: spawned heads collide and short chains strand before resource growth. |
| Slithery Fight (1412259) | r50 98/95; r100 141/113; r200 152/184 | r116, length 3 | r494, length 72, h2h | Midgame economy lead reverses; early queen loss plus decisive length-72 head-on at r494. |
| Stripes (1412260) | r50 2/24 | r38, length 3 | r38, length 3, h2h | Very weak food collection; queen collision at r38; partial-body fix cannot solve narrow-route starvation. |

Artifacts: `build/finals/heartbreaker-iteration/akaashi04-series/review/` (all curves, event-linked drops, summaries and plots).

Akaashi 05 adds general bounded sprint escape for queens: shortest-first legal prefixes of up to three steps, known visible terrain, exact body/pearl/paid-step simulation, lower endpoint risk, six continuation steps. Safe incumbent moves remain. It fixes a restricted single-step dodge search, without map identifiers or coordinate conditions.

Two measured counterfactuals: Around UNSW 1410660 oracle 36,347 turns/zero mismatches; original prefix through r387 then 05 only for queen 0. NN avoids r388 collision but queen dies at r397. Stripes 1412260 oracle 505 turns/zero mismatches; prefix through r36 then 05 only for queen 0. SE avoids original r38 collision, queen dies at r44; branch draws at r61 rather than original B win at r60. Other actors use recorded commands/sonar; exhausted lists use empty MOVE. These demonstrate avoidance of specific deaths, not wins against adaptive opponents.

05 synthetic endpoint escape test and all four earlier regression suites pass. Native Trophy/Autarky screen vs04, seed 81012, both seats: 2–2, zero faults. Metered Trophy same seed/both seats: 1–1, zero faults; candidate peak 8.8M points, p99 <=8.5M. Artifacts: `build/finals/20261008-akaashi05-screen/`, `...-runtime/`.

05 source fingerprint: `4a8d86ca8dc1cca4270d7623723bd42ddd28c8703204881df83aad7ecd19d7d0`.

Outstanding economy targets remain, especially opening corridor viability on Autarky/Prisoners Dilemma/Stripes. Next inspect 05 failures, and prioritize food/production changes or valuable late-dragon survival from the new evidence.

### Akaashi 05 deployment and five-map retest

20276 (v107), `LV-akaashi-05-sprint-queen-escape-55ad3fc2-ai`, compiled
and was verified sole active. Archive: 15 files, 3,941,224 bytes, ZIP integrity
and local-source byte checks passed. Archive SHA256
`55ad3fc299b062320aa2cc66fd5c77c860fb3175fbae6e157f4b3487b26976a0`;
server sourceHash `2ce46a1e8404ea60bb59150309cbd1167393f11a702a387b47d10d7feefd03d6`.
Accepted and verified five unranked Heartbreaker games **1413068–1413072**:
Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes; series
`66b05548-b3dd-4129-8db4-085a3c7fa0d1`. All pending at readback. Receipts:
`build/finals/20261008-akaashi05-submit/`. Goal remains active.

Next continuation: refresh 1413068, collect finished replays and generate
all loss curves. In addition to opening food/production viability, prioritize
Slithery Fight 1412259 dragon 1590's length-72 H2H at r494: authoritative
final standings show both queens dead and longest 12 vs55. This is a
plausibly outcome-changing late material loss; verify a legal escape from
its current observations before changing late long-dragon behavior.

## Akaashi 06 validation checkpoint

Latest user steering: finish current iteration and test. 05 live retest completed 0–5; all loss curves are in `build/finals/heartbreaker-iteration/akaashi05-series/review/`. 06 applies bounded dodge checks to late non-feeder heads of length >=12 before the partial-body shortcut. Partial known cells with >=6 unseen tail cells remain occupied for the six-step horizon. Reconstructed 1412259 dragon 1590 changes W to S at r494. Full oracle failed (39,133 mismatches / 39,147 turns); attempted branch rejected. No counterfactual win/survival claim. Synthetic asset/exclusion tests and prior safety cases compiled against06 pass. Native Slithery/Dilemma seed81013 both seats: 2–2, zero replay faults. Initial metered run was interrupted with truncated artifacts; recovery run is `build/finals/20261008-akaashi06-runtime-recovery/`.

06 focused runtime recovery completed: 0–2 vs05 on Slithery Fight, zero runner/replay faults, candidate peak13.6M points, p99<=8.6M. Uploaded 20296 (v108), LV-akaashi-06-late-material-safety-406f4835-ai; server sourceHash 4d5d6364ca83997284e2779cd8ba9b510c9116383a025bca236219e2ff01b98b; archive SHA256 406f4835b0edbf17f4f7201197fa48ce5063baf5a5b6c5eafe47bc1e438a1ea8. Compilation/readback and five-map live test pending. No general improvement claim.

06 compilation/readback succeeded: 20296 sole active. Accepted and API-verified five-map Heartbreaker test1415322–1415326, seriesc7153758-39cf-42e0-bf8e-201ad801e97a. User steering: finish current iteration and test; no new version started. Receipts build/finals/20261008-akaashi06-submit/; monitor/collection build/finals/heartbreaker-iteration/akaashi06-series/.

## Akaashi 06 current iteration — finished

Heartbreaker test1415322–1415326 completed **1–4**: Default won; Autarky, Prisoners Dilemma, Slithery Fight and Stripes lost. All five replays collected; total/queen/longest curves and linked death/split diagnostics are under `build/finals/heartbreaker-iteration/akaashi06-series/review/`. Own bot TLE/invalid-action faults: 0. Authenticated post-test read verifies20296 (v108) sole active. No next version started.

Autarky/Prisoners Dilemma/Stripes retain early food/population deficits (r50 total A/B25/50,3/38,2/18 respectively). Slithery Fight leads at r100143/114 and r300160/130 but loses its queen at r198 and substantial late heads (largest25 at r459); late material/queen safety remains incomplete. Default won despite queen death at r66, with strong early economy (r10056/19). Results use fresh server seeds, so no causal strength improvement is established by the single win.

User explicitly requested pause after this test. Completed1–4, active20296 verified, own faults zero. Work stopped; no additional bot or test queued. Goal status update tool reported no goal attached to the thread; pause is recorded in working memory.

## 8 October 2026 — Trophy centre congestion / Akaashi 07

User requests holding centre while surplus dragons expand/attack, based on Team A1416376. Downloaded authenticated metadata and replay; no server mutations. Replay confirms A85/B20 material and32/8 units at r100,16/32 A heads in centre x/y7–17. Food collection flips82/28 (r50–99) to64/81 (r100–149); queen dies at r309, enemy queen at r17. Detailed measured outputs under `build/finals/centre-expansion-1416376/`. Congestion is a plausible contributing cause, not a proven sole explanation.

New immutable candidate `akaashi-07-hotspot-capacity`, parent06, adds nearest-head resource reservation (two incumbents plus visible enemy pressure), sharp surplus target discount including memory fallback, and ordinary crowded-production suppression in r50–289. Observations only; no map coordinates. Local per-resource capacity is an approximation to hotspot allocation. Attack targeting inherited.

Allocation regression passes. All six inherited safety fixtures pass against07; initial ad hoc invocations used wrong queen-escape mode and omitted visible-body `-DFIXED`, then reran with their proper existing fixture settings. Native bounded comparison dry-run then execution: `.venv/bin/python tools/finals/screen.py --candidate akaashi-07-hotspot-capacity --opponents akaashi-06-late-material-safety --maps maps/live/trophy.map maps/live/default.map --seeds 81014 --output build/finals/20261008-akaashi07-screen`. Both seats, four fixtures: **2–2**, zero errors/TLE/invalid-action faults. Sources frozen in run directory. Metered two-seat Trophy check same seed launched after dry-run with `--sandbox`, output `build/finals/20261008-akaashi07-runtime/`; pending. No deployment or strength promotion. Prior server loop stays paused.

07 focused metered check completed: Trophy seed81014 both seats vs06 **1–1**, native winners reproduced, zero runner errors or candidate TLE/invalid-action faults. Candidate peak9.9M points, p99<=8.0M; audit `build/finals/20261008-akaashi07-runtime/audit.json`. Source fingerprint `24936696c026e2ac457852b9007255dd5cf390ed7c78ea95cb7405552f8cac3a`. Allocation candidate remains local/experimental; no server mutation, no strength promotion.


User explicitly requested submission and Heartbreaker retest across all seven lost maps. Frozen zip has 15 expected source files byte-verified against Akaashi07, archive SHA256 `05e3b9c81bbb959dc336e225b619fbd8dadb8fd95bba079d0cfd6f02fe5c142e`. Uploaded `LV-akaashi-07-hotspot-capacity-05e3b9c8-ai`, submission20333/v109; compilation succeeded, API readback sole active. Unranked matches accepted and individually verified pending: 1418905 Australia(map29),1418906 Autarky(19),1418907 Devil(13),1418908 Maze(31),1418909 Prisoners Dilemma(17),1418910 Stripes(32),1418911 Trophy(11), series `d80af811-b386-40c0-9572-08f80742afb0`. Receipt directory `build/finals/20261008-akaashi07-submit/`. At queue readback outcomes were pending; they later completed **2–5**, as detailed below.

Results collected after all seven completed: Akaashi07 **2–5**, zero own TLE/invalid-action faults. Wins Devil/Trophy. Losses: Australia (queen H2H r60; despite A122/B29 r100 and217/71 r200, a length57 self death at r497 precedes loss), Autarky (14/43 r50, queen H2H r66), Maze (46/66 r100, queen H2H r260), Prisoners Dilemma (7/16 r50, queen H2H r49), Stripes (5/22 r50, queen wall r64). Full curves and death/split joins in `build/finals/heartbreaker-iteration/akaashi07-series/review/`; replay receipts under submit directory. Zero runtime faults. Single fresh-seed run is not a matched causal estimate; no strength promotion. No new iteration started.


## 8 October 2026 — Australia 1418905 queen escort

User pointed to visualizer round48. Exact replay shows equal length-two A21 near queen1 and B10. Engine action order has B10 move before A21. On protocol r47, A21 can move N to34,27 (visualizer's round48 setup); on protocol r48, B10 moves E into that head, causing mutual H2H. A direct move onto B10's old head would encounter the body and die, so the policy needs to shadow its path before contact. Queen itself later mutually kills B10 at protocol r60 and also dies, as original replay diagnostics show.

Local Akaashi08 adds a nearest visible nonqueen escort potential for a comparable pursuer within five tiles of the queen. Original engine replay oracle: Australia, seed `cb06256202a7d9f9`,31,975 turns, zero observation mismatches/extra turns. Native reconstructed A21 history changes protocol r47 W->N. Engine scripted branch runs candidate for queen1 and escort21 after prefix r46, all other agents use recorded actions. A21/B10 trade at r48; A queen remains alive, final r181 A win. Opponent actions are nonresponsive; branch contains21 invalid-command deaths after state divergence, so final score is not strength evidence. Seven existing hotspot/safety regressions pass. Fingerprint `3538265a77e7355410d97bc989fe5595ae14b7317ec29d4429539c6aed151d8f`. No upload; active server remains20333. Artifacts `build/finals/queen-intercept-1418905/`.

## 8 October 2026 — Akaashi 01–06 family round robin

The user asked to identify the best Akaashi bot and run a full family round
robin, then capped the work at 500 games. The roster was frozen to snapshots
01–06, the six family directories present when the run started. The suite uses
the 15-map frozen frontier bundle plus Stripes, a documented Akaashi loss map.
Every ordered bot pair ran once per map, giving both seats: 30 games per map,
160 per bot, and 32 per unordered pair. The 16 maps were Colosseum, arena,
Autarky, Big Empty, Default, Default Small, Devil, Dilemma, Portals, Queen of
Spades, Schooltime, Slithery Fight, Stripes, Stronghold, Trauma, and Trophy.

| Rank | Snapshot | W–D–L | Points |
|---:|---|---:|---:|
| 1 | Akaashi 02 — `akaashi-02-queen-strike` | 88–0–72 | 264 |
| 2 | Akaashi 04 — `akaashi-04-visible-body-safety` | 86–0–74 | 258 |
| 3 | Akaashi 03 — `akaashi-03-threatened-queen-split` | 85–0–75 | 255 |
| 4 | Akaashi 06 — `akaashi-06-late-material-safety` | 77–0–83 | 231 |
| 5 | Akaashi 05 — `akaashi-05-sprint-queen-escape` | 76–0–84 | 228 |
| 6 | Akaashi 01 — `akaashi-01-queen-escape` | 68–0–92 | 204 |

Akaashi 02's 32-game head-to-head records were 19–13 vs01, 18–14 vs03,
19–13 vs04, 17–15 vs05, and 21–11 vs06. The top three are close, and map
leaders varied: 02 led on Colosseum, Autarky, Portals, and Trophy; 04 led on
Big Empty, Devil, Dilemma, and Queen of Spades; 06 led on Schooltime and
Slithery Fight. 01 led Default Small, 03 led Default, and several maps had
ties. The result identifies 02 as the top snapshot in this selected
development pool, not a statistically confirmed family-wide or contest-wide
strength promotion.

The run used native `unswbc 1.2.9`, with sandbox CPU metering disabled and a
600-second runner timeout. The first 90 core games (Colosseum, arena, Autarky)
were serial; the remaining 390 games were run with four isolated workers after
the serial pace on Big Empty proved too slow. All 480 core fixtures completed
with valid outcomes and zero runner errors. The runner retained logs and
replays. It did not perform replay fault analysis or sandbox metering, so
runtime faults are recorded as unmeasured rather than zero. Seeds are retained
in logs and linked `match_diagnostics` queue events.

There were 491 completed match records across the three result directories.
Up to five interrupted in-flight launches were not retained as result rows;
even counting all five, total launches stayed below the 500-game cap. The
analysis uses the balanced 480-game core and excludes five exploratory Colosseum games
from the initial interrupted run and six partial Big Empty games from the
serial run. Their results and queue events remain intact. The three
statistics run IDs are `9a89df2075c14f7a8d7480ce02f3c5ea`,
`0ae0332cf2574be5a41352d30281e2c0`, and
`357fdce4804347d5b30f87c39144fdfc`; the first exact ID is recorded in its
manifest. The local statistics ledger was rebuilt from all source queues
(5,184 events total), including existing experiments.

Reports and per-game rows (seeds, rounds, outcomes, logs, and replay names) are
under `build/finals/20261008-akaashi-round-robin-500cap/`:
`combined-standings.csv`, `combined-head-to-head.csv`,
`combined-per-map.csv`, `combined-games.csv`, and `combined-summary.json`.
Run outputs and source manifests are in that directory and
`build/finals/20261008-akaashi-round-robin-500cap-rest/`; the five exploratory
games are in `build/finals/20261008-akaashi-round-robin/`. Queue run IDs are
`9a89df2075c14f7a8d7480ce02f3c5ea`, `0ae0332cf2574be5a41352d30281e2c0`, and
`357fdce4804347d5b30f87c39144fdfc`. Akaashi 07 and 08 appeared after the
run's roster freeze and were not tested.

## 8 October 2026 — Akaashi composite family screens

The user asked for a new Akaashi family combining useful behavior from the
line and accounting for the newer untested 07/08 snapshots. The first six-bot
round robin had ranked 02 above 04 and 03, while 07/08 were untested. Since 08
already inherits 01–07, I compared alternative forks and retained every bot
snapshot unchanged.

| Candidate | Frozen roster / schedule | W–D–L | Errors |
|---|---|---:|---:|
| `akaashi-09-adaptive-capacity` | Focused vs01–08; six maps; 96 games | 44–0–52 | 0 |
| `akaashi-10-ranked-capacity` | Focused vs01–09; six maps; 108 games | 53–0–55 | 0 |
| `akaashi-11-escort-expansion` | Focused vs01–10; six maps; 120 games | 57–0–63 | 0 |
| `akaashi-12-queen-strike-escort` | Focused vs01–11; six maps; 132 games | **71–0–61** | 0 |
| 12 hard-map follow-up | Focused vs01,03,04,05,11; Autarky/Default/Slithery Fight/Stripes; 40 games | **16–0–24** | 0 |

The 09/10/11 hypotheses varied the 07 hotspot target reservation. 09 used a
45% first-surplus factor tapering to a 12% floor; 10 used 12% tapering to a
3% floor; 11 disabled per-target discounts while keeping ordinary crowded
production suppression and the 08 escort. Their focused scores were not
strong enough to establish an advantage. The final variant, 12, returns to
the measured 02 base and ports only the 08 nearest-ally escort bonus. This
preserves 02's visible affordable queen strikes and 01's queen escape without
assuming the later cumulative hotspot changes improve overall results.

Main screen: both seats, every one of 11 opponents, on Autarky, Default,
Prisoners Dilemma, Slithery Fight, Stripes, and Trophy (12 matches per
opponent). Akaashi12's record by opponent was:

| Opponent | 12's W–D–L |
|---|---:|
| 01 Queen Escape | 5–0–7 |
| 02 Queen Strike | 7–0–5 |
| 03 Threatened Queen Split | 6–0–6 |
| 04 Visible Body Safety | 5–0–7 |
| 05 Sprint Queen Escape | 5–0–7 |
| 06 Late Material Safety | 7–0–5 |
| 07 Hotspot Capacity | 7–0–5 |
| 08 Queen Intercept | 9–0–3 |
| 09 Adaptive Capacity | 8–0–4 |
| 10 Ranked Capacity | 7–0–5 |
| 11 Escort Expansion | 5–0–7 |

By map, Akaashi12 went 13–9 on Autarky, 10–12 on Default, 14–8 on Prisoners
Dilemma, 12–10 on Slithery Fight, and 11–11 on both Stripes and Trophy. It
beat the original 01–08 group 51–45 and the full 01–11 pool 71–61. It did not
beat each snapshot: it lost to01,04,05,11 and tied03. The separate 40-game
follow-up on four weak maps against those opponents went16–24, confirming that
the Default/autarky-side losses remain a real risk rather than disappearing in
the focused rescreen. Do not combine that deliberately reweighted sample with
the 132-game balanced screen when reporting the main rate.

The game runner was native `unswbc 1.2.9`, 600-second timeout, with replays
retained and sandbox/metering disabled. All five schedules completed with
zero runner errors. Replay fault audits and CPU-limit verification were not
performed. The focused regression `python3 tests/test_akaashi_hotspot_capacity.py`
passes for the 06/07/09/10/11 capacity implementations; the tournament
compiled and ran Akaashi12. The combined 09–12 screens plus the focused
follow-up used 496 matches, under the user's 500-game ceiling for this
candidate comparison. This is a six-map development result only, not
unseen-map confirmation, a strength promotion, or authorization to upload.

Artifacts: `build/finals/20261008-akaashi09-lineup-96/`,
`build/finals/20261008-akaashi10-lineup-108/`,
`build/finals/20261008-akaashi11-lineup-120/`,
`build/finals/20261008-akaashi12-lineup-132/`, and
`build/finals/20261008-akaashi12-hard-map-confirm-40/`. The 12 main directory
includes `akaashi12-head-to-head.csv` and `akaashi12-per-map.csv`. Run IDs:
`5524174a13fd444ead1d0c0ff276c6db`,
`0fd96369bae6403e9266257ec2ffc717`,
`80a9eb51c9ef4ee79911ebd40f66929d`,
`fff9e6ee653a493ca67b30d684f90cc7`, and
`db7d17c3f54d4dd39851a7e5a48b3def`.

## 8 October 2026 — Akaashi replay-feature audit

At the user's request, decoded retained replays with the registered F1 local
feature extractor and computed side-game means/medians for the documented
material checkpoints, pearl economy, births/deaths/kills, survival causes,
length milestones, and end margins. Cohorts: the balanced Akaashi01–06
round-robin slice on the six maps shared with candidate12 (180 games, 60
appearances per bot), plus all 132 candidate12 line-screen games (12 against
each of01–11). These cohorts share maps but use different opponent pools, so
their aggregate feature levels are descriptive rather than opponent-adjusted.

Replay extraction succeeded for all 312 games / 624 side rows. All 2,808 V0
bookkeeping checks passed; no TLE or invalid-death events were recorded. These
checks do not measure sandbox CPU compliance. In the older cohort, 02 had the
best win record at34–26 (56.7%), followed by06 at33–27 and04 at31–29.
Candidate12 went71–61 (53.8%) in the broader focused screen, but only35–37
against the original01–06 group; its other36–24 came against07–11. Directly
against02, candidate12 went7–5 and averaged 553.6 final-checkpoint pearls and
+11.7 end total margin, versus02's473.3 and−11.7; 02 had slightly more
round-100 total (49.7 vs47.4). This small schedule-specific H2H favors12, but
does not establish an overall replacement for02's balanced-pool result.

Compact and full registered-feature reports are in
`build/finals/20261008-akaashi-replay-stats/`; the summary and interpretation
are recorded in [`docs/akaashi-family.md`](../akaashi-family.md). In
particular, `registered-feature-summary.csv` and
`registered-12-head-to-head.csv` keep mean and median for every extracted
numeric feature. `12-vs-02.csv` gives the direct comparison, `by-map.csv`
contains map-conditioned summaries, and the two `extracted-*` directories
retain side features, deaths, and check results. This remains development
evidence from six maps; candidate12 has no unseen-map confirmation or sandbox
runtime check.

## 8 October 2026 — user-requested Akaashi 12 submission

Uploaded `akaashi-12-queen-strike-escort` at the user's request as
**submission 20432 (v110)**, `LV-akaashi-12-queen-strike-escort-634cb502-ai`.
Archive SHA256 `634cb502b90b3f320914de853c3b6f2df1f7264650557aa8fe0ec8669bbe56d9`,
3,940,958 bytes; server sourceHash
`fa2be5835f99045d642111a6c803cdbe34d04956a39ec5fcfc496dffbe22ce7d`.
Server compilation succeeded.

The submission auto-activated after asynchronous compilation. I immediately
restored the incumbent **20333 / Akaashi 07** under the existing qualifier
entry gate. Fresh final API readback confirms 20333 sole active and 20432 idle.
The user requested a submission; this did not promote 12, which has not cleared
the strength/runtime gates. No live match was queued. Receipt artifacts:
`build/finals/20261008-akaashi12-submit/`.

## 8 October 2026 — user-requested Kuroo 02 submission

Packaged and uploaded `kuroo-02-escort-soft-reserve` as **submission 20472
(v111)**, `LV-kuroo-02-escort-soft-reserve-026a480c-ai`. The 15-file archive
is 3,941,225 bytes, SHA256 `026a480c17e97ca1c71dba54a5bf6868753418d2a3a722f1030e2a826d781652`;
server sourceHash `c3dba860bfa0e938e38fee1c381d82c984a322a0d059eb9838f1a4c9ca032952`.
Server compilation succeeded.

The first post-upload readback showed incumbent 20432 active while Kuroo was
processing. After the asynchronous build, the server auto-activated Kuroo02;
the guarded finalizer restored **20432 / Akaashi12** and verified it as the
sole active submission. Kuroo02 is idle and has no sandbox runtime validation
or live match result. This records the requested submission, not a strength
promotion. Receipts: `build/finals/20261008-kuroo02-submit/`.


## 8 October 2026 — Kuroo soft reserve and match1427506

User requested a new Akaashi02/12-derived family for A405 wall death, then
steered toward reserving several slots through split disincentives and
preserving larger dragons' free movement bonuses. Created Kuroo01/02.
Measured original oracle:54,133 turns, zero mismatches; A405 r199 length7,
63/64 units, MOVE N wall death. Hard reserve prevented a legal SPLIT5.
Candidate exact-history output SPLIT5; capacity/emergency regression and
inherited queen escape/strike cases pass for both. Soft band8, initial target
four free slots; strength remains unmeasured. Native8-fixture screen pending
at build/finals/20261008-kuroo02-screen/, seed81020, Around UNSW/Trophy, both
seats against Akaashi02 and12. See docs/kuroo-family.md for the full protocol.

Measured Kuroo02 native screen:8/8 fixtures complete,4–4 overall;3–1 vs
Akaashi02,1–3 vsAkaashi12; zero runner errors. Around UNSW2–0 vs02 and0–2
vs12; Trophy1–1 against each. No strength improvement established. Both
Kuroo variants output SPLIT5 on the original A405 history; scripted engine
branch confirms a valid r199 split (parent2/child5), but subsequent recorded
commands refer to changed bodies/IDs, so later branch deaths are unusable
for survival claims. Replay fault audit pending.

Replay audit completed for all8 fixtures: winner parity passes, zero TLEs
and invalid deaths on either side. Analysis retained in screen/analysis/.
Native execution is not sandbox CPU validation. At this measurement checkpoint
there had been no upload or activation.

## 8 October 2026 — Kuroo 02 active retest from match1427506

The user directed that Kuroo02 remain active and be queued against the same
opponent in match1427506 on every map lost in that series. API readback
identified ComTamSuonNuong (team193) as the opponent; team7 lost 14 of 17
games. Exact lost maps and IDs: Around UNSW34, Australia29, Devil13, Islands30,
Maze31, Portals20, Prisoners Dilemma17, Schooltime9, Slithery Fight21,
Stripes32, Tower Defense33, Trauma15, Trophy11, weakhold28.

Activated **20472/v111** and verified it sole active, then POSTed 14 unranked
games against team193. Accepted IDs **1431103–1431116**, series
`086328b2-45f1-4238-818f-1de0c4240aa9`; per-game API readbacks confirmed the
opponent, map, unranked status, and pending state. Final active readback again
confirmed 20472 sole active. Outcomes are pending; no promotion claim. Receipts
and match-derived map list: `build/finals/20261008-kuroo02-submit/`.


### 8 October — Kuroo03, Slithery Fight1431111 queen obstruction

Measured:02 retest vs ComTamSuonNuong193 finished2–12 (Australia/Maze wins),
zero own TLE/invalid deaths. All14 curve/death/split reviews saved at
`build/finals/heartbreaker-iteration/kuroo02-series/review/`.

Protocol438 (visualiser439) A1 length31 becomes7 via guard `C SPLIT24`;
head-on death at460. Original queen reconstructed parity461/461. Full oracle
failed51,992/52,007; original worker573 reconstructed mismatches82/362.
No engine counterfactual claimed. Original captured guard state has only
one-turn north survival; clearing A573 visible body (also replacing with
pearls) gives north/west six-turn survival. This supports obstruction feeding,
not an adaptive game outcome.

Implemented fresh `kuroo-03-queen-retention`: late nearby crowns can feed;
known body bordering a fresh queen beacon permits earlier sacrifice; soft
visible-support target scoring; bounded legal queen sprints before emergency
splits plus Akaashi05 threat BFS/dodge. Candidate reconstructed worker573
selects feed at436; candidate queen histories diverge earlier and must not be
used as original-state movement evidence. Full rationale in docs/kuroo-family.md.

Verification: `python3 tests/test_kuroo_queen_retention.py`; inherited escape
(modeE), strike and capacity CPP fixtures compiled against03, all pass.
`.venv/bin/python tools/finals/screen.py --candidate kuroo-03-queen-retention
--opponents kuroo-02-escort-soft-reserve --maps maps/live/slithery_fight.map
maps/live/trophy.map --seeds 81031 --output build/finals/20261008-kuroo03-final-screen`
(dry-run first):2–2, zero runner or
replay faults. Final source hash5ae4fb0d34f6929e1b22f28040b9c86cde7243bc180a5421a0b6d5799481a0d6.
Preliminary pre-threat-BFS screen seed81030 also2–2, separate source.
No strength gain, sandbox runtime validation, upload or promotion measured.
Proposed next: broader paired comparison and runtime audit of03; revisit
queen head-on losses across the12 server loss maps. Active02 preserved.

## 8 October 2026 — Kuroo02 expanded parent comparison

Responding to the request for a more conclusive Kuroo02 comparison, ran two
serial native panels with frozen source, four fresh seeds, both seats, and16
maps (8 maps x2 seeds in each batch):64 games vs Akaashi02 and64 vs Akaashi12.
All128 runner results completed without errors. Replay analysis found no TLE
or invalid-death faults; the registered F1 extractor processed128/128 games,
produced256 side rows and1,152 V0 checks with zero residual failures.

Kuroo02 finished32–32 vs02 and34–30 vs12. The 50,000-draw hierarchical
map/game bootstrap 90% intervals are37.5–62.5% and42.2–64.1%. The four-game
edge vs12 is inconclusive. Feature differences show no clear broad early
material or sprint-cost gain and higher deaths/1,000 dragon-turns vs each
parent (+1.12 vs02, +0.43 vs12; map-bootstrap intervals exclude zero). Wall
deaths are higher vs12 by0.08/1k dragon-turns, with a small positive lower
map-bootstrap bound; the estimate is descriptive. See `docs/kuroo-family.md`
for per-map records, selected paired features, intervals, and artifact paths.
This does not establish improvement or justify promotion. Both variants stay
local; no upload, activation, or server match.


### 8 October — user-requested Kuroo03 expanded map test

Measured final03 unchanged vs02 on all22 live maps, two fresh seeds81032/81033,
both sides:88 games, **31–57**, zero draws/runner errors. All88 replay winner
checks pass; zero TLE/invalid-death events for either bot. Win score35.2%,90%
map-cluster interval[26.1%,43.2%]; advantage−14.8pp[−23.9,−6.8]. Reject03 for
strength, no upload/promotion;02 remains active.

Queens alive at game end03=15/88 vs02=24/88, paired difference−10.2pp
[−17.0,−3.4]. Among59 games reaching300:19/59 vs23/59. Game-end-censored
queen survival round mean201.3 vs218.3, difference−17.1[−39.3,+3.5]. Late queen
segments shed/game1.398 vs1.420: no clear difference. Late length>=8 self-deaths
(r>=400)3.432 vs2.795, difference+0.636[+0.250,+1.068]; these include feeds and
accidental collisions, not causal proof of excessive sacrifice alone.
All intervals resample whole maps.03 combines several rules; ablation needed
to assign causality. No sandbox budget check performed.

Protocol/results/full metrics:
`build/finals/20261008-kuroo03-expanded/{run.py,analyze.py,manifest.json,results.json}`,
`analysis/{summary.json,diagnostics.json}`. Four frozen serial shards, dry-runs
first; native runner tools/finals/screen.py. Per-map table in docs/kuroo-family.md.
Proposed follow-up: isolate local obstruction feed in a fresh snapshot from
the03 queen targeting/dodge/threat changes; no new candidate built this turn.

### Kuroo03 regression diagnosis — 8 October

Follow-up asked what went wrong/how to fix it. Additional replay analysis
`build/finals/20261008-kuroo03-expanded/diagnose.py`, output
`analysis/diagnosis.json`: queen deaths before r29003=66 vs02=56; r290–399
6 vs5; r>=4001 vs3; queens alive15 vs24.29 matches end before290,03 wins9
and loses20. Only guard/dodge/threat changes differ before290; support-target
change starts290 and new crown/body-feeding starts400. Thus the early behavior
regression cannot be attributed to those late additions. This timing does not
isolate individual guard changes or estimate their standalone win effect.

Queen paid movement segments03=154 vs02=22 across88 games. Queen wall deaths
6 vs0; h2h61 vs58. Large self-death length after400 totals4652 vs3959; causes
include intentional feeds and accidental self-collision. These describe the
bundle's play, not independent causal attribution.

Code review: new queen dodge permits paid sprint paths from round zero and
ranks endpoint risk without an explicit retained-length cost. New late escape
fallback picks the first path passing the terrain/body horizon, with no
explicit enemy-reach landing filter. Existing after_path tests obstacles and
future head adjacency but does not itself reject enemy-reachable current-turn
landings. Body feed trigger proves adjacency to a<=2-round beacon, not that
this body is the critical blocking route or that the queen can harvest the
corpse safely. Blanket late crown role conversion starts within range16,
before a verified local need. Queen support bonus attracts any visible ally
head, without testing whether it can actually escort/protect her.

Proposed fix: fork02 and isolate local obstruction-feeding from global guard
changes; require current visible queen or an explicit distress request,
verified obstruction/route benefit and safe food access, elect one donor,
preserve cover under an active attack. Test queen movement independently:
prefer safe free sprints, penalize paid length loss unless needed for survival,
apply landing threat checks to every fallback, and use bounded search capable
of the long queen's actual free-step allowance rather than an arbitrary
three-step ceiling. Future horizon currently models single-step turns and
can be pessimistic for long queens; change that only as a separately tested
snapshot. Run component ablations and broader paired/runtime checks before
combining. No bot source edits or promotion performed in this diagnosis turn.

## Kuroo04/05 — isolated corrections from02 (8 October)

User approved separate corrections and tests after03 regression diagnosis.
Both new snapshots fork immutable02; none of03's blanket crown conversion,
all-game sprint dodge/threat changes or queen support attraction are retained.

- `kuroo-04-local-obstruction-feed`: after400, a visible queen must have no
  clear known adjacent exit. Donor body removal must open an adjacent food
  cell with another known step; elect lowest ID among visible local blockers;
  do not sacrifice with a visible enemy head within6 of the queen. Return an
  intentional self-feed only into known own body. Existing feeder/crown
  behavior otherwise stays inherited. This checks a local two-step opening,
  not a full future queen survival certificate. Invisible queens cannot
  request rescue in04; no new distress radio protocol has been implemented.
- `kuroo-05-free-queen-escape`: after290 and length>=8/full known body, try
  a bounded beam of legal **free** paths before a split or short-horizon
  action. Search up to `min(16,ceil(length/4))` steps, beam8 endpoints and
  at most16 horizon questions. Require known terrain and landing outside
  marked enemy reach/head adjacency; retain inherited six-turn body check.
  No extra paid movement, no early guard change, no new feed rule. This
  still inherits the guard's single-step future-turn model and optimistic
  node-cap behavior; it does not fix every long-queen pathfinding limitation.

Regression `python3 tests/test_kuroo_isolated_safety.py` passes: donor
eligibility, clear exit/unknown terrain/attacker/early/invisible exclusions,
single-donor election; five-step free queen escape beyond the old three-step
cap with preserved length, unsafe/early/partial-body rejection. Inherited
queen escape(modeE), queen strike and soft reserve CPP fixtures pass for both.

Frozen fingerprints:
04 `e9961318b84164f3297dc0c49b8aa8f22576646ea5de0c9a85c439c7141dd1e4`;
05 `bf5e7308ae8bdcbd31538f399171cb3b01da36a6b6b11b133d757f68185f4041`.

Native development panel: each against02 on all22 live maps, seed81034,
both seats,44 games each/88 total. Four independent serial shards, dry-run
first. Both source fingerprints unchanged after testing. All88 replay
winner checks pass, zero runner errors/TLE/invalid deaths for either side.

| Result | Kuroo04 | Kuroo05 |
|---|---:|---:|
| Win/loss vs02 |22–22|21–23|
| Map-cluster90% score interval |[50%,50%]|[43.2%,50.0%]|
| Queen alive at game end,candidate vs02 |12/44 vs12/44|12/44 vs12/44|
| Final queen length mean,dead=0,candidate vs02 |3.841 vs3.841|4.614 vs3.841|
| Late queen segments shed/game,candidate vs02 |1.614 vs1.614|0.886 vs1.614|

Every04 map is1–1. All22 swapped-seat replay pairs have identical gameplay
snapshots/events/results: no observable effect on this panel. The degenerate
bootstrap interval reflects one seed and exact paired symmetry; it is not
proof of equivalence on unseen seeds/maps or that the new predicate never
runs (an inherited feed could choose the same action).

05 is1–1 on21 maps and0–2 on Islands. Logged `BK:L` new free escapes occur
**twice**, on Stronghold/Islands;20/22 map-pair replays remain identical.
Stronghold A queen finishes49 versus15 for the02 A queen in the swapped
control-like seat pair; she sheds32 rather than64, but A still loses to a
length74 B queen. Islands A queen survives358 vs339 in the swapped02 A
history; both queens ultimately die, and candidate A loses rather than
winning. Thus the measured length benefit is concentrated in one map and
has no demonstrated win gain. These reactive paired games are not fixed
opponent engine counterfactuals. Do not combine/promote these candidates.

Focused05 sandbox check: Slithery Fight, seed81034, both sides,1–1, same
winner per seat as native. No candidate TLE/invalid deaths across53,510
metered turns. Candidate peak11,060,270 points(A)/10,904,744(B);
p99 8,235,691(A)/8,073,997(B). This is a two-fixture runtime screen, not
coverage of every map or worst-case search state.04 has no sandbox check.
Artifacts `build/finals/20261008-kuroo05-runtime/runtime-audit.json`.

Reproduction/analysis:
`.venv/bin/python build/finals/20261008-kuroo04-05-isolated/run.py` (fresh
output), `python3 .../analyze-kuroo04.py`, `python3 .../analyze-kuroo05.py`,
`python3 .../effects.py`. Full manifests/maps/replays and per-game summaries
are in that directory, with combined `kuroo04/analysis/` and
`kuroo05/analysis/`. No upload/activation; Kuroo02 stays active.

Proposed next: a separate queen-issued targeted distress packet is needed
for the original1431111 case, where the donor's head is outside queen vision.
The queen should identify the obstructing donor and requested opening; the
donor should validate a fresh request and local body match, and only one
should yield. This requires its own radio/turn-order regression and paired
comparison. The stronger04 visibility condition alone cannot fix that
specific original state. No distress candidate built in this turn.

## Kuroo06/07 — targeted queen distress (8 October)

User explicitly requested implementation and continued interrupted test runs.
06 forks02;07 forks06 solely to fix the visible-queen distance rejection.
Measured snapshots remain immutable. Active server remains02; no upload or
activation was performed.

Protocol type8 uses the existing team marker/checksum envelope. Payload:
donor ID12 bits, opening x/y7 bits each, round9 bits, queen ID1 bit,
pre-action queen length8 bits. Requests expire after two rounds, never rewind
a newer request, reject wrong recipients/team markers/corrupt checksums and
invalid coordinates/times. The queen, from r400/length>=8/full known body,
selects one nearby body owner whose removal increases known reachable space
by>=4 cells to>=8 total (BFS cap min32,length+4). Preserve a visible escort
head if a visible attacker is present. This is a bounded static topology
check, not a guarantee of future safe pathfinding or food harvest.

Donor eligibility requires length>=8, the named opening still matching
known own body, a fresh request, no visible enemy head within6 of the opening,
and a visible queen still near it. Exception: a same-round queen sighting may
certify an off-screen unknown tail of a partially reconstructed body, within
plausible body distance; never contradict visible cells, and never apply
this certificate after the next round. The donor selects a known own-body
collision, marked as intentional feed so the inherited guard preserves it.
Verified queen strikes still take priority. Queen movement/split guard is
unchanged: this protocol does not ban emergency splits or prove that the
original1431111 queen retains31 cells.

Requests override gossip on all four sonar directions. Sonar can hit the
selected body while its head is outside queen vision, but intervening own
and foreign bodies can block/refract rays. Sending a request is not receipt.
Diagnostics `QD:R <donor> <cell>` and `QD:F` distinguish sends and feeds.

### Regression and replay evidence

`python3 tests/test_kuroo_targeted_distress.py` verifies target/topology,
expiry, exact-recipient, checksum/team, attacker, future/stale, monotonic
message order, known-body and current unknown-tail-certificate conditions.
`python3 tests/test_kuroo_distress_visibility.py` verifies the06 rejection
and07 acceptance of a queen two diagonal cells from an opening (Manhattan4,
Chebyshev2), with expiry/distant-queen rejection retained.
`.venv/bin/python tests/test_kuroo_distress_delivery.py`, also run with
`KUROO_DISTRESS_BOT=kuroo-07-distress-visibility`, runs an official-engine
fixture with the native donor process: protocol3 is negotiated before the
message, the distant donor receives it in the same round and self-feeds,
and the scripted queen grows8→9 on the donated food. The fixture deliberately
ends other actors with empty commands; it is a mechanism regression, not
an adaptive win/survival trial. Inherited escape(modeE), strike and capacity
CPP fixtures passed against both06 and07.

Original1431111 reconstructed queen history emits a request to573 at
protocol438, while retaining `SPLIT24`. Injecting that packet into worker573's
reconstructed history yields intentional `MOVE E`/`QD:F` at438. Original
worker reconstruction has82/362 command mismatches; original full engine
oracle fails. These are decision diagnostics, not an exact engine
counterfactual or a saved-game claim. Artifact directory
`build/finals/20261008-kuroo06-distress/`. An initial captured-body fixture
sent a64-bit packet before first-turn protocol negotiation; it failed and
was replaced by the portable protocol3-negotiated regression above.

### Native and sandbox results

Each candidate was compared against02 on all22 live maps, seed81036,
both starting sides (44 games each). Dry-runs first; source/map hashes pinned.
06 raw result23–21, but three invalid deaths occurred before the new protocol
starts: opponent149 r204 on Stronghold, candidate750 r250 on Slithery,
opponent110 r378 on Weakhold. Zero TLEs.41 clean games score21–20,90%
map-cluster interval[47.6%,55.0%]. Do not credit those early faults or cross-run
behavior differences to late distress rules.06 had19 request turns in one
Stronghold game, only one named-donor ray hit, and zero actual feeds.

06/07 replay states in that Stronghold seed already differ at r205, following
the06 opponent invalid death. Therefore06→07 whole-game outcomes are not a
clean late-rule causal comparison, despite matching map/seed/source manifests.

07 final result **22–22**, all44 replay winner/fault checks pass: zero runner
errors, TLEs or invalid deaths. Every map is1–1 on this seed. End-game queens
alive7/44 on both sides; queen final length mean2.795 vs0.955 (dead=0).
The degenerate50% map-bootstrap interval follows exact paired score symmetry
with one seed; it is not proof of equivalence/generalization.

**Observed successful feed:** Stronghold, candidate B, queen1 requests donor5
at r422; donor5 self-feeds that round at length49. Queen eats16 corpse pearls
from that donor, survives to500 and finishes length87, versus6 for the
corresponding02 B queen in the opposite-seat run. Mirrored gameplay states
are identical through start-of-round422 and first diverge at423 after this
request/feed.07 has one request and one successful feed across the44 games.
The stronger final queen does not change the match winner or aggregate
win rate; the measured benefit is concentrated in this one case.

07 Stronghold sandbox, same seed/both sides:1–1, zero candidate TLE/invalid
deaths across25,888 metered turns. Candidate peak10,256,438(A)/10,336,059(B)
points; p99 8,057,655(A)/8,515,144(B).06 Slithery sandbox pair also finishes
1–1, zero candidate faults across52,274 metered turns; peak10,992,064(A)/
10,954,174(B), p99 8,557,994(A)/8,402,543(B). These are focused runtime
screens, not all-map/worst-state budget guarantees.

Interrupted07 native fixtures and06 sandbox attempts were resumed using
unchanged sources, retaining completed results. Harness180/360-second
wall-clock timeouts are recorded; a600-second retry completes the06 A
sandbox game in127.9s after recovery. Two07 native timeout entries were
rerun to completion. Do not classify harness timeouts as judge TLE events.

Frozen hashes:
06 `4f3480f7cedafa8f8e457fe722abe9fea1ca342b97823a1096f7b87ec58ff002`;
07 `d01d1fa570f56a4048afa684b2c3d8b0088f741db668c6f3652f80de84942ace`.

Artifacts: `build/finals/20261008-kuroo06-screen/analysis/`,
`build/finals/20261008-kuroo07-screen/analysis/` (summary, activity and
feed-case.json), and `20261008-kuroo06-runtime/`/`20261008-kuroo07-runtime/`
(runtime-audit.json, logs and replays). Each screen has run.py/analyze.py and
four frozen part manifests;07's recovery runner resumes existing results
with600-second limits. Protocol mechanism implemented and tested; **07 stays
local/unpromoted**,02 remains active. Proposed next: independent fresh seeds
and opponents, with receipt-aware routing if requests remain rarely delivered.

### 8 October — user-requested Kuroo07 submission and activation

User explicitly instructed “submit and keep it active”, superseding the
previous request to retain02 and the local-only status of07. Exact tested
snapshot `d01d1fa570f56a4048afa684b2c3d8b0088f741db668c6f3652f80de84942ace` packaged as15 root C++ source/header
files, zip3760694 bytes, SHA256 `25dd4d8af6488e3363d2f338aaf6a260e7087bd6f4ac96cc0014afa4f66468dc`. Fresh authenticated
preflight verified team7 and incumbent20472. Uploaded once as**20627/v112**,
`LV-kuroo-07-distress-visibility-25dd4d8a-ai`. Server compilation completed successfully; authenticated
readback verifies20627 is the**sole active** submission. Server sourceHash
`7e9f3afe2cad37d6d3b2076cc33d5dc6d8be2f5c727c8bdb0e4938bab635d07d`. No incumbent restoration or new match queue.

This is an explicit user-requested deployment, not statistically confirmed
strength promotion; the measured22–22 development panel remains unchanged.
Receipt/archive/preflight/readback: `build/finals/20261008-kuroo07-submit/`.

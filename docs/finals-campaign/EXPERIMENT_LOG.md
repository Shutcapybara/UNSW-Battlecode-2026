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

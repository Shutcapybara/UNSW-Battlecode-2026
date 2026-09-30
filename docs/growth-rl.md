# Unattended opening-growth learning on the RTX 3060

The campaign lives in `tools/growth_rl/`, with machine settings in
`configs/growth-rl-3060.json`. Generated games, feature caches, models, logs and
reports live under `build/growth-rl-3060/`. Existing measured bots are controls.
This is a local research campaign, not an automatically activated ladder bot.

## What is learned

The default opening objective is retained team growth from the current turn to
round 100:

```
log(1 + team_length_100) - log(1 + team_length_now)
+ 0.25 * [log(1 + living_dragons_100) - log(1 + living_dragons_now)]
```

The population weight is an explicit objective setting, not a split rule. The
dominant term rewards retained length: spawning more dragons by splitting the
same material does not masquerade as length growth. No reward is assigned just
for splitting, moving toward a pearl, avoiding a portal, or reaching a hand-set
population on a particular map. Deaths and sprint costs matter through retained
team material. Early completed games use an explicitly absorbing terminal state;
reports mark checkpoints beyond the actual match duration.

A neural critic predicts these outcomes at +10 rounds, +25 rounds, and r100. A
separate head predicts final win/draw score. Final win is a training label for
that head, never a policy input and never an action bonus. The actor uses
Monte Carlo advantage-weighted regression: recorded actions followed by growth
above the critic's prediction get more weight. Advantages are clipped through
bounded exponential weights. This is replay-based policy learning; it does not
prove that changing an action will cause the predicted outcome. New local games
provide interaction data, and paired evaluation determines whether to replace
the local incumbent.

Both extraction and deployment use `features_view.Proc`, based on the dragon's
actual protocol view and its own history. The policy sees neither map names,
source IDs, replay results, absolute coordinates nor future observations. Full
replay state is used only for rewards and statistics. Structural features such
as map dimensions, visible beds and observed body occupancy remain available.

The action vocabulary contains four one-step moves, sixteen complete two-step
sprints, and three split allocations: minimum child, half, maximum child.
Duplicate/invalid splits are masked from engine constraints. Longer sprints,
other split sizes, invalid commands and explicit suicide are excluded and counted
in the train/validation coverage report; locked test coverage is not serialized,
and unsupported actions are never relabelled as a different action.
Fatal movement choices remain learnable. This finite vocabulary and the existing
feature representation are capacity limitations, not a claim of unrestricted RL.
The current bot sends no sonar. Its policy runs after r100 too; a specialised
endgame policy is not implemented, so final win regression remains a real risk
and is part of the promotion gate.

## Collection and overfitting controls

The collector reuses `tools/download_team_games.py` through the hub's paced,
read-only API client. It takes completed ranked and unranked games from the
current top ten, preserving game, series, team and exact submission IDs when the
API supplies them.
Missing submission identities stay explicitly unknown. An explicit team and
submission list can replace automatic selection. Current rank is rank at fetch
time, not a reconstructed historical rank or evidence that an unranked loss was
intentional. Ranked status and missing submission identity remain explicit in
the dataset. Submission IDs are resolved from either flat fields or nested team
objects when present; the collector never infers a historical version from a
team's current active submission. The API key comes from `BATTLECODE_API_KEY`,
the `unswbc auth` user store, or the ignored `.battlecode-api-key` file; it is
not copied into models, settings or logs, nor forwarded to signed replay
storage URLs.

Series are discovered from public team profiles and expanded into completed
games; the HTML downloader is a fallback. The downloader now skips pending-only
history pages instead of stopping early.
Requests are paced and bounded to 60 new games per pass. A read-only collector
refreshes the corpus every 15 minutes while training and paired evaluation run;
it shares a lock with dataset extraction so partial downloads cannot enter a
training snapshot. Failure to reach the public API does not stop local learning.
Dataset extraction rejects unsupported,
unfinished or reconstruction-inconsistent replays. The cache identity is the
decompressed replay SHA-256 plus extractor version. Gzip/raw copies deduplicate.

Both sides and all windows of a game stay together. Related games use series
identity when available; mirrored local fixtures share a group. A deterministic
hash assigns 70/15/15 train/validation/test buckets. Old holdouts never migrate
into training as the corpus grows. Unknown public series identities fall back
to game/content identity and cannot guarantee opponent/submission independence.
No game is moved into validation merely to make a small run succeed.

The three configured map holdouts are also forced into the replay-test split.
Their replay statistics stay out of training, validation, and the cohort
distribution report. The repeated local generalisation fixtures include these
maps as part of the current 29-map benchmark, so that fixture gate is adaptive
validation rather than a locked final map test.

Feature schema, normalisation, actor and critic fitting use training games only.
The critic and actor select checkpoints with validation metrics. Test metrics
stay locked unless `train --final-test` is explicitly requested. The default
pool panel is separate from rollout/bootstrap maps. Public-corpus map holdouts
can be specified through `holdout_map_names`. Repeated validation is adaptive;
this is not a multiple-testing-corrected claim of improvement.

Each side-game has equal training weight, avoiding accidental overweighting of
large swarms. RAM is bounded by deterministic sampling of at most 48 action rows
per side-game after full reward reconstruction. The runner also keeps only the
ten series snapshots needed by checkpoint reports after labeling actor rows;
the fingerprint includes this row budget and the extractor version, so a changed
sample cannot silently resume unfinished training. The GPU receives minibatches,
not the entire corpus. The current cap is 1,000 distinct games. The first auth-backed refresh
added 60 public replays to an inventory that already held 949, plus 24 bootstrap
and 3 self-play fixtures; the dataset therefore uses a stable hash sample when
the accumulated corpus exceeds the cap. Selection is not permanently the first
1,000 filenames.

## The unattended loop

1. Refresh the ranked replay corpus, retaining old completed downloads.
2. If needed, bootstrap local games using the existing Vibing++ learned clone
   against Yuna and Ouroboros on three training maps.
3. Reconstruct and audit data; fit the growth critic and weighted actor on CUDA.
4. Export a dependency-free JSON policy and check its logits against PyTorch.
5. Play candidate and incumbent against identical map/opponent/seed/seat fixtures.
6. Promote only the local incumbent pointer if retained growth improves and the
   win-rate guard and population/material guards pass.
7. Play exploratory candidate rollouts on training maps, including one game per
   cycle against the separate ranked top-ten winner tree when at least ten
   eligible training games are available, then repeat with new data.

The top-ten winner tree is fit only on public ranked training games where the
winner's recorded rank is 1–10. It reports action-match and NLL on that cohort's
validation games when available, but remains an exploratory zoo opponent; it
cannot be selected as the promoted policy from this offline score. Its local
rollout is tagged separately in provenance so later reports can distinguish
tree-opponent games from the existing rollout pool.

Candidate acceptance uses paired native fixtures on the 10-map live pool and the
29-map off-pool panel, seeds 1–3, both seats, the fixed eight-bot zoo, and
`lune-r1-07-latecap8x-only`. The initial comparison baseline is
`renoir-23-nodevil`, selected because its policy removes Devil's map-dimension
terms. Those two source snapshots are pinned under the campaign's
`reference-bots-20260930` directory from Git commit `6287e163`.

The 90% bootstrap resamples map/opponent clusters, keeping seats and seeds
together. A candidate must complete both panels, improve retained growth on the
live pool, stay within 0.02 on generalisation, and keep r100 population, total
material, and win-score lower bounds above -0.02 on both panels. The upper
interval for each wall, self, body, and head-to-head death rate must stay within
10% of the baseline. Reports include r10/r25/r50/r75/r100 deltas for population,
material, longest dragon, pearls and corpse-pearl share. The replay distribution
report groups those measures by source cohort and win/loss outcome. Training
also writes `phase_behavior.json` and `phase_behavior_summary.json`: full-replay
pearl, death, split, sprint, and supported-action rates for r0–r10, r10–r25,
r25–r50, r50–r75, and r75–r100, split by cohort, outcome, window completion,
and map. These statistics are computed before actor-row sampling; locked test
games stay out of both reports. This is a local evidence gate; it does not
establish live Elo or judge CPU safety.
Evaluation replays are rejected if accidentally supplied as training data. The
worker makes no submission, activation or challenge API calls.

The paired panel journal is flushed after each completed fixture. If `STOP` is
requested during a panel run, the worker finishes active fixtures, stops, and
resumes the same cycle and missing fixtures at the next start. The gate uses
two concurrent fixture workers on this PC.

Each local game also appends an experiment record through the repository's
`StatsStore(queue_only=True)`. Its `.run.json` receipt names the run under
`game_stats/local/runs/`. Shared aggregates are not rewritten by the worker.

## Next-mechanism evidence

The attached 30 September baseline calls Sciel-03b's visible ally-saturation
discount the next EW-food experiment. That queue is superseded by the later
`origin/r/sciel:claude/sciel-status.md`: 03b and its radio-informed 03c variant
left ally head-on deaths +31% and +38%; right-of-way variants 04a/04b still left
them +29%/+24% and reduced pool win rate. The report closes the EW-memory family
and names target claims as the next distinct mechanism. Do not spend another
cycle repeating a visible-density discount.

Target claims require a dragon to send its intended bed/cell and peers to use
that claim when choosing their next target. This learner currently emits only
move/split actions and sends no sonar, so target claims need an explicit
protocol/action extension; a movement-only feature cannot implement the
mechanism. If added, keep the same paired pool and generalisation gate and
report arrival collisions, retained material, population, deaths, and win
score. Do not fold it into the active frozen cycles or bypass their gate.

## Windows operation

The isolated environment is `build/rl-venv/`. On this machine it was created
using the installed Python 3.13 executable; the Windows Store `python` alias
did not work. CUDA PyTorch uses the cu128 wheel, supported by the installed
572.83 driver. The tested GPU is an RTX 3060 with 12 GB VRAM.

```powershell
# Start hidden; no console window required.
./tools/growth_rl/Start-GrowthRL.ps1 -Action start

# Read current stage and process liveness.
./tools/growth_rl/Start-GrowthRL.ps1 -Action status

# Request a graceful stop at a bounded stage/game boundary.
./tools/growth_rl/Start-GrowthRL.ps1 -Action stop

# Resume the worker automatically at this Windows account's next logon.
./tools/growth_rl/Register-GrowthRLTask.ps1 -Action register

# Remove that logon task.
./tools/growth_rl/Register-GrowthRLTask.ps1 -Action unregister

# Run a single foreground cycle.
./build/rl-venv/Scripts/python.exe -m tools.growth_rl run --config configs/growth-rl-3060.json --once

# Download only, using the same collector.
./build/rl-venv/Scripts/python.exe -m tools.growth_rl collect --out build/growth-rl-3060/public --max-downloads 30
```

`status.json` reports stage, PID, timestamps and errors. Logs are
`worker-*.log` and `worker-*.err.log`. `STOP` requests shutdown; starting again
removes that marker. An OS file lock prevents two workers using the same output.
Completed replays/features and persistent incumbent state survive restart;
interrupted training can be restarted without overwriting earlier cycle folders.
`cycle.json` tracks unfinished work so evaluation resumes from its paired
fixture journal.
`last.pt` is saved each training epoch. The internal training API also supports
resuming matching network/feature checkpoints. The per-user logon task starts
the hidden worker after the next sign-in and skips launch when its recorded
worker is already live. It uses the user's profile, including the local
`unswbc auth` store. The current process continues after this chat while Windows
stays awake; the task does not run before that user signs in.

Inspect `cycles/NNNNNN/training/` for `training_summary.json`, `policy.json`,
`model.pt`, `checkpoints.csv`, `distributions.json`, `cohort_summary.json`, and
`win_associations.json`.
Distributions use one observation per side-game at r10/25/50/75/100, grouped by
map, ranked/unranked source cohort, available submission ID, rank snapshot, and
win/loss/all. The row-level CSV also retains team ID and fetch time for submission
history analysis. `cohort_summary.json` aggregates those visible train/validation
observations across maps by source cohort, checkpoint, and win/loss/all, with
sample counts, quantiles, pearl income over trailing 10-round windows,
corpse-pearl share, and deaths per 1,000 dragon-turns. It is descriptive; rows
can share a game, team, or submission and are not independent confidence bounds.
The locked test split is excluded from both reports.
Win association fits only surviving-to-checkpoint games and reports held-out
predictive metrics; it cannot turn correlations into causal strategy advice.
`evaluation/gate.json`, `pairs.json`, and `pairs.jsonl` record paired-game
decisions and resumable progress. `incumbent.json` exists only after a
candidate passes the full local gate.

## Evidence behind the design

The older Q1/Q4 findings identify the r100 material deficit and weak local
opponent pressure. The newer `TEAM-SUMMARY-2026-09-29.md` and
`analysis/BENCHMARKS.md` refine that into retained growth, efficiency and loss
rates: forcing a production schedule did not fix pearl-bound growth.
`analysis/C1-pace-targets.md` shows why pooled population targets are misleading.
The out-of-sample rule excludes map-name policy branches. The replay statistics
handoff supplies identity, grouping and causal-interpretation cautions; its old
Mac-only/no-training task constraints do not describe this Windows RL request.
These reports are historical evidence, not a substitute for the new experiment.

The legacy `rl_earlygame_gpu.py` remains a separate prototype. Its selected-action
dueling-Q bug is repaired: training now gathers the chosen value from the full
action menu rather than cancelling the advantage in a singleton forward pass.
The new campaign does not use that prototype's hand-shaped portal/split rewards.

Validation command:

```powershell
./build/rl-venv/Scripts/python.exe -m pytest tests/test_growth_rl.py tests/test_rl_earlygame.py tests/test_download_team_games.py -q
```

# Finals option-policy workflow

Read [the working memory](../../FINALS_WORKING_MEMORY.md) before running games.
Measured bot sources are immutable. All output belongs under `build/finals/`.

The retained bot is Bokuto 18. Bokuto 62 and 63 are isolated economy experiments;
64 is the copy-and-propose interface, and 65 adds the native collection handshake.
None of these numbers implies promotion. See the working-memory ledger for results.

- `screen.py`: explicit candidate/opponent/map/seat/seed fixtures, frozen bot sources,
  one worker, bounded games, dry-run and checked resume. Runner errors are separate.
- `replay_probe.py`: builds an instrumented copy and reconstructs local legal histories
  to inspect movement/production/escape and guard decisions. Server timers need an oracle.
- `parity.py`: compares complete native replies (including radio order) over replay histories.
- `collect.py`: runs full official-engine episodes against native frozen opponents.
  A `FINALS_RPC=1` build of 65 emits encoder/action candidates, receives `SELECT`, emits
  packet candidates, receives `SEND`, then commits the selected turn. Only encoder and
  candidate arrays go to the actor; replay/outcome/team identifiers remain metadata.
- `model.py`, `clone.py`: shared 32-unit candidate scorers and incumbent-label warm-start.
  Clone accuracy is integration evidence. It does not establish strategic improvement.
- `model_parity.py`: checks exported C++ float32 scores and argmax against PyTorch.
- `ppo.py`: earlier resumable action-only or sonar-only ablation trainer.
- `spatial_model.py`, `train_spatial.py`: encoder-v1 CNN/scalar shared trunk with conditional
  action and sonar heads, baseline-choice warm start, joint resumable PPO, and a fixed greedy
  monitor panel. One dragon-turn PPO likelihood is the action log-probability plus the four
  sonar-ray log-probabilities conditioned on the selected action features. Both heads and the
  shared encoder learn from the same terminal team return. `--actor action` and `--actor sonar`
  remain single-head ablations. Writes `progress.jsonl`/`progress.csv`, per-update checkpoints
  and paired results. The repeated monitor is not independent confirmation.
- `export_bot.py`: creates a new standalone C++ artifact and archived checkpoint under
  build/, physically removes the unused atlas, and compiles default greedy inference.
- `analyze_screen.py`: map-cluster intervals, carried totals/queen survival, fault scans,
  and matched keeper deltas when a matching baseline screen is supplied.

Compile the collector and obtain native opponent binaries via the toolkit or a prior
frozen screen, then collect a complete episode:

```sh
g++ -std=c++20 -O2 -DFINALS_RPC=1 bots/bokuto-65-policy-collector/main.cpp \
  -o build/finals/option-rpc
.venv/bin/python tools/finals/collect.py --bridge build/finals/option-rpc \
  --opponent <native-frozen-opponent> --map <development-map> --seed 61006 \
  --seat A --output build/finals/example-episode
.venv/bin/python tools/finals/clone.py --actor action \
  --data build/finals/example-episode/episode.npz --epochs 5 \
  --output build/finals/example-clone
```

The submitted runtime needs no Python, RPC or trace logging. Export/integration and
judge checks must pass before using a model. PPO development results, action retention,
staged sonar training and fresh confirmation gates remain separate tasks.

Collection keeps terminal team reward (+1/-1/0) as the objective and adds bounded
Heartbreaker potential-difference shaping (alpha 0.2, gamma 0.997). Potential uses the
queen/longest/total-length tiebreak proxy, queen survival, material advantage, and distinct
head-visited tiles, with a normalized weighted sum in [-1, 1]. It is computed from the
completed official replay and used only for reward labels; privileged replay state never
enters actor inputs. Terminal potential is zero on elimination and round-limit endings, so
discounted shaping telescopes to a start-state constant. It does not pay raw per-turn bonuses
for eating, feeding, sending sonar or staying alive. The exact constants are pinned in each
run manifest and `collect.py`.

`EngineModule.rounds` is the final protocol round label; the CLI prints that value plus one.
A donor's last decision keeps discounted team credit after its own death. Collection retains
actual commands and masks unexpected guard overrides out of actor training. Training normalizes
by team round and episode so swarm size and packet count do not multiply the objective. The
console reports terminal W/D/L reward separately from shaped policy return and its potential
contribution; use terminal outcomes and held-out paired score to judge strength.

## Joint spatial policy trainer

The trainer retains the audited 1,193-value encoder-v1 input and uses one shared encoder for both
candidate heads. The sonar scorer receives the selected action's full 32-value feature vector, so
its packet decisions are conditioned on the movement/landing intent. PPO sums the chosen action
log-probability and all four conditional sonar-ray log-probabilities, then applies the same
terminal team return to both heads and the shared representation. Training uses equal
episode/round weights. `--actor action` and `--actor sonar` are available for ablations; the
default is joint training.

This prototype does not yet train persistent options, an offline IQL warm start, or a centralized
full-team critic. Its value head sees the same local observation as the actor. The shaped reward
implementation has passed formula/credit tests and replay decoding against a saved full game, but
has not yet been trained or shown to improve match strength; promotion still requires independent
held-out confirmation.

Create a fresh RPC bridge, native fallback opponent and incumbent-label warm-start episode:

```sh
mkdir -p build/finals/spatial-encoder
g++ -std=c++20 -O2 -DFINALS_RPC=1 bots/bokuto-68-sonar-history/main.cpp \
  -o build/finals/spatial-encoder/bridge
g++ -std=c++20 -O2 bots/bokuto-18-queenfeed/main.cpp \
  -o build/finals/spatial-encoder/bokuto18
.venv/bin/python tools/finals/collect.py --bridge build/finals/spatial-encoder/bridge \
  --opponent build/finals/spatial-encoder/bokuto18 --map maps/maze.map --seed 61610 \
  --seat A --output build/finals/spatial-encoder/warmstart
```

Train both heads together against the fallback while checking a fixed, distinct four-map monitor
panel after each update:

```sh
.venv/bin/python tools/finals/train_spatial.py --actor joint \
  --bridge build/finals/spatial-encoder/bridge \
  --warmstart-data build/finals/spatial-encoder/warmstart/episode.npz \
  --opponents build/finals/spatial-encoder/bokuto18 \
  --maps maps/maze.map maps/islands.map maps/portals.map maps/stripes.map \
  --eval-opponents build/finals/spatial-encoder/bokuto18 \
  --eval-maps tools/ouroboros/holdout/default_FY.map \
    tools/ouroboros/holdout/trauma_FY.map tools/ouroboros/holdout/trophy_TFX.map \
    tools/ouroboros/holdout/Colosseum_FY.map \
  --updates 4 --games-per-update 2 --eval-games 8 --epochs 3 \
  --threads 8 --workers 4 \
  --output build/finals/spatial-joint-shaped-pilot
```

For continuous training, use the same inputs and output path, replace `--updates 4` with
`--until-stopped --eval-every 5`, and press Ctrl+C when you want to stop. Completed updates are
checkpointed; restart the same command with `--resume` to continue. The monitor is still the same
fixed panel, so use it as a plateau signal rather than independent confirmation.

`--workers` runs independent official-engine episodes in isolated processes and preserves fixture
order when collecting results. Training uses at most `games-per-update` workers; with two games,
the setting above uses two concurrent training games and four concurrent evaluation games. Each
worker receives a read-only policy snapshot and divides the requested PyTorch thread budget across
workers. The default is one worker for backwards-compatible serial runs.

The console prints each game's terminal reward and, after each update, PPO losses, active action
and sonar decisions, per-head baseline-choice rates, training reward/score, cumulative training
reward/score, shaped policy return and potential contribution, evaluation score against the cached
baseline on identical seeds, map-cluster
interval and monitor trend. `progress.csv` stores the same update summaries and can be opened in a
spreadsheet. For improvement, focus on `paired_score_delta` and its interval on the fixed monitor;
cumulative terminal reward mostly grows with the number and outcomes of sampled games. To extend
the same run, repeat the command with `--updates 10 --resume`; keep the remaining arguments and
input hashes unchanged. The earlier terminal-only pilot cannot be resumed under this reward/code
version; start a fresh output directory. Incumbent-label warm-start episodes remain schema-
compatible because the clone uses action/sonar labels, not saved returns; rebuild and recollect the
episode if its ignored `build/` artifact is absent.
Use `--actor action` or `--actor sonar` for single-head ablations. A flat
monitor is a plateau *signal* on that repeated panel, not proof of generalization or a promotion
decision.

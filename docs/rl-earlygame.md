# Early-game offline RL

`tools/rl_earlygame.py` fits a small offline fitted-Q policy from replay
actions. It is aimed at the failure mode identified in the field analysis:
being materially behind by round 100, then losing more material by round 250.

The training rows use the same actor-local v4 observation features already
used by the imitation-learning tools. The reward has four parts:

- final win/loss reward injected at the round-100 checkpoint and trajectory end;
- small population and length progress rewards;
- pearl and early split rewards to improve the opening economy;
- safety penalties for kelp, portal transit, low-space moves, and nearby enemy
  body segments.

This is deliberately not trained on final standings as an online input. The
final outcome is a training label only. At runtime the policy sees the current
protocol feature row and filters out visible kelp moves. The exported
`model.json` is scored by `tools/rl_runtime.py`, which has no numpy,
scikit-learn, or PyTorch dependency.

Training requires the replay dependencies used by the existing recon tools,
including `pycapnp`, plus numpy, pandas, and scikit-learn:

```sh
python3 tools/rl_earlygame.py train \
  --replays public_replays/team-306 \
  --out build/rl-earlygame \
  --max-games 80 --max-round 250
```

The output includes:

- `model.json`: deployable linear Q model;
- `training_summary.json`: replay hashes, splits, hyperparameters, holdout
  metrics, and winner/loss feature distributions;
- `validation_predictions.csv` and `test_predictions.csv`;
- `splits.json` and `replay_manifest.json`.

To score a state saved as JSON:

```sh
python3 tools/rl_earlygame.py recommend \
  --model build/rl-earlygame/model.json --state state.json
```

The model is an opening policy component, not a complete bot. It should be
gated by the bot's existing legal move generator and compared in bounded
live tournaments, especially on Portals and other maps where CPU/TLE deaths
are strongly map-dependent.

## RTX 3060 trainer

Install the CUDA PyTorch wheel appropriate for the installed NVIDIA driver,
then run:

```sh
python3 -m pip install numpy pandas scikit-learn pycapnp
python3 -m pip install 'torch>=2.7' \
  --index-url https://download.pytorch.org/whl/cu128
python3 tools/rl_earlygame_gpu.py train \
  --replays public_replays/team-306 \
  --out build/rl-earlygame-gpu \
  --max-games 120 --max-round 250 --batch-size 2048
```

The GPU trainer is a dueling Q-network with a target network, mixed precision,
and a small conservative-Q penalty to reduce unseen-action overestimation. It
writes both `model.pt` and a traced `model.ts`. The 3060 is used for network
fitting; the final tournament bot should normally use a distilled or JSON
policy because the tournament CPU budget is separate from the training
machine.

## RTX 3060 trainer

Install the CUDA PyTorch wheel appropriate for the installed NVIDIA driver,
then run:

```sh
python3 -m pip install -r tools/requirements-rl.txt
python3 tools/rl_earlygame_gpu.py train \
  --replays public_replays/team-306 \
  --out build/rl-earlygame-gpu \
  --max-games 120 --max-round 250 --batch-size 2048
```

The GPU trainer is a dueling Q-network with a target network, mixed precision,
and a small conservative-Q penalty to reduce unseen-action overestimation. It
writes both `model.pt` and a traced `model.ts`. The 3060 is used for network
fitting; the final tournament bot should normally use a distilled or JSON
policy because the tournament CPU budget is separate from the training
machine.

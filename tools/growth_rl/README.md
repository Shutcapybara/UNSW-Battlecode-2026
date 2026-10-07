# growth_rl PPO

`tools/growth_rl/ppo.py` adds on-policy PPO fine-tuning to the existing growth policy runtime. It uses the same v4
legal-view features, per-dragon memory, F/R/B/L walk and sprint actions, split actions, structural split mask, and
command decoder as `bot_main.py`. The actor runs against a frozen snapshot for each update; a frozen copy of the
starting policy is the KL anchor. Each learner-side decision receives the terminal team result (+1 win, -1 loss,
0 draw), and the critic learns that return from the same local observation.

Start from a neural AWR policy artifact for useful experiments:

```sh
.venv/bin/python -m tools.growth_rl ppo \
  --init-policy PATH/TO/growth_awr/policy.json \
  --maps default.map,devil.map \
  --out build/growth_rl/ppo/run --updates 6
```

For callback and checkpoint plumbing only, use `--allow-random-init`; random-start match results do not measure bot
strength. Each update writes `policy.json`, `checkpoint.pt`, an update record, and a deployable `bot/` package.
Multi-update runs start a fresh process per update to bound the engine's WASM memory growth. Training maps must be
under `maps/live/`; the frozen Autarky, Maze, and Trauma holdouts are refused.

The exported neural policy loads through the existing `Policy` class and package runner. Export checks numerical
logits and masked action selection against the deploy runtime. Use the existing paired pool/generalization evaluator
before treating an artifact as an improvement. The repository does not include a pretrained `growth_awr` artifact;
produce one from replay data before fine-tuning, since random-start runs only validate plumbing. This first PPO
implementation uses terminal reward and a local critic; it does not implement P-7's replay-derived potential shaping
or a multi-opponent league. The separate
`tools/learn/ppo.py` file is the encoder-v1 P-7 architecture smoke and still emits direct moves; this `growth_rl`
entry point is the end-to-end deploy-wrapper path.

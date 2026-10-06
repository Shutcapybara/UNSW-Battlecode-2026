# Kenma17 — combined learned direction prior

Parent: kenma-16-lossless-model-text, strategy equivalent to03. Replace the search's first-step prior with Hinata's existing A5 development fold0, explicitly truncated to400 rounds. Inputs:1193 encoder-v1 values,270 HB values in verified parent binding order, and three parent HB probabilities rounded as the training exporter (six decimal places then float32). All118 HB side-file hashes match the training manifest; encoder allowlist order matches the C++ twin. Four classes F/R/B/L; search normalizes F/R/L and leaves reverse at the parent's zero prior. Weight1.0 unchanged. Parent fallback is logged explicitly. No new fit or map identity inputs.

The combined prior requires the original HB model as an input. Kenma16's lossless text encoding makes both models fit in4MiB. Original pocket-rescue, donor, slot-reserve, path-scoring and split logic remain; no orbit or corridor caution.

Model provenance: existing A5-u model_f0.txt reconstructed from verified archive parts; SHA6695befe886641235869dfea42d51f42816dec17eb621b037963f230d23b899b. This is a development-fold model, not a full-data fit. Pooled five-fold A5-400 offline accuracy72.67% is a source result, not a playing-strength claim for this snapshot.

Status: rejected at46–56/102. Full runtime feature/prediction parity and exact-source sandbox passed. Full102 replay fallback audit passed. Reserved seeds11–13/new maps untouched. Generator tools/kenma/prepare_stacked.py; evidence main build/kenma/stacked-prior/.

Actual initial archive4,083,138 bytes (cap4,194,304). Runtime1f11fcbb25ebd6a0f75d9dd47804e033800826dd6a83939e94f60d7cadff6961. End-to-end check covers2,759 turns from40 processes across four retained replays: all4,044,694 feature values agree between the live helper path and Python encoder/canonical parent HB exporter; all2,759 argmax decisions agree with LightGBM, max probability error2.61e-8. Includes newborn histories and recorded split/move actions. tools/kenma/verify_stacked.py; output stacked-prior/runtime-parity.json. This is integration evidence, not playing strength. Full102-game comparison will retain logs/replays for fallback auditing.

Deployment PASS: four Schooltime/UNSW games, both seats,seed1; max13,525,820 points including first turns (first-turn max13,151,074), zero errors; archived source4,083,138 bytes. Output main build/kenma/deploy/kenma-17-stacked-direction-prior/summary.json. Full native run k17-v-carthage-s123 retains all replays; use tools/kenma/audit_replay_logs.py with marker kenma_stacked_fallback and --require-complete --fail-if-present after completion. No playing-strength claim before the full score.

Full Carthage screen completed **46–56/102**, zero errors; rejected against03 at58–44. Full102-replay fallback audit found zero kenma_stacked_fallback markers, so this regression is not explained by fallback inference. Output k17-v-carthage-s123/score.json and replay-log-audit.json. All102 retained replays read and reconstructed;8 queens survive (6 Schooltime,1 Default,1 Stripes). Evidence k17-final-diagnostics.json.

| Map | Wins | Losses |
|---|---:|---:|
| live/schooltime | 6 | 0 |
| live/portals | 2 | 4 |
| live/slithery_fight | 0 | 6 |
| live/queen_of_spades | 1 | 5 |
| live/default | 4 | 2 |
| live/trophy | 4 | 2 |
| live/dilemma | 2 | 4 |
| live/autarky | 4 | 2 |
| live/devil | 0 | 6 |
| live/trauma | 2 | 4 |
| live/australia | 2 | 4 |
| live/islands | 2 | 4 |
| live/unsw | 3 | 3 |
| live/maze | 2 | 4 |
| live/weakhold | 3 | 3 |
| live/stripes | 6 | 0 |
| live/tower_defense | 3 | 3 |

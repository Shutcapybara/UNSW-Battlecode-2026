# G1 CUDA and batched-engine groundwork on unswbc 1.2.5

Date: 2026-10-03. Host: director's RTX 3060 Ti machine.

## CUDA smoke

The shared virtual environment contains `unswbc 1.2.5` and PyTorch
`2.14.1+cu130`, with CUDA runtime 13.0. Outside the restricted execution
sandbox, PyTorch detects the NVIDIA GeForce RTX 3060 Ti and completes a
64×64 CUDA matrix multiplication correctly (sum 262144). `nvidia-smi` reports
driver 580.178.04, CUDA 13.0, and 8192 MiB of GPU memory.

The restricted sandbox hides NVIDIA device access: there, `nvidia-smi` cannot
communicate with the driver and `torch.cuda.is_available()` returns false.
The same checks succeed with approved host execution
(`sandbox_permissions=require_escalated`). No driver changes were made.

## Implemented wrapper

`tools/antioch/rl/batched_engine_bench.py` runs independent official in-process
engines with one shared PyTorch inference service. Engine processes send actor
features through pipes; the service batches requests across games and returns
actions to the waiting callbacks. A thread backend is also available. Spawned
CPU workers do not inherit the CUDA context. CPU affinity is limited to at most
eight CPUs, including the inference service; environment count can exceed eight
to keep inference batches populated while callbacks wait.

`--encoder hq8` uses the new 36-field H-Q8-v1 Python encoder on actual callback
observations. Each dragon has separate memory initialized from the official
`bot_spawn` callback and reset each game. This is the conservative observable
subset described in `tools/antioch/rl/hq8_schema.md`. The workload emits MOVE
actions only and therefore does not exercise split-history updates.

The inference workload is a seeded, **untrained** MLP with two hidden layers of
128 units: 32→128→128→4 for the basic probe or 36→128→128→4 for H-Q8. This measures
environment/inference plumbing, not game strength, an expert policy, a trained
network, or a production training loop. Actor observations are encoded during
the run; they are not cached feature tensors. The move mask only excludes
observed occupied destination cells and is not a complete legal-action model.

## Measurements so far

The GPU inference-only smoke command was:

```sh
.venv/bin/python tools/antioch/rl/batched_engine_bench.py \
  --device cuda --inference-only --seconds 1 \
  --output build/antioch/rl/cuda-inference-smoke-1.2.5.json
```

It included CPU→GPU input transfer, inference, and GPU→CPU output transfer.
Each batch-size setting ran for one second, on the 32-feature probe model.

| Batch size | Decisions/s |
|---|---:|
| 1 | 4,790 |
| 8 | 39,848 |
| 32 | 149,301 |
| 128 | 594,815 |
| 512 | 2,005,892 |

These are inference-only rates, **not engine throughput**. One complete match
also passed through the H-Q8 process backend and real CUDA inference: 1,041
callbacks, no engine or service errors. Reproduction:

```sh
.venv/bin/python tools/antioch/rl/batched_engine_bench.py \
  --device cuda --encoder hq8 --backend processes --workers 1 \
  --seconds 0.2 --maps default \
  --output build/antioch/rl/batched-engine-hq8-process-cuda-smoke-1.2.5.json
```

`--seconds` stops launching new games; current games finish before the rate is
computed, and their decisions and elapsed time are included. This short smoke
finished in 2.374 seconds. It establishes callback communication correctness,
not sustained performance. Engine compilation and initial model warmup are
excluded from the reported steady-state interval.

## Sustained G1 result

After the Carthage comparison released the CPU, the bounded sustained command
ran with approved host access for CUDA:

```sh
.venv/bin/python tools/antioch/rl/batched_engine_bench.py \
  --device cuda --encoder hq8 --backend processes --workers 8 \
  --seconds 60 --batch-size 8 --wait-ms 0.25 --cpu-limit 8 \
  --output build/antioch/rl/batched-engine-hq8-cuda-8-workers-1.2.5.json
```

Measured result:

| Field | Result |
|---|---:|
| Elapsed | 62.57 s |
| Actual engine callback decisions | 497,642 |
| Throughput | 7,953 decisions/s; 28,630,161/hour |
| CPU use | 3.05 average cores; affinity limited to CPUs 0–7 |
| Games | 698 across default, trophy, big_empty, portals, trauma and schooltime |
| Mean inference batch | 5.17 (maximum 8; wait 0.25 ms) |
| Engine / service errors | 0 |

This clears G1's ≥20,000,000 actor-decisions/hour threshold for this workload.
The actions come from an untrained seeded MLP, and the encoder is the
conservative H-Q8-v1 subset. It measures full-engine callback and batched
inference throughput, not policy quality, a production learner, complete
H-Q8 deployment readiness, or the training loop. Compile and initial model
warm-up were excluded. Raw output:
`build/antioch/rl/batched-engine-hq8-cuda-8-workers-1.2.5.json`.

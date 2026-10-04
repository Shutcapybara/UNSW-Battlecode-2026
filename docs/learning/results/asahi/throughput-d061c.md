# In-loop self-play throughput on the Mac (D-061 §C, P-7 entry measurement)

Asahi, 4 Oct 2026 23:45Z. Job 179 (`tools/asahi/throughput.py --workers 8 --seconds 300`), raw: `throughput-d061c.json`.
Engine: official wasm engine in-process (`unswbc 1.2.3` in the repo `.venv`, engine hash 26e68680…), 17 live maps,
random seeds. Encoder: `tools/learn` encode v1 (legal observation, per-dragon). Network: untrained A10-shaped CNN
(conv3×3 C→32, conv3×3 32→32, linear →64 →4), numpy float32, batch 1 per decision. 8 worker processes, nice 10.

| mode | decisions | wall s | decisions / h (8 workers) | µs / decision-core (busy) | engine + glue | encoder | network | games, mean rounds |
|---|---|---|---|---|---|---|---|---|
| engine (keep facing) | 2,024,648 | 20.7 | 3.5×10⁸ | 73.8 | 73.8 | — | — | 40,000, 10.4 |
| + encoder | 2,024,648 | 37.1 | 2.0×10⁸ | 139.0 | 78.4 | 60.6 | — | 40,000, 10.4 |
| + untrained network | 16,002,916 | 304.1 | **1.89×10⁸** | 150.9 | 25.2 | 58.9 | 66.8 | 18,371, 188.7 |

- **Entry bar 1×10⁷ decisions per hour: passed by a factor of about 19** (net mode, wall-clock, process start-up
  included: 0.7 % of worker time). Replicates: jobs 177 and 178 (net mode, without process recycling) gave
  1.91×10⁸ and 1.88×10⁸.
- The trivial-policy games last about 10 rounds, so their 74 µs per decision is mostly per-game start-up
  (instantiating the wasm module); in the long games of the network mode the engine and glue cost 25 µs per decision.
  The 74 µs engine floor agrees with Sugawara's cloud figure (73 µs, D-063 §D); our encoder (59–61 µs) and network
  (67 µs) differ from his single-core figures (111–140 µs, 22–40 µs) in the expected directions for an M-series core
  and an unoptimised im2col forward pass.
- **Engineering finding for any rollout loop:** a process that runs many games leaks address space through
  wasmtime stores (`mmap failed to reserve 0x104000000 bytes`, ENOMEM) even with `gc.collect()` every 4 games
  (jobs 176–178: all 8 workers failed in the short-game modes; the long-game mode survived about 2,250 games per
  worker). Recycling processes (here at most 500 games or 30 s per process) removes it. The earlier job 172 failure
  ("ctypes objects containing pointers cannot be pickled") was this error, which carries ctypes pointers and could not
  be returned from a worker; workers now return plain numbers and tracebacks as text.
- Not measured: learner updates, rollout storage, a privileged critic, batched inference across dragons, games with
  many dragons (here 4.6 decisions per round on average, an untrained policy). The figure is the rollout ceiling of
  the actor side only.

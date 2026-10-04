# H-Q8 v1 encoder contract

`hq8_features.py` and `hq8_features.hpp` encode the same 36 signed 32-bit integer features in `NAMES` order. They accept only each dragon's initialization (id, team, dimensions, unit limit), its 7×7 protocol block and its own split actions. Measured bot snapshots are unchanged. This is a conservative first implementation of the H-Q8 proposal, with explicit observability limits.

`-1` means unknown, not dead, absent, or zero. A queen is `alive=1` only when its head is visible in the current observation. A previous sighting remains in last position and age; silence never becomes death. The queen is id 0 for team A and 1 for team B. Distances are torus Manhattan distances. The round horizon is 500.

Mode is 3 (queen race) when both queen heads are currently visible, otherwise unknown. Turtle/hunt/longest race require confirmed mortality evidence that this protocol does not provide. RL map likelihood and pocket map are unknown because no deployed map classifier was specified. Sonar remains undecoded (`sonar_decoded=0`); interpreting another bot's message bits as queen telemetry would be unsafe without a shared message schema.

Only an actor that is itself the queen supplies exact queen length and its own split age. Split age is elapsed round count from its last emitted split; before any split it is elapsed time since game start. Visible segments of other dragons are lower bounds, never exact lengths. Queen length margin remains unknown; queen rank is a visible lower bound where the actor is the queen (`own_rank_exact=0`). Enemy reach counts use visible length lower bounds in `distance ≤ 1 + ceil(visible_length/4)` and are explicitly marked inexact. Crowding/escort counts exclude the queen itself and include only visible heads.

Reachable free cells are counted within five ordinary grid steps, exclude the starting head and all currently occupied cells, and stop at walls, portal edges and the boundary of the visible window. A portal or window boundary encountered before depth five sets the censor flag. This measures static observed space, not dynamic body-tail motion or unseen portal exits. Bed and pearl distances are minima over visible tiles. Pearl origin is unknown (corpse/bed provenance is absent from the protocol). Other-queen split age and exact teamwide rank are unavailable.

`hq8_parity.py` reconstructs protocol observations using the existing replay reconstruction path, runs stateful Python and C++ encoders over all turns in each chosen replay/side, then selects a deterministic distributed sample. It compares packed little-endian int32 bytes, not floating-point tolerances. A passing check demonstrates encoder parity for this declared contract; it does not validate omitted latent inference features or deployment integration. Full G2 readiness still needs a shared sonar/state-inference contract and integration with the selected learned bot.

## Measured parity on 3 October 2026

Command (low CPU priority):

```sh
nice -n 10 .venv/bin/python tools/antioch/rl/hq8_parity.py \
  --replay-dir build/carthage/runs/carthage-05-free-sprint/pool/replays \
  --turns 1000 --out build/antioch/rl/hq8-parity-1000-1.2.5.json
```

The check passed with **zero byte mismatches across 146,912 actor turns**, from seed-1 Carthage-05 pool replays on Default, Portals, Trauma, Schooltime, Queen of Spades, Autarky, Slithery Fight and Dilemma, observing both teams. The deterministic 1,000-turn sample includes 282 queen turns, 331 turns at round 250 or later, 187 after an observed own-queen split, 81 with a stale own-queen position and 66 with a visible enemy queen. All 36 features are compared. The sample byte digest is `abb0320d6a31114437c8ec8d96d9a8041b38312a19a1e75d8755b97d1de20870`.

An independent replay reconstruction pass on those eight files recorded 144,957 successful movement checks and 16 successful terminal standings checks, with no bad or mismatch counters (`build/antioch/rl/hq8-reconstruction-checks-1.2.5.json`). Local `unswbc` was 1.2.5. Replay parsing required installing `pycapnp==2.2.4` into the project virtual environment; no gameplay bot snapshot was modified. Source/replay hashes are recorded in the generated parity report. This establishes parity for the declared observable subset; the unresolved proposal features above remain open.

### Actual-controller observation trace on the local pilot

The separate diagnostic probe `tools/antioch/rl/hq8_runtime_probe.py` copied
`carthage-05-free-sprint` into `build/`, emitted the 36 H-Q8 values from the
actual `hb1::block_from(ct, game)` controller observation, and compared them
with replay reconstruction from the probe's same game. Five frozen pilot
fixtures (game IDs 1, 22, 41, 62 and 81) span all five pilot maps and both A/B
seats. All **46,147 actor turns matched exactly**, with zero feature
mismatches. The base source fingerprint matched the local pilot manifest
(`7df05a3f40b011fa52f700c789ddf30414da08ab50d6c36964ef8cc223f9d45f`).

This specifically checks the runtime observation adapter used by Carthage05.
The diagnostic bot adds logging and encoder work, so the games are parity
fixtures and provide no strategy or performance evidence. Detailed source and
replay hashes are in `build/antioch/rl/hq8-runtime-probe-v1/report.json`.

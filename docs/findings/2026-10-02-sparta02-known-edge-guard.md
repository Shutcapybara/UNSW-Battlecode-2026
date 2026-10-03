# Sparta 02 — known-edge queen guard

Sparta 02 is an incremental child of Sparta 01. The first Sparta 01 screen had
16 wall deaths among 40 own-queen games. Its simulator maps an unknown edge to
the neighboring cell for optimistic route planning, so a simulated move could
be scored as safe even though the engine's unseen edge might be blocked.

## Change

`SimResult` now records whether any simulated step crossed an unknown edge.
The original queen assigns that route a veto score, alongside simulated
deaths, head-on trades, and visible enemy-reachable cells. Other dragons and
all non-queen path scoring keep Sparta 01 behavior. The point is to stop the
queen from volunteering into unmapped terrain while leaving the rest of the
team free to explore and report it.

## Evaluation

The fixed-seed screen used Devil, Queen of Spades, Schooltime, and Trauma,
both seats, seeds 1–3, one worker. The paired runner recorded source/map
hashes and kept output under `build/sparta02-paired-screen-20261002/`.

| Opponent | Result | Reached r490 | Sparta queen alive@490 | Sparta queen deaths |
|---|---:|---:|---:|---|
| Sparta 01 | 12–12 | 10/24 | 0/10 | 14 head-on, 7 wall, 2 body, 1 no death event |
| Carthage 05 | 9–15 | 10/24 | 0/10 | 16 wall, 4 head-on, 2 body, 2 no death event |

There were zero runner errors. In the direct Sparta 02–Sparta 01 games, the
two versions each had zero queens alive@490 among ten reached games and the
same cause counts. The edge veto did not change the observed result in this
screen. Carthage 05's queen also survived 0/10 reached games against Sparta
02; Sparta killed its queen in 16 games, all by head-on, while Sparta's own
queen died to a wall in 16 games. The strategy's aggressive hunt is active,
but the protection side remains inadequate.

Verdict: **do not carry the unknown-edge veto forward as an improvement**.
Keep Sparta 02 as a diagnostic control. The source-level rationale was
plausible, but these paired outcomes and queen measurements do not support a
gain. This focused screen is not frontier evidence.

Reproduce with:

```sh
python3 tools/sparta/paired_screen.py \
  --candidate sparta-02-known-edge-guard \
  --opponents sparta-01-queen-priority carthage-05-free-sprint \
  --maps devil queen_of_spades schooltime trauma --seeds 1,2,3 \
  --output build/sparta02-paired-screen-20261002
```

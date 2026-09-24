# ouroboros-v12-core — v10, modular, with doctrine and the ladder option

- **Line:** Ouroboros (Claude). **Base:** `ouroboros-v10-beacon`.
- **Borrowed:** the decision ladder of `hunter-v20-portal-scouts` (user line),
  ported to Python in `ladder.py` (attack → split → owned pearl → explore).
- **Hypothesis (P1, macro spec §13):** the 1,800-line v10 can be split into
  ~300-line modules and gain a map-class doctrine layer and new options with
  **neutral defaults**, without changing a single action.
- **Verdict:** *infrastructure, not a competitor.* Action-stream equivalent to
  v10 (16/16). Every new knob is off by default; `ouroboros-v13-ladder` is the
  version that turns the compact doctrine on.

## Layout (one shared namespace)

`main.py` `exec()`s the modules in order into its own globals, so hot
functions keep plain global lookups (same speed as the single file) while
each file can be read or edited alone (~150–400 lines each).

| File | Contents |
|---|---|
| `defaults.py` | every tunable: `P`, per-role `RP`, `DOCTRINE` (per map class), `params.py` loading |
| `world.py` | IO, persistent world model, geometry, `sense()`, zone heat, pruning |
| `comms.py` | sonar packet catalogue, `hear()`, relay queue, sightings, 4-ray scheduler |
| `safety.py` | threat map, `head_risk`, exact `simulate`, `flood`, `doom`, tunnels, fallback |
| `targets.py` | the goal field: `choose_target`, zone waypoints, reverse distances |
| `roles.py` | production (`split_value`, team size), child role mix, crown election / feeding, orphan roles |
| `evaluate.py` | candidate generation and the evaluation function (`decide`) |
| `ladder.py` | hunter-v20's priority ladder as an option set (off unless `ladder=1`) |
| `main.py` | loader, turn loop, act (`take_turn`, `boot_turn`, `commit_path`) |

## New knobs (all neutral by default)

| Key | Default | Meaning |
|---|---|---|
| `DOCTRINE["compact"/"open"]` | `{}` | overrides applied once the map size is known; class = compact if ≤ `compact_max_cells` (625) tiles. In `params.py`: `"compact:ladder": 1` |
| `ladder` | 0 | non-crown, non-feeding dragons decide by the ladder |
| `ladder_until` | 500 | … before this round |
| `ladder_attack_units` | 3 | trade up into a *longer* enemy head only with this many units |
| `ladder_split_min` | 4 | split whenever at least this long |
| `ladder_safety` | 1 | veto a ladder step: 1 = certain death, 2 = also a pocket smaller than len + `space_slack` |
| `ladder_risk_max` | 99 | veto a ladder step whose `head_risk` exceeds this (off) |
| `w_eat_prod` | 0 | extra value per pearl eaten before `split_stop` (λ_unit share of a pearl) |
| `orphan_role` | 0 | newborn with no hand-off: 0 = hunter (v10), 1 = draw from the doctrine mix |

## Findings made while building it

- **Hand-off rays miss about half the newborns.** A ray fired into our own
  neck exits the tail *continuing in the same direction*; it reaches the child
  only if the last three segments were collinear. On an arena game 8 of 15
  children never heard their role and defaulted to hunter. Making those
  orphans gatherers (`orphan_role=1`) *lost* 11 net on compact maps (36–54 →
  25–65 against hunter-v20/v14/fry-v14), so the accidental hunter share is
  load-bearing. Kept as a knob; not changed.
- **v10's gatherers pass up adjacent pearls.** Eval breakdown
  (`tools/ouroboros/explain.py`): 40 of 100 decisions with a pearl within
  3 steps targeted a predicted spawn or an enemy sighting instead; the
  pearl step then lost to crowd / ally-head / risk penalties (e.g. pearl
  +1.0, goal +1.2 against head risk −2.4, ally head −2.5, crowd −1.0).
- Single-knob sweeps of the evaluator on compact maps (spawn window, goal
  weight, crowd, spread, risk, split gates, production bonus) all stayed
  within ±5 of 36–54 on 90 games (noise: σ ≈ 4.6). The evaluator is at a
  local optimum on compact maps; the ladder is a structural change (+25 net,
  see v13).

## Judge packaging

The judge compiles every `*.py` to `*.pyc` and deletes the sources, so
`main.py` loads each module from source when present and otherwise
unmarshals its `.pyc`. (Found by `unswbc run --sandbox`: the first build
exited on turn 0.)

## Results

- **Equivalence:** `tools/ouroboros/equiv.py ouroboros-v10-beacon ouroboros-v12-core`:
  16/16 identical action streams (8 maps × both sides; fry-v14 and kraken-v04),
  instruction counts excluded.
- Behaviour is v10's, so v10's cycle-0 baseline applies (P0, gauntlet × 30 maps,
  both sides): compact 65–1–54, open 115–5.

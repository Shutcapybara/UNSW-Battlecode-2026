# Leviathan cycle 1 — convergence handoff

Scope: GPT's core line, following the Cycle 0 HANDOFF and ACTIVE directives.
Claude remains the unifier. This work does not update ACTIVE, shared files, other
lines, or the HANDOFF component table. No online submission is made.

## Decision and evidence

**Carry leviathan-v09-arrival as the single Leviathan candidate.** It passes
the declared gate: G+V 244–86 versus 229–99–2 for v08; compact 93–57 versus
79–69–2; open 151–29 versus 150–30. There are 32 improved outcomes and 17
regressions. The largest opponent regression is −2 net W–L versus Ouroboros,
within the −3 limit. V08 is an equivalent reference baseline, not a second
competitive submission.

Both versions pass four judge games each. V09's per-game p99 range is
28.8–48.9M and peak range 41.5–67.1M, within the required limits. All 29
regression tests pass. Full movement/split/sonar equivalence: 18 v08/reference
fixtures and six v09-neutral/v08 fixtures. Final native and judge matrices have
no runner errors, replay-analysis discrepancies or recorded timeouts.

The source bundle is `build/leviathan/cycle1-final/leviathan-v09-arrival.zip`.
The bot README preserves the complete class/side/opponent tables and ablations;
`build/leviathan/cycle1-final/flips.json` names every changed fixture. Raw games
remain in the six G/V/J run directories. Working-candidate selection does not
change ACTIVE or claim the inherited protocol/doctrine gaps below are fixed.

Results and the final recommendation are recorded in the bot READMEs and RESULTS.md.
The experiment is frozen before inspecting the transpose/flip validation set;
those maps must not subsequently be described as untouched hold-outs.

## Why change the working base

The current gauntlet establishes v07's weakness (0–22 vs Ouroboros v10,
4–18 vs Hunter v14). Building another independent crown or survival subsystem
would maintain an implementation of components already selected for convergence.
V08 therefore adopts the full Ouroboros v10 evaluator, explicitly credited in its
README. Its only refactor moves the parameter table into config.py. V07 and every
older bot remain available. The existing v07 regression suite remains intact.

V09 tests one destination feature tied to V's material/control term: treat a
bed as a pearl target when its countdown is strictly less than the walking route
length. This matches the hunter arrival predicate without copying its ladder.
The first step occurs now, so distance d means arrival in round now+d−1.
Predictions older than four rounds decay and then expire. The normal ownership,
threat and route-distance costs still apply. The option is limited to maps of
at most 625 cells in the tested profile.

A separate ablation corrects inherited optimistic body simulation: a remembered
pearl is a target but only a pearl observed this turn contributes immediate
growth. Bed predictions never contribute simulated growth. The inherited
candidate length cap already prevents remembered pearls funding otherwise
unaffordable sprints; this correction concerns material and body prediction.

## Measured mechanism on the 30-game compact screen

The matched set is five compact maps, both sides, against Hunter v14, Hunter
v20 and Kraken v04. Arrival alone changes 15–14–1 to 22–8 (eight improvements,
one regression). Average opening [0,30) pearls rise 16.23→23.07, splits
6.27→8.63, and ending units 6.27→8.40. Opponent pearl intake is nearly flat
(18.37→18.17), supporting improved collection rather than simply weaker
opposition. Deaths rise slightly, 1.80→2.03; this is an economic improvement,
not evidence of safer tactics.

Confirmed-only simulation alone preserves the 15–14–1 outcomes, although three
of the thirty action streams change. Arrival with confirmation preserves the
arrival-only 22–8 outcomes. The full combined G score is 85–25 versus 78–31–1;
compact 35–15 versus 26–23–1, open 50–10 versus 52–8. The two open regressions
are default/A versus Hunter v14 and queen_of_spades/B versus Kraken v04.
Arrival is disabled on those maps, so these regressions belong to the confirmed
simulation change. Keep correctness and targeting evidence separate. Both losses reach round 500:
default's longest falls 22→7 (the opponent also has 7 and wins total length),
and queen_of_spades' longest falls 29→13 against the opponent's 14. Their first
action divergences are round 90 and 64 respectively, after identical opening
metrics. This identifies late conversion losses; it does not prove a general
benefit to optimistic simulation.

## Component interfaces for the unifier

| Component | Location | Inputs / outputs |
|---|---|---|
| Parameter and role tables | `bots/leviathan-v09-arrival/config.py` | P and RP; snapshot overrides in params.py |
| Pearl arrival valuation | `bots/leviathan-v09-arrival/pearl_model.py:arrival_value` | round, walking ETA, due round, length-valued reward, TTL → target reward |
| Pearl observation | `main.py:sense` | visible tiles → remembered pearls, seen stamps, spawn_at |
| Target consumer | `main.py:choose_target` | bounded route BFS → target; invokes arrival_value only when enabled |
| Confirmed growth consumer | `main.py:simulate` | candidate route and body → collision, length, eaten pearls, resulting body |
| Terrain / portals | `main.py:dest`, `learn`, `DC_reset` | inherited v10 cache and edge model |
| Safety / threats | `main.py:simulate`, `flood`, `doom`, `head_risk` | inherited candidate simulation and filters |
| Production | `main.py:team_target`, `split_value`, `child_role` | inherited population target, split candidate and role assignment |
| Crown / feeding | `main.py:take_turn` | inherited election, demotion, feeding and emergency transfer |
| Communication | `main.py:hear`, `send_sonars` | inherited checksum packets, role hand-off and relays |
| Measurement | `tools/leviathan/lab.py`, `cycle_report.py`, `converge.py` | immutable snapshots → standard ledger, opening autopsy, paired flips |

The new component is a pure function and can be copied into another evaluator
without copying the bot. The rest of the core intentionally retains v10 function
boundaries for straightforward comparisons; it has not been represented as a
finished modular architecture.

## Parameters added by this experiment

| Key | Neutral | Tested | Range / consumer |
|---|---:|---:|---|
| `pearl.prepos` | 0 | 1 | Boolean; choose_target arrival valuation |
| `pearl.compact_only` | 1 | 1 | Boolean; use the feature only for area ≤625 |
| `pearl.prediction_ttl` | 4 | 4 | 0–30 rounds; arrival_value overdue decay |
| `pearl.confirmed_only` | 0 | 1 | Boolean; simulate requires current seen stamp for growth |

Neutral config.py defaults preserve v08 behavior. params.py is the explicit
selected experiment; the lab applies overrides only to private source snapshots.
No parameter-only bot folders are created. Existing v10 parameter names remain
unchanged so its parameter points transfer exactly.

## Known convergence gaps inherited from the base

These are not claimed fixed by a pearl-target experiment:

- Self/enemy sonar packets have 12-bit IDs and portal packets have 8-bit IDs.
  The mandated 16-bit identity/correctable portal work is still required before
  claiming full HANDOFF compliance. Direct observations cannot repair every
  gossip-created portal identity in this base.
- The full map-class × phase doctrine table, option masks, explicit scout quota,
  chase cap and parity pricing are not implemented. Existing v10 knobs cover
  production/role mixes/crown/feeding but cannot reproduce every hunter priority.
- The inherited emergency split may transfer more than two segments to save a
  crown. Voluntary production creates two-segment children.
- Feeding intentionally emits no action, recorded by the engine as an invalid
  action death. Health reports must distinguish these from malformed moves,
  unaffordable sprints and judge timeouts; never claim zero invalid deaths.
- Bed availability is uncertain: a spawn attempt can fail when occupied. A
  destination prediction is not a guarantee of future material.
- No new sonar packet is added; no claim is made that inherited packet kinds
  have all passed consumer ablations.

The next unifier should merge or reject the pearl component on the paired data,
then integrate independently validated packet, doctrine and safety components.
A local experimental recommendation is not an ACTIVE promotion.

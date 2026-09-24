# hydra-v11-macro

**Line:** Hydra (GLM) · **Base:** fresh implementation (not a hunter.cpp fork).
Borrowed from `leviathan-v07-local-cache`: raw single-write I/O discipline and
the invalidated terrain graph cache (`world.py`), credited per lineage rules.

**The one hypothesis** (`docs/macro-spec.md`, phases P0-P2): a single linear
evaluation in length units over exactly-simulated candidates beats the
hunter-v03 priority ladder the hydra line inherited (v06-v10), because the
ladder self-harms (31% of deaths) and cannot price survival against income.

**Verdict up front: not promoted.** P0 gate passed (exact-sim survival +
CPU). P1 borderline-failed (7 combined wins vs the fry+ouroboros gate, needs
8). P2 failed (8-14 vs fry-v14, needs 16-10). Kept as the hydra working base:
the architecture is sound and cheap, the remaining gaps are measured and
diagnosed below.

## What it is

Per-turn: observe (terrain edges, portals, pearls, bed countdowns, bodies) →
threat map (BFS per visible enemy head, p=.75/.35/.15 by sprint depth, bodies
block) → one bounded target BFS per turn ("compass": live + remembered pearls,
predicted bed spawns, frontier, ally-deconflicted) → candidates (4 single
steps, gated 2-3 step sprints, head-to-head trades, SPLIT 2) each exactly
simulated (kelp/self/body/head-to-head, payment pops tail, mid-path pearls) →
linear score in segment units → argmax → one stdout write.

Doctrine is a parameter table (`weights.py`), two merged dicts by map class
(compact ≤ 625 tiles / open), overridable via `params.py`
(`OVERRIDES = {...}`). Production schedule: `target(t) = t0 + slope·t`, capped
(min(cap, limit, n/3 on tiny maps)); splits score `split·(split_base +
urgency)` so breeding beats foraging below target; `split_stop 380`. Crown
(P4, local election without radio): from `crown_start 260` the longest dragon
stops splitting and trading, farms with `crown_food_mult 1.5` greed and
`crown_risk_mult 3` death pricing; from `crown_kill_round 380` units strike
the enemy's big dragons. Economy: bed countdowns → predicted spawn rounds
(re-armed on the mean gap when expired unseen), corpse-pearl tracking,
contested-pearl deconfliction against visible allies.

## Engineering notes (engine facts, read from `unswbc/engine/src/`)

- A plain step pushes head and pops tail: **length only changes with a pearl
  (+1) or a sprint payment (-1)**. Getting this wrong corrupted the body
  model and caused neck-collision deaths (fixed; was the top self-harm source).
- Moving into ANY current body segment (including the neck) kills the mover;
  head-to-head kills both; death drops a pearl on every 2nd segment.
- SPLIT at the unit limit kills the splitter (gated). Illegal actions kill.
- Bed countdown k shown post-tick means a spawn attempt at round r+k.
- The sonar "back-ray hand-off" works because the ray wraps the torus: a
  straight-bodied parent's forward ray reaches the newborn's head (the old
  tail tip) before its own neck. Relevant for P3.

## Measurement tools

`tools/autopsy.py`, `tools/hydra_replay.py` (population/pearl/split series),
and NEW `tools/hydra_deathcontext.py`: death causes plus the action/indicator
trail into each death, decoded from the packed replay. Also fixed a real bug
in `tools/hydra_replay.py`: the capnp `text()` reader misparsed byte-list
pointers, which had silently broken map-text parsing (team attribution in
older workflows was luck).

## Results (2026-09-25, native, 11 maps, both sides, `--timeout 1200`)

**Gauntlet fixture** (`build/v11-fixture`): **23-87**.

| Opponent | W-L |
|---|---|
| fry-v14 | 8-14 |
| hunter-v20 | 7-15 |
| kraken-v04 | 5-17 |
| hunter-v14 | 3-19 |
| ouroboros-v10 | 0-22 |

By class: compact **6-44**, open **17-43**. Loss modes: 38 compact
eliminations, 35 open length-tiebreaks, 8 open eliminations, 6 compact
length. Before the crown, the fry matchup was 7-15 with all-open games lost
on length; the crown flipped 2 and made stronghold/trauma sweeps (4-0).

Opening economy (arena vs fry, r24): pearls 55v34, splits 12v12, pop 10v10 —
the production schedule wins the early numbers war. Mid-game arena peak:
pearl ratio 1.75x at r80 (237v135).

Style metrics (replay-verified): self-harm ≈ 0 (0 self / 0 wall on big_empty;
1-6 wall on devil — see open bugs); deaths/game 97 on big_empty (88
head-to-heads are doctrine churn, not self-harm); the ≤130/g P1 bar passes.
The style bar "both win types present" passes only with the crown ON.

CPU (judge-priced sandbox, big_empty): p50 32.4M, **p99 43.0M**, max 55.5M —
P0 gate (<60M p99) passed with headroom.

## The diagnosis (measured, one mechanism per item)

1. **Birth conversion is the economic bottleneck**: 5.0 pearls per split vs
   fry-v14's 2.6. My dragons re-breed too slowly (travel time between pearls);
   fry's 64-unit density shortens travel and compounds. This is the compact
   elimination spiral: my opening wins, my churn rate cannot be sustained,
   deaths exceed births from r40, extinction. Candidate fix: planned
   multi-pearl harvest routes (the fry-v03 port from the backlog), not more
   weight tuning.
2. **Open maps are survivor accumulation**: fry's longest (33-38) and
   ouroboros's (51) both come from one protected dragon eating while the
   population sits at the unit limit. My crown reached 25-27 before crowning
   itself into an ouroboros herding pocket and dying to a panic trade.
   Crowning later is not the fix; not dying is — and that needs escorts,
   which need radio (P3).
3. **Local information cannot do feeding**: the "yield pearls to bigger
   allies" experiment failed because visible segment counts undercount real
   length badly on big maps. Feeding/right-of-way needs the P3 status
   channel (id, length, crown-flag) — the spec's reading is confirmed.
4. **Trades are doctrine, not self-harm**: head-to-heads on compact are how
   fry plays; matching fry's churn while out-birthing is the only way churn
   pays. Until (1) is fixed, my compact trades are unaffordable; consider
   ouroboros-style compact survival as the alternative doctrine.

## Open bugs

- ~6 wall deaths/game vs ouroboros on devil: trails show straight walks into
  map-border kelp. The terrain graph verified EXACT against the engine
  offline (dest() cross-checked over all cells; vision-fold mapping
  cross-checked against map truth), so the cause is elsewhere — suspected a
  vision-timing edge case. 6 deaths/game is not the main gap; left open.
- Panic (boxed, no candidates) still exists by construction in crowds; tier 1
  now trades an adjacent enemy head, which converts some to mutual kills.

## Iteration log (single changes, measured on arena/big_empty screens)

1. `length mispredict fix` — plain steps don't shrink length; arena hitSelf
   deaths 14 → 0.
2. `panic hardening` — boxed dragons trade an adjacent enemy head first.
3. `split pocket ban` (REVERTED) — banning splits with no free neighbour froze
   births on arena and lost both sides: churn wins compact, fry-style.
4. `trade discipline` — trade_min_len 4, open margin 3 + local parity gate.
5. `production-first` — split_base 0.6, open slope 0.5 cap 64, risk 6.0,
   trade_unit 4.0 → 1.5.
6. `crown v1` (bed_mult 2.0) — bed camping starved the crown: longest 16.
7. `crown v2` (bed 1.0, food 1.5, risk 3, start 260) — best config; longest
   25-27 on big_empty; +2 fixture wins, stronghold/trauma sweeps.
8. `crown spacing + compass 380` (REVERTED) — both made length/total worse.
9. `feeding right-of-way` (kept, inert) — failed for the reason in diagnosis 3.

## Next cycle (in priority order)

1. P2 economy: harvest-route planning (port fry-v03's planned multi-pearl
   routes); target the 5.0 → 2.6 pearls/birth gap. Gate: ≥16-10 vs fry.
2. P3 radio: status channel (id, length, crown-flag) → real crown election +
   feeding + escort. This is the pre-condition for open-map length wins
   against ouroboros-v10. Gate: length tiebreaks won ≥ 40%.
3. Wall-death bug hunt with the deathcontext tool.

# Von Neumann: aggression as an optimised component, not a stance

Lineage owner: GLM (Javert line). Started 2026-09-26. Mission, from the
strategy/execution brief: pick a sensible baseline given measured performance
and design simplicity, freeze everything not related to combat procedures,
iterate hard on combat strategy, refit the policy as evidence accumulates, and
decide whether **aggression is a valid optimisable component** of the policy —
explicitly not whether the bot can be made purely aggressive.

## 1. Baseline choice

**Baseline: `porthos-x04-policy`, copied byte-identically to
`bots/von_neumann-x01-frozen`** (SHA-256 manifest in
`tools/von_neumann/frozen.json`; 19 files, zero mismatches).

Why this baseline, given the alternatives:

| Candidate | Measured strength | Combat surface | Verdict |
|---|---|---|---|
| porthos-x04-policy | 182-game gauntlet **126–56** (+13 over its stream-verified MC-parity control); 24-game screen 19–5; top French-line skill posterior in the 60k-game replay model | `decision.py` policy P1 with explicit aggression parameters (`aggro_*`, `atk_margin`), combat/threat/hunt parameter sections isolated in `params.py`, `override.py` variant mechanism | **chosen** |
| monte_christo-v01-core | playing control, 4–2 head-to-head vs every French-line cell | combat tangled in the monolithic policy; no variant mechanism | rejected: design simplicity |
| javert-v01-game-relative | fresh reserve 10–2 vs MC 5–7 | Aramis contract, but its gain is the information layer, not combat; loses MC head-to-head 2–4 | rejected: weaker measured base, wrong lever |
| aramis-v01/v02, athos, dartegnan | known strength regressions | semantic but heavyweight | rejected |
| valjean (other session, in progress) | unmeasured at freeze time | promising Q-scale | rejected: not a measured version |

The porthos chassis is the only baseline that is simultaneously (a) the
strongest measured member of its ancestry, (b) parity-verified to the playing
control at the 182-game scale, and (c) already parameterised for combat, with
a **measured +13 gauntlet gain attributable to its early-saturation aggression
policy P1** — i.e. aggression is already a proven conditional lever there, and
the open question is its optimal conditioning.

## 2. Freeze discipline

Frozen from x01 (combat iteration must not touch): `world`, `protocol`,
`comms`, `radio`, `roles`, `swarm`, `density`, `tactics`, `targets`,
`executors`, `main`, `risk_features`, `diagnostics`, `intentions` (candidate
construction), and every non-combat parameter block (production, target
values, crown/feeding endgame, communication).

Iteration surface: `decision.py` combat branches (strike admission, threat
cost, aggression gate), combat/threat/hunt/aggression parameters, plus two new
default-off combat mechanisms in `von_neumann-x02-mech` (CM-1 length-balance
margin, CM-2 support-weighted trade gain; POLICY_VERSION 3, switches at 0
reproduce P1 exactly).

## 3. Evidence base carried in

From the 60k-game replay-statistics study (round-100 checkpoint, effect sizes
on final outcome): `initiated_h2h_fraction` **−0.172** and
`team_kills_per_round` **−0.194** (initiating contact is on average
associated with losing), while `length_volatility` +0.429,
`control_change` +1.250, `unit_change` +0.495, `pearls_per_dragon_round`
+0.416 (growth/expansion win). Porthos P1's +13 gauntlet shows one specific
conditioning of aggression (early + population-saturated + forager, pushing
toward enemy length density) is an exception. The study must therefore
separate *unconditional* aggression (expected bad) from *conditioned*
aggression (plausibly good) — matching the brief.

## 4. Harness

- Dev screen: `configs/von_neumann/screen.toml` — identical fixtures to the
  porthos parity screen (tew-v12 / hunter-v20 / ouroboros-v13 × Colosseum /
  devil / queen_of_spades / trauma × both sides, 24 games). Baseline record
  19–5 (porthos run `porthos-x04-policy_20260925224950114366`).
- Sweep driver: `tools/von_neumann/sweep.py` — override-only variants of x01,
  auto-generated `override.py`, sequential per lane, per-fixture pairing
  against the baseline record (deterministic engine).
- Mechanism master: `bots/von_neumann-x02-mech` (default-off CM-1/CM-2).
- Tests: `tests/test_von_neumann.py` (5 checks: P1 defaults, CM-1 direction +
  evidence gate, balance values, CM-2 bonus + cap, x01/x02 score parity).
- Reserve: `configs/von_neumann/reserve.toml` — two fresh combat-focused map
  families (`vn_reserve_corridor_clash` 26×26, `vn_reserve_open_field` 32×20)
  frozen before any outcome was read, vs four stylistically varied references
  (hunter-v20, ouroboros-v13, avery-v08, sinbad-v06), 16 games.
- Selection rule: `tools/von_neumann/selection_rule.json` — frozen before any
  outcome was read. Screen ≥21/24 advances; gauntlet ≥127 survives; promotion
  needs gauntlet + fresh-reserve (≥ x01's own reserve record + 1) + clean
  judge. Bounds arms (pacifist/berserk) are diagnostics, never candidates.

Harness validation: `von_neumann-x01-frozen` on the screen reproduced the
porthos-x04 record **24/24 identical** (winner side, round count, reason) —
the copy, config and deterministic pairing are exact.

An initial sweep-driver bug was caught by this discipline: the generated
`override.py` placed `OVERRIDE = {...}` inside a comment, so the first
"pacifist" arm silently ran the baseline (bit-identical games). The driver
now self-checks the generated file, and the invalidated run is recorded in
`tools/von_neumann/invalidated_runs.json`.

## 5. Experiment log

All arms: override-only variants of `von_neumann-x01-frozen` on the 24-game
dev screen (deterministic engine; per-fixture pairing against the baseline
record). Runner: `tools/von_neumann/sweep.py`; full tallies with per-fixture
rows in `tools/von_neumann/sweep_results.json`.

### Structural checks

| Check | Result |
|---|---|
| x01-frozen vs recorded porthos-x04 screen | **24/24 identical** fixtures (winner side, rounds, reason) — copy/config/pairing exact |
| x02-mech (P1+CM, switches off) vs x01 | **24/24 identical** fixtures incl. combat stats — the mechanism switches are exact no-ops when off |
| `tests/test_von_neumann.py` | 5 checks pass (P1 defaults, CM-1 direction + evidence gate, balance values, CM-2 bonus + cap, x01↔x02 score parity) |
| Trace diagnostic (`von_neumann-x01-trace`, hunter-v20 × Colosseum/trauma × both sides) | ~34k selections decoded from replay event logs: intentional strikes (`reason=strike`) **0**; h2h selections via gather/scout paths 33; prey chases 0; no-surviving-move fallbacks 445 (233 on trauma alone). **The explicit hunt/strike machinery almost never fires in baseline play; contact is created by economy movement, not by combat objectives.** |

### Bounds arms (diagnostics; never promotion candidates)

| Arm | Override | Screen | Reading |
|---|---|---|---|
| **pacifist** | `attack=0, v_hunt=0` | **14–10** (9 fixtures flip, 2 back) | removing strike admission + hunting costs 5 net games; deaths balloon (93.9→154.7 per game). **The combat machinery is load-bearing.** |
| **berserk** | `atk_margin=-99, atk_units=1` | **18–6** | trading at every contact is roughly neutral-vs-bad (−1), *not* catastrophic — strike opportunities are rare enough (trace) that unconditional permissiveness barely bites. |

### Parameter sweeps (single knobs, incumbent = frozen defaults 19–5)

28 override arms ran (`tools/von_neumann/sweep.py table` for the live table;
full per-fixture rows in `sweep_results.json`):

- **Exactly 19–5, mostly with zero fixture flips (16 arms)**: `margin-1`,
  `plong-06`, `push-0`, `push-4`, `hunt-100`, `huntlen-8`, `vhunt-2`,
  `preymin-10`, `atkunits-1`, `aggro-off` (aggro_relax+push both 0!),
  `relax-05`, `relax-25`, `sat-05`, `sat-09`, `until-100`, `until-300`. On
  this roster the P1 aggression/hunt knobs and the swarm push term never
  change a single selection — consistent with the trace (contacts are rare,
  created by economy movement).
- **Negative (11 arms)**: `margin-2` 14–10 · `peq-09` 14–10 · `margin-0`
  16–8 · `margin-05neg` 16–8 (bit-identical games to `margin-0`: strike
  gains move in whole segments, so any margin in (−1, 0] admits the same
  trade set) · `peq-05` 16–8 · `hunt-300` 17–7 · `huntpack` 17–7 ·
  `preymin-6` 17–7 · `threat-15` 15–9 · `berserk` 18–6 · `x04-support` 18–6.
- **One arm above baseline**: `threat-05` (halve the standing-in-reach
  penalty) **20–4** (+1, single fixture flip, deaths 125→144/game: it wins
  one more by accepting more risk). Below the pre-registered ≥21/24 gate;
  not adopted, and per the frozen refit rule no gauntlet confirmation was
  run.

**No arm reaches the advance gate; every adoption test fails.** The incumbent
stays the frozen defaults.

### Mechanism cells

| Cell | Mechanism | Screen | Reading |
|---|---|---|---|
| x03-balance | CM-1 length-balance margin (w=3.0) | **17–7** (−2) | conditioning the margin on local length balance *hurt*: the swarm field's coarse, decayed quadrants are a worse referee than the fixed margin at this contact frequency |
| x04-support | CM-2 support-weighted gain (w=1.0) | **18–6** (−1) | paying for visible nearby allies nudges a handful of trades the wrong way |

### Fresh reserve (baseline record)

`von_neumann-x01-frozen` on the two frozen combat map families, 16 games:
**8–8**. Per opponent: ouroboros-v13 3–1, sinbad-v06 3–1, hunter-v20 2–2,
avery-v08 **0–4**. The crown-race style is the baseline's weak spot on both
fresh families. This is the promotion reference for any future variant; no
variant this cycle reached the screen gate, so the reserve gate was not
exercised.

### Harness caveat measured

tew-v12-mid-support and ouroboros-v13-ladder produce **identical candidate
trajectories on 5 of 8 shared screen fixtures** (same rounds, same candidate
stats; present also in the original porthos record). The screen's 24 fixtures
carry at most ~19 independent games — a known roster-correlation limit
(handoff §7), now quantified for this config.

## 6. Verdict on aggression (per the frozen selection rule)

1. **Aggression is a necessary component**: the pacifist bound loses 5 net
   games (14–10) with massively inflated deaths. Removing combat admission
   from this policy family is measurably bad.
2. **Aggression is not a free-standing optimisation axis at this contact
   frequency**: the trace shows intentional strikes/hunts almost never fire;
   consistent with that, berserk (−1), the margin/relax/sat/until/push sweeps
   (flat or negative) and both new conditioning mechanisms (−1/−2) all fail to
   beat the frozen P1 settings. P1's early-saturation gate sits at a flat
   local optimum of the combat surface.
3. **Formal outcome per `selection_rule.json`**: no conditioning passed the
   screen gate, so no gauntlet/promotion run was warranted; **the incumbent
   policy stays exactly the frozen P1 aggression gate**, and the verdict is
   *aggression = necessary, currently not improvable by re-parameterisation on
   this evidence; the binding constraint is contact creation (economy-driven),
   not trade admission*.

This matches the replay-statistics prior (initiated contact is on average
negative) while explaining why P1's narrow gate was already near-optimal: the
screen roster rarely offers the kind of trade the gate admits.

### Honest limits of this cycle

- The dev screen barely exercises the aggression machinery (16 flat arms,
  `aggro-off` zero flips): it has **little power to detect aggression
  improvements**, only to detect regressions (bounds + negative arms). A
  gauntlet-roster sweep (7 opponents × 13 maps, where P1's aggression gained
  +13) is the natural next instrument for any aggression-positive hypothesis.
- 24 fixtures ≈ ≤19 independent games (tew/ouroboros duplication above); the
  20–4 vs 19–5 difference is one fixture — noise-level evidence, correctly
  not promoted.
- One cycle, one roster family; the reserve exposed avery-v08 0–4 as an
  unaddressed matchup hole (crown-race endgame, not combat admission).

## 7. Next hypotheses (ranked)

1. **Contact creation, not trade admission** — the binding constraint per the
   trace. Approach/intercept objectives that manufacture favourable contacts
   (executor-level, e.g. javert's executor-conditioned ATTACK ideas) rather
   than re-weighting admission of the contacts that happen anyway.
2. **threat-05 confirmation on the gauntlet roster** (w_threat 0.5) — the only
   positive signal; needs the wider roster before any adoption claim.
3. **Avery matchup**: the baseline loses 0–4 to crown-race on fresh maps;
   endgame feeding/crown defense is the measured hole (matches the Aramis
   feeding leak: 40/128 donations recovered).
4. **Measurement power**: add an independent-opponent screen roster (the
   porthos gauntlet set) for aggression studies specifically.

## 8. Files

- Bots: `bots/von_neumann-x01-frozen` (control), `bots/von_neumann-x02-mech`
  (CM master, default-off, 24/24 parity), `bots/von_neumann-x03-balance`,
  `bots/von_neumann-x04-support` (mechanism cells), `bots/von_neumann-x01-trace`
  (diagnostic only; never deploy).
- Tools: `tools/von_neumann/{sweep.py,analyse_trace.py,make_reserve.py,
  frozen.json,selection_rule.json,reserve_frozen.json,sweep_results.json,
  invalidated_runs.json}`.
- Configs: `configs/von_neumann/{screen,gauntlet,reserve,sandbox,trace}.toml`
  + `reserve_maps/`.
- Tests: `tests/test_von_neumann.py` (5 checks).
- Runs: `experiment_data/von_neumann-*` (validation/parity/mechanisms/reserve/
  trace) and `experiment_data/vn-x01-*` (28 sweep arms; two pre-fix no-op runs
  recorded in `invalidated_runs.json`).
- Study doc: `docs/von_neumann.md` (this file).

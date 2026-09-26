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

### Cycle-2 verdict on aggression (per selection_rule_cycle2.json)

The addendum's validation condition — *some information-conditioned
aggression variant passes the union gate while aggro-off does not* — resolved
**in reverse**: aggro-off itself was the only arm to pass (+2 union), and it
passed the gauntlet (+4). Therefore:

1. **P1's aggression block is not a beneficial optimisable component.** Its
   two pieces split cleanly: the swarm-push term never engages anywhere
   measured (0 flips in 60 fixtures incl. saturation maps); the strike-margin
   relax engages only under saturation on big maps, where it is a small net
   liability (round-500 length races).
2. **Better information did not rehabilitate it.** Validated dual windows,
   self-size/phase factoring and room normalisation produced only
   flat-to-negative consumers (mb2 −3, tf −1/−3 on dev; +1 at best on the
   union).
3. **What remains promising is contact creation** (cycle-1 conclusion,
   unchanged) and the avery/crown-race matchup hole — both outside the
   frozen execution layer this cycle.

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
- Cycle 2: the fresh reserve family cannot express saturation (0 flips both
  cycles) — it validates nothing about gate-dependent behaviour; ~10 of the
  cycle's runs carried harness timeouts under 4-way parallel load and were
  resumed to zero errors (deterministic outcomes unaffected); grad1's
  inertness means INFO-1's value is untested, not refuted (its weight can
  never change an argmax against the goal-progress term at current scale).

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

## 9. Cycle 2: optimise the information available to aggression

Brief: with aggression at a flat local optimum (cycle 1), freeze the
execution layer and iterate the feature/information layer — EWMA density
fields (friendly/enemy, counts and sizes), own size, time, per-instance
terrain with available-space normalisation, message validation, dual
windows, and friendly-vs-enemy gradients — with all decisions
context-dependent (never compass). Then return to aggression.

### Freeze boundary (cycle 2)

Frozen byte-exact from x01: `executors`, `intentions`, `targets`, `tactics`,
`main`, `world`, `roles`, `radio`, `comms`, `risk_features`, `diagnostics`,
and all non-information parameters. Iterated: `swarm`, `density` (field
construction), `features` (fact construction), `decision` (three consumption
switches), `params` (switches, all default-off). Master source:
`bots/von_neumann-x06-info` (POLICY_VERSION 4).

A key scope finding: **the entire upgrade is receiver-side.** The radio
stream is unchanged — the dual windows reinterpret the same packets with a
second decay constant; space-normalisation uses the per-instance terrain
already in `world`; and idea #7 (message validation) turned out to be
already satisfied at the packet port: every packet carries a team-tag byte
plus a 56-bit mixing checksum, and `comms.unpack` rejects foreign-team or
corrupted payloads (p ≈ 1−2⁻¹⁶); a regression test now pins this. So
build-only cells are parity-exact by construction, and consumption cells
change decisions only.

### Stage A: EWMA choices validated against actual dragon data

`tools/von_neumann/ewma_validate.py` decodes 14 replays (gauntlet + fresh
reserve + dev screen maps), reconstructs per-round per-dragon ground truth
(id-keyed heads, teams, split lengths, pearls; lengths approximated
birth+pearls), and replays the bot's exact EWMA rules across half-lives
{0.5, 1, 2, 4, 8, 16}; 229,404 dragon-round observations. Frozen record:
`tools/von_neumann/ewma_frozen.json`.

| h | est_err enemy | contact lag | exit "ghost" |
|---|---|---|---|
| 0.5 | 0.039 | 0 | 0.00 |
| 1.0 | 0.087 | 0 | 0.22 |
| 2.0 | 0.142 | 0.57 | 0.67 |
| **4.0 (inherited)** | 0.192 | 0.89 | 0.94 |
| 8.0 | 0.235 | 1.06 | 1.05 |
| 16.0 | 0.271 | 1.07 | 1.05 |

- **The inherited half-life 4.0 sits at the stability knee** — exit memory
  and contact lag saturate beyond it while estimation error keeps growing.
  The existing constant is data-validated, not replaced.
- **Short window = 1.0**: zero contact lag with one round of exit memory,
  2.2× lower error than the long window. The pair (1, 4) yields the
  rising/falling-contact derivative.
- The pre-stated choice rule (min lag) was degenerate — a near-raw window
  always wins on lag; revised to the knee rule after reading the table and
  before any cycle-2 screen outcome (recorded in the frozen file).
- Measured cost of fuzzed-position reporting: the send-side position EWMA
  lags the true head by **3.2 tiles** on average — the spatial resolution
  ceiling of remote evidence, and a documented trade-off (send-side anonymity
  vs accuracy), unchanged this cycle.

### Mechanisms (x06 switches; 0 = P1 exactly)

INFO-1 `w_grad` — the early-saturation push toward enemy control follows the
gradient **damped by bounded room at the landing cell** (`spatial_gain =
swarm_gain · min(1, room/12)`): the same enemy density in a tight corridor
is a worse push target than in open water.

INFO-2 `w_mb2` — the strike margin shifts with the **short-window**
enemy-minus-ally balance, **damped by own length** (a 3-segment forager
reads +3 enemy segments differently than a 15-segment dragon) and **faded by
game phase**; evidence-gated (no confidence → no shift). This is CM-1
retried with the validated window and self-size/phase factoring.

INFO-3 `w_tf` — `threat_cost` scales by `1 + w_tf·contact`, where `contact`
is the short-window enemy length at the head normalised to [0,1]: standing
in reach is worse when fresh evidence confirms someone is actually there.
(Cycle 1's blind threat-05 was +1; this is its evidence-based successor.)

Tests: `tests/test_von_neumann.py` now 11 checks (P1 defaults, mb2
direction/gate/phase/own-length damping, short-window faster decay,
threat-scale normalisation, **foreign-team packet rejection**, spatial-gain
construction, plus the cycle-1 checks).

### Cycle-2 results

Dev screen (24 games, baseline 19–5): build-only cell `info-build` 19–5 exact
parity (the receiver-side construction changes nothing, as designed);
`grad1` 19–5 with **zero fixture flips — bit-identical games**;
`mb2-2`/`mb2-4` 16–8; `tf-05` 18–6, `tf-10` 16–8; `info-all` 14–10.
Nothing beats the baseline where the baseline is already measured — and the
flip counts show *why*: on compact fixtures the aggression gate never fires
and the margin/threat consumers only ever touch rare strike decisions.

**Instrument finding (pre-registered addendum
`selection_rule_cycle2.json`):** measured from gauntlet replays, the team
reaches the P1 saturation gate (≥45 units by round 200) on 12/40 gauntlet
games — always on big maps (big_empty, schooltime, stronghold, trauma,
trophy) and **never on the dev screen's compact maps**. Cycle-1's flat
aggression arms were unmeasurable, not neutral. The saturation screen
(`configs/von_neumann/sat_screen.toml`, 18 games, same roster, big maps) was
frozen as the second instrument; its baseline record (x06 defaults-off,
behaviour-identical to x01) is **13–5**, union baseline **32–10**.

Union results (42 games):

| Arm | Dev | Sat | Union | vs 32–10 | Flips |
|---|---|---|---|---|---|
| grad1 (INFO-1) | 19–5 | 13–5 | 32–10 | +0 | **0** (fully inert: 0 flips, 0 round changes even where the gate fires) |
| **re-agro-off** | 19–5 | **15–3** | **34–8** | **+2** | 4, all big_empty round-500 length races (3 losses→wins, 1 win→loss) |
| re-grad-push4 | 19–5 | 14–4 | 33–9 | +1 | few |
| re-grad-relax25 | 19–5 | 13–5 | 32–10 | +0 | 0 |
| tf-05 (INFO-3) | 18–6 | 15–3 | 33–9 | +1 | few |
| re-tf-grad | 18–6 | 15–3 | 33–9 | +1 | few |

**re-agro-off meets the frozen advance gate** (union ≥ baseline+2, ≥2 flips,
0 errors) and advanced to the 182-game gauntlet as
`bots/von_neumann-x07-quiet` (x06 base + `aggro_relax=0, aggro_push=0`;
everything else default).

### Promotion gates for x07-quiet

| Gate | Requirement | Result | Verdict |
|---|---|---|---|
| Gauntlet (182) | ≥ 127 wins (parent record 126–56) | **130–52**, 0 errors | **PASS** (+4; per-opponent: avery 19–7, drake 20–6, hunter 18–8, hydra 23–3, ouroboros 18–8, sinbad 14–9–3, tew 14–9–3) |
| Fresh reserve (16) | ≥ 9 wins (baseline 8–8 + 1) | 8–8 | **FAIL** — but with **0 flips and 0 round changes**: bit-identical games. The reserve maps never saturate, so the mechanism is unexpressed there, not refuted. |
| Judge sandbox (4) | 0 TLE / faults, budget clean | 2–2, 0 faults, 0 TLE; stronghold won both sides (longest 40 vs 8 at r500) | PASS |

**No promotion under the frozen rule** (all gates required). The honest
reading across 240 games: silencing the gate is strictly-better-where-
expressed (gauntlet +4, union +2) and bit-identical-where-unexpressed (dev
compact, fresh reserve) — weak dominance, never negative. The rule's reserve
gate exists to catch dev-overfitting and here fired on a family that cannot
measure the mechanism; a future reserve family with saturating maps is owed
before any release. `von_neumann-x07-quiet` is retained as a measured cell;
the playing recommendation remains porthos-x04 behaviour, with the x07
gauntlet record attached.

Mechanism reading of the two decisive arms:

- The **swarm push term (P1-1b) is dead in practice**: grad1 shows zero
  engagement anywhere — with or without room normalisation the push term
  (≤2.0 × a small balance delta) never overcomes the goal-progress term that
  steers movement. P1's "+13 aggression" cannot have come through this term
  on any fixture measured.
- The **strike-margin relax (P1-1a) is the engaging piece**, and where it
  fires (saturation + big maps) it is a net −2 liability: every flip is a
  round-500 longest-dragon race on big_empty, where relaxed trades spend
  length the endgame needs. The information upgrades (validated windows,
  self-size/phase factoring, room normalisation) did not rescue it — the
  consuming arms were flat-to-negative.

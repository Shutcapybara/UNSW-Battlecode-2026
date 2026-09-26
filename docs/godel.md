# Godel: aggression as an optimised component — second chassis, independent verdict

Lineage owner: Kimi. Started 2026-09-26. Mission, from the strategy/execution
brief: pick a sensible baseline given measured performance and design
simplicity, freeze everything not related to combat procedures, iterate hard
on combat strategy, refit the policy as evidence accumulates, and decide
whether **aggression is a valid optimisable component** of the policy —
explicitly not whether the bot can be made purely aggressive.

Von Neumann (GLM) runs the same question on the porthos-x04 (French-line)
chassis. Godel deliberately uses a second, stylistically independent chassis
so the verdict can be checked for chassis-robustness rather than assumed.

## 1. Synthesis: what the three replay analyses actually say

Three independent pipelines over the same ~60k-game ledger converge on one
picture. Read together they are consistent; no pairwise contradiction exists.

| Question | Evidence study (`replay_analysis_20260926_evidence`, 7,762 round-100 games) | Features study (`replay_analysis_20260926103000`, 13,268 games) | Replay-stats study (`replay_stats_20260926_features`, 7,440 round-100 games) |
|---|---|---|---|
| Does killing predict winning? | Opponent-kill advantage adds **nothing** at round 100: Δ −0.0002 [−0.0007, +0.0004], q=0.643 | Raw kill counts symmetric by construction, carry nothing | `enemy_kills_per_round` weight ≈ 0, CI crosses 0 |
| Does fighting (contact per exposure) predict winning? | Friendly deaths need economic context (+0.00046, negligible) | Kills **and** deaths-to-opponent per dragon-round both mark losers (~11% vs ~83% close-game win rate) — fighting is a symptom of being pressured | `initiated_h2h_fraction` **−0.172**, `team_kills_per_round` **−0.194**: initiating contact associates with losing |
| Does the combat family as a whole carry signal? | Detailed events add +0.0216 beyond simple behaviour | — | Combat family Δ log loss **−0.0786** [−0.089, −0.069], Holm p≈0 — real held-out value, but it lives in *not dying badly* (`wall_deaths_per_round` −0.381, `death_lengths_mean` −0.133, `control×killed_by_enemy` −0.093), not in killing |
| What actually wins? | Population/cap Δ 0.104; pearls/round 0.0677 — growth dominates | Pearls per round 83.7% vs 12.0%; dragon count ~82–84%; space control 81.7% | `control_change` +1.250, `unit_change` +0.495, `pearls_per_dragon_round` +0.416 |
| Crown concentration? | `longest` between-bot ρ −0.256 | Crown-share winners take 15.0% of close games — swarm-of-beats-crown | `crown_share` −1.018 |
| Between-bot correlations | — | — | `team_kills_per_round` ρ **+0.451** with skill: strong bots kill more, but within-match killing does not predict winning. Skill absorbs strategy; neither direction is causal |
| Map dependence | Holding out `stronghold` flips loss 0.632 → 0.772 (no transfer) | `big_empty` reverses spatial gains (−0.44); 20/21 maps positive | Lineage-held-out combat-family value stands (−0.205 all-features) |

**Coherent takeaway.** Unconditional aggression — seeking contact, trading
when merely even, initiating head-to-heads — is on average a *losing* posture;
the positive between-bot kill correlation is composition (winners fight from
advantage), not cause. But combat is not ignorable: the combat feature family
carries real held-out value concentrated in *avoiding bad deaths* and in
engagement context. The only aggression plausibly worth optimising is
**conditioned aggression**: strike when the trade is favourable (up in length,
with local support, into overextension), refuse it otherwise. Two independent
datums already point this way: porthos P1's +13 gauntlet gain is attributable
to a *specific* conditioning (early + population-saturated + density-seeking),
and Von Neumann's first bounds arm shows removing strikes entirely costs
porthos-x04 5 games on the 24-game screen (pacifist 14–10 vs baseline 19–5).

The Godel experiment tests whether that conditioning generalises to a second
chassis, and whether the parameters/mechanisms of strike admission can be
refit to beat the frozen defaults.

## 2. Baseline choice

**Baseline: `ouroboros-v13-ladder`, copied byte-identically to
`bots/godel-x01-frozen`** (SHA-256 manifest `tools/godel/frozen.json`; 10
files, zero mismatches).

| Candidate | Measured strength | Combat surface | Verdict |
|---|---|---|---|
| ouroboros-v13-ladder | Panel 73.7% established, **1345 fixtures / 119 opponents**; Davidson posterior +1.26 ± 0.07 (1961 games); G+V 214-1-25 vs its own control | Ladder strike rule isolated in `ladder.py`; threat model (`p_strike*`, `trade_bias`), per-role `trade_margin`/`strike_bonus`/`risk`, hunt-share mixes, `crown_kill_round` — all plain parameters in `defaults.py`, overridable via `params.py` without touching code | **chosen** |
| tew-v12-mid-support | 72.4%, 3164 fixtures — the best-measured bot | Same codebase family (policy base *is* v13) + support-gated strike | rejected as baseline (weaker, same chassis); kept as screen opponent, treated as correlated evidence |
| sinbad-v07-divecap | Panel 85.4% but **sparse** (24 fixtures) | Unfinished variant; strategy brief warns against choosing by version number | rejected: unmeasured |
| porthos-x04-policy | Panel 76.2%, 182 fixtures | Already Von Neumann's chassis | rejected for Godel: duplicate chassis adds no independence; kept as opponent |
| hunter-v20/v14, fry-v14 | Established C++ references | Combat in C++; slow iterate/test cycle, no parameter doctrine mechanism | rejected: design simplicity |
| leviathan-v09-arrival | 65.3%, 999 fixtures | Strong arrival-aware economy; weakest of the strong | rejected: combat not the bottleneck |
| kraken-v04-eval | Not top-rated; 1283 LOC | Simplest codebase, but eval-banker with minimal combat surface | rejected: too little combat to optimise |

The ouroboros chassis is (a) the strongest well-measured Python bot outside
the French line, (b) already doctrine-parameterised, so parameter arms are
`params.py`-only variants auditable by file diff, and (c) map-class aware
(ladder on compact ≤ 625 tiles, evaluator on open) — matching the analyses'
map-dependence warning by construction.

## 3. Freeze discipline

Frozen from x01 (combat iteration must not touch): `world.py`, `comms.py`,
`targets.py`, `roles.py` (crown election, production doctrine), `main.py`,
and every non-combat parameter block in `defaults.py`: material values,
economy/goal field, sprint costs, production (`split_min`, `child_size`,
`team_target_*`, `w_split`, `split_stop`…), portal handling, sonar/gossip,
crown/feeding endgame (except `crown_kill_round`), safety geometry (`w_trap`,
`space_slack`, `w_space`, doom/tunnel/exit weights).

Iteration surface (only): `ladder_attack_units`, `ladder_risk_max`,
`ladder_safety`, the trade-up condition in `ladder.py`; `p_strike1/2/3`,
`p_split_child`, `trade_bias`, `threat_reach` in `safety.py`; per-role
`trade_margin`, `strike_bonus`, `risk`, `w_enemy`, hunt share of `mix_*`,
`crown_kill_round`. Mechanism variants may add default-off switches to
`ladder.py`/`safety.py`/`evaluate.py` combat branches only, and must
reproduce x01 exactly with switches at defaults (structural parity test).

## 4. Harness

- Dev screen: `configs/godel/screen.toml` — hunter-v20-portal-scouts,
  tew-v12-mid-support, porthos-x04-policy × Colosseum / devil (compact,
  ladder path) / queen_of_spades / trauma (open, evaluator path) × both
  sides, 24 games, jobs=4. Deterministic engine ⇒ exact per-fixture pairing
  against the x01 record.
- Gauntlet: `configs/godel/gauntlet.toml` — 7 opponents × 13 maps × both
  sides = 182 games.
- Reserve: `configs/godel/reserve.toml` — two fresh combat-focused map
  families (`godel_reserve_pincer` 28×24, `godel_reserve_fourgates` 24×24)
  frozen before any outcome was read (`tools/godel/reserve_frozen.json`),
  vs hunter-v20, porthos-x04, avery-v08, kraken-v04; 16 games.
- Selection rule: `tools/godel/selection_rule.json` — frozen before any
  outcome was read. Screen ≥ baseline+2 advances; gauntlet ≥ baseline+3
  survives; promotion needs gauntlet + fresh-reserve (≥ x01 reserve + 1) +
  clean judge. Bounds arms (pacifist/berserk) are diagnostics, never
  candidates. Refit = coordinate descent over the combat parameters from the
  current incumbent, re-run after every adopted mechanism change.

## 5. Experiment log

All screens are `configs/godel/screen.toml` (24 games, deterministic fixtures,
exact pairing). Baseline record established by `godel-x01-frozen` run
`godel-x01-frozen_20260926024107406787`: **13–11** (vs hunter-v20 7–1,
tew-v12 4–4, porthos-x04 2–6; by map: Colosseum 2–4, devil 5–1,
queen_of_spades 3–3, trauma 3–3), zero errors/faults.

**Bounds arms** (diagnostics, never candidates):

| Arm | Change | Screen | Reading |
|---|---|---|---|
| x02-pacifist | all strikes priced out | **7–17** (porthos 0–8) | Conditioned aggression is load-bearing: −6 wins |
| x03-berserk | every trade admissible + paid | **12–12** (porthos 4–4) | Stance-level aggression nets −1; it doubles the porthos score (2–6 → 4–4) but loses the hunter/tew games it changes |

Both bounds arms fail the advance margin (15), as the verdict rule requires
for aggression to count as *conditional*.

**Coordinate descent (the policy refit).** Round 1 from x01
(`tools/godel/sweep_round1.json`, frozen pre-outcome):

| Arm | Parameter moved | Screen | Verdict |
|---|---|---|---|
| x04 | ladder_attack_units 3→4 | 13–11 | null (1 fixture touched) |
| x05 | hunt.trade_margin 0→1 | 13–11 | null (9 fixtures touched, net wash) |
| x06 | hunt.strike_bonus 1→2 | 11–13 | **worse** — paying for strikes loses |
| x07 | trade_bias 1.5→2.5 | **14–10** | **adopted** |
| x08 | p_strike1 0.75→0.60 | 12–12 | worse — discounting threat loses |
| x09 | mix_mid hunt 0.45→0.55 | 13–11 | null |
| x10 | crown_kill_round 380→340 | 13–11 | null |

Round 2 from incumbent x07 (`sweep_round2.json`): x11 trade_bias 3.5 → 13–11
(overshoot); x12 +hunt.trade_margin 1 → 14–10 (tie); x13 +ladder_attack_units
4 → 14–10 (tie); **x14 +p_strike2 0.35→0.5 → 15–9, adopted and passes the
≥15 advance threshold**; x15 +gather/scout margins 4 → 14–10 (tie).

Round 3 from incumbent x14 (`sweep_round3.json`): x16 p_strike2 0.5 *alone*
(missing 2×2 cell) → **12–12, worse than baseline**; x17 p_strike2 0.65 →
13–11 (overshoot); x18 +p_strike3 0.30 → 14–10; x19 +p_strike1 0.90 → 12–12;
x20 +hunt.trade_margin 1 → 12–12. **Converged**: every single-coordinate move
from x14 is worse or ties.

The 2×2 on the adopted set:

| | p_strike2 = 0.35 | p_strike2 = 0.5 |
|---|---|---|
| trade_bias = 1.5 | 13–11 (x01) | 12–12 (x16) |
| trade_bias = 2.5 | 14–10 (x07) | **15–9 (x14)** |

The gain is a genuine interaction: threat caution alone hurts, trade-cost
caution alone helps, together they are best. Direction of every adopted
change: **price enemy aggression higher and feel trades as costlier** — the
threat model was *under*-pricing enemy strikes. No adopted change makes the
bot attack more; the refit makes engagement *choosier*.

**Mechanism cells** on master `godel-x21-mech` (`sweep_mechanisms.json`,
frozen pre-outcome; parity checks passed: x21 bare = x01 on all 24 fixtures
exactly, x22 = x14 on all 24 fixtures exactly):

| Cell | Mechanism | Screen | Verdict |
|---|---|---|---|
| x23 | GM-1 support-gated strike (radius 4) | 15–9 | tie — tew's conditioning adds nothing here |
| x24 | GM-2 support-relaxed admission | 14–10 | worse |
| x25 | GM-1 + GM-2 | 15–9 | tie |

Final incumbent: **x14 = x01 + {trade_bias 2.5, p_strike2 0.5}** (params-only;
behaviourally identical to x22 on the mech master). Advanced to gauntlet.

## 6. Results

**Gauntlet** (`configs/godel/gauntlet.toml`, 182 games, 7 opponents × 13 maps
× both sides, zero errors/faults both runs):

| Bot | Record | vs sinbad-v03 | vs tew-v12 | vs avery-v06 | vs drake-v05 | vs porthos-x04 | vs hunter-v20 | vs hydra-v09 |
|---|---|---|---|---|---|---|---|---|
| x01 baseline | **112–70** | 10–16 | 13–13 | 13–13 | 20–6 | 9–17 | 21–5 | 26–0 |
| x14 refit | **112–70** | 12–14 | 9–17 | 14–12 | 22–4 | 13–13 | 19–7 | 23–3 |

Paired per-fixture analysis: **19 fixtures flip to wins, 19 flip to losses**
(21% of all fixtures change winner — this is a real behavioural rebalance,
not a null). The refit gains exactly where predicted (aggressive opponents:
porthos +4, sinbad +2, drake +2) and loses against supported-hunt kin and the
lanchester banker (tew −4, hydra −3, hunter −2). Net zero ⇒ **x14 fails the
frozen gauntlet gate (112 < 115 = baseline + 3). No promotion.** The screen's
+2 gain did not generalise across the wider roster — the same screen→reserve
failure shape as aramis-v02, and a caution that the 24-game screen overfits
conditioning to its three opponents.

**Fresh reserve** (maps frozen pre-outcome, 16 games; run as a sanity check
after the gauntlet gate failed — not a promotion attempt): x01 9–7,
**x14 12–4** (hunter-v20 4–0 vs x01's 2–2; porthos 2–2 vs 1–3). On genuinely
fresh, combat-focused maps the refit is worth +3/16. This does not override
the gauntlet gate; it shows the refit's value is real but **conditional on
map combat intensity** — mirroring the replay studies' map-dependence
warnings (stronghold/big_empty non-transfer).

**Judge**: not run — the judge gate applies to promotion candidates only, and
no cell passed the gauntlet. The x14 changes are threat-model constants that
cannot increase search cost; the frozen parent ouroboros-v13 is already
judge-measured clean (sandbox p99 < 60M, max 67.5M CPU points against its
< 60M/< 80M gate; see its README's CPU table).

**Verdict (per the frozen aggression_verdict_rule).** No conditioning passed
the promotion gate, so aggression is **not promoted as an optimisable
component this cycle** — but the three-way decomposition is the informative
part:

1. **Aggression is load-bearing, not decorative.** Pacifist collapses to
   7–17 (baseline 13–11), including 0–8 vs porthos-x04. A combat procedure
   must exist.
2. **Stance-level aggression is refuted.** Berserk nets 12–12 < 13–11; its
   porthos gain (2–6 → 4–4) is paid for elsewhere. Matches the replay
   evidence: initiating contact associates with losing.
3. **Re-conditioning works locally but did not generalise.** The refit
   (trade_bias 2.5, p_strike2 0.5 — *cautious* direction: price enemy strikes
   higher, feel trades as costlier) won the screen (+2), kept it through a
   clean 2×2 interaction (p_strike2 alone: 12–12), then exactly cancelled on
   the gauntlet (+19/−19 flips) and won the fresh combat reserve (+3). The
   support-gate mechanisms (tew's proven conditioning, GM-1/GM-2) added
   nothing on top.

Synthesis with Von Neumann: both chassis agree qualitatively — removing
aggression is catastrophic (porthos pacifist 14–10 → ours 7–17; both well
below baseline), unconditional aggression does not beat the inherited
conditioning, and the optimal engagement price sits on the *cautious* side of
the inherited default. Chassis-robust conclusion: **aggression is a valid
component to keep and calibrate defensively; it is not a dial to turn up.**

**Next cycle recommendations.** (a) The 24-game screen overfits: refit
against ≥6 opponents or a screen+mini-gauntlet composite before adopting.
(b) The refit's matchup asymmetry (beats aggressive bots, loses to
supported-hunt kin) suggests conditioning aggression on *opponent style
evidence* rather than global constants — a stateful mechanism, budgeted.
(c) big_empty/default remain weak (0.29–0.64); combat conditioning is not
the lever there.

Artifacts: runs under `experiment_data/godel-*`; plans `tools/godel/
sweep_round{1,2,3}.json`, `sweep_mechanisms.json`; frozen rule
`tools/godel/selection_rule.json`; reserve fingerprints
`tools/godel/reserve_frozen.json`; discipline tests `tests/test_godel.py`
(4 checks, all passing).
